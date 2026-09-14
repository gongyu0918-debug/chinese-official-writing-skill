"""Prototype: incorporate short-format semantics into the common rules; no short route."""
from pathlib import Path
import difflib
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parents[4]
SOURCE = ROOT / 'output/common-layer-experiment-r10/candidate'
DEST = ROOT / 'output/common-layer-unified-r12'
SKILL = DEST / 'skill'
assert not DEST.exists(), 'Keep previous frozen candidates intact'
shutil.copytree(SOURCE, SKILL, ignore=shutil.ignore_patterns('__pycache__'))

def replace(name, old, new):
    p = SKILL / name
    text = p.read_text(encoding='utf-8-sig')
    assert text.count(old) == 1, (name, old)
    p.write_text(text.replace(old, new), encoding='utf-8', newline='\n')

replace('SKILL.md', '- **材料较少或短稿**：在信息选择后按需读 `references/task-route-cards.md` 和 `references/short-draft-naturalness.md`；短路径压缩流程和篇幅动作，同时保留当前稿件的主文种规则。\n', '')
replace('references/reference-index.md', '- 短稿、只有上限、短正文自然度：`short-draft-naturalness.md`。\n', '')
replace('references/writing-rules.md',
        '按主文种组织必要要素和合理衔接。普通完整短稿至少 80 字；材料中的缘由、用途和作用要表达完整。局部替换、字段处理或用户明确要求更短时，按实际任务范围处理。短稿可以用自然段承接章节功能；用户已有标题、顺序和模板优先。',
        '按主文种写全必要要素、缘由、用途和合理衔接。普通完整短稿至少 80 字；局部替换、字段处理或用户明确要求更短时，按实际任务范围处理。\n\n围绕事项组织自然段，一两句话能够说清的内容直接写入段内；章节功能可由自然段承接，标题和编号用于区分事项、方便查阅。用户已有标题、顺序、字段和模板优先。完成文种动作即可收束，用户指定尾语照录。篇幅上限无需填满，保留事实和有作用的分析。')
for name in ('task-route-cards.md', 'short-draft-naturalness.md'):
    path = (SKILL / 'references' / name).resolve()
    assert path.parent == (SKILL / 'references').resolve()
    assert (SOURCE / 'references' / name).is_file()
    path.unlink()

before = {p.relative_to(SOURCE).as_posix(): p for p in SOURCE.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
after = {p.relative_to(SKILL).as_posix(): p for p in SKILL.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
changes = []
for name in sorted(before.keys() | after.keys()):
    a = before[name].read_text(encoding='utf-8-sig') if name in before else ''
    b = after[name].read_text(encoding='utf-8-sig') if name in after else ''
    if a != b:
        changes.extend(difflib.unified_diff(a.splitlines(True), b.splitlines(True), fromfile='r10/' + name, tofile='r12/' + name))
manifest = {name: hashlib.sha256(p.read_bytes()).hexdigest() for name, p in sorted(after.items())}
record = {'source': SOURCE.relative_to(ROOT).as_posix(), 'candidate': SKILL.relative_to(ROOT).as_posix(), 'files': manifest,
          'manifest_sha256': hashlib.sha256(json.dumps(manifest, sort_keys=True).encode()).hexdigest(),
          'note': 'Only fold short-format and local-task semantics into existing owners. R11 length-handling sentence is not included. Scripts and genre contents unchanged. Not adopted.'}
(DEST / 'build.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
(DEST / 'changes.diff').write_text(''.join(changes), encoding='utf-8')
print(json.dumps({'files': len(manifest), 'manifest_sha256': record['manifest_sha256'], 'changed_paths': [x[4:].strip() for x in changes if x.startswith('+++ ')]}, ensure_ascii=False))
