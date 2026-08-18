#!/usr/bin/env python3
"""Bounded under-length revision capability for the optional Hook.

The capability starts only for an explicit output lower bound or range when
the completed draft is more than ten percent short.  It permits one revision,
one semantic delta verdict, and a hash-bound final echo.  Any uncertainty or
runtime failure selects the byte-identical original draft.
"""

from __future__ import annotations

from difflib import SequenceMatcher
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import re
import sys
from typing import Any, Final


CAPABILITY_NAME: Final = "under_length"
SCHEMA_VERSION: Final = 1
UNDER_TOLERANCE_RATIO: Final = 0.10
MAX_FINAL_ECHO_ATTEMPTS: Final = 1
PREFERRED_MINIMUM_HEADROOM: Final = 10
PREFERRED_MAXIMUM_HEADROOM: Final = 30
PHASE_REVISION: Final = "under_length_awaiting_revision"
PHASE_VERDICT: Final = "under_length_awaiting_verdict"
PHASE_OUTPUT: Final = "under_length_awaiting_output"
PHASE_COMPLETE: Final = "under_length_complete"
PHASE_FAILED: Final = "under_length_technical_failure"

SCOPE_MIN_RE: Final = re.compile(
    r"(?P<scope>正文|成稿|回复|输出|全文|终稿)[^，,。；;\n]{0,28}?[，,：:]?\s*"
    r"(?:不少于|至少|不低于|不小于)\s*(?P<minimum>\d{2,5})\s*字"
)
SCOPE_RANGE_RE: Final = re.compile(
    r"(?P<scope>正文|成稿|回复|输出|全文|终稿)[^，,。；;\n]{0,28}?[，,：:]?\s*"
    r"(?P<minimum>\d{2,5})\s*(?:—|－|-|~|至|到)\s*(?P<maximum>\d{2,5})\s*字"
)
ACTION_MIN_RE: Final = re.compile(
    r"(?:起草|撰写|拟写|写一(?:篇|份))[^，,。；;\n]{0,20}?[，,：:]?\s*"
    r"(?:不少于|至少|不低于|不小于)\s*(?P<minimum>\d{2,5})\s*字"
)
ACTION_RANGE_RE: Final = re.compile(
    r"(?:起草|撰写|拟写|写一(?:篇|份))[^，,。；;\n]{0,20}?[，,：:]?\s*"
    r"(?P<minimum>\d{2,5})\s*(?:—|－|-|~|至|到)\s*(?P<maximum>\d{2,5})\s*字"
)
MATERIAL_CONTEXT_RE: Final = re.compile(
    r"(?:材料|附件|引语|原文|背景|摘录|写明|载明|提到|如下|制度|合同|条款|解释).{0,18}$"
)
APPROXIMATE_LENGTH_RE: Final = re.compile(r"(?:约|左右|控制在)")
SHORTFALL_PERMISSION_RE: Final = re.compile(
    r"(?:(?:材料|事实|信息)(?:不足|有限).{0,16}(?:宁可|可以|允许|可).{0,8}"
    r"(?:短于|低于|少于)(?:下限|字数|篇幅)|"
    r"(?:不必|无需|不要).{0,8}(?:强行|勉强)?(?:达到|凑到)(?:下限|字数|篇幅))"
)
EXPLICIT_TITLE_RE: Final = re.compile(
    r"(?:标题|题目)\s*(?:为|是|：|:)\s*[《\"]?([^》\"\n，。；;]+)"
)
EXPLICIT_FIELD_RE: Final = re.compile(
    r"(?:字段|栏目)\s*(?:为|包括|：|:)\s*([^。；;\n]+)"
)
STATUS_ANCHOR_RE: Final = re.compile(
    r"(?:在办|正在(?:核查|办理|推进|处理|调查|侦办|抢修|统计)|"
    r"尚未|未(?:完成|确定|实施|形成|办结)|拟(?:议|定|完善|优化|改进)|待(?:定|核)|"
    r"下一年度(?:拟|将))"
)
GENERAL_CONTINUATION_RE: Final = re.compile(
    r"(?:按计划推进|按既定安排(?:办理|推进)?|按工作计划(?:持续)?推进|"
    r"按规定程序(?:办理|推进)?|确保按期完成)"
)
UNSUPPORTED_ADDED_PROCESS_RE: Final = re.compile(
    r"(?:"
    r"提前(?:做好当日工作衔接|通知本部门联络员|了解会议地点)|"
    r"(?:遵守|维护)(?:会场|会议)秩序|保持(?:通讯|通信)畅通|"
    r"督促.{0,12}(?:参会|准备)|"
    r"(?:共同|专题)?研究提出.{0,12}(?:解决办法|解决方案|解决措施)|"
    r"推动.{0,12}(?:尽快|及时)(?:处理|解决)|"
    r"明确报送的(?:内容|时间|方式)|统筹做好会议.{0,8}准备|"
    r"逐项说明工作(?:已完成|正在推进)|"
    r"(?:书面材料|材料).{0,16}(?:条理清晰|内容完整|查阅使用|如实反映)"
    r")"
)
MARKDOWN_HEADING_RE: Final = re.compile(r"^\s*#{1,6}\s+")
NUMBERED_HEADING_RE: Final = re.compile(
    r"^\s*(?:[一二三四五六七八九十]+、|\d+[.、])\s*\S+$"
)
HARD_ANCHOR_PATH: Final = Path(__file__).resolve().parents[2] / "shared" / "hard_anchors.py"


