#!/usr/bin/env python3
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import hashlib
import importlib.util
import os
from pathlib import Path
import shutil
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
R1_HARNESS = HERE / "harness.py"
CONTRACT_PATH = ROOT / "chinese-official-writing/hooks/shared/hard_anchors.py"
OUTPUT = ROOT / "output/post-v169-ah001-r2/formal-r3-production"
AUTH_ENV = "POST_V169_AH001_PRODUCTION_AUTH"
AUTH_VALUE = "APPROVED_BY_USER_20260818"
EXPECTED_PRODUCT_DIFF = [
    "chinese-official-writing/hooks/capabilities/over_length/runtime.py",
    "chinese-official-writing/hooks/capabilities/under_length/runtime.py",
    "chinese-official-writing/hooks/shared/hard_anchors.py",
]


def load_r1() -> Any:
    spec = importlib.util.spec_from_file_location("ah001_production_runner", R1_HARNESS)
    if spec is None or spec.loader is None:
        raise RuntimeError("R1 runner unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.OUTPUT = OUTPUT
    module.CONTRACT_PATH = CONTRACT_PATH
    contract_spec = importlib.util.spec_from_file_location(
        "ah001_production_contract", CONTRACT_PATH
    )
    if contract_spec is None or contract_spec.loader is None:
        raise RuntimeError("production contract unavailable")
    contract = importlib.util.module_from_spec(contract_spec)
    sys.modules[contract_spec.name] = contract
    contract_spec.loader.exec_module(contract)
    module.CONTRACT = contract
    return module


R1 = load_r1()
BASE_SYSTEM_PROMPT = R1.system_prompt


def preflight() -> dict[str, Any]:
    if R1.git("status", "--porcelain", "--", "chinese-official-writing"):
        raise RuntimeError("candidate product dirty")
    changed = R1.git(
        "diff", "--name-only", R1.BASELINE_COMMIT, "--", "chinese-official-writing"
    ).splitlines()
    if changed != EXPECTED_PRODUCT_DIFF:
        raise RuntimeError(f"unexpected product diff: {changed}")
    control = R1.CONTRACT.compare("已核验12件。", "已核验12件，另有3件。")
    if control.get("status") != "fallback":
        raise RuntimeError("production contract control failed")
    return {
        "baseline_commit": R1.BASELINE_COMMIT,
        "candidate_commit": R1.git("rev-parse", "HEAD"),
        "changed_paths": changed,
        "contract_sha256": hashlib.sha256(CONTRACT_PATH.read_bytes()).hexdigest(),
    }


def system_prompt(skill_root: Path) -> str:
    return (
        BASE_SYSTEM_PROMPT(skill_root)
        + "同一锚点重复时，只删除纯重复出现；承载范围、归属或状态的唯一事实必须保留。"
        "如果重复值位于该事实中，改写该句以避免重复，不得整句删除。"
    )


R1.preflight = preflight
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
    R1.write_json(OUTPUT / "preflight.json", preflight())
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
