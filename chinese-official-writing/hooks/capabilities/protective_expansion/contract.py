#!/usr/bin/env python3
"""Build semantic observation packets and apply exact delete-only selections."""

from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass
import hashlib
import json
import re
import sys
from typing import Any, Final, Iterable


PACKET_SCHEMA_VERSION: Final = 1
RESPONSE_SCHEMA_VERSION: Final = 1
MAX_INPUT_CHARACTERS: Final = 200_000
MAX_SELECTIONS: Final = 8
MIN_REASON_CHARACTERS: Final = 6
MAX_REASON_CHARACTERS: Final = 240
SENTENCE_RE: Final = re.compile(r"[^。！？\n]+[。！？]?")
HEADING_RE: Final = re.compile(
    r"^(?:#{1,6}\s+|[一二三四五六七八九十]+[、.]|第[一二三四五六七八九十百]+[章节条])"
)
ANCHOR_RE: Final = re.compile(
    r"\d+(?:\.\d+)?(?:%|％|万元|亿元|元|个|项|次|台|名|份|套|条|组|天|年|月|日)?|"
    r"[零〇一二两三四五六七八九十百千万亿]+(?:个|项|次|台|名|份|套|条|组|天|年|月|日|元)|"
    r"“[^”\n]+”|《[^》\n]+》"
)
EXPLICIT_DELETE_RE: Final = re.compile(r"(?:删除|删去|去掉|移除|不要写|不要保留)")
PRESERVE_RE: Final = re.compile(r"(?:逐字|原样)?(?:保留|写明|载明)|不得删除|不要删除|不能删除")
EXTERNAL_SOURCE_CUE_RE: Final = re.compile(
    r"(?:根据|依据|参照|结合)(?:已上传的?|所附|附件|上传文件|附件中的?|文件中的?|工具读取的?)(?:材料|附件|文件|内容)?|"
    r"(?:见|详见)(?:附件|上传文件)|从(?:附件|上传文件|本地文件)"
)
ALLOWED_FAMILIES: Final = frozenset(
    {
        "role_scope_disclaimer",
        "downstream_state_chain",
        "drafting_future_metadata",
        "detached_missing_result",
        "serial_self_certification",
        "unsupported_assurance",
        "unanchored_future_action",
        "negative_scope_expansion",
        "meeting_self_proof",
        "opposition_self_proof",
        "semantic_repetition",
    }
)
REQUIRED_ASSERTIONS: Final = (
    "authority_sufficient",
    "no_independent_genre_function",
    "deletion_preserves_fact_and_status",
    "deletion_preserves_rights_and_duties",
    "deletion_needs_no_rewrite",
)


@dataclass(frozen=True)
class Segment:
    segment_id: str
    kind: str
    start: int
    end: int
    sentence_start: int
    sentence_end: int
    text: str
    text_sha256: str
    eligible: bool
    protection_reason: str | None


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def canonical_json_sha256(value: dict[str, Any]) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return sha256_text(payload)


def _sentence_spans(text: str) -> Iterable[tuple[str, int, int, int]]:
    offset = 0
    for line in text.splitlines(keepends=True):
        content = line.rstrip("\r\n")
        line_break_length = len(line) - len(content)
        for match in SENTENCE_RE.finditer(content):
            raw = match.group(0)
            leading = len(raw) - len(raw.lstrip())
            trailing = len(raw) - len(raw.rstrip())
            start = offset + match.start() + leading
            end = offset + match.end() - trailing
            sentence = text[start:end]
            if sentence:
                yield sentence, start, end, line_break_length
        offset += len(line)


def _normalized(value: str) -> str:
    return re.sub(r"\s+", "", value.strip().rstrip("。！？"))


def _authority_window(target: str, authority: str) -> str:
    normalized_target = _normalized(target)
    normalized_authority = _normalized(authority)
    position = normalized_authority.find(normalized_target)
    if position < 0:
        return ""
    return normalized_authority[max(0, position - 28) : position + len(normalized_target) + 20]


def _authority_protection(target: str, request: str, source: str) -> str | None:
    source_window = _authority_window(target, source)
    if source_window:
        return "explicit_source_text"
    request_window = _authority_window(target, request)
    if request_window and not EXPLICIT_DELETE_RE.search(request_window):
        return "explicit_request_text"
    if request_window and PRESERVE_RE.search(request_window):
        return "explicit_preserve_directive"
    return None


