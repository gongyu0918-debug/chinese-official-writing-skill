from pathlib import Path
import runpy,sys
E=Path(__file__).resolve().parent
sys.argv=[str(E/'run_atom.py'),str(E/'combined-depth.json')]
m=runpy.run_path(str(E/'run_atom.py'),run_name='depth_exact_repeat')
rows=[m['one'](0,'technical_control',arm,'max',repeat=True) for arm in ('baseline','candidate')]
m['save'](m['OUT']/'repeat-technical-receipts.json',rows)