def _load_hard_anchor_contract() -> Any | None:
    try:
        spec = importlib.util.spec_from_file_location(
            "cow_under_length_hard_anchors", HARD_ANCHOR_PATH
        )
        if spec is None or spec.loader is None:
            return None
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
    except Exception:
        return None
    return module


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _body_text(text: str) -> str:
    lines = [line for line in text.splitlines() if line.strip()]
    body: list[str] = []
    for index, line in enumerate(lines):
        stripped = line.strip()
        if MARKDOWN_HEADING_RE.match(stripped) or NUMBERED_HEADING_RE.match(stripped):
            continue
        if index == 0 and len(stripped) <= 30 and not re.search(r"[。！？!?]", stripped):
            continue
        body.append(stripped)
    return "\n".join(body)


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
        (prefix.rfind(token) for token in ("起草", "撰写", "拟写", "写一", "只")),
        default=-1,
    )
    return (
        (
            output_action
            or material_context is None
            or last_output_signal > material_context.start()
        )
        and not APPROXIMATE_LENGTH_RE.search(prefix + match.group(0))
    )


def parse_spec(request: str) -> dict[str, Any] | None:
    """Return only an output-scoped hard lower bound or range."""

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
    minima: list[re.Match[str]] = []
    for pattern, output_action in ((SCOPE_MIN_RE, False), (ACTION_MIN_RE, True)):
        minima.extend(
            match
            for match in pattern.finditer(request)
            if _authoritative_match(request, match, output_action=output_action)
        )
    if not minima:
        return None
    match = minima[-1]
    scope = match.groupdict().get("scope")
    return {
        "minimum": int(match.group("minimum")),
        "maximum": 0,
        "scope": "body" if scope == "正文" or "正文" in match.group(0) else "full",
    }


def _user_allows_shortfall(request: str) -> bool:
    return bool(SHORTFALL_PERMISSION_RE.search(request))


def _required_labels(request: str) -> set[str]:
    labels: set[str] = set()
    for pattern in (EXPLICIT_TITLE_RE, EXPLICIT_FIELD_RE):
        for match in pattern.finditer(request):
            labels.update(
                token.strip(" 《》\"“”")
                for token in re.split(r"[、,，/]", match.group(1))
                if token.strip(" 《》\"“”")
            )
    return labels


def _status_transition_reason(original: str, candidate: str) -> str | None:
    for before, after in (
        ("尚未确定", "已经确定"),
        ("正在核查", "核查完成"),
        ("正在调查", "调查完成"),
        ("正在侦办", "侦办完成"),
        ("正在抢修", "抢修完成"),
        ("拟", "已确定"),
    ):
        if before in original and before not in candidate and after in candidate:
            return "under_length_status_upgraded"
    return None


def mechanical_reason(
    original: str, candidate: str, spec: dict[str, Any], request: str
) -> str | None:
    candidate_length = count_text(candidate, spec["scope"])
    if candidate_length < spec["minimum"]:
        return "under_length_candidate_below_minimum"
    maximum = int(spec.get("maximum") or 0)
    if maximum and candidate_length > maximum:
        return "under_length_candidate_above_maximum"
    anchors = _load_hard_anchor_contract()
    if anchors is None:
        return "under_length_hard_anchor_contract_unavailable"
    ignored_values = {
        str(spec["minimum"]),
        str(spec.get("maximum") or 0),
    }
    anchor_result = anchors.compare(
        original,
        candidate,
        request,
        ignored_authority_values=ignored_values,
    )
    anchor_reason = anchor_result.get("reason")
    if anchor_reason == "numbers":
        return "under_length_number_added_dropped_or_changed"
    if anchor_reason == "quantities":
        return "under_length_quantity_added_dropped_or_changed"
    if anchor_reason == "quotes":
        return "under_length_quote_dropped_or_changed"
    if anchor_reason == "fields":
        return "under_length_field_order_or_name_changed"
    for label in _required_labels(request):
        if label not in candidate:
            return "under_length_explicit_title_or_field_dropped"
    transition_reason = _status_transition_reason(original, candidate)
    if transition_reason:
        return transition_reason
    has_anchor = bool(STATUS_ANCHOR_RE.search(request) or STATUS_ANCHOR_RE.search(original))
    if GENERAL_CONTINUATION_RE.search(candidate) and not has_anchor:
        return "under_length_general_continuation_unanchored"
    return None


