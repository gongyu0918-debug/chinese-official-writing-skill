#!/usr/bin/env python3
"""Measure draft length before substantive review; no host lifecycle required."""

from __future__ import annotations

import argparse
from dataclasses import asdict
import json
import re
import sys
from pathlib import Path

# Resolve the packaged sibling module even when the host enables safe-path mode.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from prose_lint import InputReadError, body_lines, printable, read_text, scan

TRIAL_NOTICE = "文后提示：本稿为拟生成稿件。"


def count_length(text: str, mode: str = "nonspace") -> int:
    """Reuse the existing review-gate counting convention as a pure function."""
    if mode == "cjk":
        return len(re.findall(r"[\u3400-\u4dbf\u4e00-\u9fff]", text))
    if mode != "nonspace":
        raise ValueError(f"unsupported count mode: {mode}")
    return len(re.sub(r"\s+", "", text))


def outline_entries(text: str, mode: str) -> list[dict]:
    """观察用：各段首句与字数占比，不判断主旨正确或篇幅是否达标。"""

    stripped = text.strip()
    if not stripped:
        return []
    base_offset = len(text) - len(text.lstrip())
    separator = re.compile(r"\r?\n[ \t]*\r?\n")
    segments: list[tuple[int, str]] = []
    cursor = 0
    for match in separator.finditer(stripped):
        segments.append((cursor, stripped[cursor:match.start()]))
        cursor = match.end()
    segments.append((cursor, stripped[cursor:]))
    blocks = [(offset, block) for offset, block in segments if block.strip()]
    if len(blocks) == 1 and "\n" in blocks[0][1]:
        offset, block = blocks[0]
        blocks = []
        for line_match in re.finditer(r"[^\r\n]+", block):
            if line_match.group(0).strip():
                blocks.append((offset + line_match.start(), line_match.group(0)))
    total = count_length(stripped, mode)
    entries: list[dict] = []
    line_no = 1
    consumed = 0
    for offset, block in blocks:
        start = base_offset + offset
        line_no += text[consumed:start].count("\n")
        consumed = start
        content = block.strip()
        sentence = re.match(r"[^。！？!?\n]*(?:[。！？!?]|$)", content)
        first_sentence = sentence.group(0).strip() if sentence else content
        if len(first_sentence) > 80:
            first_sentence = first_sentence[:80] + "…"
        block_count = count_length(content, mode)
        entries.append({
            "line": line_no,
            "first_sentence": first_sentence,
            "count": block_count,
            "ratio": round(block_count / total, 4) if total else 0.0,
        })
    return entries


def measure_draft(
    path: str,
    text: str,
    mode: str = "nonspace",
    minimum: int | None = None,
    maximum: int | None = None,
    delivery_mode: str = "draft-body",
    include_outline: bool = False,
) -> dict:
    draft = text if delivery_mode == "review-only" else "\n".join(body_lines(text.splitlines()))
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
    report = {
        "path": path,
        "mode": mode,
        "scope": "full-review" if delivery_mode == "review-only" else "draft-before-postscript",
        "count": count,
        "minimum": minimum,
        "maximum": maximum,
        "status": status,
        "below_by": below,
        "above_by": above,
    }
    if include_outline:
        report["outline"] = outline_entries(draft, mode)
    return report


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
    parser.add_argument("--outline", action="store_true", help="观察用列出各段首句和字数占比；不判断主旨或篇幅是否达标。")
    parser.add_argument("--scan", action="store_true", help="Also scan the same text for prose, structure and format risks; emits JSON.")
    parser.add_argument("--trial", action="store_true", help="Require the fixed final trial-draft notice; never infer drafting intent.")
    parser.add_argument("--delivery-mode", choices=("draft-body", "gap-note-allowed", "review-only"), default="draft-body")
    parser.add_argument("--allow-markdown", action="store_true")
    args = parser.parse_args(argv)
    if args.trial and args.delivery_mode == "review-only":
        parser.error("--trial applies to a draft, not review-only output")
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
            print(printable(f"ERROR: {exc}"), file=sys.stderr)
            had_error = True
            continue
        report = measure_draft(
            path, text, args.count_mode, args.min_chars, args.max_chars,
            args.delivery_mode, args.outline,
        )
        if args.trial:
            lines = text.strip().splitlines()
            report["trial_notice"] = {
                "required": TRIAL_NOTICE,
                "ok": len(lines) >= 3 and not lines[-2].strip() and lines[-1].strip() == TRIAL_NOTICE,
            }
            if not report["trial_notice"]["ok"]:
                report["trial_notice"]["next_step"] = (
                    "先核对入口模式：真实稿应移除误传的 --trial，不得为通过检查改贴试写标签；"
                    "只有确属试写时才补齐固定文后标识。"
                )
        if args.scan:
            try:
                report["review_candidates"] = [asdict(finding) for finding in scan(
                    path, text, include_format=True, include_structure=True,
                    delivery_mode=args.delivery_mode, allow_markdown=args.allow_markdown)]
                report["facts_verified"] = False
            except InputReadError as exc:
                print(printable(f"ERROR: {exc}"), file=sys.stderr)
                had_error = True
        reports.append(report)
    if args.json or args.scan or args.trial:
        print(printable(json.dumps(reports, ensure_ascii=False, indent=2)))
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
            print(printable(f"{item['path']}: {item['count']} ({item['mode']}; {item['scope']}); {detail}"))
            for index, entry in enumerate(item.get("outline", []), start=1):
                percent = entry["ratio"] * 100
                print(printable(
                    f"  第 {index} 段（约第 {entry['line']} 行，{entry['count']} 字，占 {percent:.1f}%）：{entry['first_sentence']}"
                ))
    if had_error:
        return 2
    if args.trial and any(not item["trial_notice"]["ok"] for item in reports):
        return 1
    if args.fail_on_violation and any(item["status"] in {"below", "above"} for item in reports):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
