#!/usr/bin/env python3
"""Locate selected literal text in effective material and draft; no fact verdicts."""

from __future__ import annotations

import argparse
from bisect import bisect_right
import json
from pathlib import Path
import re
import sys


def read_plain(path: str) -> str:
    """Read UTF-8 TXT/MD strictly, preserving whitespace and line endings."""
    if Path(path).suffix.lower() not in {".txt", ".md"}:
        raise ValueError(f"仅支持 UTF-8 TXT/MD: {path}")
    return Path(path).read_bytes().decode("utf-8-sig")


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


def compare_material(source: str, draft: str, literals: list[str]) -> dict:
    if not literals:
        raise ValueError("必须明确选择至少一个 literal")
    # Validate before deduplicating so invalid inputs produce a useful error.
    for literal in literals:
        if not isinstance(literal, str) or not literal:
            raise ValueError("literal 必须为非空字符串")
    return {
        "scope": "full-input-exact-literals",
        "notice": "仅定位所选原文；未出现不等于遗漏或错误，出现也不证明事实正确。请核对上下文。",
        "items": [{
            "literal": literal,
            "source": locate(source, literal),
            "draft": locate(draft, literal),
        } for literal in dict.fromkeys(literals)],
    }


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, help="本轮有效材料的 UTF-8 TXT/MD 路径。")
    parser.add_argument("--draft", required=True, help="待核稿件的 UTF-8 TXT/MD 路径。")
    parser.add_argument("--literal", action="append", required=True, help="明确选中的原文片段，可重复传入。")
    args = parser.parse_args(argv)
    try:
        report = compare_material(read_plain(args.source), read_plain(args.draft), args.literal)
    except (ValueError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(json.dumps({"source": args.source, "draft": args.draft, **report}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
