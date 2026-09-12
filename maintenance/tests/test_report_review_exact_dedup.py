from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class ReportReviewExactDedupTests(unittest.TestCase):
    def test_report_leaf_keeps_genre_boundary_without_approval_restatement(self) -> None:
        report = (
            ROOT
            / "chinese-official-writing"
            / "references"
            / "genre-playbook-report.md"
        ).read_text(encoding="utf-8")

        self.assertIn("报告不写请批语或审批请求", report)
        self.assertIn("使用事实性汇报语言", report)
        self.assertIn("报告事项与范围", report)
        self.assertIn("进行中、待核、建议和拟议状态保持原级别", report)
        self.assertNotIn("复核只输出位置", report)


if __name__ == "__main__":
    unittest.main()
