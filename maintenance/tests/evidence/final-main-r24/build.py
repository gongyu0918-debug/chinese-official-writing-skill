"""Freeze the final ordinary Skill candidate; keep the original main untouched."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / 'output/final-main-r24'
SOURCE = ROOT / 'chinese-official-writing'


def files(path):
    return {p.relative_to(path).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(path.rglob('*')) if p.is_file() and '__pycache__' not in p.parts}


before = files(SOURCE)
assert hashlib.sha256(json.dumps(before, sort_keys=True).encode()).hexdigest() == '9fade115eae2892cf4ac2af3d9587f784d2b476c200ef32ab9eca128d50ec18a'
assert not OUT.exists()
shutil.copytree(SOURCE, OUT / 'candidate', ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
refs = OUT / 'candidate/references'
p = refs / 'reference-index.md'; text = p.read_text(encoding='utf-8')
old = '请示、普通采购或经费等申请：`genre-playbook-request.md`；请批事项或必要要素拿不准时用 `genre-checklist-request.md`。'
new = '请示、普通采购或经费等申请：`genre-playbook-request.md`；审核、复核、审后改稿，或细查请批事项和办理要素时，读取 `genre-checklist-request.md`。'
assert text.count(old) == 1
p.write_text(text.replace(old, new), encoding='utf-8', newline='\n')
p = refs / 'genre-playbook-request.md'; text = p.read_text(encoding='utf-8')
body = text.split('## 请示/申请\n', 1)[1]
old = '采购进展和后续安排沿用材料状态。材料只写供应商或采购日期尚未确定时，正文停在该状态；“批准后另行确定”“按规定办理”也属于后续安排，材料未给时不补入。篇幅调整保留完整理由、申请事项和请批动作。'
new = '采购进展沿用材料状态。供应商、采购日期尚未确定时照实保留；与申请事项相称的后续建议可按拟议安排表述，具体程序、期限和承诺依材料或明确授权使用。篇幅调整保留完整理由、申请事项和请批动作。'
assert body.count(old) == 1
p.write_text('# 请示/申请\n' + body.replace(old, new), encoding='utf-8', newline='\n')
after = files(OUT / 'candidate')
changed = [p for p,h in after.items() if before[p] != h]
assert set(changed) == {'references/reference-index.md','references/genre-playbook-request.md'}
r = {'source_head': subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
     'original_main':'1ce7112303172478faa2392667a2de1098eb912c','changed_from_r23':changed,
     'before':before,'candidate':after,'fingerprint':hashlib.sha256(json.dumps(after,sort_keys=True).encode()).hexdigest()}
(OUT/'build.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in r.items() if k not in {'before','candidate'}},ensure_ascii=False))
