"""Bounded source-relation candidates; no factual verdict or draft selection.

Offsets are Python string offsets into the unmodified input. Evidence spans and
hashes establish provenance only: an independent semantic review must establish
the original error, the correction, and preservation of all other facts.
"""

from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Iterable


MAX_CANDIDATES = 4
MAX_EVIDENCE = 4
KINDS = frozenset({"state_mismatch", "unsupported_prerequisite"})
_SENTENCE_RE = re.compile(r"[^。！？\n]+[。！？]?[”’\"'）)\]】》〉〕〗」』]*")
_CLAUSE_RE = re.compile(r"[^，,；;。！？\r\n]+")
_STATE_PATTERNS = (
    ("not_started", re.compile(r"(?:(?:尚|仍|还)?未|(?:尚|仍|还)?没有)(?:曾)?(?:开始|开展|启动)")),
    ("not_finished", re.compile(r"(?:(?:尚|仍|还)?未|(?:尚|仍|还)?没有)(?:全部|完全)?(?:完成|办结|结束)")),
    ("unsettled", re.compile(
        r"(?:(?:尚|仍|还)?未|(?:尚|仍|还)?没有)(?:确定|决定|明确|约定)|"
        r"(?:尚|仍)?(?:待定|未定)|有待(?:确定|明确)|(?:尚|仍)?不(?:确定|明确)|未知|不详|未(?:提供|说明|给出)"
    )),
    ("active", re.compile(r"正在|仍在|(?<![未不])已(?:经)?(?:开始|开展|启动)")),
    ("finished", re.compile(r"(?<![未不])已(?:经)?(?:全部|完全)?(?:完成|办结|结束)|(?:全部|全数)(?:完成|办结|结束)")),
    ("settled", re.compile(r"(?<![未不])已(?:经)?(?:确定|决定|明确)")),
)
_OPPOSED = frozenset({
    frozenset({"active", "not_started"}),
    frozenset({"active", "finished"}),
    frozenset({"not_finished", "finished"}),
    frozenset({"not_started", "finished"}),
    frozenset({"unsettled", "settled"}),
    frozenset({"partial", "full"}),
})
_COMPLETION_RE = re.compile(r"完成|办结|结束")
_PARTIAL_RE = re.compile(r"部分|少数|个别")
_FULL_RE = re.compile(r"全部|全数|全体|所有|均|都")
_PREREQUISITE_RE = re.compile(
    r"(?P<after>[^，,；;。！？\n]{2,48}?)(?:之后|以后|后)[，,\s]*"
    r"(?:(?:再|才|方)(?:能|可)?|[^，,；;。！？\n]{0,24}?(?:可(?:以)?|能(?:够)?)"
    r"[^，,；;。！？\n]{0,6}(?:推进|开展|进行|启动))"
    r"|只有(?P<only>[^；;。！？\n]{2,48}?)[，,\s]*才"
    r"|(?P<before>[^，,；;。！？\n]{2,48}?)(?:之前|前)[，,\s]*(?:暂不|不得|不能)"
)
_DEICTIC_FIELD_RE = re.compile(r"(?:上述|这些|该|这(?:一|两)?项?)(?:时间|日期)")
_PREVIOUS_UNIT_RE = re.compile(r"(?P<quote>[^；;。！？\r\n]+)[；;。！？][ \t]*(?:\r?\n[ \t]*)?\Z")
_PROPOSAL_RE = re.compile(r"^(?:建议|可考虑|例如|比如|假设|假如)")
_TERM_RE = re.compile(r"[\u3400-\u9fff]+|[A-Za-z][A-Za-z0-9_-]*")
_GENERIC_TERMS = frozenset({
    "目前", "当前", "现阶段", "截至", "本次", "下一步", "后续", "相关",
    "工作", "事项", "任务", "情况", "进度", "时间", "日期", "安排",
    "完成", "办结", "结束", "进行", "开展", "启动", "推进", "明确", "确定",
    "尚未", "仍未", "未定", "已经", "正在", "部分", "少数", "个别",
    "全部", "全体", "所有", "全数", "之后", "以后", "之前", "只有",
})
_REVIEW_REQUIREMENTS = {
    "original_error": "逐项确认完整请求及材料支持原稿确有状态、完成范围或无据前置条件问题；候选、词面差异及证据哈希都不是错误证明。",
    "correction": "逐项确认实际替换或删除解决了原问题；材料仅说日期未知时，既不能推出必须等待，也不能反推事项已经开展。",
    "retained_facts": "逐项核对其他主体、对象、数字、时间、范围、条件及必要内容保持；删除须结合完整上下文确认必要事实仍在。以最新明确更正为准，合理分析和同项自然延续不当然是新增事实；来源冲突或证据不足记为未知。",
}


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _sentences(text: str) -> Iterable[tuple[int, str, int, int]]:
    offset = 0
    for line_number, line in enumerate(text.splitlines(keepends=True), 1):
        for match in _SENTENCE_RE.finditer(line.rstrip("\r\n")):
            quote = match.group().strip()
            if quote:
                start = offset + match.start() + len(match.group()) - len(match.group().lstrip())
                yield line_number, quote, start, start + len(quote)
        offset += len(line)


