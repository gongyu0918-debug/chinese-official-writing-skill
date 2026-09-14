"""Bind the fixed final batch and its prespecified diagnostic repeats separately."""
from pathlib import Path
import hashlib
import json
from collections import Counter
import importlib.util

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('native_inspection', ROOT / 'maintenance/tests/evidence/common-layer-r10/inspect_native.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def files(path):
    return {p.relative_to(path).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(path.rglob('*')) if p.is_file() and '__pycache__' not in p.parts}


build = read(ROOT / 'output/final-main-r24/build.json')
assert files(ROOT / 'output/final-main-r24/candidate') == build['candidate']
baseline_files = files(ROOT / 'output/final-main-native-r24-m0/snapshots/main')
report = {'candidate_fingerprint': build['fingerprint'], 'baseline_commit': build['original_main'],
          'scope': 'Fixed final batch and diagnostic repeats remain separate. A preference is not itself proof of a rule-caused regression. Tokens are not monetary prices.', 'batches': {}}
for batch, model_ids, prefix, expected in [
    ('initial', range(5), 'final-main-native', 20),
    ('repeat', [0, 2], 'final-main-repeat', 6),
    ('environment-damaged', [3], 'final-main-repeat', 2),
    ('encoding-recovery', [3], 'final-main-utf8', 2),
]:
    calls, pairs, inspections = [], [], []
    for index in model_ids:
        suffix = f'{prefix}-r24-m{index}'
        run = ROOT / 'output' / suffix
        binding = read(run / 'binding.json')
        assert binding['baseline_commit'] == build['original_main'] and binding['ordinary_only'] is True
        assert files(run / 'snapshots/main') == baseline_files
        assert files(run / 'snapshots/candidate') == build['candidate']
        inspection = module.inspect(run)
        if batch == 'encoding-recovery':
            assert binding['utf8_read'] is True
            assert all('SKILL.md' in r['unique_pages'] for r in inspection['records'])
        (run / 'inspection.json').write_text(json.dumps(inspection, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        inspections.append(inspection)
        for p in sorted(run.glob('*.result.json')):
            row = read(p)
            assert not row['invalid'] and row['returncode'] == 0
            final = p.with_name(p.name.replace('.result.json', '.final.txt'))
            assert hashlib.sha256(final.read_text(encoding='utf-8-sig').encode()).hexdigest() == row['draft_sha256']
            calls.append({k: v for k, v in row.items() if k != 'commands'} | {'run': suffix})
        blind_name = suffix.replace('final-main-native-', 'final-main-')
        blind = ROOT / 'output/blind-r16' / blind_name
        mapping = {p['id']: p for p in read(blind / 'mapping.json')}
        for verdict in read(blind / 'review.json')['verdicts']:
            identity = mapping[verdict['id']]
            result = {'model': identity['model'], 'case': identity['case'], 'packet': blind.relative_to(ROOT).as_posix(), 'id': verdict['id'], 'findings': verdict['findings']}
            for field in ['body', 'delivery']:
                preference = verdict[field + '_preference']
                result[field] = 'tie' if preference == 'tie' else identity[preference]['arm']
            pairs.append(result)
    assert len(calls) == expected and len(pairs) == expected // 2
    totals = {}
    for arm in ['baseline', 'candidate']:
        keys = ['commands', 'read_chars_unique', 'input_tokens', 'cached_input_tokens', 'uncached_input_tokens', 'output_tokens', 'seconds', 'prose_lint.py', 'draft_length.py', 'anti_ai_page_returned', 'tasks_with_prose_command']
        totals[arm] = {k: round(sum(i['summary'][arm][k] for i in inspections), 2) for k in keys}
    report['batches'][batch] = {'calls': calls, 'pairs': pairs, 'counts': {k: dict(Counter(p[k] for p in pairs)) for k in ['body', 'delivery']}, 'execution': totals, 'snapshot_bindings': 'PASS',
                              'rule_comparability': 'EXCLUDED: baseline SKILL returned mojibake after Windows PowerShell default decoding; raw blind tie retained only.' if batch == 'environment-damaged' else 'comparable within each pair'}
candidate = ROOT / 'output/final-main-r24/candidate'
paths = [candidate / 'SKILL.md', *sorted((candidate / 'references').glob('*.md'))]
size = sum(len(p.read_text(encoding='utf-8-sig')) for p in paths)
report['rule_size'] = {'baseline_chars': 92415, 'candidate_chars': size, 'reduction_percent': round(100 * (1 - size / 92415), 2), 'files': len(paths), 'scope': 'SKILL.md + references; normalized LF; excludes README, scripts and removed Hooks.'}
(HERE / 'final-evidence.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'rule_size': report['rule_size'], 'batches': {k: {'calls': len(v['calls']), 'counts': v['counts'], 'snapshot_bindings': v['snapshot_bindings']} for k, v in report['batches'].items()}}, ensure_ascii=False))
