"""Bind one-page compression, actual native reads and anonymous preferences."""
from collections import Counter
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
build = json.loads((ROOT / 'output/common-compression-r18/build.json').read_text(encoding='utf-8'))


def file_map(root):
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(root.rglob('*'))
            if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc'}


runs = []
for channel in ['qwen', 'deepseek']:
    name = 'common-compression-native-r18-' + channel
    run = ROOT / 'output' / name
    binding = json.loads((run / 'binding.json').read_text(encoding='utf-8'))
    receipts = json.loads((run / 'results.json').read_text(encoding='utf-8'))
    assert len(receipts) == 12
    assert len({(r['model'], r['case'], r['arm']) for r in receipts}) == 12
    for arm in ['baseline', 'candidate']:
        # The reused runner stores every baseline in snapshots/main, even for 2.0 pairs.
        snapshot = run / 'snapshots' / ('main' if arm == 'baseline' else arm)
        assert snapshot.is_dir(), snapshot
        assert file_map(snapshot) == build['files'][arm], (name, arm)
    inspection = json.loads((run / 'inspection.json').read_text(encoding='utf-8'))
    observed = []
    for row in inspection['records']:
        final = run / (row['stem'] + '.final.txt')
        trace = run / (row['stem'] + '.trace.jsonl')
        assert hashlib.sha256(final.read_bytes()).hexdigest() == row['final_sha256']
        assert hashlib.sha256(trace.read_bytes()).hexdigest() == row['trace_sha256']
        observed.append({
            **{k: row[k] for k in ['stem', 'case', 'arm', 'invalid', 'read_chars_unique', 'seconds', 'uncached_input_tokens', 'unique_pages']},
            'repeated_full_pages': {k: v for k, v in row['page_returns'].items() if v > 1},
            'script_commands': dict(Counter(c['script'] for c in row['script_calls'])),
        })
    blind = ROOT / 'output/blind-r16' / ('common-compression-r18-' + channel)
    packet = json.loads((blind / 'packet.json').read_text(encoding='utf-8'))
    mapping = {r['id']: r for r in json.loads((blind / 'mapping.json').read_text(encoding='utf-8'))}
    review = json.loads((blind / 'review.json').read_text(encoding='utf-8'))
    verdicts = review['verdicts']
    assert len(packet['pairs']) == len(verdicts) == 6
    assert set(mapping) == {v['id'] for v in verdicts}
    counts = {'body': Counter(), 'delivery': Counter()}
    decoded = []
    for verdict in verdicts:
        m = mapping[verdict['id']]
        row = {k: m[k] for k in ['id', 'model', 'case']}
        for axis in counts:
            label = verdict[axis + '_preference']
            assert label in ['A', 'B', 'tie']
            arm = label if label == 'tie' else m[label]['arm']
            row[axis] = arm
            counts[axis][arm] += 1
        decoded.append(row)
    runs.append({
        'run': name, 'models': binding['models'], 'effort': binding['effort'],
        'calls': len(receipts), 'technical_valid': sum(not r['invalid'] for r in receipts),
        'totals': inspection['summary'], 'observations': observed,
        'matched_anti_prose_pairs': inspection['matched_anti_prose_pairs'],
        'blind_packet_sha256': hashlib.sha256((blind / 'packet.json').read_bytes()).hexdigest(),
        'blind_review_sha256': hashlib.sha256((blind / 'review.json').read_bytes()).hexdigest(),
        'blind_counts': counts, 'decoded': decoded,
    })
repeat_run = ROOT / 'output/common-compression-native-r18-review-repeat'
repeat_rows = json.loads((repeat_run / 'results.json').read_text(encoding='utf-8'))
assert len(repeat_rows) == 2 and all(not r['invalid'] for r in repeat_rows)
for arm in ['baseline', 'candidate']:
    assert file_map(repeat_run / 'snapshots' / ('main' if arm == 'baseline' else arm)) == build['files'][arm]
repeat_blind = ROOT / 'output/blind-r16/common-compression-r18-review-repeat'
repeat_mapping = json.loads((repeat_blind / 'mapping.json').read_text(encoding='utf-8'))[0]
repeat_verdict = json.loads((repeat_blind / 'review.json').read_text(encoding='utf-8'))['verdicts'][0]
repeat = {'calls': 2, 'technical_valid': 2, 'case': 'review', 'model': repeat_rows[0]['model'],
          'inspection': json.loads((repeat_run / 'inspection.json').read_text(encoding='utf-8'))['summary']}
for axis in ['body', 'delivery']:
    label = repeat_verdict[axis + '_preference']
    repeat[axis] = label if label == 'tie' else repeat_mapping[label]['arm']
record = {
    'source_head': build['source_head'], 'product_fingerprints': build['fingerprints'],
    'sizes': build['sizes'], 'calls': sum(r['calls'] for r in runs),
    'technical_valid': sum(r['technical_valid'] for r in runs), 'runs': runs,
    'attribution_repeat': repeat, 'total_calls_with_repeat': 26,
    'scope': 'Current 2.0 versus one common-page compression. Not a new global comparison against 1.x. Original blind judgments precede any parent calibration. Script command counts do not prove correct input or sequence; read characters and uncached tokens are not money saved.',
}
(HERE / 'summary.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'calls': record['calls'], 'technical_valid': record['technical_valid'],
                  'reviews': [{'run': r['run'], 'counts': r['blind_counts'], 'decoded': r['decoded']} for r in runs]}, ensure_ascii=False))
