"""Audit the user-facing Skill surface for leaked engineering instructions."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PRODUCT = ROOT / "chinese-official-writing"
PROHIBITED = (
    "git commit",
    "git push",
    "pytest",
    "python -m unittest",
    "worktree",
    "maintenance/",
    "开发命令",
    "构建命令",
)
ROUTING_DESCRIPTION_PHRASES = (
    "按交付模式和文种场景渐进读取规则",
    "按交付模式读取规则",
)
ALLOWED_TOOL_COMMANDS = {
    "references/prose-lint-usage.md",
    "references/delivery-review-gate.md",
}


def audit() -> list[str]:
    errors: list[str] = []
    files = [PRODUCT / "SKILL.md", *sorted((PRODUCT / "references").glob("*.md"))]
    for path in files:
        text = path.read_text(encoding="utf-8")
        rel = path.relative_to(PRODUCT).as_posix()
        lower = text.lower()
        for phrase in PROHIBITED:
            if phrase.lower() in lower:
                errors.append(f"{rel}: leaked engineering phrase {phrase!r}")
        if path.name == "SKILL.md":
            match = re.search(r"^description: (.+)$", text, re.MULTILINE)
            if not match:
                errors.append("SKILL.md: missing description")
            else:
                description = match.group(1)
                for phrase in ROUTING_DESCRIPTION_PHRASES:
                    if phrase in description:
                        errors.append(f"SKILL.md: description contains routing phrase {phrase!r}")
    return errors


if __name__ == "__main__":
    problems = audit()
    if problems:
        print("\n".join(problems))
        raise SystemExit(1)
    print("product surface clean: no engineering commands or routing prose in description")
