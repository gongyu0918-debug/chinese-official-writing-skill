#!/usr/bin/env python3
"""Sync the canonical skill into adapter layouts for other agent tools."""

from __future__ import annotations

import json
import shutil
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CANONICAL = ROOT / "chinese-official-writing"
VERSION = "1.3.3"
ROOT_README = ROOT / "README.md"
OPENCLAW_MARKETPLACE_README = ROOT / "openclaw" / "marketplace-readme.md"
OPENCLAW_SKILL_CARD = ROOT / "openclaw" / "skill-card.md"
CLAUDE_PLUGIN_MANIFEST = ROOT / ".claude-plugin" / "plugin.json"

TARGETS = {
    "claude": ROOT / "skills" / "chinese-official-writing",
    "agents": ROOT / ".agents" / "skills" / "chinese-official-writing",
    "hermes": ROOT / "hermes" / "skills" / "chinese-official-writing",
    "openclaw": ROOT / "openclaw" / "skills" / "chinese_official_writing",
}


def versioned_text(text: str) -> str:
    text = re.sub(r"chinese-official-writing@\d+\.\d+\.\d+", f"chinese-official-writing@{VERSION}", text)
    text = re.sub(r"--version\s+\d+\.\d+\.\d+", f"--version {VERSION}", text)
    text = re.sub(
        r"^\d+\.\d+\.\d+ \(source: server release metadata and skill frontmatter\)",
        f"{VERSION} (source: server release metadata and skill frontmatter)",
        text,
        flags=re.M,
    )
    return text


def patch_frontmatter(target: Path, mode: str) -> None:
    skill_file = target / "SKILL.md"
    text = skill_file.read_text(encoding="utf-8")
    original = text
    if mode == "openclaw":
        text = text.replace("name: chinese-official-writing", "name: chinese_official_writing", 1)
        if "\ncategory: writing\n" not in text.split("---", 2)[1]:
            text = text.replace(
                "license: MIT-0\n",
                "license: MIT-0\ncategory: writing\ntags:\n  - chinese\n  - official-document\n  - writing\n  - gongwen\n  - ai-compute\n",
                1,
            )
        text = re.sub(r"\n  hermes:\n(?:    .+\n)+", "\n", text, count=1)
    elif mode == "hermes":
        if f'\nversion: "{VERSION}"\n' not in text.split("---", 2)[1]:
            text = text.replace("license: MIT-0\n", f'license: MIT-0\nversion: "{VERSION}"\n', 1)
        text = re.sub(r"\n  openclaw:\n(?:    .+\n)+(?=  hermes:)", "\n", text, count=1)
    if text != original:
        skill_file.write_text(text, encoding="utf-8", newline="\n")


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
    readme = versioned_text(OPENCLAW_MARKETPLACE_README.read_text(encoding="utf-8")).strip()
    agent_rules = """

## Agent 使用规则

安装后执行写作任务时，仍按以下规则处理：

1. 先判断文种，再抽取办理要素，再选择论证链条，最后进入语言和格式复核。
2. 文种判断以官方规范和 `references/genre-routing.md` 为准；社区模板不得替代文种功能。
3. 起草前按 `references/handling-elements.md` 核对发文主体、受文对象、事项、依据、时限、责任、附件、反馈渠道和请批事项。
4. 成文时按 `references/argument-chains.md` 组织段落，每段服务一个论点，通常按“结论前置、事实支撑、判断归纳、事项落点”展开。
5. 起草或改写输出正式正文；审稿或复核输出问题位置、风险层级和修改建议；压缩或顺稿输出改后正文和极简改动说明。
6. 从发文单位、报告单位、项目单位或主管单位视角写，不使用旁观者、教师或评论员口吻。
7. 数据和判断要可追溯；不编造实际数据，测算和预估必须标明性质。
8. 起草算力、采购、租赁或服务器租赁材料时，论证重点放在需求来源、Token/资源换算、成本比较、SLA、并发、安全、交付和验收。
9. 最终正文不得残留 `〔签发日期〕`、`〔会议时间〕`、`〔待补充〕`、`[具体项目名称]`、`XXXX万元`、`YYYY年MM月DD日`、`（签发日期）` 等未完成占位；缺项在正文外提示用户确认。当前日期只可用于草稿落款，不得替代维护时间、会议时间、实施期限、政策依据或业务数据。
10. 检查 `.txt`、`.md` 或 `.docx` 草稿时，可使用 `scripts/prose_lint.py`。脚本只提示风险，不自动改写。
"""
    skill_file.write_text(f"---{parts[1]}---\n\n{readme}{agent_rules}", encoding="utf-8")


def update_claude_plugin_manifest() -> None:
    if not CLAUDE_PLUGIN_MANIFEST.exists():
        raise RuntimeError(f"missing Claude plugin manifest: {CLAUDE_PLUGIN_MANIFEST}")
    manifest = json.loads(CLAUDE_PLUGIN_MANIFEST.read_text(encoding="utf-8"))
    manifest["version"] = VERSION
    CLAUDE_PLUGIN_MANIFEST.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def update_root_readme() -> None:
    ROOT_README.write_text(versioned_text(ROOT_README.read_text(encoding="utf-8")), encoding="utf-8")


def update_openclaw_skill_card_source() -> None:
    OPENCLAW_SKILL_CARD.write_text(
        versioned_text(OPENCLAW_SKILL_CARD.read_text(encoding="utf-8")),
        encoding="utf-8",
    )


def copy_skill(target: Path, mode: str) -> None:
    ignore = shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store", "Thumbs.db")
    shutil.copytree(CANONICAL, target, ignore=ignore, dirs_exist_ok=True)
    patch_frontmatter(target, mode)
    if mode == "openclaw":
        (target / "README.md").write_text(
            versioned_text(OPENCLAW_MARKETPLACE_README.read_text(encoding="utf-8")),
            encoding="utf-8",
        )
        reserved_skill_card = target / "skill-card.md"
        if reserved_skill_card.exists():
            reserved_skill_card.unlink()
        patch_openclaw_marketplace_body(target)


def main() -> int:
    if not (CANONICAL / "SKILL.md").exists():
        raise SystemExit(f"missing canonical skill: {CANONICAL}")
    for mode, target in TARGETS.items():
        copy_skill(target, mode)
        print(f"synced {target.relative_to(ROOT)}")
    update_root_readme()
    print(f"synced {ROOT_README.relative_to(ROOT)}")
    update_openclaw_skill_card_source()
    print(f"synced {OPENCLAW_SKILL_CARD.relative_to(ROOT)}")
    update_claude_plugin_manifest()
    print(f"synced {CLAUDE_PLUGIN_MANIFEST.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
