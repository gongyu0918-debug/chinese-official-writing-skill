"""Adopt a read-only DOCX format detector after real-document replay."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[4]
SOURCE = ROOT / 'output/prose-docx-zero-r17/candidate/scripts/prose_lint.py'
FROZEN = ROOT / 'output/reference-verification-r17-adopted'
assert not FROZEN.exists()
assert subprocess.check_output(['git', 'branch', '--show-current'], cwd=ROOT, text=True).strip() == 'codex/reference-rewrite-20260912'
before = 'd69f2a2f02972f1ed832f1f34af2f8ccd140033c6422f95d3637e920c42b46dc'
after = '96d79b02e0a23d7ea9eb7427b2b5b21c09cb2e03cd0f7243fdc3ab0fb1a9f460'
data = SOURCE.read_bytes()
assert hashlib.sha256(data).hexdigest() == after
targets = [ROOT / 'chinese-official-writing'] + [ROOT / 'packages' / name / 'skills' / folder for name, folder in [('agent-skills', 'chinese-official-writing'), ('hermes', 'chinese-official-writing'), ('qwen-code', 'chinese-official-writing'), ('qwenwork', 'chinese-official-writing'), ('openclaw', 'chinese_official_writing')]]
relative = Path('scripts/prose_lint.py')
for root in targets:
    path = root / relative
    assert path.resolve().is_relative_to(ROOT.resolve())
    assert all(not p.is_symlink() and not p.is_junction() for p in [path, *path.parents] if p.is_relative_to(ROOT))
    assert hashlib.sha256(path.read_bytes()).hexdigest() == before
    assert not subprocess.check_output(['git', 'status', '--porcelain', '--', path.relative_to(ROOT).as_posix()], cwd=ROOT, text=True).strip()
for root in targets:
    (root / relative).write_bytes(data)
assert all((root / relative).read_bytes() == data for root in targets)
shutil.copytree(ROOT / 'chinese-official-writing', FROZEN / 'candidate', ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
def files(root):
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(root.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc'}
current = files(FROZEN / 'candidate')
previous = files(ROOT / 'output/editorial-object-r17-adopted/candidate')
assert set(current) == set(previous)
assert {k for k in current if current[k] != previous[k]} == {relative.as_posix()}
record = {'source_head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(), 'main_unchanged': subprocess.check_output(['git', 'rev-parse', 'main'], cwd=ROOT, text=True).strip(), 'changed_since_editorial_adoption': [relative.as_posix()], 'files': current, 'fingerprint': hashlib.sha256(json.dumps(current, sort_keys=True).encode()).hexdigest(), 'script_sha256': after, 'mirror_count': 5, 'native_invocation': 'NOT_RUN', 'decision': '采用已在12份原生生成DOCX上复放的显式零字号风险检测；不新增页面、流程或默认硬门。新风险未验证native调用，不追认原超时稿已修复。'}
(FROZEN / 'adoption.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({k: record[k] for k in ['fingerprint', 'script_sha256', 'native_invocation', 'decision']}, ensure_ascii=False))
