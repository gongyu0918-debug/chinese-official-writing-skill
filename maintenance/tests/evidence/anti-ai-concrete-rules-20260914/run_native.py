"""Reuse the native isolated runner for three unchanged historical prompts."""
from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parents[4]
SOURCE = ROOT/'maintenance/tests/evidence/mit-script-delivery-r1/run_eval.py'
spec = importlib.util.spec_from_file_location('anti_ai_native', SOURCE)
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)
runner.CASES = {name:runner.CASES[name] for name in (
    'commentary_review_rewrite','narration','motion_separate_amendments')}

if __name__ == '__main__':
    runner.main()
