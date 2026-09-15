"""Archive native drafts and compact execution proofs without duplicating rule returns."""
from pathlib import Path
import argparse
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[4]
EVIDENCE = Path(__file__).resolve().parent


def digest(data):
    return hashlib.sha256(data).hexdigest()


def archive(source, label):
    source = ROOT / source
    target = EVIDENCE / 'writing-results' / label
    target.mkdir(parents=True, exist_ok=True)
    binding = json.loads((source / 'binding.json').read_text(encoding='utf-8'))
    for name in ['binding.json', 'runner-source.py']:
        (target / name).write_text((source / name).read_text(encoding='utf-8'), encoding='utf-8', newline='\n')
    records = []
    for result_path in sorted(source.glob('*.result.json')):
        result = json.loads(result_path.read_text(encoding='utf-8'))
        prefix = result_path.name.removesuffix('.result.json')
        draft_path = source / (prefix + '.final.txt')
        draft = draft_path.read_text(encoding='utf-8') if draft_path.exists() else ''
        if draft_path.exists():
            (target / (prefix + '.final.txt')).write_text(draft, encoding='utf-8', newline='\n')
        assert digest(draft.encode()) == result['draft_sha256']
        snapshot = source / 'snapshots' / ('main' if result['arm'] == 'baseline' else 'candidate')
        rule_pages = [snapshot / 'SKILL.md', *sorted((snapshot / 'references').glob('*.md'))]
        page_text = {p.relative_to(snapshot).as_posix(): p.read_text(encoding='utf-8-sig').replace('\r\n','\n').replace('\r','').strip() for p in rule_pages}
        calls = []
        full_returned = set()
        for call in result['commands']:
            output = call.get('aggregated_output', '').replace('\r\n', '\n').replace('\r', '')
            pages = [name for name, body in page_text.items() if body and body in output and call.get('exit_code') == 0]
            full_returned.update(pages)
            command = call.get('command', '')
            # A candidate call is only a pointer for human checking: a command
            # can read script source or request help without scanning a draft.
            script_candidate = any(name in command for name in ['draft_length.py','prose_lint.py'])
            calls.append({'id': call.get('id'), 'command': command, 'exit_code': call.get('exit_code'), 'output_sha256': digest(output.encode()), 'output_chars': len(output), 'full_pages_returned': pages, 'script_name_in_command': script_candidate, 'output_excerpt': output[:10000] if script_candidate and not pages else None})
        trace = source / (prefix + '.trace.jsonl')
        record = {k:v for k,v in result.items() if k != 'commands'}
        record.update({'raw_trace':str(trace.resolve()), 'trace_sha256':digest(trace.read_bytes()), 'full_pages_returned':sorted(full_returned), 'commands':calls})
        records.append(record)
    (target / 'execution-proof.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n', encoding='utf-8',newline='\n')
    print(json.dumps({'label':label,'calls':len(records),'invalid':[(r['case'],r['model'],r['arm'],r['invalid']) for r in records if r['invalid']]},ensure_ascii=False))


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('source')
    parser.add_argument('label')
    args=parser.parse_args()
    archive(args.source,args.label)
