#!/usr/bin/env python3
"""Map verified Claude Code hook events to the existing bounded gate bridge."""

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
from types import ModuleType
from typing import Any, Iterator


ALLOWED_EVENTS = {"UserPromptSubmit", "PostToolUse", "Stop"}
ALLOWED_POST_TOOL_NAMES = {"Bash", "Read"}
ADAPTER_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ADAPTER_ROOT / "skills" / "chinese-official-writing"
CORE_BRIDGE_PATH = SKILL_ROOT / "hooks" / "gate_stop_hook.py"
TURN_STATE_DIRECTORY = "claude-adapter-turns"
CORE_DATA_DIRECTORY = "claude-gate-core"
STATE_SCHEMA_VERSION = 1
SAFE_KEY_MAX_LENGTH = 120
TURN_DIGEST_LENGTH = 16
_MISSING = object()


def _allow() -> dict[str, Any]:
    return {"continue": True}


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


def _host_paths() -> tuple[Path, Path] | None:
    raw_root = os.environ.get("CLAUDE_PLUGIN_ROOT")
    raw_data = os.environ.get("CLAUDE_PLUGIN_DATA")
    if not raw_root or not raw_data:
        return None
    try:
        plugin_root = Path(raw_root).expanduser().resolve()
        data_root = Path(raw_data).expanduser().resolve()
    except OSError:
        return None
    if plugin_root != ADAPTER_ROOT or not CORE_BRIDGE_PATH.is_file():
        return None
    return plugin_root, data_root


def _turn_state_path(data_root: Path, session_id: str) -> Path:
    return data_root / TURN_STATE_DIRECTORY / f"{_safe_key(session_id)}.json"


def _start_turn(data_root: Path, session_id: str, prompt: str) -> str | None:
    path = _turn_state_path(data_root, session_id)
    current = _read_json(path) or {}
    counter = current.get("counter")
    if not isinstance(counter, int) or isinstance(counter, bool) or counter < 0:
        counter = 0
    counter += 1
    digest = hashlib.sha256(prompt.encode("utf-8")).hexdigest()[:TURN_DIGEST_LENGTH]
    turn_id = f"claude-{counter}-{digest}"
    try:
        _atomic_write_json(
            path,
            {
                "schema_version": STATE_SCHEMA_VERSION,
                "counter": counter,
                "turn_id": turn_id,
            },
        )
    except OSError:
        return None
    return turn_id


def _active_turn(data_root: Path, session_id: str) -> str | None:
    value = _read_json(_turn_state_path(data_root, session_id))
    if value is None:
        return None
    turn_id = value.get("turn_id")
    return turn_id if isinstance(turn_id, str) and turn_id else None


def _common_event(event: dict[str, Any], turn_id: str) -> dict[str, Any]:
    return {
        "hook_event_name": event["hook_event_name"],
        "session_id": event["session_id"],
        "turn_id": turn_id,
        "cwd": event["cwd"],
    }


def _map_event(event: dict[str, Any], data_root: Path) -> dict[str, Any] | None:
    name = event.get("hook_event_name")
    session_id = event.get("session_id")
    cwd = event.get("cwd")
    if name not in ALLOWED_EVENTS or not isinstance(session_id, str) or not session_id:
        return None
    if not isinstance(cwd, str) or not cwd:
        return None
    if name == "UserPromptSubmit":
        prompt = event.get("prompt")
        if not isinstance(prompt, str) or not prompt.strip():
            return None
        turn_id = _start_turn(data_root, session_id, prompt)
        if turn_id is None:
            return None
        mapped = _common_event(event, turn_id)
        mapped["prompt"] = prompt
        return mapped

    turn_id = _active_turn(data_root, session_id)
    if turn_id is None:
        return None
    mapped = _common_event(event, turn_id)
    if name == "PostToolUse":
        tool_name = event.get("tool_name")
        tool_input = event.get("tool_input")
        if tool_name not in ALLOWED_POST_TOOL_NAMES or not isinstance(tool_input, dict):
            return None
        if tool_name == "Bash":
            command = tool_input.get("command")
            if not isinstance(command, str) or not command:
                return None
            mapped["tool_input"] = {"command": command}
        else:
            file_path = tool_input.get("file_path")
            if not isinstance(file_path, str) or not file_path:
                return None
            mapped["tool_input"] = {"command": file_path}
        response = event.get("tool_response")
        if isinstance(response, dict):
            mapped["tool_response"] = response
        return mapped

    stop_hook_active = event.get("stop_hook_active")
    message = event.get("last_assistant_message")
    if not isinstance(stop_hook_active, bool) or not isinstance(message, str):
        return None
    mapped["stop_hook_active"] = stop_hook_active
    mapped["last_assistant_message"] = message
    return mapped


def _load_core_bridge() -> ModuleType | None:
    try:
        spec = importlib.util.spec_from_file_location("cow_shared_gate_bridge", CORE_BRIDGE_PATH)
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


def _valid_response(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        return _allow()
    if value.get("decision") == "block" and isinstance(value.get("reason"), str):
        return {"decision": "block", "reason": value["reason"]}
    return _allow()


def handle(event: dict[str, Any]) -> dict[str, Any]:
    paths = _host_paths()
    if paths is None or not isinstance(event, dict):
        return _allow()
    _, data_root = paths
    mapped = _map_event(event, data_root)
    if mapped is None:
        return _allow()
    bridge = _load_core_bridge()
    if bridge is None or not callable(getattr(bridge, "handle", None)):
        return _allow()
    try:
        with _bridge_environment(data_root):
            return _valid_response(bridge.handle(mapped))
    except (OSError, RuntimeError, ValueError):
        return _allow()


def main() -> int:
    try:
        event = json.load(sys.stdin)
        result = handle(event if isinstance(event, dict) else {})
    except Exception:
        result = _allow()
    sys.stdout.write(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
