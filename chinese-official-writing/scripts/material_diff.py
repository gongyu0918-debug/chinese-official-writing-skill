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


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", help="本轮有效材料的 UTF-8 TXT/MD/DOCX 路径。")
    parser.add_argument("--draft", help="待核稿件的 UTF-8 TXT/MD/DOCX 路径。")
    parser.add_argument("--literal", action="append", help="明确选中的原文片段，可重复传入。")
    parser.add_argument(
        "--stdin",
        action="store_true",
        help="零落盘模式：从标准输入读取 UTF-8 JSON（包含 source、draft、literals 字段）。",
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
            if not isinstance(source_text, str) or not isinstance(draft_text, str) or not isinstance(literals, list):
                raise ValueError("--stdin JSON 必须包含字符串 source、draft 及列表 literals")
            report = compare_material(source_text, draft_text, literals)
            source_label, draft_label = "<stdin:source>", "<stdin:draft>"
        else:
            if not args.source or not args.draft or not args.literal:
                raise ValueError("非 --stdin 模式必须提供 --source、--draft 和至少一个 --literal")
            uses_docx = any(Path(p).suffix.lower() == ".docx" for p in (args.source, args.draft))
            report = compare_material(
                read_material_input(args.source),
                read_material_input(args.draft),
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