def _states(clause: str) -> list[tuple[str, int, int]]:
    states: list[tuple[str, int, int]] = []
    for kind, pattern in _STATE_PATTERNS:
        for match in pattern.finditer(clause):
            if not any(match.start() < end and start < match.end() for _, start, end in states):
                states.append((kind, match.start(), match.end()))
    if _COMPLETION_RE.search(clause):
        for kind, pattern in (("partial", _PARTIAL_RE), ("full", _FULL_RE)):
            states.extend((kind, m.start(), m.end()) for m in pattern.finditer(clause))
    return states


def _terms(clause: str) -> set[str]:
    # Mask operators before matching a matter. A shared "未定" or "日期"
    # alone must not link unrelated subjects; this is not an entailment test.
    content = list(clause)
    for _, start, end in _states(clause):
        content[start:end] = " " * (end - start)
    terms = set()
    for match in _TERM_RE.finditer("".join(content)):
        token = match.group().lower()
        for size in range(2, min(6, len(token)) + 1):
            terms.update(token[i:i + size] for i in range(len(token) - size + 1))
    return {term for term in terms - _GENERIC_TERMS
            if not re.fullmatch(r"[〇零一二两三四五六七八九十百千万亿]+", term)}


def _unsettled_terms(clause: str, states: list[tuple[str, int, int]]) -> set[str]:
    # Match the field beside the operator, not an earlier actor/action. For
    # example, waiting for verification is not waiting for its unknown date.
    terms: set[str] = set()
    for kind, start, end in states:
        if kind == "unsettled":
            after = clause[end:].strip(" 的了：:")
            operand = after[:8] if after else clause[:start].rstrip()[-4:]
            terms.update(_terms(operand))
    return terms


def _authority(request: str, source: str) -> list[dict[str, Any]]:
    records = []
    for origin, text in (("request", request), ("source", source)):
        for _, quote, start, end in _sentences(text):
            for match in _CLAUSE_RE.finditer(quote):
                clause = match.group().strip()
                states = _states(clause)
                if states:
                    records.append({
                        "evidence": {"origin": origin, "quote": quote,
                                     "span_start": start, "span_end": end},
                        "states": {kind for kind, _, _ in states},
                        "terms": _terms(clause),
                        "unsettled_terms": _unsettled_terms(clause, states),
                    })
    return records


def _previous_unsettled_context(draft: str, start: int) -> dict[str, Any] | None:
    match = _PREVIOUS_UNIT_RE.search(draft[:start])
    if match is None:
        return None
    raw = match.group("quote")
    quote = raw.strip()
    if not any(kind == "unsettled" for kind, _, _ in _states(quote)):
        return None
    offset = match.start("quote") + len(raw) - len(raw.lstrip())
    return {"quote": quote, "span_start": offset, "span_end": offset + len(quote)}


