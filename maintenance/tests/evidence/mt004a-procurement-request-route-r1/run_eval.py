from __future__ import annotations

import importlib.util
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
UPSTREAM = REPO / "maintenance/tests/evidence/reference-slimming-r1/run_eval.py"


def main() -> int:
    spec = importlib.util.spec_from_file_location("mt004a_reference_runner", UPSTREAM)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load runner: {UPSTREAM}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.REPO = REPO
    module.CASES_PATH = HERE / "cases.json"
    module.OUTPUT_BASE = REPO / "output/mt004a-procurement-request-route-r1"
    return module.main()


if __name__ == "__main__":
    raise SystemExit(main())
