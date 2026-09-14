"""Adopt only the tested editorial clarification and identical repository mirrors."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[4]
PROTOTYPE = ROOT / 'output/editorial-object-r17'
FROZEN = ROOT / 'output/editorial-object-r17-adopted'
assert not FROZEN.exists()
assert subprocess.check_output(['git', 'branch', '--show-current'], cwd=ROOT, text=True).strip() == 'codex/reference-rewrite-20260912'
assert not subprocess.check_output(['git', 'status', '--porcelain', '--', 'chinese-official-writing', 'packages'], cwd=ROOT, text=True).strip()
relative = Path('references/genre-playbook-editorial-note.md')
before = (PROTOTYPE / 'baseline' / relative).read_bytes()
after = (PROTOTYPE / 'candidate' / relative).read_bytes()
targets = [ROOT / 'chinese-official-writing'] + [ROOT / 'packages' / name / 'skills' / folder for name, folder in [('agent-skills', 'chinese-official-writing'), ('hermes', 'chinese-official-writing'), ('qwen-code', 'chinese-official-writing'), ('qwenwork', 'chinese-official-writing'), ('openclaw', 'chinese_official_writing')]]
for root in targets:
    path = root / relative
    assert path.resolve().is_relative_to(ROOT.resolve())
    assert all(not p.is_symlink() and not p.is_junction() for p in [path, *path.parents] if p.is_relative_to(ROOT))
    assert path.read_bytes() == before, str(path)
for root in targets:
    (root / relative).write_bytes(after)
shutil.copytree(ROOT / 'chinese-official-writing', FROZEN / 'candidate', ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
def files(root):
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(root.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc'}
current = files(FROZEN / 'candidate')
assert current == files(PROTOTYPE / 'candidate')
assert all((root / relative).read_bytes() == after for root in targets)
record = {'source_head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(), 'main_unchanged': subprocess.check_output(['git', 'rev-parse', 'main'], cwd=ROOT, text=True).strip(), 'changed': [relative.as_posix()], 'files': current, 'fingerprint': hashlib.sha256(json.dumps(current, sort_keys=True).encode()).hexdigest(), 'mirror_count': 5, 'decision': '仅纳入编发对象澄清；正文/完整交付四对均为候选3、基线1。保留单独按语措辞和提示偏差、MiniMax漏脚本等反例。未证明整个2.0优于1.x，议案原型不采用。未合main、安装、推送或发布。'}
(FROZEN / 'adoption.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({k: record[k] for k in ['changed', 'fingerprint', 'mirror_count', 'decision']}, ensure_ascii=False))
