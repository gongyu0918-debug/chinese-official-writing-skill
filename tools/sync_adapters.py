#!/usr/bin/env python3
"""Sync the canonical skill into adapter layouts for other agent tools."""

from __future__ import annotations

import json
import shutil
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CANONICAL = ROOT / "chinese-official-writing"
VERSION = "1.5.5"
ROOT_README = ROOT / "README.md"
OPENCLAW_MARKETPLACE_README = ROOT / "openclaw" / "marketplace-readme.md"
OPENCLAW_README = ROOT / "openclaw" / "README.md"
OPENCLAW_SKILL_CARD = ROOT / "openclaw" / "skill-card.md"
CLAUDE_PLUGIN_MANIFEST = ROOT / ".claude-plugin" / "plugin.json"

TARGETS = {
    "claude": ROOT / "skills" / "chinese-official-writing",
    "agents": ROOT / ".agents" / "skills" / "chinese-official-writing",
    "qwen": ROOT / ".qwen" / "skills" / "chinese-official-writing",
    "hermes": ROOT / "hermes" / "skills" / "chinese-official-writing",
    "openclaw": ROOT / "openclaw" / "skills" / "chinese_official_writing",
}


def versioned_text(text: str) -> str:
    text = re.sub(r"chinese-official-writing@\d+\.\d+\.\d+", f"chinese-official-writing@{VERSION}", text)
    text = re.sub(r"--version(?:\s+|=)\d+\.\d+\.\d+", f"--version={VERSION}", text)
    text = re.sub(
        r"^\d+\.\d+\.\d+ \(source: server release metadata and skill frontmatter\)",
        f"{VERSION} (source: server release metadata and skill frontmatter)",
        text,
        flags=re.M,
    )
    return text


def versioned_skill_text(text: str) -> str:
    return re.sub(r'version: "\d+\.\d+\.\d+"', f'version: "{VERSION}"', text)


def update_canonical_skill_version() -> None:
    skill_file = CANONICAL / "SKILL.md"
    skill_file.write_text(
        versioned_skill_text(skill_file.read_text(encoding="utf-8")),
        encoding="utf-8",
        newline="\n",
    )


