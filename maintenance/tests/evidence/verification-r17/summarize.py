"""Keep native technical counts, blind preferences and execution costs separate."""
from pathlib import Path
from collections import Counter
import json

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
RUNS = {
    'final-genres-native-r17-low-frequency': 10,
    'final-word-native-r17': 12,
    'editorial-object-native-r17-qwen': 4,
    'editorial-object-native-r17-minimax': 4,
    'motion-purpose-native-r17': 8,
    'final-modes-native-r17': 8,
}
run_records = []
for name, count in RUNS.items():
    root = ROOT / 'output' / name
    rows = json.loads((root / 'results.json').read_text(encoding='utf-8-sig'))
    assert len(rows) == count, (name, len(rows))
    inspection = json.loads((root / 'inspection.json').read_text(encoding='utf-8-sig'))
    run_records.append({'run': name, 'calls': len(rows), 'technical_valid': sum(not x['invalid'] for x in rows), 'invalid': [{k: x[k] for k in ['model', 'case', 'arm', 'invalid']} for x in rows if x['invalid']], 'totals': inspection['summary']})

reviews = []
for name in ['final-genres-r17', 'editorial-object-r17', 'motion-purpose-r17', 'final-modes-r17']:
    root = ROOT / 'output/blind-r16' / name
    mapping = {r['id']: r for r in json.loads((root / 'mapping.json').read_text(encoding='utf-8'))}
    verdicts = json.loads((root / 'verdicts.json').read_text(encoding='utf-8'))
    assert set(mapping) == {v['id'] for v in verdicts}
    counts = {'body': Counter(), 'delivery': Counter()}
    decoded = []
    for v in verdicts:
        row = mapping[v['id']]
        result = {k: row[k] for k in ['id', 'run', 'model', 'case']}
        for axis in counts:
            pref = v[axis + '_preference']
            assert pref in {'A', 'B', 'tie'}
            arm = pref if pref == 'tie' else row[pref]['arm']
            counts[axis][arm] += 1
            result[axis] = arm
        decoded.append(result)
    reviews.append({'name': name, 'pairs': len(verdicts), 'counts': counts, 'decoded': decoded})

record = {'calls': sum(r['calls'] for r in run_records), 'technical_valid': sum(r['technical_valid'] for r in run_records), 'runs': run_records, 'blind_reviews': reviews, 'note': 'Separate frozen comparisons, not a pooled success rate. Word originals and rendered pages are assessed independently.'}
assert record['calls'] == 46
(HERE / 'summary.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'calls': record['calls'], 'technical_valid': record['technical_valid'], 'reviews': [{k: r[k] for k in ['name', 'pairs', 'counts']} for r in reviews]}, ensure_ascii=False))
