"""One exact-prompt max/max repeat for the isolated wording discrepancy."""
import runpy
import sys
from pathlib import Path

p = Path(__file__).resolve().parent
sys.argv = [str(p / 'run_atom.py'), str(p / 'mode-dedup.json')]
runner = runpy.run_path(str(p / 'run_atom.py'), run_name='repeat_module')
for arm in ['candidate', 'baseline']:
    runner['one'](1, 'explicit_rewrite', arm, repeat=True)
