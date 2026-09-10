"""Five provider lanes; never concurrently occupy the same provider channel."""
import concurrent.futures,json,runpy,sys
from pathlib import Path
E=Path(__file__).resolve().parent
modules=[]
for name in ['word-guidance','length-alignment']:
 sys.argv=[str(E/'run_atom.py'),str(E/(name+'.json'))]
 m=runpy.run_path(str(E/'run_atom.py'),run_name='frozen_'+name);m['prepare']();modules.append(m)
sys.argv=[str(E/'run_atom.py'),str(E/'correspondence.json')]
prior=runpy.run_path(str(E/'run_atom.py'),run_name='exact_correspondence_repeat')
for i,case in [(1,'ordinary_letter'),(2,'complex_reply')]:
 for arm in ['baseline','candidate']:
  receipt=prior['OUT']/'runs'/str(i)/case/arm/'max/receipt.json'
  assert json.loads(receipt.read_text(encoding='utf-8'))['valid_final']
def work(i):
 out=[]
 if i in [1,2]:
  case={1:'ordinary_letter',2:'complex_reply'}[i]
  arms=['baseline','candidate'] if i%2==0 else ['candidate','baseline']
  for arm in arms:out.append(prior['one'](i,case,arm,repeat=True))
 order=modules if i%2==0 else list(reversed(modules))
 for m in order:out.extend(m['lane'](i))
 return out
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:results=list(pool.map(work,range(5)))
for m in modules:
 m['save'](m['OUT']/'receipts.json',[r for group in results for r in group if r['atom']==m['ATOM']])

prior['save'](prior['OUT']/'repeat-validation-receipts.json',[r for group in results for r in group if r['atom']=='correspondence'])
