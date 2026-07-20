#!/usr/bin/env python3
"""Transactional one-pass review gate for Chinese official drafts.

The gate never drafts prose.  It snapshots an already complete D0, locates
review candidates once, accepts one bounded repair packet, verifies
deterministic invariants once, and then permanently selects D0 or D1.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import time
import uuid
from collections import Counter
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable, Iterator


SCHEMA_VERSION = 2
SEMANTIC_VERDICT_SCHEMA_VERSION = 1
REPAIR_PACKET_SCHEMA_VERSION = 1
GUIDED_MARKER_SCHEMA_VERSION = 1
MAX_REVISIONS = 1
MAX_VERIFICATIONS = 1
MAX_FINDINGS = 12
MAX_JSON_BYTES = 1_000_000
MIN_BODY_RETAIN_RATIO = 0.70
LENGTH_WORSENING_TOLERANCE_RATIO = 0.05
MIN_LENGTH_WORSENING_TOLERANCE = 20
REPAIR_MODE_EXTRACT = "extract"
REPAIR_MODE_REWRITE_SENTENCE = "rewrite_sentence"
REPAIR_MODE_DECISIONS = "decisions"
DECISION_KEEP = "KEEP"
DECISION_DELETE = "DELETE"
DECISION_REWRITE = "REWRITE"

STATE_DETECTING = "DETECTING"
STATE_AWAITING_REPAIR = "AWAITING_REPAIR"
STATE_MECHANICAL_VERIFYING = "MECHANICAL_VERIFYING"
STATE_AWAITING_VERDICT = "AWAITING_VERDICT"
STATE_SEMANTIC_VERIFYING = "SEMANTIC_VERIFYING"
STATE_TERMINAL_D0 = "TERMINAL_D0"
STATE_TERMINAL_D1 = "TERMINAL_D1"
TERMINAL_STATES = {STATE_TERMINAL_D0, STATE_TERMINAL_D1}

STATE_FILE = "state.json"
DETECTION_FILE = "detection.json"
REPAIR_PACKET_FILE = "repair.packet.json"
GUIDED_MARKER_FILE = "guided-marker.sidecar.json"
REQUEST_FILE = "request.snapshot.txt"
SOURCE_FILE = "source.snapshot.txt"
D0_FILE = "d0.snapshot.txt"
BACKUP_FILE = "snapshot.backup.json"
REPAIR_FILE = "repair.accepted.json"
D1_FILE = "d1.candidate.txt"
VERIFICATION_PACKET_FILE = "semantic-verification.packet.json"
VERDICT_FILE = "semantic-verdict.accepted.json"
SELECTION_FILE = "selection.claim.json"
SELECTION_BACKUP_FILE = "selection.claim.backup.json"
SELECTION_RECOVERY_MARKER = "_selection_recovery_from_backup"
REPORT_FILE = "report.json"
LOCK_FILE = "gate.lock"
DISPATCH_LOCK_FILE = "dispatch.lock"
RESERVED_FILES = {
    STATE_FILE,
    DETECTION_FILE,
    REPAIR_PACKET_FILE,
    GUIDED_MARKER_FILE,
    REQUEST_FILE,
    SOURCE_FILE,
    D0_FILE,
    BACKUP_FILE,
    REPAIR_FILE,
    D1_FILE,
    VERIFICATION_PACKET_FILE,
    VERDICT_FILE,
    SELECTION_FILE,
    SELECTION_BACKUP_FILE,
    REPORT_FILE,
    LOCK_FILE,
    DISPATCH_LOCK_FILE,
}

PROTECTIVE_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "inference-disclaimer",
        re.compile(
            r"(?:尚|仍|还|目前)?(?:不能|无法|不足以|不宜|不得以)(?:仅凭|单凭|据此|直接据此|由此)?"
            r"[^。！？\n]{0,70}(?:推定|判断|认定|说明|证明|得出|形成|确定|比较|作为[^。！？\n]{0,16}依据)"
        ),
    ),
    (
        "writing-self-certification",
        re.compile(r"不(?:将|把)[^。！？\n]{1,80}(?:写成|表述为|认定为|作为)[^。！？\n]{0,40}"),
    ),
    (
        "writing-self-certification",
        re.compile(r"不(?:直接)?与[^。！？\n]{1,80}(?:混用|等同)|不(?:直接)?等同于[^。！？\n]{1,80}"),
    ),
    (
        "scope-self-certification",
        re.compile(
            r"(?:为确保[^。！？\n]{0,20}边界清晰[，,])?"
            r"(?:本次|本报告|本说明|本纪要)[^。！？\n]{0,45}(?:不涉及|不对)[^。！？\n]{1,90}"
        ),
    ),
    (
        "scope-self-certification",
        re.compile(r"不对[^。！？\n]{1,80}(?:作出|预设)[^。！？\n]{0,40}(?:结论|安排|决定)"),
    ),
    (
        "scope-self-certification",
        re.compile(
            r"(?:本次)?(?:会议|专题会)[^。！？\n]{0,30}未(?:就|对)?[^。！？\n]{0,60}"
            r"(?:作出|形成|确定)[^。！？\n]{0,24}(?:结论|决定|安排|意见)"
        ),
    ),
    (
        "unanchored-unresolved-conclusion",
        re.compile(
            r"(?:尚未|仍未|暂未|还未|未(?!对|就))[^。！？\n]{0,24}"
            r"形成[^。！？\n]{0,28}(?:结论|决定|意见)"
        ),
    ),
    (
        "multi-object-pending-tail",
        re.compile(
            r"[^。！？\n]{1,48}(?:、|以及|和)[^。！？\n]{1,40}"
            r"(?:尚未|仍未|暂未|还未|未)(?:确定|明确|核定|形成)"
        ),
    ),
    (
        "unsupported-negative-claim",
        re.compile(r"(?:未|没有)(?:发生|出现|发现)[^。！？\n]{1,60}"),
    ),
    (
        "gap-state-narration",
        re.compile(
            r"(?:尚未|仍未|暂未|还未|未)[^。！？\n]{0,50}"
            r"(?:确定|明确|形成)[^。！？\n]{0,32}"
            r"(?:需|须|建议)(?:补充|补全|完善|提供)"
        ),
    ),
    (
        "questioned-unresolved",
        re.compile(r"是否[^。！？\n]{1,80}(?:尚未形成结论|未形成结论|尚未确定|仍无法确定)"),
    ),
    (
        "material-reading-narration",
        re.compile(
            r"(?:现有|已有|已给|所给|用户(?:已)?提供的|上述)(?:资料|材料|信息|内容)"
            r"(?:仅|只|未|没有|尚未|不足以|无法)[^。！？\n]{0,35}"
            r"(?:反映|说明|提供|支持|明确|确认|判断|形成)"
        ),
    ),
    (
        "material-reading-narration",
        re.compile(
            r"材料(?:中)?(?:仅载明|未提供)[^。！？\n]{0,35}"
            r"(?:正文|本(?:报告|通报|纪要)|文章|正式报送|落款|请(?:补充|提供)|建议补充|完善)"
        ),
    ),
    (
        "material-reading-narration",
        re.compile(
            r"(?<=[，,：:；;])(?:材料|资料|信息|内容)(?:中)?"
            r"(?:已|未|没有|仅|只|尚未)(?:明确|反映|记载|载明|提供|说明|确认)"
            r"[^。！？\n]{0,80}"
        ),
    ),
    (
        "material-reading-narration",
        re.compile(
            r"[^。！？\n]{2,30}以(?:现有|上述)?(?:材料|资料|信息|内容)(?:所)?"
            r"(?:记载|载明|提供|反映)(?:的)?(?:情况|内容)?为准"
        ),
    ),
    (
        "writing-self-certification",
        re.compile(
            r"(?:据实|如实)反映[^。！？\n]{0,40}"
            r"不(?:作|做)[^。！？\n]{0,50}(?:分析|判断|推定|认定|结论)"
        ),
    ),
)

STATUS_MARKER = re.compile(r"(?:尚未|仍未|未形成|未确定|待研究|待评估|待核实|无法确定)")
SENTENCE_CLOSERS = "”’\"'）)]】》〉〕〗」』"
SENTENCE_RE = re.compile(
    r"[^。！？\n]+[。！？]?[" + re.escape(SENTENCE_CLOSERS) + r"]*"
)
NUMBER_RE = re.compile(r"(?<![A-Za-z])\d+(?:\.\d+)?%?(?![A-Za-z])")
STRUCTURED_COUNT_UNIT_ALTERNATIVES = (
    r"个接口实例|个工作日|个自然日|个月|台次|年度|年期|时段|小时|分钟|万元|"
    r"个|项|次|台|名|份|套|处|条|组|天|年|元"
)
CHINESE_QUANTITY_RE = re.compile(
    r"[零〇一二两三四五六七八九十百千万亿]+(?:"
    + STRUCTURED_COUNT_UNIT_ALTERNATIVES
    + r")"
)
LATIN_ID_RE = re.compile(r"(?<![A-Za-z0-9])[A-Za-z][A-Za-z0-9_.:/-]{1,}(?![A-Za-z0-9])")
QUOTE_RE = re.compile(r"“[^”\n]+”|《[^》\n]+》")
STRUCTURED_ANCHOR_UNIT = (
    r"(?:个百分点|"
    + STRUCTURED_COUNT_UNIT_ALTERNATIVES
    + r"|月|日|时|分|笔|%)"
)
STRUCTURED_HSPACE = r"[ \t\u00a0\u3000]*"
STRUCTURED_HORIZONTAL_SPACE_RE = re.compile(r"[ \t\u00a0\u3000]+")
STRUCTURED_RANGE_SEPARATOR = r"(?:至|到|—|–|-|~|～)"
STRUCTURED_TIME_TOKEN = (
    rf"\d{{1,2}}{STRUCTURED_HSPACE}时"
    rf"(?:{STRUCTURED_HSPACE}\d{{1,2}}{STRUCTURED_HSPACE}分)?"
)
STRUCTURED_FULL_DATE = (
    rf"(?:\d{{4}}{STRUCTURED_HSPACE}年{STRUCTURED_HSPACE})?"
    rf"\d{{1,2}}{STRUCTURED_HSPACE}月{STRUCTURED_HSPACE}"
    rf"\d{{1,2}}{STRUCTURED_HSPACE}日"
)
STRUCTURED_RANGE_END_DATE = (
    rf"(?:(?:\d{{4}}{STRUCTURED_HSPACE}年{STRUCTURED_HSPACE})?"
    rf"\d{{1,2}}{STRUCTURED_HSPACE}月{STRUCTURED_HSPACE})?"
    rf"\d{{1,2}}{STRUCTURED_HSPACE}日"
)
STRUCTURED_DATE_TIME_RANGE_RE = re.compile(
    STRUCTURED_FULL_DATE
    + STRUCTURED_HSPACE
    + STRUCTURED_TIME_TOKEN
    + STRUCTURED_HSPACE
    + STRUCTURED_RANGE_SEPARATOR
    + STRUCTURED_HSPACE
    + STRUCTURED_RANGE_END_DATE
    + STRUCTURED_HSPACE
    + STRUCTURED_TIME_TOKEN
)
STRUCTURED_DATE_TIME_RE = re.compile(
    STRUCTURED_FULL_DATE
    + rf"(?:{STRUCTURED_HSPACE}{STRUCTURED_RANGE_SEPARATOR}"
    + rf"{STRUCTURED_HSPACE}{STRUCTURED_RANGE_END_DATE})?"
    + rf"(?:{STRUCTURED_HSPACE}{STRUCTURED_TIME_TOKEN}"
    + rf"(?:{STRUCTURED_HSPACE}{STRUCTURED_RANGE_SEPARATOR}"
    + rf"{STRUCTURED_HSPACE}{STRUCTURED_TIME_TOKEN})?)?"
)
STRUCTURED_TIME_RE = re.compile(
    STRUCTURED_TIME_TOKEN
    + rf"(?:{STRUCTURED_HSPACE}{STRUCTURED_RANGE_SEPARATOR}"
    + rf"{STRUCTURED_HSPACE}{STRUCTURED_TIME_TOKEN})?"
)
STRUCTURED_NUMBER_RANGE_RE = re.compile(
    rf"\d+(?:\.\d+)?{STRUCTURED_HSPACE}{STRUCTURED_RANGE_SEPARATOR}"
    rf"{STRUCTURED_HSPACE}\d+(?:\.\d+)?{STRUCTURED_HSPACE}"
    + STRUCTURED_ANCHOR_UNIT
)
STRUCTURED_NUMBER_UNIT_RE = re.compile(
    rf"\d+(?:\.\d+)?{STRUCTURED_HSPACE}" + STRUCTURED_ANCHOR_UNIT
)
STRUCTURED_ANCHOR_PATTERNS = (
    (QUOTE_RE, False),
    (STRUCTURED_DATE_TIME_RANGE_RE, True),
    (STRUCTURED_DATE_TIME_RE, True),
    (STRUCTURED_TIME_RE, True),
    (STRUCTURED_NUMBER_RANGE_RE, True),
    (STRUCTURED_NUMBER_UNIT_RE, True),
    (CHINESE_QUANTITY_RE, False),
    (LATIN_ID_RE, False),
)
HEADING_RE = re.compile(
    r"^(?:[一二三四五六七八九十百]+[、.]|（[一二三四五六七八九十百]+）|\d+[、.]|附件(?:\d+)?[：:]?)"
)
RANGE_RE = re.compile(r"(\d{2,5})\s*(?:—|–|-|至|到|~|～)\s*(\d{2,5})\s*(?:字|字符)")
MIN_RE = re.compile(r"(?:不少于|不低于|至少)\s*(\d{2,5})\s*(?:字|字符)")
MAX_RE = re.compile(r"(?:不超过|不多于|最多|控制在)\s*(\d{2,5})\s*(?:字|字符)(?:以内)?")
POSITIVE_SETTLED_RE = re.compile(
    r"(?:已经|已)[^，。；！？\n]{0,8}(?:完成|解决|确定|决定|明确|同意|批准|实施|办结|恢复|形成)"
)
BARE_SETTLED_RE = re.compile(r"(?:确定|决定|明确|同意|批准|实施|形成)")
UNRESOLVED_TARGET_RE = re.compile(
    r"(?:是否|尚未|仍未|未(?:形成|确定|决定|明确|确认|核实)|"
    r"(?:尚|仍)?不能|无法|不足以|待(?:确认|核实|研究|评估|调查|观察)|"
    r"(?:正在|正)(?:组织)?(?:调查|排查|核查|诊断|处理|研究|推进))"
)
UNRESOLVED_PREFIX_CONTEXT_RE = re.compile(
    r"(?:是否|不|未|尚未|仍未|不能|尚不能|无法|不得|不宜|尚需|仍需|有待|待|正在|正)"
    r"[^，。；！？.!?]{0,10}$"
)
UNRESOLVED_SUFFIX_CONTEXT_RE = re.compile(
    r"^[^，。；！？.!?]{0,10}"
    r"(?:是否|尚未|仍未|不能|无法|尚需|仍需|有待|待|正在|正)"
)
NEGATING_PREFIX_RE = re.compile(r"(?:不|未|尚未|不能|不得|不把|不将)[^，。；！？\n]{0,8}$")
NEGATION_TOKEN_RE = re.compile(r"(?:没有|并非|尚未|不能|不得|不宜|无法|不足以|不把|不将|未|无|不)")
UNCERTAINTY_MARKER_RE = re.compile(
    r"(?:是否|尚未|仍未|未形成|未确定|未决定|未明确|未确认|未核实|"
    r"待(?:确认|核实|研究|评估|调查)|(?:正在|正)(?:组织)?(?:调查|排查|核查|诊断|处理|研究|推进))"
)
OPEN_CONDITION_RE = re.compile(
    r"(?:如果|即使|即便|倘若|假如|除非|无论|虽然|尽管|只要)|^若(?!干)"
)
GUIDED_MARKER_OPEN = "⟦OWG-DROP⟧"
GUIDED_MARKER_CLOSE = "⟦/OWG-DROP⟧"
GUIDED_MARKER_EXACT_RE = re.compile(r"⟦/?OWG-DROP⟧")
GUIDED_MARKER_NAME_RE = re.compile(
    r"OWG\s*-\s*(?:DROP|P0)", re.IGNORECASE
)
GUIDED_MARKER_FRAGMENT_RE = re.compile(
    r"(?:⟦\s*/?\s*OWG\s*-\s*(?:DROP|P0)\s*⟧|"
    r"/?OWG\s*-\s*(?:DROP|P0)\s*⟧|"
    r"⟦\s*/?\s*OWG\s*-\s*(?:DROP|P0)|"
    r"/?OWG\s*-\s*(?:DROP|P0))",
    re.IGNORECASE,
)
SEMANTIC_SENSITIVE_LABELS = {
    "gap-state-narration",
    "material-reading-narration",
    "multi-object-pending-tail",
    "questioned-unresolved",
    "peripheral-pending-cluster",
    "scope-self-certification",
    "unanchored-unresolved-conclusion",
    "unsupported-negative-claim",
}
PURE_PERIPHERAL_MATERIAL_RE = re.compile(
    r"(?:除[^，,。！？\n]{1,24}外[，,])?"
    r"(?:材料|资料|信息|内容)(?:中)?(?:未|没有)(?:反映|说明)"
    r"(?:其他|其余|更多)[^，,；;。！？\n]*"
)
PURE_WRITING_SELF_CERT_RE = re.compile(
    r"(?:上述|有关|前述)?(?:情况|事项|内容)"
    r"(?:在)?(?:本报告|本通报|本纪要|本说明|本文)(?:中)?"
    r"(?:据实|如实)?(?:反映|记录)[，,]"
    r"不(?:作|做)[^。！？\n]{0,60}(?:分析|判断|推定|认定|结论)"
)
SEMANTIC_CHECKS = (
    "no_new_fact_action_or_actor",
    "decision_and_unresolved_state_preserved",
    "necessary_content_preserved",
    "p0_expression_removed_or_reduced",
    "genre_structure_and_usability_preserved",
)
GUIDED_SEMANTIC_CHECK = "guided_marker_scope_safe"


def _semantic_checks_for_state(state: dict[str, Any]) -> tuple[str, ...]:
    if state.get("guided_marker_sha256") is not None:
        return (*SEMANTIC_CHECKS, GUIDED_SEMANTIC_CHECK)
    return SEMANTIC_CHECKS


@dataclass(frozen=True)
class Finding:
    finding_id: str
    labels: tuple[str, ...]
    line: int
    target: str
    source_exact: bool
    request_exact: bool
    span_start: int
    span_end: int


@dataclass(frozen=True)
class CandidateResult:
    selected: str
    reason: str
    text: str


@dataclass(frozen=True)
class GuidedMarker:
    marker_id: str
    target: str
    target_sha256: str
    span_start: int
    span_end: int
    line: int


@dataclass(frozen=True)
class GuidedDraft:
    raw_sha256: str
    fallback_d0: str
    parse_status: str
    markers: tuple[GuidedMarker, ...]
    errors: tuple[str, ...]

    def sidecar(self) -> dict[str, Any]:
        return {
            "schema_version": GUIDED_MARKER_SCHEMA_VERSION,
            "parse_status": self.parse_status,
            "input_draft_sha256": self.raw_sha256,
            "d0_sha256": sha256_text(self.fallback_d0),
            "marker_count": len(self.markers),
            "markers": [asdict(marker) for marker in self.markers],
            "errors": list(self.errors),
        }


class GateInputError(ValueError):
    """Raised when a transaction cannot safely acquire a complete D0."""


class TransactionBusyError(RuntimeError):
    """Raised when another process owns the transaction lock."""


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def normalized_text(text: str) -> str:
    return re.sub(r"[^0-9A-Za-z\u4e00-\u9fff]+", "", text)


REQUEST_STATUS_FILLER_RE = re.compile(r"(?:目前|现阶段|当前|事项|亦|尚|仍|均)")


def _request_anchors_unresolved_replacement(replacement: str, request: str) -> bool:
    """Accept only an unresolved status restatement already present in the request."""

    if not request or not UNCERTAINTY_MARKER_RE.search(replacement):
        return False
    clauses = [part for part in re.split(r"[；;。！？!?]", replacement) if part.strip()]
    status_clause = clauses[-1] if clauses else replacement
    replacement_core = REQUEST_STATUS_FILLER_RE.sub("", normalized_text(status_clause))
    request_core = REQUEST_STATUS_FILLER_RE.sub("", normalized_text(request))
    if len(replacement_core) >= 6 and replacement_core in request_core:
        return True

    # A request may bind one unresolved status to several coordinated topics.
    # Permit a repair to retain a strict subset only when every named topic and
    # the same status phrase are already present in the request.
    status = "未形成结论"
    if status not in replacement_core or status not in request_core:
        return False
    subject = replacement_core.split(status, 1)[0]
    subject = re.sub(r"^(?:对于|有关|关于)", "", subject)
    topics = [part for part in re.split(r"(?:、|和|与|及)", subject) if len(part) >= 2]
    if not 1 <= len(topics) <= 4:
        return False

    request_before_status = request.rsplit(status, 1)[0]
    request_status_clause = re.split(r"[。！？；;]", request_before_status)[-1]
    request_status_clause = REQUEST_STATUS_FILLER_RE.sub("", request_status_clause)
    request_status_clause = re.sub(r"^(?:对于|有关|关于)", "", request_status_clause)
    request_topics = [
        normalized_text(part)
        for part in re.split(r"(?:、|和|与|及)", request_status_clause)
        if len(normalized_text(part)) >= 2
    ]

    def topic_is_anchored(topic: str) -> bool:
        if topic in request_topics:
            return True
        for request_topic in request_topics:
            if len(request_topic) < 4 or not topic.endswith(request_topic):
                continue
            modifier = topic[: -len(request_topic)]
            if modifier and any(modifier in other for other in request_topics):
                return True
        return False

    return bool(request_topics) and all(topic_is_anchored(topic) for topic in topics)


def _has_guided_marker_token(text: str) -> bool:
    return bool(GUIDED_MARKER_NAME_RE.search(text))


def _strip_guided_marker_tokens(text: str) -> str:
    return GUIDED_MARKER_FRAGMENT_RE.sub("", text)


def _parse_guided_draft(raw: str) -> GuidedDraft:
    raw_sha256 = sha256_text(raw)
    if not _has_guided_marker_token(raw):
        return GuidedDraft(raw_sha256, raw, "NONE", (), ())

    fallback = _strip_guided_marker_tokens(raw)
    errors: list[str] = []
    markers: list[GuidedMarker] = []
    output_parts: list[str] = []
    cursor = 0
    marker_start: int | None = None
    marker_clean_start: int | None = None

    residue = GUIDED_MARKER_EXACT_RE.sub("", raw)
    if _has_guided_marker_token(residue):
        errors.append("unknown_or_deprecated_marker_token")

    for token in GUIDED_MARKER_EXACT_RE.finditer(raw):
        literal = token.group(0)
        if literal == GUIDED_MARKER_OPEN:
            if marker_start is not None:
                errors.append("nested_marker")
                continue
            prefix = raw[cursor : token.start()]
            output_parts.append(prefix)
            marker_clean_start = sum(len(part) for part in output_parts)
            marker_start = token.end()
            cursor = token.end()
            continue

        if marker_start is None or marker_clean_start is None:
            errors.append("orphan_closing_marker")
            cursor = token.end()
            continue
        content = raw[marker_start : token.start()]
        output_parts.append(content)
        marker_id = f"G{len(markers) + 1:03d}"
        if not content.strip():
            errors.append(f"{marker_id}:empty_marker")
        if "\n" in content or "\r" in content:
            errors.append(f"{marker_id}:cross_paragraph_marker")
        markers.append(
            GuidedMarker(
                marker_id=marker_id,
                target=content,
                target_sha256=sha256_text(content),
                span_start=marker_clean_start,
                span_end=marker_clean_start + len(content),
                line="".join(output_parts[:-1]).count("\n") + 1,
            )
        )
        marker_start = None
        marker_clean_start = None
        cursor = token.end()

    if marker_start is not None:
        errors.append("unclosed_marker")
    else:
        output_parts.append(raw[cursor:])
    if len(markers) > MAX_FINDINGS:
        errors.append("marker_budget_exceeded")

    parsed_fallback = "".join(output_parts)
    if not errors and parsed_fallback != fallback:
        errors.append("marker_parse_mismatch")
    if errors or not markers:
        return GuidedDraft(raw_sha256, fallback, "INVALID", (), tuple(errors or ["marker_pair_missing"]))
    return GuidedDraft(raw_sha256, fallback, "VALID", tuple(markers), ())


def _bind_postdraft_marker_pass(original_d0: str, reviewed_draft: str) -> tuple[GuidedDraft, bool]:
    """Bind a mark-only review to the immutable pre-review D0."""

    parsed = _parse_guided_draft(reviewed_draft)
    errors = list(parsed.errors)
    if _has_guided_marker_token(original_d0):
        errors.append("pre_marker_d0_contains_marker")
    if parsed.fallback_d0 != original_d0:
        errors.append("postdraft_marker_pass_changed_text")
    if errors:
        return (
            GuidedDraft(
                parsed.raw_sha256,
                _strip_guided_marker_tokens(original_d0),
                "INVALID",
                (),
                tuple(dict.fromkeys(errors)),
            ),
            False,
        )
    return parsed, True


def _postdraft_marker_binding_mode(verified: bool | None) -> str:
    if verified is True:
        return "VERIFIED"
    if verified is False:
        return "INVALID"
    return "LEGACY"


def iter_sentence_spans(text: str) -> Iterable[tuple[int, str, int, int]]:
    offset = 0
    for line_number, line_with_ending in enumerate(text.splitlines(keepends=True), start=1):
        line = line_with_ending.rstrip("\r\n")
        for match in SENTENCE_RE.finditer(line):
            sentence = match.group(0).strip()
            if sentence:
                leading = len(match.group(0)) - len(match.group(0).lstrip())
                start = offset + match.start() + leading
                yield line_number, sentence, start, start + len(sentence)
        offset += len(line_with_ending)


def iter_sentences(text: str) -> Iterable[tuple[int, str]]:
    for line_number, sentence, _, _ in iter_sentence_spans(text):
        yield line_number, sentence


def _is_heading_line(line: str) -> bool:
    stripped = line.strip()
    return bool(HEADING_RE.match(stripped)) and not re.search(r"[。！？]$", stripped)


def _is_document_title_line(line: str) -> bool:
    """Distinguish a standalone title from a titleless first body paragraph."""

    stripped = line.strip().rstrip(SENTENCE_CLOSERS)
    return bool(stripped) and not re.search(r"[。！？]$", stripped)


def _leading_structure_marker(text: str) -> str:
    """Return the exact leading list/heading marker, if present."""

    match = HEADING_RE.match(text.strip())
    return match.group(0) if match else ""


def labels_for_sentence(sentence: str) -> set[str]:
    labels = {label for label, regex in PROTECTIVE_PATTERNS if regex.search(sentence)}
    if len(STATUS_MARKER.findall(sentence)) >= 2:
        labels.add("peripheral-pending-cluster")
    return labels


def _merge_exact_span_findings(
    findings: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Count one decision per exact draft span, preserving guided authority."""

    merged: list[dict[str, Any]] = []
    positions: dict[tuple[int, int, str], int] = {}
    for finding in findings:
        key = (
            finding["span_start"],
            finding["span_end"],
            finding["target"],
        )
        existing_index = positions.get(key)
        if existing_index is None:
            positions[key] = len(merged)
            merged.append(dict(finding))
            continue

        existing = merged[existing_index]
        if finding.get("guided_marker") is True:
            combined = dict(finding)
        else:
            combined = dict(existing)
        combined["labels"] = sorted(
            set(existing.get("labels", ())) | set(finding.get("labels", ()))
        )
        combined["source_exact"] = bool(
            existing.get("source_exact") or finding.get("source_exact")
        )
        combined["request_exact"] = bool(
            existing.get("request_exact") or finding.get("request_exact")
        )
        merged[existing_index] = combined
    return merged


