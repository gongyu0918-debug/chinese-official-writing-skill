#!/usr/bin/env python3
"""Run the frozen 12-pair structure-only R2 comparison."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import harness as base


EVIDENCE_ROOT = Path(__file__).resolve().parent
R2_CASES = EVIDENCE_ROOT / "cases-r2.json"
R1_CASES = EVIDENCE_ROOT / "cases.json"
R2_CASES_SHA256 = "31db9af5dbac656c57b7ed7f0e6c1b211ca223221bbee92cb2c5074d83eac3f9"
R1_CASES_SHA256 = "0bab8696cd2bc82cb6a8e40244cb41fcef717385bf684f7b5df541e3b5780ba9"


def normalized_sha256(path: Path) -> str:
    text = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_r2_payload() -> dict[str, object]:
    if normalized_sha256(R2_CASES) != R2_CASES_SHA256:
        raise RuntimeError("R2 cases hash mismatch")
    if normalized_sha256(R1_CASES) != R1_CASES_SHA256:
        raise RuntimeError("R1 cases hash mismatch")
    plan = json.loads(R2_CASES.read_text(encoding="utf-8"))
    source = json.loads(R1_CASES.read_text(encoding="utf-8"))
    source_by_id = {item["id"]: item for item in source["cases"]}
    cases = []
    for planned in plan["cases"]:
        original = source_by_id[planned["source_case_id"]]
        cases.append({
            "id": planned["id"],
            "source_case_id": planned["source_case_id"],
            "provider": planned["provider"],
            "genre": original["genre"],
            "request": original["request"],
        })
    return {"schema_version": 1, "models": plan["models"], "cases": cases}


base.PROTOTYPE_PATH = EVIDENCE_ROOT / "prototype-structure-only-r2.md"
base.PROTOTYPE_SHA256 = "d5479112bf5c6031de355cfad6e38d87d1007432c2bb5859b781eabce4ee60c5"
base.EXPECTED_CASES = 12
base.EXPECTED_PER_PROVIDER = 4
base.EXPECTED_CALLS = 24
base.load_payload = load_r2_payload


if __name__ == "__main__":
    raise SystemExit(base.main())
