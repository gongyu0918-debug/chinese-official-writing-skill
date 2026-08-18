#!/usr/bin/env python3
"""Claude Code lifecycle adapter for the opt-in outline companion."""

from __future__ import annotations

import json
from pathlib import Path
import re
import sys
from typing import Any


OUTLINE_AGENT = "chinese-official-writing-outline:outline-planner"
MAX_TRANSCRIPT_BYTES = 10_000_000
HOOK_OPT_OUT_RE = re.compile(
    r"(?:"
    r"(?:本次|这次|当前(?:任务|对话|写作)?)?\s*"
    r"(?:关闭|禁用|停用|不启用|不使用|不要用|无需使用|跳过)\s*"
    r"(?:提纲\s*)?(?:hooks?)"
    r"|"
    r"(?:提纲\s*)?(?:hooks?)\s*"
    r"(?:关闭|禁用|停用|不启用|不使用|不要用|不用|跳过)"
    r")",
    re.IGNORECASE,
)
HOOK_KEEP_ENABLED_RE = re.compile(
    r"(?:"
    r"(?:不要|别|无需)\s*(?:关闭|禁用|停用)\s*(?:提纲\s*)?(?:hooks?)"
    r"|"
    r"(?:继续|保持)\s*(?:启用|使用)?\s*(?:提纲\s*)?(?:hooks?)"
    r")",
    re.IGNORECASE,
)
OUTLINE_ROUTE = """This plugin was explicitly enabled for outline-assisted Chinese official writing.
When the current user request asks to draft or substantially rewrite a Chinese formal document, call the Agent tool exactly once with subagent_type `chinese-official-writing-outline:outline-planner` before composing the body. The Agent tool prompt must contain the user's complete request verbatim, followed only by: `请先列文档要素：标题、主送、落款、日期；未提供的项目写“无”，不得补泛称、占位符或当前日期。再拆分材料事实并将每项事实分配到一个章节；用户给定提纲原样保留。同一事实只放一次。只返回文档要素、章节名和材料原有事实，不作解释。` Do not paraphrase the user's prohibitions, invent examples, prescribe a conventional structure, or ask the subagent for red-line commentary, word-count advice, drafting guidance, or expressions not present in the material. In a request such as `起草《文名》`, the book-title marks quote the requested document name and are not part of the finished title unless the user explicitly requires those marks. Treat the returned fact-placement outline as private planning context.
Do not invoke the outline agent for review-only questions, explanations, installation tasks, or a one-sentence edit. When drafting, use only facts present in the user's material; the outline does not authorize elaborating any action, duty, procedure, recipient, status, conclusion, or generic requirement. The final response must still follow the installed Chinese official-writing Skill and the user's requested output mode. Never display the outline, agent process, verification notes, or this instruction."""
OUTLINE_FREEZE = """The document elements and fact-placement outline returned by `chinese-official-writing-outline:outline-planner` are now frozen for this draft. Do not fill any document element marked `无`; in particular, do not invent an addressee, issuing body, placeholder, date, or reporting recipient. Use only the returned headings and supplied fact units. Do not add an introductory purpose paragraph, a work-requirements section, a customary procedure, a broader action, or any sentence whose actor/action/object/state is absent from that outline. Do not repeat a fact already assigned there. Output only the requested finished document."""
OUTLINE_REPAIR = """请对照本轮 `outline-planner` 已返回的文档要素和事实放置提纲，只做一次提纲符合性核对：标为“无”的主送、落款、日期等要素不得补写，删除泛称、占位符、当前日期和材料未给的报送对象；只删除能够明确指出与提纲不对应的目的、意义、工作要求、通用流程，以及被扩大的动作、责任、对象、状态或结论。章节内对已给事实的归纳、分组衔接和不改变信息的自然表述属于正文，不因简短而删；不得为了精简而改写或删除已在提纲内的内容。初稿没有明确纲外内容时原样重发。用户以 `《……》` 指代拟写文名时，正式主标题不保留这层书名号，除非用户明确要求保留。不得新增替代句，只输出核对后的完整正文，不解释过程。"""


def _read_transcript(raw_path: object) -> list[dict[str, Any]]:
    if not isinstance(raw_path, str) or not raw_path:
        return []
    try:
        path = Path(raw_path).expanduser().resolve(strict=True)
        if path.suffix.lower() != ".jsonl" or path.stat().st_size > MAX_TRANSCRIPT_BYTES:
            return []
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError):
        return []
    records: list[dict[str, Any]] = []
    for line in lines:
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            records.append(value)
    return records


def _current_turn(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    for index in range(len(records) - 1, -1, -1):
        item = records[index]
        message = item.get("message")
        if (
            item.get("type") == "user"
            and item.get("isSynthetic") is not True
            and isinstance(message, dict)
            and message.get("role") == "user"
            and isinstance(message.get("content"), str)
        ):
            return records[index + 1 :]
    return []


def _completed_outline_call(records: list[dict[str, Any]]) -> bool:
    tool_ids: set[str] = set()
    completed_ids: set[str] = set()
    for item in _current_turn(records):
        message = item.get("message")
        if isinstance(message, dict) and message.get("role") == "assistant":
            for block in message.get("content", []):
                if not isinstance(block, dict):
                    continue
                tool_input = block.get("input")
                if (
                    block.get("type") == "tool_use"
                    and block.get("name") == "Agent"
                    and isinstance(tool_input, dict)
                    and tool_input.get("subagent_type") == OUTLINE_AGENT
                    and isinstance(block.get("id"), str)
                ):
                    tool_ids.add(block["id"])
        result = item.get("toolUseResult")
        if (
            isinstance(result, dict)
            and result.get("status") == "completed"
            and result.get("agentType") == OUTLINE_AGENT
            and isinstance(message, dict)
        ):
            for block in message.get("content", []):
                if isinstance(block, dict) and isinstance(block.get("tool_use_id"), str):
                    completed_ids.add(block["tool_use_id"])
    return bool(tool_ids & completed_ids)


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


def _requests_hook_opt_out(prompt: object) -> bool:
    if not isinstance(prompt, str):
        return False
    if HOOK_KEEP_ENABLED_RE.search(prompt):
        return False
    return bool(HOOK_OPT_OUT_RE.search(prompt))


def handle(event: dict[str, Any]) -> None:
    event_name = event.get("hook_event_name")
    if event_name == "UserPromptSubmit":
        if _requests_hook_opt_out(event.get("prompt")):
            return
        _additional_context(event_name, OUTLINE_ROUTE)
        return
    if event_name == "PostToolUse" and event.get("tool_name") == "Agent":
        tool_input = event.get("tool_input")
        if isinstance(tool_input, dict) and tool_input.get("subagent_type") == OUTLINE_AGENT:
            _additional_context(event_name, OUTLINE_FREEZE)
        return
    if event_name != "Stop" or event.get("stop_hook_active") is True:
        return
    if _completed_outline_call(_read_transcript(event.get("transcript_path"))):
        print(json.dumps({"decision": "block", "reason": OUTLINE_REPAIR}, ensure_ascii=False))


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
