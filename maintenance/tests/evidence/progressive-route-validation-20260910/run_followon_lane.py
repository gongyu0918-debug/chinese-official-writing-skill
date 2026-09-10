"""Run one explicit provider lane after shared inputs are prepared."""
import json,runpy,sys
from pathlib import Path
E=Path(__file__).resolve().parent
i=int(sys.argv[1]);assert i in range(5)
modules=[]
for name in ['word-guidance','length-alignment']:
 sys.argv=[str(E/'run_atom.py'),str(E/(name+'.json'))]
 modules.append(runpy.run_path(str(E/'run_atom.py'),run_name='prepared_'+name))
if i in [1,2]:
 sys.argv=[str(E/'run_atom.py'),str(E/'correspondence.json')]
 prior=runpy.run_path(str(E/'run_atom.py'),run_name='exact_repeat')
 case={1:'ordinary_letter',2:'complex_reply'}[i]
 arms=['baseline','candidate'] if i%2==0 else ['candidate','baseline']
 for arm in arms:prior['one'](i,case,arm,repeat=True)
for m in (modules if i%2==0 else list(reversed(modules))):
 rows=m['lane'](i);m['save'](m['OUT']/('receipts-lane-'+str(i)+'.json'),rows)
