"""Address two inherited cold-review conflicts without changing frozen samples."""
from pathlib import Path
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parents[4]
SOURCE = ROOT / 'output/reference-integration-r16/candidate'
DEST = ROOT / 'output/reference-integration-r16-rule-refinement/candidate'
assert not DEST.exists()
shutil.copytree(SOURCE, DEST, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
changes = {
    'references/compression-details.md': (
        '上下限采用用户给出的数值，只有一侧限制时只传对应参数；大致篇幅可只统计实际字数，再结合文种和材料调整。',
        '上下限按用户要求和共性写作页的适用范围传入；用户只给上限时，仍保留适用的默认下限。约数目标结合文种和材料取合理范围。',
    ),
    'references/genre-playbook-news-commentary.md': (
        '本页的评论专项核对：使用直接判断、事实解释和自然衔接，将否定后转折改为直接判断，合并真正同义的段落；事实段只核对，不重写；评论推演逐句核对事实依据和适用范围，只修改判断强度超过材料支持的句子。',
        '评论推演逐句核对依据和适用范围，调整超过依据的判断；事实段保持来源口径，按本轮范围修正语言与篇幅。合并同义复述和空泛转折，保留有实际作用的否定与比较。',
    ),
}
for relative, (old, new) in changes.items():
    path = DEST / relative
    raw = path.read_bytes()
    assert raw.count(old.encode()) == 1
    path.write_bytes(raw.replace(old.encode(), new.encode()))
def files(root):
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(root.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc'}
before, after = files(SOURCE), files(DEST)
assert {k for k in before if before[k] != after[k]} == set(changes)
record = {'source': str(SOURCE), 'candidate': str(DEST), 'changed': list(changes), 'files': after, 'fingerprint': hashlib.sha256(json.dumps(after, sort_keys=True).encode()).hexdigest(), 'notes': 'F01/F02规则修正；F03单脚本原型另存。冻结原候选及写稿不变。'}
(DEST.parent/'build.json').write_text(json.dumps(record, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print(json.dumps({k:record[k] for k in ['changed','fingerprint']}, ensure_ascii=False))
