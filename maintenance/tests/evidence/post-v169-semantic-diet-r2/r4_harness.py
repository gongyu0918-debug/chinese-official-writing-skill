#!/usr/bin/env python3
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import importlib.util
import os
from pathlib import Path
import shutil
import subprocess
from typing import Any


ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
R2_HARNESS = HERE / "harness.py"
OUTPUT = ROOT / "output/post-v169-semantic-diet-r2/formal-r4"
AUTH_ENV = "POST_V169_SEMANTIC_R4_AUTH"
AUTH_VALUE = "APPROVED_BY_USER_20260818"
EXPECTED_DIFF = [
    "chinese-official-writing/references/anti-ai-patterns.md",
    "chinese-official-writing/references/genre-playbook-request.md",
]


def load_r2() -> Any:
    spec = importlib.util.spec_from_file_location("semantic_r2_runner", R2_HARNESS)
    if spec is None or spec.loader is None:
        raise RuntimeError("R2 runner unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.OUTPUT = OUTPUT
    return module


R2 = load_r2()


def preflight() -> dict[str, Any]:
    if R2.git(R2.BASELINE_ROOT, "rev-parse", "HEAD") != R2.BASELINE_COMMIT:
        raise RuntimeError("baseline HEAD drifted")
    if R2.git(R2.BASELINE_ROOT, "status", "--porcelain", "--", "chinese-official-writing"):
        raise RuntimeError("baseline product dirty")
    if R2.git(ROOT, "status", "--porcelain", "--", "chinese-official-writing"):
        raise RuntimeError("candidate product dirty")
    changed = R2.git(ROOT, "diff", "--name-only", R2.BASELINE_COMMIT, "--", "chinese-official-writing").splitlines()
    if changed != EXPECTED_DIFF:
        raise RuntimeError(f"unexpected product diff: {changed}")
    return {"baseline_commit": R2.BASELINE_COMMIT, "candidate_commit": R2.git(ROOT, "rev-parse", "HEAD"), "changed_paths": changed}


def run_lane(claude: str, provider: str, model: str, cases: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [R2.run_arm(claude, provider, model, case, "candidate") for case in cases]


def execute() -> None:
    if os.environ.get(AUTH_ENV) != AUTH_VALUE:
        raise RuntimeError(f"missing {AUTH_ENV}")
    if OUTPUT.exists():
        raise RuntimeError(f"output exists: {OUTPUT}")
    claude = shutil.which("claude")
    if not claude:
        raise RuntimeError("claude executable unavailable")
    payload = R2.load_cases()
    cases = payload["cases"][:2]
    OUTPUT.mkdir(parents=True)
    R2.write_json(OUTPUT / "preflight.json", preflight())
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(run_lane, claude, provider, model, cases) for provider, model in payload["models"].items()]
        results = [item for future in futures for item in future.result()]
    results.sort(key=lambda item: item["arm_id"])
    R2.write_json(
        OUTPUT / "manifest.json",
        {"calls_planned": 4, "calls_completed": len(results), "technical_valid": sum(bool(item["technical_valid"]) for item in results), "arms": results},
    )


if __name__ == "__main__":
    execute()
