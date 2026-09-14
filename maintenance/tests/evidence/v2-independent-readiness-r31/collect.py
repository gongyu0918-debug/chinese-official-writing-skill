"""Collect file/read/usage facts and anonymous drafts, without scoring prose."""
from pathlib import Path
import hashlib
import json
import re
import sys

run = Path(sys.argv[1]).resolve()
binding = json.loads((run / 'binding.json').read_text(encoding='utf-8'))
rows = []
for p in sorted(run.glob('*.result.json')):
    d = json.loads(p.read_text(encoding='utf-8'))
    folder = 'candidate' if d['arm'] == 'candidate' else 'main'
    product = run / 'snapshots' / folder
    calls = d['commands']
    outputs = '\n'.join(x.get('aggregated_output', '') for x in calls if x.get('exit_code') == 0).replace('\r','')
    numbered_output = re.sub(r'^\s*\d+\s*:\s?', '', outputs, flags=re.M)
    pages = {}
    for page in [product / 'SKILL.md', *sorted((product / 'references').glob('*.md'))]:
        content = page.read_text(encoding='utf-8-sig').replace('\r\n','\n').strip()
        if content in outputs or content in numbered_output:
            pages[page.relative_to(product).as_posix()] = len(content)
    usage = {key: sum((u or {}).get(key,0) or 0 for u in d.get('usage',[])) for key in ('input_tokens','cached_input_tokens','output_tokens')}
    usage['uncached_input_tokens'] = usage['input_tokens'] - usage['cached_input_tokens']
    script_calls = []
    for x in calls:
        command = x.get('command','')
        if re.search(r'python[^\r\n]*?(?:draft_length|prose_lint)\.py', command, re.I):
            script_calls.append({'command':command,'exit_code':x.get('exit_code')})
    rows.append({k:d[k] for k in ('model','case','arm','seconds','invalid','draft_sha256')} | {
        'file':p.name,'usage':usage,'full_returned_pages':pages,'full_returned_chars':sum(pages.values()),
        'commands':len(calls),'failed_commands':sum(x.get('exit_code')!=0 for x in calls), 'script_calls':script_calls})
(run/'observations.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
summary = {}
for arm in ('baseline','candidate'):
    selected = [r for r in rows if r['arm']==arm and not r['invalid']]
    summary[arm] = {'valid':len(selected),'seconds':round(sum(x['seconds'] for x in selected),2),
        'full_returned_chars':sum(x['full_returned_chars'] for x in selected),
        'usage':{key:sum(x['usage'][key] for x in selected) for key in ('input_tokens','cached_input_tokens','uncached_input_tokens','output_tokens')}}
print(json.dumps({'calls':len(rows),'invalid':[r['file'] for r in rows if r['invalid']],'summary':summary},ensure_ascii=False))

if len(sys.argv) > 2:
    dest=Path(sys.argv[2]).resolve()
    dest.mkdir(parents=True,exist_ok=False)
    pairs=[]
    for key in sorted({(r['model'],r['case']) for r in rows}):
        pair={r['arm']:r for r in rows if (r['model'],r['case'])==key}
        if set(pair)!= {'baseline','candidate'} or any(r['invalid'] for r in pair.values()):
            continue
        pid=f'P{len(pairs)+1:02d}'
        arms=('candidate','baseline') if len(pairs)%2==0 else ('baseline','candidate')
        packet=f'{pid}\n\n用户原题\n{binding["cases"][key[1]]}\n'
        entry={'id':pid,'model':key[0],'case':key[1],'arms':{}}
        for label,arm in zip(('A','B'),arms):
            path=run/pair[arm]['file'].replace('.result.json','.final.txt')
            raw=path.read_bytes()
            original=raw.decode('utf-8-sig')
            pattern=re.compile(r'(?<=[/\\])m\d+-[^/\\\s<>]*-(?:baseline|candidate)(?=[/\\])')
            swaps=[m.group(0) for m in pattern.finditer(original)]
            displayed=pattern.sub('run-X',original)
            packet+=f'\n完整交付 {label}\n{displayed}\n'
            entry['arms'][label]={'source':str(path),'arm':arm,'sha256':hashlib.sha256(raw).hexdigest(),'identity_path_substitutions':swaps}
        target=dest/f'{pid}.txt'
        target.write_text(packet,encoding='utf-8')
        entry['packet_sha256']=hashlib.sha256(target.read_bytes()).hexdigest()
        pairs.append(entry)
    (dest.parent/(dest.name+'-mapping.private.json')).write_text(json.dumps(pairs,ensure_ascii=False,indent=2),encoding='utf-8')
    print('anonymous pairs',len(pairs))