def patch_frontmatter(target: Path, mode: str) -> None:
    skill_file = target / "SKILL.md"
    text = versioned_skill_text(skill_file.read_text(encoding="utf-8"))
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
2. 文种判断以官方规范、`references/genre-routing.md` 和 `references/genre-playbooks.md` 为准；社区模板不得替代文种功能。
3. 起草前按 `references/handling-elements.md` 核对发文主体、受文对象、事项、依据、时限、责任、附件、反馈渠道和请批事项。
4. 成文时按 `references/argument-chains.md` 组织段落，每段服务一个论点，通常按“结论前置、事实支撑、判断归纳、事项落点”展开。
5. 材料稀疏、短稿、低上下文局部修改或用户明确不新增事实时，先按 `references/task-route-cards.md` 处理已给事实和少量缺口；复杂长文、多材料或结构锁定再转读 `references/workflow.md`。起草、改稿、复核、排版交付先判定任务模式；用户已有提纲、模板、标题顺序时优先保留；事实不足时先完成可用正文，再在正文后列待确认事项或“补充以下信息后，文章会更完整”，不在正文前中断成稿或连续追问；用户明示某些事项未提供且这些事项影响办理落地时，正文后短列用户点名的缺项，不漏列、不扩展成调查问卷；去 AI 味、变换句式或调整清单结构不得补写未给解释、原因、影响、流程、人员、字段或整改动作；后续轮次用户未补齐事实时仍继续执行本轮修改，不把待确认事项升级为阻断条件。
6. 多材料合稿按 `references/workflow.md` 区分原文已有事实、压实合并表达和待确认补充；数据冲突不得默认就高或自选最优。
7. 起草或改写输出正式正文；用户要求检查、审一下、格式核验或语气检查时，审稿或复核输出问题位置、风险层级和修改建议，不默认重写全文，不做 0-100 分评分。
8. 从发文单位、报告单位、项目单位或主管单位视角写，不使用旁观者、教师或评论员口吻。
9. 数据和判断要可追溯；不编造实际数据，测算和预估必须标明性质。
10. 起草算力、采购、租赁或服务器租赁材料时，论证重点放在需求来源、Token/资源换算、成本比较、SLA、并发、安全、交付和验收。
11. 联网搜索只用于事实核查、双重验证和时效性来源；默认不外搜，只有用户明确要求搜索或核验公开来源，或任务含“最新/当前/今日/现行政策/近期数据”等时效事实时才可联网核验。搜索后在正文外说明来源、日期或检索口径；不因出现单位名称就搜索单位公开样文、固定格式或写作风格。
12. 用户要求 Word、docx、GB/T 9704、红头、发文字号、签发、版记或正式文件时，先按 `references/format-gbt9704.md` 做正式交付前要素核对卡和缺项清单，再交给 DOCX/document 技能或现有文档工具；不得编造文号、签发人、印章、密级、版记等要素。
13. 最终正文不得残留 `〔签发日期〕`、`〔会议时间〕`、`〔待补充〕`、`[具体项目名称]`、`XXXX万元`、`YYYY年MM月DD日`、`（签发日期）`、`（成文日期待确认）` 等未完成占位；缺项在正文外提示用户确认。用户明示成文日期缺失、待确认或需另行确认时，不使用当前日期补落款；当前日期只可用于其他已允许的草稿落款，不得替代维护时间、会议时间、实施期限、政策依据或业务数据。
14. 正式 Word 输出前不得残留 Markdown `**`、代码块或标题井号；检查 `.txt`、`.md` 或 `.docx` 草稿时，可使用 `scripts/prose_lint.py`。脚本只提示风险，不自动改写。
15. 成稿前按 `references/proofreading-checklist.md` 顺手做 AI 写稿轻量校对，只看语言、引用保真和稿内一致性风险；用户给定领导讲话、古诗词、名言和政策原文默认同语境原样保留，成语只有明显误引或不合语境时才替换；真实性核验不属于默认修正范围，不默认联网反查。
16. 轻量语气替换只作建议层，不新增硬清洗；去口语化必须保留原文事实，不补造依据、数据、成效或责任安排；`老板关心`、`钱花得值`、`马上要搞` 等口语来源不得自动升级成 `领导高度关注`、`投入产出清晰`、`推进较为紧迫`、`按程序推进` 等强判断；去 AI 味看成簇问题，不把单个正式词或单个转折当作硬清洗理由；句群节奏和模板化痕迹只作软性审稿项，公文去 AI 味不是聊天化，不加入第一人称、反问、口语插入或情绪化表达；正文调整只能使用已给事实，不为显得自然或完整补造解释、原因、影响、流程、人员、字段或整改动作。
17. 社区技能和公开样文只借鉴流程思路、检查维度和 prompt/markdown 组织方式；不复制社区代码、脚本、正则、模板正文、大段 prompt 或固定话术，也不扩大默认联网、强制确认、硬清洗或重排版范围。
18. 长篇限字稿件先做篇幅预算，压缩铺垫、重复和套话，保留措施、责任、时限和结尾落点，避免头重脚轻或草草收尾。
19. OpenClaw 安装包以本入口规则和 `references/final-review-layers.md`、`references/review-checklist.md` 为准；遇到事实、文种、行文关系、用户模板或结构锁定问题，必须回看包内 `references/`，不要假设市场页摘要已经包含完整边界。canonical 全文见 GitHub 仓库。
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


def update_openclaw_readme_sources() -> None:
    OPENCLAW_MARKETPLACE_README.write_text(
        versioned_text(OPENCLAW_MARKETPLACE_README.read_text(encoding="utf-8")),
        encoding="utf-8",
    )
    OPENCLAW_README.write_text(
        versioned_text(OPENCLAW_README.read_text(encoding="utf-8")),
        encoding="utf-8",
    )


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
    update_canonical_skill_version()
    update_openclaw_readme_sources()
    print("synced openclaw README sources")
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
