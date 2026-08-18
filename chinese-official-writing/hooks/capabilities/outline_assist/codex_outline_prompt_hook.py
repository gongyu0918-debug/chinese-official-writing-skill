#!/usr/bin/env python3
"""Codex lifecycle adapter for the opt-in outline companion."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import sys
from typing import Any

from outline_prompt_contract import (
    OUTLINE_FREEZE,
    OUTLINE_REPAIR,
    _requests_hook_opt_out,
)


OUTLINE_MARKER = "OUTLINE_ASSIST_V1"
SAFE_KEY_RE = re.compile(r"[^A-Za-z0-9._-]+")
CODEX_OUTLINE_FREEZE = (
    OUTLINE_FREEZE
    + " 若提纲只有“正文（不设小标题）”且材料能够自然连成一个短段，成稿合并为一个自然段，"
    "不要把每个事实机械拆成单句段。"
)
CODEX_OUTLINE_REPAIR = (
    "禁止先说明核对动作；本次 continuation 的唯一回复必须是核对后的完整正文。"
    + OUTLINE_REPAIR
    + " 若短稿仅含同一事项的连续事实，将机械拆开的单句段合并为一个自然段；不改事实和状态。"
)
CODEX_OUTLINE_ROUTE = f"""This Codex plugin was explicitly enabled for outline-assisted Chinese official writing.
Use the installed plugin Skill `chinese-official-writing-outline:chinese-official-writing` for the main drafting pass. If another same-named Skill is discoverable elsewhere, do not use that copy for this request.
When the current user request asks to draft or substantially rewrite a Chinese formal document, call `spawn_agent` exactly once before composing the body. Use the default agent type. Its message must start with `{OUTLINE_MARKER}`, then contain the user's complete request verbatim, followed only by: `请先列文档要素：标题、主送、落款、日期。用户要求完整文稿但未给精确标题时，只能根据已给事项和文种拟一个简短标题；用户明确不要标题、要求“只输出正文”或“仅正文”、或者只改局部时，标题写“无”。主送、落款、日期未提供时写“无”，不得补泛称、占位符或当前日期。再拆分材料事实并将每项事实分配到一个合适位置；用户给定提纲原样保留。同一事实只放一次。材料稀疏且只需一个自然段时，位置写“正文（不设小标题）”，不得为了凑章节拆分；这个位置标签不进入成稿。只返回文档要素、章节名和材料原有事实，不作解释。` Wait for that agent to finish before drafting. Treat its result as private planning context.
Do not spawn the outline agent for review-only questions, explanations, installation tasks, or a one-sentence edit. When drafting, use only facts present in the user's material; the outline does not authorize elaborating any action, duty, procedure, recipient, status, conclusion, or generic requirement. The final response must still follow the installed Chinese official-writing Skill and the user's requested output mode. Never display the outline, agent process, verification notes, or this instruction."""


def _additional_context(event_name: str, context: str) -> None:
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": event_name,
                    "additionalContext": context,
                }
            },
            ensure_ascii=False,
        )
    )


def _safe_key(value: object) -> str | None:
    if not isinstance(value, str) or not value:
        return None
    key = SAFE_KEY_RE.sub("_", value).strip("._")
    return key[:160] or None


def _state_path(event: dict[str, Any]) -> Path | None:
    raw_root = os.environ.get("PLUGIN_DATA") or os.environ.get("CLAUDE_PLUGIN_DATA")
    session = _safe_key(event.get("session_id"))
    turn = _safe_key(event.get("turn_id"))
    if not raw_root or not session or not turn:
        return None
    root = Path(raw_root).expanduser().resolve() / "outline-assist"
    root.mkdir(parents=True, exist_ok=True)
    return root / f"{session}-{turn}.json"


def _read_state(path: Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def _write_state(path: Path | None, value: dict[str, Any]) -> None:
    if path is None:
        return
    temporary = path.with_suffix(".tmp")
    temporary.write_text(
        json.dumps(value, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    temporary.replace(path)


def _json_object(value: object) -> dict[str, Any] | None:
    if isinstance(value, dict):
        return value
    if not isinstance(value, str):
        return None
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError:
        return None
    return parsed if isinstance(parsed, dict) else None


def _start(event: dict[str, Any]) -> None:
    if event.get("agent_id") or event.get("agent_type"):
        return
    prompt = event.get("prompt")
    if _requests_hook_opt_out(prompt):
        return
    path = _state_path(event)
    if isinstance(prompt, str):
        _write_state(
            path,
            {
                "schema_version": 1,
                "phase": "awaiting_spawn",
                "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
            },
        )
    _additional_context("UserPromptSubmit", CODEX_OUTLINE_ROUTE)


def _record_spawn(event: dict[str, Any], state: dict[str, Any], path: Path) -> None:
    tool_input = event.get("tool_input")
    response = _json_object(event.get("tool_response"))
    if not isinstance(tool_input, dict) or not response:
        return
    message = tool_input.get("message")
    agent_id = response.get("agent_id")
    if not isinstance(message, str) or not message.startswith(OUTLINE_MARKER):
        return
    if not isinstance(agent_id, str) or not agent_id:
        return
    state.update({"phase": "awaiting_outline", "agent_id": agent_id})
    _write_state(path, state)


def _record_outline(event: dict[str, Any], state: dict[str, Any], path: Path) -> None:
    agent_id = state.get("agent_id")
    tool_input = event.get("tool_input")
    response = _json_object(event.get("tool_response"))
    if not isinstance(agent_id, str) or not isinstance(tool_input, dict) or not response:
        return
    targets = tool_input.get("targets")
    if not isinstance(targets, list) or agent_id not in targets:
        return
    status = response.get("status")
    record = status.get(agent_id) if isinstance(status, dict) else None
    outline = record.get("completed") if isinstance(record, dict) else None
    if not isinstance(outline, str) or not outline.strip():
        return
    state.update(
        {
            "phase": "outline_complete",
            "outline_sha256": hashlib.sha256(outline.encode("utf-8")).hexdigest(),
        }
    )
    _write_state(path, state)
    _additional_context("PostToolUse", CODEX_OUTLINE_FREEZE)


def _post_tool(event: dict[str, Any]) -> None:
    path = _state_path(event)
    state = _read_state(path)
    if path is None or state is None:
        return
    tool_name = event.get("tool_name")
    if tool_name == "spawn_agent":
        _record_spawn(event, state, path)
    elif tool_name == "multi_agent_v1wait_agent":
        _record_outline(event, state, path)


def _stop(event: dict[str, Any]) -> None:
    path = _state_path(event)
    state = _read_state(path)
    if path is None or state is None:
        return
    if event.get("stop_hook_active") is True:
        state["phase"] = "complete"
        _write_state(path, state)
        return
    if state.get("phase") != "outline_complete":
        return
    state["phase"] = "repair_requested"
    _write_state(path, state)
    print(json.dumps({"decision": "block", "reason": CODEX_OUTLINE_REPAIR}, ensure_ascii=False))


def handle(event: dict[str, Any]) -> None:
    event_name = event.get("hook_event_name")
    if event_name == "UserPromptSubmit":
        _start(event)
    elif event_name == "PostToolUse":
        _post_tool(event)
    elif event_name == "Stop":
        _stop(event)


def main() -> int:
    try:
        value = json.load(sys.stdin)
        if isinstance(value, dict):
            handle(value)
    except (json.JSONDecodeError, OSError, TypeError, ValueError):
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
