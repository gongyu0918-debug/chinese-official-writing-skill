#!/usr/bin/env python3
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import importlib.util
import os
from pathlib import Path
import shutil
from typing import Any


ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
R1_HARNESS = HERE / "harness.py"
OUTPUT = ROOT / "output/post-v169-ah001-r2/formal-r2-dedup"
AUTH_ENV = "POST_V169_AH001_DEDUP_AUTH"
AUTH_VALUE = "APPROVED_BY_USER_20260818"


def load_r1() -> Any:
    spec = importlib.util.spec_from_file_location("ah001_r1_runner", R1_HARNESS)
    if spec is None or spec.loader is None:
        raise RuntimeError("R1 runner unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.OUTPUT = OUTPUT
    return module


R1 = load_r1()
BASE_SYSTEM_PROMPT = R1.system_prompt


def system_prompt(skill_root: Path) -> str:
    return (
        BASE_SYSTEM_PROMPT(skill_root)
        + "同一锚点重复时，只删除纯重复出现；承载范围、归属或状态的唯一事实必须保留。"
        "如果重复值位于该事实中，改写该句以避免重复，不得整句删除。"
    )


R1.system_prompt = system_prompt


def execute() -> None:
    if os.environ.get(AUTH_ENV) != AUTH_VALUE:
        raise RuntimeError(f"missing {AUTH_ENV}")
    if OUTPUT.exists():
        raise RuntimeError(f"output exists: {OUTPUT}")
    claude = shutil.which("claude")
    if not claude:
        raise RuntimeError("claude executable unavailable")
    payload = R1.load_cases()
    case = next(item for item in payload["cases"] if item["id"] == "A03")
    OUTPUT.mkdir(parents=True)
    R1.write_json(OUTPUT / "preflight.json", R1.preflight())
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [
            pool.submit(R1.run_arm, claude, provider, model, case)
            for provider, model in payload["models"].items()
        ]
        results = [future.result() for future in futures]
    results.sort(key=lambda item: item["arm_id"])
    R1.write_json(
        OUTPUT / "manifest.json",
        {
            "calls_planned": 2,
            "calls_completed": len(results),
            "technical_valid": sum(bool(item["technical_valid"]) for item in results),
            "mechanical_ok": sum(bool(item["mechanical_ok"]) for item in results),
            "arms": results,
        },
    )


if __name__ == "__main__":
    execute()
