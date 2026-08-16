#!/usr/bin/env python3
"""Run four candidate-only short-draft R2 writings before any A/B glue."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import threading
from typing import Any

R1_HARNESS = Path(__file__).resolve().parent / "harness.py"
R1_SPEC = importlib.util.spec_from_file_location("v167_short_naturalness_r1", R1_HARNESS)
if R1_SPEC is None or R1_SPEC.loader is None:
    raise RuntimeError("cannot load short-draft R1 harness")
r1 = importlib.util.module_from_spec(R1_SPEC)
R1_SPEC.loader.exec_module(r1)


base = r1.base
EVIDENCE_ROOT = Path(__file__).resolve().parent
PROTOTYPE = EVIDENCE_ROOT / "prototype-short-draft-naturalness-r2.md"
PROTOTYPE_SHA256 = "e4c9d71d4a633c886b83f1648890047c9a626853ba542e9c78e983abbbaabed5"
AUTH_ENV = "V167_SHORT_NATURALNESS_R2_AUTH"
AUTH_VALUE = "APPROVED_BY_USER_20260817"
EXPECTED_CALLS = 4


def normalized_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_text(encoding="utf-8").replace("\r\n", "\n").encode("utf-8")).hexdigest()


def cases_and_models() -> tuple[list[dict[str, Any]], dict[str, str]]:
    if normalized_sha256(PROTOTYPE) != PROTOTYPE_SHA256:
        raise RuntimeError("R2 prototype hash mismatch")
    payload = r1.load_payload()
    cases = [item for item in payload["cases"] if item["id"] in {"N03", "N04", "N05", "N06"}]
    if [item["id"] for item in cases] != ["N03", "N04", "N05", "N06"]:
        raise RuntimeError("R2 candidate case mismatch")
    return cases, payload["models"]


def prepare_skill_roots(runtime: Path) -> dict[str, Any]:
    roots = runtime / "skills"
    baseline = roots / "baseline/chinese-official-writing"
    candidate = roots / "candidate/chinese-official-writing"
    if roots.exists():
        shutil.rmtree(roots)
    base.export_baseline(baseline)
    shutil.copytree(baseline, candidate)
    (candidate / "references/short-draft-naturalness.md").write_text(
        PROTOTYPE.read_text(encoding="utf-8").replace("\r\n", "\n"), encoding="utf-8", newline="\n"
    )
    skill_path = candidate / "SKILL.md"
    skill = skill_path.read_text(encoding="utf-8").replace("\r\n", "\n")
    if skill.count(r1.INSERT_BEFORE) != 1:
        raise RuntimeError("R2 route insertion point mismatch")
    skill_path.write_text(skill.replace(r1.INSERT_BEFORE, r1.ROUTE_SENTENCE + r1.INSERT_BEFORE, 1), encoding="utf-8", newline="\n")
    baseline_manifest = base.tree_manifest(baseline)
    candidate_manifest = base.tree_manifest(candidate)
    baseline_by_path = {item["path"]: item["sha256"] for item in baseline_manifest}
    candidate_by_path = {item["path"]: item["sha256"] for item in candidate_manifest}
    differing = sorted(
        path for path in set(baseline_by_path) | set(candidate_by_path)
        if baseline_by_path.get(path) != candidate_by_path.get(path)
    )
    if differing != ["SKILL.md", "references/short-draft-naturalness.md"]:
        raise RuntimeError(f"unexpected R2 prototype diff: {differing}")
    receipt = {
        "baseline_commit": base.BASELINE_COMMIT, "baseline_product_tree": base.BASELINE_PRODUCT_TREE,
        "baseline_root": str(baseline.resolve()), "candidate_root": str(candidate.resolve()),
        "differing_paths": differing,
        "baseline_manifest_sha256": base.sha256_text(json.dumps(baseline_manifest, sort_keys=True)),
        "candidate_manifest_sha256": base.sha256_text(json.dumps(candidate_manifest, sort_keys=True)),
    }
    base.atomic_json(runtime / "skill-roots.json", receipt)
    return receipt


def preflight(claude: str, cases: list[dict[str, Any]]) -> dict[str, Any]:
    with socket.create_connection((base.GATEWAY_HOST, base.GATEWAY_PORT), timeout=5):
        pass
    version = subprocess.run([claude, "--version"], capture_output=True, text=True, encoding="utf-8", timeout=20, check=True).stdout.strip()
    return {"checked_utc": base.utc_now(), "gateway": base.GATEWAY, "claude": claude, "claude_version": version, "cases": len(cases), "calls": EXPECTED_CALLS}


def execute(output: Path) -> None:
    if os.environ.get(AUTH_ENV) != AUTH_VALUE:
        raise RuntimeError(f"missing exact authorization marker {AUTH_ENV}")
    if output.exists():
        raise RuntimeError(f"output must not exist: {output}")
    claude = shutil.which("claude")
    if not claude:
        raise RuntimeError("claude executable not found")
    cases, models = cases_and_models()
    output.mkdir(parents=True)
    runtime = base.ROOT / "output/v167-formulaic-mechanicality-real-first/runtime" / output.name
    if runtime.exists():
        raise RuntimeError(f"runtime must not exist: {runtime}")
    runtime.mkdir(parents=True)
    base.atomic_json(output / "preflight.json", preflight(claude, cases))
    roots_receipt = prepare_skill_roots(runtime)
    skill_roots = {"baseline": Path(roots_receipt["baseline_root"]), "candidate": Path(roots_receipt["candidate_root"])}
    by_provider = {provider: [item for item in cases if item["provider"] == provider] for provider in ("ollama", "alibaba2")}
    progress: list[dict[str, Any]] = []
    lock = threading.Lock()

    def lane(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        values = []
        for case in items:
            result = r1.run_arm(claude, output, runtime, skill_roots, models, case, "candidate")
            values.append(result)
            with lock:
                progress.append({"arm_id": result["arm_id"], "technical_valid": result["technical_valid"]})
                base.atomic_json(output / "progress.json", {"completed": len(progress), "total": EXPECTED_CALLS, "arms": progress})
        return values

    results: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(lane, items) for items in by_provider.values()]
        for future in as_completed(futures):
            results.extend(future.result())
    results.sort(key=lambda item: item["arm_id"])
    base.atomic_json(output / "manifest.json", {
        "schema_version": 1, "finished_utc": base.utc_now(), "baseline_commit": base.BASELINE_COMMIT,
        "calls_planned": EXPECTED_CALLS, "calls_completed": len(results),
        "technical_valid": sum(item["technical_valid"] for item in results), "arms": results,
    })


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--show-plan", action="store_true")
    parser.add_argument("--prepare-only", action="store_true")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    cases, models = cases_and_models()
    if args.show_plan:
        print(json.dumps({"cases": len(cases), "calls": EXPECTED_CALLS, "models": {key: models[key] for key in ("ollama", "alibaba2")}}, ensure_ascii=False, indent=2))
        return 0
    if args.prepare_only:
        target = base.ROOT / "output/v167-short-draft-naturalness-real-first/prepare-r2"
        if target.exists():
            shutil.rmtree(target)
        target.mkdir(parents=True)
        print(json.dumps(prepare_skill_roots(target), ensure_ascii=False, indent=2))
        shutil.rmtree(target)
        return 0
    if args.execute:
        if args.out is None:
            parser.error("--execute requires --out")
        execute(args.out.resolve())
        return 0
    parser.error("choose --show-plan, --prepare-only, or --execute")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
