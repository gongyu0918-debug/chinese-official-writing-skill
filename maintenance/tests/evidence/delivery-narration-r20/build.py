"""Rebuild the final delivery/navigation candidate from its reviewed exact bytes."""
from pathlib import Path
import hashlib
import json
import re
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[4]
SOURCE = ROOT / 'chinese-official-writing'
HERE = Path(__file__).resolve().parent
DEST = ROOT / 'output/delivery-narration-r20-final-rebuild'
assert not DEST.exists()
assert not subprocess.check_output(['git','status','--porcelain','--','chinese-official-writing'],cwd=ROOT,text=True).strip()
for arm in ['baseline','candidate']:
    shutil.copytree(SOURCE,DEST/arm,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
relatives = ['SKILL.md', 'references/writing-rules.md']
for relative in relatives:
    (DEST/'candidate'/relative).write_bytes((HERE/('final-candidate-'+Path(relative).name)).read_bytes())
def files(root):
    return {p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(root.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc'}
before,after=files(DEST/'baseline'),files(DEST/'candidate')
assert set(before)==set(after)
assert {k for k in before if before[k]!=after[k]}==set(relatives)
assert files(SOURCE)==before
sizes={}
for arm in ['baseline','candidate']:
    text=''.join((DEST/arm/name).read_text(encoding='utf-8-sig') for name in relatives)
    sizes[arm]={'chars':len(text),'nonspace':len(re.sub(r'\s','',text))}
    common=(DEST/arm/'references/writing-rules.md').read_text(encoding='utf-8-sig')
    assert common.index('第二步') < common.index('draft_length.py') < common.index('第三步') < common.index('anti-ai-patterns.md') < common.index('prose-lint-usage.md') < common.index('第四步')
record={'source_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'changed':relatives,'sizes':sizes,'files':{'baseline':before,'candidate':after},'fingerprints':{a:hashlib.sha256(json.dumps(v,sort_keys=True).encode()).hexdigest() for a,v in [('baseline',before),('candidate',after)]}}
(DEST/'build.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:record[k] for k in ['changed','sizes','fingerprints']},ensure_ascii=False))
