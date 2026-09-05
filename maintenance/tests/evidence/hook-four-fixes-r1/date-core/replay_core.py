#!/usr/bin/env python3
"""Six frozen real-D0 pairs through actual core subprocesses; no model calls."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys


BASELINE = "3532afd6619ac6256558e9552b92d03da5ae9c0f"
INPUT_SHA256 = "0d7e15949cd2ef9abe07629ff285ac039ef164efdb8f4f2694ca8cc80583acaa"
SOURCE_PREFIX = "chinese-official-writing"
EXPECTED_CANDIDATE_HASHES = {
    "chinese-official-writing/hooks/core/gate_stop_hook.py": "969235f48c8a7f8592b84742257b08315e823326c76d4198e7e12b7cc5eb32ea",
    "chinese-official-writing/hooks/shared/source_bound_dates.py": "5f28a20b0b32cda9f4610fbbabfbb7592819272662abba852d8c3f96b85aae3a",
}
SELECTED_CASES = (
    "AH2-REPAIR-TRAINING", "AH2-REPAIR-OPEN-DAY", "AH2-REPAIR-DRILL",
    "AH2-CONTROL-COMPLETE", "REAL-D0-ISO-FORMAT-EXAMPLE", "REAL-D0-ISO-OLD-DRAFT",
)


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def write_json(path: Path, value) -> None:
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def freeze_sources(repo: Path, output: Path) -> dict:
    baseline = output / "snapshots/baseline"
    candidate = output / "snapshots/candidate"
    baseline.mkdir(parents=True)
    candidate.mkdir(parents=True)
    entries = []
    tree = subprocess.check_output(["git", "ls-tree", "-rz", BASELINE, "--", SOURCE_PREFIX], cwd=repo)
    for entry in filter(None, tree.split(b"\0")):
        metadata, name = entry.split(b"\t", 1)
        mode, kind, object_id = metadata.split()
        if kind != b"blob" or mode not in {b"100644", b"100755"}:
            raise ValueError("Unsupported baseline tree entry")
        entries.append((name.decode("utf-8"), object_id))
    payload = subprocess.run(["git", "cat-file", "--batch"], cwd=repo, check=True,
                             input=b"\n".join(oid for _, oid in entries) + b"\n", capture_output=True).stdout
    position = 0
    for name, object_id in entries:
        header_end = payload.index(b"\n", position)
        returned_id, kind, size = payload[position:header_end].split()
        if returned_id != object_id or kind != b"blob":
            raise ValueError("Unexpected cat-file response")
        position = header_end + 1
        raw = payload[position:position + int(size)]
        position += int(size) + 1
        target = (baseline / name).resolve()
        if not target.is_relative_to(baseline.resolve()):
            raise ValueError("Baseline path escaped snapshot")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
    paths = subprocess.check_output(["git", "ls-files", "-z", "--", SOURCE_PREFIX], cwd=repo).decode().split("\0")
    for name in filter(None, paths):
        target = candidate / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((repo / name).read_bytes())
    if any((repo / name).read_bytes() != (candidate / name).read_bytes() for name in filter(None, paths)):
        raise ValueError("Candidate changed while freezing; no core event executed")
    for name, expected in EXPECTED_CANDIDATE_HASHES.items():
        if sha((candidate / name).read_bytes()) != expected:
            raise ValueError(f"Final candidate hash mismatch: {name}")
    manifests = {}
    for arm, root in (("baseline", baseline), ("candidate", candidate)):
        manifests[arm] = {str(p.relative_to(root)).replace("\\", "/"): sha(p.read_bytes())
                          for p in sorted(root.rglob("*")) if p.is_file()}
    return {
        "baseline_commit": BASELINE,
        "baseline_export": "git cat-file --batch raw binary stdout; no newline conversion",
        "expected_candidate_sha256": EXPECTED_CANDIDATE_HASHES,
        "candidate_head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo).decode().strip(),
        "candidate_changed_product_paths": subprocess.check_output(
            ["git", "diff", "--name-only", BASELINE, "--", SOURCE_PREFIX], cwd=repo).decode().splitlines(),
        "snapshot_sha256": manifests,
    }


def read_json(path: Path) -> dict:
    return json.loads(path.read_bytes()) if path.is_file() else {}


def run_case(root: Path, case: dict, output: Path) -> dict:
    output.mkdir(parents=True)
    core = root / SOURCE_PREFIX / "hooks/core/gate_stop_hook.py"
    skill = root / SOURCE_PREFIX / "SKILL.md"
    data = output / "data"
    record_path = data / "candidate-ai-gate-hook/date-core" / f"{case['id']}.json"
    env = {k: v for k, v in os.environ.items()
           if not k.startswith("COW_GATE_") and k not in {"PLUGIN_ROOT", "PLUGIN_DATA", "PYTHONPATH", "PYTHONHOME"}}
    env.update(COW_GATE_HOOK_DATA=str(data), COW_GATE_CAPABILITY="delivery_review",
               PYTHONDONTWRITEBYTECODE="1", PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
    records = []

    def call(name: str, **fields) -> tuple[dict, dict]:
        event = {"hook_event_name": name, "session_id": "date-core", "turn_id": case["id"],
                 "cwd": str(root), **fields}
        step = output / f"{len(records) + 1:02d}-{name}"
        step.mkdir()
        write_json(step / "event.json", event)
        completed = subprocess.run([sys.executable, "-I", "-B", "-X", "utf8", str(core)],
                                   input=json.dumps(event, ensure_ascii=False).encode("utf-8"),
                                   capture_output=True, cwd=root, env=env, timeout=40)
        (step / "stdout.json").write_bytes(completed.stdout)
        (step / "stderr.txt").write_bytes(completed.stderr)
        if completed.returncode != 0:
            raise RuntimeError(f"Core subprocess exit {completed.returncode}: {case['id']} {name}")
        response = json.loads(completed.stdout)
        record = read_json(record_path)
        state = {}
        if record.get("txn"):
            txn = Path(record["txn"]).resolve()
            if not txn.is_relative_to(data.resolve()):
                raise ValueError("Transaction escaped isolated data directory")
            state = read_json(txn / "state.json")
        if data.is_dir():
            shutil.copytree(data, step / "data-after-event")
        summary = {"event": name, "response": response, "record": record,
                   "transaction_state": state, "subprocess_exit_code": completed.returncode}
        write_json(step / "observation.json", summary)
        records.append(summary)
        return response, record

    call("UserPromptSubmit", prompt=case["request"])
    # This is an actual bounded file-read subprocess, then a core PostToolUse event.
    read_command = [sys.executable, "-I", "-B", "-X", "utf8", "-c",
                    "from pathlib import Path; import sys; sys.stdout.buffer.write(Path(sys.argv[1]).read_bytes())", str(skill)]
    read = subprocess.run(read_command, capture_output=True, cwd=root, env=env, timeout=10)
    (output / "skill-read.stdout.txt").write_bytes(read.stdout)
    (output / "skill-read.stderr.txt").write_bytes(read.stderr)
    if read.returncode != 0 or read.stdout != skill.read_bytes():
        raise RuntimeError("Frozen Skill read failed")
    call("PostToolUse", tool_input={"cmd": subprocess.list2cmdline(read_command)},
         tool_response={"exit_code": read.returncode, "output": read.stdout.decode("utf-8")})
    first_response, first_record = call("Stop", last_assistant_message=case["d0"], stop_hook_active=False)
    first_state = records[-1]["transaction_state"]
    visible = None
    status = "PENDING_MODEL_OR_CORE_CONTINUATION"
    if first_record.get("hook_phase") == "awaiting_final_output" and isinstance(first_record.get("emitted_output"), str):
        selected = first_record["emitted_output"]
        if sha(selected.encode("utf-8")) != first_record.get("emitted_sha256"):
            raise ValueError("Core emitted text/hash mismatch")
        if not str(first_response.get("reason", "")).endswith(selected):
            raise ValueError("Core continuation did not carry exact emitted text")
        final_response, final_record = call("Stop", last_assistant_message=selected, stop_hook_active=True)
        verified = (final_response.get("continue") is True and final_record.get("delivery_verified") is True
                    and final_record.get("hook_phase") == "complete")
        status = "EXACT_ECHO_TERMINAL" if verified else "EXACT_ECHO_NOT_VERIFIED"
        if verified:
            visible = selected
            (output / "visible-final.txt").write_bytes(visible.encode("utf-8"))
    elif first_response.get("continue") is True and not first_response.get("decision"):
        status = "ALLOWED_WITHOUT_EMIT"
        visible = case["d0"]
        (output / "visible-final.txt").write_bytes(visible.encode("utf-8"))
    final_record = records[-1]["record"]
    result = {
        "case_id": case["id"], "kind": case["kind"], "status": status,
        "model_calls": 0, "request_sha256": case["request_sha256"], "d0_sha256": case["d0_sha256"],
        "date_audit_after_first_stop": first_record.get("source_bound_date"),
        "state_after_first_stop": first_state.get("state"), "selected_after_first_stop": first_state.get("selected"),
        "visible_final_sha256": sha(visible.encode("utf-8")) if visible is not None else None,
        "visible_final_equals_d0": visible == case["d0"] if visible is not None else None,
        "visible_final": visible, "final_record": final_record, "events": records,
    }
    write_json(output / "result.json", result)
    return result


def main() -> int:
    here = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--inputs", type=Path, default=here / "inputs.json")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raw = args.inputs.read_bytes()
    if sha(raw) != INPUT_SHA256:
        raise ValueError("Frozen input packet hash mismatch")
    cases = [case for case in json.loads(raw)["cases"] if case["id"] in SELECTED_CASES]
    if tuple(case["id"] for case in cases) != SELECTED_CASES:
        raise ValueError("Unexpected fixed case set or ordering")
    args.output = args.output.resolve()
    args.output.mkdir(parents=True, exist_ok=False)
    (args.output / "inputs.json").write_bytes(raw)
    origin = freeze_sources(args.repo_root.resolve(), args.output)
    prereg = {"created_utc": datetime.now(timezone.utc).isoformat(), "model_calls": 0,
              "selected_case_ids": SELECTED_CASES, "inputs_sha256": INPUT_SHA256, **origin,
              "stop_rule": "Run U, actual Skill read/PostToolUse, Stop. Only directly emitted text may be echoed byte-for-byte. Any model repair/verdict request remains pending. No fabricated model JSON."}
    write_json(args.output / "preregistration.json", prereg)
    summary = []
    for case in cases:
        arms = {}
        for arm in ("baseline", "candidate"):
            value = run_case(args.output / "snapshots" / arm, case, args.output / "cases" / case["id"] / arm)
            value["matches_pure_helper_expected_output"] = value["visible_final"] == case["expected"][f"{arm}_output"]
            arms[arm] = value
        summary.append({"case_id": case["id"], "kind": case["kind"], "arms": arms})
    result = {"model_calls": 0, "core_subprocess_events": sum(len(arm["events"]) for case in summary for arm in case["arms"].values()),
              "all_exact_echo_terminal": all(arm["status"] == "EXACT_ECHO_TERMINAL" for case in summary for arm in case["arms"].values()),
              "all_visible_outputs_match_helper_expectations": all(arm["matches_pure_helper_expected_output"] for case in summary for arm in case["arms"].values()),
              "replay_script_sha256": sha(Path(__file__).read_bytes()), "cases": summary}
    write_json(args.output / "results.json", result)
    print(json.dumps({k:v for k,v in result.items() if k != "cases"}, ensure_ascii=False))
    print(json.dumps({"results_sha256": sha((args.output / "results.json").read_bytes())}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
