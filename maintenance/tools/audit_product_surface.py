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
    "宿主适配",
    "运行时能力",
    "构建 Skill",
    "维护 Skill",
)
ROUTE_META_LEAKS = (
    "从 `SKILL.md` 直接进入",
    "从 SKILL.md 直接进入",
    "补充读取：",
    "总路由表",
    "停止读取本页",
    "不回读",
    "route-manifest.json",
    "共性伴读",
    "短路命中",
    "材料稀疏",
    "材料稀薄",
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
        for phrase in ROUTE_META_LEAKS:
            if phrase.lower() in lower:
                errors.append(f"{rel}: leaked construction/routing residue {phrase!r}")
        if path.name == "SKILL.md":
            match = re.search(r"^description: (.+)$", text, re.MULTILINE)
            if not match:
                errors.append("SKILL.md: missing description")
            else:
                description = match.group(1)
                for phrase in ROUTING_DESCRIPTION_PHRASES:
                    if phrase in description:
                        errors.append(f"SKILL.md: description contains routing phrase {phrase!r}")
            if "## 任务模式路由与写作主线" in text:
                errors.append("SKILL.md: duplicate detailed routing section remains on homepage")
            if text.count("交付动作 → 主文种首叶") != 1:
                errors.append("SKILL.md: homepage route spine is missing or duplicated")
            if "所有任务先按交付动作分模式" in text:
                errors.append("SKILL.md: duplicated route instruction remains outside route spine")
            scope = text.split("## 入口契约", 1)[0]
            for phrase in ("compatibility-scene-routing.md", "genre-playbook-opinion.md", "genre-playbook-institution-rules.md", "hooks/README.md"):
                if phrase in scope:
                    errors.append(f"SKILL.md: routing pointer leaked into applicability scope: {phrase!r}")
            for phrase in ("请示请求上级指示或批准", "报告汇报、反映或答复", "通知写清对象"):
                if phrase in text:
                    errors.append(f"SKILL.md: genre-specific rule leaked into homepage: {phrase!r}")
    return errors


if __name__ == "__main__":
    problems = audit()
    if problems:
        print("\n".join(problems))
        raise SystemExit(1)
    print("product surface clean: no engineering commands or routing prose in description")
