#!/usr/bin/env python3
"""Run short-draft naturalness R3 with upper bounds only."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
from typing import Any


R1_HARNESS = Path(__file__).resolve().parent / "harness.py"
R1_SPEC = importlib.util.spec_from_file_location("v167_short_naturalness_r1_for_r3", R1_HARNESS)
if R1_SPEC is None or R1_SPEC.loader is None:
    raise RuntimeError("cannot load short-draft R1 harness")
r1 = importlib.util.module_from_spec(R1_SPEC)
R1_SPEC.loader.exec_module(r1)
base = r1.base

EVIDENCE_ROOT = Path(__file__).resolve().parent
CASES = EVIDENCE_ROOT / "cases-r3.json"
PROTOTYPE = EVIDENCE_ROOT / "prototype-short-draft-naturalness-r3.md"
CASES_SHA256 = "52c65d2d1f3261cc024689d2edce500665db79f329918d2fef7e224a5b2f28a7"
PROTOTYPE_SHA256 = "25e6361675e40b7b299e37f8980295d840774be6f5df884ba4e910ab90c140ce"


def normalized_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_text(encoding="utf-8").replace("\r\n", "\n").encode("utf-8")).hexdigest()


def load_payload() -> dict[str, Any]:
    for path, expected in ((CASES, CASES_SHA256), (PROTOTYPE, PROTOTYPE_SHA256)):
        if normalized_sha256(path) != expected:
            raise RuntimeError(f"hash mismatch: {path.name}")
    payload = json.loads(CASES.read_text(encoding="utf-8"))
    if len(payload.get("cases", [])) != 4:
        raise RuntimeError("expected four max-only cases")
    return payload


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
        raise RuntimeError("R3 route insertion point mismatch")
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
        raise RuntimeError(f"unexpected R3 prototype diff: {differing}")
    receipt = {
        "baseline_commit": base.BASELINE_COMMIT, "baseline_product_tree": base.BASELINE_PRODUCT_TREE,
        "baseline_root": str(baseline.resolve()), "candidate_root": str(candidate.resolve()),
        "differing_paths": differing,
        "baseline_manifest_sha256": base.sha256_text(json.dumps(baseline_manifest, sort_keys=True)),
        "candidate_manifest_sha256": base.sha256_text(json.dumps(candidate_manifest, sort_keys=True)),
    }
    base.atomic_json(runtime / "skill-roots.json", receipt)
    return receipt


base.PROTOTYPE_PATH = PROTOTYPE
base.PROTOTYPE_SHA256 = PROTOTYPE_SHA256
base.EXPECTED_CASES = 4
base.EXPECTED_PER_PROVIDER = 2
base.EXPECTED_CALLS = 8
base.AUTH_ENV = "V167_SHORT_NATURALNESS_R3_AUTH"
base.AUTH_VALUE = "APPROVED_BY_USER_20260817"
base.load_payload = load_payload
base.prepare_skill_roots = prepare_skill_roots


if __name__ == "__main__":
    raise SystemExit(base.main())
