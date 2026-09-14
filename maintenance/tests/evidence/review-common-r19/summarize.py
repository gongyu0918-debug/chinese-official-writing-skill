"""Keep each frozen review-page prototype and its evidence distinct."""
from pathlib import Path
from collections import Counter
import hashlib
import json

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
GROUPS = [('qwen', 'review-common-r19', 'qwen'), ('deepseek', 'review-common-r19', 'deepseek'),
          ('repaired', 'review-common-r19-repaired', 'repaired'),
          ('calculated', 'review-common-r19-calculated', 'calculated-valid')]


def files(root):
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(root.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc'}


groups = []
for suffix, prototype, blind_suffix in GROUPS:
    run = ROOT / 'output' / ('review-common-native-r19-' + suffix)
    build = json.loads((ROOT / 'output' / prototype / 'build.json').read_text(encoding='utf-8'))
    rows = json.loads((run / 'results.json').read_text(encoding='utf-8'))
    binding = json.loads((run / 'binding.json').read_text(encoding='utf-8'))
    inspection = json.loads((run / 'inspection.json').read_text(encoding='utf-8'))
    assert len(rows) == 8 and len({(r['model'], r['case'], r['arm']) for r in rows}) == 8
    for arm in ['baseline', 'candidate']:
        assert files(run / 'snapshots' / ('main' if arm == 'baseline' else arm)) == build['files'][arm]
    blind = ROOT / 'output/blind-r16' / ('review-common-r19-' + blind_suffix)
    mapping = {r['id']: r for r in json.loads((blind / 'mapping.json').read_text(encoding='utf-8'))}
    review = json.loads((blind / 'review.json').read_text(encoding='utf-8'))['verdicts']
    assert len(mapping) == len(review) == 4
    counts, decoded = {'body': Counter(), 'delivery': Counter()}, []
    for verdict in review:
        m = mapping[verdict['id']]
        row = {k: m[k] for k in ['id', 'model', 'case']}
        for label in ['A', 'B']:
            assert hashlib.sha256((ROOT / m[label]['file']).read_bytes()).hexdigest() == m[label]['sha256']
        for axis in counts:
            label = verdict[axis + '_preference']
            assert label in ['A', 'B', 'tie']
            choice = label if label == 'tie' else m[label]['arm']
            row[axis] = choice
            counts[axis][choice] += 1
        decoded.append(row)
    observations = []
    for row in inspection['records']:
        observations.append({
            **{k: row[k] for k in ['stem', 'model', 'case', 'arm', 'invalid', 'seconds', 'read_chars_unique', 'uncached_input_tokens', 'unique_pages']},
            'repeated_pages': {k: n for k, n in row['page_returns'].items() if n > 1},
            'script_commands': dict(Counter(c['script'] for c in row['script_calls'])),
        })
    raw_source = run / 'runner-source.py'
    if raw_source.is_file():
        actual = hashlib.sha256(raw_source.read_bytes()).hexdigest()
        assert actual == binding['runner_sha256']
        provenance = {'raw_hash_match': True, 'retained_source_sha256': actual,
                      'origin': 'raw runner source copied at launch'}
    else:
        provenance = json.loads((run / 'runner-source-provenance.json').read_text(encoding='utf-8'))
    groups.append({'group': suffix, 'prototype': prototype, 'fingerprints': build['fingerprints'],
                   'calls': len(rows), 'technical_valid': sum(not r['invalid'] for r in rows),
                   'actual_efforts': sorted({(r['model'], r['effort']) for r in rows}),
                   'totals': inspection['summary'], 'matched_anti_prose_pairs': inspection['matched_anti_prose_pairs'],
                   'blind_counts': counts, 'decoded': decoded, 'observations': observations,
                   'runner_raw_sha256': binding['runner_sha256'],
                   'runner_source_provenance': provenance})
record = {'calls': sum(g['calls'] for g in groups), 'technical_valid': sum(g['technical_valid'] for g in groups),
          'groups': groups, 'scope': 'Initial candidate had a confirmed grammar-check omission and is not eligible for adoption. Grammar-repaired and explicit-calculation variants are separate frozen 8-call comparisons. No pooled version success rate, no new full 1.x comparison. First three batches retained semantic runner reconstructions, with the original raw-source limitation explicitly labeled; calculated batch retained the matching raw source at launch. Skill snapshots and original artifacts are hash-verified.'}
(HERE / 'summary.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'calls': record['calls'], 'technical_valid': record['technical_valid'],
                  'groups': [{'group': g['group'], 'counts': g['blind_counts'], 'decoded': g['decoded']} for g in groups]}, ensure_ascii=False))