def _structural_protection(target: str, kind: str) -> str | None:
    stripped = target.strip()
    if not stripped:
        return "empty_segment"
    if kind == "sentence" and HEADING_RE.match(stripped):
        return "heading_or_numbered_item"
    if "“" in target or "”" in target:
        return "quoted_content"
    return None


def _segment(
    draft: str,
    kind: str,
    start: int,
    end: int,
    sentence_start: int,
    sentence_end: int,
    request: str,
    source: str,
    index: int,
) -> Segment:
    target = draft[start:end]
    protection = _structural_protection(target, kind) or _authority_protection(
        target, request, source
    )
    return Segment(
        segment_id=f"S{index:03d}",
        kind=kind,
        start=start,
        end=end,
        sentence_start=sentence_start,
        sentence_end=sentence_end,
        text=target,
        text_sha256=sha256_text(target),
        eligible=protection is None,
        protection_reason=protection,
    )


def enumerate_segments(request: str, draft: str, source: str = "") -> list[Segment]:
    segments: list[Segment] = []
    for sentence, start, end, line_break_length in _sentence_spans(draft):
        sentence_end = end
        full_end = end
        line_start = draft.rfind("\n", 0, start) + 1
        line_end = draft.find("\n", end)
        line_end = len(draft) if line_end < 0 else line_end
        if not draft[line_start:start].strip() and not draft[end:line_end].strip():
            full_end = min(len(draft), end + line_break_length)
        segments.append(
            _segment(
                draft,
                "sentence",
                start,
                full_end,
                start,
                sentence_end,
                request,
                source,
                len(segments) + 1,
            )
        )
        content_end = end - 1 if sentence.endswith(tuple("。！？")) else end
        for match in re.finditer(r"[，,；;]", sentence):
            tail_start = start + match.start()
            if tail_start > start and tail_start < content_end:
                segments.append(
                    _segment(
                        draft,
                        "tail",
                        tail_start,
                        content_end,
                        start,
                        sentence_end,
                        request,
                        source,
                        len(segments) + 1,
                    )
                )
    return segments


def build_packet(
    request: str, draft: str, source: str = "", *, authority_scope: str | None = None
) -> dict[str, Any]:
    if any(len(value) > MAX_INPUT_CHARACTERS for value in (request, draft, source)):
        return {"schema_version": PACKET_SCHEMA_VERSION, "status": "unavailable", "reason": "input_too_large"}
    scope = authority_scope or ("explicit_source" if source.strip() else "request_only")
    authority_incomplete = bool(
        not source.strip()
        and (
            scope == "external_material_observed"
            or (scope == "request_only" and EXTERNAL_SOURCE_CUE_RE.search(request))
        )
    )
    packet = {
        "schema_version": PACKET_SCHEMA_VERSION,
        "status": "ready",
        "authority_scope": scope,
        "authority_incomplete": authority_incomplete,
        "request": request,
        "source": source,
        "draft": draft,
        "request_sha256": sha256_text(request),
        "source_sha256": sha256_text(source),
        "draft_sha256": sha256_text(draft),
        "allowed_families": sorted(ALLOWED_FAMILIES),
        "required_assertions": list(REQUIRED_ASSERTIONS),
        "segments": [asdict(item) for item in enumerate_segments(request, draft, source)],
    }
    packet["packet_sha256"] = canonical_json_sha256(packet)
    return packet


