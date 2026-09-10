"""Exact same-effort repeat for the combined candidate's compiler-actor addition."""
import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location('atom',Path(__file__).with_name('run_atom.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
rows=[m.one(2,'opinion_rewrite',arm,'max',True) for arm in ['baseline','candidate']]
m.save(m.OUT/'repeat-opinion_rewrite-receipts.json',rows)
