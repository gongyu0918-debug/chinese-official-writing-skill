"""Summarize all attempts and the selected final per arm without hiding fallback."""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
E = Path(__file__).resolve().parent
OUT = ROOT / 'output/skill-lightening-merge-check'
freeze = json.loads((E / 'freeze.json').read_text(encoding='utf-8'))
attempts = json.loads((E / 'receipts.json').read_text(encoding='utf-8'))
rows = []
for provider, cases in freeze['assignments'].items():
    for case in cases:
        for arm in ['baseline', 'candidate']:
            valid = [r for r in attempts if r['provider_index'] == int(provider) and r['case'] == case and r['arm'] == arm and r['valid_final']]
            assert len(valid) == 1, (provider, case, arm, valid)
            r = valid[0]
            d = OUT / 'runs' / provider / case / arm / r['effort']
            files, size, failures = set(), 0, []
            for line in (d / 'trace.jsonl').read_text(encoding='utf-8').splitlines():
                ev = json.loads(line); it = ev.get('item', {})
                if ev.get('type') != 'item.completed' or it.get('type') != 'command_execution':
                    continue
                names = re.findall(r'(?:SKILL|[a-z][a-z-]+)\.md', it.get('command', ''))
                output = it.get('aggregated_output', '').replace('\r\n', '\n')
                if it.get('exit_code') != 0 or not output:
                    failures.append({'files_named': names, 'exit_code': it.get('exit_code'), 'empty_output': not output})
                elif names and ('\n#' in '\n' + output or 'name: chinese-official-writing' in output):
                    files.update(names); size += len(output)
            rows.append({'provider': int(provider), 'case': case, 'arm': arm, 'effort': r['effort'],
                         'returned_files_named_in_commands': sorted(files),
                         'returned_characters_including_repeats': size,
                         'failed_or_empty_commands': failures,
                         'final_sha256': hashlib.sha256((d / 'final.txt').read_bytes()).hexdigest()})
assert len(rows) == 26
pairs = []
for provider, cases in freeze['assignments'].items():
    for case in cases:
        selected = {r['arm']: r for r in rows if r['provider'] == int(provider) and r['case'] == case}
        pairs.append({'provider': int(provider), 'case': case,
                      'same_effort': selected['baseline']['effort'] == selected['candidate']['effort'],
                      'returned_character_delta': selected['candidate']['returned_characters_including_repeats'] - selected['baseline']['returned_characters_including_repeats']})
summary = {'writer_attempts': len(attempts), 'logical_pairs': len(pairs), 'valid_finals': len(rows),
           'same_effort_pairs': sum(p['same_effort'] for p in pairs),
           'invalid_attempts': [r for r in attempts if not r['valid_final']],
           'pairs': pairs, 'rows': rows,
           'limits': 'One route per interaction task supplements previous independent-atom multi-route evidence. Character counts describe observable Markdown tool returns including repeats, not billing or full context. Mixed-effort results do not establish max/max differences.'}
(E / 'observations.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({k:v for k,v in summary.items() if k not in ['rows','pairs','limits']}, ensure_ascii=False))
