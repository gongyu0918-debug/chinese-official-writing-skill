from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / "chinese-official-writing/SKILL.md"
REFERENCE = ROOT / "chinese-official-writing/references/short-draft-naturalness.md"


class ShortDraftNaturalnessTests(unittest.TestCase):
    def test_skill_routes_short_drafts_without_numeric_magic(self) -> None:
        skill = SKILL.read_text(encoding="utf-8")
        self.assertIn("references/short-draft-naturalness.md", skill)
        self.assertIn("用户明确要求简短正文", skill)
        self.assertIn("用户只给篇幅上限", skill)
        self.assertIn("文种、材料密度和交付形态", skill)
        self.assertIn("明确说明不要求短稿", skill)
        self.assertIn("明确字数下限或区间", skill)
        self.assertNotIn("正文不超过300字", skill)
        self.assertNotIn("200字左右", skill)

    def test_reference_stays_naturalness_only(self) -> None:
        text = REFERENCE.read_text(encoding="utf-8")
        self.assertIn("篇幅上限是边界", text)
        self.assertIn("材料少时允许短而真实", text)
        self.assertIn("任务明确说明不要求短稿时不读本页", text)
        self.assertIn("不把“接近”“可能”", text)
        self.assertNotIn("不超过300字", text)
        self.assertNotIn("200字左右", text)
        self.assertNotIn("扩写", text)
        self.assertNotIn("Hook", text)


if __name__ == "__main__":
    unittest.main()
