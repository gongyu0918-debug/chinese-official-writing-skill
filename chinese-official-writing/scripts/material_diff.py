#!/usr/bin/env python3
"""Locate selected literal text in effective material and draft; no fact verdicts."""

from __future__ import annotations

import argparse
from bisect import bisect_right
import json
from pathlib import Path
import re
import sys

# Resolve the packaged sibling module even when the host enables safe-path mode.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from prose_lint import InputReadError, read_docx


def read_plain(path: str) -> str:
    """Read UTF-8 TXT/MD strictly, preserving whitespace and line endings."""
    if Path(path).suffix.lower() not in {".txt", ".md"}:
        raise ValueError(f"仅支持 UTF-8 TXT/MD: {path}")
    return Path(path).read_bytes().decode("utf-8-sig")


def read_material_input(path: str) -> str:
    """Read UTF-8 TXT/MD or DOCX for literal location checks."""
    target = Path(path)
    if target.suffix.lower() == ".docx":
        try:
            return read_docx(target, scope="main-document", skip_hidden=True)
        except InputReadError as exc:
            raise ValueError(str(exc)) from exc
    return read_plain(path)


def occurrences(text: str, literal: str) -> list[int]:
    if not isinstance(literal, str) or not literal:
        raise ValueError("literal 必须为非空字符串")
    positions = []
    start = text.find(literal)
    while start != -1:
        positions.append(start)
        start = text.find(literal, start + 1)
    return positions


def locate(text: str, literal: str) -> list[dict]:
    lines = [0, *(m.end() for m in re.finditer(r"\r\n|\r|\n", text))]
    result = []
    for start in occurrences(text, literal):
        line = bisect_right(lines, start)
        end = start + len(literal)
        left = max(0, start - 24)
        result.append({
            "start": start, "end": end, "line": line,
            "column": start - lines[line - 1] + 1,
            "context_start": left, "context": text[left:end + 24],
        })
    return result


def compare_material(
    source: str,
    draft: str,
    literals: list[str],
    *,
    scope: str = "full-input-exact-literals",
    notice: str = "仅定位所选原文；未出现不等于遗漏或错误，出现也不证明事实正确。请核对上下文。",
) -> dict:
    if not literals:
        raise ValueError("必须明确选择至少一个 literal")
    # Validate before deduplicating so invalid inputs produce a useful error.
    for literal in literals:
        if not isinstance(literal, str) or not literal:
            raise ValueError("literal 必须为非空字符串")
    return {
        "scope": scope,
        "notice": notice,
        "items": [{
            "literal": literal,
            "source": locate(source, literal),
            "draft": locate(draft, literal),
        } for literal in dict.fromkeys(literals)],
    }


DATE_PATTERN = re.compile(
    r"(?<!\d)(?:20\d{2}\s*[年.\-/]\s*\d{1,2}\s*[月.\-/]\s*\d{1,2}\s*日?"
    r"|(?<!年)\d{1,2}\s*月\s*\d{1,2}\s*日)(?!\d)"
)
QUANTITY_PATTERN = re.compile(
    r"(?<!\d)\d+(?:\.\d+)?\s*"
    r"(?:亿元|万元|元|个百分点|百分点|%|％|个工作日|工作日|人次|人|家次|家|处|项|条|件|套|台|份|名|场|轮|次|个|天|日|小时|分钟|个月|年|月"
    r"|kVA|kW|MW|TB|GB|PB|万平方米|平方米|亩|公里|吨|公斤)"
)
TITLE_PATTERN = re.compile(r"《([^《》\n]{2,48})》")


def _normalize_date(raw: str) -> str:
    nums = re.findall(r"\d+", raw)
    if len(nums) == 3:
        return f"{int(nums[0])}年{int(nums[1])}月{int(nums[2])}日"
    if len(nums) == 2:
        return f"{int(nums[0])}月{int(nums[1])}日"
    return raw.strip()


def _extract_dates(text: str) -> list[str]:
    seen: list[str] = []
    for m in DATE_PATTERN.finditer(text):
        norm = _normalize_date(m.group(0))
        if norm not in seen:
            seen.append(norm)
    return seen


def _date_covered(target: str, pool: set[str]) -> bool:
    if target in pool:
        return True
    # "11月15日" is covered if "2026年11月15日" is in pool, and vice versa only if month-day matches when year wasn't repeated
    if not re.match(r"^\d{4}年", target):
        return any(item.endswith(target) for item in pool)
    return False


def _normalize_quantity(raw: str) -> str:
    s = re.sub(r"\s+", "", raw).replace("％", "%")
    m = re.match(r"^(\d+(?:\.\d+)?)(\D.*)$", s)
    if m:
        num, unit = m.group(1), m.group(2)
        if "." in num:
            num = num.rstrip("0").rstrip(".")
        else:
            num = str(int(num))
        s = f"{num}{unit}"
    return s