def observer_instruction(packet: dict[str, Any]) -> str:
    clear_response = {
        "schema_version": RESPONSE_SCHEMA_VERSION,
        "packet_sha256": packet.get("packet_sha256"),
        "request_sha256": packet.get("request_sha256"),
        "draft_sha256": packet.get("draft_sha256"),
        "decision": "CLEAR",
        "selections": [],
    }
    delete_response = {
        "schema_version": RESPONSE_SCHEMA_VERSION,
        "packet_sha256": packet.get("packet_sha256"),
        "request_sha256": packet.get("request_sha256"),
        "draft_sha256": packet.get("draft_sha256"),
        "decision": "DELETE_SPANS",
        "selections": [
            {
                "segment_id": "从观察包复制一个 eligible=true 的 S 编号",
                "family": "从 allowed_families 复制一个值",
                "reason": "说明该片段在当前文种和可见权威范围内为何没有独立作用",
                "assertions": {key: True for key in REQUIRED_ASSERTIONS},
            }
        ],
    }
    return (
        "请对完整初稿做一次保护性外扩语义观察，只输出一个 JSON 对象。不要输出正文、代码围栏或说明。"
        "这不是否定词检测：先判断句子在当前文种和上下文中是否承担事实状态、程序边界、法律效果、"
        "预算来源、监督责任、决策过程或风险告知。承担任一独立功能即不选。"
        "只要片段的语义事实在 source 中得到支持，即使措辞不完全相同也不选。"
        "只选择没有独立正文作用的连续自证、无锚下游状态串、泛化免责声明、材料外未来安排或范围扩大。"
        "如果 request 已明确列出可用事实并明确不写某类过程，而初稿仍补入该过程的下游未发生状态，"
        "该状态属于材料外扩，可在删除后正文仍完整时选择。"
        "如果 request 明确说明某项决定、转归、安排或程序没有材料依据，初稿却自行补入该项，"
        "这不是需要保留的真实未决状态，而是无依据未来治理元信息；删除后正文完整时应选择。"
        "同理，request 明确说明没有专项资金、监督、公开、验收或其他安排时，初稿不得补成相应承诺。"
        "如果同一句在有依据前缀后连续附加两个或更多无依据保护性分句，应选择覆盖全部无依据分句的最宽 eligible tail，"
        "不能只删最后一句而留下相邻的无依据自证；但不得把有依据的主体、事实或支出渠道一并选入。"
        "反之，request 或 source 只说事项尚未完成、尚未确定，且该状态本身有信息作用时，不得据此删除。"
        "不得要求改写、补责任主体、补进行态或补字；需要补写才能完整、看不到权威材料或有疑问时返回 CLEAR。"
        "decision 只允许 CLEAR 或 DELETE_SPANS，绝不能输出 SELECT、DELETE 或其他值。"
        "CLEAR 必须配空 selections；DELETE_SPANS 必须至少选择一项。"
        "选择时只能引用 eligible=true 的 segment_id；每项 family 必须来自 allowed_families，reason 简述当前上下文为何可删，"
        "并把 required_assertions 中每个字段逐项写为 true。CLEAR 骨架如下：\n"
        + json.dumps(clear_response, ensure_ascii=False)
        + "\nDELETE_SPANS 骨架（不要照抄示例字符串，须使用观察包中的真实值）："
        + json.dumps(delete_response, ensure_ascii=False)
        + "\n观察包如下：\n"
        + json.dumps(packet, ensure_ascii=False)
    )


def _selection_map(response: dict[str, Any]) -> tuple[dict[str, dict[str, Any]] | None, str]:
    selections = response.get("selections")
    if not isinstance(selections, list) or len(selections) > MAX_SELECTIONS:
        return None, "invalid_selections"
    mapped: dict[str, dict[str, Any]] = {}
    for selection in selections:
        if not isinstance(selection, dict) or not isinstance(selection.get("segment_id"), str):
            return None, "invalid_selection_item"
        segment_id = selection["segment_id"]
        if segment_id in mapped:
            return None, "duplicate_segment"
        mapped[segment_id] = selection
    return mapped, "ok"


def _validate_selection(selection: dict[str, Any], segment: dict[str, Any]) -> str | None:
    if segment.get("eligible") is not True:
        return "protected_segment"
    if selection.get("family") not in ALLOWED_FAMILIES:
        return "unknown_family"
    reason = selection.get("reason")
    if not isinstance(reason, str) or not MIN_REASON_CHARACTERS <= len(reason.strip()) <= MAX_REASON_CHARACTERS:
        return "invalid_reason"
    assertions = selection.get("assertions")
    if not isinstance(assertions, dict) or any(assertions.get(key) is not True for key in REQUIRED_ASSERTIONS):
        return "incomplete_assertions"
    return None


