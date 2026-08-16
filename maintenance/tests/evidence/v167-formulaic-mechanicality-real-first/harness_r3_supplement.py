#!/usr/bin/env python3
"""Run only the six R3 pairs invalidated by provider/environment failures."""

from __future__ import annotations

from typing import Any

import harness_r3 as r3


base = r3.base
SUPPLEMENT_IDS = {"R01", "R02", "R03", "R04", "R05", "R10"}


def load_supplement_payload() -> dict[str, Any]:
    payload = r3.load_r3_payload()
    cases = []
    for case in payload["cases"]:
        if case["id"] not in SUPPLEMENT_IDS:
            continue
        selected = dict(case)
        selected["provider"] = "luna"
        cases.append(selected)
    if {case["id"] for case in cases} != SUPPLEMENT_IDS:
        raise RuntimeError("supplement case set mismatch")
    return {
        "schema_version": 1,
        "models": {"luna": "gpt-5.6-luna"},
        "cases": cases,
    }


base.EXPECTED_CASES = 6
base.EXPECTED_PER_PROVIDER = 6
base.EXPECTED_CALLS = 12
base.MAX_PROVIDER_LANES = 1
base.AUTH_ENV = "V167_FORMULAIC_R3_SUPPLEMENT_AUTH"
base.AUTH_VALUE = "APPROVED_BY_USER_20260817"
base.load_payload = load_supplement_payload


if __name__ == "__main__":
    raise SystemExit(base.main())
