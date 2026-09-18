"""Reuse the native A/B harness; serialize calls within each provider."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import importlib.util
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
spec = importlib.util.spec_from_file_location(
    'scenario_native_eval', ROOT / 'maintenance/tests/evidence/mit-script-delivery-r1/run_eval.py'
)
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)
runner.CASES = json.loads((HERE / 'cases.json').read_text(encoding='utf-8'))
# Launch this driver once per provider. Pair order and native isolation remain
# the existing harness behavior; queueing never mixes two requests on a route.
runner.ThreadPoolExecutor = lambda **kwargs: ThreadPoolExecutor(max_workers=1)

if __name__ == '__main__':
    runner.main()