def _revision_instruction(request: str, original: str, spec: dict[str, Any]) -> str:
    maximum = int(spec.get("maximum") or 0)
    target = f"{spec['minimum']}—{maximum}字" if maximum else f"不少于{spec['minimum']}字"
    preferred_minimum = spec["minimum"] + PREFERRED_MINIMUM_HEADROOM
    preferred_maximum = spec["minimum"] + PREFERRED_MAXIMUM_HEADROOM
    if maximum:
        preferred_minimum = min(maximum, preferred_minimum)
        preferred_maximum = min(maximum, preferred_maximum)
    preferred = (
        f"本轮优先控制在{preferred_minimum}—{preferred_maximum}字"
        if preferred_minimum < preferred_maximum
        else f"本轮至少达到{preferred_minimum}字"
    )
    return (
        "篇幅复核发现上一稿低于用户明确下限 10% 以上。请以原请求、用户材料和 D0 为事实边界，"
        f"将 D0 修订到{target}；{preferred}，只输出完整终稿。\n"
        "公文常识只用于安排文种结构、段落顺序和自然衔接，不能据此补写本次事项的场景、原因、目的、"
        "过程、作用、影响、评价、体验或未来用途。每个新增句的核心谓语都必须能由原请求、用户材料或 D0 "
        "中的明确表述直接回指；允许重组、分类和归纳已列事实，允许说明已给事实之间不引入新事件信息的"
        "直接关系。合理推断必须同时有材料中的主体和同一事项或状态锚，只能保持原有强度；不能把常见做法、"
        "可能效果或一般必要性写成本次事实。已有计划方向时，‘拟完善、拟优化’与‘将在下一年度改进’可作"
        "同强度变体。不得新增材料未出现的具体主体、日期、数字、金额、职责、流程、会议内容、决定、结果、"
        "验收结论或完成状态；也不得新增群众体验、参与方式、反馈内容、工作成效、保障作用、资金充分性、"
        "效率影响、规范化目标等材料没有写明的判断。不得用连续否定、免责声明、空泛承诺或重复句式凑字。"
        "同一数字、金额、用途和未决状态原则上只写一次，不通过再次列举硬值补足篇幅。"
        "若现有事实不足以安全达到下限，逐字返回 D0，不要勉强补足。\n"
        "【原请求】\n" + request + "\n【D0】\n" + original
    )


def _increment_items(original: str, candidate: str) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    matcher = SequenceMatcher(a=original, b=candidate, autojunk=False)
    for index, opcode in enumerate(matcher.get_opcodes(), start=1):
        operation, d0_start, d0_end, d1_start, d1_end = opcode
        if operation == "equal":
            continue
        d0_text = original[d0_start:d0_end]
        d1_text = candidate[d1_start:d1_end]
        items.append(
            {
                "id": f"I{index:03d}",
                "operation": operation,
                "d0_text": d0_text,
                "d0_sha256": _sha256_text(d0_text),
                "d1_text": d1_text,
                "d1_sha256": _sha256_text(d1_text),
            }
        )
    return items


def _unsupported_added_process(
    request: str, original: str, increments: list[dict[str, Any]]
) -> str | None:
    authority = re.sub(r"\s+", "", request + "\n" + original)
    for item in increments:
        added = item.get("d1_text")
        if not isinstance(added, str):
            continue
        for match in UNSUPPORTED_ADDED_PROCESS_RE.finditer(added):
            phrase = re.sub(r"\s+", "", match.group(0))
            if phrase and phrase not in authority:
                return "under_length_unsupported_added_process"
    return None


