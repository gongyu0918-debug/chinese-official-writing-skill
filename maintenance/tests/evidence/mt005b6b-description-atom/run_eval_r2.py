from __future__ import annotations

import importlib.util
from pathlib import Path
import subprocess
import sys


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
BASE_RUNNER = REPO / "maintenance/tests/evidence/mt005c-codex-cli-20260822/run_eval.py"

spec = importlib.util.spec_from_file_location("mt005_base_runner_r2", BASE_RUNNER)
if spec is None or spec.loader is None:
    raise RuntimeError(f"cannot load base runner: {BASE_RUNNER}")
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)

runner.CASES_PATH = HERE / "cases-r2.json"
runner.OUTPUT_ROOT = REPO / "output/mt005b6b-codex-cli-20260824-r2"

real_run = subprocess.run


def run_with_opencodex(command, *args, **kwargs):
    command = list(command)
    if len(command) > 1 and command[1] == "exec":
        command[2:2] = [
            "-c",
            'openai_base_url="http://127.0.0.1:10100/v1"',
            "-c",
            f'model_catalog_json="{(Path.home() / ".codex/opencodex-catalog.json").as_posix()}"',
        ]
    return real_run(command, *args, **kwargs)


runner.subprocess.run = run_with_opencodex

if __name__ == "__main__":
    sys.exit(runner.main())
