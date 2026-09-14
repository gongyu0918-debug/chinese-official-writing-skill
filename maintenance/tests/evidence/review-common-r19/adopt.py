"""Adopt the exact tested one-page compression on the isolated development branch."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
EXPERIMENT = ROOT / 'output/review-common-r19-calculated'
FROZEN = ROOT / 'output/review-common-r19-adopted'
build = json.loads((EXPERIMENT / 'build.json').read_text(encoding='utf-8'))
decision = json.loads((HERE / 'decision.json').read_text(encoding='utf-8'))
assert decision['status'] == 'adopt-development-only'
assert decision['candidate_fingerprint'] == build['fingerprints']['candidate']
assert not FROZEN.exists()
assert subprocess.check_output(['git', 'branch', '--show-current'], cwd=ROOT, text=True).strip() == 'codex/reference-rewrite-20260912'


def files(root):
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(root.rglob('*'))
            if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc'}


canonical = ROOT / 'chinese-official-writing'
assert files(canonical) == build['files']['baseline']
assert files(EXPERIMENT / 'candidate') == build['files']['candidate']
relative = Path('references/review-checklist.md')
targets = [canonical] + [ROOT / 'packages' / name / 'skills' / folder for name, folder in [
    ('agent-skills', 'chinese-official-writing'), ('hermes', 'chinese-official-writing'),
    ('qwen-code', 'chinese-official-writing'), ('qwenwork', 'chinese-official-writing'),
    ('openclaw', 'chinese_official_writing')]]
for root in targets:
    path = root / relative
    assert path.resolve().is_relative_to(ROOT.resolve())
    assert hashlib.sha256(path.read_bytes()).hexdigest() == build['files']['baseline'][relative.as_posix()]
    assert not subprocess.check_output(['git', 'status', '--porcelain', '--', path.relative_to(ROOT).as_posix()], cwd=ROOT, text=True).strip()
data = (EXPERIMENT / 'candidate' / relative).read_bytes()
for root in targets:
    (root / relative).write_bytes(data)
assert files(canonical) == build['files']['candidate']
assert all((root / relative).read_bytes() == data for root in targets)
shutil.copytree(canonical, FROZEN / 'candidate', ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
assert files(FROZEN / 'candidate') == build['files']['candidate']
record = {
    'source_head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
    'main_unchanged': subprocess.check_output(['git', 'rev-parse', 'main'], cwd=ROOT, text=True).strip(),
    'fingerprint': build['fingerprints']['candidate'], 'files': files(canonical),
    'changed': [relative.as_posix()], 'mirror_count': 5,
    'decision_sha256': hashlib.sha256((HERE / 'decision.json').read_bytes()).hexdigest(),
    'scope': 'Local development only. No main merge, installation, push or release.',
}
(FROZEN / 'adoption.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({k: record[k] for k in ['fingerprint', 'changed', 'mirror_count', 'scope']}, ensure_ascii=False))
