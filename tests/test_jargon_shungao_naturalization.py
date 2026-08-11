from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
RUNTIME_ROOTS = [
    ROOT / "chinese-official-writing",
    ROOT / "skills" / "chinese-official-writing",
    ROOT / ".agents" / "skills" / "chinese-official-writing",
    ROOT / ".qwen" / "skills" / "chinese-official-writing",
    ROOT / "hermes" / "skills" / "chinese-official-writing",
]


class ShungaoNaturalizationTests(unittest.TestCase):
    def test_runtime_instructions_use_plain_editing_terms(self) -> None:
        for root in RUNTIME_ROOTS:
            texts = [root.joinpath("SKILL.md").read_text(encoding="utf-8")]
            texts.extend(path.read_text(encoding="utf-8") for path in root.joinpath("references").glob("*.md"))
            joined = "\n".join(texts)
            with self.subTest(root=root):
                self.assertNotIn("顺稿", joined)
                self.assertIn("润色修改", joined)

        canonical = ROOT / "chinese-official-writing"
        skill = canonical.joinpath("SKILL.md").read_text(encoding="utf-8")
        workflow = canonical.joinpath("references", "workflow.md").read_text(encoding="utf-8")
        review = canonical.joinpath("references", "review-checklist.md").read_text(encoding="utf-8")
        self.assertIn("压缩、润色修改或去口语化", skill)
        self.assertIn("先处理结构，再润色语言", workflow)
        self.assertIn("旧主送、旧金额、旧日期", canonical.joinpath("references", "proofreading-checklist.md").read_text(encoding="utf-8"))
        self.assertIn("润色修改、报告化或去口语化", review)


if __name__ == "__main__":
    unittest.main()
