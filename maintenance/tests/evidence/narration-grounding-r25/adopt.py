"""Adopt the tested request-route alignment and narration repair as one local pack."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
PACK = ROOT / 'output/narration-grounding-r25'
OUT = ROOT / 'output/narration-grounding-r25-adopted'


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def files(path):
    return {p.relative_to(path).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(path.rglob('*')) if p.is_file() and '__pycache__' not in p.parts}


r24 = read(ROOT / 'output/final-main-r24/build.json')
build = read(PACK / 'build.json')
decision = read(HERE / 'decision.json')
assert decision['status'] == 'accept-development-with-recorded-limits'
assert decision['candidate_fingerprint'] == build['fingerprint']
assert not OUT.exists()
assert subprocess.check_output(['git', 'branch', '--show-current'], cwd=ROOT, text=True).strip() == 'codex/reference-rewrite-20260912'
canonical = ROOT / 'chinese-official-writing'
before = files(canonical)
assert before == r24['before']
assert files(PACK / 'candidate') == build['candidate']
baseline = files(ROOT / 'output/final-main-native-r24-m0/snapshots/main')
for index in [0, 3]:
    run = ROOT / 'output' / f'narration-grounding-native-r25-m{index}'
    binding = read(run / 'binding.json')
    assert binding['baseline_commit'] == build['baseline_commit']
    assert binding['ordinary_only'] and binding['utf8_read']
    assert files(run / 'snapshots/main') == baseline
    assert files(run / 'snapshots/candidate') == build['candidate']
    rows = [read(p) for p in run.glob('*.result.json')]
    assert len(rows) == 2 and all(not r['invalid'] and r['returncode'] == 0 for r in rows)
changed = [p for p, h in build['candidate'].items() if before[p] != h]
assert set(changed) == {'references/reference-index.md', 'references/genre-playbook-request.md', 'references/genre-playbook-narration.md'}
targets = [canonical] + [ROOT / 'packages' / pkg / 'skills' / name for pkg, name in [
    ('agent-skills', 'chinese-official-writing'), ('hermes', 'chinese-official-writing'),
    ('qwen-code', 'chinese-official-writing'), ('qwenwork', 'chinese-official-writing'),
    ('openclaw', 'chinese_official_writing')]]
for target in targets:
    for relative in changed:
        assert hashlib.sha256((target / relative).read_bytes()).hexdigest() == before[relative]
        assert not subprocess.check_output(['git', 'status', '--porcelain', '--', (target / relative).relative_to(ROOT).as_posix()], cwd=ROOT, text=True).strip()
for target in targets:
    for relative in changed:
        shutil.copyfile(PACK / 'candidate' / relative, target / relative)
    for relative in changed:
        assert (target / relative).read_bytes() == (canonical / relative).read_bytes()
assert files(canonical) == build['candidate']
shutil.copytree(canonical, OUT / 'candidate', ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
record = {'fingerprint': build['fingerprint'], 'files': files(canonical), 'changed_from_r23': changed,
          'changed_from_r24': build['changed_from_r24'], 'mirrors': 5,
          'source_head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
          'main': subprocess.check_output(['git', 'rev-parse', 'main'], cwd=ROOT, text=True).strip(),
          'native_calls_r24_r25': 34, 'encoding_damaged_pair_calls': 2, 'direct_final_narration_calls': 4,
          'scope': 'Local development completion; unchanged pages inherit bounded prior evidence. No main merge, installation, push or publication.'}
(OUT / 'adoption.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({k: record[k] for k in ['fingerprint', 'changed_from_r23', 'mirrors', 'scope']}, ensure_ascii=False))
