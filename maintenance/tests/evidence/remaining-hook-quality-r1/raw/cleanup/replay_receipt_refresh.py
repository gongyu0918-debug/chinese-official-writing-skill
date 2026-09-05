#!/usr/bin/env python3
"""Labeled offline receipt fault control; no real draft or model response."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
from unittest import mock


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output = args.output.resolve()
    args.output.mkdir(parents=True, exist_ok=False)
    source = args.source_root.resolve() / "chinese-official-writing/hooks/core/gate_stop_hook.py"
    spec = importlib.util.spec_from_file_location("receipt_refresh_core", source)
    hook = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(hook)
    os.environ["COW_GATE_HOOK_DATA"] = str(args.output / "data")
    cases = []
    for trigger in ("Stop", "HostAbort"):
        event = dict(hook_event_name=trigger, session_id="receipt-refresh", turn_id=trigger.lower(), abort_reason="turn_changed")
        path = hook._record_path(event)
        initial = dict(data_retention_state=hook.REDACTED_RECORD_STATE, raw_artifact_delete_failures=0, hook_phase="failed_bounded", failure_reason="hook_selected_output_echo_budget_exhausted", delivery_verified=False)
        hook._atomic_write(path, initial)
        original_sha = sha(path.read_bytes())
        neighbor = path.with_name("other-turn.json")
        hook._atomic_write(neighbor, {"request": "synthetic-neighbor-control"})
        neighbor_sha = sha(neighbor.read_bytes())
        original_replace = hook.os.replace
        failures = []

        def one_failure(src, dst):
            if Path(dst) == path and not failures:
                failures.append("one receipt os.replace OSError; unlink remains available")
                raise OSError("injected receipt refresh failure")
            return original_replace(src, dst)

        with mock.patch.object(hook.os, "replace", side_effect=one_failure):
            first = hook.handle(event)
        after_first = dict(exists=path.exists(), sha256=sha(path.read_bytes()) if path.exists() else None, record=hook._read_json(path))
        second = hook.handle({**event, "hook_event_name": "Stop"})
        after_second = dict(exists=path.exists(), sha256=sha(path.read_bytes()) if path.exists() else None, record=hook._read_json(path))
        cases.append(dict(trigger=trigger, initial=initial, original_sha256=original_sha, failure_injected=failures, first=first, after_first=after_first, second=second, after_second=after_second, neighbor_unchanged=sha(neighbor.read_bytes()) == neighbor_sha))
    result = dict(core_sha256=sha(source.read_bytes()), script_sha256=sha(Path(__file__).read_bytes()), model_calls=0, evidence_type="synthetic terminal plus one OS replace failure; not natural model output", cases=cases)
    (args.output / "result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"core_sha256":result["core_sha256"], "cases":[dict(trigger=c["trigger"], injected=bool(c["failure_injected"]), first_continue=c["first"].get("continue"), first_receipt_exists=c["after_first"]["exists"], second_continue=c["second"].get("continue"), original_bytes_preserved=c["original_sha256"] == c["after_first"]["sha256"], neighbor_unchanged=c["neighbor_unchanged"]) for c in cases]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
