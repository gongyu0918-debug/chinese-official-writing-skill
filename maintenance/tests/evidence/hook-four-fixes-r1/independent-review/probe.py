"""Narrow offline checks for record-lock failure and stale terminal writers."""
from __future__ import annotations

import argparse
import contextlib
import hashlib
import io
import json
from pathlib import Path
import sys
import time
import types


D0 = "中心举办读书交流活动\n\n2026年9月5日，中心举办读书交流活动，共20人参加。"
FAILURE = "hook_selected_output_echo_budget_exhausted"


def digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def load_core(path: Path, data: Path):
    source = path.read_bytes()
    core = types.ModuleType("independent_terminal_review")
    core.__file__ = str(path)
    exec(compile(source, str(path), "exec"), core.__dict__)
    core._data_root = lambda: data
    for name in ("_handle_delivery_cleanliness_capability", "_handle_protective_capability", "_handle_under_length_capability", "_handle_over_length_capability"):
        setattr(core, name, lambda *args: None)
    return core, digest(source)


def event(turn: str) -> dict:
    return {"hook_event_name": "Stop", "session_id": "independent-review", "turn_id": turn,
            "stop_hook_active": True, "last_assistant_message": "controlled incorrect echo"}


def active_record(core, data: Path, turn: str) -> tuple[Path, dict]:
    record_path = core._record_path(event(turn))
    txn = data / "transactions" / "independent-review" / turn
    core._atomic_write(txn / "state.json", {"run_id": turn, "state": "TERMINAL_D0"})
    record = {"schema_version": 1, "request": "请起草消息。", "skill_seen": True, "txn": str(txn), "run_id": turn,
              "hook_phase": "awaiting_final_output", "emitted_output": D0, "emitted_sha256": digest(D0.encode()), "stop_attempts": 1}
    core._atomic_write(record_path, record)
    return record_path, record


def main_response(core, payload: dict) -> dict:
    old_stdin = sys.stdin
    stream = io.StringIO()
    started = time.monotonic()
    try:
        sys.stdin = io.StringIO(json.dumps(payload))
        with contextlib.redirect_stdout(stream):
            exit_code = core.main()
    finally:
        sys.stdin = old_stdin
    return {"response": json.loads(stream.getvalue()), "exit_code": exit_code,
            "seconds": round(time.monotonic() - started, 3)}


def lock_timeout(core, data: Path) -> dict:
    record_path, _ = active_record(core, data, "locked-echo")
    with core._record_lock(record_path):
        contender = core._acquire_file_lock(record_path.with_suffix(".state-lock"))
        if contender is not None:
            core._release_bootstrap_lock(*contender)
            raise RuntimeError("OS lock did not exclude an independent open handle")
        held = main_response(core, event("locked-echo"))
    released = main_response(core, event("locked-echo"))
    return {"held": held, "after_release": released,
            "pass": held["response"].get("continue") is False and released["response"].get("decision") == "block"}


def stale_terminal(core, data: Path, failed: bool) -> dict:
    turn = "terminal-failure" if failed else "terminal-success"
    record_path, stale = active_record(core, data, turn)
    terminal = {"schema_version": 1, "hook_phase": "failed_bounded" if failed else "complete",
                "data_retention_state": core.REDACTED_RECORD_STATE, "delivery_verified": not failed,
                "emitted_sha256": digest(D0.encode()), "stop_attempts": 4 if failed else 1}
    if failed:
        terminal["failure_reason"] = FAILURE
    core._atomic_write(record_path, terminal)
    before = digest(record_path.read_bytes())
    response_before_finish = core._handle_selected_output_echo(event(turn), record_path, stale, 1)
    response = core._finish_stop_response(record_path, stale, response_before_finish)
    persisted = core._read_json(record_path)
    expected = response.get("continue") is False if failed else response.get("continue") is True
    return {"terminal": "failed" if failed else "complete", "caller_refreshed": stale == terminal,
            "record_unchanged": before == digest(record_path.read_bytes()),
            "raw_keys_in_record": sorted(set(persisted) & core.RAW_RECORD_KEYS),
            "response_before_finish": response_before_finish, "response": response,
            "pass": expected and stale == terminal and before == digest(record_path.read_bytes())}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--core", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    core, core_hash = load_core(args.core.resolve(), output / "data")
    result = {"scope": "Offline lock and stale-writer checks only. Original short D0 is reused. Other capability handlers are bypassed; no gate subprocess or model is invoked. No bootstrap/HostAbort claim.",
              "core_sha256": core_hash, "d0_sha256": digest(D0.encode()), "model_calls": 0,
              "lock_timeout": lock_timeout(core, output / "data"),
              "stale_terminal": [stale_terminal(core, output / "data", failed) for failed in (True, False)]}
    result["pass"] = result["lock_timeout"]["pass"] and all(row["pass"] for row in result["stale_terminal"])
    (output / "result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
