"""Five provider lanes; never concurrently occupy the same provider channel."""
import concurrent.futures,json,runpy,sys
from pathlib import Path
E=Path(__file__).resolve().parent
modules=[]
for name in ['terminology','correspondence']:
 sys.argv=[str(E/'run_atom.py'),str(E/(name+'.json'))]
 m=runpy.run_path(str(E/'run_atom.py'),run_name='frozen_'+name);m['prepare']();modules.append(m)
def work(i):
 out=[]
 order=modules if i%2==0 else list(reversed(modules))
 for m in order:out.extend(m['lane'](i))
 return out
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:results=list(pool.map(work,range(5)))
for m in modules:
 m['save'](m['OUT']/'receipts.json',[r for group in results for r in group if r['atom']==m['ATOM']])