def locate_candidates(
    request: str,
    draft: str,
    source: str = "",
    guided_marker_sidecar: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if not draft.strip():
        raise GateInputError("D0 must be a non-empty complete draft")

    findings: list[Finding] = []
    finding_number = 0
    lines = draft.splitlines()
    first_nonempty = next((line.strip() for line in lines if line.strip()), "")
    for line_number, sentence, span_start, span_end in iter_sentence_spans(draft):
        whole_line = lines[line_number - 1].strip()
        first_line_is_title = (
            whole_line == first_nonempty and _is_document_title_line(whole_line)
        )
        if whole_line == sentence and (first_line_is_title or _is_heading_line(whole_line)):
            continue
        labels = labels_for_sentence(sentence)
        if not labels:
            continue
        sentence_normalized = normalized_text(sentence)
        source_exact = bool(
            source and len(sentence_normalized) >= 8 and sentence.strip() in source
        )
        request_exact = bool(
            len(sentence_normalized) >= 8 and sentence.strip() in request
        )
        finding_number += 1
        findings.append(
            Finding(
                finding_id=f"P{finding_number:03d}",
                labels=tuple(sorted(labels)),
                line=line_number,
                target=sentence,
                source_exact=source_exact,
                request_exact=request_exact,
                span_start=span_start,
                span_end=span_end,
            )
        )

    serialized_findings: list[dict[str, Any]] = []
    for item in findings:
        serialized = asdict(item)
        serialized["labels"] = list(item.labels)
        serialized_findings.append(serialized)
    if guided_marker_sidecar is not None:
        markers = guided_marker_sidecar.get("markers")
        if (
            guided_marker_sidecar.get("schema_version") != GUIDED_MARKER_SCHEMA_VERSION
            or guided_marker_sidecar.get("parse_status") != "VALID"
            or guided_marker_sidecar.get("d0_sha256") != sha256_text(draft)
            or not isinstance(markers, list)
        ):
            raise GateInputError("guided marker sidecar is invalid")
        for marker in markers:
            if not isinstance(marker, dict):
                raise GateInputError("guided marker record is invalid")
            marker_id = marker.get("marker_id")
            target = marker.get("target")
            span_start = marker.get("span_start")
            span_end = marker.get("span_end")
            line = marker.get("line")
            if (
                not isinstance(marker_id, str)
                or not isinstance(target, str)
                or not target.strip()
                or not isinstance(span_start, int)
                or not isinstance(span_end, int)
                or not isinstance(line, int)
                or span_start < 0
                or span_end <= span_start
                or draft[span_start:span_end] != target
                or marker.get("target_sha256") != sha256_text(target)
            ):
                raise GateInputError("guided marker span is invalid")
            labels = sorted(labels_for_sentence(target) | {"guided-drop-marker"})
            serialized_findings.append(
                {
                    "finding_id": marker_id,
                    "labels": labels,
                    "line": line,
                    "target": target,
                    "source_exact": bool(
                        source
                        and len(normalized_text(target)) >= 8
                        and target.strip() in source
                    ),
                    "request_exact": bool(
                        len(normalized_text(target)) >= 8 and target.strip() in request
                    ),
                    "span_start": span_start,
                    "span_end": span_end,
                    "guided_marker": True,
                    "marker_id": marker_id,
                }
            )
        if len({item["finding_id"] for item in serialized_findings}) != len(
            serialized_findings
        ):
            raise GateInputError("guided marker finding id collides")
    serialized_findings = _merge_exact_span_findings(serialized_findings)
    return {
        "schema_version": SCHEMA_VERSION,
        "request_sha256": sha256_text(request),
        "source_sha256": sha256_text(source),
        "draft_sha256": sha256_text(draft),
        "revision_budget": MAX_REVISIONS,
        "verify_budget": MAX_VERIFICATIONS,
        "findings": serialized_findings,
        "guided_marker_sha256": (
            sha256_text(
                json.dumps(guided_marker_sidecar, ensure_ascii=False, indent=2) + "\n"
            )
            if guided_marker_sidecar is not None
            else None
        ),
    }


def _headings(text: str) -> list[str]:
    nonempty = [line.strip() for line in text.splitlines() if line.strip()]
    if not nonempty:
        return []
    headings = [nonempty[0]] if _is_document_title_line(nonempty[0]) else []
    headings.extend(line for line in nonempty[1:] if _is_heading_line(line))
    return headings


def _section_body_counts(text: str) -> list[int]:
    nonempty = [line.strip() for line in text.splitlines() if line.strip()]
    if not nonempty:
        return []
    counts = [0]
    section = 0
    for index, line in enumerate(nonempty):
        if index == 0 and _is_document_title_line(line):
            continue
        if _is_heading_line(line):
            section += 1
            counts.append(0)
            continue
        sentence_count = sum(1 for _ in SENTENCE_RE.finditer(line))
        counts[section] += max(1, sentence_count)
    return counts


def _body_length(text: str) -> int:
    nonempty = [line.strip() for line in text.splitlines() if line.strip()]
    if not nonempty:
        return 0
    body_start = 1 if _is_document_title_line(nonempty[0]) else 0
    body_lines = [line for line in nonempty[body_start:] if not _is_heading_line(line)]
    return len(normalized_text("\n".join(body_lines)))


def _length_bounds(request: str) -> tuple[int | None, int | None, str]:
    use_cjk = "中文字符" in request
    range_match = RANGE_RE.search(request)
    if range_match:
        return int(range_match.group(1)), int(range_match.group(2)), "cjk" if use_cjk else "nonspace"
    min_match = MIN_RE.search(request)
    max_match = MAX_RE.search(request)
    minimum = int(min_match.group(1)) if min_match else None
    maximum = int(max_match.group(1)) if max_match else None
    return minimum, maximum, "cjk" if use_cjk else "nonspace"


def _count_length(text: str, mode: str) -> int:
    if mode == "cjk":
        return len(re.findall(r"[\u3400-\u4dbf\u4e00-\u9fff]", text))
    return len(re.sub(r"\s+", "", text))


def _length_violation_distance(
    length: int, minimum: int | None, maximum: int | None
) -> int:
    below = max((minimum or 0) - length, 0) if minimum is not None else 0
    above = max(length - maximum, 0) if maximum is not None else 0
    return below + above


def _length_worsening_tolerance(
    draft_length: int, minimum: int | None, maximum: int | None
) -> int:
    """Allow a small local-review variance while still catching gross loss."""

    reference = maximum or minimum or draft_length
    return max(
        MIN_LENGTH_WORSENING_TOLERANCE,
        round(reference * LENGTH_WORSENING_TOLERANCE_RATIO),
    )


def _replacement_adds_sentence(text: str) -> bool:
    """Detect a second sentence without treating decimal/version dots as boundaries."""

    stripped = text.strip()
    numbered_prefix = HEADING_RE.match(stripped)
    closers = SENTENCE_CLOSERS
    for index, char in enumerate(stripped):
        if char not in "。！？.!?":
            continue
        suffix = stripped[index + 1 :].lstrip()
        while suffix and suffix[0] in closers:
            suffix = suffix[1:].lstrip()
        if not suffix:
            continue
        if char == "." and index > 0:
            if numbered_prefix is not None and index == numbered_prefix.end() - 1:
                continue
            previous = stripped[index - 1]
            following = stripped[index + 1]
            if (
                previous.isascii()
                and previous.isalnum()
                and following.isascii()
                and following.isalnum()
            ):
                continue
        return True
    return False


def _hard_anchor_counters(text: str) -> tuple[Counter[str], ...]:
    return (
        Counter(NUMBER_RE.findall(text)),
        Counter(CHINESE_QUANTITY_RE.findall(text)),
        Counter(LATIN_ID_RE.findall(text)),
        Counter(QUOTE_RE.findall(text)),
    )


@dataclass(frozen=True)
class StructuredAnchorOccurrence:
    canonical: str
    span_start: int
    span_end: int


def _structured_anchor_occurrences(text: str) -> list[StructuredAnchorOccurrence]:
    candidates: list[StructuredAnchorOccurrence] = []
    for pattern, normalize_horizontal_space in STRUCTURED_ANCHOR_PATTERNS:
        for match in pattern.finditer(text):
            matched_text = match.group(0)
            candidates.append(
                StructuredAnchorOccurrence(
                    canonical=(
                        STRUCTURED_HORIZONTAL_SPACE_RE.sub("", matched_text)
                        if normalize_horizontal_space
                        else matched_text
                    ),
                    span_start=match.start(),
                    span_end=match.end(),
                )
            )
    candidates.sort(
        key=lambda item: (
            -(item.span_end - item.span_start),
            item.span_start,
            item.span_end,
            item.canonical,
        )
    )
    selected: list[StructuredAnchorOccurrence] = []
    for candidate in candidates:
        if any(
            candidate.span_start < existing.span_end
            and existing.span_start < candidate.span_end
            for existing in selected
        ):
            continue
        selected.append(candidate)
    return sorted(selected, key=lambda item: (item.span_start, item.span_end))


def _hard_anchor_spans(text: str) -> list[tuple[int, int]]:
    spans: list[tuple[int, int]] = []
    for pattern in (NUMBER_RE, CHINESE_QUANTITY_RE, LATIN_ID_RE, QUOTE_RE):
        spans.extend((match.start(), match.end()) for match in pattern.finditer(text))
    return spans


def _guided_delete_required_anchor_phrases(target: str) -> set[str] | None:
    structured = _structured_anchor_occurrences(target)
    required: set[str] = set()
    for span_start, span_end in _hard_anchor_spans(target):
        covering = [
            occurrence
            for occurrence in structured
            if occurrence.span_start <= span_start and span_end <= occurrence.span_end
        ]
        if not covering:
            return None
        required.add(
            max(
                covering,
                key=lambda item: item.span_end - item.span_start,
            ).canonical
        )
    return required


def _hard_anchor_counter_sum(texts: Iterable[str]) -> tuple[Counter[str], ...]:
    totals = tuple(Counter() for _ in range(4))
    for text in texts:
        for total, current in zip(totals, _hard_anchor_counters(text)):
            total.update(current)
    return totals


def _spans_intersect(
    span_start: int, span_end: int, changed_spans: Iterable[tuple[int, int]]
) -> bool:
    return any(
        span_start < changed_end and changed_start < span_end
        for changed_start, changed_end in changed_spans
    )


def _compact_extract(text: str) -> str:
    return re.sub(r"\s+", "", text.strip())


def _is_pure_protective_text(text: str) -> bool:
    core = text.strip().rstrip("。！？").strip()
    if not core or any(delimiter in core for delimiter in "，,；;"):
        return False
    return _protective_start(core) == 0


def _is_pure_process_self_certification(text: str) -> bool:
    core = text.strip().rstrip("。！？").strip()
    if not core or any(_hard_anchor_counters(core)):
        return False
    return bool(
        PURE_PERIPHERAL_MATERIAL_RE.fullmatch(core)
        or PURE_WRITING_SELF_CERT_RE.fullmatch(core)
    )


def _is_safe_prefix_replacement(
    finding: dict[str, Any], target: str, replacement: str
) -> bool:
    if replacement == "":
        return True
    labels = set(finding.get("labels") or [])
    if labels & SEMANTIC_SENSITIVE_LABELS:
        return False
    replacement_core = replacement.strip().rstrip("。！？；;").strip()
    if not replacement_core:
        return False
    if OPEN_CONDITION_RE.search(replacement_core):
        return False
    target_stripped = target.strip()
    if not target_stripped.startswith(replacement_core):
        return False
    remainder = target_stripped[len(replacement_core) :].lstrip()
    if not remainder or remainder[0] not in "，,；;。！？":
        return False
    protective_suffix = remainder[1:].lstrip()
    return _is_pure_protective_text(protective_suffix)


def _protective_start(sentence: str) -> int | None:
    starts = [match.start() for _, regex in PROTECTIVE_PATTERNS if (match := regex.search(sentence))]
    return min(starts) if starts else None


def _safe_full_deletion(finding: dict[str, Any], target: str) -> bool:
    if finding.get("guided_marker") is True:
        return bool(target.strip()) and "\n" not in target and "\r" not in target
    if _is_pure_process_self_certification(target):
        return True
    labels = set(finding.get("labels") or [])
    if labels & SEMANTIC_SENSITIVE_LABELS:
        return False
    return _is_pure_protective_text(target)


def _guided_span_is_independent_sentence(
    draft: str, finding: dict[str, Any], target: str
) -> bool:
    span_start = finding.get("span_start")
    span_end = finding.get("span_end")
    if (
        not isinstance(span_start, int)
        or not isinstance(span_end, int)
        or span_start < 0
        or span_end <= span_start
        or draft[span_start:span_end] != target
    ):
        return False

    core = target.strip()
    if not core or "\n" in target or "\r" in target:
        return False
    while core and core[-1] in "”’）》】〕」』":
        core = core[:-1].rstrip()
    if not core or core[-1] not in "。！？!?":
        return False

    prefix = draft[:span_start]
    line_start = max(prefix.rfind("\n"), prefix.rfind("\r")) + 1
    same_line_prefix = prefix[line_start:].strip()
    if same_line_prefix:
        boundary = prefix.rstrip()
        while boundary and boundary[-1] in "”’）》】〕」』":
            boundary = boundary[:-1].rstrip()
        if not boundary or boundary[-1] not in "。！？!?":
            return False

    suffix = draft[span_end:]
    next_text = suffix.lstrip(" \t")
    if next_text.startswith(("，", ",", "；", ";", "：", ":")):
        return False
    return True


def _delete_contract(
    finding: dict[str, Any], draft: str
) -> tuple[bool, str | None]:
    target = finding.get("target")
    if not isinstance(target, str) or not target.strip():
        return False, "invalid_delete_target"
    guided_marker = finding.get("guided_marker") is True
    if finding.get("source_exact") is True and not guided_marker:
        return False, "source_explicit_sentence_is_read_only"
    if guided_marker:
        if not _guided_span_is_independent_sentence(draft, finding, target):
            return False, "guided_span_not_independent_sentence"
        return True, None
    if _is_pure_process_self_certification(target):
        return True, None
    labels = set(finding.get("labels") or [])
    if labels & SEMANTIC_SENSITIVE_LABELS:
        return False, "semantic_sensitive_finding"
    if not _is_pure_protective_text(target):
        return False, "mixed_required_and_protective_text"
    if any(_hard_anchor_counters(target)):
        return False, "hard_anchor_change_requires_guided_proof"
    return True, None


def _finding_action_contract(
    finding: dict[str, Any], draft: str
) -> tuple[list[str], str | None]:
    guided_marker = finding.get("guided_marker") is True
    if finding.get("source_exact") is True and not guided_marker:
        return [DECISION_KEEP], "source_explicit_sentence_is_read_only"
    target = finding.get("target")
    if (
        guided_marker
        and isinstance(target, str)
        and any(_hard_anchor_counters(target))
        and _guided_delete_required_anchor_phrases(target) is None
    ):
        return [DECISION_KEEP, DECISION_REWRITE], "guided_delete_hard_anchor_unstructured"
    delete_allowed, block_reason = _delete_contract(finding, draft)
    allowed = [DECISION_KEEP, DECISION_REWRITE]
    if delete_allowed:
        allowed.insert(1, DECISION_DELETE)
    return allowed, block_reason


def _has_unlicensed_settled_status(replacement: str, authority: str) -> bool:
    authority_normalized = normalized_text(authority)
    replacement_normalized = normalized_text(replacement)
    for match in POSITIVE_SETTLED_RE.finditer(replacement):
        prefix = replacement[max(0, match.start() - 12) : match.start()]
        if NEGATING_PREFIX_RE.search(prefix):
            continue
        if replacement_normalized and replacement_normalized in authority_normalized:
            continue
        return True
    return False


def _turns_unresolved_into_settled(
    target: str, replacement: str, authority: str
) -> bool:
    if not UNRESOLVED_TARGET_RE.search(target):
        return False
    replacement_normalized = normalized_text(replacement)
    if replacement_normalized and replacement_normalized in normalized_text(authority):
        return False
    for match in BARE_SETTLED_RE.finditer(replacement):
        prefix = replacement[max(0, match.start() - 14) : match.start()]
        suffix = replacement[match.end() : match.end() + 14]
        if UNRESOLVED_PREFIX_CONTEXT_RE.search(prefix):
            continue
        if UNRESOLVED_SUFFIX_CONTEXT_RE.search(suffix):
            continue
        return True
    return False


def _drops_clause_negation(target: str, replacement: str) -> bool:
    if not replacement:
        return False
    replacement_core = replacement.strip().rstrip("。！？；;").strip()
    start = target.find(replacement_core)
    if start < 0:
        return False
    clause_prefix = re.split(r"[，,；;。！？]", target[:start])[-1]
    return bool(NEGATION_TOKEN_RE.search(clause_prefix)) and not bool(
        NEGATION_TOKEN_RE.search(replacement_core)
    )


def _drops_uncertainty(target: str, replacement: str) -> bool:
    return bool(UNCERTAINTY_MARKER_RE.search(target)) and not bool(
        UNCERTAINTY_MARKER_RE.search(replacement)
    )


def evaluate_candidate(
    request: str,
    source: str,
    draft: str,
    run_id: str,
    detection: dict[str, Any] | None,
    repair_packet: dict[str, Any] | None,
    guided_marker_sidecar: dict[str, Any] | None = None,
) -> CandidateResult:
    """Apply and verify one bounded repair packet without mutating D0."""

    if not draft.strip():
        raise GateInputError("D0 must be a non-empty complete draft")
    if not isinstance(detection, dict):
        return CandidateResult("D0", "detection_missing_or_invalid", draft)

    expected_detection = locate_candidates(
        request,
        draft,
        source,
        guided_marker_sidecar=guided_marker_sidecar,
    )
    expected_detection["run_id"] = run_id
    if detection != expected_detection:
        return CandidateResult("D0", "detection_content_mismatch", draft)
    findings = detection.get("findings")
    if not isinstance(findings, list) or not findings:
        return CandidateResult("D0", "no_review_candidate", draft)

    if not isinstance(repair_packet, dict):
        return CandidateResult("D0", "repair_missing_or_invalid", draft)
    if repair_packet.get("schema_version") != SCHEMA_VERSION:
        return CandidateResult("D0", "repair_schema_mismatch", draft)
    if repair_packet.get("run_id") != run_id:
        return CandidateResult("D0", "repair_run_mismatch", draft)
    if repair_packet.get("request_sha256") != sha256_text(request):
        return CandidateResult("D0", "repair_input_hash_mismatch", draft)
    if repair_packet.get("source_sha256") != sha256_text(source):
        return CandidateResult("D0", "repair_input_hash_mismatch", draft)
    if repair_packet.get("draft_sha256") != sha256_text(draft):
        return CandidateResult("D0", "repair_input_hash_mismatch", draft)
    if repair_packet.get("guided_marker_sha256") != detection.get(
        "guided_marker_sha256"
    ):
        return CandidateResult("D0", "repair_guided_marker_hash_mismatch", draft)
    if repair_packet.get("revision_count") != 1:
        return CandidateResult("D0", "revision_budget_violation", draft)

    repairs = repair_packet.get("repairs")
    if not isinstance(repairs, list) or not repairs:
        return CandidateResult("D0", "no_confirmed_repair", draft)
    repair_mode = repair_packet.get("repair_mode", REPAIR_MODE_EXTRACT)
    if repair_mode not in {
        REPAIR_MODE_EXTRACT,
        REPAIR_MODE_REWRITE_SENTENCE,
        REPAIR_MODE_DECISIONS,
    }:
        return CandidateResult("D0", "repair_mode_invalid", draft)
    if repair_mode == REPAIR_MODE_REWRITE_SENTENCE and len(repairs) != 1:
        return CandidateResult("D0", "sentence_rewrite_budget_violation", draft)
    if repair_mode == REPAIR_MODE_DECISIONS:
        if len(findings) > MAX_FINDINGS:
            return CandidateResult("D0", "finding_budget_exceeded", draft)
        if len(repairs) != len(findings):
            return CandidateResult("D0", "decision_packet_incomplete", draft)

    finding_by_id: dict[str, dict[str, Any]] = {}
    for finding in findings:
        if not isinstance(finding, dict) or not isinstance(finding.get("finding_id"), str):
            return CandidateResult("D0", "detection_finding_invalid", draft)
        finding_id = finding["finding_id"]
        if finding_id in finding_by_id:
            return CandidateResult("D0", "duplicate_finding_id", draft)
        finding_by_id[finding_id] = finding

    seen_repairs: set[str] = set()
    repair_item_hard_anchor_changed = False
    guided_anchor_deletions: list[tuple[int, int, str]] = []
    request_anchored_anchor_changes: list[str] = []
    candidate = draft
    operations: list[tuple[int, int, str]] = []
    authority = source
    for repair in repairs:
        if not isinstance(repair, dict):
            return CandidateResult("D0", "repair_item_invalid", draft)
        if repair_mode == REPAIR_MODE_DECISIONS and set(repair) != {
            "finding_id",
            "target",
            "decision",
            "replacement",
        }:
            return CandidateResult("D0", "decision_item_schema_mismatch", draft)
        finding_id = repair.get("finding_id")
        target = repair.get("target")
        replacement = repair.get("replacement")
        if not isinstance(finding_id, str) or finding_id in seen_repairs:
            return CandidateResult("D0", "duplicate_or_missing_repair_id", draft)
        seen_repairs.add(finding_id)
        finding = finding_by_id.get(finding_id)
        if finding is None or target != finding.get("target"):
            return CandidateResult("D0", "repair_target_not_detected", draft)
        if not isinstance(target, str) or not isinstance(replacement, str):
            return CandidateResult("D0", "repair_text_invalid", draft)
        guided_marker = finding.get("guided_marker") is True
        decision: str | None = None
        if repair_mode == REPAIR_MODE_DECISIONS:
            decision = repair.get("decision")
            if decision not in {DECISION_KEEP, DECISION_DELETE, DECISION_REWRITE}:
                return CandidateResult("D0", "decision_invalid", draft)
            allowed_decisions, decision_block_reason = _finding_action_contract(
                finding, draft
            )
            if decision not in allowed_decisions:
                return CandidateResult(
                    "D0",
                    decision_block_reason or "decision_not_allowed_for_finding",
                    draft,
                )
            if decision == DECISION_KEEP:
                if replacement != target:
                    return CandidateResult("D0", "keep_decision_changed_text", draft)
                continue
            if finding.get("source_exact") is True and not guided_marker:
                return CandidateResult("D0", "source_explicit_sentence_is_read_only", draft)
            effective_mode = (
                REPAIR_MODE_EXTRACT if decision == DECISION_DELETE else REPAIR_MODE_REWRITE_SENTENCE
            )
            if decision == DECISION_DELETE and replacement != "":
                return CandidateResult("D0", "delete_decision_must_be_empty", draft)
            if decision == DECISION_REWRITE and not normalized_text(replacement):
                return CandidateResult("D0", "rewrite_decision_must_be_nonempty", draft)
        else:
            if finding.get("source_exact") is True and not guided_marker:
                return CandidateResult("D0", "source_explicit_sentence_is_read_only", draft)
            effective_mode = repair_mode
        if guided_marker:
            span_start = finding.get("span_start")
            span_end = finding.get("span_end")
            if (
                not isinstance(span_start, int)
                or not isinstance(span_end, int)
                or span_start < 0
                or span_end <= span_start
                or draft[span_start:span_end] != target
            ):
                return CandidateResult("D0", "guided_marker_span_mismatch", draft)
        else:
            if draft.count(target) != 1:
                return CandidateResult("D0", "repair_target_not_unique", draft)
            span_start = draft.index(target)
            span_end = span_start + len(target)
        target_marker = _leading_structure_marker(target)
        if target_marker and _leading_structure_marker(replacement) != target_marker:
            return CandidateResult("D0", "list_marker_changed", draft)
        if replacement != "".join(replacement.splitlines()):
            return CandidateResult("D0", "replacement_crosses_paragraph_boundary", draft)
        if _replacement_adds_sentence(replacement):
            return CandidateResult("D0", "replacement_adds_sentences", draft)
        if effective_mode == REPAIR_MODE_REWRITE_SENTENCE and not normalized_text(replacement):
            return CandidateResult("D0", "sentence_rewrite_must_be_nonempty", draft)
        if replacement == "":
            if effective_mode != REPAIR_MODE_EXTRACT:
                return CandidateResult("D0", "sentence_rewrite_must_be_nonempty", draft)
            if not _safe_full_deletion(finding, target):
                return CandidateResult("D0", "full_deletion_not_proven_safe", draft)
        elif effective_mode == REPAIR_MODE_EXTRACT:
            if not _is_safe_prefix_replacement(finding, target, replacement):
                return CandidateResult("D0", "replacement_not_safe_prefix", draft)
        elif OPEN_CONDITION_RE.search(replacement.strip()):
            return CandidateResult("D0", "sentence_rewrite_opens_condition", draft)
        if _has_unlicensed_settled_status(
            replacement, authority
        ) or (
            effective_mode == REPAIR_MODE_REWRITE_SENTENCE
            and _turns_unresolved_into_settled(target, replacement, authority)
        ):
            return CandidateResult("D0", "replacement_strengthens_status", draft)
        if effective_mode == REPAIR_MODE_EXTRACT:
            if not guided_marker and _drops_uncertainty(target, replacement):
                return CandidateResult("D0", "replacement_drops_uncertainty", draft)
            if not guided_marker and _drops_clause_negation(target, replacement):
                return CandidateResult("D0", "replacement_drops_negation", draft)
        if labels_for_sentence(replacement) and not _request_anchors_unresolved_replacement(
            replacement, request
        ):
            return CandidateResult("D0", "replacement_retains_protective_pattern", draft)
        if _hard_anchor_counters(target) != _hard_anchor_counters(replacement):
            if (
                repair_mode == REPAIR_MODE_DECISIONS
                and guided_marker
                and decision == DECISION_DELETE
            ):
                guided_anchor_deletions.append((span_start, span_end, target))
            else:
                repair_item_hard_anchor_changed = True
                request_anchored_anchor_changes.append(target)
        operations.append((span_start, span_end, replacement))

    ordered_operations = sorted(operations, key=lambda item: item[0])
    for previous, current in zip(ordered_operations, ordered_operations[1:]):
        if current[0] < previous[1]:
            return CandidateResult("D0", "repair_spans_overlap", draft)
    for span_start, span_end, replacement in reversed(ordered_operations):
        candidate = candidate[:span_start] + replacement + candidate[span_end:]

    if not candidate.strip() or candidate == draft:
        return CandidateResult("D0", "empty_or_unchanged_candidate", draft)
    if repair_mode == REPAIR_MODE_DECISIONS and seen_repairs != set(finding_by_id):
        return CandidateResult("D0", "decision_packet_incomplete", draft)
    draft_anchor_counters = _hard_anchor_counters(draft)
    candidate_anchor_counters = _hard_anchor_counters(candidate)
    if candidate_anchor_counters != draft_anchor_counters:
        if request_anchored_anchor_changes:
            for before, after in zip(draft_anchor_counters, candidate_anchor_counters):
                if any(
                    value not in before and count > 0
                    for value, count in after.items()
                ):
                    return CandidateResult("D0", "hard_anchor_added", draft)
            candidate_anchor_phrases = {
                occurrence.canonical
                for occurrence in _structured_anchor_occurrences(candidate)
            }
            for target in request_anchored_anchor_changes:
                required = _guided_delete_required_anchor_phrases(target)
                if required is None:
                    return CandidateResult("D0", "hard_anchor_change_unstructured", draft)
                if not required.issubset(candidate_anchor_phrases):
                    return CandidateResult(
                        "D0", "hard_anchor_change_not_redundant", draft
                    )
            repair_item_hard_anchor_changed = False
        elif not guided_anchor_deletions:
            return CandidateResult("D0", "hard_anchor_counter_changed", draft)
        else:
            changed_spans = [
                (span_start, span_end) for span_start, span_end, _ in operations
            ]
            surviving_anchor_phrases = {
                occurrence.canonical
                for occurrence in _structured_anchor_occurrences(draft)
                if not _spans_intersect(
                    occurrence.span_start,
                    occurrence.span_end,
                    changed_spans,
                )
            }
            authority_anchor_phrases = {
                occurrence.canonical
                for authority_text in (request, source)
                for occurrence in _structured_anchor_occurrences(authority_text)
            }
            for _, _, target in guided_anchor_deletions:
                required = _guided_delete_required_anchor_phrases(target)
                if required is None:
                    return CandidateResult(
                        "D0", "guided_delete_hard_anchor_unstructured", draft
                    )
                if not required.issubset(
                    surviving_anchor_phrases
                ) or not required.issubset(authority_anchor_phrases):
                    return CandidateResult(
                        "D0", "guided_delete_hard_anchor_not_redundant", draft
                    )
            permitted_removals = _hard_anchor_counter_sum(
                target for _, _, target in guided_anchor_deletions
            )
            for before, after, permitted in zip(
                draft_anchor_counters,
                candidate_anchor_counters,
                permitted_removals,
            ):
                if after - before:
                    return CandidateResult("D0", "hard_anchor_added", draft)
                if before - after != permitted:
                    return CandidateResult(
                        "D0", "hard_anchor_reduction_not_authorized", draft
                    )
    if repair_item_hard_anchor_changed:
        return CandidateResult("D0", "repair_item_hard_anchor_changed", draft)
    if _headings(candidate) != _headings(draft):
        return CandidateResult("D0", "heading_or_title_changed", draft)

    before_sections = _section_body_counts(draft)
    after_sections = _section_body_counts(candidate)
    if len(before_sections) != len(after_sections) or any(
        before > 0 and after == 0 for before, after in zip(before_sections, after_sections)
    ):
        return CandidateResult("D0", "body_or_section_emptied", draft)
    before_body_length = _body_length(draft)
    after_body_length = _body_length(candidate)
    if before_body_length <= 0 or after_body_length < before_body_length * MIN_BODY_RETAIN_RATIO:
        return CandidateResult("D0", "body_content_collapsed", draft)

    minimum, maximum, count_mode = _length_bounds(request)
    draft_length = _count_length(draft, count_mode)
    candidate_length = _count_length(candidate, count_mode)
    expansion_allowance = _length_worsening_tolerance(
        draft_length, minimum, maximum
    )
    if candidate_length > draft_length + expansion_allowance:
        return CandidateResult("D0", "candidate_length_expansion_exceeded", draft)
    draft_violation = _length_violation_distance(draft_length, minimum, maximum)
    candidate_violation = _length_violation_distance(candidate_length, minimum, maximum)
    bounded_p0_shortening = (
        repair_mode == REPAIR_MODE_DECISIONS
        and minimum is not None
        and draft_length < minimum
        and candidate_length < draft_length
    )
    if (
        not bounded_p0_shortening
        and candidate_violation
        > draft_violation + _length_worsening_tolerance(draft_length, minimum, maximum)
    ):
        return CandidateResult("D0", "prompt_length_compliance_worsened", draft)
    if repair_mode == REPAIR_MODE_DECISIONS:
        reason = "verified_bounded_decision_packet"
    else:
        reason = (
            "verified_single_sentence_rewrite"
            if repair_mode == REPAIR_MODE_REWRITE_SENTENCE
            else "verified_single_extractive_revision"
        )
    return CandidateResult("D1", reason, candidate)


def read_text(path: str | Path) -> str:
    return Path(path).read_text(encoding="utf-8")


def read_json(path: str | Path | None) -> dict[str, Any] | None:
    if not path:
        return None
    try:
        raw = Path(path).read_bytes()
        if len(raw) > MAX_JSON_BYTES:
            return None
        value = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError, RecursionError):
        return None
    return value if isinstance(value, dict) else None