def _verdict_instruction(
    request: str,
    original: str,
    candidate: str,
    spec: dict[str, Any],
    increments: list[dict[str, Any]],
) -> str:
    anchors = _load_hard_anchor_contract()
    ignored_values = {str(spec["minimum"]), str(spec.get("maximum") or 0)}
    anchor_relations = (
        anchors.compare(
            original,
            candidate,
            request,
            ignored_authority_values=ignored_values,
        ).get("relation_packet", [])
        if anchors is not None
        else []
    )
    response = {
        "schema_version": SCHEMA_VERSION,
        "request_sha256": _sha256_text(request),
        "d0_sha256": _sha256_text(original),
        "d1_sha256": _sha256_text(candidate),
        "verdict": "PASS or FAIL",
        "checks": {
            "no_new_specific_fact": False,
            "facts_and_states_preserved": False,
            "length_genre_and_naturalness_preserved": False,
        },
        "increments": [
            {**item, "category": "restatement"} for item in increments
        ],
    }
    return (
        "只读核验 D1 相对 D0 的全部增量，并只输出一个 JSON 对象。冻结增量须逐 id 原样回填。"
        "每项分类为 restatement、transparent_derivation、reasonable_inference 或 new_specific_fact。"
        "公文常识只能支持结构和衔接，不能单独支持本次事项的新谓语。材料事实、无需新增事件信息的直接关系，"
        "以及同时具有材料主体和同一事项或状态锚、且不升级强度的合理推断可以通过；已有下一年度计划时，"
        "拟完善、拟优化与将在下一年度改进是允许的同强度表达。新增具体人事、时间、数字、职责、流程、"
        "决定、结果或状态升级，以及材料未写明的场景、原因、目的、作用、影响、评价、体验、反馈内容、"
        "工作成效、保障作用、资金充分性或规范化目标，必须标 new_specific_fact 并 FAIL。"
        "透明分类和真实归纳不能只因换了概括词而失败，但不得借概括补入新的事实判断。"
        "候选以等义总量句明确承载同一主体、对象和范围时，不要求重复保留原稿中的范围自证；"
        "只有范围缩小、主体或对象换位、事项遗漏或状态改变才按关系丢失处理。"
        "以保护性外扩、重复、自证或空话凑字也必须 FAIL。"
        "凡 D1 新增通知、督促、落实、准备、报送方式、会议纪律、协调办法等动作或义务，而原请求或 D0 "
        "没有同一事项授权，均属新增流程或职责，不得标为 restatement。"
        "只评价 D1 增量，不把 D0 原有问题归给 D1；不确定即 FAIL。\n"
        + json.dumps(response, ensure_ascii=False)
        + "\n【原请求】\n" + request
        + "\n【D0】\n" + original
        + "\n【D1】\n" + candidate
        + "\n【共享硬锚关系复核项】\n" + json.dumps(anchor_relations, ensure_ascii=False)
        + "\n【冻结增量】\n" + json.dumps(increments, ensure_ascii=False)
        + "\n【篇幅规格】\n" + json.dumps(spec, ensure_ascii=False)
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
    increments: list[dict[str, Any]],
) -> bool:
    if not isinstance(value, dict):
        return False
    if value.get("schema_version") != SCHEMA_VERSION:
        return False
    if value.get("request_sha256") != _sha256_text(request):
        return False
    if value.get("d0_sha256") != _sha256_text(original):
        return False
    if value.get("d1_sha256") != _sha256_text(candidate):
        return False
    expected_checks = {
        "no_new_specific_fact",
        "facts_and_states_preserved",
        "length_genre_and_naturalness_preserved",
    }
    checks = value.get("checks")
    if (
        value.get("verdict") != "PASS"
        or not isinstance(checks, dict)
        or set(checks) != expected_checks
        or not all(checks.get(key) is True for key in expected_checks)
    ):
        return False
    received = value.get("increments")
    if not isinstance(received, list) or len(received) != len(increments):
        return False
    expected = {
        (
            item["id"], item["operation"], item["d0_text"], item["d0_sha256"],
            item["d1_text"], item["d1_sha256"],
        )
        for item in increments
    }
    allowed = {"restatement", "transparent_derivation", "reasonable_inference", "new_specific_fact"}
    actual = {
        (
            item.get("id"), item.get("operation"), item.get("d0_text"),
            item.get("d0_sha256"), item.get("d1_text"), item.get("d1_sha256"),
        )
        for item in received
        if isinstance(item, dict) and item.get("category") in allowed
    }
    return actual == expected and all(
        isinstance(item, dict) and item.get("category") != "new_specific_fact"
        for item in received
    )


