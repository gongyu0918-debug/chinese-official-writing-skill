#!/usr/bin/env python3
"""Shared hard-anchor snapshots for bounded Hook revisions."""

from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass
import re
from typing import Any, Final, Iterable


NUMBER_RE: Final = re.compile(
    r"\d+(?:\.\d+)?(?:万元|人次|个月|小时|分钟|秒钟|元|年|月|日|时|分|秒|"
    r"台|件|项|人|页|份|条|个|号|场|名|组|户|家|所|辆)?"
)
CJK_QUANTITY_UNITS: Final = (
    "人次",
    "个月",
    "小时",
    "分钟",
    "秒钟",
    "台",
    "件",
    "项",
    "次",
    "年",
    "月",
    "日",
    "天",
    "份",
    "人",
    "套",
    "批",
    "元",
    "个",
    "场",
    "名",
    "页",
    "条",
    "组",
    "号",
    "户",
    "家",
    "所",
    "辆",
)
CJK_QUANTITY_RE: Final = re.compile(
    r"[一二三四五六七八九十百千万两]+(?:"
    + "|".join(re.escape(unit) for unit in CJK_QUANTITY_UNITS)
    + r")(?![个件项台人次场名页条组户家所辆套批])"
)
QUOTE_RE: Final = re.compile(r"“[^”\n]+”|‘[^’\n]+’|\"[^\"\n]+\"")
FIELD_SEGMENT_RE: Final = re.compile(
    r"(?:^|[；;])\s*(?P<label>[\u4e00-\u9fffA-Za-z][\u4e00-\u9fffA-Za-z0-9（）()\xb7 _-]{0,18})"
    r"[：:]\s*(?P<value>[^；;]+)"
)
FIELD_VALUE_SENTENCE_RE: Final = re.compile(r"[。！？!?]")
FIELD_INTRO_LABEL_RE: Final = re.compile(r"如下$")
FIELD_PROSE_LABEL_RE: Final = re.compile(r"(?:指出|强调|表示|认为|要求|提出)$")
STATE_CUE_RE: Final = re.compile(r"拟|尚未|未形成|正在|仍在|待核实|待审批|待研究")
CLAUSE_BOUNDARY_RE: Final = re.compile(r"[\n。！？；;]")


@dataclass(frozen=True)
class AnchorOccurrence:
    kind: str
    value: str
    start: int
    end: int
    context: str
    is_length_bound: bool


@dataclass(frozen=True)
class AnchorSnapshot:
    numbers: tuple[AnchorOccurrence, ...]
    quantities: tuple[AnchorOccurrence, ...]
    quotes: tuple[AnchorOccurrence, ...]
    fields: tuple[str, ...]
    state_contexts: tuple[str, ...]

    def to_payload(self) -> dict[str, Any]:
        return {
            "numbers": [asdict(item) for item in self.numbers],
            "quantities": [asdict(item) for item in self.quantities],
            "quotes": [asdict(item) for item in self.quotes],
            "fields": list(self.fields),
            "state_contexts": list(self.state_contexts),
        }


def _normalized_clause(text: str, start: int, end: int) -> str:
    left = max(
        (match.end() for match in CLAUSE_BOUNDARY_RE.finditer(text, 0, start)),
        default=0,
    )
    right_match = CLAUSE_BOUNDARY_RE.search(text, end)
    right = right_match.start() if right_match else len(text)
    return re.sub(r"\s+", "", text[left:right].strip())


def _occurrences(
    text: str, pattern: re.Pattern[str], kind: str
) -> tuple[AnchorOccurrence, ...]:
    return tuple(
        AnchorOccurrence(
            kind=kind,
            value=match.group(0),
            start=match.start(),
            end=match.end(),
            context=_normalized_clause(text, match.start(), match.end()),
            is_length_bound=(
                kind == "number" and _number_is_length_bound(text, match)
            ),
        )
        for match in pattern.finditer(text)
    )


def _number_is_length_bound(text: str, match: re.Match[str]) -> bool:
    right = text[match.end() : min(len(text), match.end() + 24)]
    if re.match(r"\s*字(?!节)", right):
        return True
    return bool(
        re.match(
            r"\s*(?:—|－|-|~|至|到)\s*\d+(?:\.\d+)?(?:个)?\s*字(?!节)",
            right,
        )
    )


def _field_labels(text: str) -> tuple[str, ...]:
    """Return labels from populated form-like lines, including inline forms."""

    labels: list[str] = []
    for line in text.splitlines():
        matches = [
            match
            for match in FIELD_SEGMENT_RE.finditer(line)
            if match.group("value").strip()
            and not FIELD_INTRO_LABEL_RE.search(match.group("label").strip())
            and not FIELD_PROSE_LABEL_RE.search(match.group("label").strip())
        ]
        if len(matches) >= 2 and all(
            not FIELD_VALUE_SENTENCE_RE.search(match.group("value"))
            for match in matches
        ):
            labels.extend(match.group("label").strip() for match in matches)
            continue
        if not matches:
            continue
        match = matches[0]
        value = match.group("value").strip()
        if match.group(0).lstrip().startswith(match.group("label")) and len(value) <= 80:
            labels.append(match.group("label").strip())
    return tuple(labels)


