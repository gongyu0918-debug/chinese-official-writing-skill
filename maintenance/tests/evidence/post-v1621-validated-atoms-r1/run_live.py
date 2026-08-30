#!/usr/bin/env python3
"""Run combined post-v1.6.21 holdouts through real Codex Stop lifecycles."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import re
import sys


HERE = Path(__file__).resolve().parent
BASE_PATH = HERE.parent / "ul006-implicit-underlength-r2" / "run_live.py"
SPEC = importlib.util.spec_from_file_location("post_v1621_validated_atoms_base", BASE_PATH)
assert SPEC is not None and SPEC.loader is not None
BASE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = BASE
SPEC.loader.exec_module(BASE)
BASE_RUN_ONE = BASE.run_one

BASE.CONFIG_PATH = HERE / "cases.json"
BASE.OUTPUT_ROOT = BASE.ROOT / "output" / "post-v1621-validated-atoms-r1-live"
BASE.MARKETPLACE_NAME = "post-v1621-validated-atoms-r1-local"


def _notice_boundary(final: str) -> dict[str, object]:
    lines = [line.strip() for line in final.splitlines() if line.strip()]
    tail = lines[-3:]
    inferred_issuer_lines = [
        line for line in tail
        if re.fullmatch(r"行政服务中心(?:（[^）]+）)?", line)
    ]
    inferred_date_lines = [
        line for line in tail
        if re.fullmatch(r"2026年\d{1,2}月\d{1,2}日", line)
    ]
    return {
        "tail_lines": tail,
        "inferred_issuer_lines": inferred_issuer_lines,
        "inferred_date_lines": inferred_date_lines,
        "boundary_failure": bool(inferred_issuer_lines or inferred_date_lines),
    }


def run_one(provider_id: str, model: str, case: dict, effort: str) -> dict:
    record = BASE_RUN_ONE(provider_id, model, case, effort)
    if case["kind"] != "control_no_start":
        return record
    records_path = BASE.OUTPUT_ROOT / record["files"]["hook_records"]
    hook_records = json.loads(records_path.read_text(encoding="utf-8"))
    hook_record = hook_records[-1]["record"] if hook_records else {}
    clean_no_start = bool(
        hook_record.get("hook_phase") == "complete"
        and hook_record.get("delivery_verified") is True
        and hook_record.get("emitted_sha256") == record.get("final_sha256")
        and not isinstance(hook_record.get("under_length"), dict)
    )
    if clean_no_start:
        record["technical_failures"] = [
            item for item in record["technical_failures"]
            if item != "lifecycle_contract_not_met"
        ]
        record["disposition"] = "disabled_genre_no_start"
    final_path = BASE.OUTPUT_ROOT / record["files"]["final"]
    final = final_path.read_text(encoding="utf-8", errors="replace")
    record["notice_boundary"] = _notice_boundary(final)
    BASE.write_json(
        BASE.OUTPUT_ROOT / "raw" / provider_id / case["id"] / "result.json",
        record,
    )
    return record


BASE.run_one = run_one


if __name__ == "__main__":
    sys.exit(BASE.main())
