#!/usr/bin/env python3
"""Map Kimi Code plugin events and the exact current wire D0 to the shared gate."""

from __future__ import annotations

from contextlib import contextmanager
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import time
from types import ModuleType
from typing import Any, Iterator


ALLOWED_EVENTS = {"UserPromptSubmit", "PostToolUse", "Stop"}
ALLOWED_POST_TOOL_NAMES = {"Skill", "Read", "ReadFile", "Bash"}
ADAPTER_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ADAPTER_ROOT / "skills" / "chinese-official-writing"
CORE_BRIDGE_PATH = SKILL_ROOT / "hooks" / "gate_stop_hook.py"
CAPABILITY_CONFIG_PATH = ADAPTER_ROOT / "hook-capability.json"
TURN_STATE_DIRECTORY = "kimi-adapter-turns"
CORE_DATA_DIRECTORY = "kimi-gate-core"
PLUGIN_DATA_DIRECTORY = "plugin-data/chinese-official-writing-gate"
STATE_SCHEMA_VERSION = 1
SAFE_KEY_MAX_LENGTH = 120
TURN_DIGEST_LENGTH = 16
MAX_SESSION_INDEX_TAIL_BYTES = 4_000_000
MAX_CURRENT_TURN_WIRE_BYTES = 8_000_000
WIRE_FLUSH_ATTEMPTS = 20
WIRE_FLUSH_INTERVAL_SECONDS = 0.025
TERMINAL_FINISH_REASONS = {"end_turn", "completed", "stop"}
THINK_BLOCK_RE = re.compile(r"^\s*(?:<think>.*?</think>\s*)+", re.DOTALL)
_MISSING = object()
SUPPORTED_CAPABILITIES = {
    "delivery_review",
    "protective_expansion",
    "under_length",
    "over_length",
    "delivery_cleanliness",
    "repetition_cleanup",
}


def _allow() -> dict[str, Any]:
    return {}


