"""Replay archived actual replies only after verifying their exact runtime prompts.

No model calls, core/native event emulation, installation, or writes occur.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def text_sha(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def load_runtime(candidate):
    path = HERE / ("runtime-candidate-r2.py" if candidate else "runtime-baseline.py")
    spec = importlib.util.spec_from_file_location("saved_cleanliness_runtime", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def replay(label, case, runtime, call_paths, expected_path, migrated=False):
    record = {"request": case["request"]}
    response = runtime.start({"last_assistant_message": case["d0"]}, record)
    delivered = case["d0"]
    for relative in call_paths:
        call = HERE / relative
        assert response.get("decision") == "block", (label, relative)
        assert response["reason"] == (call / "prompt.txt").read_text(encoding="utf-8"), (label, relative, "prompt mismatch")
        assert read(call / "receipt.json")["technical_valid"] is True
        delivered = (call / "reply.txt").read_text(encoding="utf-8")
        response = runtime.advance({"last_assistant_message": delivered}, record)
    expected = read(HERE / expected_path)
    assert response == expected["last_response"], label
    assert record["delivery_cleanliness"]["audit"] == expected["audit"], label
    assert text_sha(delivered) == expected["final_visible_sha256"], label
    return {"label": label, "all_real_input_prompts_match": True,
            "replayed_actual_replies": len(call_paths), "new_model_calls": 0,
            "migrated_protocol_unchanged_evidence": migrated,
            "selection": record["delivery_cleanliness"]["audit"]["selection"],
            "delivery_verified": record["delivery_cleanliness"]["audit"]["delivery_verified"],
            "final_sha256": text_sha(delivered), "expected_body_or_preservation_exact": delivered == case["expected"]}


def main():
    argparse.ArgumentParser(description=__doc__).parse_args()
    provenance = read(HERE / "archive-provenance.json")
    for path, record in provenance["copies"].items():
        assert sha(HERE / path) == record["sha256"], path
    for path, record in provenance["stream_extracts"].items():
        assert sha(HERE / path) == record["extract_sha256"], path
    fixture = read(HERE / "fixture.json")
    cases = {c["id"]: c for c in fixture["cases"]}
    for case in cases.values():
        for field in ("request", "d0", "body", "expected"):
            assert text_sha(case[field]) == case[field + "_sha256"]
    result = []
    for name in ("P6", "M6", "C4", "C5", "C6"):
        count = read(HERE / f"r1/{name}/result.json")["call_count"]
        paths = [f"r1/{name}/calls/{i}" for i in range(1, count + 1)]
        result.append(replay("baseline-" + name, cases[name], load_runtime(False), paths, f"r1/{name}/result.json"))
        if name != "M6":
            result.append(replay("candidate-migrated-" + name, cases[name], load_runtime(True), paths,
                                 f"r1/{name}/result.json", migrated=True))
    result.append(replay("candidate-M6-paired-echo", cases["M6"], load_runtime(True),
                         ["r1/M6/calls/1", "r1/M6/calls/2", "r2-paired-echo/calls/1"],
                         "r2-paired-echo/result.json", migrated=True))
    result.append(replay("candidate-M6-independent-full", cases["M6"], load_runtime(True),
                         [f"r2-full/M6/calls/{i}" for i in range(1, 4)], "r2-full/M6/result.json"))
    print(json.dumps({"all_replays_match_recorded_runtime_behavior": True, "new_model_calls": 0,
                      "baseline_M6_functional_failure_preserved": True, "replays": result}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
