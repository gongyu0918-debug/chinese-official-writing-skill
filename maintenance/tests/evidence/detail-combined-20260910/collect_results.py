import json,re,hashlib,statistics
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];E=Path(__file__).resolve().parent;OUT=ROOT/'output/detail-combined-20260910'
result={}
for atom in ['combined','mode-dedup']:
 p=OUT/atom;freeze=json.loads((p/'freeze.json').read_text(encoding='utf-8'));rows=[]
 for r in sorted((p/'runs').rglob('receipt.json')):
  rec=json.loads(r.read_text(encoding='utf-8'));d=r.parent;assert hashlib.sha256((d/'prompt.txt').read_bytes()).hexdigest()==rec['prompt_sha256']
  rec['path']=d.relative_to(p).as_posix();rec['repeat']='repeat1' in d.parts
  f=d/'final.txt';body=f.read_text(encoding='utf-8') if f.exists() else '';rec['chars']=len(re.sub(r'\s','',body));rec['final_sha256']=hashlib.sha256(f.read_bytes()).hexdigest() if f.exists() else None
  mdchars=0;allchars=0;commands=0;reads=[];usage=None
  for line in (d/'trace.jsonl').read_text(encoding='utf-8').splitlines():
   try:x=json.loads(line)
   except json.JSONDecodeError:continue
   if x.get('type')=='turn.completed':usage=x.get('usage')
   i=x.get('item',{})
   if x.get('type')=='item.completed' and i.get('type')=='command_execution':
    cmd=i.get('command','');output=i.get('aggregated_output','');commands+=1;allchars+=len(output)
    if '.md' in cmd and re.search(r'Get-Content|ReadAllText|\btype\b|\bcat\b',cmd,re.I):
     mdchars+=len(output);reads.extend(re.findall(r'[A-Za-z0-9_-]+\.md',cmd))
  rec.update(native_usage=usage,document_command_output_chars=mdchars,all_command_output_chars=allchars,command_count=commands,document_read_names=sorted(set(reads)));rows.append(rec)
 prim=[r for r in rows if not r['repeat']];pairs=[]
 assignments={k:list(v) for k,v in freeze['config']['assignments'].items()}
 if atom=='combined':assignments['3'].append('long_report')
 for provider,cases in assignments.items():
  for case in cases:
   selected={}
   for arm in ['baseline','candidate']:
    valid=[r for r in prim if str(r['provider'])==provider and r['case']==case and r['arm']==arm and r['valid_final']]
    selected[arm]=valid[0] if valid else None
   pair={'provider':provider,'case':case,'both_valid':all(selected.values()),'both_max':all(r and r['effort']=='max' for r in selected.values())}
   if pair['both_max']:pair['document_output_delta']=selected['candidate']['document_command_output_chars']-selected['baseline']['document_command_output_chars']
   pairs.append(pair)
 result[atom]={'attempts':len(rows),'valid':sum(r['valid_final'] for r in rows),'pairs':pairs,'receipts':rows}
(E/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({a:{k:v for k,v in x.items() if k!='receipts'} for a,x in result.items()},ensure_ascii=False,indent=2))