def snapshot(text: str) -> AnchorSnapshot:
    return AnchorSnapshot(
        numbers=_occurrences(text, NUMBER_RE, "number"),
        quantities=_occurrences(text, CJK_QUANTITY_RE, "quantity"),
        quotes=_occurrences(text, QUOTE_RE, "quote"),
        fields=_field_labels(text),
        state_contexts=tuple(
            re.sub(r"\s+", "", clause)
            for clause in CLAUSE_BOUNDARY_RE.split(text)
            if STATE_CUE_RE.search(clause)
        ),
    )


def _counter(items: Iterable[AnchorOccurrence]) -> Counter[str]:
    return Counter(item.value for item in items)


def _filtered_authority_counter(
    items: Iterable[AnchorOccurrence], ignored_values: set[str]
) -> Counter[str]:
    return Counter(
        item.value
        for item in items
        if not _authority_value_is_ignored(item, ignored_values)
    )


def _authority_value_is_ignored(
    item: AnchorOccurrence, ignored_values: set[str]
) -> bool:
    numeric = re.search(r"\d+(?:\.\d+)?", item.value)
    return bool(
        item.is_length_bound and numeric and numeric.group(0) in ignored_values
    )


def _fields_changed(
    original: tuple[str, ...],
    candidate: tuple[str, ...],
    authority: tuple[str, ...],
    allowed_labels: Iterable[str],
) -> bool:
    allowed = Counter(label.strip() for label in (*authority, *allowed_labels) if label.strip())
    for label in original:
        if allowed[label] > 0:
            allowed[label] -= 1
    original_index = 0
    additions: list[str] = []
    for label in candidate:
        if original_index < len(original) and label == original[original_index]:
            original_index += 1
        else:
            additions.append(label)
    if original_index != len(original):
        return True
    for label in additions:
        if allowed[label] <= 0:
            return True
        allowed[label] -= 1
    return False


def _contexts_by_value(items: Iterable[AnchorOccurrence]) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    for item in items:
        result.setdefault(item.value, []).append(item.context)
    return result


def _relation_items(
    original: AnchorSnapshot, candidate: AnchorSnapshot
) -> list[dict[str, Any]]:
    relations: list[dict[str, Any]] = []
    for kind in ("numbers", "quantities", "quotes"):
        before = _contexts_by_value(getattr(original, kind))
        after = _contexts_by_value(getattr(candidate, kind))
        for value in sorted(set(before) & set(after)):
            if before[value] != after[value]:
                relations.append(
                    {
                        "kind": kind[:-1],
                        "value": value,
                        "original_contexts": before[value],
                        "candidate_contexts": after[value],
                        "check": "same_subject_object_matter_and_state",
                    }
                )
    if original.state_contexts != candidate.state_contexts:
        relations.append(
            {
                "kind": "state",
                "original_contexts": list(original.state_contexts),
                "candidate_contexts": list(candidate.state_contexts),
                "check": "no_pending_or_planned_state_upgrade",
            }
        )
    return relations


def _missing_and_added(
    original: Iterable[AnchorOccurrence],
    candidate: Iterable[AnchorOccurrence],
    authority: Iterable[AnchorOccurrence],
    ignored_values: set[str],
) -> tuple[list[str], list[str]]:
    original_counter = _counter(original)
    candidate_counter = _counter(candidate)
    allowed = original_counter | _filtered_authority_counter(authority, ignored_values)
    missing = sorted(value for value in original_counter if candidate_counter[value] == 0)
    added = sorted(value for value in candidate_counter if allowed[value] == 0)
    return missing, added


def compare(
    original_text: str,
    candidate_text: str,
    authority_text: str = "",
    *,
    ignored_authority_values: Iterable[str] = (),
    allowed_field_labels: Iterable[str] = (),
) -> dict[str, Any]:
    original = snapshot(original_text)
    candidate = snapshot(candidate_text)
    authority = snapshot(authority_text)
    ignored = set(ignored_authority_values)
    violations: dict[str, Any] = {}
    for kind in ("numbers", "quantities", "quotes"):
        missing, added = _missing_and_added(
            getattr(original, kind),
            getattr(candidate, kind),
            getattr(authority, kind),
            ignored,
        )
        violations[f"missing_{kind}"] = missing
        violations[f"added_{kind}"] = added
    violations["fields_changed"] = _fields_changed(
        original.fields,
        candidate.fields,
        authority.fields,
        allowed_field_labels,
    )
    reason = next(
        (
            kind
            for kind in ("numbers", "quantities", "quotes")
            if violations[f"missing_{kind}"] or violations[f"added_{kind}"]
        ),
        "fields" if violations["fields_changed"] else None,
    )
    reductions: list[dict[str, Any]] = []
    for kind in ("numbers", "quantities", "quotes"):
        before = _counter(getattr(original, kind))
        after = _counter(getattr(candidate, kind))
        reductions.extend(
            {
                "kind": kind[:-1],
                "value": value,
                "before": count,
                "after": after[value],
            }
            for value, count in sorted(before.items())
            if 0 < after[value] < count
        )
    relations = [] if reason else _relation_items(original, candidate)
    return {
        "status": "fallback" if reason else ("semantic_review_required" if relations else "pass"),
        "mechanical_ok": reason is None,
        "reason": reason,
        "violations": violations,
        "count_reductions": reductions,
        "relation_packet": relations,
        "original": original.to_payload(),
        "candidate": candidate.to_payload(),
    }
