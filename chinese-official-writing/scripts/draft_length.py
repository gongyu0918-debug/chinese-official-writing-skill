#!/usr/bin/env python3
"""Measure draft length before substantive review."""

from __future__ import annotations

import argparse
from dataclasses import asdict
import json
import re
import sys
from pathlib import Path

# Resolve the packaged sibling module even when the host enables safe-path mode.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from material_diff import audit_material
from prose_lint import InputReadError, body_lines, printable, read_text, scan

TRIAL_NOTICE = "文后提示：本稿为拟生成稿件。"
COUNT_SCOPES = ("auto", "full")

# Unicode 17.0 assigned CJK unified/compatibility ideographs plus ideographic zero.
# Pin the repertoire rather than depending on the host Python Unicode database.
# Sources: https://www.unicode.org/Public/17.0.0/ucd/PropList.txt
#          https://www.unicode.org/Public/17.0.0/ucd/UnicodeData.txt
CJK_IDEOGRAPHS = re.compile(
    r"[\u3007\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufa6d\ufa70-\ufad9"
    r"\U00020000-\U0002a6df\U0002a700-\U0002b81d\U0002b820-\U0002cead"
    r"\U0002ceb0-\U0002ebe0\U0002ebf0-\U0002ee5d\U0002f800-\U0002fa1d"
    r"\U00030000-\U0003134a\U00031350-\U00033479]"
)


def count_length(text: str, mode: str = "nonspace") -> int:
    """Count non-whitespace characters or CJK ideographs as a pure function."""
    if mode == "cjk":
        return len(CJK_IDEOGRAPHS.findall(text))
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
    count_scope: str = "auto",
) -> dict:
    if count_scope not in COUNT_SCOPES:
        raise ValueError(f"unsupported count scope: {count_scope}")
    if count_scope == "full":
        draft = text
        scope = "full-text"
    elif delivery_mode == "gap-note-allowed":
        draft = "\n".join(body_lines(text.splitlines()))
        scope = "draft-before-postscript"
    elif delivery_mode == "review-only":
        draft = text
        scope = "full-review"
    else:
        draft = text
        scope = "full-draft"
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
        "scope": scope,
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


