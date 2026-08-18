#!/usr/bin/env python3
from __future__ import annotations

from collections import Counter
import argparse
import json
import re
from typing import Any, Iterable


NUMBER_RE = re.compile(
    r"(?<![A-Za-z0-9])\d+(?:\.\d+)?(?:万元|元|年|月|日|时|分|秒|台|件|项|人次|人|页|份|条|个|号)?(?![A-Za-z0-9])"
)
QUOTE_RE = re.compile(r"“[^”\n]+”|‘[^’\n]+’|\"[^\"\n]+\"")
FIELD_RE = re.compile(r"(?m)^(?P<label>[\u4e00-\u9fffA-Za-z][^：:\n]{0,18})[：:]")
STATE_CUE_RE = re.compile(r"拟|尚未|未形成|正在|仍在|待核实|待审批|待研究")
CLAUSE_BOUNDARY_RE = re.compile(r"[\n。！？；;]")


def _clause(text: str, start: int, end: int) -> str:
    left = max((match.end() for match in CLAUSE_BOUNDARY_RE.finditer(text, 0, start)), default=0)
    right_match = CLAUSE_BOUNDARY_RE.search(text, end)
    right = right_match.start() if right_match else len(text)
    return re.sub(r"\s+", "", text[left:right].strip())


def _occurrences(text: str, pattern: re.Pattern[str], kind: str) -> list[dict[str, Any]]:
    return [
        {
            "kind": kind,
            "value": match.group(0),
            "start": match.start(),
            "end": match.end(),
            "context": _clause(text, match.start(), match.end()),
        }
        for match in pattern.finditer(text)
    ]


def snapshot(text: str) -> dict[str, Any]:
    return {
        "numbers": _occurrences(text, NUMBER_RE, "number"),
        "quotes": _occurrences(text, QUOTE_RE, "quote"),
        "fields": [match.group("label").strip() for match in FIELD_RE.finditer(text)],
        "state_contexts": [
            re.sub(r"\s+", "", clause)
            for clause in CLAUSE_BOUNDARY_RE.split(text)
            if STATE_CUE_RE.search(clause)
        ],
    }


def _counter(items: Iterable[dict[str, Any]]) -> Counter[str]:
    return Counter(str(item["value"]) for item in items)


def _relation_items(
    original: dict[str, Any], candidate: dict[str, Any]
) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for kind in ("numbers", "quotes"):
        original_by_value: dict[str, list[str]] = {}
        candidate_by_value: dict[str, list[str]] = {}
        for item in original[kind]:
            original_by_value.setdefault(str(item["value"]), []).append(str(item["context"]))
        for item in candidate[kind]:
            candidate_by_value.setdefault(str(item["value"]), []).append(str(item["context"]))
        for value in sorted(set(original_by_value) & set(candidate_by_value)):
            before = original_by_value[value]
            after = candidate_by_value[value]
            if before != after:
                items.append(
                    {
                        "kind": kind[:-1],
                        "value": value,
                        "original_contexts": before,
                        "candidate_contexts": after,
                        "check": "same_subject_object_matter_and_state",
                    }
                )
    if original["state_contexts"] != candidate["state_contexts"]:
        items.append(
            {
                "kind": "state",
                "original_contexts": original["state_contexts"],
                "candidate_contexts": candidate["state_contexts"],
                "check": "no_pending_or_planned_state_upgrade",
            }
        )
    return items


def compare(original_text: str, candidate_text: str, authority_text: str = "") -> dict[str, Any]:
    original = snapshot(original_text)
    candidate = snapshot(candidate_text)
    authority = snapshot(authority_text)
    original_numbers = _counter(original["numbers"])
    candidate_numbers = _counter(candidate["numbers"])
    allowed_numbers = original_numbers | _counter(authority["numbers"])
    missing_numbers = sorted(value for value in original_numbers if candidate_numbers[value] == 0)
    added_numbers = sorted(value for value in candidate_numbers if allowed_numbers[value] == 0)
    original_quotes = _counter(original["quotes"])
    candidate_quotes = _counter(candidate["quotes"])
    allowed_quotes = original_quotes | _counter(authority["quotes"])
    missing_quotes = sorted(value for value in original_quotes if candidate_quotes[value] == 0)
    added_quotes = sorted(value for value in candidate_quotes if allowed_quotes[value] == 0)
    fields_changed = candidate["fields"] != original["fields"]
    violations = {
        "missing_numbers": missing_numbers,
        "added_numbers": added_numbers,
        "missing_quotes": missing_quotes,
        "added_quotes": added_quotes,
        "fields_changed": fields_changed,
    }
    mechanical_ok = not any(
        (missing_numbers, added_numbers, missing_quotes, added_quotes, fields_changed)
    )
    reductions = [
        {"value": value, "before": count, "after": candidate_numbers[value]}
        for value, count in sorted(original_numbers.items())
        if 0 < candidate_numbers[value] < count
    ]
    relations = _relation_items(original, candidate) if mechanical_ok else []
    status = "fallback" if not mechanical_ok else ("semantic_review_required" if relations else "pass")
    return {
        "status": status,
        "mechanical_ok": mechanical_ok,
        "violations": violations,
        "safe_count_reductions": reductions,
        "relation_packet": relations,
        "original": original,
        "candidate": candidate,
    }


def self_test() -> dict[str, Any]:
    duplicate = "本次共核验75件工单。经逐项核对，75件工单均纳入范围，其中22件需要补充材料。"
    deduped = "本次共核验75件工单，其中22件需要补充材料。"
    dedup = compare(duplicate, deduped)
    assert dedup["mechanical_ok"]
    assert dedup["safe_count_reductions"] == [{"value": "75件", "before": 2, "after": 1}]

    dropped = compare(duplicate, "本次共核验75件工单。")
    assert dropped["status"] == "fallback" and dropped["violations"]["missing_numbers"] == ["22件"]

    added = compare("已核验12件工单。", "已核验12件工单，另有3件待办。")
    assert added["status"] == "fallback" and added["violations"]["added_numbers"] == ["3件"]

    quote = "王明强调：‘数据必须真实、准确、完整。’信息科于8月25日前完成核对。"
    quote_dropped = compare(quote, "王明作出工作强调，信息科于8月25日前完成核对。")
    assert quote_dropped["status"] == "fallback" and quote_dropped["violations"]["missing_quotes"]

    fields = "项目名称：档案数字化\n申请数量：6台\n预算金额：25200元"
    reordered = "申请数量：6台\n项目名称：档案数字化\n预算金额：25200元"
    assert compare(fields, reordered)["violations"]["fields_changed"]

    original = "运行管理科核验12件，客户服务科核验21件。"
    swapped = "运行管理科核验21件，客户服务科核验12件。"
    swap_result = compare(original, swapped)
    assert swap_result["mechanical_ok"] and swap_result["status"] == "semantic_review_required"
    assert {item["value"] for item in swap_result["relation_packet"]} == {"12件", "21件"}
    return {"controls": 6, "status": "PASS"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        print(json.dumps(self_test(), ensure_ascii=False))
        return 0
    parser.error("use --self-test")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
