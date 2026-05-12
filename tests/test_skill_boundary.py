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


if __name__ == "__main__":
    unittest.main()
