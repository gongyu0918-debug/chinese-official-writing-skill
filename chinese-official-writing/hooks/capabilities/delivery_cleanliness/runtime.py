#!/usr/bin/env python3
"""Bounded final-output cleanup for the optional Hook.

The capability asks for one cleanup pass after a complete draft exists.  It
accepts only deletion-only candidates and then requires a hash-bound semantic
verdict over every removed span.  Clean drafts and every uncertain or failed
transition fall back to the byte-identical original draft.
"""

from __future__ import annotations

from difflib import SequenceMatcher
import hashlib
import json
from typing import Any, Final


CAPABILITY_NAME: Final = "delivery_cleanliness"
SCHEMA_VERSION: Final = 1
MAX_FINAL_ECHO_ATTEMPTS: Final = 1
MIN_CANDIDATE_RETENTION_RATIO: Final = 0.35
PHASE_REVISION: Final = "delivery_cleanliness_awaiting_revision"
PHASE_VERDICT: Final = "delivery_cleanliness_awaiting_verdict"
PHASE_OUTPUT: Final = "delivery_cleanliness_awaiting_output"
PHASE_COMPLETE: Final = "delivery_cleanliness_complete"
PHASE_FAILED: Final = "delivery_cleanliness_technical_failure"
ALLOWED_DELETION_CATEGORIES: Final = {
    "unrequested_wrapper",
    "process_narration",
    "protocol_metadata",
    "format_wrapper",
}


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _block(message: str) -> dict[str, Any]:
    return {"decision": "block", "reason": message}


def _allow() -> dict[str, Any]:
    return {"continue": True}


def _revision_instruction(request: str, original: str) -> str:
    return (
        "请做一次交付洁净度整理，只输出可直接交付的完整终稿。只删除用户没有要求的过程说明、"
        "工具或权限状态、协议 JSON、代码围栏和纯包装性标题标记；正文中的文字、顺序、标点、数字、"
        "状态和换行必须原样保留。用户明确要求 Markdown、JSON 或解释过程时必须保留相应格式与内容。"
        "若没有可安全删除的包装，逐字返回 D0；不得改写、概括、补充或重排正文。\n"
        "【原请求】\n" + request + "\n【D0】\n" + original
    )


def _deletion_items(original: str, candidate: str) -> tuple[list[dict[str, Any]], str | None]:
    items: list[dict[str, Any]] = []
    matcher = SequenceMatcher(a=original, b=candidate, autojunk=False)
    for index, opcode in enumerate(matcher.get_opcodes(), start=1):
        operation, d0_start, d0_end, d1_start, d1_end = opcode
        if operation == "equal":
            continue
        if operation != "delete" or d1_start != d1_end:
            return [], "delivery_cleanliness_not_deletion_only"
        deleted = original[d0_start:d0_end]
        items.append(
            {
                "id": f"D{index:03d}",
                "start": d0_start,
                "end": d0_end,
                "text": deleted,
                "sha256": _sha256_text(deleted),
            }
        )
    if not items:
        return [], "delivery_cleanliness_no_deletion"
    if len(candidate) / max(1, len(original)) < MIN_CANDIDATE_RETENTION_RATIO:
        return [], "delivery_cleanliness_excessive_deletion"
    return items, None


def _verdict_instruction(
    request: str,
    original: str,
    candidate: str,
    deletions: list[dict[str, Any]],
) -> str:
    skeleton = {
        "schema_version": SCHEMA_VERSION,
        "request_sha256": _sha256_text(request),
        "d0_sha256": _sha256_text(original),
        "d1_sha256": _sha256_text(candidate),
        "verdict": "PASS or FAIL",
        "checks": {
            "only_unrequested_non_body_removed": False,
            "body_facts_states_and_order_preserved": False,
            "requested_format_preserved": False,
            "candidate_directly_usable": False,
        },
        "deletions": [{**item, "category": "unrequested_wrapper"} for item in deletions],
    }
    return (
        "只读核验 D1 相对 D0 的全部删除，并只输出一个 JSON 对象。冻结删除项须逐 id 原样回填。"
        "每项只能分类为 unrequested_wrapper、process_narration、protocol_metadata 或 format_wrapper。"
        "只有用户未要求、且不属于正文事实、状态、结构或明确格式的包装才能 PASS；删除任何正文、"
        "用户要求的 Markdown/JSON/说明、标题正文、数字、状态、段落或有用上下文都必须 FAIL。"
        "D1 不得包含任何新增、改写或重排；不确定即 FAIL。\n"
        + json.dumps(skeleton, ensure_ascii=False)
        + "\n【原请求】\n" + request
        + "\n【D0】\n" + original
        + "\n【D1】\n" + candidate
        + "\n【冻结删除项】\n" + json.dumps(deletions, ensure_ascii=False)
    )


def _parse_json(value: Any) -> dict[str, Any] | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = json.loads(value.strip())
    except json.JSONDecodeError:
        return None
    return parsed if isinstance(parsed, dict) else None