def _safe_key(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("._")
    return cleaned[:SAFE_KEY_MAX_LENGTH] or "session"


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def _atomic_write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(value, handle, ensure_ascii=False, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass


def _selected_capability() -> str | None:
    value = _read_json(CAPABILITY_CONFIG_PATH)
    capability = value.get("capability") if value else None
    return capability if capability in SUPPORTED_CAPABILITIES else None


def _host_paths() -> tuple[Path, Path] | None:
    raw_root = os.environ.get("KIMI_PLUGIN_ROOT")
    raw_home = os.environ.get("KIMI_CODE_HOME")
    if not raw_root or not raw_home:
        return None
    try:
        plugin_root = Path(raw_root).expanduser().resolve()
        kimi_home = Path(raw_home).expanduser().resolve()
    except OSError:
        return None
    if plugin_root != ADAPTER_ROOT or not CORE_BRIDGE_PATH.is_file():
        return None
    return kimi_home, kimi_home / PLUGIN_DATA_DIRECTORY


def _turn_state_path(data_root: Path, session_id: str) -> Path:
    return data_root / TURN_STATE_DIRECTORY / f"{_safe_key(session_id)}.json"


def _session_wire(kimi_home: Path, session_id: str) -> Path | None:
    index_path = kimi_home / "session_index.jsonl"
    try:
        size = index_path.stat().st_size
        start = max(0, size - MAX_SESSION_INDEX_TAIL_BYTES)
        with index_path.open("rb") as handle:
            handle.seek(start)
            raw = handle.read(MAX_SESSION_INDEX_TAIL_BYTES + 1)
        if len(raw) > MAX_SESSION_INDEX_TAIL_BYTES:
            return None
        if start > 0:
            newline = raw.find(b"\n")
            if newline < 0:
                return None
            raw = raw[newline + 1 :]
        lines = raw.decode("utf-8").splitlines()
        sessions_root = (kimi_home / "sessions").resolve(strict=True)
    except (OSError, UnicodeError):
        return None
    for line in reversed(lines):
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(item, dict) or item.get("sessionId") != session_id:
            continue
        raw_dir = item.get("sessionDir")
        if not isinstance(raw_dir, str) or not raw_dir:
            return None
        try:
            session_dir = Path(raw_dir).expanduser().resolve(strict=True)
            if not session_dir.is_relative_to(sessions_root) or session_dir.name != session_id:
                return None
            wire = (session_dir / "agents" / "main" / "wire.jsonl").resolve(strict=True)
            if not wire.is_relative_to(session_dir) or not wire.is_file():
                return None
        except OSError:
            return None
        return wire
    return None


def _prompt_text(value: Any) -> str | None:
    if isinstance(value, str):
        return value if value.strip() else None
    if not isinstance(value, list):
        return None
    texts = [
        part.get("text")
        for part in value
        if isinstance(part, dict)
        and part.get("type") == "text"
        and isinstance(part.get("text"), str)
        and part.get("text").strip()
    ]
    text = "\n".join(texts)
    return text if text.strip() else None


def _start_turn(
    kimi_home: Path, data_root: Path, session_id: str, prompt: str
) -> str | None:
    wire = _session_wire(kimi_home, session_id)
    if wire is None:
        return None
    try:
        wire_offset = wire.stat().st_size
    except OSError:
        return None
    path = _turn_state_path(data_root, session_id)
    current = _read_json(path) or {}
    counter = current.get("counter")
    if not isinstance(counter, int) or isinstance(counter, bool) or counter < 0:
        counter = 0
    counter += 1
    digest = hashlib.sha256(prompt.encode("utf-8")).hexdigest()[:TURN_DIGEST_LENGTH]
    turn_id = f"kimi-{counter}-{digest}"
    try:
        _atomic_write_json(
            path,
            {
                "schema_version": STATE_SCHEMA_VERSION,
                "counter": counter,
                "turn_id": turn_id,
                "wire_path": str(wire),
                "wire_offset": wire_offset,
            },
        )
    except OSError:
        return None
    return turn_id


def _active_state(data_root: Path, session_id: str) -> dict[str, Any] | None:
    value = _read_json(_turn_state_path(data_root, session_id))
    if value is None:
        return None
    turn_id = value.get("turn_id")
    wire_path = value.get("wire_path")
    wire_offset = value.get("wire_offset")
    if not isinstance(turn_id, str) or not turn_id:
        return None
    if not isinstance(wire_path, str) or not wire_path:
        return None
    if not isinstance(wire_offset, int) or isinstance(wire_offset, bool) or wire_offset < 0:
        return None
    return value


def _wire_records(path: Path, offset: int) -> list[dict[str, Any]] | None:
    try:
        size = path.stat().st_size
        if size < offset or size - offset > MAX_CURRENT_TURN_WIRE_BYTES:
            return None
        with path.open("rb") as handle:
            handle.seek(offset)
            raw = handle.read(MAX_CURRENT_TURN_WIRE_BYTES + 1)
    except OSError:
        return None
    if len(raw) > MAX_CURRENT_TURN_WIRE_BYTES:
        return None
    try:
        text = raw.decode("utf-8")
    except UnicodeError:
        return None
    records: list[dict[str, Any]] = []
    for line in text.splitlines():
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            records.append(value)
    return records


def _completed_assistant_text(records: list[dict[str, Any]]) -> str | None:
    parts_by_step: dict[str, list[str]] = {}
    completed: list[str] = []
    for record in records:
        if record.get("type") != "context.append_loop_event":
            continue
        event = record.get("event")
        if not isinstance(event, dict):
            continue
        step_key = event.get("stepUuid") or event.get("uuid")
        if not isinstance(step_key, str) or not step_key:
            step_key = f"{event.get('turnId')}:{event.get('step')}"
        event_type = event.get("type")
        if event_type == "step.begin":
            parts_by_step.setdefault(step_key, [])
        elif event_type == "content.part":
            part = event.get("part")
            if (
                isinstance(part, dict)
                and part.get("type") == "text"
                and isinstance(part.get("text"), str)
            ):
                parts_by_step.setdefault(step_key, []).append(part["text"])
        elif event_type == "step.end" and event.get("finishReason") in TERMINAL_FINISH_REASONS:
            completed.append(step_key)
    for step_key in reversed(completed):
        raw = "".join(parts_by_step.get(step_key, []))
        if not raw.strip():
            continue
        cleaned = THINK_BLOCK_RE.sub("", raw).strip()
        if "<think>" in cleaned or "</think>" in cleaned:
            return None
        return cleaned if cleaned else None
    return None


def _current_d0(
    kimi_home: Path, session_id: str, state: dict[str, Any]
) -> str | None:
    current_wire = _session_wire(kimi_home, session_id)
    if current_wire is None:
        return None
    try:
        recorded_wire = Path(str(state["wire_path"])).expanduser().resolve(strict=True)
    except (KeyError, OSError):
        return None
    if recorded_wire != current_wire:
        return None
    offset = int(state["wire_offset"])
    for attempt in range(WIRE_FLUSH_ATTEMPTS):
        records = _wire_records(current_wire, offset)
        if records is None:
            return None
        message = _completed_assistant_text(records)
        if message is not None:
            return message
        if attempt + 1 < WIRE_FLUSH_ATTEMPTS:
            time.sleep(WIRE_FLUSH_INTERVAL_SECONDS)
    return None


def _normalized_tool_input(event: dict[str, Any]) -> dict[str, Any] | None:
    tool_name = event.get("tool_name")
    tool_input = event.get("tool_input")
    if tool_name not in ALLOWED_POST_TOOL_NAMES or not isinstance(tool_input, dict):
        return None
    if tool_name == "Bash":
        command = tool_input.get("command") or tool_input.get("cmd")
    elif tool_name in {"Read", "ReadFile"}:
        command = tool_input.get("path") or tool_input.get("file_path")
    else:
        skill_name = tool_input.get("skill") or tool_input.get("name")
        command = str(SKILL_ROOT / "SKILL.md") if skill_name == "chinese-official-writing" else None
    if not isinstance(command, str) or not command:
        return None
    return {"command": command}


def _map_event(
    event: dict[str, Any], kimi_home: Path, data_root: Path
) -> dict[str, Any] | None:
    name = event.get("hook_event_name")
    session_id = event.get("session_id")
    cwd = event.get("cwd")
    if name not in ALLOWED_EVENTS or not isinstance(session_id, str) or not session_id:
        return None
    if not isinstance(cwd, str) or not cwd:
        return None
    if name == "UserPromptSubmit":
        prompt = _prompt_text(event.get("prompt"))
        if prompt is None:
            return None
        turn_id = _start_turn(kimi_home, data_root, session_id, prompt)
        if turn_id is None:
            return None
        return {
            "hook_event_name": name,
            "session_id": session_id,
            "turn_id": turn_id,
            "cwd": cwd,
            "prompt": prompt,
        }
    state = _active_state(data_root, session_id)
    if state is None:
        return None
    mapped: dict[str, Any] = {
        "hook_event_name": name,
        "session_id": session_id,
        "turn_id": state["turn_id"],
        "cwd": cwd,
    }
    if name == "PostToolUse":
        tool_input = _normalized_tool_input(event)
        if tool_input is None:
            return None
        mapped["tool_input"] = tool_input
        output = event.get("tool_output")
        if isinstance(output, str):
            mapped["tool_output"] = {"output": output}
        return mapped
    stop_hook_active = event.get("stop_hook_active")
    if not isinstance(stop_hook_active, bool):
        return None
    message = _current_d0(kimi_home, session_id, state)
    if message is None:
        return None
    mapped["stop_hook_active"] = stop_hook_active
    mapped["last_assistant_message"] = message
    return mapped


def _load_core_bridge() -> ModuleType | None:
    try:
        spec = importlib.util.spec_from_file_location("cow_kimi_shared_gate", CORE_BRIDGE_PATH)
        if spec is None or spec.loader is None:
            return None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    except (ImportError, OSError, RuntimeError):
        return None
    return module


@contextmanager
def _bridge_environment(data_root: Path) -> Iterator[None]:
    overrides = {
        "COW_GATE_HOOK_DATA": str(data_root / CORE_DATA_DIRECTORY),
        "COW_GATE_CAPABILITY": _selected_capability() or "delivery_review",
    }
    previous = {key: os.environ.get(key, _MISSING) for key in overrides}
    try:
        os.environ.update(overrides)
        yield
    finally:
        for key, value in previous.items():
            if value is _MISSING:
                os.environ.pop(key, None)
            else:
                os.environ[key] = str(value)


def _host_response(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        return _allow()
    reason = value.get("reason")
    if value.get("decision") != "block" or not isinstance(reason, str):
        return _allow()
    return {
        "hookSpecificOutput": {
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }


def handle(event: dict[str, Any]) -> dict[str, Any]:
    paths = _host_paths()
    if paths is None or not isinstance(event, dict):
        return _allow()
    kimi_home, data_root = paths
    mapped = _map_event(event, kimi_home, data_root)
    if mapped is None:
        return _allow()
    bridge = _load_core_bridge()
    if bridge is None or not callable(getattr(bridge, "handle", None)):
        return _allow()
    try:
        with _bridge_environment(data_root):
            return _host_response(bridge.handle(mapped))
    except (OSError, RuntimeError, ValueError):
        return _allow()


def main() -> int:
    try:
        event = json.load(sys.stdin)
        result = handle(event if isinstance(event, dict) else {})
    except Exception:
        result = _allow()
    if result:
        sys.stdout.write(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
        sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
