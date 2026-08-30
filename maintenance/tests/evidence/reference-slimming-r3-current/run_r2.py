from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
RUNNER_PATH = HERE / "run_candidate.py"


def load_runner():
    spec = importlib.util.spec_from_file_location("reference_slimming_r3_r2", RUNNER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load runner: {RUNNER_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.REPO = REPO
    module.CASES_PATH = HERE / "cases.json"
    module.CONFIG_PATH = HERE / "r2-config.json"
    module.OUTPUT_ROOT = REPO / "output/reference-slimming-r3-current/review-direct-leaf-r2"
    module.BASELINE_OUTPUT = REPO / "output/reference-slimming-r3-current/review-direct-leaf-r1"
    return module


if __name__ == "__main__":
    sys.exit(load_runner().main())
