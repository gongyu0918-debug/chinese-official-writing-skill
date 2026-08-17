#!/usr/bin/env python3
"""Bounded over-length compression for the optional delivery Hook."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
from pathlib import Path
import re
import sys
from typing import Any, Final


CAPABILITY_NAME: Final = "over_length"
SCHEMA_VERSION: Final = 1
OVER_TOLERANCE_RATIO: Final = 0.10
MAX_COMPRESSION_ATTEMPTS: Final = 2
MAX_FINAL_ECHO_ATTEMPTS: Final = 1
TARGET_HEADROOM_RATIO: Final = 0.96
MIN_TARGET_HEADROOM: Final = 8
PHASE_OBSERVATION: Final = "over_length_awaiting_repetition_observation"
PHASE_REVISION: Final = "over_length_awaiting_revision"
PHASE_VERDICT: Final = "over_length_awaiting_verdict"
PHASE_OUTPUT: Final = "over_length_awaiting_output"
PHASE_COMPLETE: Final = "over_length_complete"
PHASE_FAILED: Final = "over_length_technical_failure"

SCOPE_MAX_RE: Final = re.compile(
    r"(?P<scope>正文|成稿|回复|输出|全文|终稿)[^，,。；;\n]{0,28}?[，,：:]?\s*"
    r"(?:不超过|不多于|至多|控制在)\s*(?P<maximum>\d{2,5})\s*字"
)
SCOPE_RANGE_RE: Final = re.compile(
    r"(?P<scope>正文|成稿|回复|输出|全文|终稿)[^，,。；;\n]{0,28}?[，,：:]?\s*"
    r"(?P<minimum>\d{2,5})\s*(?:—|－|-|~|至|到)\s*(?P<maximum>\d{2,5})\s*字"
)
ACTION_MAX_RE: Final = re.compile(
    r"(?:起草|撰写|拟写|写一(?:篇|份)|压缩|精简)[^，,。；;\n]{0,20}?[，,：:]?\s*"
    r"(?:不超过|不多于|至多|控制在)\s*(?P<maximum>\d{2,5})\s*字"
)
ACTION_RANGE_RE: Final = re.compile(
    r"(?:起草|撰写|拟写|写一(?:篇|份)|压缩|精简)[^，,。；;\n]{0,20}?[，,：:]?\s*"
    r"(?P<minimum>\d{2,5})\s*(?:—|－|-|~|至|到)\s*(?P<maximum>\d{2,5})\s*字"
)
MATERIAL_CONTEXT_RE: Final = re.compile(
    r"(?:材料|附件|引语|原文|背景|摘录|写明|载明|提到|如下|制度|合同|条款).{0,18}$"
)
APPROXIMATE_LENGTH_RE: Final = re.compile(r"(?:约|左右)")
NUMBER_RE: Final = re.compile(r"\d+(?:\.\d+)?")
CJK_QUANTITY_RE: Final = re.compile(
    r"[一二三四五六七八九十百千万两]+(?:台|件|项|次|个月|年|天|份|人|套|批|元)"
)
QUOTE_RE: Final = re.compile(r"[\"“][^\"”\n]{1,160}[\"”]")
MARKDOWN_HEADING_RE: Final = re.compile(r"^\s*#{1,6}\s+\S+")
NUMBERED_HEADING_RE: Final = re.compile(
    r"^\s*(?:第[一二三四五六七八九十百]+[章节]|[一二三四五六七八九十]+、|\d+[.、])"
)
CONTRACT_PATH: Final = (
    Path(__file__).resolve().parents[1] / "protective_expansion" / "contract.py"
)


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _body_text(text: str) -> str:
    lines = [line for line in text.splitlines() if line.strip()]
    body: list[str] = []
    for index, line in enumerate(lines):
        stripped = line.strip()
        if MARKDOWN_HEADING_RE.match(stripped) or _is_numbered_heading(stripped):
            continue
        if index == 0 and len(stripped) <= 30 and not re.search(r"[。！？!?]", stripped):
            continue
        body.append(stripped)
    return "\n".join(body)


def _is_numbered_heading(value: str) -> bool:
    return bool(
        NUMBERED_HEADING_RE.match(value)
        and len(value) <= 40
        and not re.search(r"[。；;！？!?]", value)
    )


def count_text(text: str, scope: str) -> int:
    source = _body_text(text) if scope == "body" else text
    return len(re.sub(r"\s+", "", source))


def _block(message: str) -> dict[str, Any]:
    return {"decision": "block", "reason": message}


def _allow() -> dict[str, Any]:
    return {"continue": True}


def _authoritative_match(
    request: str, match: re.Match[str], *, output_action: bool
) -> bool:
    prefix = request[max(0, match.start() - 24) : match.start()]
    material_context = MATERIAL_CONTEXT_RE.search(prefix)
    last_output_signal = max(
        (
            prefix.rfind(token)
            for token in ("起草", "撰写", "拟写", "写一", "压缩", "精简", "只")
        ),
        default=-1,
    )
    return (
        output_action
        or material_context is None
        or last_output_signal > material_context.start()
    ) and not APPROXIMATE_LENGTH_RE.search(prefix + match.group(0))


def parse_spec(request: str) -> dict[str, Any] | None:
    """Return only an output-scoped hard upper bound or range."""

    ranges: list[re.Match[str]] = []
    for pattern, output_action in ((SCOPE_RANGE_RE, False), (ACTION_RANGE_RE, True)):
        ranges.extend(
            match
            for match in pattern.finditer(request)
            if _authoritative_match(request, match, output_action=output_action)
        )
    if ranges:
        match = ranges[-1]
        minimum, maximum = int(match.group("minimum")), int(match.group("maximum"))
        if minimum <= 0 or minimum > maximum:
            return None
        scope = match.groupdict().get("scope")
        return {
            "minimum": minimum,
            "maximum": maximum,
            "scope": "body" if scope == "正文" or "正文" in match.group(0) else "full",
        }
    maxima: list[re.Match[str]] = []
    for pattern, output_action in ((SCOPE_MAX_RE, False), (ACTION_MAX_RE, True)):
        maxima.extend(
            match
            for match in pattern.finditer(request)
            if _authoritative_match(request, match, output_action=output_action)
        )
    if not maxima:
        return None
    match = maxima[-1]
    scope = match.groupdict().get("scope")
    return {
        "minimum": 0,
        "maximum": int(match.group("maximum")),
        "scope": "body" if scope == "正文" or "正文" in match.group(0) else "full",
    }


def _load_repetition_contract() -> Any | None:
    try:
        spec = importlib.util.spec_from_file_location(
            "cow_over_length_repetition_contract", CONTRACT_PATH
        )
        if spec is None or spec.loader is None:
            return None
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
    except Exception:
        return None
    return module


def _extract_json_object(value: Any) -> dict[str, Any] | None:
    if not isinstance(value, str):
        return None
    text = value.strip()
    if text.startswith("```") and text.endswith("```"):
        lines = text.splitlines()
        if len(lines) >= 3:
            text = "\n".join(lines[1:-1]).strip()
    start = text.find("{")
    if start < 0:
        return None
    try:
        payload, end = json.JSONDecoder().raw_decode(text[start:])
    except json.JSONDecodeError:
        return None
    if text[start + end :].strip() or not isinstance(payload, dict):
        return None
    return payload


def _headings(text: str) -> set[str]:
    headings: set[str] = set()
    for index, line in enumerate(text.splitlines()):
        stripped = line.strip()
        if (
            MARKDOWN_HEADING_RE.match(stripped)
            or _is_numbered_heading(stripped)
            or (
                index == 0
                and 1 <= len(stripped) <= 40
                and not re.search(r"[。！？!?]", stripped)
            )
        ):
            headings.add(stripped)
    return headings


def mechanical_reason(
    original: str, candidate: str, spec: dict[str, Any]
) -> str | None:
    if not candidate.strip():
        return "over_length_empty_candidate"
    if set(NUMBER_RE.findall(candidate)) != set(NUMBER_RE.findall(original)):
        return "over_length_number_added_dropped_or_changed"
    if set(CJK_QUANTITY_RE.findall(candidate)) != set(CJK_QUANTITY_RE.findall(original)):
        return "over_length_quantity_added_dropped_or_changed"
    if not set(QUOTE_RE.findall(original)).issubset(set(QUOTE_RE.findall(candidate))):
        return "over_length_quote_dropped_or_changed"
    if not _headings(original).issubset(_headings(candidate)):
        return "over_length_outline_heading_dropped"
    candidate_length = count_text(candidate, spec["scope"])
    minimum = int(spec.get("minimum") or 0)
    if minimum and candidate_length < minimum:
        return "over_length_candidate_below_minimum"
    if candidate_length > int(spec["maximum"]):
        return "over_length_candidate_above_maximum"
    return None


def _target_text(spec: dict[str, Any]) -> str:
    minimum, maximum = int(spec.get("minimum") or 0), int(spec["maximum"])
    target_maximum = max(minimum, min(maximum, math.floor(maximum * TARGET_HEADROOM_RATIO)))
    if maximum - target_maximum < MIN_TARGET_HEADROOM:
        target_maximum = maximum
    return (
        f"{minimum}—{target_maximum}字"
        if minimum
        else f"不超过{target_maximum}字"
    )


def _revision_instruction(
    request: str,
    original: str,
    working: str,
    spec: dict[str, Any],
    attempt: int,
) -> str:
    follow_up = "这是最后一次压缩。" if attempt == MAX_COMPRESSION_ATTEMPTS else ""
    return (
        "上一稿超过用户明确上限10%以上。请只输出压缩后的完整终稿，不要解释过程。"
        f"目标为{_target_text(spec)}。{follow_up}"
        "先合并重复说明，再删去不承载事实的衔接、客套和同义收束；仍偏长时，在保留正文脉络的前提下重写长句。"
        "每个段落或相邻句组只写一个主要事项；同一原因、理由、目的、事实、动作和状态只在最贴近的位置写一次。"
        "职责分工已经完整写明后，结尾不得再以‘继续做好、持续推进、有序推进’逐项复述同一组职责；"
        "办理中状态确需保留时，只写状态和必要承接，不重新展开前文责任清单。"
        "必须保留全部事实、数字、日期、金额、引语、未决状态、责任主体及其关系、标题和必要层级；"
        "不得新增具体人事、程序、承诺、结论或完成状态，也不得把不同主体和事项合并。"
        "事实不足以安全达标时，逐字返回原始稿。\n"
        "【原请求】\n" + request
        + "\n【原始完整稿】\n" + original
        + "\n【本轮待压缩稿】\n" + working
    )


def _verdict_instruction(
    request: str, original: str, candidate: str, spec: dict[str, Any]
) -> str:
    skeleton = {
        "schema_version": SCHEMA_VERSION,
        "request_sha256": _sha256_text(request),
        "original_sha256": _sha256_text(original),
        "candidate_sha256": _sha256_text(candidate),
        "verdict": "PASS or FAIL",
        "checks": {
            "no_new_specific_fact": False,
            "facts_and_states_complete": False,
            "responsibilities_and_relations_preserved": False,
            "genre_structure_preserved": False,
            "natural_and_non_repetitive": False,
        },
        "reason": "简述判定依据",
    }
    return (
        "只读核验压缩稿相对原始稿的变化，只输出一个JSON对象。"
        "删除零增量复述、客套和胶水可以通过；句式、段落合并可以变化。"
        "遗漏独立事实、状态、主体、职责、关系或必需结构，改变未决强度，或者新增具体内容，均须FAIL。"
        "还要跨段检查同义重复：前文已经完整列出职责、原因、理由或目的，结尾只换成‘继续做好、持续推进、"
        "有序推进’再次列举而没有新状态、新要求或新关系时，natural_and_non_repetitive必须为false并FAIL。"
        "不要因为更短而降低标准，也不要把正常精简误判为事实缺失；不确定即FAIL。\n"
        + json.dumps(skeleton, ensure_ascii=False)
        + "\n【原请求】\n" + request
        + "\n【原始稿】\n" + original
        + "\n【压缩稿】\n" + candidate
        + "\n【篇幅规格】\n" + json.dumps(spec, ensure_ascii=False)
    )


def _verdict_passes(
    value: dict[str, Any] | None,
    request: str,
    original: str,
    candidate: str,
) -> bool:
    expected_checks = {
        "no_new_specific_fact",
        "facts_and_states_complete",
        "responsibilities_and_relations_preserved",
        "genre_structure_preserved",
        "natural_and_non_repetitive",
    }
    if not isinstance(value, dict):
        return False
    checks = value.get("checks")
    return bool(
        value.get("schema_version") == SCHEMA_VERSION
        and value.get("request_sha256") == _sha256_text(request)
        and value.get("original_sha256") == _sha256_text(original)
        and value.get("candidate_sha256") == _sha256_text(candidate)
        and value.get("verdict") == "PASS"
        and isinstance(checks, dict)
        and set(checks) == expected_checks
        and all(checks.get(key) is True for key in expected_checks)
    )


def _select(record: dict[str, Any], selection: str, reason: str) -> dict[str, Any]:
    state = record["over_length"]
    output = state.get("candidate") if selection == "D1" else state["original"]
    if not isinstance(output, str):
        output, selection = state["original"], "D0"
    state["audit"] = {
        "schema_version": SCHEMA_VERSION,
        "trigger": "over",
        "original_sha256": _sha256_text(state["original"]),
        "candidate_sha256": (
            _sha256_text(state.get("candidate", "")) if state.get("candidate") else None
        ),
        "spec": state.get("spec"),
        "original_count": state.get("original_count"),
        "candidate_count": state.get("candidate_count"),
        "compression_attempts": state.get("compression_attempts", 0),
        "repetition_selection": state.get("repetition_selection"),
        "selection": selection,
        "reason": reason,
        "delivery_sha256": _sha256_text(output),
        "delivery_verified": False,
    }
    state["phase"] = PHASE_OUTPUT
    record["over_length_selected_output"] = output
    record["over_length_selected_sha256"] = _sha256_text(output)
    return _block(
        "篇幅收束已完成。请逐字输出下列已选终稿，不要调用工具、不要加说明：\n"
        + output
    )


def _begin_revision(record: dict[str, Any]) -> dict[str, Any]:
    state = record["over_length"]
    state["compression_attempts"] = int(state.get("compression_attempts") or 0) + 1
    state["phase"] = PHASE_REVISION
    return _block(
        _revision_instruction(
            str(record.get("request") or ""),
            state["original"],
            state["working"],
            state["spec"],
            state["compression_attempts"],
        )
    )


def start(event: dict[str, Any], record: dict[str, Any]) -> dict[str, Any] | None:
    request = record.get("request")
    draft = event.get("last_assistant_message")
    if not isinstance(request, str) or not isinstance(draft, str) or not draft.strip():
        return None
    spec = parse_spec(request)
    if spec is None:
        return None
    original_count = count_text(draft, spec["scope"])
    if original_count <= math.floor(spec["maximum"] * (1 + OVER_TOLERANCE_RATIO)):
        return None
    contract = _load_repetition_contract()
    if contract is None:
        return None
    packet = contract.build_packet(
        request,
        draft,
        "",
        authority_scope="request_only",
        capability="repetition_cleanup",
    )
    if packet.get("status") != "ready":
        return None
    record["over_length"] = {
        "schema_version": SCHEMA_VERSION,
        "capability": CAPABILITY_NAME,
        "phase": PHASE_OBSERVATION,
        "original": draft,
        "working": draft,
        "original_count": original_count,
        "spec": spec,
        "repetition_packet": packet,
        "compression_attempts": 0,
    }
    return _block(contract.observer_instruction(packet))


def _consume_observation(event: dict[str, Any], record: dict[str, Any]) -> dict[str, Any]:
    state = record["over_length"]
    contract = _load_repetition_contract()
    response = _extract_json_object(event.get("last_assistant_message"))
    if contract is None or response is None:
        return _select(record, "D0", "repetition_observation_unavailable")
    result = contract.apply_response(state["repetition_packet"], response)
    if result.get("status") == "fallback":
        return _select(record, "D0", str(result.get("reason") or "repetition_fallback"))
    working = result.get("output")
    if not isinstance(working, str) or not working.strip():
        return _select(record, "D0", "repetition_output_missing")
    state["repetition_selection"] = result.get("selection")
    state["working"] = working
    state["repetition_count"] = count_text(working, state["spec"]["scope"])
    reason = mechanical_reason(state["original"], working, state["spec"])
    if reason is None:
        state["candidate"] = working
        state["candidate_count"] = state["repetition_count"]
        return _select(record, "D1", "repetition_cleanup_met_upper_bound")
    if reason == "over_length_candidate_below_minimum":
        state["working"] = state["original"]
    elif reason != "over_length_candidate_above_maximum":
        return _select(record, "D0", reason)
    return _begin_revision(record)


def _consume_revision(event: dict[str, Any], record: dict[str, Any]) -> dict[str, Any]:
    state = record["over_length"]
    candidate = event.get("last_assistant_message")
    if not isinstance(candidate, str) or not candidate.strip():
        return _select(record, "D0", "revision_missing")
    state["candidate"] = candidate
    state["candidate_count"] = count_text(candidate, state["spec"]["scope"])
    reason = mechanical_reason(state["original"], candidate, state["spec"])
    if (
        reason == "over_length_candidate_above_maximum"
        and int(state.get("compression_attempts") or 0) < MAX_COMPRESSION_ATTEMPTS
    ):
        state["working"] = candidate
        return _begin_revision(record)
    if reason:
        return _select(record, "D0", reason)
    state["phase"] = PHASE_VERDICT
    return _block(
        _verdict_instruction(
            str(record.get("request") or ""),
            state["original"],
            candidate,
            state["spec"],
        )
    )


def _consume_verdict(event: dict[str, Any], record: dict[str, Any]) -> dict[str, Any]:
    state = record["over_length"]
    request = str(record.get("request") or "")
    verdict = _extract_json_object(event.get("last_assistant_message"))
    if _verdict_passes(verdict, request, state["original"], state.get("candidate", "")):
        return _select(record, "D1", "semantic_pass")
    return _select(record, "D0", "semantic_rejected")


def _verify_output(event: dict[str, Any], record: dict[str, Any]) -> dict[str, Any]:
    state = record["over_length"]
    delivered = event.get("last_assistant_message")
    if isinstance(delivered, str) and _sha256_text(delivered) == record.get(
        "over_length_selected_sha256"
    ):
        state["phase"] = PHASE_COMPLETE
        state["audit"]["delivery_verified"] = True
        record.pop("over_length_selected_output", None)
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
        record["over_length_selected_output"] = state["original"]
        record["over_length_selected_sha256"] = _sha256_text(state["original"])
        return _block(
            "压缩稿回显不一致，已回退原始稿。请逐字输出下列 D0，不要调用工具、不要加说明：\n"
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
    record.pop("over_length_selected_output", None)
    return _allow()


def advance(event: dict[str, Any], record: dict[str, Any]) -> dict[str, Any]:
    state = record["over_length"]
    phase = state.get("phase")
    if phase == PHASE_OBSERVATION:
        return _consume_observation(event, record)
    if phase == PHASE_REVISION:
        return _consume_revision(event, record)
    if phase == PHASE_VERDICT:
        return _consume_verdict(event, record)
    if phase == PHASE_OUTPUT:
        return _verify_output(event, record)
    return _allow()
