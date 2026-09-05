#!/usr/bin/env python3
"""Replay frozen inputs against two isolated date-helper copies; no model calls."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path


INPUTS_SHA256 = "6ade05483c423b58141458791185e18845d332abf5e402a97045d5767be8a7c1"


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def load_module(path: Path, expected_sha256: str):
    if digest(path.read_bytes()) != expected_sha256:
        raise ValueError(f"Frozen module hash mismatch: {path.name}")
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    here = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=here / "results.json",
                        help="New JSON result path; existing output is never overwritten.")
    args = parser.parse_args()
    if args.output.exists():
        parser.error("output already exists; select a new path")
    inputs_raw = (here / "inputs.json").read_bytes()
    if digest(inputs_raw) != INPUTS_SHA256:
        raise ValueError("Frozen input packet hash mismatch")
    packet = json.loads(inputs_raw)
    origin = json.loads((here / "prototype-origin.json").read_bytes())
    modules = {
        arm: load_module(here / f"source_bound_dates_{arm}.py", origin[f"{arm}_sha256"])
        for arm in ("baseline", "candidate")
    }
    results = []
    for case in packet["cases"]:
        for name in ("request", "d0"):
            if digest(case[name].encode("utf-8")) != case[f"{name}_sha256"]:
                raise ValueError(f"Input hash mismatch: {case['id']} {name}")
        arms = {}
        for arm, module in modules.items():
            result = module.restore_unique_full_date(case["request"], case["d0"])
            output = result["output"]
            arms[arm] = {
                "result": result,
                "matches_frozen_expectation": output == case["expected"][f"{arm}_output"],
                "d0_byte_identical": output.encode("utf-8") == case["d0"].encode("utf-8"),
            }
        results.append({"id": case["id"], "kind": case["kind"],
                        "request_sha256": case["request_sha256"], "d0_sha256": case["d0_sha256"],
                        "arms": arms})
    passed = all(arm["matches_frozen_expectation"] for case in results for arm in case["arms"].values())
    document = {
        "schema_version": 1,
        "run_utc": datetime.now(timezone.utc).isoformat(),
        "scope": packet["scope"],
        "model_calls": 0,
        "core_lifecycle_executed": False,
        "baseline_commit": origin["baseline_commit"],
        "inputs_sha256": INPUTS_SHA256,
        "baseline_sha256": origin["baseline_sha256"],
        "candidate_sha256": origin["candidate_sha256"],
        "replay_script_sha256": digest(Path(__file__).read_bytes()),
        "case_count": len(results),
        "all_frozen_expectations_met": passed,
        "cases": results,
    }
    with args.output.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(document, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    print(json.dumps({"case_count": len(results), "all_frozen_expectations_met": passed,
                      "results_sha256": digest(args.output.read_bytes())}))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
