from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
BASE_PATH = HERE / "run_eval.py"


spec = importlib.util.spec_from_file_location("cold_review_r3_base", BASE_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError(f"cannot load module: {BASE_PATH}")
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)
base.HERE = HERE
base.CASES_PATH = HERE / "r3-cases.json"
base.OUTPUT_ROOT = base.REPO / "output/post-v1623-cold-review-fixes-r3"
base.WRITER.OUTPUT_ROOT = base.OUTPUT_ROOT


if __name__ == "__main__":
    sys.exit(base.main())

