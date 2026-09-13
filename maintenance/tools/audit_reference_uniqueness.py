"""Detect exact repeated prose and selected misplaced delivery instructions.

This is a deliberately conservative audit: it catches repeated substantive
sentences and body-only delivery instructions outside the delivery page. Route
tables and code examples are excluded because they are indexes or data, not
duplicate writing rules.
Semantic duplication, conflicts and conditional routing require separate review.
"""

from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PRODUCT = ROOT / "chinese-official-writing"
DELIVERY_PAGE = PRODUCT / "references" / "writing-rules.md"

BODY_ONLY_MARKERS = (
    "只要稿件",
    "只要正文",
    "只输出正文",
    "不需说明",
    "不需要解释",
    "直接给我成稿",
    "用户只想要正文",
)


def _prose_lines(path: Path):
    fenced = False
    for number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()
        if line.startswith("```"):
            fenced = not fenced
            continue
        if fenced or not line or line.startswith(("#", "|", ">")):
            continue
        # Strip list markers, links and inline spacing for exact-line matching.
        normalized = re.sub(r"^[-*+]\s+", "", line)
        normalized = " ".join(normalized.split())
        if len(normalized) < 28:
            continue
        yield number, normalized


def _delivery_lines(path: Path) -> set[int]:
    """Allow delivery preferences only inside the common workflow's final step."""
    lines = path.read_text(encoding="utf-8").splitlines()
    start = next((i for i, value in enumerate(lines, 1) if value.strip() == "## 第四步：交付"), None)
    if start is None:
        return set()
    end = next((i for i, value in enumerate(lines[start:], start + 1) if value.startswith("## ")), len(lines) + 1)
    return set(range(start, end))


def audit() -> list[str]:
    errors: list[str] = []
    markdown = [PRODUCT / "SKILL.md", *sorted((PRODUCT / "references").glob("*.md"))]

    homepage = (PRODUCT / "SKILL.md").read_text(encoding="utf-8")
    entry = homepage.split("## 入口契约", 1)[1].split("## 路由主线", 1)[0]
    if any(marker in entry for marker in BODY_ONLY_MARKERS):
        errors.append("SKILL.md: body-only delivery marker leaked into entry contract")
    index = (PRODUCT / "references" / "reference-index.md").read_text(encoding="utf-8")
    if "正文直交付" in index:
        errors.append("reference-index.md: body-only delivery was left in entrance task selection")

    # The common page also contains intake and review. Exempt only its delivery
    # section so relocating a preference into intake still fails the audit.
    for path in markdown:
        rel = path.relative_to(PRODUCT).as_posix()
        allowed_lines = _delivery_lines(path) if path == DELIVERY_PAGE else set()
        for number, line in _prose_lines(path):
            if any(marker in line for marker in BODY_ONLY_MARKERS):
                if number in allowed_lines:
                    continue
                errors.append(f"{rel}:{number}: body-only delivery rule outside delivery page")

    # Exact substantive prose repeated across pages should have one owner.
    occurrences: defaultdict[str, list[tuple[str, int]]] = defaultdict(list)
    for path in markdown:
        rel = path.relative_to(PRODUCT).as_posix()
        for number, line in _prose_lines(path):
            occurrences[line].append((rel, number))
    for line, places in occurrences.items():
        if len(places) > 1:
            joined = "; ".join(f"{rel}:{number}" for rel, number in places)
            errors.append(f"duplicate substantive rule: {joined}: {line}")
    return errors


if __name__ == "__main__":
    problems = audit()
    if problems:
        print("\n".join(problems))
        raise SystemExit(1)
    print("exact-line audit passed: no repeated substantive lines or selected misplaced body-only rules; semantic review remains separate")
