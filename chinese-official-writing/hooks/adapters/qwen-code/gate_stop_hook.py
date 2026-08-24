#!/usr/bin/env python3
"""Map Qwen Code native-extension events to the shared bounded gate."""

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
ALLOWED_POST_TOOL_NAMES = {
    "skill",
    "read_file",
    "run_shell_command",
    "Skill",
    "ReadFile",
    "Bash",
}
ADAPTER_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ADAPTER_ROOT / "skills" / "chinese-official-writing"
CORE_BRIDGE_PATH = SKILL_ROOT / "hooks" / "gate_stop_hook.py"
CAPABILITY_CONFIG_PATH = ADAPTER_ROOT / "hook-capability.json"
TURN_STATE_DIRECTORY = "qwen-adapter-turns"
CORE_DATA_DIRECTORY = "qwen-gate-core"
PLUGIN_DATA_DIRECTORY = "plugin-data/chinese-official-writing-gate"
STATE_SCHEMA_VERSION = 1
SAFE_KEY_MAX_LENGTH = 120
TURN_DIGEST_LENGTH = 16
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


def _selected_capability() -> str | None:
    value = _read_json(CAPABILITY_CONFIG_PATH)
    capability = value.get("capability") if value else None
    return capability if capability in SUPPORTED_CAPABILITIES else None


def _runtime_root(event: dict[str, Any]) -> Path | None:
    for key in ("QWEN_RUNTIME_DIR", "QWEN_HOME"):
        raw = os.environ.get(key)
        if raw:
            try:
                return Path(raw).expanduser().resolve()
            except OSError:
                return None
    raw_transcript = event.get("transcript_path")
    if not isinstance(raw_transcript, str) or not raw_transcript:
        return None
    try:
        transcript = Path(raw_transcript).expanduser().resolve(strict=True)
    except OSError:
        return None
    if transcript.suffix.lower() != ".jsonl":
        return None
    for parent in transcript.parents:
        if parent.name == "projects":
            return parent.parent
    return None


def _host_data_root(event: dict[str, Any]) -> Path | None:
    if not CORE_BRIDGE_PATH.is_file():
        return None
    runtime_root = _runtime_root(event)
    return runtime_root / PLUGIN_DATA_DIRECTORY if runtime_root is not None else None


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
    turn_id = f"qwen-{counter}-{digest}"
    try:
        _atomic_write_json(
            path,
            {
                "schema_version": STATE_SCHEMA_VERSION,
                "counter": counter,
                "turn_id": turn_id,
                "stop_events": 0,
            },
        )
    except OSError:
        return None
    return turn_id


def _active_turn(data_root: Path, session_id: str) -> str | None:
    value = _read_json(_turn_state_path(data_root, session_id))
    turn_id = value.get("turn_id") if value else None
    return turn_id if isinstance(turn_id, str) and turn_id else None


def _consume_stop_position(data_root: Path, session_id: str) -> bool | None:
    """Return whether this is a continuation Stop and persist the next position.

    Qwen Code 0.22.0 reports ``stop_hook_active=true`` for every Stop event,
    including the first D0. The shared core uses the Claude-compatible meaning
    (false for D0, true for a Stop-requested continuation), so the native
    adapter reconstructs that distinction from its own current-turn counter.
    """

    path = _turn_state_path(data_root, session_id)
    value = _read_json(path)
    if value is None:
        return None
    stop_events = value.get("stop_events", 0)
    if not isinstance(stop_events, int) or isinstance(stop_events, bool) or stop_events < 0:
        return None
    value["stop_events"] = stop_events + 1
    try:
        _atomic_write_json(path, value)
    except OSError:
        return None
    return stop_events > 0


def _submitted_prompt(event: dict[str, Any]) -> str | None:
    value = event.get("submitted_prompt")
    return value if isinstance(value, str) and value.strip() else None


