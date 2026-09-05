#!/usr/bin/env python3
"""Same real D0, actual core subprocesses, exact selected echo; no model call."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def main() -> None:
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
    record_path = data / "candidate-ai-gate-hook/cleanup/normal.json"
    events = []

    def call(name, **fields):
        payload = dict(hook_event_name=name, session_id="cleanup", turn_id="normal", cwd=str(args.source_root), **fields)
        completed = subprocess.run([sys.executable, "-B", "-X", "utf8", str(source)], input=json.dumps(payload, ensure_ascii=False).encode("utf-8"), capture_output=True, env=env, cwd=args.source_root, timeout=35)
        response = json.loads(completed.stdout)
        record = json.loads(record_path.read_bytes()) if record_path.exists() else None
        events.append(dict(event=payload, exit_code=completed.returncode, stdout=completed.stdout.decode("utf-8"), stderr=completed.stderr.decode("utf-8"), response=response, record=record))
        return response, record

    call("UserPromptSubmit", prompt=sample["request"])
    call("PostToolUse", tool_input={"cmd": f'Get-Content "{skill}"'}, tool_response={"exit_code": 0, "output": skill_raw.decode("utf-8")})
    first, record = call("Stop", last_assistant_message=d0, stop_hook_active=False)
    selected = record.get("emitted_output")
    assert first.get("decision") == "block" and isinstance(selected, str)
    assert sha(selected.encode("utf-8")) == record["emitted_sha256"]
    final, record = call("Stop", last_assistant_message=selected, stop_hook_active=True)
    duplicate, record = call("Stop", last_assistant_message=selected, stop_hook_active=True)
    raw_files = []
    for path in data.rglob("*"):
        if path.is_file() and path.suffix not in {".state-lock", ".bootstrap-lock"} and "中心举办读书交流活动".encode("utf-8") in path.read_bytes():
            raw_files.append(path.relative_to(data).as_posix())
    result = dict(core_sha256=sha(source.read_bytes()), skill_sha256=sha(skill_raw), sample_sha256=sha(sample_raw), script_sha256=sha(Path(__file__).read_bytes()), d0_sha256=sha(d0.encode("utf-8")), selected_sha256=sha(selected.encode("utf-8")), model_calls=0, exact_echo_is_driver_copy=True, selected_unchanged=(selected == d0), final=final, duplicate=duplicate, final_record=record, raw_content_files=raw_files, events=events)
    (args.output / "result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    assert result["selected_unchanged"] and final == duplicate == {"continue": True}
    assert record.get("delivery_verified") is True and "request" not in record and not raw_files
    print(json.dumps({k: v for k, v in result.items() if k not in {"events", "final_record"}}, ensure_ascii=False))


if __name__ == "__main__":
    main()
