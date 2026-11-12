#!/usr/bin/env python3
"""Count and hash long-writing outputs without writing any files."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path


LIMITS = {
    "L1": (3000, 3800),
    "L2": (3000, 4000),
    "L3": (1500, 2200),
    "L4": (3000, 3800),
    "L5": (1800, 2500),
    "L6": (2200, 3000),
    "L7": (2200, 3000),
    "L8": (1500, 2200),
    "L9": (3000, 4000),
    "L12": (800, 1200),
}


def count(text: str) -> int:
    return len(re.sub(r"\s+", "", text))


def scoped_text(case_id: str, text: str) -> tuple[str, str | None]:
    lines = text.splitlines(keepends=True)
    if case_id == "L4":
        indexes = [i for i, line in enumerate(lines) if "排版方案" in line]
        if not indexes:
            raise ValueError("L4 missing 排版方案 boundary")
        split = indexes[-1]
        return "".join(lines[:split]), "".join(lines[split:])
    if case_id == "L12":
        indexes = [i for i, line in enumerate(lines) if "消息正文" in line]
        if indexes:
            split = indexes[-1]
            return "".join(lines[split + 1 :]), None
        table_indexes = [i for i, line in enumerate(lines) if line.lstrip().startswith("|")]
        if not table_indexes:
            raise ValueError("L12 missing 消息正文 or source-table boundary")
        return "".join(lines[table_indexes[-1] + 1 :]), None
    return text, None


def main() -> int:
    root = Path(sys.argv[1])
    reports = []
    for path in sorted(root.glob("L*-*.md")):
        match = re.match(r"(L\d+)-([AB]\d*)\.md$", path.name)
        if not match:
            continue
        case_id, side = match.groups()
        raw = path.read_bytes()
        text = raw.decode("utf-8-sig")
        report = {
            "id": case_id,
            "side": side,
            "path": str(path),
            "bytes": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest(),
            "full_nonspace": count(text),
        }
        try:
            scoped, secondary = scoped_text(case_id, text)
            scoped_count = count(scoped)
            report["scope_nonspace"] = scoped_count
            if secondary is not None:
                report["secondary_nonspace"] = count(secondary)
            if case_id in LIMITS:
                minimum, maximum = LIMITS[case_id]
                report["min_chars"] = minimum
                report["max_chars"] = maximum
                report["within"] = minimum <= scoped_count <= maximum
        except ValueError as exc:
            report["scope_error"] = str(exc)
        reports.append(report)
    print(json.dumps(reports, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
