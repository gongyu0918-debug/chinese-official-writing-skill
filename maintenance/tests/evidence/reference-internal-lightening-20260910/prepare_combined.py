"""Combine frozen atoms; preserve each task verbatim for cross checks."""
import json
from pathlib import Path
E=Path(__file__).resolve().parent
a=json.loads((E/'ai-examples.json').read_text(encoding='utf-8'))
h=json.loads((E/'home-route-dedup.json').read_text(encoding='utf-8'))
c={'atom':'combined','baseline':a['baseline'],'candidate':'28ee4ed6220adcfd5ef22e7e194c5415b18fd502',
 'expected_diff':['SKILL.md','references/ai-compute-docs.md','references/ai-compute-examples.md'],
 'assignments':{str(i):a['assignments'][str(i)]+h['assignments'][str(i)] for i in range(5)},
 'cases':a['cases']|h['cases']}
(E/'combined.json').write_text(json.dumps(c,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
s=(E/'run_home_after_ai.py').read_text(encoding='utf-8')
s=s.replace('Do not overlap two experiments on the same provider lane.', 'Wait for each home lane before running its frozen combined cases.')
s=s.replace("/ai-examples'","/home-route-dedup'")
(E/'run_combined_after_home.py').write_text(s,encoding='utf-8',newline='\n')
