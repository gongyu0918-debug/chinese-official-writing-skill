#!/usr/bin/env python3
"""Map documented Codex and WorkBuddy/CodeBuddy events to the shared gate."""

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
ALLOWED_POST_TOOL_NAMES = {"Bash", "Read", "Skill"}
ADAPTER_PATH = Path(__file__).resolve()
ADAPTER_ROOT = ADAPTER_PATH.parents[1]
PACKAGED_SKILL_ROOT = ADAPTER_ROOT / "skills" / "chinese-official-writing"
SKILL_ROOT = PACKAGED_SKILL_ROOT if PACKAGED_SKILL_ROOT.is_dir() else ADAPTER_ROOT
CORE_BRIDGE_PATH = SKILL_ROOT / "hooks" / "gate_stop_hook.py"
CAPABILITY_CONFIG_PATH = ADAPTER_ROOT / "hook-capability.json"
TURN_STATE_DIRECTORY = "workbuddy-adapter-turns"
CORE_DATA_DIRECTORY = "shared-gate-core"
STATE_SCHEMA_VERSION = 1
SAFE_KEY_MAX_LENGTH = 120
TURN_DIGEST_LENGTH = 16
MAX_TRANSCRIPT_BYTES = 8_000_000
_MISSING = object()
SUPPORTED_CAPABILITIES = {"delivery_review", "protective_expansion", "under_length"}


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


def _host_paths() -> tuple[str, Path] | None:
    if os.environ.get("PLUGIN_ROOT"):
        host = "codex"
        raw_root = os.environ.get("PLUGIN_ROOT")
        raw_data = os.environ.get("PLUGIN_DATA")
    elif os.environ.get("CODEBUDDY_PLUGIN_ROOT"):
        host = "workbuddy"
        raw_root = os.environ.get("CODEBUDDY_PLUGIN_ROOT")
        raw_data = os.environ.get("CODEBUDDY_PLUGIN_DATA")
    else:
        return None
    if not raw_root or not raw_data:
        return None
    try:
        plugin_root = Path(raw_root).expanduser().resolve()
        data_root = Path(raw_data).expanduser().resolve()
    except OSError:
        return None
    if plugin_root != ADAPTER_ROOT or not CORE_BRIDGE_PATH.is_file():
        return None
    return host, data_root


def _turn_state_path(data_root: Path, session_id: str) -> Path:
    return data_root / TURN_STATE_DIRECTORY / f"{_safe_key(session_id)}.json"


def _start_workbuddy_turn(data_root: Path, session_id: str, prompt: str) -> str | None:
    path = _turn_state_path(data_root, session_id)
    current = _read_json(path) or {}
    counter = current.get("counter")
    if not isinstance(counter, int) or isinstance(counter, bool) or counter < 0:
        counter = 0
    counter += 1
    digest = hashlib.sha256(prompt.encode("utf-8")).hexdigest()[:TURN_DIGEST_LENGTH]
    turn_id = f"workbuddy-{counter}-{digest}"
    try:
        _atomic_write_json(
            path,
            {"schema_version": STATE_SCHEMA_VERSION, "counter": counter, "turn_id": turn_id},
        )
    except OSError:
        return None
    return turn_id


def _active_workbuddy_turn(data_root: Path, session_id: str) -> str | None:
    value = _read_json(_turn_state_path(data_root, session_id))
    if value is None:
        return None
    turn_id = value.get("turn_id")
    return turn_id if isinstance(turn_id, str) and turn_id else None


def _recover_workbuddy_prompt(event: dict[str, Any]) -> str | None:
    """Recover the current prompt when CodeBuddy registers plugin hooks late."""
    session_id = event.get("session_id")
    raw_path = event.get("transcript_path")
    if not isinstance(session_id, str) or not session_id:
        return None
    if not isinstance(raw_path, str) or not raw_path:
        return None
    try:
        path = Path(raw_path).expanduser().resolve(strict=True)
        if path.name != f"{session_id}.jsonl" or path.stat().st_size > MAX_TRANSCRIPT_BYTES:
            return None
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError):
        return None
    for line in reversed(lines):
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(item, dict) or item.get("sessionId") != session_id:
            continue
        if item.get("type") != "message" or item.get("role") != "user":
            continue
        content = item.get("content")
        if not isinstance(content, list):
            continue
        texts = [
            part.get("text")
            for part in content
            if isinstance(part, dict)
            and part.get("type") == "input_text"
            and isinstance(part.get("text"), str)
            and part.get("text").strip()
        ]
        if texts:
            return "\n".join(texts)
    return None


