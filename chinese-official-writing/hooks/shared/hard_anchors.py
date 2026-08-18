#!/usr/bin/env python3
"""Shared hard-anchor snapshots for bounded Hook revisions."""

from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass
import re
from typing import Any, Final, Iterable


NUMBER_RE: Final = re.compile(
    r"(?<![A-Za-z0-9])\d+(?:\.\d+)?(?:万元|元|年|月|日|时|分|秒|台|件|项|人次|人|页|份|条|个|号)?(?![A-Za-z0-9])"
)
CJK_QUANTITY_RE: Final = re.compile(
    r"[一二三四五六七八九十百千万两]+(?:台|件|项|次|个月|年|天|份|人|套|批|元)"
)
QUOTE_RE: Final = re.compile(r"“[^”\n]+”|‘[^’\n]+’|\"[^\"\n]+\"")
FIELD_RE: Final = re.compile(r"(?m)^(?P<label>[\u4e00-\u9fffA-Za-z][^：:\n]{0,18})[：:]")
STATE_CUE_RE: Final = re.compile(r"拟|尚未|未形成|正在|仍在|待核实|待审批|待研究")
CLAUSE_BOUNDARY_RE: Final = re.compile(r"[\n。！？；;]")


@dataclass(frozen=True)
class AnchorOccurrence:
    kind: str
    value: str
    start: int
    end: int
    context: str


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
        )
        for match in pattern.finditer(text)
    )


def snapshot(text: str) -> AnchorSnapshot:
    return AnchorSnapshot(
        numbers=_occurrences(text, NUMBER_RE, "number"),
        quantities=_occurrences(text, CJK_QUANTITY_RE, "quantity"),
        quotes=_occurrences(text, QUOTE_RE, "quote"),
        fields=tuple(match.group("label").strip() for match in FIELD_RE.finditer(text)),
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
    return Counter(item.value for item in items if item.value not in ignored_values)


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
    violations["fields_changed"] = candidate.fields != original.fields
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