def locate_candidates(request: str, source: str, draft: str) -> list[dict[str, Any]]:
    """Locate at most four unconfirmed, source-related sentence candidates.

    This deliberately does not treat unfinished as unstarted, infer a full
    population from an unqualified noun, or reconcile conflicting sources.
    No candidate means only that these narrow patterns did not locate one.
    A final semicolon clause with an adjacent date/time anaphor can be targeted
    separately; its leading semicolon is removed while the final stop survives.
    """
    authority = _authority(request, source)
    findings = []
    for line, target, start, end in _sentences(draft):
        hits: list[tuple[str, dict[str, Any]]] = []
        related = []
        draft_context = None
        local_span = None
        for match in _CLAUSE_RE.finditer(target):
            clause = match.group().strip()
            states = {kind for kind, _, _ in _states(clause)}
            terms = _terms(clause)
            # Search the whole sentence below: a comma may separate "后" and "才".
            for record in authority:
                if terms & record["terms"]:
                    related.append(record["evidence"])
                    if any(frozenset({left, right}) in _OPPOSED
                           for left in states for right in record["states"]):
                        hits.append(("state_mismatch", record["evidence"]))
        if not _PROPOSAL_RE.match(target):
            for match in _PREREQUISITE_RE.finditer(target):
                condition = next(value for value in match.groupdict().values() if value is not None)
                terms = _terms(condition)
                context = (
                    _previous_unsettled_context(draft, start + match.start())
                    if _DEICTIC_FIELD_RE.search(condition) else None
                )
                context_terms = _terms(context["quote"]) if context else set()
                for record in authority:
                    if "unsettled" not in record["states"]:
                        continue
                    if terms & record["unsettled_terms"] or context_terms & record["unsettled_terms"]:
                        hits.append(("unsupported_prerequisite", record["evidence"]))
                        if context and context_terms & record["unsettled_terms"]:
                            draft_context = context
                            prefix = draft[start:start + match.start()].rstrip()
                            if prefix.endswith(("；", ";")) and target.endswith(("。", "！", "？")):
                                local_span = (start + len(prefix) - 1, end - 1)
        if not hits:
            continue
        kind = ("unsupported_prerequisite"
                if any(k == "unsupported_prerequisite" for k, _ in hits) else "state_mismatch")
        if local_span is not None:
            start, end = local_span
            target = draft[start:end]
            hits = [(kind, item) for hit_kind, item in hits if hit_kind == kind]
        # Keep trigger evidence and any matching latest correction visible. The
        # verifier still needs the complete request/source, not only this sample.
        evidence = []
        seen = set()
        triggers = sorted((item for _, item in hits), key=lambda x: (x["origin"] != "request", -x["span_start"]))
        context_records = sorted(related, key=lambda x: (x["origin"] != "request", -x["span_start"]))
        latest = [next((item for item in context_records if item["origin"] == origin), None)
                  for origin in ("request", "source")]
        ordered = triggers[:1] + [item for item in latest if item is not None] + triggers[1:] + context_records
        for item in ordered:
            key = (item["origin"], item["span_start"], item["span_end"])
            if key not in seen:
                evidence.append(dict(item))
                seen.add(key)
            if len(evidence) == MAX_EVIDENCE:
                break
        relation = (
            "核对是否将材料未定字段写成推进同一事项的等待条件；未定字段本身不证明必须等待。"
            if kind == "unsupported_prerequisite" else
            "核对状态或完成范围的词面差异是否对应同一主体、对象和阶段；不同分项、时间或最新更正可能使原稿成立。"
        )
        relation_record: dict[str, Any] = {"kind": kind, "evidence": evidence, "relation": relation}
        if draft_context is not None:
            # D0 supplies only the adjacent referent; it is not source authority.
            relation_record["draft_context"] = draft_context
        findings.append({
            "finding_id": f"S{len(findings) + 1:03d}",
            "labels": ["source-" + kind.replace("_", "-")],
            "line": line, "target": target, "span_start": start, "span_end": end,
            "source_exact": bool(source and len(re.sub(r"\s", "", target)) >= 8 and target in source),
            "request_exact": bool(len(re.sub(r"\s", "", target)) >= 8 and target in request),
            "assessment_status": "pending",
            "source_relation": relation_record,
        })
        if len(findings) == MAX_CANDIDATES:
            break
    return findings


def _checked_span(text: str, item: dict[str, Any], quote: str) -> tuple[int, int]:
    start, end = item.get("span_start"), item.get("span_end")
    if (type(start) is not int or type(end) is not int or start < 0 or end <= start
            or end > len(text) or text[start:end] != quote):
        raise ValueError("source relation span does not match its input")
    return start, end


