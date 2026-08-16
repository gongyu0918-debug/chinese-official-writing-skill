from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / "chinese-official-writing/SKILL.md"
REFERENCE = ROOT / "chinese-official-writing/references/short-draft-naturalness.md"


class ShortDraftNaturalnessTests(unittest.TestCase):
    def test_skill_routes_upper_bound_short_drafts_to_the_reference(self) -> None:
        skill = SKILL.read_text(encoding="utf-8")
        self.assertIn("references/short-draft-naturalness.md", skill)
        self.assertIn("没有硬性下限", skill)
        self.assertIn("不用短稿规则代替篇幅不足处理", skill)

    def test_reference_stays_naturalness_only(self) -> None:
        text = REFERENCE.read_text(encoding="utf-8")
        self.assertIn("篇幅上限是边界", text)
        self.assertIn("材料少时允许短而真实", text)
        self.assertNotIn("扩写", text)
        self.assertNotIn("Hook", text)


if __name__ == "__main__":
    unittest.main()
