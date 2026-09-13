"""Build one shared independent-review prototype, preserving all other bytes."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
SOURCE = ROOT/'chinese-official-writing'
DEST = ROOT/'output/independent-review-r21'
assert not DEST.exists()
assert not subprocess.check_output(['git','status','--porcelain','--','chinese-official-writing'],cwd=ROOT,text=True).strip()
for arm in ['baseline','candidate']:
    shutil.copytree(SOURCE,DEST/arm,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
addition = '''宿主提供独立上下文的 subagent（子代理）时，主 Agent 优先发起一次独立复核，使用新上下文。提供用户需求、有效材料、拟交付全文（含文后提示）、主文种页及 `review-checklist.md`、`anti-ai-patterns.md`，起草对话和自查结论留在主上下文。复核者按这些规则检查旁白与自证、事实状态及正文/提示隔离，返回具体位置、问题和改法，直接交回主 Agent。主 Agent 核实并修正已确认问题，实际遗留事项按第四步提示。宿主没有子代理能力时，继续完成本页的复核。'''
p=DEST/'candidate/references/writing-rules.md'
s=p.read_text(encoding='utf-8');anchor='## 第四步：交付';assert s.count(anchor)==1
p.write_text(s.replace(anchor,addition+'\n\n'+anchor),encoding='utf-8')
p=DEST/'candidate/references/review-checklist.md';s=p.read_text(encoding='utf-8')
old='\n确需独立复核时，提供稿件、判断所需材料、范围及来源，依据证据处理分歧。\n'
assert s.count(old)==1;p.write_text(s.replace(old,''),encoding='utf-8')
def files(root):
    return {p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(root.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc'}
before,after=files(DEST/'baseline'),files(DEST/'candidate')
changed=[k for k in before if before[k]!=after[k]]
assert set(changed)=={'references/writing-rules.md','references/review-checklist.md'}
for relative in changed:
    (HERE/('candidate-'+Path(relative).name)).write_bytes((DEST/'candidate'/relative).read_bytes())
record={'source_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'changed':changed,'files':{'baseline':before,'candidate':after},'fingerprints':{a:hashlib.sha256(json.dumps(v,sort_keys=True).encode()).hexdigest() for a,v in [('baseline',before),('candidate',after)]}}
(DEST/'build.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'changed':changed,'fingerprints':record['fingerprints']},ensure_ascii=False))
