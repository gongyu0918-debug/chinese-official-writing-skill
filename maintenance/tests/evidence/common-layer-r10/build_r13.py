"""Remove duplicate workflow at the end of the index; keep attachment routing in the entrypoint."""
from pathlib import Path
import difflib
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parents[4]
SOURCE = ROOT / 'output/common-layer-unified-r12/skill'
DEST = ROOT / 'output/common-layer-index-r13'
SKILL = DEST / 'skill'
assert not DEST.exists()
shutil.copytree(SOURCE, SKILL, ignore=shutil.ignore_patterns('__pycache__'))
p = SKILL / 'SKILL.md'
text = p.read_text(encoding='utf-8-sig')
old = '一次要求多份独立稿件时逐份选路；同一稿件中的会议、采购、整改等内容按稿件用途判断。'
assert text.count(old) == 1
p.write_text(text.replace(old, '独立稿件及具有独立用途的附件分别选路；文内背景和引用按主文本用途处理。'), encoding='utf-8', newline='\n')
p = SKILL / 'references/reference-index.md'
text = p.read_text(encoding='utf-8-sig')
assert text.count('\n## 停止规则\n') == 1
p.write_text(text.split('\n## 停止规则\n', 1)[0].rstrip() + '\n', encoding='utf-8', newline='\n')
changes = []
for name in ('SKILL.md', 'references/reference-index.md'):
    a = (SOURCE / name).read_text(encoding='utf-8-sig')
    b = (SKILL / name).read_text(encoding='utf-8-sig')
    changes.extend(difflib.unified_diff(a.splitlines(True), b.splitlines(True), fromfile='r12/' + name, tofile='r13/' + name))
manifest = {p.relative_to(SKILL).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(SKILL.rglob('*')) if p.is_file() and '__pycache__' not in p.parts}
record = {'source': SOURCE.relative_to(ROOT).as_posix(), 'candidate': SKILL.relative_to(ROOT).as_posix(), 'files': manifest, 'manifest_sha256': hashlib.sha256(json.dumps(manifest, sort_keys=True).encode()).hexdigest(), 'note': 'Only two routing files changed. Common writing rules, all primary leaves and both scripts unchanged. No short/long fork or new reference.'}
(DEST / 'build.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
(DEST / 'changes.diff').write_text(''.join(changes), encoding='utf-8')
print(record['manifest_sha256'])
