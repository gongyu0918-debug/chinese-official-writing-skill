from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ReportReviewExactDedupTests(unittest.TestCase):
    def test_report_leaf_keeps_genre_boundary_without_approval_restatement(self) -> None:
        report = (
            ROOT
            / "chinese-official-writing"
            / "references"
            / "genre-checklist-report.md"
        ).read_text(encoding="utf-8")

        self.assertIn("报告不写审批请求", report)
        self.assertIn("使用事实性汇报语言", report)
        self.assertIn("工作报告写进展、做法、问题和下一步安排", report)
        self.assertIn("专题报告先给结论，再写事实、分析和建议", report)
        self.assertNotIn("不在报告中请求上级批准", report)


if __name__ == "__main__":
    unittest.main()
