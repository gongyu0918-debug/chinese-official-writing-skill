"""Clarify the scope of a motion body without adding shared reading."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[4]
SOURCE = ROOT / 'chinese-official-writing'
DEST = ROOT / 'output/motion-purpose-r17'
assert not DEST.exists()
assert not subprocess.check_output(['git', 'status', '--porcelain', '--', 'chinese-official-writing'], cwd=ROOT, text=True).strip()
for arm in ['baseline', 'candidate']:
    shutil.copytree(SOURCE, DEST / arm, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
relative = 'references/genre-playbook-motion.md'
text = '''# 议案

议案用于各级人民政府依照法律程序向同级人民代表大会或者人民代表大会常务委员会提请审议事项。确认提案主体、受文机关和法定提请关系。

正文围绕审议对象，按材料概述提请缘由、已履行的准备程序，并以“现提请审议”或“请审议决定”等提出请求。材料给出主要内容或要求论证时，写清相应要点和必要性；条文、方案或详细说明由附件承载，正文准确承接其名称和事项。

采用上报、提请语气，审议结论留待受文机关作出。提案权限、审议对象或所附文本尚待明确时，保留其待定状态。完成成稿或专项核对后，按 `writing-rules.md` 完成复核与交付。
'''
(DEST / 'candidate' / relative).write_text(text, encoding='utf-8')

def files(root):
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(root.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc'}

before, after = files(DEST / 'baseline'), files(DEST / 'candidate')
assert set(before) == set(after)
assert {k for k in before if before[k] != after[k]} == {relative}
assert files(SOURCE) == before
record = {'source_head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(), 'changed': [relative], 'files': {'baseline': before, 'candidate': after}, 'fingerprints': {a: hashlib.sha256(json.dumps(v, sort_keys=True).encode()).hexdigest() for a, v in [('baseline', before), ('candidate', after)]}, 'source_unchanged': True}
(DEST / 'build.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'changed': record['changed'], 'fingerprints': record['fingerprints']}, ensure_ascii=False))