def atomic_write_text(path: str | Path, text: str) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    temp_name: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="\n",
            prefix=f".{target.name}.",
            suffix=".tmp",
            dir=target.parent,
            delete=False,
        ) as handle:
            temp_name = handle.name
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, target)
        temp_name = None
    finally:
        if temp_name:
            try:
                Path(temp_name).unlink()
            except OSError:
                pass


def atomic_write_json(path: str | Path, value: dict[str, Any]) -> None:
    atomic_write_text(path, json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def _encode_snapshot(text: str) -> str:
    return base64.b64encode(text.encode("utf-8")).decode("ascii")


def _decode_snapshot(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    try:
        return base64.b64decode(value.encode("ascii"), validate=True).decode("utf-8")
    except (ValueError, UnicodeError):
        return None


def _path_within(path: Path, directory: Path) -> bool:
    resolved_path = path.resolve(strict=False)
    resolved_directory = directory.resolve(strict=False)
    return resolved_path == resolved_directory or resolved_directory in resolved_path.parents


def _validate_detect_paths(request: Path, draft: Path, sources: list[Path], txn: Path) -> None:
    for item in [request, draft, *sources]:
        if _path_within(item, txn):
            raise GateInputError("input files must stay outside the transaction directory")


@contextmanager
def transaction_lock(txn: Path) -> Iterator[None]:
    txn.mkdir(parents=True, exist_ok=True)
    lock_path = txn / LOCK_FILE
    with lock_path.open("a+b") as handle:
        handle.seek(0, os.SEEK_END)
        if handle.tell() == 0:
            handle.write(b"0")
            handle.flush()
        handle.seek(0)
        locked = False
        try:
            if os.name == "nt":
                import msvcrt

                try:
                    msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
                except OSError as exc:
                    raise TransactionBusyError("transaction is already locked") from exc
            else:
                import fcntl

                try:
                    fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                except OSError as exc:
                    raise TransactionBusyError("transaction is already locked") from exc
            locked = True
            yield
        finally:
            if locked:
                handle.seek(0)
                if os.name == "nt":
                    import msvcrt

                    msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
                else:
                    import fcntl

                    fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


@contextmanager
def dispatch_lock(txn: Path, timeout: int) -> Iterator[None]:
    """Serialize the complete host path so concurrent calls share one selection."""

    txn.mkdir(parents=True, exist_ok=True)
    lock_path = txn / DISPATCH_LOCK_FILE
    deadline = time.monotonic() + timeout
    with lock_path.open("a+b") as handle:
        handle.seek(0, os.SEEK_END)
        if handle.tell() == 0:
            handle.write(b"0")
            handle.flush()
        locked = False
        try:
            while not locked:
                handle.seek(0)
                try:
                    if os.name == "nt":
                        import msvcrt

                        msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
                    else:
                        import fcntl

                        fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                    locked = True
                except OSError as exc:
                    if time.monotonic() >= deadline:
                        raise TransactionBusyError("dispatcher is still running") from exc
                    time.sleep(0.02)
            yield
        finally:
            if locked:
                handle.seek(0)
                if os.name == "nt":
                    import msvcrt

                    msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
                else:
                    import fcntl

                    fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def _load_state(txn: Path) -> dict[str, Any] | None:
    return read_json(txn / STATE_FILE)


def _load_backup(txn: Path) -> dict[str, Any] | None:
    return read_json(txn / BACKUP_FILE)


def _load_snapshots(txn: Path, state: dict[str, Any]) -> tuple[str, str, str]:
    backup = _load_backup(txn) or {}
    result: list[str] = []
    for filename, hash_key, backup_key in (
        (REQUEST_FILE, "request_sha256", "request_b64"),
        (SOURCE_FILE, "source_sha256", "source_b64"),
        (D0_FILE, "d0_sha256", "d0_b64"),
    ):
        expected_hash = state.get(hash_key)
        text: str | None = None
        try:
            candidate = read_text(txn / filename)
            if isinstance(expected_hash, str) and sha256_text(candidate) == expected_hash:
                text = candidate
        except (OSError, UnicodeError):
            pass
        if text is None:
            candidate = _decode_snapshot(backup.get(backup_key))
            if candidate is not None and isinstance(expected_hash, str) and sha256_text(candidate) == expected_hash:
                text = candidate
        if text is None:
            raise GateInputError(f"transaction snapshot corrupt: {filename}")
        result.append(text)
    return result[0], result[1], result[2]


def emergency_d0(txn: Path) -> str | None:
    backup = _load_backup(txn) or {}
    state = _load_state(txn) or {}
    text = _decode_snapshot(backup.get("d0_b64"))
    expected = backup.get("d0_sha256") or state.get("d0_sha256")
    if text is not None and isinstance(expected, str) and sha256_text(text) == expected:
        return text
    try:
        text = read_text(txn / D0_FILE)
        return text if text.strip() and isinstance(expected, str) and sha256_text(text) == expected else None
    except (OSError, UnicodeError):
        return None


def _state_summary(state: dict[str, Any]) -> dict[str, Any]:
    keys = (
        "schema_version",
        "run_id",
        "state",
        "detect_count",
        "repair_count",
        "mechanical_check_count",
        "verify_count",
        "repair_agent_call_count",
        "verdict_agent_call_count",
        "postdraft_marker_pass_verified",
        "guided_marker_parse_status",
        "guided_marker_count",
        "selected",
        "reason",
        "state_trace",
    )
    return {key: state.get(key) for key in keys}


def _fallback_d0_claim(txn: Path, state: dict[str, Any]) -> dict[str, Any]:
    text = emergency_d0(txn)
    return {
        "schema_version": SCHEMA_VERSION,
        "run_id": state.get("run_id"),
        "selected": "D0",
        "output_sha256": state.get("d0_sha256"),
        "output_b64": _encode_snapshot(text) if text is not None else None,
        "semantic_receipt_sha256": None,
    }


def _valid_selection_claim(
    txn: Path, state: dict[str, Any], claim: dict[str, Any] | None
) -> dict[str, Any] | None:
    expected_keys = {
        "schema_version",
        "run_id",
        "selected",
        "output_sha256",
        "output_b64",
        "semantic_receipt_sha256",
    }
    if not isinstance(claim, dict) or set(claim) != expected_keys:
        return None
    selected = claim.get("selected")
    recovering = state.get(SELECTION_RECOVERY_MARKER) is True
    expected_hash = (
        claim.get("output_sha256")
        if selected == "D1" and recovering
        else state.get("d1_sha256")
        if selected == "D1"
        else state.get("d0_sha256")
    )
    output_text = _decode_snapshot(claim.get("output_b64"))
    if (
        claim.get("schema_version") != SCHEMA_VERSION
        or claim.get("run_id") != state.get("run_id")
        or selected not in {"D0", "D1"}
        or not isinstance(expected_hash, str)
        or claim.get("output_sha256") != expected_hash
        or output_text is None
        or not output_text.strip()
        or sha256_text(output_text) != expected_hash
    ):
        return None
    receipt = claim.get("semantic_receipt_sha256")
    if selected == "D0":
        return claim if receipt is None else None
    expected_receipt = (
        receipt if recovering else state.get("semantic_pass_receipt_sha256")
    )
    if not isinstance(expected_receipt, str) or receipt != expected_receipt:
        return None
    try:
        accepted_verdict = read_text(txn / VERDICT_FILE)
    except (OSError, UnicodeError):
        return None
    if sha256_text(accepted_verdict) != expected_receipt:
        return None
    verdict = read_json(txn / VERDICT_FILE)
    verdict_state = dict(state)
    if recovering:
        verdict_state["d1_sha256"] = expected_hash
        verdict_state["semantic_pass_receipt_sha256"] = expected_receipt
    passed, _ = _semantic_verdict_result(verdict_state, verdict)
    return claim if passed else None


def _read_selection_claim(txn: Path, state: dict[str, Any]) -> dict[str, Any] | None:
    paths = (txn / SELECTION_FILE, txn / SELECTION_BACKUP_FILE)
    if not any(path.exists() for path in paths):
        if state.get("state") == STATE_TERMINAL_D1 or _possible_prior_d1(txn):
            raise GateInputError(
                "selection record is missing after semantic PASS; host must use its retained selected output"
            )
        return None
    for path in paths:
        valid = _valid_selection_claim(txn, state, read_json(path))
        if valid is not None:
            return valid
    recovery_state = _selection_state_from_backup(txn)
    if recovery_state is not None:
        for path in paths:
            valid = _valid_selection_claim(txn, recovery_state, read_json(path))
            if valid is not None:
                return valid
    raise GateInputError(
        "selection record exists but cannot be verified; host must use its retained selected output"
    )


def _claim_selection(
    txn: Path, state: dict[str, Any], selected: str, output_text: str
) -> dict[str, Any]:
    if not output_text.strip():
        raise GateInputError("selected output must be non-empty")
    receipt = state.get("semantic_pass_receipt_sha256") if selected == "D1" else None
    if selected == "D1" and not isinstance(receipt, str):
        raise GateInputError("D1 selection requires a verified semantic receipt")
    claim = {
        "schema_version": SCHEMA_VERSION,
        "run_id": state.get("run_id"),
        "selected": selected,
        "output_sha256": sha256_text(output_text),
        "output_b64": _encode_snapshot(output_text),
        "semantic_receipt_sha256": receipt,
    }
    path = txn / SELECTION_FILE
    payload = json.dumps(claim, ensure_ascii=False, sort_keys=True) + "\n"
    temp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="\n",
            prefix=".selection.claim.",
            suffix=".tmp",
            dir=txn,
            delete=False,
        ) as handle:
            temp_path = Path(handle.name)
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        try:
            os.link(temp_path, path)
            atomic_write_text(txn / SELECTION_BACKUP_FILE, payload)
        except FileExistsError:
            pass
        except OSError as exc:
            raise GateInputError("atomic selection claim could not be published") from exc
    finally:
        if temp_path is not None:
            try:
                temp_path.unlink()
            except OSError:
                pass
    return _read_selection_claim(txn, state) or _fallback_d0_claim(txn, state)


def _claimed_text(txn: Path, state: dict[str, Any], claim: dict[str, Any]) -> str | None:
    text = _decode_snapshot(claim.get("output_b64"))
    if text is not None and text.strip() and sha256_text(text) == claim.get("output_sha256"):
        return text
    if claim.get("selected") == "D0":
        return emergency_d0(txn)
    try:
        candidate = read_text(txn / D1_FILE)
    except (OSError, UnicodeError):
        return None
    return candidate if candidate.strip() and sha256_text(candidate) == state.get("d1_sha256") else None


def _terminalize(
    txn: Path,
    state: dict[str, Any],
    selected: str,
    reason: str,
    candidate: str | None = None,
) -> dict[str, Any]:
    requested = selected
    output_text = emergency_d0(txn)
    if output_text is None:
        raise GateInputError("trusted D0 snapshot is unavailable")
    if selected == "D1":
        if candidate is None or not candidate.strip():
            selected = "D0"
            reason = "empty_candidate_at_commit"
        elif _has_guided_marker_token(candidate):
            selected = "D0"
            reason = "guided_marker_residue_in_candidate"
        else:
            atomic_write_text(txn / D1_FILE, candidate)
            output_text = candidate
            state["d1_sha256"] = sha256_text(candidate)
    claim = _claim_selection(txn, state, selected, output_text)
    selected = str(claim.get("selected"))
    output_hash = claim.get("output_sha256")
    if selected == "D1" and _claimed_text(txn, state, claim) is None:
        selected = "D0"
        output_hash = state.get("d0_sha256")
        reason = "claimed_d1_missing_or_corrupt"
    elif requested != selected:
        reason = f"selection_already_claimed_{selected.lower()}"
    terminal_state = STATE_TERMINAL_D1 if selected == "D1" else STATE_TERMINAL_D0
    updated = dict(state)
    trace = list(updated.get("state_trace") or [])
    if not trace or trace[-1] != terminal_state:
        trace.append(terminal_state)
    updated.update(
        {
            "state": terminal_state,
            "selected": selected,
            "reason": reason,
            "output_sha256": output_hash,
            "state_trace": trace,
        }
    )
    atomic_write_json(txn / REPORT_FILE, _state_summary(updated) | {"output_sha256": output_hash})
    atomic_write_json(txn / STATE_FILE, updated)
    return updated


def _reconcile_selection_claim(
    txn: Path, state: dict[str, Any]
) -> dict[str, Any] | None:
    claim = _read_selection_claim(txn, state)
    if claim is None:
        return None
    candidate = _claimed_text(txn, state, claim)
    if claim.get("selected") == "D1" and candidate is not None:
        recovered = dict(state)
        recovered["d1_sha256"] = claim.get("output_sha256")
        recovered["semantic_pass_receipt_sha256"] = claim.get(
            "semantic_receipt_sha256"
        )
        return _terminalize(
            txn, recovered, "D1", "selection_claim_recovered", candidate
        )
    return _terminalize(txn, state, "D0", "selection_claim_recovered")


def detect_transaction(
    request_path: Path,
    draft_path: Path,
    source_paths: list[Path],
    txn: Path,
    repair_timeout: int,
    verdict_timeout: int | None = None,
    dispatch_input_sha256: str | None = None,
    guided_marker_sidecar: dict[str, Any] | None = None,
    postdraft_marker_pass_verified: bool | None = None,
) -> dict[str, Any]:
    if repair_timeout < 1 or repair_timeout > 3600:
        raise GateInputError("repair timeout must be between 1 and 3600 seconds")
    if verdict_timeout is None:
        verdict_timeout = repair_timeout
    if verdict_timeout < 1 or verdict_timeout > 3600:
        raise GateInputError("verdict timeout must be between 1 and 3600 seconds")
    _validate_detect_paths(request_path, draft_path, source_paths, txn)
    request = read_text(request_path)
    draft = read_text(draft_path)
    source = "\n\n".join(read_text(path) for path in source_paths)
    if not draft.strip():
        raise GateInputError("D0 must be a non-empty complete draft")
    input_hashes = {
        "request_sha256": sha256_text(request),
        "source_sha256": sha256_text(source),
        "d0_sha256": sha256_text(draft),
    }
    effective_dispatch_input_sha256 = dispatch_input_sha256 or sha256_text(draft)
    marker_mode = (
        str(guided_marker_sidecar.get("parse_status"))
        if isinstance(guided_marker_sidecar, dict)
        else "NONE"
    )
    guided_marker_text: str | None = None
    input_hashes["dispatch_input_sha256"] = effective_dispatch_input_sha256
    input_hashes["guided_marker_parse_status"] = marker_mode
    postdraft_marker_binding_mode = _postdraft_marker_binding_mode(
        postdraft_marker_pass_verified
    )
    input_hashes["postdraft_marker_binding_mode"] = postdraft_marker_binding_mode
    if guided_marker_sidecar is not None:
        guided_marker_text = json.dumps(
            guided_marker_sidecar, ensure_ascii=False, indent=2
        ) + "\n"
        input_hashes["guided_marker_sha256"] = sha256_text(guided_marker_text)
    marker_binding_sha256 = sha256_text(guided_marker_text or "")
    input_hashes["guided_marker_binding_sha256"] = marker_binding_sha256

    with transaction_lock(txn):
        existing = _load_state(txn)
        if existing:
            if any(existing.get(key) != value for key, value in input_hashes.items()):
                raise GateInputError(
                    "transaction is already bound to different request, source, or D0 inputs"
                )
            state_name = existing.get("state")
            if state_name in TERMINAL_STATES:
                return existing
            reconciled = _reconcile_selection_claim(txn, existing)
            if reconciled is not None:
                return reconciled
            if state_name in {
                STATE_AWAITING_REPAIR,
                STATE_AWAITING_VERDICT,
            }:
                return existing
            if state_name in {
                STATE_DETECTING,
                STATE_MECHANICAL_VERIFYING,
                STATE_SEMANTIC_VERIFYING,
            }:
                return _terminalize(txn, existing, "D0", "interrupted_transaction_recovered")
            return _terminalize(txn, existing, "D0", "invalid_transaction_state")
        if any(
            (txn / name).exists()
            for name in RESERVED_FILES
            if name not in {LOCK_FILE, DISPATCH_LOCK_FILE}
        ):
            raise GateInputError("transaction directory already contains untrusted files")

        run_id = str(uuid.uuid4())
        backup = {
            "schema_version": SCHEMA_VERSION,
            "run_id": run_id,
            "request_sha256": sha256_text(request),
            "source_sha256": sha256_text(source),
            "d0_sha256": sha256_text(draft),
            "request_b64": _encode_snapshot(request),
            "source_b64": _encode_snapshot(source),
            "d0_b64": _encode_snapshot(draft),
        }
        backup["dispatch_input_sha256"] = effective_dispatch_input_sha256
        backup["guided_marker_parse_status"] = marker_mode
        backup["postdraft_marker_pass_verified"] = postdraft_marker_pass_verified
        backup["postdraft_marker_binding_mode"] = postdraft_marker_binding_mode
        backup["guided_marker_binding_sha256"] = marker_binding_sha256
        if guided_marker_text is not None:
            backup["guided_marker_sha256"] = sha256_text(guided_marker_text)
            backup["guided_marker_b64"] = _encode_snapshot(guided_marker_text)
        atomic_write_text(txn / REQUEST_FILE, request)
        atomic_write_text(txn / SOURCE_FILE, source)
        atomic_write_text(txn / D0_FILE, draft)
        atomic_write_json(txn / BACKUP_FILE, backup)
        deadline = datetime.now(timezone.utc) + timedelta(seconds=repair_timeout)
        state = {
            "schema_version": SCHEMA_VERSION,
            "run_id": run_id,
            "state": STATE_DETECTING,
            "request_sha256": sha256_text(request),
            "source_sha256": sha256_text(source),
            "d0_sha256": sha256_text(draft),
            "dispatch_input_sha256": effective_dispatch_input_sha256,
            "postdraft_marker_pass_verified": postdraft_marker_pass_verified,
            "postdraft_marker_binding_mode": postdraft_marker_binding_mode,
            "guided_marker_sha256": (
                sha256_text(guided_marker_text) if guided_marker_text is not None else None
            ),
            "guided_marker_binding_sha256": marker_binding_sha256,
            "guided_marker_parse_status": marker_mode,
            "guided_marker_count": (
                guided_marker_sidecar.get("marker_count")
                if isinstance(guided_marker_sidecar, dict)
                else 0
            ),
            "detection_sha256": None,
            "d1_sha256": None,
            "detect_count": 1,
            "repair_count": 0,
            "mechanical_check_count": 0,
            "verify_count": 0,
            "repair_agent_call_count": 0,
            "verdict_agent_call_count": 0,
            "selected": None,
            "reason": None,
            "repair_timeout_seconds": repair_timeout,
            "verdict_timeout_seconds": verdict_timeout,
            "repair_deadline_utc": deadline.isoformat(),
            "verdict_deadline_utc": None,
            "verification_packet_sha256": None,
            "repair_packet_sha256": None,
            "semantic_pass_receipt_sha256": None,
            "state_trace": [STATE_DETECTING],
        }
        atomic_write_json(txn / STATE_FILE, state)
        try:
            if guided_marker_text is not None:
                atomic_write_text(txn / GUIDED_MARKER_FILE, guided_marker_text)
                parse_status = guided_marker_sidecar.get("parse_status")
                if parse_status == "INVALID":
                    marker_errors = guided_marker_sidecar.get("errors") or []
                    reason = (
                        "postdraft_marker_pass_changed_text"
                        if "postdraft_marker_pass_changed_text" in marker_errors
                        else "guided_marker_parse_invalid"
                    )
                    return _terminalize(txn, state, "D0", reason)
                if parse_status != "VALID":
                    return _terminalize(txn, state, "D0", "guided_marker_status_invalid")
            detection = locate_candidates(
                request,
                draft,
                source,
                guided_marker_sidecar=guided_marker_sidecar,
            )
            detection["run_id"] = run_id
            atomic_write_json(txn / DETECTION_FILE, detection)
            state["detection_sha256"] = sha256_text(read_text(txn / DETECTION_FILE))
            if not detection["findings"]:
                return _terminalize(txn, state, "D0", "no_review_candidate")
            if len(detection["findings"]) > MAX_FINDINGS:
                return _terminalize(txn, state, "D0", "finding_budget_exceeded")
            repair_packet = _build_repair_packet(state, detection, draft)
            atomic_write_json(txn / REPAIR_PACKET_FILE, repair_packet)
            state["repair_packet_sha256"] = sha256_text(
                read_text(txn / REPAIR_PACKET_FILE)
            )
            state["state"] = STATE_AWAITING_REPAIR
            state["state_trace"] = [STATE_DETECTING, STATE_AWAITING_REPAIR]
            atomic_write_json(txn / STATE_FILE, state)
            return state
        except Exception:
            return _terminalize(txn, state, "D0", "detection_failed")


def _deadline_expired(
    state: dict[str, Any], key: str = "repair_deadline_utc"
) -> bool:
    value = state.get(key)
    if not isinstance(value, str):
        return True
    try:
        deadline = datetime.fromisoformat(value)
    except ValueError:
        return True
    if deadline.tzinfo is None:
        deadline = deadline.replace(tzinfo=timezone.utc)
    return datetime.now(timezone.utc) > deadline


def _build_repair_packet(
    state: dict[str, Any], detection: dict[str, Any], draft: str
) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    for raw_finding in detection.get("findings") or []:
        finding = dict(raw_finding)
        allowed_decisions, delete_block_reason = _finding_action_contract(
            finding, draft
        )
        finding["allowed_decisions"] = allowed_decisions
        finding["delete_block_reason"] = delete_block_reason
        findings.append(finding)
    return {
        "schema_version": REPAIR_PACKET_SCHEMA_VERSION,
        "response_schema_version": SCHEMA_VERSION,
        "response_revision_count": 1,
        "response_repair_mode": REPAIR_MODE_DECISIONS,
        "phase": "repair",
        "run_id": state.get("run_id"),
        "request_sha256": state.get("request_sha256"),
        "source_sha256": state.get("source_sha256"),
        "draft_sha256": state.get("d0_sha256"),
        "detection_sha256": state.get("detection_sha256"),
        "files": {
            "request": REQUEST_FILE,
            "source": SOURCE_FILE,
            "draft": D0_FILE,
            "detection": DETECTION_FILE,
            "guided_markers": (
                GUIDED_MARKER_FILE if state.get("guided_marker_sha256") else None
            ),
        },
        "finding_count": len(detection.get("findings") or []),
        "max_findings": MAX_FINDINGS,
        "allowed_decisions": [DECISION_KEEP, DECISION_DELETE, DECISION_REWRITE],
        "guided_marker_sha256": state.get("guided_marker_sha256"),
        "findings": findings,
    }


def _load_bound_packet(
    txn: Path, state: dict[str, Any], filename: str, hash_key: str
) -> dict[str, Any]:
    text = read_text(txn / filename)
    if sha256_text(text) != state.get(hash_key):
        raise GateInputError(f"transaction packet corrupt: {filename}")
    packet = json.loads(text)
    if not isinstance(packet, dict):
        raise GateInputError(f"transaction packet invalid: {filename}")
    return packet


def _load_guided_marker_sidecar(
    txn: Path, state: dict[str, Any]
) -> dict[str, Any] | None:
    expected = state.get("guided_marker_sha256")
    if expected is None:
        return None
    if not isinstance(expected, str):
        raise GateInputError("guided marker hash is invalid")
    text = read_text(txn / GUIDED_MARKER_FILE)
    if sha256_text(text) != expected:
        raise GateInputError("guided marker sidecar is corrupt")
    payload = json.loads(text)
    if not isinstance(payload, dict):
        raise GateInputError("guided marker sidecar is invalid")
    return payload


def _claim_agent_call(
    txn: Path, expected_state: str, counter_key: str, repeated_reason: str
) -> tuple[dict[str, Any], bool]:
    with transaction_lock(txn):
        state = _load_state(txn)
        if not state:
            raise GateInputError("transaction state is missing")
        if state.get("state") in TERMINAL_STATES:
            return state, False
        if state.get("state") != expected_state:
            return _terminalize(txn, state, "D0", "invalid_transaction_state"), False
        count = state.get(counter_key, 0)
        if not isinstance(count, int) or count != 0:
            return _terminalize(txn, state, "D0", repeated_reason), False
        state[counter_key] = 1
        atomic_write_json(txn / STATE_FILE, state)
        return state, True


def _run_bridge(
    bridge_command: list[str], phase: str, packet_path: Path, timeout: int
) -> dict[str, Any]:
    if not bridge_command or not bridge_command[0]:
        raise GateInputError("bridge command is missing")
    completed = subprocess.run(
        [*bridge_command, phase, str(packet_path)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="strict",
        shell=False,
        timeout=timeout,
        check=False,
    )
    if completed.returncode != 0:
        raise GateInputError(f"{phase} bridge returned non-zero status")
    encoded = completed.stdout.encode("utf-8")
    if not encoded or len(encoded) > MAX_JSON_BYTES:
        raise GateInputError(f"{phase} bridge response size is invalid")
    payload = json.loads(completed.stdout)
    if not isinstance(payload, dict):
        raise GateInputError(f"{phase} bridge response is not an object")
    return payload


@contextmanager
def _external_response_file(
    txn: Path, prefix: str, payload: dict[str, Any]
) -> Iterator[Path]:
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    if len(encoded.encode("utf-8")) > MAX_JSON_BYTES:
        raise GateInputError("bridge response exceeds JSON size limit")
    handle = tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        prefix=prefix,
        suffix=".json",
        dir=txn.parent,
        delete=False,
    )
    path = Path(handle.name)
    try:
        with handle:
            handle.write(encoded)
        yield path
    finally:
        path.unlink(missing_ok=True)


@contextmanager
def _external_text_file(txn: Path, prefix: str, text: str) -> Iterator[Path]:
    txn.parent.mkdir(parents=True, exist_ok=True)
    handle = tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        prefix=prefix,
        suffix=".txt",
        dir=txn.parent,
        delete=False,
    )
    path = Path(handle.name)
    try:
        with handle:
            handle.write(text)
        yield path
    finally:
        path.unlink(missing_ok=True)


