"""Bind R12 independent reviews and summarize only valid paired execution."""
from pathlib import Path
from collections import Counter
import json

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
BLIND = ROOT / 'output/common-layer-blind-r12'
mappings = {}
for group in ['unified', 'coverage', 'retry']:
    for row in json.loads((BLIND / f'mapping-{group}.json').read_text(encoding='utf-8-sig')):
        mappings[row['id']] = row
rows = []
for group in ['unified', 'more']:
    for verdict in json.loads((BLIND / f'verdicts-{group}.json').read_text(encoding='utf-8-sig')):
        mapping = mappings[verdict['id']]
        row = {**verdict, 'mapping': mapping, 'comparison': 'R8+80 to R12' if 'coverage' in mapping['run'] else 'R10 to R12'}
        for field in ['body', 'delivery']:
            letter = verdict[field + '_winner']
            row[field + '_preferred_arm'] = mapping[letter]['arm'] if letter in ['A','B'] else 'tie'
        if verdict['id'] == 'C05':
            row['calibration'] = 'Independent review-more appendix: with an explicit 80-character hard minimum both outputs are 79 and short by one. Minor length noncompliance; relative factual/language verdict unchanged. Preserve original JSON.'
        if verdict['id'] == 'C04':
            row['execution_limit'] = 'Both manuscripts add unsupported specifics. Baseline additionally had nested Windows PowerShell decoding/command failures. Its much weaker output is not an attributable rule-quality win.'
        rows.append(row)
summary = {name: {field: dict(Counter(r[field+'_preferred_arm'] for r in rows if r['comparison']==name)) for field in ['body','delivery']} for name in ['R10 to R12','R8+80 to R12']}
metrics = {}
for name in ['R10 to R12','R8+80 to R12']:
    records=[]
    for row in rows:
        if row['comparison']!=name:continue
        group = row['mapping']['run'].split('r12-',1)[1]
        inspected=json.loads((HERE / f'execution-r12-{group}.json').read_text(encoding='utf-8-sig'))['records']
        records.extend(r for r in inspected if r['case']==row['mapping']['case'] and r['model']==row['mapping']['model'])
    metrics[name] = {}
    for arm in ['baseline','candidate']:
        arm_rows=[r for r in records if r['arm']==arm]
        metrics[name][arm]={key:round(sum(r[key] for r in arm_rows),2) for key in ['read_chars_unique','uncached_input_tokens','input_tokens','output_tokens','commands','seconds']}
        metrics[name][arm]['calls']=len(arm_rows)
        metrics[name][arm]['anti_ai_page_returned']=sum('references/anti-ai-patterns.md' in r['unique_pages'] for r in arm_rows)
        metrics[name][arm]['tasks_with_prose_command']=sum(any(s['script']=='prose_lint.py' for s in r['script_calls']) for r in arm_rows)
report={'note':'Different baselines remain separate. Failed original explanation pair excluded from paired comparison, then both arms rerun. Raw failures remain archived. Preferences include mild differences, not hard-failure counts. Cost metrics do not establish effective or equivalent checks.', 'summary':summary, 'paired_execution':metrics, 'records':rows}
(HERE / 'quality-r12.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n',encoding='utf-8')
print(json.dumps({'summary':summary,'paired_execution':metrics},ensure_ascii=False))
