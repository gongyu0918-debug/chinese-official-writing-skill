"""Native confirmation of script fixes with the released anti-AI leaf retained."""
from pathlib import Path
import importlib.util
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
spec = importlib.util.spec_from_file_location("script_merge_eval", ROOT / "maintenance/tests/evidence/mit-script-delivery-r1/run_eval.py")
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)
runner.CASES = json.loads((HERE / "cases.json").read_text(encoding="utf-8"))

if __name__ == "__main__":
    runner.main()