def _build_verification_packet(
    txn: Path, state: dict[str, Any], repair_sha256: str
) -> dict[str, Any]:
    return {
        "schema_version": SEMANTIC_VERDICT_SCHEMA_VERSION,
        "run_id": state.get("run_id"),
        "request_sha256": state.get("request_sha256"),
        "source_sha256": state.get("source_sha256"),
        "draft_sha256": state.get("d0_sha256"),
        "candidate_sha256": state.get("d1_sha256"),
        "repair_sha256": repair_sha256,
        "guided_marker_sha256": state.get("guided_marker_sha256"),
        "files": {
            "request": REQUEST_FILE,
            "source": SOURCE_FILE,
            "draft": D0_FILE,
            "candidate": D1_FILE,
            "repair": REPAIR_FILE,
            "guided_markers": (
                GUIDED_MARKER_FILE if state.get("guided_marker_sha256") else None
            ),
        },
        "required_checks": list(_semantic_checks_for_state(state)),
    }


def _semantic_verdict_result(
    state: dict[str, Any], verdict: dict[str, Any] | None
) -> tuple[bool, str]:
    if not isinstance(verdict, dict):
        return False, "semantic_verdict_missing_or_invalid"
    expected_keys = {
        "schema_version",
        "run_id",
        "request_sha256",
        "source_sha256",
        "draft_sha256",
        "candidate_sha256",
        "verdict",
        "checks",
    }
    if state.get("guided_marker_sha256") is not None:
        expected_keys.add("guided_marker_sha256")
    if set(verdict) != expected_keys:
        return False, "semantic_verdict_schema_mismatch"
    if verdict.get("schema_version") != SEMANTIC_VERDICT_SCHEMA_VERSION:
        return False, "semantic_verdict_schema_mismatch"
    for packet_key, state_key in (
        ("run_id", "run_id"),
        ("request_sha256", "request_sha256"),
        ("source_sha256", "source_sha256"),
        ("draft_sha256", "d0_sha256"),
        ("candidate_sha256", "d1_sha256"),
    ):
        if verdict.get(packet_key) != state.get(state_key):
            return False, "semantic_verdict_hash_mismatch"
    if state.get("guided_marker_sha256") is not None and verdict.get(
        "guided_marker_sha256"
    ) != state.get("guided_marker_sha256"):
        return False, "semantic_verdict_guided_marker_hash_mismatch"
    checks = verdict.get("checks")
    required_checks = _semantic_checks_for_state(state)
    if not isinstance(checks, dict) or set(checks) != set(required_checks):
        return False, "semantic_verdict_checks_mismatch"
    if verdict.get("verdict") == "FAIL":
        return False, "semantic_verdict_failed"
    if verdict.get("verdict") != "PASS" or any(
        checks.get(key) is not True for key in required_checks
    ):
        return False, "semantic_verdict_not_unanimous"
    return True, "semantic_verdict_passed"


