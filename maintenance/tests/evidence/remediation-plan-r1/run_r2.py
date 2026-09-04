from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
RUNNER_PATH = HERE / "run_candidate.py"


def main() -> int:
    spec = importlib.util.spec_from_file_location("wr028_r2_runner", RUNNER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load runner: {RUNNER_PATH}")
    runner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runner)
    runner.CONFIG_PATH = HERE / "candidate-r2-config.json"
    runner.OUTPUT_ROOT = runner.REPO / "output/remediation-plan-r1/candidate-r2"
    runner.WRITER_OUTPUT_ROOT = runner.OUTPUT_ROOT
    return runner.main()


if __name__ == "__main__":
    sys.exit(main())
