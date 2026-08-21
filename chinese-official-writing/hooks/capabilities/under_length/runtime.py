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
FACT_LEDGER_SCHEMA_VERSION: Final = 2
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
    labels = _required_field_labels(request)
    for match in EXPLICIT_TITLE_RE.finditer(request):
        label = match.group(1).strip(" 《》\"“”")
        if label:
            labels.add(label)
    return labels


def _required_field_labels(request: str) -> set[str]:
    labels: set[str] = set()
    for match in EXPLICIT_FIELD_RE.finditer(request):
        raw = re.split(
            r"[，,]\s*(?=(?:请(?:扩写|压缩|起草|撰写|输出|将|把)|正文|全文|成稿|输出|扩写|压缩|起草|撰写))",
            match.group(1),
            maxsplit=1,
        )[0]
        labels.update(
            token.strip(" 《》\"“”")
            for token in re.split(r"[、,，/]", raw)
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
    try:
        anchor_result = anchors.compare(
            original,
            candidate,
            request,
            ignored_authority_values=ignored_values,
            allowed_field_labels=_required_field_labels(request),
            allow_transparent_quantity_summaries=True,
        )
    except Exception:
        return "under_length_hard_anchor_contract_unavailable"
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


_LEDGER_ROLES: Final = ("subject", "object", "predicate", "status", "intensity")
_LEDGER_CORE_ROLES: Final = ("subject", "predicate", "object")
_LEDGER_RELATIONS: Final = {
    "same", "restatement", "transparent_derivation", "reasonable_inference"
}
_LEDGER_SAFE_RESTATEMENTS: Final = frozenset(
    {
        frozenset({"开展", "进行"}),
        frozenset({"面向", "对象为"}),
        frozenset({"尚未确定", "仍待明确"}),
    }
)
_LEDGER_ACHIEVED_EFFECT_RE: Final = re.compile(
    r"(?:已经|现已|已|取得|实现).{0,10}(?:提升|提高|改善|缓解|降低|减少|增强|成效|效果)"
)


def _ledger_text(value: Any) -> str:
    if not isinstance(value, str):
        return ""
    return re.sub(r"\s+", "", value).strip("，。；：、,.;: ")


def _ledger_role_is_absent(value: str) -> bool:
    return value in {"", "无", "未涉及", "不适用", "__none__"}


def _ledger_safe_restatement(source: str, candidate: str) -> bool:
    return frozenset({source, candidate}) in _LEDGER_SAFE_RESTATEMENTS


def _fact_ledger_passes(
    value: dict[str, Any] | None,
    request: str,
    original: str,
    candidate: str,
    increments: list[dict[str, Any]],
) -> bool:
    """Check a narrow, hash-bound fact ledger for every D1 increment.

    This prototype does not pretend to perform full Chinese semantic parsing.
    It mechanically requires each subject/object/predicate/state/intensity
    claim to point to exact source text. The non-empty subject, predicate and
    object must also co-occur in one selected source span, so separately true
    spans cannot be concatenated into a new relation. Same-value relations are
    mechanically exact; a restatement must point to wording somewhere in the
    frozen authority. The independent verifier still supplies the final
    semantic judgment.
    """

    if not isinstance(value, dict) or value.get("schema_version") != FACT_LEDGER_SCHEMA_VERSION:
        return False
    frozen = _fact_ledger_template(request, original, increments)
    spans = frozen["spans"]
    expected_sources = {"request": request, "d0": original}
    by_id: dict[str, dict[str, Any]] = {}
    for span in spans:
        span_id, origin = span.get("id"), span.get("origin")
        start, end = span.get("start"), span.get("end")
        quote, digest = span.get("quote"), span.get("sha256")
        if (
            not isinstance(span_id, str) or not span_id or span_id in by_id
            or origin not in expected_sources
            or not isinstance(start, int) or not isinstance(end, int)
            or start < 0 or start >= end or end > len(expected_sources[origin])
            or not isinstance(quote, str)
            or quote != expected_sources[origin][start:end]
            or digest != _sha256_text(quote)
        ):
            return False
        by_id[span_id] = span
    expected_ids = {item["id"] for item in increments if item.get("d1_text")}
    ledger = value.get("ledger")
    if not isinstance(ledger, list) or len(ledger) != len(expected_ids):
        return False
    received: set[str] = set()
    for entry in ledger:
        if not isinstance(entry, dict):
            return False
        increment_id, span_ids = entry.get("increment_id"), entry.get("span_ids")
        if (
            not isinstance(increment_id, str) or increment_id in received
            or increment_id not in expected_ids or not isinstance(span_ids, list)
            or not span_ids or any(span_id not in by_id for span_id in span_ids)
        ):
            return False
        item = next(item for item in increments if item["id"] == increment_id)
        added = _ledger_text(item.get("d1_text"))
        source_text = _ledger_text("".join(by_id[span_id]["quote"] for span_id in span_ids))
        if not added or not source_text:
            return False
        core_source_roles: list[str] = []
        has_reasonable_inference = False
        for role in _LEDGER_ROLES:
            payload = entry.get(role)
            if not isinstance(payload, dict):
                return False
            source_role = _ledger_text(payload.get("source"))
            candidate_role = _ledger_text(payload.get("candidate"))
            relation = payload.get("relation")
            if relation not in _LEDGER_RELATIONS:
                return False
            if relation == "reasonable_inference":
                has_reasonable_inference = True
            if _ledger_role_is_absent(source_role) or _ledger_role_is_absent(candidate_role):
                if not (_ledger_role_is_absent(source_role) and _ledger_role_is_absent(candidate_role)):
                    return False
                if relation != "same":
                    return False
                continue
            if source_role not in source_text or candidate_role not in added:
                return False
            if role in _LEDGER_CORE_ROLES:
                core_source_roles.append(source_role)
            if relation == "same" and source_role != candidate_role:
                return False
            if (
                relation == "restatement"
                and candidate_role not in source_text
                and not _ledger_safe_restatement(source_role, candidate_role)
            ):
                return False
            if relation == "transparent_derivation" and candidate_role not in source_text:
                return False
        if has_reasonable_inference and any(
            match.group(0) not in source_text
            for match in _LEDGER_ACHIEVED_EFFECT_RE.finditer(added)
        ):
            return False
        if core_source_roles and not any(
            all(value in _ledger_text(by_id[span_id]["quote"]) for value in core_source_roles)
            for span_id in span_ids
        ):
            return False
        received.add(increment_id)
    return received == expected_ids


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


def _fact_ledger_template(
    request: str, original: str, increments: list[dict[str, Any]]
) -> dict[str, Any]:
    spans: list[dict[str, Any]] = []
    for origin, text, prefix in (
        ("request", request, "R"), ("d0", original, "D")
    ):
        index = 0
        for match in re.finditer(r"[^。！？；：;\r\n]+[。！？；：;]?", text):
            quote = match.group(0)
            leading = len(quote) - len(quote.lstrip())
            trailing = len(quote) - len(quote.rstrip())
            start = match.start() + leading
            end = match.end() - trailing
            if start >= end:
                continue
            quote = text[start:end]
            index += 1
            spans.append(
                {
                    "id": f"{prefix}{index:03d}",
                    "origin": origin,
                    "start": start,
                    "end": end,
                    "quote": quote,
                    "sha256": _sha256_text(quote),
                }
            )
    ledger: list[dict[str, Any]] = []
    for item in (item for item in increments if item.get("d1_text")):
        role = {"source": "", "candidate": "", "relation": "same"}
        ledger.append(
            {
                "increment_id": item["id"],
                "span_ids": [],
                **{name: dict(role) for name in _LEDGER_ROLES},
            }
        )
    return {
        "schema_version": FACT_LEDGER_SCHEMA_VERSION,
        "authority_sha256": _sha256_text(request + "\n" + original),
        "sources": {
            "request": {"sha256": _sha256_text(request), "length": len(request)},
            "d0": {"sha256": _sha256_text(original), "length": len(original)},
        },
        "spans": spans,
        "ledger": ledger,
    }


def _compact_fact_ledger_response(
    frozen: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": FACT_LEDGER_SCHEMA_VERSION,
        "ledger": frozen["ledger"],
    }


def _compact_span_catalog(
    frozen: dict[str, Any],
) -> list[dict[str, str]]:
    return [
        {"id": span["id"], "quote": span["quote"]}
        for span in frozen["spans"]
    ]


def _render_compact_span_catalog(frozen: dict[str, Any]) -> str:
    return "\n".join(
        f"{item['id']}\t{json.dumps(item['quote'], ensure_ascii=False)}"
        for item in _compact_span_catalog(frozen)
    )


def _verdict_instruction(
    request: str,
    original: str,
    candidate: str,
    spec: dict[str, Any],
    increments: list[dict[str, Any]],
) -> str | None:
    anchors = _load_hard_anchor_contract()
    if anchors is None:
        return None
    ignored_values = {str(spec["minimum"]), str(spec.get("maximum") or 0)}
    try:
        anchor_relations = anchors.compare(
            original,
            candidate,
            request,
            ignored_authority_values=ignored_values,
            allowed_field_labels=_required_field_labels(request),
            allow_transparent_quantity_summaries=True,
        ).get("relation_packet", [])
    except Exception:
        return None
    frozen_ledger = _fact_ledger_template(request, original, increments)
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
        "fact_ledger": _compact_fact_ledger_response(frozen_ledger),
    }
    return (
        "只读核验 D1 相对 D0 的全部增量，并只输出一个 JSON 对象。冻结增量须逐 id 原样回填。"
        "每项分类为 restatement、transparent_derivation、reasonable_inference 或 new_specific_fact。"
        "材料事实、无需新增事件信息的直接关系，以及材料事实与事项或对象通常功能直接支持的一层原因、目的、"
        "即时作用或低强度预期可以通过，不要求这些推断逐字出现在材料中。推断须绑定材料中的主体、对象、范围和"
        "当前状态，不得升级强度；满足时标 reasonable_inference。已有下一年度计划时，"
        "拟完善、拟优化与将在下一年度改进是允许的同强度表达。新增具体人事、时间、数字、职责、流程、"
        "决定、结果或状态升级，材料不能直接支持的具体场景、前提、评价、体验、反馈内容、工作成效、"
        "资金充分性或规范化目标，以及把预期写成已经取得的成效，必须标 new_specific_fact 并 FAIL。"
        "不能仅凭事项名称或空泛常识补作用凑字，但不得只因出现为了、便于、缓解、提高、改善或促进等作用词而失败。"
        "透明分类和真实归纳不能只因换了概括词而失败，但不得借概括补入新的事实判断。"
        "候选以等义总量句明确承载同一主体、对象和范围时，不要求重复保留原稿中的范围自证；"
        "但‘涉及两个小区’、‘86人参加’等独立范围事实仍必须保留。"
        "只有范围缩小、主体或对象换位、事项遗漏或状态改变才按关系丢失处理。"
        "以保护性外扩、重复、自证或空话凑字也必须 FAIL。"
        "凡 D1 新增通知、督促、落实、准备、报送方式、会议纪律、协调办法等动作或义务，而原请求或 D0 "
        "没有同一事项授权，均属新增流程或职责，不得标为 restatement。"
        "只评价 D1 增量，不把 D0 原有问题归给 D1；具体事实、状态或责任关系实质不确定时才 FAIL，"
        "推断措辞没有逐字来源本身不构成不确定。\n"
        "来源目录已由 Hook 按请求与 D0 的句或分句机械冻结；offset、origin 和 hash 只在 Hook 内部保存并回查，"
        "无需也不得调用工具重算。fact_ledger.ledger 已按每个非空增量给出一条骨架；"
        "不得删除固定的 increment_id 或把同一增量的多个子句拆成多条 ledger。只从已有来源目录选择直接相关 id 填入 span_ids，"
        "需要多个来源时可选择多个已有 id；没有直接相关 span 时应 FAIL。再填写 subject、object、predicate、status、intensity 五项。"
        "五个角色已用空字符串和 relation=same 预填为“不适用”；不涉及的角色须原样保留，不得改成 null，涉及的角色再替换为实际值。"
        "复合增量可在同一角色字段中填写材料与候选均连续出现的复合短语。"
        "每项都要给 source、candidate 和 relation；"
        "source 必须是所引 span 的原文，candidate 必须出现在该增量中。relation=same 时逐字保持；"
        "relation=restatement 时，candidate 须出现在冻结的请求或 D0 中，或仅使用开展/进行、面向/对象为、"
        "尚未确定/仍待明确这三组低风险等义表达；relation=transparent_derivation 时，candidate 仍须出现在冻结来源中；"
        "relation=reasonable_inference 时，source 须给出直接事实或通常功能锚，candidate 只能承载一层低强度"
        "原因、目的、即时作用或预期，不能承载新增具体事实或既成成效；"
        "合理推断也不免除同一来源 span 约束：核心角色的 source 应从同一条直接事实或通常功能锚中拆取，"
        "不要把用户允许推断、允许措辞或强度说明本身填作核心 source，也不要把问题句、计划句和通用授权句"
        "分开拼成一条关系；candidate 可以在低强度推断范围内不同于 source，但仍须出现在对应增量中。"
        "主体、谓语或动作、对象只要非空，至少一个所引来源 span 必须同时承载这些核心角色；不得跨 span 拼接新关系。"
        "不能用局部相关 span 为新增谓语、状态或强度背书。真实但无关的 span、局部相关但新增谓语的 span 均须 FAIL。"
        + json.dumps(response, ensure_ascii=False)
        + "\n【冻结来源目录】\n" + _render_compact_span_catalog(frozen_ledger)
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
    if actual != expected or not all(
        isinstance(item, dict) and item.get("category") != "new_specific_fact"
        for item in received
    ):
        return False
    return _fact_ledger_passes(
        value.get("fact_ledger"), request, original, candidate, increments
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
        instruction = _verdict_instruction(
            request, state["original"], candidate, state["spec"], state["increments"]
        )
        if instruction is None:
            return _select(record, "D0", "under_length_hard_anchor_contract_unavailable")
        state["phase"] = PHASE_VERDICT
        return _block(instruction)
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
