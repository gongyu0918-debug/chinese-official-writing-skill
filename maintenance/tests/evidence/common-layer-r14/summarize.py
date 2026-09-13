"""Map the closed anonymous reviews and report exposure separately from preference."""
from collections import Counter
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
report = {}
for atom, group in [('A', 'A-sanitized'), ('B', 'B'), ('AB', 'AB')]:
    folder = ROOT / 'output/common-layer-blind-r14' / group
    mapping = {r['id']: r for r in json.loads((folder / 'mapping.json').read_text(encoding='utf-8'))}
    verdicts = json.loads((folder / 'verdicts.json').read_text(encoding='utf-8'))
    assert len(verdicts) == len(mapping) and {v['id'] for v in verdicts} == set(mapping)
    preferences, pairs = {}, []
    for key in ['body_preference', 'delivery_preference']:
        counts = Counter()
        for verdict in verdicts:
            choice = verdict[key]
            assert choice in ['A', 'B', 'tie'], choice
            counts['tie' if choice == 'tie' else mapping[verdict['id']][choice]['arm']] += 1
        preferences[key] = dict(counts)
    for verdict in verdicts:
        m = mapping[verdict['id']]
        pairs.append({'id': verdict['id'], 'model': m['model'], 'case': m['case'], **{
            key: 'tie' if verdict[key] == 'tie' else m[verdict[key]]['arm']
            for key in ['body_preference', 'delivery_preference']
        }})
    run = ROOT / 'output' / f'common-layer-native-r14-{atom}'
    inspection = json.loads((run / 'inspection.json').read_text(encoding='utf-8'))
    exposures = []
    for r in inspection['records']:
        exposures.append({k: r[k] for k in ['model', 'case', 'arm', 'unique_pages', 'read_chars_unique', 'uncached_input_tokens']})
    report[atom] = {'preferences': preferences, 'pairs': pairs, 'metrics': inspection['summary'], 'exposures': exposures}
(HERE / 'summary.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({k: v['preferences'] for k, v in report.items()}, ensure_ascii=False))
