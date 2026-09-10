"""Run a single selected provider from an already frozen configuration."""
from pathlib import Path
import runpy,sys
E=Path(__file__).resolve().parent
name=sys.argv[1];i=int(sys.argv[2]);assert name in {'correspondence-refined','combined'} and i in range(5)
sys.argv=[str(E/'run_atom.py'),str(E/(name+'.json'))]
m=runpy.run_path(str(E/'run_atom.py'),run_name='selected_'+name)
rows=m['lane'](i);m['save'](m['OUT']/('receipts-lane-'+str(i)+'.json'),rows)
