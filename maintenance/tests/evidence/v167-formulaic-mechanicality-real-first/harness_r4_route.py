#!/usr/bin/env python3
"""Run the three-case R4 explicit phrase route follow-up."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import harness_r4 as r4


base = r4.base
DIRECT_ROUTE = (
    "用户明确要求选择、核对或解释公文开端、引叙、承启、综合、期请或结尾用语时，"
    "在读取 `references/information-selection.md` 后直接读取 `references/formulaic-language.md`；"
    "普通起草、改写、压缩和复核不读取该页。\n\n"
)
INSERT_BEFORE = "## 使用顺序\n"


def load_route_payload() -> dict[str, Any]:
    payload = r4.load_r4_payload()
    cases = [item for item in payload["cases"] if item["id"] in {"Q03", "Q06", "Q09"}]
    if [item["id"] for item in cases] != ["Q03", "Q06", "Q09"]:
        raise RuntimeError("explicit route cases mismatch")
    if any(not item["phrase_lookup"] for item in cases):
        raise RuntimeError("route follow-up contains a non-phrase case")
    return {"schema_version": 1, "models": payload["models"], "cases": cases}


def prepare_skill_roots(runtime: Path) -> dict[str, Any]:
    receipt = r4.prepare_skill_roots(runtime)
    candidate = Path(receipt["candidate_root"])
    skill_path = candidate / "SKILL.md"
    skill = skill_path.read_text(encoding="utf-8").replace("\r\n", "\n")
    if skill.count(INSERT_BEFORE) != 1 or DIRECT_ROUTE in skill:
        raise RuntimeError("direct route insertion contract mismatch")
    skill_path.write_text(skill.replace(INSERT_BEFORE, DIRECT_ROUTE + INSERT_BEFORE, 1), encoding="utf-8", newline="\n")
    baseline = Path(receipt["baseline_root"])
    baseline_manifest = base.tree_manifest(baseline)
    candidate_manifest = base.tree_manifest(candidate)
    baseline_by_path = {item["path"]: item["sha256"] for item in baseline_manifest}
    candidate_by_path = {item["path"]: item["sha256"] for item in candidate_manifest}
    differing = sorted(
        path for path in set(baseline_by_path) | set(candidate_by_path)
        if baseline_by_path.get(path) != candidate_by_path.get(path)
    )
    expected = ["SKILL.md", "references/formulaic-language.md", "references/task-route-cards.md"]
    if differing != expected:
        raise RuntimeError(f"unexpected route prototype diff: {differing}")
    receipt.update({
        "differing_paths": differing,
        "candidate_manifest_sha256": base.sha256_text(json.dumps(candidate_manifest, sort_keys=True)),
        "direct_route_sha256": base.sha256_text(DIRECT_ROUTE),
    })
    base.atomic_json(runtime / "skill-roots.json", receipt)
    return receipt


base.EXPECTED_CASES = 3
base.EXPECTED_PER_PROVIDER = 1
base.EXPECTED_CALLS = 6
base.AUTH_ENV = "V167_FORMULAIC_R4_ROUTE_AUTH"
base.AUTH_VALUE = "APPROVED_BY_USER_20260817"
base.load_payload = load_route_payload
base.prepare_skill_roots = prepare_skill_roots


if __name__ == "__main__":
    raise SystemExit(base.main())
