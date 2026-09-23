#!/usr/bin/env python3
"""Measure draft length before substantive review; no host lifecycle required."""

from __future__ import annotations

import argparse
from dataclasses import asdict
import json
import re
import sys

from prose_lint import InputReadError, body_lines, read_text, scan


def count_length(text: str, mode: str = "nonspace") -> int:
    """Reuse the existing review-gate counting convention as a pure function."""
    if mode == "cjk":
        return len(re.findall(r"[\u3400-\u4dbf\u4e00-\u9fff]", text))
    if mode != "nonspace":
        raise ValueError(f"unsupported count mode: {mode}")
    return len(re.sub(r"\s+", "", text))


def measure_draft(
    path: str,
    text: str,
    mode: str = "nonspace",
    minimum: int | None = None,
    maximum: int | None = None,
) -> dict:
    draft = "\n".join(body_lines(text.splitlines()))
    count = count_length(draft, mode)
    below = max(minimum - count, 0) if minimum is not None else 0
    above = max(count - maximum, 0) if maximum is not None else 0
    if below:
        status = "below"
    elif above:
        status = "above"
    elif minimum is not None or maximum is not None:
        status = "within"
    else:
        status = "counted"
    return {
        "path": path,
        "mode": mode,
        "scope": "draft-before-postscript",
        "count": count,
        "minimum": minimum,
        "maximum": maximum,
        "status": status,
        "below_by": below,
        "above_by": above,
    }


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Measure Chinese draft length and report optional bounds.")
    parser.add_argument("files", nargs="+", help="TXT/MD/DOCX paths, or '-' for stdin.")
    parser.add_argument("--encoding", help="Encoding for text files.")
    parser.add_argument("--count-mode", choices=("nonspace", "cjk"), default="nonspace")
    parser.add_argument("--min-chars", type=int, help="Lower bound per input draft.")
    parser.add_argument("--max-chars", type=int, help="Upper bound per input draft.")
    parser.add_argument(
        "--fail-on-violation",
        action="store_true",
        help="Return exit code 1 when a supplied length bound is violated.",
    )
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--scan", action="store_true", help="Also scan the same text for prose, structure and format risks; emits JSON.")
    parser.add_argument("--delivery-mode", choices=("draft-body", "gap-note-allowed", "review-only"), default="draft-body")
    parser.add_argument("--allow-markdown", action="store_true")
    args = parser.parse_args(argv)
    if any(value is not None and value < 0 for value in (args.min_chars, args.max_chars)):
        parser.error("length bounds must be non-negative")
    if args.min_chars is not None and args.max_chars is not None and args.min_chars > args.max_chars:
        parser.error("--min-chars must not exceed --max-chars")
    reports = []
    had_error = False
    for file_arg in args.files:
        try:
            path, text = read_text(file_arg, args.encoding, docx_scope="main-document")
        except InputReadError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            had_error = True
            continue
        report = measure_draft(path, text, args.count_mode, args.min_chars, args.max_chars)
        if args.scan:
            report["review_candidates"] = [asdict(finding) for finding in scan(
                path, text, include_format=True, include_structure=True,
                delivery_mode=args.delivery_mode, allow_markdown=args.allow_markdown)]
            report["facts_verified"] = False
        reports.append(report)
    if args.json or args.scan:
        print(json.dumps(reports, ensure_ascii=False, indent=2))
    else:
        for item in reports:
            if item["below_by"]:
                detail = f"低于下限，差 {item['below_by']}"
            elif item["above_by"]:
                detail = f"超过上限，多 {item['above_by']}"
            elif item["status"] == "within":
                detail = "在范围内"
            else:
                detail = "已统计"
            print(f"{item['path']}: {item['count']} ({item['mode']}; {item['scope']}); {detail}")
    if had_error:
        return 2
    if args.fail_on_violation and any(item["status"] in {"below", "above"} for item in reports):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
