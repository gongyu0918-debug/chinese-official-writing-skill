#!/usr/bin/env python3
"""Same real D0: an unbootstrapped turn must not delete a neighboring turn txn."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--sample", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.source_root = args.source_root.resolve()
    args.output = args.output.resolve()
    args.output.mkdir(parents=True, exist_ok=False)
    sample_raw = args.sample.read_bytes()
    sample = json.loads(sample_raw)
    d0 = sample["d0"]
    assert sha(d0.encode("utf-8")) == sample["receipt"]["final_sha256"]
    (args.output / "sample.json").write_bytes(sample_raw)
    source = args.source_root / "chinese-official-writing/hooks/core/gate_stop_hook.py"
    skill = args.source_root / "chinese-official-writing/SKILL.md"
    skill_raw = skill.read_bytes()
    data = args.output / "data"
    env = {k: v for k, v in os.environ.items() if not k.startswith("COW_GATE_") and k not in {"PLUGIN_ROOT", "PLUGIN_DATA"}}
    env.update(COW_GATE_HOOK_DATA=str(data), COW_GATE_CAPABILITY="delivery_review", PYTHONDONTWRITEBYTECODE="1", PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
    events = []

    def call(name, turn, **fields):
        payload = dict(hook_event_name=name, session_id="turn-collision", turn_id=turn, cwd=str(args.source_root), **fields)
        completed = subprocess.run([sys.executable, "-B", "-X", "utf8", str(source)], input=json.dumps(payload, ensure_ascii=False).encode("utf-8"), capture_output=True, env=env, cwd=args.source_root, timeout=35)
        response = json.loads(completed.stdout)
        path = data / "candidate-ai-gate-hook/turn-collision" / f"{turn}.json"
        record = json.loads(path.read_bytes()) if path.exists() else None
        events.append(dict(event=payload, exit_code=completed.returncode, response=response, record=record, stderr=completed.stderr.decode("utf-8")))
        return response, record

    for turn in ("t-inputs", "t"):
        call("UserPromptSubmit", turn, prompt=sample["request"])
        call("PostToolUse", turn, tool_input={"cmd":f'Get-Content "{skill}"'}, tool_response={"exit_code":0,"output":skill_raw.decode("utf-8")})
        if turn == "t-inputs":
            first, active = call("Stop", turn, last_assistant_message=d0, stop_hook_active=False)
            assert first.get("decision") == "block"
            selected = active["emitted_output"]
    txn = Path(active["txn"])
    before_abort = {p.relative_to(txn).as_posix():sha(p.read_bytes()) for p in txn.rglob("*") if p.is_file()}
    abort, cancelled = call("HostAbort", "t", abort_reason="turn_changed")
    after_abort = {p.relative_to(txn).as_posix():sha(p.read_bytes()) for p in txn.rglob("*") if p.is_file()}
    final, delivered = call("Stop", "t-inputs", last_assistant_message=selected, stop_hook_active=True)
    result = dict(core_sha256=sha(source.read_bytes()), script_sha256=sha(Path(__file__).read_bytes()), sample_sha256=sha(sample_raw), d0_sha256=sha(d0.encode("utf-8")), model_calls=0, turns_are_accepted_by_core=True, active_turn="t-inputs", cancelled_unbootstrapped_turn="t", before_abort=before_abort, after_abort=after_abort, active_artifacts_unchanged=before_abort == after_abort, abort=abort, cancelled_record=cancelled, final=final, final_record=delivered, delivery_verified=delivered.get("delivery_verified") is True, events=events)
    (args.output / "result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({k:result[k] for k in ("core_sha256","d0_sha256","model_calls","active_artifacts_unchanged","delivery_verified","abort","final")},ensure_ascii=False))


if __name__ == "__main__":
    main()
