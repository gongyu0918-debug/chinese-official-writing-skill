from __future__ import annotations

from pathlib import Path
import json
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]


def relative_files(root: Path) -> list[str]:
    return sorted(
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc"
    )


class SkillBoundaryTests(unittest.TestCase):
    def test_canonical_skill_declares_trigger_and_exclusion_boundaries(self) -> None:
        text = (ROOT / "chinese-official-writing" / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn("当用户明确要求中文通知", text)
        self.assertIn("## 触发条件与边界", text)
        self.assertIn("批量语料生成", text)
        self.assertIn("规避人工审核", text)
        self.assertIn("替代法律/财务/采购/审计/政策依据判断", text)

    def test_adapter_skill_copies_keep_boundaries(self) -> None:
        paths = [
            ROOT / "skills" / "chinese-official-writing" / "SKILL.md",
            ROOT / ".agents" / "skills" / "chinese-official-writing" / "SKILL.md",
            ROOT / "hermes" / "skills" / "chinese-official-writing" / "SKILL.md",
            ROOT / "openclaw" / "skills" / "chinese_official_writing" / "SKILL.md",
        ]

        for path in paths:
            with self.subTest(path=path):
                text = path.read_text(encoding="utf-8")
                self.assertIn("批量语料生成", text)
                self.assertIn("规避人工审核", text)

    def test_primary_adapter_mirrors_match_canonical_bytes(self) -> None:
        canonical = ROOT / "chinese-official-writing"
        canonical_files = relative_files(canonical)
        for target in [
            ROOT / "skills" / "chinese-official-writing",
            ROOT / ".agents" / "skills" / "chinese-official-writing",
        ]:
            with self.subTest(target=target):
                self.assertEqual(relative_files(target), canonical_files)
                for relative in canonical_files:
                    self.assertEqual((target / relative).read_bytes(), (canonical / relative).read_bytes(), relative)

    def test_packaged_resource_mirrors_match_canonical_bytes(self) -> None:
        canonical = ROOT / "chinese-official-writing"
        for target in [
            ROOT / "hermes" / "skills" / "chinese-official-writing",
            ROOT / "openclaw" / "skills" / "chinese_official_writing",
        ]:
            for folder in ["agents", "references", "scripts"]:
                canonical_folder = canonical / folder
                target_folder = target / folder
                with self.subTest(target=target, folder=folder):
                    files = relative_files(canonical_folder)
                    self.assertEqual(relative_files(target_folder), files)
                    for relative in files:
                        self.assertEqual(
                            (target_folder / relative).read_bytes(),
                            (canonical_folder / relative).read_bytes(),
                            f"{target}/{folder}/{relative}",
                        )

    def test_reference_loading_table_keeps_progressive_disclosure(self) -> None:
        text = (ROOT / "chinese-official-writing" / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn("按任务渐进读取资料，不要一次性加载全部文件", text)
        self.assertIn("| 文件 | 阶段 | 加载条件 |", text)
        self.assertIn("`references/ai-compute-docs.md` | 专项选读", text)
        self.assertIn("仅在 AI 算力、GPU/服务器租赁、模型服务、采购、租赁、可研、成本比较、SLA、安全或验收材料中读取", text)

    def test_trigger_description_covers_reported_genres(self) -> None:
        text = (ROOT / "chinese-official-writing" / "SKILL.md").read_text(encoding="utf-8")

        for keyword in ["复函", "公示", "决议", "议案", "公报", "命令", "工作要点", "审查材料"]:
            self.assertIn(keyword, text)

    def test_multi_round_revision_rules_keep_structure_and_genre_format(self) -> None:
        skill = (ROOT / "chinese-official-writing" / "SKILL.md").read_text(encoding="utf-8")
        workflow = (ROOT / "chinese-official-writing" / "references" / "workflow.md").read_text(encoding="utf-8")
        checklist = (ROOT / "chinese-official-writing" / "references" / "review-checklist.md").read_text(encoding="utf-8")

        for text in [skill, workflow, checklist]:
            self.assertIn("多轮", text)
            self.assertIn("增加自然段", text)
            self.assertIn("反馈渠道", text)
            self.assertIn("原因分析", text)
            self.assertIn("发送人", text)
            self.assertIn("接收方", text)
        self.assertIn("改稿前小标题清单", checklist)
        self.assertIn("改稿后小标题清单", checklist)
        self.assertIn("小标题数量", checklist)

    def test_legal_genres_have_checklist_and_handling_elements(self) -> None:
        checklist = (ROOT / "chinese-official-writing" / "references" / "genre-checklist.md").read_text(encoding="utf-8")
        elements = (ROOT / "chinese-official-writing" / "references" / "handling-elements.md").read_text(encoding="utf-8")

        self.assertIn("## 通告", checklist)
        for genre in ["决议", "公告", "通告", "意见"]:
            self.assertIn(f"| {genre} |", elements)

    def test_reported_genre_coverage_gaps_have_minimum_support(self) -> None:
        routing = (ROOT / "chinese-official-writing" / "references" / "genre-routing.md").read_text(encoding="utf-8")
        checklist = (ROOT / "chinese-official-writing" / "references" / "genre-checklist.md").read_text(encoding="utf-8")
        elements = (ROOT / "chinese-official-writing" / "references" / "handling-elements.md").read_text(encoding="utf-8")

        for keyword in ["工作要点：", "工作总结：", "审查材料：", "讲话稿/致辞/述职报告"]:
            self.assertIn(keyword, routing)
        for heading in ["## 征求意见函", "## 采购公告"]:
            self.assertIn(heading, checklist)
        for genre in ["公示", "征求意见函", "采购公告"]:
            self.assertIn(f"| {genre} |", elements)

    def test_format_reference_clarifies_document_number_brackets(self) -> None:
        text = (ROOT / "chinese-official-writing" / "references" / "format-gbt9704.md").read_text(encoding="utf-8")

        self.assertIn("年份使用六角括号 `〔〕`", text)
        self.assertIn("不要用方括号 `[]` 或圆括号 `()` 替代", text)

    def test_final_drafts_must_not_keep_unfinished_placeholders(self) -> None:
        skill = (ROOT / "chinese-official-writing" / "SKILL.md").read_text(encoding="utf-8")
        elements = (ROOT / "chinese-official-writing" / "references" / "handling-elements.md").read_text(encoding="utf-8")
        checklist = (ROOT / "chinese-official-writing" / "references" / "review-checklist.md").read_text(encoding="utf-8")

        for text in [skill, elements, checklist]:
            self.assertTrue("最终正文" in text or "交付正文" in text)
            self.assertIn("〔签发日期〕", text)
            self.assertIn("未完成占位", text)

        self.assertIn("当前日期不得替代维护时间", skill)
        self.assertIn("当前日期只可用于草稿落款", elements)
        self.assertIn("未把当前日期误用为维护时间", checklist)
        self.assertIn("[具体项目名称]", skill)
        self.assertIn("YYYY年MM月DD日", elements)

    def test_openclaw_marketplace_readme_is_user_facing(self) -> None:
        text = (ROOT / "openclaw" / "marketplace-readme.md").read_text(encoding="utf-8")

        self.assertIn("clawhub install chinese-official-writing", text)
        self.assertIn("其他平台", text)
        self.assertIn("GitHub 仓库 README", text)
        self.assertIn("完整规则、硬边界和复核清单", text)
        self.assertNotIn("### Codex / OpenAI Skill", text)
        self.assertNotIn("npm run eval:official-writing", text)

    def test_claude_plugin_manifest_version_matches_skill_and_sync_script(self) -> None:
        manifest = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
        skill = (ROOT / "chinese-official-writing" / "SKILL.md").read_text(encoding="utf-8")
        sync_script = (ROOT / "tools" / "sync_adapters.py").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        openclaw_readme = (ROOT / "openclaw" / "README.md").read_text(encoding="utf-8")
        marketplace_readme = (ROOT / "openclaw" / "marketplace-readme.md").read_text(encoding="utf-8")
        skill_card = (ROOT / "openclaw" / "skill-card.md").read_text(encoding="utf-8")

        skill_version = re.search(r'version: "([^"]+)"', skill)
        sync_version = re.search(r'VERSION = "([^"]+)"', sync_script)
        readme_version = re.search(r"chinese-official-writing@(\d+\.\d+\.\d+)", readme)
        openclaw_publish_version = re.search(r"--version\s+(\d+\.\d+\.\d+)", openclaw_readme)
        marketplace_version = re.search(r"chinese-official-writing@(\d+\.\d+\.\d+)", marketplace_readme)
        skill_card_version = re.search(r"^(\d+\.\d+\.\d+) \(source: server release metadata", skill_card, re.M)

        self.assertIsNotNone(skill_version)
        self.assertIsNotNone(sync_version)
        self.assertIsNotNone(readme_version)
        self.assertIsNotNone(openclaw_publish_version)
        self.assertIsNotNone(marketplace_version)
        self.assertIsNotNone(skill_card_version)
        self.assertEqual(manifest["version"], skill_version.group(1))
        self.assertEqual(manifest["version"], sync_version.group(1))
        self.assertEqual(manifest["version"], readme_version.group(1))
        self.assertEqual(manifest["version"], openclaw_publish_version.group(1))
        self.assertEqual(manifest["version"], marketplace_version.group(1))
        self.assertEqual(manifest["version"], skill_card_version.group(1))
        self.assertIn("ROOT_README", sync_script)
        self.assertIn("OPENCLAW_README", sync_script)
        self.assertIn("OPENCLAW_MARKETPLACE_README", sync_script)
        self.assertIn("OPENCLAW_SKILL_CARD", sync_script)

    def test_lint_strict_fail_on_is_documented(self) -> None:
        skill = (ROOT / "chinese-official-writing" / "SKILL.md").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("--strict --fail-on medium", skill)
        self.assertIn("--strict --fail-on medium", readme)

    def test_revision_workflow_forbids_new_unprovided_facts(self) -> None:
        skill = (ROOT / "chinese-official-writing" / "SKILL.md").read_text(encoding="utf-8")
        workflow = (ROOT / "chinese-official-writing" / "references" / "workflow.md").read_text(encoding="utf-8")
        checklist = (ROOT / "chinese-official-writing" / "references" / "review-checklist.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("未新增原文外事实", skill)
        self.assertIn("不新增原文没有交代的活动、依据、数据、成效或责任安排", workflow)
        self.assertIn("未新增原文外事实", workflow)
        self.assertIn("未新增原文外事实", checklist)

    def test_v140_mode_routing_material_mapping_and_format_bridge_are_documented(self) -> None:
        skill = (ROOT / "chinese-official-writing" / "SKILL.md").read_text(encoding="utf-8")
        workflow = (ROOT / "chinese-official-writing" / "references" / "workflow.md").read_text(encoding="utf-8")
        checklist = (ROOT / "chinese-official-writing" / "references" / "review-checklist.md").read_text(
            encoding="utf-8"
        )
        anti_ai = (ROOT / "chinese-official-writing" / "references" / "anti-ai-patterns.md").read_text(
            encoding="utf-8"
        )
        format_ref = (ROOT / "chinese-official-writing" / "references" / "format-gbt9704.md").read_text(
            encoding="utf-8"
        )

        for text in [skill, workflow]:
            self.assertIn("任务模式路由", text)
            self.assertIn("起草", text)
            self.assertIn("改稿", text)
            self.assertIn("复核", text)
            self.assertIn("排版交付", text)
        self.assertIn("原文已有事实", workflow)
        self.assertIn("压实合并表达", workflow)
        self.assertIn("待确认补充", workflow)
        self.assertIn("数据冲突不得默认就高", workflow)
        self.assertIn("空章节不直接编实", workflow)
        self.assertIn("原文已有事实", checklist)
        self.assertIn("未默认就高或自选最优", checklist)
        for term in ["夸大意义", "宣传腔", "模糊归因", "公式化未来展望", "同义词循环", "机械三段式", "过度抽象词互相解释"]:
            self.assertIn(term, anti_ai)
        self.assertIn("不新增硬清洗", anti_ai)
        self.assertIn("Word/排版交付衔接", format_ref)
        self.assertIn("DOCX/document 技能", format_ref)
        self.assertIn("不得编造文号", format_ref)
        self.assertIn("Markdown `**加粗**`", format_ref)

    def test_v141_formal_delivery_review_and_tone_rules_are_documented(self) -> None:
        skill = (ROOT / "chinese-official-writing" / "SKILL.md").read_text(encoding="utf-8")
        checklist = (ROOT / "chinese-official-writing" / "references" / "review-checklist.md").read_text(
            encoding="utf-8"
        )
        official_style = (ROOT / "chinese-official-writing" / "references" / "official-style.md").read_text(
            encoding="utf-8"
        )
        format_ref = (ROOT / "chinese-official-writing" / "references" / "format-gbt9704.md").read_text(
            encoding="utf-8"
        )
        sync_script = (ROOT / "tools" / "sync_adapters.py").read_text(encoding="utf-8")

        for text in [skill, format_ref, checklist, sync_script]:
            self.assertIn("正式交付前要素核对", text)
            self.assertIn("签发", text)
            self.assertIn("版记", text)
        self.assertIn("缺项清单", format_ref)
        self.assertIn("不得用 `[依据/背景]`", format_ref)
        self.assertIn("未编造文号、签发人、印章或版记", checklist)
        self.assertIn("用户可读格式复核项", checklist)
        for term in ["标题", "文种", "主送/受文对象", "发文字号", "日期", "附件", "落款", "结尾语", "层级编号"]:
            self.assertIn(term, checklist)
        self.assertIn("位置、风险层级、修改建议", checklist)
        self.assertIn("未默认重写全文", checklist)
        self.assertIn("不做 0-100 分评分", checklist)
        self.assertIn("轻量语气替换建议", official_style)
        for term in ["我觉得", "搞", "差不多", "马上", "然后"]:
            self.assertIn(term, official_style)
        self.assertIn("保留原文事实", official_style)
        self.assertIn("不新增硬清洗", official_style)
        self.assertIn("不新增硬清洗", skill)

        skill_files = relative_files(ROOT / "chinese-official-writing")
        for forbidden in ["document_generator.py", "generate_official_doc.py", "install_fonts.py"]:
            self.assertNotIn(forbidden, skill_files)

    def test_openclaw_agent_rules_include_v140_routing_and_format_bridge(self) -> None:
        text = (ROOT / "openclaw" / "skills" / "chinese_official_writing" / "SKILL.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("任务模式", text)
        self.assertIn("references/workflow.md", text)
        self.assertIn("原文已有事实", text)
        self.assertIn("待确认补充", text)
        self.assertIn("数据冲突不得默认就高", text)
        self.assertIn("references/format-gbt9704.md", text)
        self.assertIn("正式 Word 输出前不得残留 Markdown", text)

    def test_openclaw_skill_card_source_is_tracked_but_not_packaged_directly(self) -> None:
        source = (ROOT / "openclaw" / "skill-card.md").read_text(encoding="utf-8")
        packaged_path = ROOT / "openclaw" / "skills" / "chinese_official_writing" / "skill-card.md"

        self.assertIn("Known Risks and Mitigations", source)
        self.assertFalse(packaged_path.exists())

    def test_openclaw_skill_card_uses_absolute_links_and_key_genres(self) -> None:
        skill = (ROOT / "chinese-official-writing" / "SKILL.md").read_text(encoding="utf-8")
        source = (ROOT / "openclaw" / "skill-card.md").read_text(encoding="utf-8")

        self.assertNotIn("](references/", source)
        self.assertIn("https://github.com/gongyu0918-debug/chinese-official-writing-skill/blob/main/", source)
        for keyword in ["通知", "请示", "报告", "函", "复函", "批复", "方案", "说明", "申请", "采购公告", "审查材料"]:
            with self.subTest(keyword=keyword):
                self.assertIn(keyword, skill)
                self.assertIn(keyword, source)

    def test_readme_discloses_stub_eval_and_deepseek_column_sources(self) -> None:
        text = (ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("默认本地运行使用确定性本地草稿", text)
        self.assertIn("OFFICIAL_WRITING_AGENT_COMMAND", text)
        self.assertIn("风险数来自本地合成消融", text)
        self.assertIn("DeepSeek 列只记录 A/B 样稿生成数量和 C 轮评估是否形成有效结论", text)
        self.assertIn("文档自述噪音", text)
        self.assertIn("不等同于草稿正文缺陷", text)


if __name__ == "__main__":
    unittest.main()
