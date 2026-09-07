"""One real candidate echo and one independent full cleanliness chain; no retries."""
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(value):
    return hashlib.sha256(value).hexdigest()


def text_sha(value):
    return sha(value.encode("utf-8"))


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def run(paired):
    prereg = read(HERE / "r2-preregister.json")
    fixture = read(HERE / "fixture.json")
    assert sha((HERE / "runtime-candidate-r2.py").read_bytes()) == prereg["candidate_sha256"]
    assert sha((HERE / "runtime-baseline.py").read_bytes()) == prereg["baseline_sha256"]
    for path, expected in fixture["source_sha256"].items():
        if path.endswith("/runtime.py"):
            continue
        assert sha((ROOT / path).read_bytes()) == expected, path
    case = next(c for c in fixture["cases"] if c["id"] == "M6")
    for field in ("request", "d0", "expected", "body"):
        assert text_sha(case[field]) == case[field + "_sha256"]
    assert case["request_sha256"] == prereg["request_sha256"]
    assert case["d0_sha256"] == prereg["source_d0_sha256"]
    out = HERE / ("r2-paired-echo" if paired else "r2-full/M6")
    out.mkdir(parents=True, exist_ok=False)
    save(out / "input.json", case)
    runtime = load("clean_candidate", HERE / "runtime-candidate-r2.py")
    real = load("clean_real", ROOT / "maintenance/tests/evidence/date-source-real-r1/run.py")
    claude = shutil.which("claude")
    assert claude
    record = {"request": case["request"]}
    response = runtime.start({"last_assistant_message": case["d0"]}, record)
    events = [{"origin": "runtime_start", "response": response, "state": copy.deepcopy(record)}]
    calls = []
    current = case["d0"]
    if paired:
        for index, phase in ((1, "revision"), (2, "verdict")):
            source = HERE / "r1/M6/calls" / str(index)
            prompt = (source / "prompt.txt").read_text(encoding="utf-8")
            current = (source / "reply.txt").read_text(encoding="utf-8")
            receipt = read(source / "receipt.json")
            assert prompt == response["reason"]
            assert text_sha(current) == prereg["reused_real_replies"][phase + "_sha256"]
            assert receipt["technical_valid"] is True
            response = runtime.advance({"last_assistant_message": current}, record)
            events.append({"origin": "reused_actual_real_reply_unchanged_prompt", "source": str(source.relative_to(HERE)),
                           "prompt_sha256": text_sha(prompt), "reply_sha256": text_sha(current),
                           "response": response, "state": copy.deepcopy(record)})
        assert text_sha(response["reason"]) == prereg["offline_same_real_inputs"]["candidate"]["next_reason_sha256"]
    status = "pending"
    for index in range(1, 2 if paired else fixture["max_continuations_per_case"] + 1):
        if not response or response.get("decision") != "block":
            break
        phase = record["delivery_cleanliness"]["phase"]
        save(out / f"invocation-{index}.json", {"argv": real.command(claude, prereg["model"]),
             "phase": phase, "prompt_sha256": text_sha(response["reason"]), "model": prereg["model"],
             "effort": "max", "model_retries": 0, "runtime_sha256": prereg["candidate_sha256"],
             "isolation": "fresh no-tool CLI; empty Skills/plugins/MCP; existing cheap route; environment values omitted"})
        try:
            current, receipt = real.restricted_reply(prereg["model"], response["reason"], out / "calls" / str(index), claude)
        except Exception as exc:
            status = "technical_failure_no_retry"
            save(out / "failure.json", {"exception_type": type(exc).__name__, "index": index, "phase": phase})
            break
        stream = [json.loads(s) for s in (out / "calls" / str(index) / "stream.jsonl").read_text(encoding="utf-8").splitlines()]
        calls.append({"index": index, "phase": phase, "reply_sha256": text_sha(current), "receipt": receipt,
                      "session_ids": sorted({e["session_id"] for e in stream if isinstance(e.get("session_id"), str)})})
        response = runtime.advance({"last_assistant_message": current}, record)
        events.append({"origin": "new_actual_real_reply", "index": index, "reply_sha256": text_sha(current),
                       "response": response, "state": copy.deepcopy(record)})
        save(out / "events.json", events)
        save(out / "calls.json", calls)
        print(json.dumps({"paired": paired, "call": index, "phase": phase, "next_phase": record["delivery_cleanliness"]["phase"]}), flush=True)
    if status == "pending":
        status = "finished" if response and response.get("decision") != "block" else "wrapper_ceiling_no_retry"
    state = record["delivery_cleanliness"]
    audit = state.get("audit", {})
    visible = current if status == "finished" else None
    result = {"id": "M6", "status": status, "candidate_sha256": prereg["candidate_sha256"],
              "request_sha256": case["request_sha256"], "d0_sha256": case["d0_sha256"],
              "expected_sha256": case["expected_sha256"], "selected_sha256": record.get("delivery_cleanliness_selected_sha256"),
              "final_visible_sha256": text_sha(visible) if visible is not None else None,
              "body_exactly_retained": visible is not None and case["body"] in visible,
              "expected_exact": visible == case["expected"], "original_unchanged": visible == case["d0"],
              "audit": audit, "phase": state["phase"], "last_response": response, "new_call_count": len(calls),
              "reused_real_call_count": 2 if paired else 0, "calls": calls,
              "counts_nonspace": {k: len("".join(v.split())) for k, v in [("d0", case["d0"]), ("expected", case["expected"]), ("visible", visible or "")]},
              "actual_native_hook_run": False,
              "functional_pass": status == "finished" and visible == case["expected"] and audit.get("delivery_verified") is True}
    save(out / "result.json", result)
    save(out / "events.json", events)
    save(out / "calls.json", calls)
    (out / "last-assistant.txt").write_text(current, encoding="utf-8", newline="\n")
    if visible is not None:
        (out / "final-visible.txt").write_text(visible, encoding="utf-8", newline="\n")
    print(json.dumps({k: result[k] for k in ("status", "functional_pass", "new_call_count", "final_visible_sha256")}), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--paired", action="store_true")
    group.add_argument("--full", action="store_true")
    args = parser.parse_args()
    run(args.paired)