def prepare_transaction(txn: Path, repairs_path: Path | None) -> dict[str, Any]:
    with transaction_lock(txn):
        state = _load_state(txn)
        if not state:
            raise GateInputError("transaction state is missing")
        state_name = state.get("state")
        if state_name in TERMINAL_STATES:
            return state
        reconciled = _reconcile_selection_claim(txn, state)
        if reconciled is not None:
            return reconciled
        if state_name == STATE_AWAITING_VERDICT:
            return state
        if state_name in {
            STATE_DETECTING,
            STATE_MECHANICAL_VERIFYING,
            STATE_SEMANTIC_VERIFYING,
        }:
            return _terminalize(txn, state, "D0", "interrupted_transaction_recovered")
        if state_name != STATE_AWAITING_REPAIR:
            return _terminalize(txn, state, "D0", "invalid_transaction_state")
        if _deadline_expired(state):
            return _terminalize(txn, state, "D0", "repair_deadline_expired")
        if repairs_path is None:
            return _terminalize(txn, state, "D0", "repair_missing")
        if _path_within(repairs_path, txn):
            return _terminalize(txn, state, "D0", "repair_path_inside_transaction")

        state["state"] = STATE_MECHANICAL_VERIFYING
        state["repair_count"] = 1
        state["mechanical_check_count"] = 1
        state["state_trace"] = list(state.get("state_trace") or []) + [STATE_MECHANICAL_VERIFYING]
        atomic_write_json(txn / STATE_FILE, state)
        try:
            request, source, draft = _load_snapshots(txn, state)
            detection = read_json(txn / DETECTION_FILE)
            guided_marker_sidecar = _load_guided_marker_sidecar(txn, state)
            repair_packet = read_json(repairs_path)
            if repair_packet is not None:
                atomic_write_json(txn / REPAIR_FILE, repair_packet)
            result = evaluate_candidate(
                request,
                source,
                draft,
                str(state.get("run_id")),
                detection,
                repair_packet,
                guided_marker_sidecar=guided_marker_sidecar,
            )
            if result.selected != "D1":
                return _terminalize(txn, state, "D0", result.reason)
            atomic_write_text(txn / D1_FILE, result.text)
            state["d1_sha256"] = sha256_text(result.text)
            repair_sha256 = sha256_text(read_text(txn / REPAIR_FILE))
            packet = _build_verification_packet(txn, state, repair_sha256)
            atomic_write_json(txn / VERIFICATION_PACKET_FILE, packet)
            state["verification_packet_sha256"] = sha256_text(
                read_text(txn / VERIFICATION_PACKET_FILE)
            )
            state["verdict_deadline_utc"] = (
                datetime.now(timezone.utc)
                + timedelta(seconds=int(state.get("verdict_timeout_seconds") or 180))
            ).isoformat()
            state["state"] = STATE_AWAITING_VERDICT
            state["reason"] = "mechanical_checks_passed"
            state["state_trace"] = list(state.get("state_trace") or []) + [STATE_AWAITING_VERDICT]
            atomic_write_json(txn / STATE_FILE, state)
            return state
        except Exception:
            return _terminalize(txn, state, "D0", "mechanical_verification_failed")