def _verdict_passes(
    value: dict[str, Any] | None,
    request: str,
    original: str,
    candidate: str,
    deletions: list[dict[str, Any]],
) -> bool:
    if not isinstance(value, dict) or value.get("schema_version") != SCHEMA_VERSION:
        return False
    if value.get("request_sha256") != _sha256_text(request):
        return False
    if value.get("d0_sha256") != _sha256_text(original):
        return False
    if value.get("d1_sha256") != _sha256_text(candidate):
        return False
    checks = value.get("checks")
    expected_checks = {
        "only_unrequested_non_body_removed",
        "body_facts_states_and_order_preserved",
        "requested_format_preserved",
        "candidate_directly_usable",
    }
    if (
        value.get("verdict") != "PASS"
        or not isinstance(checks, dict)
        or set(checks) != expected_checks
        or not all(checks.get(key) is True for key in expected_checks)
    ):
        return False
    received = value.get("deletions")
    if not isinstance(received, list) or len(received) != len(deletions):
        return False
    expected = {
        (item["id"], item["start"], item["end"], item["text"], item["sha256"])
        for item in deletions
    }
    actual = {
        (
            item.get("id"),
            item.get("start"),
            item.get("end"),
            item.get("text"),
            item.get("sha256"),
        )
        for item in received
        if isinstance(item, dict) and item.get("category") in ALLOWED_DELETION_CATEGORIES
    }
    return actual == expected


def _select(record: dict[str, Any], selection: str, reason: str) -> dict[str, Any]:
    state = record["delivery_cleanliness"]
    output = state.get("candidate") if selection == "D1" else state["original"]
    if not isinstance(output, str):
        output = state["original"]
        selection = "D0"
    state["audit"] = {
        "schema_version": SCHEMA_VERSION,
        "capability": CAPABILITY_NAME,
        "original_sha256": _sha256_text(state["original"]),
        "candidate_sha256": _sha256_text(state.get("candidate", "")) if state.get("candidate") else None,
        "selection": selection,
        "reason": reason,
        "delivery_sha256": _sha256_text(output),
        "delivery_verified": False,
    }
    state["phase"] = PHASE_OUTPUT
    record["delivery_cleanliness_selected_output"] = output
    record["delivery_cleanliness_selected_sha256"] = _sha256_text(output)
    return _block("交付洁净度整理已完成。请逐字输出下列已选终稿，不要调用工具、不要加说明：\n" + output)


def start(event: dict[str, Any], record: dict[str, Any]) -> dict[str, Any] | None:
    request = record.get("request")
    draft = event.get("last_assistant_message")
    if not isinstance(request, str) or not isinstance(draft, str) or not draft.strip():
        return None
    record["delivery_cleanliness"] = {
        "schema_version": SCHEMA_VERSION,
        "capability": CAPABILITY_NAME,
        "phase": PHASE_REVISION,
        "original": draft,
    }
    return _block(_revision_instruction(request, draft))


def advance(event: dict[str, Any], record: dict[str, Any]) -> dict[str, Any]:
    state = record["delivery_cleanliness"]
    request = record.get("request")
    if not isinstance(request, str):
        return _select(record, "D0", "request_missing")
    phase = state.get("phase")
    if phase == PHASE_REVISION:
        candidate = event.get("last_assistant_message")
        if not isinstance(candidate, str) or not candidate:
            return _select(record, "D0", "revision_missing")
        if candidate == state["original"]:
            return _select(record, "D0", "clean_or_requested_format_preserved")
        state["candidate"] = candidate
        deletions, reason = _deletion_items(state["original"], candidate)
        if reason:
            return _select(record, "D0", reason)
        state["deletions"] = deletions
        state["phase"] = PHASE_VERDICT
        return _block(
            _verdict_instruction(request, state["original"], candidate, deletions)
        )
    if phase == PHASE_VERDICT:
        candidate = state.get("candidate")
        verdict = _parse_json(event.get("last_assistant_message"))
        if isinstance(candidate, str) and _verdict_passes(
            verdict,
            request,
            state["original"],
            candidate,
            state.get("deletions", []),
        ):
            return _select(record, "D1", "semantic_pass")
        return _select(record, "D0", "semantic_rejected")
    if phase == PHASE_OUTPUT:
        delivered = event.get("last_assistant_message")
        if isinstance(delivered, str) and _sha256_text(delivered) == record.get(
            "delivery_cleanliness_selected_sha256"
        ):
            state["phase"] = PHASE_COMPLETE
            state["audit"]["delivery_verified"] = True
            record.pop("delivery_cleanliness_selected_output", None)
            return _allow()
        attempts = int(state.get("output_reprompts") or 0)
        if state.get("audit", {}).get("selection") == "D1":
            state["audit"].update(
                {
                    "selection": "D0",
                    "reason": "d1_echo_mismatch_fallback_d0",
                    "delivery_sha256": _sha256_text(state["original"]),
                }
            )
            state["output_reprompts"] = 1
            record["delivery_cleanliness_selected_output"] = state["original"]
            record["delivery_cleanliness_selected_sha256"] = _sha256_text(state["original"])
            return _block(
                "洁净稿回显不一致，已回退原始稿。请逐字输出下列 D0，不要调用工具、不要加说明：\n"
                + state["original"]
            )
        if attempts < MAX_FINAL_ECHO_ATTEMPTS:
            state["output_reprompts"] = attempts + 1
            return _block(
                "原始稿回显不一致。请逐字输出下列 D0，不要调用工具、不要加说明：\n"
                + state["original"]
            )
        state["phase"] = PHASE_FAILED
        state["audit"].update(
            {"delivery_verified": False, "reason": "d0_echo_mismatch_technical_failure"}
        )
        record.pop("delivery_cleanliness_selected_output", None)
        return _allow()
    return _allow()
