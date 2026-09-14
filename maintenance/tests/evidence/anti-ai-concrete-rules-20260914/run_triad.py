"""Test the triad increment with an unchanged historical rewrite and real three-stop route."""
from pathlib import Path
import importlib.util

ROOT=Path(__file__).resolve().parents[4]
SOURCE=ROOT/'maintenance/tests/evidence/mit-script-delivery-r1/run_eval.py'
spec=importlib.util.spec_from_file_location('triad_native',SOURCE)
runner=importlib.util.module_from_spec(spec); spec.loader.exec_module(runner)
history=(ROOT/'maintenance/tests/evidence/1.5.36-tier1-lint-anti-ai-prompts-20260804.md').read_text(encoding='utf-8')
aa02=history.split('## AA02\n',1)[1].split('\n## AA03',1)[0].strip()
runner.CASES={'aa02_summary':aa02,'narration':runner.CASES['narration']}
if __name__=='__main__':
    runner.main()