def finalize_transaction(txn: Path, verdict_path: Path | None) -> dict[str, Any]:
    with transaction_lock(txn):
        state = _load_state(txn)
        if not state:
            raise GateInputError("transaction state is missing")
        state_name = state.get("state")
        if state_name in TERMINAL_STATES:
            return state
        reconciled = _reconcile_selection_claim(txn, state)
        if reconciled is not None:
            return reconciled
        if state_name in {
            STATE_DETECTING,
            STATE_MECHANICAL_VERIFYING,
            STATE_SEMANTIC_VERIFYING,
        }:
            return _terminalize(txn, state, "D0", "interrupted_transaction_recovered")
        if state_name != STATE_AWAITING_VERDICT:
            return _terminalize(txn, state, "D0", "semantic_verdict_before_candidate")
        if _deadline_expired(state, "verdict_deadline_utc"):
            return _terminalize(txn, state, "D0", "semantic_verdict_deadline_expired")
        if verdict_path is None:
            return _terminalize(txn, state, "D0", "semantic_verdict_missing")
        if _path_within(verdict_path, txn):
            return _terminalize(txn, state, "D0", "semantic_verdict_path_inside_transaction")

        state["state"] = STATE_SEMANTIC_VERIFYING
        state["verify_count"] = 1
        state["state_trace"] = list(state.get("state_trace") or []) + [STATE_SEMANTIC_VERIFYING]
        atomic_write_json(txn / STATE_FILE, state)
        try:
            _load_snapshots(txn, state)
            candidate = read_text(txn / D1_FILE)
            if not candidate.strip() or sha256_text(candidate) != state.get("d1_sha256"):
                return _terminalize(txn, state, "D0", "candidate_snapshot_corrupt")
            verification_packet = read_text(txn / VERIFICATION_PACKET_FILE)
            if sha256_text(verification_packet) != state.get("verification_packet_sha256"):
                return _terminalize(txn, state, "D0", "verification_packet_corrupt")
            verdict = read_json(verdict_path)
            if verdict is not None:
                atomic_write_json(txn / VERDICT_FILE, verdict)
            passed, reason = _semantic_verdict_result(state, verdict)
            if not passed:
                return _terminalize(txn, state, "D0", reason)
            state["semantic_pass_receipt_sha256"] = sha256_text(
                read_text(txn / VERDICT_FILE)
            )
            atomic_write_json(txn / STATE_FILE, state)
            return _terminalize(txn, state, "D1", reason, candidate)
        except Exception:
            return _terminalize(txn, state, "D0", "semantic_verification_failed")


