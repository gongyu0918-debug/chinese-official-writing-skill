from __future__ import annotations

from pathlib import Path
import json
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]


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

        skill_version = re.search(r'version: "([^"]+)"', skill)
        sync_version = re.search(r'VERSION = "([^"]+)"', sync_script)

        self.assertIsNotNone(skill_version)
        self.assertIsNotNone(sync_version)
        self.assertEqual(manifest["version"], skill_version.group(1))
        self.assertEqual(manifest["version"], sync_version.group(1))

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
