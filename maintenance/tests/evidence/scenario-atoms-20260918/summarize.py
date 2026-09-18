"""Measure native executions and returned rule pages without grading prose."""
from pathlib import Path
import hashlib
import json
import re
import statistics

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
RUNS = ROOT / 'output/scenario-atoms-native-20260918'
SCRIPT = re.compile(r'''\b(?:python|py)(?:\.exe)?\s+["']?(?!-)[^;\r\n]*?(prose_lint|draft_length)\.py["']?(?=\s)''')


def compact(text):
    return re.sub(r'\s+', '', text)


if __name__ == '__main__':
    rows = []
    snapshot_diffs = {}
    for run in sorted(RUNS.iterdir()):
        if not (run / 'binding.json').exists():
            continue
        provider = run.name
        snapshots = {arm: run / 'snapshots' / directory for arm, directory in
                     (('baseline', 'main'), ('candidate', 'candidate'))}
        pages = {arm: {p.name: p.read_text(encoding='utf-8-sig') for p in root.glob('references/*.md')}
                 for arm, root in snapshots.items()}
        snapshot_diffs[provider] = [name for name in sorted(set(pages['baseline']) | set(pages['candidate']))
                                    if pages['baseline'].get(name) != pages['candidate'].get(name)]
        for path in sorted(run.glob('*.result.json')):
            item = json.loads(path.read_text(encoding='utf-8'))
            returned = '\n'.join(c['aggregated_output'] for c in item['commands'] if c.get('exit_code') == 0)
            returned_compact = compact(returned)
            loaded = []
            for name, content in pages[item['arm']].items():
                normalized = compact(content)
                # Require actual page content, not a filename printed by the index.
                if normalized[:min(160, len(normalized))] in returned_compact:
                    loaded.append({'page': name, 'full_content_returned': normalized in returned_compact,
                                   'page_chars': len(content)})
            script_calls = []
            for command in item['commands']:
                cmd = re.sub(r'''\\+(?=["'])''', '', command['command'])
                if '--help' in cmd:
                    continue
                for match in SCRIPT.finditer(cmd):
                    script_calls.append({'script': match[1], 'command_id': command['id'],
                                         'exit_code': command.get('exit_code')})
            usage = {key: sum((u or {}).get(key, 0) for u in item.get('usage', []))
                     for key in ('input_tokens', 'cached_input_tokens', 'output_tokens')}
            usage['uncached_input_tokens'] = usage['input_tokens'] - usage['cached_input_tokens']
            rows.append({k: item[k] for k in ('model', 'case', 'arm', 'effort', 'seconds', 'invalid')} |
                        {'run': path.stem.removesuffix('.result'), 'queue': provider, 'usage': usage, 'returned_pages': loaded,
                         'script_calls': script_calls, 'trace_sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
    paired = {}
    for row in rows:
        paired.setdefault((row['queue'], row['model'], row['case']), {})[row['arm']] = row
    valid_pairs = [pair for pair in paired.values()
                   if set(pair) == {'baseline', 'candidate'} and not any(row['invalid'] for row in pair.values())]
    totals = {}
    for arm in ('baseline', 'candidate'):
        selected = [pair[arm] for pair in valid_pairs]
        totals[arm] = {'calls': len(selected), 'seconds': round(sum(r['seconds'] for r in selected), 2),
                       'median_seconds': statistics.median(r['seconds'] for r in selected) if selected else None,
                       'returned_pages': sum(len(r['returned_pages']) for r in selected),
                       'returned_page_chars': sum(sum(p['page_chars'] for p in r['returned_pages']) for r in selected),
                       'usage': {key: sum(r['usage'][key] for r in selected) for key in
                                 ('input_tokens', 'cached_input_tokens', 'uncached_input_tokens', 'output_tokens')},
                       'script_executing_drafts': {name: sum(any(c['script'] == name and c['exit_code'] == 0
                           for c in r['script_calls']) for r in selected) for name in ('draft_length', 'prose_lint')}}
    result = {'method': 'Read evidence requires actual returned page content. Page characters count each observed page once per call, not billing tokens. Aggregate includes complete valid pairs only. Failed attempts stay in calls and failed_attempts. Latency is an observation, not a causal speed claim.',
              'valid_pairs': len(valid_pairs),
              'failed_attempts': [{k: row[k] for k in ('queue', 'run', 'invalid', 'seconds')} for row in rows if row['invalid']],
              'snapshot_diffs': snapshot_diffs, 'totals': totals, 'calls': rows}
    (HERE / 'execution-summary.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'totals': totals, 'snapshot_diffs': snapshot_diffs}, ensure_ascii=False))
