#!/usr/bin/env python3
"""Sync the canonical skill into adapter layouts for other agent tools."""

from __future__ import annotations

import shutil
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CANONICAL = ROOT / "chinese-official-writing"
VERSION = "1.2.14"

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


def patch_openclaw_marketplace_body(target: Path) -> None:
    """Use a marketplace-friendly body for ClawHub's web README view.

    ClawHub renders the SKILL.md body on the public skill page, not the
    package README.md. Keep the frontmatter executable and replace the body
    with the public README plus a compact agent-use rule block.
    """

    skill_file = target / "SKILL.md"
    text = skill_file.read_text(encoding="utf-8")
    parts = text.split("---", 2)
    if len(parts) < 3:
        raise RuntimeError("OpenClaw SKILL.md frontmatter is malformed")
    readme = (ROOT / "README.md").read_text(encoding="utf-8").strip()
    agent_rules = """

## Agent 使用规则

安装后执行写作任务时，仍按以下规则处理：

1. 先判断文种，再抽取办理要素，再选择论证链条，最后进入语言和格式复核。
2. 文种判断以官方规范和 `references/genre-routing.md` 为准；社区模板不得替代文种功能。
3. 起草前按 `references/handling-elements.md` 核对发文主体、受文对象、事项、依据、时限、责任、附件、反馈渠道和请批事项。
4. 成文时按 `references/argument-chains.md` 组织段落，每段服务一个论点，通常按“结论前置、事实支撑、判断归纳、事项落点”展开。
5. 从发文单位、报告单位、项目单位或主管单位视角写，不使用旁观者、教师或评论员口吻。
6. 数据和判断要可追溯；不编造实际数据，测算和预估必须标明性质。
7. 起草算力、采购、租赁或服务器租赁材料时，论证重点放在需求来源、Token/资源换算、成本比较、SLA、并发、安全、交付和验收。
8. 检查 `.txt`、`.md` 或 `.docx` 草稿时，可使用 `scripts/prose_lint.py`。脚本只提示风险，不自动改写。
"""
    skill_file.write_text(f"---{parts[1]}---\n\n{readme}{agent_rules}", encoding="utf-8")


def copy_skill(target: Path, mode: str) -> None:
    if target.exists():
        shutil.rmtree(target)
    ignore = shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store", "Thumbs.db")
    shutil.copytree(CANONICAL, target, ignore=ignore)
    patch_frontmatter(target, mode)
    if mode == "openclaw":
        shutil.copyfile(ROOT / "README.md", target / "README.md")
        patch_openclaw_marketplace_body(target)


def main() -> int:
    if not (CANONICAL / "SKILL.md").exists():
        raise SystemExit(f"missing canonical skill: {CANONICAL}")
    for mode, target in TARGETS.items():
        copy_skill(target, mode)
        print(f"synced {target.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
