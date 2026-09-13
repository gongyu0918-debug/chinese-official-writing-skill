"""Extract only native thread/model metadata and message hashes, never reasoning."""
from pathlib import Path
import argparse
import hashlib
import json

ROOT = Path(__file__).resolve().parents[4]


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def session_metadata(path, expected_id):
    owners, models, users, completions = [], [], [], []
    for line in path.open(encoding='utf-8'):
        event = json.loads(line)
        payload = event.get('payload', {})
        if event.get('type') == 'session_meta' and payload.get('id') == expected_id:
            owners.append({k: payload[k] for k in ['id', 'parent_thread_id', 'forked_from_id', 'source', 'model_provider', 'multi_agent_version'] if k in payload})
        elif event.get('type') == 'turn_context':
            models.append({k: payload[k] for k in ['model', 'effort'] if k in payload})
        elif event.get('type') == 'response_item' and payload.get('type') == 'message' and payload.get('role') == 'user':
            users.append(digest(payload.get('content')))
        elif event.get('type') == 'event_msg' and payload.get('type') == 'task_complete':
            final = payload.get('last_agent_message')
            completions.append({'timestamp': event.get('timestamp'), 'duration_ms': payload.get('duration_ms'),
                                'final_sha256_trimmed': hashlib.sha256(final.strip().encode()).hexdigest() if isinstance(final, str) else None})
    return {'file': path.name, 'owner_metadata': owners, 'turn_models': models, 'user_message_hashes': users, 'completed_turns': completions}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('run')
    args = parser.parse_args()
    run = ROOT / 'output' / args.run
    binding = json.loads((run / 'binding.json').read_text(encoding='utf-8'))
    rows = json.loads((run / 'results.json').read_text(encoding='utf-8'))
    sessions = Path(binding['runtime']) / 'codex-profile' / 'sessions'
    paths = list(sessions.rglob('*.jsonl')) if sessions.is_dir() else []
    evidence = []
    for row in rows:
        for item in row.get('collaboration_items', []):
            if item.get('tool') != 'spawn_agent':
                continue
            sender = item['sender_thread_id']
            for receiver in item['receiver_thread_ids']:
                record = {'case': row['case'], 'arm': row['arm'], 'model': row['model'],
                          'root_seconds': row['seconds'], 'parent_id': sender, 'child_id': receiver,
                          'handoff_has_postscript': '文后提示' in (item.get('prompt') or ''),
                          'handoff_sha256': digest(item.get('prompt'))}
                for key, identity in [('parent', sender), ('child', receiver)]:
                    found = [p for p in paths if identity in p.name]
                    record[key] = session_metadata(found[0], identity) if len(found) == 1 else None
                child, parent = record['child'], record['parent']
                if child:
                    fork = any(m.get('forked_from_id') for m in child['owner_metadata'])
                    overlap = sorted(set(child['user_message_hashes']) & set(parent['user_message_hashes'])) if parent else []
                    record.update(has_fork_history=fork, shared_parent_user_messages=len(overlap),
                                  context_evidence='inherited-parent-history' if fork else 'fresh-thread-metadata-without-fork-history')
                    if child['completed_turns'] and parent and parent['completed_turns']:
                        ct, pt = child['completed_turns'][-1], parent['completed_turns'][-1]
                        record['child_completed_before_parent'] = ct['timestamp'] <= pt['timestamp']
                        record['same_final_text'] = ct['final_sha256_trimmed'] is not None and ct['final_sha256_trimmed'] == pt['final_sha256_trimmed']
                else:
                    record['context_evidence'] = 'unavailable'
                evidence.append(record)
    result = {'run': args.run, 'root_calls': len(rows), 'spawn_calls': len(evidence), 'records': evidence,
              'limits': 'Model identifiers are native turn metadata; openai is the CLI transport provider. Root usage is not assumed to include child usage. No hidden reasoning, base instructions, credentials or global configuration are copied.'}
    (run / 'provenance.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'run': args.run, 'spawns': len(evidence), 'contexts': [r['context_evidence'] for r in evidence]}, ensure_ascii=False))


if __name__ == '__main__':
    main()
