import runpy,sys,concurrent.futures
from pathlib import Path
p=Path(__file__).resolve().parent
sys.argv=[str(p/'run_atom.py'),str(p/'diagnostics.json')]
m=runpy.run_path(str(p/'run_atom.py'),run_name='diagnostics_module')
m['prepare']()
def lane(i):
 case=m['config']['assignments'][str(i)][0]
 rec=m['one'](i,case,'baseline');out=[rec]
 if not rec['valid_final']:out.append(m['one'](i,case,'baseline','high'))
 return out
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:rows=list(pool.map(lane,range(5)))
m['save'](m['OUT']/'receipts.json',[x for row in rows for x in row])
