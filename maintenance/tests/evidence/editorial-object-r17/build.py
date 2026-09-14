"""Clarify publication object versus reported topic in one frozen leaf."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[4]
SOURCE = ROOT/'chinese-official-writing'
DEST = ROOT/'output/editorial-object-r17'
assert not DEST.exists()
assert not subprocess.check_output(['git','status','--porcelain','--','chinese-official-writing'],cwd=ROOT,text=True).strip()
for arm in ['baseline','candidate']:
    shutil.copytree(SOURCE,DEST/arm,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
relative='references/genre-playbook-editorial-note.md'
path=DEST/'candidate'/relative
raw=path.read_bytes()
old='结合选题背景、材料主题和编发目的，概括所编发内容的关系及阅读重点；有据的评价、分析和期望可融入其中。'
new='以本轮实际刊登的稿件或材料为编发对象，以其中报道、讨论的事项为主题，结合选题背景与编发目的说明阅读重点；多份内容按材料给定的编发关系组织，有据的评价、分析和期望可融入其中。'
assert raw.count(old.encode())==1
path.write_bytes(raw.replace(old.encode(),new.encode()))
def files(root):
    return {p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(root.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc'}
before,after=files(DEST/'baseline'),files(DEST/'candidate')
assert {k for k in before if before[k]!=after[k]}=={relative}
assert files(SOURCE)==before
record={'source_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'changed':[relative],'files':{'baseline':before,'candidate':after},'fingerprints':{a:hashlib.sha256(json.dumps(v,sort_keys=True).encode()).hexdigest() for a,v in [('baseline',before),('candidate',after)]},'source_unchanged':True}
(DEST/'build.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'changed':record['changed'],'fingerprints':record['fingerprints']},ensure_ascii=False))