def _direct_skill_invocation(event: dict[str, Any]) -> bool:
    submitted = event.get("submitted_prompt")
    if not isinstance(submitted, str):
        return False
    return re.match(r"^/chinese-official-writing(?:\s|$)", submitted.lstrip()) is not None


def _normalized_tool_input(event: dict[str, Any]) -> dict[str, Any] | None:
    tool_name = event.get("tool_name")
    tool_input = event.get("tool_input")
    if tool_name not in ALLOWED_POST_TOOL_NAMES or not isinstance(tool_input, dict):
        return None
    if tool_name in {"run_shell_command", "Bash"}:
        command = tool_input.get("command") or tool_input.get("cmd")
    elif tool_name in {"read_file", "ReadFile"}:
        command = tool_input.get("file_path") or tool_input.get("path")
    else:
        skill_name = tool_input.get("skill") or tool_input.get("name")
        command = str(SKILL_ROOT / "SKILL.md") if skill_name == "chinese-official-writing" else None
    if not isinstance(command, str) or not command:
        return None
    return {"command": command}


def _map_event(event: dict[str, Any], data_root: Path) -> dict[str, Any] | None:
    name = event.get("hook_event_name")
    session_id = event.get("session_id")
    cwd = event.get("cwd")
    if name not in ALLOWED_EVENTS or not isinstance(session_id, str) or not session_id:
        return None
    if not isinstance(cwd, str) or not cwd:
        return None
    if name == "UserPromptSubmit":
        prompt = _submitted_prompt(event)
        if prompt is None:
            return None
        turn_id = _start_turn(data_root, session_id, prompt)
        if turn_id is None:
            return None
        return {
            "hook_event_name": name,
            "session_id": session_id,
            "turn_id": turn_id,
            "cwd": cwd,
            "prompt": prompt,
        }
    turn_id = _active_turn(data_root, session_id)
    if turn_id is None:
        return None
    mapped: dict[str, Any] = {
        "hook_event_name": name,
        "session_id": session_id,
        "turn_id": turn_id,
        "cwd": cwd,
    }
    if name == "PostToolUse":
        tool_input = _normalized_tool_input(event)
        if tool_input is None:
            return None
        mapped["tool_input"] = tool_input
        response = event.get("tool_response")
        if isinstance(response, dict):
            mapped["tool_response"] = response
        return mapped
    message = event.get("last_assistant_message")
    if not isinstance(event.get("stop_hook_active"), bool) or not isinstance(message, str):
        return None
    continuation = _consume_stop_position(data_root, session_id)
    if continuation is None:
        return None
    mapped["stop_hook_active"] = continuation
    mapped["last_assistant_message"] = message
    return mapped


def _load_core_bridge() -> ModuleType | None:
    try:
        spec = importlib.util.spec_from_file_location("cow_qwen_shared_gate", CORE_BRIDGE_PATH)
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
    if value.get("decision") == "block" and isinstance(reason, str):
        return {"decision": "block", "reason": reason}
    return _allow()


def handle(event: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(event, dict):
        return _allow()
    data_root = _host_data_root(event)
    if data_root is None:
        return _allow()
    mapped = _map_event(event, data_root)
    if mapped is None:
        return _allow()
    bridge = _load_core_bridge()
    if bridge is None or not callable(getattr(bridge, "handle", None)):
        return _allow()
    try:
        with _bridge_environment(data_root):
            value = bridge.handle(mapped)
            if mapped["hook_event_name"] == "UserPromptSubmit" and _direct_skill_invocation(
                event
            ):
                bridge.handle(
                    {
                        "hook_event_name": "PostToolUse",
                        "session_id": mapped["session_id"],
                        "turn_id": mapped["turn_id"],
                        "cwd": mapped["cwd"],
                        "tool_input": {"command": str(SKILL_ROOT / "SKILL.md")},
                        "tool_response": {"success": True},
                    }
                )
            return _host_response(value)
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
