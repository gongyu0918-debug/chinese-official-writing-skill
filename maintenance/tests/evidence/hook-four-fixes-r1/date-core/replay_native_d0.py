#!/usr/bin/env python3
"""Replay one already-observed native D0 without changing its request or text."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path


TRACE_SHA256 = "cc27c8b019786fb4d87016aeef04e9fab386c4732e30507cdc74044b6640e55f"
REQUEST_SHA256 = "a634e6cb058ca4449f2e05772b0ee3229d89439683cc49682e054b3ada712b68"
D0_SHA256 = "d0928563b721c2adf6d2e0246591553e8a06df03c48cccb4ecbd486933059e6a"
REPLAY_SHA256 = "e0ffc9d36bd416d87e81ad29df541035eadea5ed49a7e7f8ee8f142049c44962"
CANDIDATE_COMMIT = "976bb8a4e11a56e314c7328ff163267e805ad9f9"


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--native-events", type=Path, required=True,
                        help="Original local native JSONL; redacted display text is never replayed.")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    helper_path = Path(__file__).with_name("replay_core.py")
    if sha(helper_path.read_bytes()) != REPLAY_SHA256:
        raise ValueError("Frozen core replay helper hash mismatch")
    spec = importlib.util.spec_from_file_location("frozen_date_core_replay", helper_path)
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    raw = args.native_events.read_bytes()
    if sha(raw) != TRACE_SHA256:
        raise ValueError("Original native event trace hash mismatch")
    rows = [(number, json.loads(line)) for number, line in enumerate(raw.splitlines(), 1) if line.strip()]
    user_line, user = next((n, row) for n, row in rows if row["native_event"].get("hook_event_name") == "UserPromptSubmit")
    stop_line, stop = next((n, row) for n, row in rows if row["native_event"].get("hook_event_name") == "Stop")
    request = user["native_event"]["prompt"]
    d0 = stop["native_event"]["last_assistant_message"]
    if sha(request.encode("utf-8")) != REQUEST_SHA256 or sha(d0.encode("utf-8")) != D0_SHA256:
        raise ValueError("Original prompt/D0 extraction hash mismatch")
    if stop.get("fault_injected") is not False:
        raise ValueError("The selected first native Stop was fault-injected")
    if d0.count("9月5日") != 1 or "2026年" in d0 or "2020年" in d0:
        raise ValueError("Unexpected original D0 date form")
    case = {"id": "NATIVE-FROZEN-NORMAL-REAL-D0", "kind": "original_natural_d0_pair",
            "request": request, "d0": d0, "request_sha256": REQUEST_SHA256, "d0_sha256": D0_SHA256}
    expected = {"baseline": d0.replace("9月5日", "2020年9月5日", 1), "candidate": d0}
    args.output = args.output.resolve()
    args.output.mkdir(parents=True, exist_ok=False)
    helper.write_json(args.output / "input-original.json", case)
    origin = helper.freeze_sources(args.repo_root.resolve(), args.output)
    helper.write_json(args.output / "preregistration.json", {
        "created_utc": datetime.now(timezone.utc).isoformat(), "model_calls": 0,
        "source_trace_sha256": TRACE_SHA256, "request_line": user_line, "first_stop_line": stop_line,
        "candidate_product_commit": CANDIDATE_COMMIT, "first_native_stop_fault_injected": False,
        "stop_rule": "Same original request and first native D0. Echo only directly emitted text; leave any model JSON request pending.",
        "expected_visible_sha256": {arm:sha(text.encode("utf-8")) for arm,text in expected.items()}, **origin,
    })
    arms = {}
    for arm in ("baseline", "candidate"):
        result = helper.run_case(args.output / "snapshots" / arm, case, args.output / "cases" / arm)
        result["matches_frozen_expected_output"] = result["visible_final"] == expected[arm]
        arms[arm] = result
    document = {
        "model_calls": 0, "new_generation_calls": 0, "case_id": case["id"],
        "request_sha256": REQUEST_SHA256, "d0_sha256": D0_SHA256,
        "core_subprocess_events": sum(len(arm["events"]) for arm in arms.values()),
        "all_exact_echo_terminal": all(arm["status"] == "EXACT_ECHO_TERMINAL" for arm in arms.values()),
        "all_frozen_expectations_met": all(arm["matches_frozen_expected_output"] for arm in arms.values()),
        "candidate_date_completeness": "FAIL: original bare month/day is preserved",
        "script_sha256": sha(Path(__file__).read_bytes()), "arms": arms,
    }
    helper.write_json(args.output / "results.json", document)
    print(json.dumps({k:v for k,v in document.items() if k != "arms"}, ensure_ascii=False))
    print(json.dumps({"results_sha256": sha((args.output / "results.json").read_bytes())}))
    return 0 if document["all_frozen_expectations_met"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
