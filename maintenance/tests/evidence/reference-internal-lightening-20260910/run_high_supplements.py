"""One high/high supplement per technically incomplete max repeat."""
import concurrent.futures,importlib.util,sys
from pathlib import Path
E=Path(__file__).resolve().parent
def module(name):
 sys.argv=[str(E/'run_atom.py'),str(E/(name+'.json'))]
 spec=importlib.util.spec_from_file_location('high_'+name,E/'run_atom.py')
 m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
targets=[(module('combined'),2,'opinion_rewrite'),(module('home-route-dedup'),4,'limited_commitment')]
def run(target):
 m,i,case=target
 rows=[]
 for arm in ['candidate','baseline']:
  rec=m.one(i,case,arm,'high')
  base=m.OUT/'runs'/str(i)/case/arm
  assert (base/'high/prompt.txt').read_bytes()==(base/'max/prompt.txt').read_bytes()
  rows.append(rec)
 m.save(m.OUT/('supplement-high-'+case+'-receipts.json'),rows)
 return rows
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(run,targets))
