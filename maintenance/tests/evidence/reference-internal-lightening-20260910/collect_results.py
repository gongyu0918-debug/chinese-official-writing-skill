"""Bounded receipt summary; character observations are not quality scores."""
import hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];E=Path(__file__).resolve().parent
OUT=ROOT/'output/reference-internal-lightening-20260910'
ATOMS=['ai-examples','home-route-dedup','combined']
result={}
for atom in ATOMS:
 p=OUT/atom
 if not (p/'freeze.json').is_file():continue
 freeze=json.loads((p/'freeze.json').read_text(encoding='utf-8'));rows=[]
 receipt_paths=list((p/'runs').glob('*/*/*/*/receipt.json'))+list((p/'runs').glob('*/*/*/*/repeat1/receipt.json'))
 for path in sorted(receipt_paths):
  rec=json.loads(path.read_text(encoding='utf-8'));d=path.parent
  prompt=(d/'prompt.txt').read_bytes();assert hashlib.sha256(prompt).hexdigest()==rec['prompt_sha256']
  norm=prompt.decode().replace((p/'frozen input'/rec['arm']/'SKILL.md').as_posix(),'{FROZEN_SKILL}/SKILL.md')
  rec.update(path=d.relative_to(p).as_posix(),repeat='repeat1' in d.parts,normalized_prompt_sha256=hashlib.sha256(norm.encode()).hexdigest())
  f=d/'final.txt';body=f.read_text(encoding='utf-8') if f.exists() else ''
  rec.update(final_sha256=hashlib.sha256(f.read_bytes()).hexdigest() if f.exists() else None,final_non_whitespace_chars=len(re.sub(r'\s','',body)))
  mdchars=0;allchars=0;commands=0;reads=[];usage=None
  for line in (d/'trace.jsonl').read_text(encoding='utf-8').splitlines():
   try:x=json.loads(line)
   except json.JSONDecodeError:continue
   if x.get('type')=='turn.completed':usage=x.get('usage')
   item=x.get('item',{})
   if x.get('type')=='item.completed' and item.get('type')=='command_execution':
    cmd=item.get('command','');out=item.get('aggregated_output','').replace('\r\n','\n').replace('\r','\n');commands+=1;allchars+=len(out)
    if '.md' in cmd and re.search(r'Get-Content|ReadAllText|\btype\b|\bcat\b',cmd,re.I):
     mdchars+=len(out);reads+=re.findall(r'[A-Za-z0-9_-]+\.md',cmd)
  rec.update(native_usage=usage,document_command_output_lf_chars=mdchars,all_command_output_lf_chars=allchars,command_count=commands,document_read_names=sorted(set(reads)));rows.append(rec)
 primary=[r for r in rows if not r['repeat']];pairs=[]
 for provider,cases in freeze['config']['assignments'].items():
  for case in cases:
   picked=None;effort=None
   for choice in ['max','high']:
    vals={arm:next((r for r in primary if str(r['provider'])==provider and r['case']==case and r['arm']==arm and r['effort']==choice and r['valid_final']),None) for arm in ['baseline','candidate']}
    if all(vals.values()):picked=vals;effort=choice;break
   pair={'provider':provider,'case':case,'both_valid_same_effort':picked is not None,'selected_effort':effort}
   if picked:
    assert len({v['normalized_prompt_sha256'] for v in picked.values()})==1,(atom,case)
    pair['document_output_delta']=picked['candidate']['document_command_output_lf_chars']-picked['baseline']['document_command_output_lf_chars']
   pairs.append(pair)
 result[atom]={'attempts':len(rows),'technical_valid_finals':sum(r['valid_final'] for r in rows),'repeats':sum(r['repeat'] for r in rows),'pairs':pairs,'receipts':rows}
(E/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({a:{k:v for k,v in x.items() if k!='receipts'} for a,x in result.items()},ensure_ascii=False,indent=2))