def _select(record: dict[str, Any], selection: str, reason: str) -> dict[str, Any]:
    state = record["under_length"]
    output = state.get("candidate") if selection == "D1" else state["original"]
    if not isinstance(output, str):
        output = state["original"]
        selection = "D0"
    state["audit"] = {
        "schema_version": SCHEMA_VERSION,
        "trigger": "under",
        "original_sha256": _sha256_text(state["original"]),
        "candidate_sha256": _sha256_text(state.get("candidate", "")) if state.get("candidate") else None,
        "spec": state.get("spec"),
        "original_count": state.get("original_count"),
        "candidate_count": state.get("candidate_count"),
        "selection": selection,
        "reason": reason,
        "delivery_sha256": _sha256_text(output),
        "delivery_verified": False,
    }
    state["phase"] = PHASE_OUTPUT
    record["under_length_selected_output"] = output
    record["under_length_selected_sha256"] = _sha256_text(output)
    return _block("篇幅复核已完成。请逐字输出下列已选终稿，不要调用工具、不要加说明：\n" + output)


def start(
    event: dict[str, Any], record: dict[str, Any], review_gate: Any
) -> dict[str, Any] | None:
    request = record.get("request")
    draft = event.get("last_assistant_message")
    if not isinstance(request, str) or not isinstance(draft, str) or not draft.strip():
        return None
    try:
        findings = review_gate.locate_candidates(request, draft).get("findings") or []
    except Exception:
        return None
    if findings:
        record["under_length_bypass"] = "ordinary_findings_present"
        return None
    if _user_allows_shortfall(request):
        record["under_length_bypass"] = "user_allows_shortfall"
        return None
    spec = parse_spec(request)
    if spec is None:
        return None
    original_count = count_text(draft, spec["scope"])
    if original_count >= math.ceil(spec["minimum"] * (1 - UNDER_TOLERANCE_RATIO)):
        return None
    record["under_length"] = {
        "schema_version": SCHEMA_VERSION,
        "capability": CAPABILITY_NAME,
        "phase": PHASE_REVISION,
        "original": draft,
        "original_count": original_count,
        "spec": spec,
    }
    return _block(_revision_instruction(request, draft, spec))


def is_active(record: dict[str, Any]) -> bool:
    return isinstance(record.get("under_length"), dict)


def advance(event: dict[str, Any], record: dict[str, Any]) -> dict[str, Any]:
    state = record["under_length"]
    request = record.get("request")
    if not isinstance(request, str):
        return _select(record, "D0", "request_missing")
    phase = state.get("phase")
    if phase == PHASE_REVISION:
        candidate = event.get("last_assistant_message")
        if not isinstance(candidate, str) or not candidate.strip():
            return _select(record, "D0", "revision_missing")
        state["candidate"] = candidate
        state["candidate_count"] = count_text(candidate, state["spec"]["scope"])
        reason = mechanical_reason(state["original"], candidate, state["spec"], request)
        if reason:
            return _select(record, "D0", reason)
        state["increments"] = _increment_items(state["original"], candidate)
        unsupported = _unsupported_added_process(
            request, state["original"], state["increments"]
        )
        if unsupported:
            return _select(record, "D0", unsupported)
        state["phase"] = PHASE_VERDICT
        return _block(
            _verdict_instruction(request, state["original"], candidate, state["spec"], state["increments"])
        )
    if phase == PHASE_VERDICT:
        verdict = _parse_json(event.get("last_assistant_message"))
        if _verdict_passes(verdict, request, state["original"], state.get("candidate", ""), state.get("increments", [])):
            return _select(record, "D1", "semantic_pass")
        return _select(record, "D0", "semantic_rejected")
    if phase == PHASE_OUTPUT:
        delivered = event.get("last_assistant_message")
        if isinstance(delivered, str) and _sha256_text(delivered) == record.get("under_length_selected_sha256"):
            state["phase"] = PHASE_COMPLETE
            state["audit"]["delivery_verified"] = True
            record.pop("under_length_selected_output", None)
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
            record["under_length_selected_output"] = state["original"]
            record["under_length_selected_sha256"] = _sha256_text(state["original"])
            return _block("扩写稿回显不一致，已回退原始稿。请逐字输出下列 D0，不要调用工具、不要加说明：\n" + state["original"])
        if attempts < MAX_FINAL_ECHO_ATTEMPTS:
            state["output_reprompts"] = attempts + 1
            return _block("原始稿回显不一致。请逐字输出下列 D0，不要调用工具、不要加说明：\n" + state["original"])
        state["phase"] = PHASE_FAILED
        state["audit"].update(
            {"delivery_verified": False, "reason": "d0_echo_mismatch_technical_failure"}
        )
        record.pop("under_length_selected_output", None)
        return _allow()
    return _allow()
