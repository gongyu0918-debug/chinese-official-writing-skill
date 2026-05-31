from __future__ import annotations

from pathlib import Path
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

    def test_legal_genres_have_checklist_and_handling_elements(self) -> None:
        checklist = (ROOT / "chinese-official-writing" / "references" / "genre-checklist.md").read_text(encoding="utf-8")
        elements = (ROOT / "chinese-official-writing" / "references" / "handling-elements.md").read_text(encoding="utf-8")

        self.assertIn("## 通告", checklist)
        for genre in ["决议", "公告", "通告", "意见"]:
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

    def test_openclaw_marketplace_readme_is_user_facing(self) -> None:
        text = (ROOT / "openclaw" / "marketplace-readme.md").read_text(encoding="utf-8")

        self.assertIn("clawhub install chinese-official-writing", text)
        self.assertIn("其他平台", text)
        self.assertIn("GitHub 仓库 README", text)
        self.assertNotIn("### Codex / OpenAI Skill", text)
        self.assertNotIn("npm run eval:official-writing", text)


if __name__ == "__main__":
    unittest.main()
