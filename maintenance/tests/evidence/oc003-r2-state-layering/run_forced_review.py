from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
BASE_RUNNER = HERE / "run_eval.py"


spec = importlib.util.spec_from_file_location("oc003_r2_forced_base", BASE_RUNNER)
if spec is None or spec.loader is None:
    raise RuntimeError(f"cannot load base runner: {BASE_RUNNER}")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
module.CASES_PATH = HERE / "forced-review-cases.json"
module.OUTPUT_ROOT = module.REPO / "output" / "oc003-r2-state-layering-forced-review"


if __name__ == "__main__":
    sys.exit(module.main())
