"""Exact-prompt repeats retain first negatives and use max on both arms."""
import concurrent.futures,importlib.util,json,sys,time
from pathlib import Path
E=Path(__file__).resolve().parent
def module(name):
 sys.argv=[str(E/'run_atom.py'),str(E/(name+'.json'))]
 spec=importlib.util.spec_from_file_location('atom_'+name,E/'run_atom.py')
 m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
targets=[(module('combined'),0,'technical_control','pending_minutes'),(module('home-route-dedup'),4,'limited_commitment','limited_commitment')]
def run(target):
 m,i,case,last=target
 prior=m.ROOT/'output/reference-internal-lightening-20260910/combined/runs'/str(i)/last
 while True:
  ps=[prior/arm/'max/receipt.json' for arm in ['baseline','candidate']]
  if all(p.exists() for p in ps):
   valid=all(json.loads(p.read_text(encoding='utf-8'))['valid_final'] for p in ps)
   if valid or all((prior/arm/'high/receipt.json').exists() for arm in ['baseline','candidate']):break
  time.sleep(2)
 rows=[m.one(i,case,arm,'max',True) for arm in ['candidate','baseline']]
 m.save(m.OUT/('repeat-'+case+'-receipts.json'),rows)
 return rows
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(run,targets))