def run_bundle_audit(payload: dict, args: argparse.Namespace) -> dict:
    """一次零落盘调用同时完成字数实测、全项规则体检与素材↔成稿数字/日期/书名号对账。"""
    if not isinstance(payload, dict):
        raise ValueError("--bundle-stdin 输入必须为 JSON 对象")
    draft = payload.get("draft")
    if not isinstance(draft, str):
        raise ValueError("--bundle-stdin JSON 必须包含字符串字段 draft")
    source = payload.get("source")
    if source is not None and not isinstance(source, str):
        raise ValueError("--bundle-stdin 字段 source 若提供则必须为字符串")

    count_mode = payload.get("count_mode", args.count_mode)
    count_scope = payload.get("count_scope", args.count_scope)
    min_chars = payload.get("min_chars", args.min_chars)
    max_chars = payload.get("max_chars", args.max_chars)
    trial = bool(payload.get("trial", args.trial))
    delivery_mode = payload.get("delivery_mode") or args.delivery_mode or ("gap-note-allowed" if trial else "draft-body")
    allow_markdown = bool(payload.get("allow_markdown", args.allow_markdown))
    public_release = bool(payload.get("public", args.public))
    include_outline = bool(payload.get("outline", args.outline))

    if count_mode not in ("nonspace", "cjk"):
        raise ValueError(f"unsupported count_mode: {count_mode}")
    if count_scope not in COUNT_SCOPES:
        raise ValueError(f"unsupported count_scope: {count_scope}")
    if delivery_mode not in ("draft-body", "gap-note-allowed", "review-only"):
        raise ValueError(f"unsupported delivery_mode: {delivery_mode}")
    if trial and delivery_mode == "review-only":
        raise ValueError("trial 模式不适用于 review-only")
    if any(v is not None and (isinstance(v, bool) or not isinstance(v, int) or v < 0) for v in (min_chars, max_chars)):
        raise ValueError("min_chars / max_chars 必须为非负整数")
    if min_chars is not None and max_chars is not None and min_chars > max_chars:
        raise ValueError("min_chars 不得大于 max_chars")

    report = measure_draft(
        "<stdin:bundle>",
        draft,
        count_mode,
        min_chars,
        max_chars,
        delivery_mode,
        include_outline,
        count_scope,
    )
    if trial:
        lines = draft.strip().splitlines()
        report["trial_notice"] = {
            "required": TRIAL_NOTICE,
            "ok": len(lines) >= 3 and not lines[-2].strip() and lines[-1].strip() == TRIAL_NOTICE,
        }
        if not report["trial_notice"]["ok"]:
            report["trial_notice"]["next_step"] = (
                "先核对入口模式：真实稿应移除误传的 --trial，不得为通过检查改贴试写标签；"
                "只有确属试写时才补齐固定文后标识。"
            )
    findings = scan(
        "<stdin:bundle>",
        draft,
        include_format=True,
        include_structure=True,
        delivery_mode=delivery_mode,
        allow_markdown=allow_markdown,
        public_release=public_release,
    )
    report["review_candidates"] = [asdict(finding) for finding in findings]
    report["review_scope"] = "full-text"
    report["facts_verified"] = False
    if source:
        report["fact_reconcile"] = audit_material(source, draft)
    return report


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Measure Chinese draft length and report optional bounds.")
    parser.add_argument("files", nargs="*", help="TXT/MD/DOCX paths, or '-' for stdin (omit when using --bundle-stdin).")
    parser.add_argument("--encoding", help="Encoding for text files.")
    parser.add_argument("--count-mode", choices=("nonspace", "cjk"), default="nonspace")
    parser.add_argument(
        "--count-scope",
        choices=("auto", "full"),
        default="auto",
        help="auto follows delivery mode; full always counts the complete input.",
    )
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
    parser.add_argument(
        "--bundle-stdin",
        action="store_true",
        help="一次零落盘全项体检：从标准输入读取 JSON（含 draft、可选 source/min_chars/max_chars/public），合并输出字数、全项风险扫描与素材对账。",
    )
    parser.add_argument("--trial", action="store_true", help="Require the fixed final trial-draft notice; never infer drafting intent.")
    parser.add_argument("--delivery-mode", choices=("draft-body", "gap-note-allowed", "review-only"), default=None)
    parser.add_argument("--allow-markdown", action="store_true")
    parser.add_argument("--public", action="store_true", help="With --scan or --bundle-stdin, also check for unmasked phone numbers, ID cards, apartment addresses, and internal/secret markers.")
    parser.add_argument(
        "--include-hidden",
        action="store_true",
        help="Include DOCX hidden runs (w:vanish) in character counts; skipped by default.",
    )
    args = parser.parse_args(argv)
    if args.bundle_stdin:
        if args.files and args.files != ["-"]:
            parser.error("--bundle-stdin cannot be combined with positional file arguments")
        try:
            raw = sys.stdin.read().lstrip("\ufeff")
            payload = json.loads(raw)
            report = run_bundle_audit(payload, args)
        except (ValueError, OSError) as exc:
            print(printable(f"ERROR: {exc}"), file=sys.stderr)
            return 2
        print(printable(json.dumps(report, ensure_ascii=False, indent=2)))
        if report.get("trial_notice") and not report["trial_notice"]["ok"]:
            return 1
        if args.fail_on_violation and report["status"] in {"below", "above"}:
            return 1
        return 0
    if not args.files:
        parser.error("the following arguments are required: files (or pass --bundle-stdin)")
    if args.delivery_mode is None:
        args.delivery_mode = "gap-note-allowed" if args.trial else "draft-body"
    if args.trial and args.delivery_mode == "review-only":
        parser.error("--trial applies to a draft, not review-only output")
    if any(value is not None and value < 0 for value in (args.min_chars, args.max_chars)):
        parser.error("length bounds must be non-negative")
    if args.min_chars is not None and args.max_chars is not None and args.min_chars > args.max_chars:
        parser.error("--min-chars must not exceed --max-chars")
    reports = []
    had_error = False
    for file_arg in args.files:
        docx_format_findings = []
        try:
            path, text = read_text(
                file_arg, args.encoding, docx_scope="main-document",
                docx_format_findings=docx_format_findings if args.scan else None,
                docx_skip_hidden=not args.include_hidden,
            )
        except InputReadError as exc:
            print(printable(f"ERROR: {exc}"), file=sys.stderr)
            had_error = True
            continue
        report = measure_draft(
            path, text, args.count_mode, args.min_chars, args.max_chars,
            args.delivery_mode, args.outline, args.count_scope,
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
                findings = scan(
                    path, text, include_format=True, include_structure=True,
                    delivery_mode=args.delivery_mode, allow_markdown=args.allow_markdown,
                    public_release=args.public,
                )
                findings.extend(docx_format_findings)
                report["review_candidates"] = [asdict(finding) for finding in findings]
                report["review_scope"] = (
                    "main-document" if Path(file_arg).suffix.lower() == ".docx" else "full-text"
                )
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