def _checked_relation(relation: Any, inputs: dict[str, str], draft: str) -> dict[str, Any]:
    if not isinstance(relation, dict) or relation.get("kind") not in KINDS:
        raise ValueError("source relation kind is invalid")
    evidence = relation.get("evidence")
    if not isinstance(evidence, list) or not evidence or not isinstance(relation.get("relation"), str):
        raise ValueError("source relation evidence is missing")
    for item in evidence:
        if not isinstance(item, dict) or item.get("origin") not in inputs or not isinstance(item.get("quote"), str):
            raise ValueError("source relation evidence origin or quote is invalid")
        _checked_span(inputs[item["origin"]], item, item["quote"])
    if "draft_context" in relation:
        context = relation["draft_context"]
        if not isinstance(context, dict) or not isinstance(context.get("quote"), str):
            raise ValueError("source relation draft context is invalid")
        _checked_span(draft, context, context["quote"])
    return json.loads(json.dumps(relation, ensure_ascii=False))


def build_relation_packet(
    request: str, source: str, draft: str, candidate: str,
    findings: list[dict[str, Any]], repairs: list[dict[str, Any]],
) -> dict[str, Any]:
    """Bind actual source-related edits to all four inputs, without judging them.

    Pass the complete finding/repair lists, including ordinary repairs, so their
    exact application can be checked against D1. KEEP/no-op items are not repairs
    of confirmed errors. Invalid bindings raise ValueError; none imply PASS.
    """
    indexed = {}
    for finding in findings:
        if not isinstance(finding, dict) or not isinstance(finding.get("finding_id"), str):
            raise ValueError("finding identity is invalid")
        if finding["finding_id"] in indexed:
            raise ValueError("finding identity is duplicated")
        indexed[finding["finding_id"]] = finding
    operations = []
    seen = set()
    for repair in repairs:
        if not isinstance(repair, dict) or not isinstance(repair.get("finding_id"), str):
            raise ValueError("repair identity is invalid")
        finding_id = repair["finding_id"]
        if finding_id in seen or finding_id not in indexed:
            raise ValueError("repair identity is duplicated or not detected")
        seen.add(finding_id)
        finding = indexed[finding_id]
        target, replacement = repair.get("target"), repair.get("replacement")
        if not isinstance(target, str) or not isinstance(replacement, str) or target != finding.get("target"):
            raise ValueError("repair target or replacement is invalid")
        start, end = _checked_span(draft, finding, target)
        decision = repair.get("decision")
        if decision not in {None, "KEEP", "DELETE", "REWRITE"} or (
            decision == "KEEP" and replacement != target
        ) or (decision == "DELETE" and replacement != "") or (decision == "REWRITE" and not replacement.strip()):
            raise ValueError("repair decision does not match its replacement")
        if replacement != target:
            operations.append((start, end, replacement, finding))
    operations.sort(key=lambda item: item[0])
    if any(current[0] < previous[1] for previous, current in zip(operations, operations[1:])):
        raise ValueError("repair spans overlap")
    rebuilt = draft
    for start, end, replacement, _ in reversed(operations):
        rebuilt = rebuilt[:start] + replacement + rebuilt[end:]
    if rebuilt != candidate:
        raise ValueError("repairs do not reproduce D1 exactly")
    items = []
    delta = 0
    for start, end, replacement, finding in operations:
        if "source_relation" in finding:
            items.append({
                "finding_id": finding["finding_id"], "target": finding["target"],
                "replacement": replacement, "span_start": start, "span_end": end,
                "candidate_span_start": start + delta,
                "candidate_span_end": start + delta + len(replacement),
                "source_relation": _checked_relation(
                    finding["source_relation"], {"request": request, "source": source}, draft
                ),
                "source_relation_supported": None, "resolved": None,
            })
        delta += len(replacement) - (end - start)
    packet = {
        "schema_version": 1, "request_sha256": _sha256(request),
        "source_sha256": _sha256(source), "d0_sha256": _sha256(draft),
        "d1_sha256": _sha256(candidate), "findings": items,
        "verification_requirements": dict(_REVIEW_REQUIREMENTS),
    }
    packet["packet_sha256"] = _sha256(json.dumps(packet, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    return packet
