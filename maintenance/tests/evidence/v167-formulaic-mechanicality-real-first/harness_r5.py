#!/usr/bin/env python3
"""Run R5: ordinary tasks skip the unchanged formulaic language page."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import harness_r4 as r4


base = r4.base
ORDINARY_CASE_IDS = ("Q01", "Q02", "Q04", "Q05", "Q07", "Q08")


def load_r5_payload() -> dict[str, Any]:
    payload = r4.load_r4_payload()
    by_id = {item["id"]: item for item in payload["cases"]}
    cases = [by_id[case_id] for case_id in ORDINARY_CASE_IDS]
    if any(item["phrase_lookup"] for item in cases):
        raise RuntimeError("R5 contains an explicit phrase query")
    return {"schema_version": 1, "models": payload["models"], "cases": cases}


def prepare_skill_roots(runtime: Path) -> dict[str, Any]:
    receipt = r4.prepare_skill_roots(runtime)
    baseline = Path(receipt["baseline_root"])
    candidate = Path(receipt["candidate_root"])
    phrase_path = Path("references/formulaic-language.md")
    (candidate / phrase_path).write_bytes((baseline / phrase_path).read_bytes())
    baseline_manifest = base.tree_manifest(baseline)
    candidate_manifest = base.tree_manifest(candidate)
    baseline_by_path = {item["path"]: item["sha256"] for item in baseline_manifest}
    candidate_by_path = {item["path"]: item["sha256"] for item in candidate_manifest}
    differing = sorted(
        path
        for path in set(baseline_by_path) | set(candidate_by_path)
        if baseline_by_path.get(path) != candidate_by_path.get(path)
    )
    expected = ["SKILL.md", "references/task-route-cards.md"]
    if differing != expected:
        raise RuntimeError(f"unexpected R5 prototype diff: {differing}")
    receipt.update(
        {
            "differing_paths": differing,
            "candidate_manifest_sha256": base.sha256_text(
                json.dumps(candidate_manifest, sort_keys=True)
            ),
            "formulaic_page_unchanged": True,
        }
    )
    base.atomic_json(runtime / "skill-roots.json", receipt)
    return receipt


base.EXPECTED_CASES = 6
base.EXPECTED_PER_PROVIDER = 2
base.EXPECTED_CALLS = 12
base.AUTH_ENV = "V167_FORMULAIC_R5_AUTH"
base.AUTH_VALUE = "APPROVED_BY_USER_20260817"
base.load_payload = load_r5_payload
base.prepare_skill_roots = prepare_skill_roots


if __name__ == "__main__":
    raise SystemExit(base.main())