def _normalized_tool_input(event: dict[str, Any]) -> dict[str, Any] | None:
    tool_name = event.get("tool_name")
    tool_input = event.get("tool_input")
    if tool_name not in ALLOWED_POST_TOOL_NAMES or not isinstance(tool_input, dict):
        return None
    if tool_name == "Bash":
        command = tool_input.get("command") or tool_input.get("cmd")
    elif tool_name == "Read":
        command = tool_input.get("file_path")
    else:
        skill_name = tool_input.get("skill")
        command = str(PACKAGED_SKILL_ROOT / "SKILL.md") if skill_name == "chinese-official-writing" else None
    if not isinstance(command, str) or not command:
        return None
    return {"command": command}


def _map_event(
    event: dict[str, Any], host: str, data_root: Path
) -> dict[str, Any] | None:
    name = event.get("hook_event_name")
    session_id = event.get("session_id")
    cwd = event.get("cwd")
    if name not in ALLOWED_EVENTS or not isinstance(session_id, str) or not session_id:
        return None
    if not isinstance(cwd, str) or not cwd:
        return None

    if host == "codex":
        turn_id = event.get("turn_id")
        if not isinstance(turn_id, str) or not turn_id:
            return None
    elif name == "UserPromptSubmit":
        prompt = event.get("prompt")
        if not isinstance(prompt, str) or not prompt.strip():
            return None
        turn_id = _start_workbuddy_turn(data_root, session_id, prompt)
        if turn_id is None:
            return None
    else:
        turn_id = _active_workbuddy_turn(data_root, session_id)
        if turn_id is None:
            return None

    mapped: dict[str, Any] = {
        "hook_event_name": name,
        "session_id": session_id,
        "turn_id": turn_id,
        "cwd": cwd,
    }
    if name == "UserPromptSubmit":
        prompt = event.get("prompt")
        if not isinstance(prompt, str) or not prompt.strip():
            return None
        mapped["prompt"] = prompt
        return mapped
    if name == "PostToolUse":
        tool_input = _normalized_tool_input(event)
        if tool_input is None:
            return None
        mapped["tool_input"] = tool_input
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
    capability = _selected_capability() or "delivery_review"
    overrides = {
        "COW_GATE_HOOK_DATA": str(data_root / CORE_DATA_DIRECTORY),
        "COW_GATE_CAPABILITY": capability,
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


def _host_response(host: str, value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        return _allow()
    reason = value.get("reason")
    if value.get("decision") != "block" or not isinstance(reason, str):
        return _allow()
    if host == "workbuddy":
        return {"continue": False, "reason": reason}
    return {"decision": "block", "reason": reason}


def handle(event: dict[str, Any]) -> dict[str, Any]:
    paths = _host_paths()
    if paths is None or not isinstance(event, dict):
        return _allow()
    host, data_root = paths
    bridge = _load_core_bridge()
    if bridge is None or not callable(getattr(bridge, "handle", None)):
        return _allow()
    try:
        with _bridge_environment(data_root):
            session_id = event.get("session_id")
            event_name = event.get("hook_event_name")
            if (
                host == "workbuddy"
                and event_name in {"PostToolUse", "Stop"}
                and isinstance(session_id, str)
                and not _active_workbuddy_turn(data_root, session_id)
            ):
                prompt = _recover_workbuddy_prompt(event)
                turn_id = (
                    _start_workbuddy_turn(data_root, session_id, prompt)
                    if prompt is not None
                    else None
                )
                cwd = event.get("cwd")
                if turn_id is not None and isinstance(cwd, str) and cwd:
                    bridge.handle(
                        {
                            "hook_event_name": "UserPromptSubmit",
                            "session_id": session_id,
                            "turn_id": turn_id,
                            "cwd": cwd,
                            "prompt": prompt,
                        }
                    )
            mapped = _map_event(event, host, data_root)
            if mapped is None:
                return _allow()
            return _host_response(host, bridge.handle(mapped))
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
