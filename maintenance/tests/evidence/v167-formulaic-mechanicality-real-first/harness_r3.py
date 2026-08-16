#!/usr/bin/env python3
"""Run the frozen R3 default-structure plus conditional-phrases comparison."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
from typing import Any

import harness as base


EVIDENCE_ROOT = Path(__file__).resolve().parent
R3_CASES = EVIDENCE_ROOT / "cases-r3.json"
R1_CASES = EVIDENCE_ROOT / "cases.json"
DEFAULT_PROTOTYPE = EVIDENCE_ROOT / "prototype-structure-default-r3.md"
PHRASE_PROTOTYPE = EVIDENCE_ROOT / "prototype-phrases-on-demand-r3.md"
R3_CASES_SHA256 = "af459dd49b38daa86bd0f41d792f202723c2b877bdc62dcc91ca7ef7a9f5adc9"
R1_CASES_SHA256 = "0bab8696cd2bc82cb6a8e40244cb41fcef717385bf684f7b5df541e3b5780ba9"
DEFAULT_PROTOTYPE_SHA256 = "589e8a076cb3dc50d1d781e5b3c22012baf9d9249577c3d79e0dcd0603d7e1ce"
PHRASE_PROTOTYPE_SHA256 = "cdd759ef383aa1dfef878d96966b45d0494d3243c9ac046d4b2b28e85229830f"
ORIGINAL_RUN_ARM = base.run_arm


def normalized_sha256(path: Path) -> str:
    text = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_r3_payload() -> dict[str, Any]:
    frozen = (
        (R3_CASES, R3_CASES_SHA256),
        (R1_CASES, R1_CASES_SHA256),
        (DEFAULT_PROTOTYPE, DEFAULT_PROTOTYPE_SHA256),
        (PHRASE_PROTOTYPE, PHRASE_PROTOTYPE_SHA256),
    )
    for path, expected in frozen:
        if normalized_sha256(path) != expected:
            raise RuntimeError(f"hash mismatch: {path.name}")
    plan = json.loads(R3_CASES.read_text(encoding="utf-8"))
    source = json.loads(R1_CASES.read_text(encoding="utf-8"))
    source_by_id = {item["id"]: item for item in source["cases"]}
    cases = []
    for planned in plan["cases"]:
        if "source_case_id" in planned:
            original = source_by_id[planned["source_case_id"]]
            genre = original["genre"]
            request = original["request"]
        else:
            genre = planned["genre"]
            request = planned["request"]
        cases.append({
            "id": planned["id"],
            "provider": planned["provider"],
            "genre": genre,
            "request": request,
            "phrase_lookup": bool(planned["phrase_lookup"]),
        })
    return {"schema_version": 1, "models": plan["models"], "cases": cases}


def prepare_skill_roots(runtime: Path) -> dict[str, Any]:
    roots = runtime / "skills"
    baseline = roots / "baseline/chinese-official-writing"
    candidate = roots / "candidate/chinese-official-writing"
    if roots.exists():
        shutil.rmtree(roots)
    base.export_baseline(baseline)
    shutil.copytree(baseline, candidate)
    (candidate / "references/formulaic-language.md").write_text(
        DEFAULT_PROTOTYPE.read_text(encoding="utf-8").replace("\r\n", "\n"),
        encoding="utf-8", newline="\n",
    )
    (candidate / "references/formulaic-phrases.md").write_text(
        PHRASE_PROTOTYPE.read_text(encoding="utf-8").replace("\r\n", "\n"),
        encoding="utf-8", newline="\n",
    )
    baseline_manifest = base.tree_manifest(baseline)
    candidate_manifest = base.tree_manifest(candidate)
    baseline_by_path = {item["path"]: item["sha256"] for item in baseline_manifest}
    candidate_by_path = {item["path"]: item["sha256"] for item in candidate_manifest}
    differing = sorted(
        path for path in set(baseline_by_path) | set(candidate_by_path)
        if baseline_by_path.get(path) != candidate_by_path.get(path)
    )
    expected = ["references/formulaic-language.md", "references/formulaic-phrases.md"]
    if differing != expected:
        raise RuntimeError(f"unexpected prototype diff: {differing}")
    receipt = {
        "baseline_commit": base.BASELINE_COMMIT,
        "baseline_product_tree": base.BASELINE_PRODUCT_TREE,
        "baseline_root": str(baseline.resolve()),
        "candidate_root": str(candidate.resolve()),
        "baseline_file_count": len(baseline_manifest),
        "candidate_file_count": len(candidate_manifest),
        "differing_paths": differing,
        "baseline_manifest_sha256": base.sha256_text(json.dumps(baseline_manifest, sort_keys=True)),
        "candidate_manifest_sha256": base.sha256_text(json.dumps(candidate_manifest, sort_keys=True)),
    }
    base.atomic_json(runtime / "skill-roots.json", receipt)
    return receipt


def run_arm(
    claude: str, output: Path, runtime: Path, skill_roots: dict[str, Path], models: dict[str, str],
    case: dict[str, Any], treatment: str,
) -> dict[str, Any]:
    result = ORIGINAL_RUN_ARM(claude, output, runtime, skill_roots, models, case, treatment)
    phrase_reads = [
        value for value in result["stream"]["reads"]
        if Path(value).as_posix().endswith("/references/formulaic-phrases.md")
    ]
    route_ok = True
    if treatment == "candidate":
        route_ok = bool(phrase_reads) is bool(case["phrase_lookup"])
    result["checks"]["phrase_lookup_route"] = route_ok
    result["phrase_lookup"] = {
        "expected": bool(case["phrase_lookup"]) if treatment == "candidate" else None,
        "read": bool(phrase_reads),
    }
    result["technical_valid"] = all(result["checks"].values())
    base.atomic_json(output / "raw" / result["arm_id"] / "meta.json", result)
    return result


base.PROTOTYPE_PATH = DEFAULT_PROTOTYPE
base.PROTOTYPE_SHA256 = DEFAULT_PROTOTYPE_SHA256
base.EXPECTED_CASES = 15
base.EXPECTED_PER_PROVIDER = 5
base.EXPECTED_CALLS = 30
base.AUTH_ENV = "V167_FORMULAIC_R3_AUTH"
base.AUTH_VALUE = "APPROVED_BY_USER_20260817"
base.load_payload = load_r3_payload
base.prepare_skill_roots = prepare_skill_roots
base.run_arm = run_arm


if __name__ == "__main__":
    raise SystemExit(base.main())
