"""Bind preserved anonymous verdicts to their true pair identities without changing reviews."""
from collections import Counter
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
rows = []
for batch, parts in [('r10', ['qwen', 'remaining']), ('r11', [''])]:
    folder = ROOT / f'output/common-layer-blind-{batch}'
    for suffix in parts:
        tail = '-' + suffix if suffix else ''
        mappings = {x['id']: x for x in json.loads((folder / f'mapping{tail}.json').read_text(encoding='utf-8-sig'))}
        for verdict in json.loads((folder / f'verdicts{tail}.json').read_text(encoding='utf-8-sig')):
            mapping = mappings[verdict['id']]
            row = {'batch': batch, **verdict, 'mapping': mapping}
            for scope in ('body', 'delivery'):
                winner = verdict[f'{scope}_winner']
                row[f'{scope}_preferred_arm'] = mapping[winner]['arm'] if winner in 'AB' and len(winner) == 1 else 'tie'
            if verdict['id'] == 'W01':
                row['calibration'] = 'Later independent appendix in review-remaining.md downgrades ordinary follow-up explanation from medium regression to light optional expansion. A/A preference remains mild. Original reviewer JSON is preserved.'
            rows.append(row)
summary = {batch: {scope: dict(Counter(x[f'{scope}_preferred_arm'] for x in rows if x['batch'] == batch)) for scope in ('body', 'delivery')} for batch in ('r10', 'r11')}
report = {'note': 'Preferences are not hard-failure counts or statistical proof. R10 compares R8+80 with R10; R11 compares R10 with a one-sentence refinement. Independent reviews only saw anonymous full messages. W01 later calibration takes precedence over its original severity.', 'summary': summary, 'records': rows}
(HERE / 'quality-results.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps(summary, ensure_ascii=False))
