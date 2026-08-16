#!/usr/bin/env python3
"""Run the four-pair R6 A/B after candidate-only writing passed."""

from __future__ import annotations

import importlib
from pathlib import Path
import threading
from typing import Any

import harness_r6 as r6


base = importlib.reload(r6.base)


def run_arm(
    claude: str,
    output: Path,
    runtime: Path,
    skill_roots: dict[str, Path],
    models: dict[str, str],
    case: dict[str, Any],
    treatment: str,
) -> dict[str, Any]:
    result = base.run_arm(
        claude, output, runtime, skill_roots, models, case, treatment
    )
    formulaic_read = any(
        Path(value).as_posix().endswith("/references/formulaic-language.md")
        for value in result["stream"]["reads"]
    )
    result["checks"]["formulaic_read"] = formulaic_read
    result["technical_valid"] = all(result["checks"].values())
    base.atomic_json(output / "raw" / result["arm_id"] / "meta.json", result)
    return result


def run_lane(
    claude: str,
    output: Path,
    runtime: Path,
    skill_roots: dict[str, Path],
    models: dict[str, str],
    cases: list[dict[str, Any]],
    progress: list[dict[str, Any]],
    lock: threading.Lock,
) -> list[dict[str, Any]]:
    results = []
    for case in cases:
        order = (
            ["baseline", "candidate"]
            if int(case["id"][1:]) % 2
            else ["candidate", "baseline"]
        )
        for treatment in order:
            result = run_arm(
                claude, output, runtime, skill_roots, models, case, treatment
            )
            results.append(result)
            with lock:
                progress.append(
                    {
                        "arm_id": result["arm_id"],
                        "technical_valid": result["technical_valid"],
                        "finished_utc": result["finished_utc"],
                    }
                )
                base.atomic_json(
                    output / "progress.json",
                    {"completed": len(progress), "total": 8, "arms": progress},
                )
    return results


base.EXPECTED_CASES = 4
base.EXPECTED_PER_PROVIDER = 2
base.EXPECTED_CALLS = 8
base.MAX_PROVIDER_LANES = 2
base.AUTH_ENV = "V167_FORMULAIC_R6_AB_AUTH"
base.AUTH_VALUE = "APPROVED_BY_USER_20260817"
base.load_payload = r6.load_r6_payload
base.prepare_skill_roots = r6.prepare_skill_roots
base.run_lane = run_lane


if __name__ == "__main__":
    raise SystemExit(base.main())
