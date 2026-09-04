#!/usr/bin/env python3
"""Replay six frozen real drafts through baseline core and real cheap CLI replies."""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
from typing import Any
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[4]
BASE_PATH = ROOT / "maintenance/tests/evidence/v167-formulaic-mechanicality-real-first/harness.py"
CORE_COMMIT = "5fbb2d26c49d0b780ad11fc4cff008854995ad3f"
MAX_CONTINUATIONS = 4
CLI_TIMEOUT = 180
SAMPLES = (
    ("alibaba2", "REMEDIATION-SHORT-SERVICE", "baseline"),
    ("alibaba1", "REMEDIATION-SHORT-SERVICE", "candidate"),
    ("ollama", "REMEDIATION-EDUCATION-LONG", "baseline"),
    ("opencode", "REMEDIATION-EDUCATION-LONG", "baseline"),
    ("minimax", "REMEDIATION-SHORT-SERVICE", "baseline"),
    ("minimax", "REMEDIATION-EDUCATION-LONG", "candidate"),
)
SPEC = importlib.util.spec_from_file_location("hook_quality_cheap_cli", BASE_PATH)
assert SPEC is not None and SPEC.loader is not None
BASE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BASE)


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def save(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def bind_samples(source: Path) -> list[dict[str, Any]]:
    fixture = read_json(source / "fixture.json")
    cases = {case["id"]: case for case in fixture["config"]["cases"]}
    bound = []
    for provider, case_id, arm in SAMPLES:
        records = read_json(source / "providers" / f"{provider}.json")["records"]
        record, = [r for r in records if r["case_id"] == case_id and r["arm"] == arm]
        draft = (source / record["final_file"]).read_text(encoding="utf-8")
        prompt = cases[case_id]["prompt"]
        assert record["exact_skill_trace"] and not record["technical_failures"]
        assert not record["hook_contamination_markers"] and "SKILL.md" in record["skill_files_read"]
        assert digest(draft) == record["final_sha256"]
        assert digest(prompt) == record["prompt_sha256"] == cases[case_id]["prompt_sha256"]
        trace = source / record["trace_file"]
        assert hashlib.sha256(trace.read_bytes()).hexdigest() == record["trace_sha256"]
        bound.append({"id": f"{provider}-{case_id}-{arm}", "provider": provider,
                      "case_id": case_id, "arm": arm, "request": prompt, "d0": draft,
                      "source_record": record, "source_model": record["model"]})
    return bound


def cli_reply(model: str, prompt: str, out: Path, claude: str) -> tuple[str, dict[str, Any]]:
    out.mkdir(parents=True, exist_ok=False)
    (out / "prompt.txt").write_text(prompt, encoding="utf-8")
    environment = BASE.build_environment(model, out / "runtime")
    command = [claude, "--setting-sources", "", "--no-session-persistence", "--tools", "",
               "--print", "--verbose", "--output-format", "stream-json", "--model", model,
               "--effort", "max"]
    started = time.monotonic()
    code, error = -1, None
    with (out / "stream.jsonl").open("w", encoding="utf-8") as stdout, (out / "stderr.txt").open("w", encoding="utf-8") as stderr:
        try:
            completed = subprocess.run(command, cwd=out / "runtime/work", env=environment,
                                       input=prompt, text=True, encoding="utf-8", stdout=stdout,
                                       stderr=stderr, timeout=CLI_TIMEOUT, check=False)
            code = completed.returncode
        except subprocess.TimeoutExpired:
            error = "timeout"
    parsed = BASE.parse_stream(out / "stream.jsonl")
    final = parsed.pop("final")
    results = []
    for line in (out / "stream.jsonl").read_text(encoding="utf-8").splitlines():
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            continue
        if item.get("type") == "result":
            results.append({key: item.get(key) for key in ("usage", "modelUsage", "total_cost_usd", "duration_ms")})
    valid = (code == 0 and bool(final.strip()) and parsed["result_count"] == 1
             and parsed["result_subtypes"] == ["success"] and parsed["result_errors"] == [False]
             and all(parsed[key] == [model] for key in ("init_models", "assistant_models", "usage_models"))
             and not parsed["plugins"] and not parsed["invalid_json_lines"])
    receipt = {"model": model, "return_code": code, "error": error, "technical_valid": valid,
               "seconds": round(time.monotonic() - started, 3), "usage_reports": results, **parsed}
    (out / "reply.txt").write_text(final, encoding="utf-8")
    save(out / "receipt.json", receipt)
    return final, receipt


def run_sample(sample: dict[str, Any], core_root: Path, out: Path, claude: str, advertised: set[str]) -> dict[str, Any]:
    out.mkdir(parents=True, exist_ok=False)
    save(out / "source.json", sample)
    (out / "d0.txt").write_text(sample["d0"], encoding="utf-8")
    core = core_root / "chinese-official-writing/hooks/core/gate_stop_hook.py"
    core_data = out / "core-data"
    environment = dict(os.environ, COW_GATE_HOOK_DATA=str(core_data), COW_GATE_CAPABILITY="delivery_review")
    record_path = core_data / "candidate-ai-gate-hook" / "quality-audit" / f"{sample['id']}.json"
    events, calls, history, finding_count = [], [], [], None
    model = sample["source_model"]
    fallback = "alibaba-token-plan-2/deepseek-v4-flash-0731"
    route_note = "same_source_route"
    if model not in advertised and sample["provider"] in {"alibaba1", "minimax"}:
        model, route_note = fallback, "source_route_not_advertised_using_alibaba2"

    def event(name: str, **extra: Any) -> dict[str, Any]:
        payload = dict(hook_event_name=name, session_id="quality-audit", turn_id=sample["id"], cwd=str(core_root), **extra)
        completed = subprocess.run([sys.executable, "-B", str(core)], input=json.dumps(payload, ensure_ascii=False),
                                   text=True, encoding="utf-8", capture_output=True, env=environment, timeout=35, check=True)
        response = json.loads(completed.stdout)
        record = read_json(record_path) if record_path.exists() else None
        entry = {"input": payload, "response": response, "record_after": record, "stderr": completed.stderr}
        if record and record.get("txn"):
            txn = Path(record["txn"])
            for filename in ("state.json", "detection.json", "report.json"):
                if (txn / filename).is_file():
                    entry[filename] = read_json(txn / filename)
        events.append(entry)
        save(out / "events.json", events)
        return response

    event("UserPromptSubmit", prompt=sample["request"])
    # Replay the successful Skill read proved by the frozen source trace,
    # mapping its exported path to this baseline core's canonical path.
    event("PostToolUse", tool_input={"cmd": f'Get-Content "{core_root / "chinese-official-writing/SKILL.md"}"'}, tool_response={"exit_code": 0})
    current, allowed, status = sample["d0"], False, "pending"
    print(json.dumps({"sample": sample["id"], "status": "started", "model": model}), flush=True)
    for round_number in range(MAX_CONTINUATIONS + 1):
        response = event("Stop", stop_hook_active=round_number > 0, last_assistant_message=current)
        detection = events[-1].get("detection.json")
        if detection is not None and finding_count is None:
            finding_count = len(detection.get("findings", []))
        if response.get("decision") != "block":
            allowed, status = True, "allowed"
            break
        if round_number == MAX_CONTINUATIONS:
            status = "wrapper_continuation_ceiling"
            event("HostAbort", abort_reason="host_ceiling")
            break
        reason = response["reason"]
        prompt = ("你正在接续同一成稿的交付门禁。原任务只作事实背景；本轮只执行末尾门禁反馈，"
                  "不要重新起草、不要调用工具。不得把过程说明加入正文。\n\n原始任务：\n"
                  + sample["request"] + "\n\n冻结初稿 D0：\n" + sample["d0"]
                  + "\n\n既有门禁对话：\n" + json.dumps(history, ensure_ascii=False)
                  + "\n\n本轮实际门禁反馈：\n" + reason)
        current, receipt = cli_reply(model, prompt, out / "calls" / f"round-{round_number + 1}", claude)
        calls.append(receipt)
        if not receipt["technical_valid"] and sample["provider"] in {"alibaba1", "minimax"} and model != fallback:
            model, route_note = fallback, "source_cli_binding_failed_using_alibaba2"
            current, receipt = cli_reply(model, prompt, out / "calls" / f"round-{round_number + 1}-fallback", claude)
            calls.append(receipt)
        if not receipt["technical_valid"]:
            status = "model_technical_failure"
            event("HostAbort", abort_reason="continuation_failed")
            break
        history.append({"hook_reason": reason, "model_reply": current})
    (out / "last-assistant.txt").write_text(current, encoding="utf-8")
    if allowed:
        (out / "final-visible.txt").write_text(current, encoding="utf-8")
    record = read_json(record_path) if record_path.exists() else {}
    receipt = {"sample_id": sample["id"], "status": status, "source_model": sample["source_model"],
               "continuation_model": model, "route_note": route_note, "call_count": len(calls),
               "finding_count": finding_count, "no_finding": finding_count == 0,
               "d0_sha256": digest(sample["d0"]), "last_assistant_sha256": digest(current),
               "final_visible_sha256": digest(current) if allowed else None,
               "unchanged_from_d0": current == sample["d0"] if allowed else None,
               "delivery_verified": record.get("delivery_verified"), "core_receipt": record,
               "calls": calls, "semantic_quality_verdict": "pending_human_review"}
    save(out / "receipt.json", receipt)
    print(json.dumps({key: receipt[key] for key in ("sample_id", "status", "call_count", "finding_count", "unchanged_from_d0", "delivery_verified")}), flush=True)
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--core-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--run", action="store_true", help="Make the authorized real model calls; otherwise validate frozen inputs only.")
    args = parser.parse_args()
    core_commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=args.core_root, text=True).strip()
    assert core_commit == CORE_COMMIT
    samples = bind_samples(args.source_root)
    if not args.run:
        print(json.dumps({"samples": [s["id"] for s in samples], "core_commit": core_commit}, ensure_ascii=False, indent=2))
        return 0
    assert not args.output.exists(), "Use a new output directory; never overwrite existing evidence."
    claude = shutil.which("claude")
    assert claude, "The existing Claude CLI is required; no installation is performed."
    with urlopen(BASE.GATEWAY + "/v1/models", timeout=10) as response:
        advertised = {item["id"] for item in json.load(response)["data"]}
    save(args.output / "fixture.json", {"core_commit": core_commit, "mode": "core_event_replay_with_fresh_real_cli_continuations",
         "source_fixture_sha256": hashlib.sha256((args.source_root / "fixture.json").read_bytes()).hexdigest(),
         "wrapper_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
         "base_harness_sha256": hashlib.sha256(BASE_PATH.read_bytes()).hexdigest(),
         "cli_version": subprocess.check_output([claude, "--version"], text=True).strip(),
         "max_continuations": MAX_CONTINUATIONS, "samples": samples,
         "advertised_routes": {s["source_model"]: s["source_model"] in advertised for s in samples}})
    lanes: dict[str, list[dict[str, Any]]] = {}
    for sample in samples:
        lanes.setdefault(sample["provider"], []).append(sample)
    def lane(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return [run_sample(item, args.core_root, args.output / "samples" / item["id"], claude, advertised) for item in items]
    with ThreadPoolExecutor(max_workers=3) as executor:
        results = [item for group in executor.map(lane, lanes.values()) for item in group]
    save(args.output / "summary.json", {"records": results, "semantic_quality_verdict": "pending_human_review"})
    return 0 if all(item["status"] == "allowed" and item["delivery_verified"] for item in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
