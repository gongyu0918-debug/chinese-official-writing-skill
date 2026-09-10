"""Archive bounded evidence, excluding model homes, credentials, caches and temp dirs."""
import hashlib,json,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
OUT=ROOT/'output/progressive-route-validation-20260910'
E=Path(__file__).resolve().parent
DEST=Path('F:/Workspaces/chinese-official-writing-skill-archives/experiments/skill-lightening-20260910/progressive-route-validation')
def sha(b):return hashlib.sha256(b).hexdigest()
records=[]
for atom in ['terminology','correspondence','correspondence-refined','word-guidance','length-alignment','combined']:
 source=OUT/atom
 if not (source/'freeze.json').is_file():continue
 freeze=json.loads((source/'freeze.json').read_text(encoding='utf-8'))
 for arm,files in freeze['hashes'].items():
  for relative,expected in files.items():assert sha((source/'frozen input'/arm/relative).read_bytes())==expected,(atom,arm,relative)
 for case,task in freeze['config']['cases'].items():
  if 'fixture' in task:assert (source/'fixtures'/(case+' 草稿.md')).read_text(encoding='utf-8')==task['fixture'],case
 paths=[source/'freeze.json']+list(source.glob('receipts*.json'))+list(source.glob('repeat*receipts.json'))
 paths+=list((source/'frozen input').rglob('*'))
 paths+=list((source/'fixtures').rglob('*')) if (source/'fixtures').exists() else []
 paths+=[p for p in (source/'runs').rglob('*') if p.is_file() and (p.name in {'prompt.txt','final.txt','receipt.json','trace.jsonl','stderr.txt'} and not {'codex-home','temp','profile'} & set(p.relative_to(source).parts) or 'work' in p.relative_to(source).parts and p.suffix in {'.docx','.py','.txt','.md'} and '__pycache__' not in p.parts)]
 entries={p.relative_to(OUT).as_posix():p for p in paths if p.is_file()}
 manifest={n:sha(p.read_bytes()) for n,p in sorted(entries.items())}
 DEST.mkdir(parents=True,exist_ok=True);dest=DEST/(atom+'.zip');assert not dest.exists(),dest
 with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED) as z:
  for n,p in entries.items():z.write(p,n)
  z.writestr('MANIFEST.json',json.dumps(manifest,ensure_ascii=False,indent=2))
 with zipfile.ZipFile(dest) as z:
  for n,h in manifest.items():assert sha(z.read(n))==h,n
 records.append({'atom':atom,'archive':str(dest),'sha256':sha(dest.read_bytes()),'files':len(entries),'verified_members':len(manifest),'frozen_inputs_unchanged':True})
(E/'archives.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(records,ensure_ascii=False,indent=2))
