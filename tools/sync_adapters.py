#!/usr/bin/env python3
"""Sync the canonical skill into adapter layouts for other agent tools."""

from __future__ import annotations

import shutil
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CANONICAL = ROOT / "chinese-official-writing"
VERSION = "1.2.4"

TARGETS = {
    "claude": ROOT / "skills" / "chinese-official-writing",
    "deepseek_tui": ROOT / ".agents" / "skills" / "chinese-official-writing",
    "hermes": ROOT / "hermes" / "skills" / "chinese-official-writing",
    "openclaw": ROOT / "openclaw" / "skills" / "chinese_official_writing",
}


def patch_frontmatter(target: Path, mode: str) -> None:
    skill_file = target / "SKILL.md"
    text = skill_file.read_text(encoding="utf-8")
    if mode == "openclaw":
        text = text.replace("name: chinese-official-writing", "name: chinese_official_writing", 1)
        text = re.sub(r"\n  hermes:\n(?:    .+\n)+", "\n", text, count=1)
    elif mode == "hermes":
        if f'\nversion: "{VERSION}"\n' not in text.split("---", 2)[1]:
            text = text.replace("license: MIT-0\n", f'license: MIT-0\nversion: "{VERSION}"\n', 1)
        text = re.sub(r"\n  openclaw:\n(?:    .+\n)+(?=  hermes:)", "\n", text, count=1)
    skill_file.write_text(text, encoding="utf-8")


def copy_skill(target: Path, mode: str) -> None:
    if target.exists():
        shutil.rmtree(target)
    ignore = shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store", "Thumbs.db")
    shutil.copytree(CANONICAL, target, ignore=ignore)
    patch_frontmatter(target, mode)
    if mode == "openclaw":
        shutil.copyfile(ROOT / "README.md", target / "README.md")


def main() -> int:
    if not (CANONICAL / "SKILL.md").exists():
        raise SystemExit(f"missing canonical skill: {CANONICAL}")
    for mode, target in TARGETS.items():
        copy_skill(target, mode)
        print(f"synced {target.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
