"""Wait for each home lane before running its frozen combined cases."""
import concurrent.futures,importlib.util,json,time
from pathlib import Path
spec=importlib.util.spec_from_file_location('atom',Path(__file__).with_name('run_atom.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
m.prepare()
prior=m.ROOT/'output/reference-internal-lightening-20260910/home-route-dedup'
frozen=json.loads((prior/'freeze.json').read_text(encoding='utf-8'))
def lane(i):
 case=frozen['config']['assignments'][str(i)][0]
 while True:
  paths=[prior/'runs'/str(i)/case/a/'max/receipt.json' for a in ['baseline','candidate']]
  if all(p.exists() for p in paths):
   valid=all(json.loads(p.read_text(encoding='utf-8'))['valid_final'] for p in paths)
   high=[prior/'runs'/str(i)/case/a/'high/receipt.json' for a in ['baseline','candidate']]
   if valid or all(p.exists() for p in high): break
  time.sleep(2)
 return m.lane(i)
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
 results=list(pool.map(lane,range(5)))
m.save(m.OUT/'receipts.json',[r for group in results for r in group])