def dispatch_transaction(
    request_path: Path,
    draft_path: Path,
    source_paths: list[Path],
    txn: Path,
    bridge_command: list[str],
    repair_timeout: int,
    verdict_timeout: int,
    marked_draft_path: Path | None = None,
) -> str:
    """Serialize one bounded review chain and emit exactly one selected draft."""

    original_d0 = read_text(draft_path)
    original_guided_draft = _parse_guided_draft(original_d0)
    retained_d0 = original_guided_draft.fallback_d0
    if not retained_d0.strip():
        raise GateInputError("D0 must be a non-empty complete draft")
    postdraft_marker_pass_verified: bool | None = None
    guided_draft = original_guided_draft
    bounded_repair_timeout = repair_timeout if 1 <= repair_timeout <= 3600 else 1
    bounded_verdict_timeout = verdict_timeout if 1 <= verdict_timeout <= 3600 else 1
    try:
        if marked_draft_path is not None:
            guided_draft, postdraft_marker_pass_verified = _bind_postdraft_marker_pass(
                original_d0, read_text(marked_draft_path)
            )
            retained_d0 = guided_draft.fallback_d0
        validation_sources = [*source_paths]
        if marked_draft_path is not None:
            validation_sources.append(marked_draft_path)
        _validate_detect_paths(request_path, draft_path, validation_sources, txn)
        with dispatch_lock(txn, bounded_repair_timeout + bounded_verdict_timeout + 5):
            with _external_text_file(txn, "review-gate-d0-", retained_d0) as clean_draft_path:
                return _dispatch_transaction_locked(
                    request_path,
                    clean_draft_path,
                    source_paths,
                    txn,
                    bridge_command,
                    repair_timeout,
                    verdict_timeout,
                    retained_d0,
                    guided_draft.raw_sha256,
                    guided_draft.sidecar() if guided_draft.parse_status != "NONE" else None,
                    postdraft_marker_pass_verified,
                )
    except (GateInputError, TransactionBusyError, OSError, UnicodeError):
        return emit_transaction(
            txn,
            retained_d0=retained_d0,
            force_retained_d0=True,
        )


def _dispatch_transaction_locked(
    request_path: Path,
    draft_path: Path,
    source_paths: list[Path],
    txn: Path,
    bridge_command: list[str],
    repair_timeout: int,
    verdict_timeout: int,
    retained_d0: str,
    dispatch_input_sha256: str | None,
    guided_marker_sidecar: dict[str, Any] | None,
    postdraft_marker_pass_verified: bool | None,
) -> str:
    """Run the serialized state transition chain without another dispatch lock."""

    state: dict[str, Any] | None = None
    bound_input_hashes: dict[str, str] | None = None
    failure_reason = "dispatch_failed"
    try:
        if verdict_timeout < 1 or verdict_timeout > 3600:
            raise GateInputError("verdict timeout must be between 1 and 3600 seconds")
        request_text = read_text(request_path)
        source_text = "\n\n".join(read_text(path) for path in source_paths)
        guided_marker_text = (
            json.dumps(guided_marker_sidecar, ensure_ascii=False, indent=2) + "\n"
            if guided_marker_sidecar is not None
            else None
        )
        bound_input_hashes = {
            "request_sha256": sha256_text(request_text),
            "source_sha256": sha256_text(source_text),
            "d0_sha256": sha256_text(retained_d0),
            "dispatch_input_sha256": dispatch_input_sha256 or sha256_text(retained_d0),
            "guided_marker_parse_status": (
                str(guided_marker_sidecar.get("parse_status"))
                if isinstance(guided_marker_sidecar, dict)
                else "NONE"
            ),
            "guided_marker_binding_sha256": sha256_text(guided_marker_text or ""),
            "postdraft_marker_binding_mode": _postdraft_marker_binding_mode(
                postdraft_marker_pass_verified
            ),
        }
        state = detect_transaction(
            request_path,
            draft_path,
            source_paths,
            txn,
            repair_timeout,
            verdict_timeout,
            dispatch_input_sha256=dispatch_input_sha256,
            guided_marker_sidecar=guided_marker_sidecar,
            postdraft_marker_pass_verified=postdraft_marker_pass_verified,
        )
        effective_repair_timeout = int(
            state.get("repair_timeout_seconds") or repair_timeout
        )
        effective_verdict_timeout = int(
            state.get("verdict_timeout_seconds") or verdict_timeout
        )
        if state.get("state") == STATE_AWAITING_REPAIR:
            _load_bound_packet(txn, state, REPAIR_PACKET_FILE, "repair_packet_sha256")
            state, claimed = _claim_agent_call(
                txn,
                STATE_AWAITING_REPAIR,
                "repair_agent_call_count",
                "repair_agent_already_called",
            )
            if claimed:
                failure_reason = "repair_bridge_failed"
                repair_payload = _run_bridge(
                    bridge_command,
                    "repair",
                    txn / REPAIR_PACKET_FILE,
                    effective_repair_timeout,
                )
                with _external_response_file(
                    txn, "review-gate-repair-", repair_payload
                ) as repair_path:
                    state = prepare_transaction(txn, repair_path)

        if state.get("state") == STATE_AWAITING_VERDICT:
            _load_bound_packet(
                txn,
                state,
                VERIFICATION_PACKET_FILE,
                "verification_packet_sha256",
            )
            state, claimed = _claim_agent_call(
                txn,
                STATE_AWAITING_VERDICT,
                "verdict_agent_call_count",
                "verdict_agent_already_called",
            )
            if claimed:
                failure_reason = "verdict_bridge_failed"
                verdict_payload = _run_bridge(
                    bridge_command,
                    "verify",
                    txn / VERIFICATION_PACKET_FILE,
                    effective_verdict_timeout,
                )
                with _external_response_file(
                    txn, "review-gate-verdict-", verdict_payload
                ) as verdict_path:
                    state = finalize_transaction(txn, verdict_path)
    except Exception:
        try:
            if isinstance(bound_input_hashes, dict) and _transaction_matches_bound_inputs(
                txn, bound_input_hashes
            ):
                state = abort_transaction(txn, failure_reason)
        except Exception:
            state = None
    return emit_transaction(
        txn,
        retained_d0=retained_d0,
        bound_input_hashes=bound_input_hashes,
        force_retained_d0=bound_input_hashes is None,
    )


def abort_transaction(txn: Path, reason: str) -> dict[str, Any]:
    with transaction_lock(txn):
        state = _load_state(txn)
        if not state:
            raise GateInputError("transaction state is missing")
        if state.get("state") in TERMINAL_STATES:
            return state
        reconciled = _reconcile_selection_claim(txn, state)
        if reconciled is not None:
            return reconciled
        return _terminalize(txn, state, "D0", reason or "aborted")


