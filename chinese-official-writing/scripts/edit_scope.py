#!/usr/bin/env python3
"""Compare or generate a candidate from explicit replacements in the original."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

from material_diff import occurrences, read_plain


def text_sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def expected_text(original: str, plan: dict) -> str:
    if not isinstance(plan, dict) or set(plan) - {"edits", "source_sha256"}:
        raise ValueError("计划只能包含 edits 和可选 source_sha256")
    if "source_sha256" in plan:
        digest = plan["source_sha256"]
        if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-fA-F]{64}", digest):
            raise ValueError("source_sha256 必须是64位十六进制字符串")
        if digest.lower() != text_sha256(original):
            raise ValueError("source_sha256 不匹配：请核对最新版原稿")
    edits = plan.get("edits")
    if not isinstance(edits, list):
        raise ValueError("edits 必须是列表；空列表表示逐字保留")
    spans = []
    for index, edit in enumerate(edits):
        label = f"edits[{index}]"
        if not isinstance(edit, dict) or set(edit) - {"old", "new", "start"}:
            raise ValueError(f"{label}: 只能包含 old、new 和可选 start")
        old, new = edit.get("old"), edit.get("new")
        if not isinstance(old, str) or not old or not isinstance(new, str):
            raise ValueError(f"{label}: old 必须非空，new 必须为字符串")
        if "start" in edit:
            start = edit["start"]
            if type(start) is not int or start < 0 or not original.startswith(old, start):
                raise ValueError(f"{label}: start 必须指向原稿中 old 的起点")
        else:
            found = occurrences(original, old)
            if len(found) != 1:
                raise ValueError(f"{label}: old 出现 {len(found)} 次；请核对原文，重复目标须指定 start")
            start = found[0]
        spans.append((start, start + len(old), new))
    spans.sort(key=lambda item: item[0])
    cursor, parts = 0, []
    for start, end, new in spans:
        if start < cursor:
            raise ValueError("替换范围重叠；所有 start 均相对于修改前原稿")
        parts.extend((original[cursor:start], new))
        cursor = end
    return "".join([*parts, original[cursor:]])


def check_scope(original: str, candidate: str, plan: dict) -> dict:
    expected = expected_text(original, plan)
    matches = expected == candidate
    difference = None
    if not matches:
        start = next((i for i, (a, b) in enumerate(zip(expected, candidate)) if a != b),
                     min(len(expected), len(candidate)))
        left = max(0, start - 24)
        difference = {
            "offset": start, "context_start": left,
            "expected_context": expected[left:start + 40],
            "candidate_context": candidate[left:start + 40],
        }
    return {
        "scope": "exact-text-replacement-plan", "matches": matches,
        "source_sha256": text_sha256(original), "edit_count": len(plan["edits"]),
        "expected_length": len(expected), "candidate_length": len(candidate),
        "first_difference": difference,
    }


def write_candidate(original: str, plan: dict, output: str) -> dict:
    """Apply the validated literal plan to a new file; never overwrite a draft."""
    expected = expected_text(original, plan)
    path = Path(output)
    if path.suffix.lower() not in {".txt", ".md"}:
        raise ValueError("输出仅支持新的 UTF-8 TXT/MD 文件")
    payload = expected.encode("utf-8")
    with path.open("xb") as stream:
        stream.write(payload)
    return {
        "scope": "exact-text-replacement-plan", "action": "created",
        "output": str(path), "source_sha256": text_sha256(original),
        "output_sha256": hashlib.sha256(payload).hexdigest(),
        "edit_count": len(plan["edits"]), "output_length": len(expected),
    }


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--original", required=True, help="最新版原稿，UTF-8 TXT/MD。")
    destination = parser.add_mutually_exclusive_group(required=True)
    destination.add_argument("--candidate", help="比较改后稿件，UTF-8 TXT/MD。")
    destination.add_argument("--output", help="按计划生成新的 UTF-8 TXT/MD，不覆盖已有文件。")
    parser.add_argument("--plan", required=True, help="依本轮修改要求预先确定的 JSON 替换计划。")
    args = parser.parse_args(argv)
    try:
        plan = json.loads(Path(args.plan).read_bytes().decode("utf-8-sig"))
        original = read_plain(args.original)
        if args.output is not None:
            report = write_candidate(original, plan, args.output)
        else:
            report = check_scope(original, read_plain(args.candidate), plan)
    except (ValueError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if args.output is not None or report["matches"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
