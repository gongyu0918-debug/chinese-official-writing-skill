from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]


class RequestReviewSequenceDedupTests(unittest.TestCase):
    def test_request_rules_keep_each_required_element_once(self) -> None:
        text = (
            ROOT
            / "chinese-official-writing"
            / "references"
            / "genre-checklist-request.md"
        ).read_text(encoding="utf-8")

        self.assertNotIn("可参考顺序：请批事项", text)
        self.assertIn("开头或前部明确请批事项", text)
        self.assertIn("依据、现状、必要性、经费或资源需求、拟实施安排", text)
        self.assertIn("妥否，请批示", text)
        self.assertIn("## 申请", text)


if __name__ == "__main__":
    unittest.main()
