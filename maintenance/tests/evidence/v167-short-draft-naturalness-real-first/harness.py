#!/usr/bin/env python3
"""Real-first A/B for ordinary short-draft naturalness without Hooks."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
from typing import Any

import sys


FORMULAIC_EVIDENCE = Path(__file__).resolve().parents[1] / "v167-formulaic-mechanicality-real-first"
sys.path.insert(0, str(FORMULAIC_EVIDENCE))
import harness as base  # noqa: E402


EVIDENCE_ROOT = Path(__file__).resolve().parent
CASES = EVIDENCE_ROOT / "cases.json"
PROTOTYPE = EVIDENCE_ROOT / "prototype-short-draft-naturalness.md"
CASES_SHA256 = "3359a56bd54abb7f3faa6359ce6b49a32084123a525333aafd8d297fa48a7f60"
PROTOTYPE_SHA256 = "1c14d93800f6b23d0134d10b9bbee4fe6e4669cd52f7d8edce0365281a66a390"
ROUTE_SENTENCE = (
    "用户明确要求正文不超过300字，或给出主要落在180—300字内的篇幅范围时，"
    "在读取 `references/information-selection.md` 后直接读取 `references/short-draft-naturalness.md`；"
    "篇幅更长、未给短篇幅要求或只审不改时不读取该页。\n\n"
)
INSERT_BEFORE = "## 使用顺序\n"
ORIGINAL_RUN_ARM = base.run_arm


def normalized_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_text(encoding="utf-8").replace("\r\n", "\n").encode("utf-8")).hexdigest()


def load_payload() -> dict[str, Any]:
    for path, expected in ((CASES, CASES_SHA256), (PROTOTYPE, PROTOTYPE_SHA256)):
        if normalized_sha256(path) != expected:
            raise RuntimeError(f"hash mismatch: {path.name}")
    payload = json.loads(CASES.read_text(encoding="utf-8"))
    if len(payload.get("cases", [])) != 6:
        raise RuntimeError("expected six short-draft cases")
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
    if skill.count(INSERT_BEFORE) != 1:
        raise RuntimeError("short-draft route insertion point mismatch")
    skill_path.write_text(skill.replace(INSERT_BEFORE, ROUTE_SENTENCE + INSERT_BEFORE, 1), encoding="utf-8", newline="\n")
    baseline_manifest = base.tree_manifest(baseline)
    candidate_manifest = base.tree_manifest(candidate)
    baseline_by_path = {item["path"]: item["sha256"] for item in baseline_manifest}
    candidate_by_path = {item["path"]: item["sha256"] for item in candidate_manifest}
    differing = sorted(
        path for path in set(baseline_by_path) | set(candidate_by_path)
        if baseline_by_path.get(path) != candidate_by_path.get(path)
    )
    if differing != ["SKILL.md", "references/short-draft-naturalness.md"]:
        raise RuntimeError(f"unexpected short-draft prototype diff: {differing}")
    receipt = {
        "baseline_commit": base.BASELINE_COMMIT, "baseline_product_tree": base.BASELINE_PRODUCT_TREE,
        "baseline_root": str(baseline.resolve()), "candidate_root": str(candidate.resolve()),
        "baseline_file_count": len(baseline_manifest), "candidate_file_count": len(candidate_manifest),
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
    target_reads = [
        value for value in result["stream"]["reads"]
        if Path(value).as_posix().endswith("/references/short-draft-naturalness.md")
    ]
    route_ok = True if treatment == "baseline" else bool(target_reads)
    result["checks"]["short_draft_route"] = route_ok
    result["short_draft_route"] = {"expected": treatment == "candidate", "read": bool(target_reads)}
    result["technical_valid"] = all(result["checks"].values())
    base.atomic_json(output / "raw" / result["arm_id"] / "meta.json", result)
    return result


base.PROTOTYPE_PATH = PROTOTYPE
base.PROTOTYPE_SHA256 = PROTOTYPE_SHA256
base.EXPECTED_CASES = 6
base.EXPECTED_PER_PROVIDER = 2
base.EXPECTED_CALLS = 12
base.AUTH_ENV = "V167_SHORT_NATURALNESS_AUTH"
base.AUTH_VALUE = "APPROVED_BY_USER_20260817"
base.load_payload = load_payload
base.prepare_skill_roots = prepare_skill_roots
base.run_arm = run_arm


if __name__ == "__main__":
    raise SystemExit(base.main())
