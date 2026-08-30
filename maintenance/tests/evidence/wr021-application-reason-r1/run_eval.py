#!/usr/bin/env python3
"""Run the WR-021 application-reason A/B with isolated Skill exports."""

from __future__ import annotations

import importlib.util
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
UPSTREAM = REPO / "maintenance/tests/evidence/short-inference-r1/run_cause_hint.py"


def main() -> int:
    spec = importlib.util.spec_from_file_location("wr021_application_reason_runner", UPSTREAM)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load runner: {UPSTREAM}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.REPO = REPO
    module.HERE = HERE
    module.CONFIG_PATH = HERE / "cases.json"
    module.OUTPUT_ROOT = REPO / "output/wr021-application-reason-r1"
    module.UPSTREAM_PATH = REPO / "maintenance/tests/evidence/v1615-like-signal-short-writing-r1/run_eval.py"
    return module.main()


if __name__ == "__main__":
    raise SystemExit(main())
