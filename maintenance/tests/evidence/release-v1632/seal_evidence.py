"""Seal scoped release evidence, including failures and engineering logs."""
import hashlib,json,re,subprocess
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
ROOT=Path(__file__).resolve().parents[4]
E=Path(__file__).resolve().parent
OUT=ROOT/'output/release-v1632-writing'
receipts=json.loads((E/'receipts.json').read_text(encoding='utf-8'))
rows=[]
for r in receipts:
 if not r['valid_final']:continue
 d=OUT/'runs'/str(r['provider_index'])/r['case']/r['arm']/r['effort']
 reads=set()
 for l in (d/'trace.jsonl').read_text(encoding='utf-8').splitlines():
  ev=json.loads(l);it=ev.get('item',{})
  if ev.get('type')=='item.completed' and it.get('type')=='command_execution' and it.get('exit_code')==0 and it.get('aggregated_output'):
   reads.update(re.findall(r'(?:SKILL|[a-z][a-z-]+)\.md',it.get('command','')))
 rows.append({'provider':r['provider_index'],'case':r['case'],'arm':r['arm'],'effort':r['effort'],'returned_file_names':sorted(reads),'final_sha256':hashlib.sha256((d/'final.txt').read_bytes()).hexdigest()})
assert len(rows)==12
summary={'pairs':6,'attempts':len(receipts),'valid_finals':len(rows),'same_effort_pairs':5,'fallback':'Alibaba channel2 advisory baseline max timeout300, high valid; not max/max causal pair','rows':rows,'root_review':'All pairs manually reviewed. News, request, complaint preserve supplied amounts/dates/states. Commentary both arms make overly strong inference; remediation both infer operational shortcomings while allowing general future measures. Advisory baseline high adds daily work; candidate max adds organization of personnel. Both preserve undecided technical plan/person/time; the mixed-effort pair cannot establish causation. Execution narration and such background expansion are existing shared risks, not claimed fixed. No confirmed new route/leaf loss or stable candidate-only quality regression in the public-baseline transfer check.','limits':'Five cheap channels, two Alibaba routes one model family; six transfer pairs supplement prior independent atom and combined evidence, not full coverage or zero-error guarantee.'}
(E/'writing-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
files={p for p in (OUT/'frozen').rglob('*') if p.is_file()}
for name in ['final.txt','prompt.txt','receipt.json','trace.jsonl','stderr.txt']:
 files.update((OUT/'runs').glob('*/*/*/*/'+name))
files.update(p for p in (ROOT/'output/release-v1632-engineering').glob('*') if p.is_file())
files.update(p for p in (ROOT/'output/release-v1632').glob('*-dry-run.json'))
files.update(p for p in E.iterdir() if p.is_file() and p.name!='archive.json')
files.add(ROOT/'maintenance/docs/release-v1632-engineering.md')
manifest={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(files)}
a=Path('F:/Workspaces/chinese-official-writing-skill-archives/experiments/skill-lightening-20260909/v1632-release-evidence.zip')
with ZipFile(a,'x',compression=ZIP_DEFLATED) as z:
 for n in manifest:z.write(ROOT/n,n)
 z.writestr('manifest.json',json.dumps(manifest,ensure_ascii=False,indent=2))
with ZipFile(a) as z:
 assert z.testzip() is None
 for n,h in manifest.items():assert hashlib.sha256(z.read(n)).hexdigest()==h
record={'archive':str(a),'sha256':hashlib.sha256(a.read_bytes()).hexdigest(),'members_verified':len(manifest),'scope':'All public-baseline transfer attempts, frozen product, engineering failures and corrections, package/dry-run evidence; no profiles or credentials.'}
(E/'archive.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(record,ensure_ascii=False))
