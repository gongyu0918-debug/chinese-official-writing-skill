"""Real-D0 lifecycle plus labeled terminal replay/concurrency fault injection."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import threading
from unittest import mock


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--core-root", type=Path, required=True)
    parser.add_argument("--sample", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    source = args.core_root / "chinese-official-writing/hooks/core/gate_stop_hook.py"
    spec = importlib.util.spec_from_file_location("lifecycle_gate", source)
    assert spec and spec.loader
    hook = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(hook)
    sample = json.loads(args.sample.read_text(encoding="utf-8"))
    request, d0 = sample["request"], sample["d0"]
    os.environ.update(COW_GATE_HOOK_DATA=str(args.output / "data"),
                      PLUGIN_ROOT=str(args.output / "plugin"), COW_GATE_CAPABILITY="delivery_review")
    events = []

    def event(name, turn="real", **kwargs):
        return dict(hook_event_name=name, session_id="four-fixes", turn_id=turn,
                    cwd=str(args.core_root), **kwargs)

    def call(name, **kwargs):
        value = event(name, **kwargs)
        response = hook.handle(value)
        path = hook._record_path(value)
        events.append({"event": value, "response": response, "record": hook._read_json(path)})
        return response

    def start(turn="real"):
        call("UserPromptSubmit", turn=turn, prompt=request)
        skill = Path(os.environ["PLUGIN_ROOT"]) / "skills/chinese-official-writing/SKILL.md"
        call("PostToolUse", turn=turn, tool_input={"cmd": f'Get-Content "{skill}"'}, tool_response={"exit_code": 0})
        response = call("Stop", turn=turn, last_assistant_message=d0, stop_hook_active=False)
        return response["reason"].split("不要加说明：\n", 1)[1]

    selected = start()
    assert selected == d0, "Fresh complete-date control must be unchanged"
    paused, resume = threading.Event(), threading.Event()
    errors = []
    # Same logical boundary: pause after the stale read, before guarded state commit.
    target = "_write_record" if hasattr(hook, "_write_record") else "_atomic_write"
    original = getattr(hook, target)

    def delayed(*a, **kw):
        if threading.current_thread().name == "late-tool":
            paused.set()
            if not resume.wait(10):
                raise RuntimeError("fault scheduler timed out")
        return original(*a, **kw)

    def late_tool():
        try:
            call("PostToolUse", tool_input={"cmd": "Get-Content supporting-material.txt"}, tool_response={"exit_code": 0})
        except Exception as exc:
            errors.append(repr(exc))

    with mock.patch.object(hook, target, side_effect=delayed):
        thread = threading.Thread(target=late_tool, name="late-tool")
        thread.start()
        assert paused.wait(5), "late event never reached commit boundary"
        try:
            terminal = call("Stop", last_assistant_message=selected, stop_hook_active=True)
        finally:
            resume.set()
            thread.join(10)
        assert not thread.is_alive() and not errors, errors
    after_race = hook._read_json(hook._record_path(event("Stop")))
    call("UserPromptSubmit", prompt=request)
    call("PostToolUse", tool_input={"cmd": f'Get-Content "{Path(os.environ["PLUGIN_ROOT"]) / "skills/chinese-official-writing/SKILL.md"}"'}, tool_response={"exit_code": 0})
    replay_stop = call("Stop", last_assistant_message=selected, stop_hook_active=True)
    after_replay = hook._read_json(hook._record_path(event("Stop")))
    next_selected = start("next-real-turn")
    next_response = call("Stop", turn="next-real-turn", last_assistant_message=next_selected, stop_hook_active=True)
    result = {"source_sample_sha256": hashlib.sha256(args.sample.read_bytes()).hexdigest(),
              "core_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
              "d0_sha256": hashlib.sha256(d0.encode()).hexdigest(),
              "terminal": terminal, "after_race": after_race, "after_replay": after_replay,
              "replay_stop": replay_stop, "next_turn": next_response,
              "selected_unchanged": selected == d0 == next_selected,
              "race_raw_restored": any(k in after_race for k in ("request", "emitted_output", "txn")),
              "replay_raw_restored": any(k in after_replay for k in ("request", "emitted_output", "txn")),
              "fault_injection": "Replay original request; pause late PostToolUse before guarded commit",
              "events": events}
    (args.output / "result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({k: v for k, v in result.items() if k not in ("events", "after_race", "after_replay")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