def _validate_response(packet: dict[str, Any], response: dict[str, Any]) -> tuple[list[dict[str, Any]] | None, str]:
    expected = {
        "schema_version": RESPONSE_SCHEMA_VERSION,
        "packet_sha256": packet.get("packet_sha256"),
        "request_sha256": packet.get("request_sha256"),
        "draft_sha256": packet.get("draft_sha256"),
    }
    if any(response.get(key) != value for key, value in expected.items()):
        return None, "response_binding_mismatch"
    decision = response.get("decision")
    mapped, reason = _selection_map(response)
    if mapped is None:
        return None, reason
    if decision == "CLEAR":
        return ([], "clear") if not mapped else (None, "clear_with_selections")
    if decision != "DELETE_SPANS" or not mapped:
        return None, "invalid_decision"
    if packet.get("authority_incomplete") is True:
        return None, "authority_incomplete"
    segments = {item["segment_id"]: item for item in packet.get("segments") or [] if isinstance(item, dict)}
    selected: list[dict[str, Any]] = []
    for segment_id, selection in mapped.items():
        segment = segments.get(segment_id)
        if segment is None:
            return None, "unknown_segment"
        invalid = _validate_selection(selection, segment)
        if invalid:
            return None, invalid
        selected.append(segment)
    return selected, "selected"


def _anchors(value: str) -> Counter[str]:
    return Counter(ANCHOR_RE.findall(value))


def _apply_segments(draft: str, selected: list[dict[str, Any]]) -> tuple[str | None, str]:
    spans = sorted((item.get("start"), item.get("end"), item) for item in selected)
    if any(not isinstance(start, int) or not isinstance(end, int) or not 0 <= start < end <= len(draft) for start, end, _ in spans):
        return None, "invalid_span"
    if any(current[0] < previous[1] for previous, current in zip(spans, spans[1:])):
        return None, "overlapping_spans"
    for start, end, item in spans:
        target = draft[start:end]
        if target != item.get("text") or sha256_text(target) != item.get("text_sha256"):
            return None, "segment_hash_mismatch"
    pieces: list[str] = []
    cursor = 0
    for start, end, _ in spans:
        pieces.append(draft[cursor:start])
        cursor = end
    pieces.append(draft[cursor:])
    candidate = "".join(pieces)
    if not candidate.strip():
        return None, "empty_candidate"
    original_anchors, candidate_anchors = _anchors(draft), _anchors(candidate)
    if any(candidate_anchors[key] == 0 for key in original_anchors):
        return None, "unique_anchor_removed"
    return candidate, "edited"


def apply_response(packet: dict[str, Any], response: dict[str, Any]) -> dict[str, Any]:
    original = packet.get("draft")
    if not isinstance(original, str) or packet.get("status") != "ready":
        return {"status": "fallback", "selection": "E0", "reason": "invalid_packet", "output": original if isinstance(original, str) else ""}
    if canonical_json_sha256({key: value for key, value in packet.items() if key != "packet_sha256"}) != packet.get("packet_sha256"):
        return {"status": "fallback", "selection": "E0", "reason": "packet_hash_mismatch", "output": original}
    selected, reason = _validate_response(packet, response)
    if selected is None:
        return {"status": "fallback", "selection": "E0", "reason": reason, "output": original, "output_sha256": sha256_text(original)}
    if not selected:
        return {"status": "clear", "selection": "E0", "reason": reason, "output": original, "output_sha256": sha256_text(original)}
    candidate, apply_reason = _apply_segments(original, selected)
    if candidate is None:
        return {"status": "fallback", "selection": "E0", "reason": apply_reason, "output": original, "output_sha256": sha256_text(original)}
    return {
        "status": "edited",
        "selection": "E1",
        "reason": apply_reason,
        "selected_segment_ids": [item["segment_id"] for item in selected],
        "output": candidate,
        "output_sha256": sha256_text(candidate),
        "original_sha256": sha256_text(original),
    }


def main() -> int:
    try:
        payload = json.load(sys.stdin)
        if not isinstance(payload, dict):
            raise ValueError("payload must be an object")
        mode = payload.get("mode")
        if mode == "packet":
            request, draft, source = (payload.get(key, "") for key in ("request", "draft", "source"))
            if not all(isinstance(value, str) for value in (request, draft, source)):
                raise ValueError("request, draft, and source must be strings")
            result = build_packet(request, draft, source, authority_scope=payload.get("authority_scope"))
        elif mode == "apply":
            packet, response = payload.get("packet"), payload.get("response")
            if not isinstance(packet, dict) or not isinstance(response, dict):
                raise ValueError("packet and response must be objects")
            result = apply_response(packet, response)
        else:
            raise ValueError("unsupported mode")
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError):
        result = {"status": "unavailable", "selection": "E0", "reason": "invalid_input"}
    sys.stdout.write(json.dumps(result, ensure_ascii=False, separators=(",", ":")) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
