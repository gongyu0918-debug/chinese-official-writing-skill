import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class CoreLintPointerRelocationTests(unittest.TestCase):
    def test_entry_keeps_lint_and_review_as_separate_explicit_routes(self) -> None:
        skill = (ROOT / "chinese-official-writing" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("references/final-review-layers.md", skill)
        self.assertIn("references/prose-lint-usage.md", skill)
        self.assertIn("脚本只提示风险，不改写正文", skill)
        self.assertIn("Hook 仅在用户明确要求交付门禁时启用", skill)
        self.assertNotIn("必须运行", skill)


if __name__ == "__main__":
    unittest.main()
