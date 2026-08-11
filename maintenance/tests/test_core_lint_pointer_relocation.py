import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class CoreLintPointerRelocationTests(unittest.TestCase):
    def test_terminal_mode_pointer_moves_without_strengthening_execution(self) -> None:
        skill = (ROOT / "chinese-official-writing" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        core = skill.split("## 核心流程", 1)[1].split("## 硬边界", 1)[0]
        scripts = skill.split("## 脚本", 1)[1]
        pointer = (
            "检查终稿正文时按 `references/final-review-layers.md` "
            "使用 `draft-body` 模式"
        )

        self.assertEqual(skill.count(pointer), 1)
        self.assertIn(pointer, core)
        self.assertNotIn(pointer, scripts)
        self.assertIn("草稿时可使用 `scripts/prose_lint.py`", scripts)
        self.assertNotIn("必须运行", skill)
        self.assertNotIn("运行一次 `python scripts/prose_lint.py", skill)


if __name__ == "__main__":
    unittest.main()
