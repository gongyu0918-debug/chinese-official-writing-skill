"""Seal merge-assessment evidence; never include isolated runtime profiles."""
import hashlib
import json
import subprocess
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[4]
E = Path(__file__).resolve().parent
OUT = ROOT / 'output/skill-lightening-merge-check'
ARCHIVES = Path('F:/Workspaces/chinese-official-writing-skill-archives/experiments/skill-lightening-20260909')
repeat = json.loads((OUT / 'repeats/receipts.json').read_text(encoding='utf-8'))
assert len(repeat) == 2
for r in repeat:
    assert r['exit_code'] == 0 and r['error'] is None
    assert r['prompt_sha256'] == r['original_prompt_sha256']
    d = OUT / 'repeats' / str(r['provider']) / r['case'] / r['arm']
    assert (d / 'final.txt').read_text(encoding='utf-8').strip()
    assert hashlib.sha256((d / 'prompt.txt').read_bytes()).hexdigest() == r['prompt_sha256']
engineering = ARCHIVES / 'merge-engineering-evidence.zip'
expected = '5e787df61f175ea118ddee2617c9964797c206785dea397bbdb0989dcf6067dc'
assert hashlib.sha256(engineering.read_bytes()).hexdigest() == expected
with ZipFile(engineering) as z:
    assert z.testzip() is None
judgment = {
    'decision': 'READY for local-main merge; assessment only, not merged/pushed/published',
    'product_commit': '9149182bae37d6031b26ae061ce5d85bbfb3938f',
    'engineering_commit': '4f8d826fbe34e5e427789ad94301d82c70ff7b07',
    'main_baseline': 'f171e82fbe2849af4ec50f3605845ae315d456d8',
    'primary_calls': {'logical_pairs': 13, 'attempts': 27, 'finals': 26, 'same_effort_pairs': 12},
    'technical_failure': 'GLM complaint candidate max: 502 duplicate tool result, no final; high fallback succeeds, mixed-effort pair excluded from max causal comparison.',
    'targeted_repeat': {'case': 'advisory', 'provider': 2, 'additional_calls': 2,
                        'initial_candidate': 'real unsupported daily-operation expansion and omitted explicit undecided state',
                        'repeated_candidate': 'both targeted defects absent',
                        'baseline_initial_and_repeat': 'targeted boundaries retained',
                        'judges': 'root and independent read-only audit of all four texts',
                        'limit': 'Not stable in one repeat; does not prove zero probability effect. Initial failure retained.'},
    'common_quality_risks': ['execution narration', 'over-strong commentary inference',
                             'both procurement drafts infer current printer count',
                             'speech demonstration timing becomes more specific',
                             'occasional overly strict review or body code fence'],
    'engineering': {'full_suite': '847 tests; initial 30 failures+1 error in 6 old-layout methods',
                    'baseline_six_methods': '6/6 pass', 'affected_suites_after_migration': '115/115 pass',
                    'legacy_static_cases': '111/111 pass; not model calls',
                    'quick_validate': 'canonical+4 ordinary packages pass; OpenClaw category mismatch identical on baseline',
                    'archive': str(engineering), 'sha256': expected},
    'repeat_receipts': repeat,
}
(E / 'judgment.json').write_text(json.dumps(judgment, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
assert not subprocess.check_output(['git', 'diff', '9149182b', 'HEAD', '--', 'chinese-official-writing'], cwd=ROOT)
files = {p for p in (OUT / 'frozen').rglob('*') if p.is_file()}
for name in ['final.txt', 'prompt.txt', 'receipt.json', 'trace.jsonl', 'stderr.txt']:
    files.update((OUT / 'runs').glob('*/*/*/*/' + name))
    files.update((OUT / 'repeats').glob('*/*/*/' + name))
files.update((OUT / 'repeats').glob('*.json'))
files.update(p for p in E.iterdir() if p.is_file() and p.name != 'archive.json')
for name in ['skill-lightening-merge-assessment-20260909.md', 'skill-lightening-engineering-20260909.md']:
    files.add(ROOT / 'maintenance/docs' / name)
manifest = {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(files)}
archive = ARCHIVES / 'skill-lightening-merge-assessment.zip'
with ZipFile(archive, 'x', compression=ZIP_DEFLATED) as z:
    for name in manifest:
        z.write(ROOT / name, name)
    z.writestr('manifest.json', json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
with ZipFile(archive) as z:
    assert z.testzip() is None
    for name, sha in manifest.items():
        assert hashlib.sha256(z.read(name)).hexdigest() == sha, name
record = {'archive': str(archive), 'sha256': hashlib.sha256(archive.read_bytes()).hexdigest(),
          'members_verified': len(manifest), 'scope': 'frozen product, all 27 primary attempts and 2 exact-input repeats, assessment; isolated runtime profiles excluded',
          'engineering_archive': str(engineering), 'engineering_sha256': expected}
(E / 'archive.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps(record, ensure_ascii=False))
