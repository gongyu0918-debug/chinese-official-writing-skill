"""Preserve the original gate failure and bounded repair results."""
import hashlib,json,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];E=Path(__file__).resolve().parent
src=ROOT/'output/reference-internal-lightening-20260910/engineering'
dest=Path('F:/Workspaces/chinese-official-writing-skill-archives/experiments/skill-lightening-20260910/reference-internal-lightening/engineering.zip')
files=['unittest-full.txt','unittest-affected.txt','baseline-gate.txt']
manifest={n:hashlib.sha256((src/n).read_bytes()).hexdigest() for n in files}
dest.parent.mkdir(parents=True,exist_ok=True);assert not dest.exists()
with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED) as z:
 for n in files:z.write(src/n,n)
 z.writestr('MANIFEST.json',json.dumps(manifest,indent=2))
with zipfile.ZipFile(dest) as z:
 for n,h in manifest.items():assert hashlib.sha256(z.read(n)).hexdigest()==h
r={'full_suite':{'command':"python -m unittest discover -s maintenance/tests -p 'test_*.py'",'executed_methods':850,'passed_methods':849,'failed_methods':1,'failed_subtests':6,'seconds':149.928,'failure':'test_lightened_indices_resolve_from_each_skill_root_and_keep_quality_bridges required the duplicate footer sentence'},
 'repair':'Assert the unchanged primary fallback and exact retained quality bridge instead of a second copy of the route condition; no product changes to satisfy the gate.',
 'affected':{'command':'python -m unittest maintenance.tests.test_real_prompt_ablation maintenance.tests.test_repository_reachability maintenance.tests.test_skill_boundary','passed':102,'total':102},
 'baseline_control':'Updated test applied to unchanged main 36653d76: 1 method / 6 package subtests passed.',
 'quick_validate':'Canonical and four regular adapter skills: 5/5; OpenClaw metadata boundary retained and covered by unittest.',
 'full_suite_repeated':False,'untouched_methods_already_passed':748,
 'archive':str(dest),'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'verified_members':len(manifest),'logs':manifest}
(E/'engineering.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'archive':str(dest),'verified_members':len(manifest)},ensure_ascii=False))