def _selected_text(txn: Path, state: dict[str, Any]) -> str:
    if state.get("state") == STATE_TERMINAL_D1 and state.get("selected") == "D1":
        claim = _read_selection_claim(txn, state)
        if claim is not None and claim.get("selected") == "D1":
            text = _claimed_text(txn, state, claim)
            if text is not None:
                return text
        raise GateInputError("selected D1 is unavailable; host must use its retained D1")
    draft = emergency_d0(txn)
    if draft is None:
        raise GateInputError("selected D0 snapshot is unavailable")
    return draft


def _selection_state_from_backup(txn: Path) -> dict[str, Any] | None:
    backup = _load_backup(txn) or {}
    required = ("run_id", "request_sha256", "source_sha256", "d0_sha256")
    if any(not isinstance(backup.get(key), str) for key in required):
        return None
    state = {
        "schema_version": SCHEMA_VERSION,
        "run_id": backup["run_id"],
        "request_sha256": backup["request_sha256"],
        "source_sha256": backup["source_sha256"],
        "d0_sha256": backup["d0_sha256"],
        "d1_sha256": None,
        "semantic_pass_receipt_sha256": None,
        SELECTION_RECOVERY_MARKER: True,
    }
    if isinstance(backup.get("guided_marker_sha256"), str):
        state["guided_marker_sha256"] = backup["guided_marker_sha256"]
    return state


def _potential_semantic_pass(txn: Path) -> bool:
    recovery_state = _selection_state_from_backup(txn)
    verdict = read_json(txn / VERDICT_FILE)
    if recovery_state is None or not isinstance(verdict, dict):
        return False
    candidate_hash = verdict.get("candidate_sha256")
    if not isinstance(candidate_hash, str):
        return False
    recovery_state["d1_sha256"] = candidate_hash
    passed, _ = _semantic_verdict_result(recovery_state, verdict)
    return passed


def _possible_prior_d1(txn: Path) -> bool:
    report = read_json(txn / REPORT_FILE)
    if isinstance(report, dict) and (
        report.get("state") == STATE_TERMINAL_D1 or report.get("selected") == "D1"
    ):
        return True
    return _potential_semantic_pass(txn)


def _resolve_emit_text(txn: Path) -> str:
    try:
        with transaction_lock(txn):
            state = _load_state(txn)
            if not state:
                state = _selection_state_from_backup(txn)
                text = emergency_d0(txn)
                if state is None or text is None:
                    raise GateInputError("transaction state and D0 snapshot are missing")
                claim = _read_selection_claim(txn, state)
                if claim is None:
                    claim = _claim_selection(txn, state, "D0", text)
                text = _claimed_text(txn, state, claim) or text
            else:
                if state.get("state") not in TERMINAL_STATES:
                    reconciled = _reconcile_selection_claim(txn, state)
                    if reconciled is not None:
                        state = reconciled
                if state.get("state") not in TERMINAL_STATES:
                    state = _terminalize(txn, state, "D0", "emit_before_terminal")
                text = _selected_text(txn, state)
    except TransactionBusyError:
        state = _load_state(txn)
        if not state:
            state = _selection_state_from_backup(txn)
            text = emergency_d0(txn)
            if state is None or text is None:
                raise
            claim = _read_selection_claim(txn, state)
            if claim is None:
                claim = _claim_selection(txn, state, "D0", text)
            text = _claimed_text(txn, state, claim) or text
        elif state.get("state") in TERMINAL_STATES:
            text = _selected_text(txn, state)
        else:
            claim = _read_selection_claim(txn, state)
            if claim is None:
                d0 = emergency_d0(txn)
                if d0 is None:
                    raise GateInputError("trusted D0 snapshot is unavailable")
                claim = _claim_selection(txn, state, "D0", d0)
            text = _claimed_text(txn, state, claim) or emergency_d0(txn)
            if text is None:
                raise GateInputError("claimed output and D0 snapshot are unavailable")

    return text


def _retained_d0_fallback_allowed(txn: Path) -> bool:
    state = _load_state(txn) or {}
    if state.get("state") == STATE_TERMINAL_D1 or state.get("selected") == "D1":
        return False
    for filename in (SELECTION_FILE, SELECTION_BACKUP_FILE):
        claim = read_json(txn / filename)
        if isinstance(claim, dict) and claim.get("selected") == "D1":
            return False
    return not _possible_prior_d1(txn)


def _transaction_binding_status(
    txn: Path, bound_input_hashes: dict[str, str]
) -> str:
    comparisons: list[bool] = []
    for record in (_load_state(txn), _load_backup(txn)):
        if not isinstance(record, dict) or not all(
            isinstance(record.get(key), str) for key in bound_input_hashes
        ):
            continue
        comparisons.append(
            all(record.get(key) == value for key, value in bound_input_hashes.items())
        )
    if not comparisons:
        return "unavailable"
    if all(comparisons):
        return "match"
    if not any(comparisons):
        return "mismatch"
    return "conflict"


def _transaction_matches_bound_inputs(
    txn: Path, bound_input_hashes: dict[str, str]
) -> bool:
    return _transaction_binding_status(txn, bound_input_hashes) == "match"


def _recover_bound_d1_from_claim(
    txn: Path, bound_input_hashes: dict[str, str]
) -> str | None:
    expected_claim_keys = {
        "schema_version",
        "run_id",
        "selected",
        "output_sha256",
        "output_b64",
        "semantic_receipt_sha256",
    }
    try:
        verdict_text = read_text(txn / VERDICT_FILE)
        verdict = json.loads(verdict_text)
    except (OSError, UnicodeError, json.JSONDecodeError):
        return None
    if not isinstance(verdict, dict):
        return None
    for filename in (SELECTION_FILE, SELECTION_BACKUP_FILE):
        claim = read_json(txn / filename)
        if not isinstance(claim, dict) or set(claim) != expected_claim_keys:
            continue
        if claim.get("schema_version") != SCHEMA_VERSION or claim.get("selected") != "D1":
            continue
        text = _decode_snapshot(claim.get("output_b64"))
        output_hash = claim.get("output_sha256")
        if not text or not isinstance(output_hash, str) or sha256_text(text) != output_hash:
            continue
        if claim.get("semantic_receipt_sha256") != sha256_text(verdict_text):
            continue
        recovery_state = {
            "run_id": claim.get("run_id"),
            "request_sha256": bound_input_hashes.get("request_sha256"),
            "source_sha256": bound_input_hashes.get("source_sha256"),
            "d0_sha256": bound_input_hashes.get("d0_sha256"),
            "d1_sha256": output_hash,
        }
        if bound_input_hashes.get("guided_marker_parse_status") != "NONE" and isinstance(
            bound_input_hashes.get("guided_marker_binding_sha256"), str
        ):
            recovery_state["guided_marker_sha256"] = bound_input_hashes[
                "guided_marker_binding_sha256"
            ]
        passed, _ = _semantic_verdict_result(recovery_state, verdict)
        if passed:
            return text
    return None


def emit_transaction(
    txn: Path,
    retained_d0: str | None = None,
    bound_input_hashes: dict[str, str] | None = None,
    force_retained_d0: bool = False,
) -> str:
    binding_status = (
        _transaction_binding_status(txn, bound_input_hashes)
        if isinstance(bound_input_hashes, dict)
        else None
    )
    strict_postdraft_binding = (
        isinstance(bound_input_hashes, dict)
        and "postdraft_marker_binding_mode" in bound_input_hashes
    )
    if (
        strict_postdraft_binding
        and binding_status != "match"
        and isinstance(retained_d0, str)
        and retained_d0.strip()
    ):
        text = retained_d0
    elif binding_status == "conflict" and isinstance(retained_d0, str) and retained_d0.strip():
        text = _recover_bound_d1_from_claim(txn, bound_input_hashes)
        if text is None:
            text = retained_d0
    elif (
        isinstance(retained_d0, str)
        and retained_d0.strip()
        and (
            force_retained_d0
            or binding_status == "mismatch"
        )
    ):
        text = retained_d0
    else:
        try:
            text = _resolve_emit_text(txn)
        except Exception:
            recovered_d1 = (
                _recover_bound_d1_from_claim(txn, bound_input_hashes)
                if isinstance(bound_input_hashes, dict)
                else None
            )
            if recovered_d1 is not None:
                text = recovered_d1
            else:
                if (
                    not isinstance(retained_d0, str)
                    or not retained_d0.strip()
                    or not _retained_d0_fallback_allowed(txn)
                ):
                    raise
                text = retained_d0

    if _has_guided_marker_token(text):
        if isinstance(retained_d0, str) and retained_d0.strip() and not _has_guided_marker_token(
            retained_d0
        ):
            text = retained_d0
        else:
            raise GateInputError("guided marker residue reached emit")
    sys.stdout.write(text)
    return text


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Transactional one-pass review gate with D0 fallback.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    dispatch_parser = subparsers.add_parser(
        "dispatch", help="Run the research harness single entry and emit one complete draft."
    )
    dispatch_parser.add_argument("--request", required=True, help="UTF-8 raw request file.")
    dispatch_parser.add_argument("--draft", required=True, help="UTF-8 complete D0 draft file.")
    dispatch_parser.add_argument(
        "--marked-draft",
        help="Optional UTF-8 postdraft mark-only review; --draft remains the immutable D0.",
    )
    dispatch_parser.add_argument(
        "--source", action="append", default=[], help="Optional user source file; repeatable."
    )
    dispatch_parser.add_argument("--txn", required=True, help="Transaction directory.")
    dispatch_parser.add_argument(
        "--bridge-executable", required=True, help="Host bridge executable."
    )
    dispatch_parser.add_argument(
        "--bridge-arg", action="append", default=[], help="Fixed bridge argument; repeatable."
    )
    dispatch_parser.add_argument("--repair-timeout", type=int, default=180)
    dispatch_parser.add_argument("--verdict-timeout", type=int, default=180)

    detect_parser = subparsers.add_parser("detect", help="Snapshot D0 and perform the only detection pass.")
    detect_parser.add_argument("--request", required=True, help="UTF-8 file containing the raw current request.")
    detect_parser.add_argument("--draft", required=True, help="UTF-8 file containing the complete D0 draft.")
    detect_parser.add_argument(
        "--marked-draft",
        help="Optional UTF-8 postdraft mark-only review; --draft remains the immutable D0.",
    )
    detect_parser.add_argument("--source", action="append", default=[], help="Optional user-supplied source file; repeatable.")
    detect_parser.add_argument("--txn", required=True, help="New or existing transaction directory.")
    detect_parser.add_argument("--repair-timeout", type=int, default=180, help="Host repair deadline in seconds.")
    detect_parser.add_argument(
        "--verdict-timeout",
        type=int,
        default=None,
        help="Host semantic verdict deadline; defaults to repair timeout.",
    )

    prepare_parser = subparsers.add_parser(
        "prepare", help="Consume one repair packet and build one mechanically checked candidate."
    )
    prepare_parser.add_argument("--txn", required=True, help="Transaction directory.")
    prepare_parser.add_argument("--repairs", help="Agent-authored repair JSON outside the transaction directory.")

    finalize_parser = subparsers.add_parser(
        "finalize", help="Consume one fixed semantic verdict and permanently select D0 or D1."
    )
    finalize_parser.add_argument("--txn", required=True, help="Transaction directory.")
    finalize_parser.add_argument("--verdict", help="Verification-only Agent JSON outside the transaction directory.")

    abort_parser = subparsers.add_parser("abort", help="Permanently select D0 without another review pass.")
    abort_parser.add_argument("--txn", required=True, help="Transaction directory.")
    abort_parser.add_argument("--reason", default="aborted", help="Internal fallback reason.")

    emit_parser = subparsers.add_parser("emit", help="Emit the selected final draft and never re-enter review.")
    emit_parser.add_argument("--txn", required=True, help="Transaction directory.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    txn = Path(args.txn)
    try:
        if args.command == "dispatch":
            dispatch_transaction(
                Path(args.request),
                Path(args.draft),
                [Path(path) for path in args.source],
                txn,
                [args.bridge_executable, *args.bridge_arg],
                args.repair_timeout,
                args.verdict_timeout,
                Path(args.marked_draft) if args.marked_draft else None,
            )
            return 0
        if args.command == "detect":
            request_path = Path(args.request)
            draft_path = Path(args.draft)
            marked_draft_path = (
                Path(args.marked_draft) if args.marked_draft else None
            )
            source_paths = [Path(path) for path in args.source]
            validation_sources = [*source_paths]
            if marked_draft_path is not None:
                validation_sources.append(marked_draft_path)
            _validate_detect_paths(request_path, draft_path, validation_sources, txn)
            if marked_draft_path is not None:
                guided_draft, postdraft_marker_pass_verified = (
                    _bind_postdraft_marker_pass(
                        read_text(draft_path), read_text(marked_draft_path)
                    )
                )
            else:
                guided_draft = _parse_guided_draft(read_text(draft_path))
                postdraft_marker_pass_verified = None
            with _external_text_file(
                txn, "review-gate-d0-", guided_draft.fallback_d0
            ) as clean_draft_path:
                state = detect_transaction(
                    request_path,
                    clean_draft_path,
                    source_paths,
                    txn,
                    args.repair_timeout,
                    args.verdict_timeout,
                    dispatch_input_sha256=guided_draft.raw_sha256,
                    guided_marker_sidecar=(
                        guided_draft.sidecar()
                        if guided_draft.parse_status != "NONE"
                        else None
                    ),
                    postdraft_marker_pass_verified=postdraft_marker_pass_verified,
                )
            sys.stdout.write(json.dumps(_state_summary(state), ensure_ascii=False, indent=2) + "\n")
            return 0
        if args.command == "prepare":
            repairs = Path(args.repairs) if args.repairs else None
            state = prepare_transaction(txn, repairs)
            sys.stdout.write(json.dumps(_state_summary(state), ensure_ascii=False, indent=2) + "\n")
            return 0
        if args.command == "finalize":
            verdict = Path(args.verdict) if args.verdict else None
            state = finalize_transaction(txn, verdict)
            sys.stdout.write(json.dumps(_state_summary(state), ensure_ascii=False, indent=2) + "\n")
            return 0
        if args.command == "abort":
            state = abort_transaction(txn, args.reason)
            sys.stdout.write(json.dumps(_state_summary(state), ensure_ascii=False, indent=2) + "\n")
            return 0
        emit_transaction(txn)
        return 0
    except TransactionBusyError as exc:
        print(f"review_gate: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:
        print(f"review_gate: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
