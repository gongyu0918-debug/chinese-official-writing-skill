from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
FORCED_RUNNER = HERE / "run_forced_review.py"


spec = importlib.util.spec_from_file_location("oc003_r2c_forced", FORCED_RUNNER)
if spec is None or spec.loader is None:
    raise RuntimeError(f"cannot load forced-review runner: {FORCED_RUNNER}")
wrapper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wrapper)
wrapper.module.OUTPUT_ROOT = wrapper.module.REPO / "output" / "oc003-r2c-condition-state"


if __name__ == "__main__":
    sys.exit(wrapper.module.main())
