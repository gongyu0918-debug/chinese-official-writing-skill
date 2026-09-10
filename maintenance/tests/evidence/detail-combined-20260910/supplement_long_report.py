import runpy,sys
from pathlib import Path
p=Path(__file__).resolve().parent
sys.argv=[str(p/'run_atom.py'),str(p/'combined.json')]
m=runpy.run_path(str(p/'run_atom.py'),run_name='supplement_module')
for arm in ['baseline','candidate']:m['one'](3,'long_report',arm)
