"""Apply the reviewed development candidate; never touch main or installations."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[4]
OLD = ROOT / 'output/reference-integration-r16/baseline'
SOURCE = ROOT / 'output/reference-integration-r16-final/candidate'
SCRIPT = ROOT / 'output/prose-business-conditional-r16/candidate/scripts/prose_lint.py'
FROZEN = ROOT / 'output/reference-integration-r16-adopted/candidate'
TARGET = ROOT / 'chinese-official-writing'
assert subprocess.check_output(['git', 'branch', '--show-current'], cwd=ROOT, text=True).strip() == 'codex/reference-rewrite-20260912'
assert not subprocess.check_output(['git', 'status', '--porcelain', '--', 'chinese-official-writing', 'packages'], cwd=ROOT, text=True).strip()
assert not FROZEN.exists()
assert hashlib.sha256(SCRIPT.read_bytes()).hexdigest() == 'd69f2a2f02972f1ed832f1f34af2f8ccd140033c6422f95d3637e920c42b46dc'

def files(root):
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in sorted(root.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc'}

def hashes(values):
    return {k: hashlib.sha256(v).hexdigest() for k, v in values.items()}

before = files(TARGET)
assert before == files(OLD), 'Canonical has an unrelated change'
shutil.copytree(SOURCE, FROZEN, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
(FROZEN/'scripts/prose_lint.py').write_bytes(SCRIPT.read_bytes())
after = files(FROZEN)
removed = sorted(before.keys() - after.keys())
assert removed == ['references/handling-elements.md', 'references/official-style.md']
for relative in removed:
    path = (TARGET / relative).resolve()
    assert path.is_relative_to(TARGET.resolve()) and not path.is_symlink()
    subprocess.run(['git', 'ls-files', '--error-unmatch', '--', path.relative_to(ROOT).as_posix()], cwd=ROOT, check=True, capture_output=True)
    assert path.read_bytes() == before[relative] == files(OLD)[relative]
    path.unlink()
for relative, data in after.items():
    path = TARGET / relative
    assert path.resolve().is_relative_to(TARGET.resolve())
    if before.get(relative) != data:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
assert files(TARGET) == after
record = {
    'source_head': subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
    'main_unchanged': subprocess.check_output(['git','rev-parse','main'],cwd=ROOT,text=True).strip(),
    'changed': sorted(k for k in before.keys() | after.keys() if before.get(k) != after.get(k)),
    'files': hashes(after), 'fingerprint': hashlib.sha256(json.dumps(hashes(after), sort_keys=True).encode()).hexdigest(),
    'reference_count': sum(k.startswith('references/') and k.endswith('.md') for k in after),
    'decision': '纳入继续验证的开发候选；组合并未证明写作优于基线，仍未满足1.x整体合并验收。未合main、安装、推送或发布。',
}
(FROZEN.parent/'adoption.json').write_text(json.dumps(record, ensure_ascii=False, indent=2)+'\n',encoding='utf-8')
print(json.dumps({k: record[k] for k in ['changed','fingerprint','reference_count','decision']},ensure_ascii=False))
