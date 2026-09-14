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
        self.assertIn("在材料支持范围内说明请批事项所需的依据、现状或必要性", text)
        self.assertIn("经费或资源需求、拟实施安排只在材料给出或请批事项本身需要时核对", text)
        self.assertIn("妥否，请批示", text)
        self.assertIn("## 申请", text)


if __name__ == "__main__":
    unittest.main()
