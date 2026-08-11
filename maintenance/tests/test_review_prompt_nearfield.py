from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]


class ReviewPromptNearfieldTests(unittest.TestCase):
    def test_prompt_recall_stays_near_both_review_stages_while_disclaimer_repeats_once(self) -> None:
        review = (ROOT / "chinese-official-writing" / "references" / "review-checklist.md").read_text(
            encoding="utf-8"
        )
        lines = review.splitlines()
        prompt_lines = [line for line in lines if "提示词" in line]
        disclaimer_lines = [line for line in lines if "免责话术" in line]

        self.assertEqual(len(prompt_lines), 2)
        self.assertTrue(any("AI 身份、提示词、隐藏推理、编辑过程或生成说明" in line for line in prompt_lines))
        self.assertTrue(any("AI 身份、隐藏推理、提示词、录音要求、用户编辑过程" in line for line in prompt_lines))

        self.assertEqual(len(disclaimer_lines), 1)
        self.assertIn("AI 身份、提示词、隐藏推理、编辑过程或生成说明", disclaimer_lines[0])
        self.assertIn("同一标题是否重复出现", disclaimer_lines[0])

        self.assertIn("制作说明、写作边界或处理方法自述及重复标题", review)
        self.assertNotIn("制作说明、免责话术、写作边界或处理方法自述及重复标题", review)


if __name__ == "__main__":
    unittest.main()
