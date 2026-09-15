"""Regression controls for lexical collisions in paired-expression detection."""
import importlib.util
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("lint_context_fusion", ROOT / "chinese-official-writing/scripts/prose_lint.py")
LINT = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = LINT
SPEC.loader.exec_module(LINT)


class PairedExpressionControls(unittest.TestCase):
    def test_lexical_ji_is_not_conjunction(self):
        for phrase in (
            "该项目按既定时间完成测试，又补充了三组对照记录。",
            "既然场地已确定，又有两人报名，可沿用原安排。",
        ):
            with self.subTest(phrase=phrase):
                self.assertFalse(any(f.label == "paired-summary" for f in LINT.scan("case", phrase)))

    def test_actual_pair_remains_a_review_signal(self):
        for phrase in ("新指引既说明办理地点，又列明受理时段。", "材料既有数据，又有明确结论。"):
            with self.subTest(phrase=phrase):
                findings = LINT.scan("case", phrase)
                self.assertEqual(len([f for f in findings if f.label == "paired-summary"]), 1)

    def test_markdown_permission_does_not_suppress_prose_signal(self):
        findings = LINT.scan("case", "不是单一事项，而是系统工程。", include_format=True,
                             delivery_mode="draft-body", allow_markdown=True)
        self.assertTrue(any(f.label == "paired-summary" for f in findings))


if __name__ == "__main__":
    unittest.main()
