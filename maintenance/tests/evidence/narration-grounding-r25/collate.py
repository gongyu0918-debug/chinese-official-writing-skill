"""Bind the two narration comparisons; retain per-model costs and judgments."""
from pathlib import Path
from collections import Counter
import hashlib
import importlib.util
import json

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('native_inspection', ROOT / 'maintenance/tests/evidence/common-layer-r10/inspect_native.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def read(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))


def files(root):
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(root.rglob('*')) if p.is_file() and '__pycache__' not in p.parts}


build = read(ROOT / 'output/narration-grounding-r25/build.json')
candidate = ROOT / 'output/narration-grounding-r25/candidate'
assert files(candidate) == build['candidate']
baseline = files(ROOT / 'output/final-main-native-r24-m0/snapshots/main')
pairs, calls, execution = [], [], []
for index in [0, 3]:
    name = f'narration-grounding-native-r25-m{index}'
    run = ROOT / 'output' / name
    binding = read(run / 'binding.json')
    assert binding['baseline_commit'] == build['baseline_commit']
    assert binding['ordinary_only'] and binding['utf8_read']
    assert files(run / 'snapshots/main') == baseline
    assert files(run / 'snapshots/candidate') == build['candidate']
    inspection = module.inspect(run)
    assert len(inspection['records']) == 2
    assert all('SKILL.md' in r['unique_pages'] for r in inspection['records'])
    assert 'references/genre-playbook-narration.md' in next(r for r in inspection['records'] if r['arm'] == 'candidate')['unique_pages']
    (run / 'inspection.json').write_text(json.dumps(inspection, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    execution.append({'run': name, 'summary': inspection['summary']})
    rows = [read(p) for p in run.glob('*.result.json')]
    assert len(rows) == 2 and all(not r['invalid'] and r['returncode'] == 0 for r in rows)
    calls.extend({k: v for k, v in r.items() if k != 'commands'} | {'run': name} for r in rows)
    packet = ROOT / 'output/blind-r16' / name
    mappings = {p['id']: p for p in read(packet / 'mapping.json')}
    for verdict in read(packet / 'review.json')['verdicts']:
        identity = mappings[verdict['id']]
        row = {'model': identity['model'], 'case': identity['case'], 'findings': verdict['findings']}
        for key in ['body', 'delivery']:
            label = verdict[key + '_preference']
            row[key] = 'tie' if label == 'tie' else identity[label]['arm']
        pairs.append(row)
size = sum(len(p.read_text(encoding='utf-8-sig')) for p in [candidate / 'SKILL.md', *sorted((candidate / 'references').glob('*.md'))])
report = {'candidate_fingerprint': build['fingerprint'], 'baseline_commit': build['baseline_commit'],
          'calls': calls, 'pairs': pairs, 'execution': execution, 'snapshots_and_required_reads': 'PASS',
          'counts': {k: dict(Counter(p[k] for p in pairs)) for k in ['body', 'delivery']},
          'rule_size': {'baseline_chars': 92415, 'candidate_chars': size, 'reduction_percent': round(100 * (1 - size / 92415), 2)},
          'scope': 'Two paired narration cases directly tested; unchanged pages inherit R24 and prior evidence. Clearly separated outside-body notes are accepted per the latest user instruction. No statistical noninferiority or universal speed/cost claim.'}
(HERE / 'results.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({k: report[k] for k in ['candidate_fingerprint', 'counts', 'rule_size', 'snapshots_and_required_reads']}, ensure_ascii=False))