def _extract_quantities(text: str) -> list[str]:
    # Strip full dates first so "2026年"/"11月"/"15日" don't pollute quantity counts
    scrubbed = DATE_PATTERN.sub(" ", text)
    seen: list[str] = []
    for m in QUANTITY_PATTERN.finditer(scrubbed):
        norm = _normalize_quantity(m.group(0))
        if norm not in seen:
            seen.append(norm)
    return seen


def _extract_titles(text: str) -> list[str]:
    seen: list[str] = []
    for m in TITLE_PATTERN.finditer(text):
        t = f"《{m.group(1).strip()}》"
        if t not in seen:
            seen.append(t)
    return seen


def audit_material(source: str, draft: str) -> dict:
    """自动抽取素材与成稿中的日期、带单位数量与书名号专名进行双向对账。"""

    src_dates = _extract_dates(source)
    drf_dates = _extract_dates(draft)
    src_date_set, drf_date_set = set(src_dates), set(drf_dates)

    src_qtys = _extract_quantities(source)
    drf_qtys = _extract_quantities(draft)
    src_qty_set, drf_qty_set = set(src_qtys), set(drf_qtys)

    src_titles = _extract_titles(source)
    drf_titles = _extract_titles(draft)
    src_title_set, drf_title_set = set(src_titles), set(drf_titles)

    return {
        "scope": "auto-fact-reconcile",
        "notice": "自动对账仅作机械线索（合理合计/换算值或成文当天日期可能出现在 draft_only，有意删略项可能出现在 source_only），请结合业务语境逐项确认。",
        "draft_only_dates": [d for d in drf_dates if not _date_covered(d, src_date_set)],
        "source_only_dates": [d for d in src_dates if not _date_covered(d, drf_date_set)],
        "draft_only_quantities": [q for q in drf_qtys if q not in src_qty_set],
        "source_only_quantities": [q for q in src_qtys if q not in drf_qty_set],
        "draft_only_titles": [t for t in drf_titles if t not in src_title_set],
        "source_only_titles": [t for t in src_titles if t not in drf_title_set],
    }


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", help="本轮有效材料的 UTF-8 TXT/MD/DOCX 路径。")
    parser.add_argument("--draft", help="待核稿件的 UTF-8 TXT/MD/DOCX 路径。")
    parser.add_argument("--literal", action="append", help="明确选中的原文片段，可重复传入。")
    parser.add_argument(
        "--audit",
        action="store_true",
        help="自动抽取素材与成稿中的日期、带单位数量和《书名号》进行双向对账（可独立使用，无需传 --literal）。",
    )
    parser.add_argument(
        "--stdin",
        action="store_true",
        help="零落盘模式：从标准输入读取 UTF-8 JSON（包含 source、draft，以及非 --audit 模式下的 literals 字段）。",
    )
    args = parser.parse_args(argv)
    try:
        if args.stdin:
            if args.source or args.draft or args.literal:
                raise ValueError("--stdin 模式不可与 --source/--draft/--literal 混用")
            payload = json.loads(sys.stdin.read().lstrip("\ufeff"))
            if not isinstance(payload, dict):
                raise ValueError("--stdin 输入必须为 JSON 对象")
            source_text = payload.get("source")
            draft_text = payload.get("draft")
            literals = payload.get("literals")
            if not isinstance(source_text, str) or not isinstance(draft_text, str):
                raise ValueError("--stdin JSON 必须包含字符串 source 和 draft")
            if args.audit:
                report = audit_material(source_text, draft_text)
                if isinstance(literals, list) and literals:
                    report["literal_matches"] = compare_material(source_text, draft_text, literals)
            else:
                if not isinstance(literals, list):
                    raise ValueError("--stdin JSON 必须包含字符串 source、draft 及列表 literals")
                report = compare_material(source_text, draft_text, literals)
            source_label, draft_label = "<stdin:source>", "<stdin:draft>"
        else:
            if not args.source or not args.draft:
                raise ValueError("非 --stdin 模式必须提供 --source 和 --draft")
            if not args.audit and not args.literal:
                raise ValueError("非 --audit 模式必须提供至少一个 --literal")
            src_content = read_material_input(args.source)
            drf_content = read_material_input(args.draft)
            if args.audit:
                report = audit_material(src_content, drf_content)
                if args.literal:
                    report["literal_matches"] = compare_material(src_content, drf_content, args.literal)
            else:
                uses_docx = any(Path(p).suffix.lower() == ".docx" for p in (args.source, args.draft))
                report = compare_material(
                    src_content,
                    drf_content,
                    args.literal,
                    scope="docx-main-document-extracted-literals" if uses_docx else "full-input-exact-literals",
                    notice=(
                        "含 DOCX 输入：位置为 DOCX 主文档提取文本坐标（不含页眉页脚/批注/直接隐藏运行），不等于 Word 原生偏移；仅作定位参考，请核对上下文。"
                        if uses_docx
                        else "仅定位所选原文；未出现不等于遗漏或错误，出现也不证明事实正确。请核对上下文。"
                    ),
                )
            source_label, draft_label = args.source, args.draft
    except (ValueError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(json.dumps({"source": source_label, "draft": draft_label, **report}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
