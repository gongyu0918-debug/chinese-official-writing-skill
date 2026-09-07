"""In-memory checks for the exact review counterexamples; no model or file mutation."""
from contextlib import ExitStack, nullcontext
from copy import deepcopy
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[4]
CORE = "chinese-official-writing/hooks/core/gate_stop_hook.py"
CONTEXT = "chinese-official-writing/hooks/shared/revision_context.py"
RUNTIME = "chinese-official-writing/hooks/capabilities/delivery_cleanliness/runtime.py"


def load(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def lineage_checks(context, core):
    def row(role, content):
        return {"sessionId": "review", "type": role, "message": {"content": content}}

    def recover(current, error=False, external=False):
        target = core.SKILL_ROOT / ("../LICENSE" if external else "SKILL.md")
        rows = [row("user", "请根据材料写报告：甲局已完成10项。"),
                row("assistant", [{"type": "tool_use", "id": "read1", "name": "Read", "input": {"file_path": str(target)}}]),
                row("user", [{"type": "tool_result", "tool_use_id": "read1", "is_error": error, "content": "failed" if error else "ok"}]),
                row("user", current)]
        raw = "\n".join(json.dumps(r, ensure_ascii=False) for r in rows).encode()
        fake = SimpleNamespace(is_file=lambda: True, stat=lambda: SimpleNamespace(st_size=len(raw)),
                               open=lambda *args: io.BytesIO(raw))
        with patch.object(context, "Path", lambda p: fake if p == "memory-transcript" else Path(p)):
            return context.recover("memory-transcript", "review", current, core.SKILL_ROOT)

    revision = "请修改刚才的报告，更正为12项，给我完整稿。"
    fresh = "请修改下面这份报告，给我完整正文。\n\n乙校开展开学检查，结果尚待复核。"
    result = {"new_self_contained_document_rejected": recover(fresh) is None,
              "explicit_same_document_revision_retained": recover(revision) is not None,
              "failed_read_rejected": recover(revision, error=True) is None,
              "read_dotdot_outside_skill_rejected": recover(revision, external=True) is None}
    assert all(result.values()), result
    return result


def input_guards(core):
    results = {}
    for name, current, marker in (
        ("terminal", {"data_retention_state": core.REDACTED_RECORD_STATE}, None),
        ("cancel_pending", {"request": "原始要求"}, "turn_changed"),
    ):
        record = {"request": "原始要求", "source_text": "历史材料"}
        writes = []
        with patch.object(core, "_record_lock", lambda p: nullcontext()), \
             patch.object(core, "_read_json", return_value=current), \
             patch.object(core, "_pending_host_abort", return_value=marker), \
             patch.object(core, "_atomic_write", side_effect=lambda *a: writes.append("record")), \
             patch.object(core, "_atomic_write_text", side_effect=lambda *a: writes.append("raw")):
            accepted = core._write_bootstrap_inputs(Path("memory"), record, Path("inputs"), "原始要求", "稿件")
        results[name] = {"accepted": accepted, "writes": writes}
        assert accepted is False and writes == []
    return results


def cancellation_during_recovery(core):
    request = "请修改刚才的报告，给我完整稿，只发正文。"
    record = {"request": request, "skill_seen": True}
    flag, writes, aborts = {"pending": None}, [], []

    def recover(*args):
        flag["pending"] = "turn_changed"
        return {"source_text": "此前用户原始材料", "turn_count": 2, "sha256": "hash"}

    def abort(event):
        aborts.append(event["abort_reason"])
        flag["pending"] = None
        return {"continue": True}

    spec = SimpleNamespace(loader=SimpleNamespace(exec_module=lambda m: None))
    event = {"hook_event_name": "Stop", "session_id": "review", "turn_id": "2", "cwd": str(ROOT),
             "stop_hook_active": False, "last_assistant_message": "下面是正文。\n\n报告",
             "revision_transcript": {"format": "claude-code", "path": "memory"}}
    with ExitStack() as stack:
        stack.enter_context(patch.dict(os.environ, {"COW_GATE_CAPABILITY": "delivery_review"}))
        for target, replacement in {
            "_record_path": lambda e: Path("memory"),
            "_pending_host_abort": lambda p: flag["pending"],
            "_read_json": lambda p: deepcopy(record),
            "_skill_was_seen": lambda *a: True,
            "_record_lock": lambda p: nullcontext(),
            "_atomic_write": lambda *a: writes.append("write"),
            "handle_host_abort": abort,
        }.items():
            stack.enter_context(patch.object(core, target, replacement))
        stack.enter_context(patch.object(core.importlib.util, "spec_from_file_location", return_value=spec))
        stack.enter_context(patch.object(core.importlib.util, "module_from_spec", return_value=SimpleNamespace(recover=recover)))
        response = core.handle(event)
    result = {"abort_dispatch": aborts, "raw_writes": writes, "response": response}
    assert aborts == ["turn_changed"] and writes == []
    return result


def prepass_handoff(core, runtime, concurrent_failure):
    text = "报告正文"
    record = {"request": "只发正文。", "skill_seen": True, "cleanliness_prepass": True,
              "delivery_cleanliness_selected_sha256": hashlib.sha256(text.encode()).hexdigest(),
              "delivery_cleanliness": {"phase": runtime.PHASE_OUTPUT,
                  "original": "下面是正文。\n\n" + text,
                  "audit": {"selection": "D1", "delivery_verified": False}}}
    failed = {"data_retention_state": core.REDACTED_RECORD_STATE, "hook_phase": "failed_bounded",
              "failure_reason": "hook_selected_output_echo_budget_exhausted"}
    bootstraps = []

    def write(path, value):
        if concurrent_failure:
            value.clear()
            value.update(deepcopy(failed))
            return False
        return True

    event = {"hook_event_name": "Stop", "session_id": "review", "turn_id": "2", "cwd": str(ROOT),
             "stop_hook_active": True, "last_assistant_message": text}
    with ExitStack() as stack:
        for target, replacement in {
            "_record_path": lambda e: Path("memory"), "_read_json": lambda p: record,
            "_pending_host_abort": lambda p: None, "_skill_was_seen": lambda *a: True,
            "_bind_revision_context": lambda *a: None, "_load_delivery_cleanliness_runtime": lambda: runtime,
            "_write_record": write, "_redact_turn_data": lambda *a: None,
            "_handle_protective_capability": lambda *a: None,
            "_handle_under_length_capability": lambda *a: None,
            "_handle_over_length_capability": lambda *a: None,
            "_bootstrap_transaction": lambda e, *a: bootstraps.append(e["last_assistant_message"]),
        }.items():
            stack.enter_context(patch.object(core, target, replacement))
        response = core.handle(event)
    if concurrent_failure:
        assert response.get("continue") is False and bootstraps == []
    else:
        assert bootstraps == [text] and record.get("cleanliness_prepass_complete") is True
    return {"response": response, "bootstrap_drafts": bootstraps,
            "failure_reason": record.get("failure_reason")}


def run():
    core = load("core_review_current", CORE)
    context = load("core_review_context", CONTEXT)
    runtime = load("core_review_cleanliness", RUNTIME)
    return {"status": "PASS", "method": "pure functions and in-memory coordinator states only; no model/verdict or native lifecycle evidence",
            "source_sha256": {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in (CORE, CONTEXT, RUNTIME)},
            "lineage": lineage_checks(context, core), "source_input_guards": input_guards(core),
            "cancel_after_entry": cancellation_during_recovery(core),
            "prepass_normal_handoff": prepass_handoff(core, runtime, False),
            "prepass_failed_terminal_handoff": prepass_handoff(core, runtime, True)}


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
