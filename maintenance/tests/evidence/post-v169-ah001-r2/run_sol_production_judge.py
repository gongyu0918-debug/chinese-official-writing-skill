#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
BASE_JUDGE = HERE / "run_sol_judge.py"


def load_base() -> Any:
    spec = importlib.util.spec_from_file_location("ah001_sol_production", BASE_JUDGE)
    if spec is None or spec.loader is None:
        raise RuntimeError("base judge unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BASE = load_base()
BASE.PACKET = HERE / "relation-production-packet.md"
BASE.OUTPUT = BASE.ROOT / "output/post-v169-ah001-r2/sol-r3-production"
BASE.EXPECTED_GROUPS = ["H09", "H10"]


if __name__ == "__main__":
    BASE.execute()
