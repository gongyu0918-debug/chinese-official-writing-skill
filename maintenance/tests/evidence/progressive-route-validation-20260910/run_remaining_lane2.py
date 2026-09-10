from pathlib import Path
import runpy,sys
E=Path(__file__).resolve().parent
for name in ('combined','combined-depth'):
 sys.argv=[str(E/'run_atom.py'),str(E/(name+'.json'))]
 m=runpy.run_path(str(E/'run_atom.py'),run_name='remaining_'+name)
 rows=m['lane'](2);m['save'](m['OUT']/'receipts-lane-2.json',rows)
