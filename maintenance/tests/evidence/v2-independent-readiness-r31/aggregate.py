"""Summarize matched native calls only; no automated semantic verdict."""
from pathlib import Path
import json
import statistics
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[4]
OUT=ROOT/'output/v2-readiness-r31'
kinds={'core':'v1','qwen2':'v1','deepseek':'v1','glmflash':'v1','word':'v1','minutes-retry':'v1','parent':'v2-parent','script-delta':'script-delta'}
pairs=[]
all_calls=[]
for batch,kind in kinds.items():
    folder=OUT/batch
    subprocess.run([sys.executable,str(Path(__file__).with_name('collect.py')),str(folder)],check=True,stdout=subprocess.DEVNULL)
    rows=json.loads((folder/'observations.json').read_text(encoding='utf-8'))
    all_calls.extend({'batch':batch,**row} for row in rows)
    for key in sorted({(r['model'],r['case']) for r in rows}):
        pair={r['arm']:r for r in rows if (r['model'],r['case'])==key}
        if set(pair)=={'baseline','candidate'} and not any(x['invalid'] for x in pair.values()):
            pairs.append({'batch':batch,'kind':kind,'model':key[0],'case':key[1],**pair})
summary={}
for kind in ('v1','v2-parent','script-delta'):
    group=[p for p in pairs if p['kind']==kind]
    summary[kind]={'pairs':len(group)}
    for arm in ('baseline','candidate'):
        rows=[p[arm] for p in group]
        summary[kind][arm]={
            'seconds_sum':round(sum(r['seconds'] for r in rows),2),
            'seconds_median':statistics.median(r['seconds'] for r in rows) if rows else None,
            'full_returned_chars':sum(r['full_returned_chars'] for r in rows),
            'usage':{key:sum(r['usage'][key] for r in rows) for key in ('input_tokens','cached_input_tokens','uncached_input_tokens','output_tokens')}}
result={'native_calls':len(all_calls),'valid_calls':sum(not r['invalid'] for r in all_calls),
        'invalid_calls':[{'batch':r['batch'],'file':r['file'],'reasons':r['invalid']} for r in all_calls if r['invalid']],
        'matched_pairs':len(pairs),'summary':summary,'pairs':pairs}
(OUT/'aggregate.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k!='pairs'},ensure_ascii=False,indent=2))
