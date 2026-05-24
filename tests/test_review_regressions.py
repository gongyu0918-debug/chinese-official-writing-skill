from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


prose_lint = load_module("prose_lint_under_test", ROOT / "chinese-official-writing" / "scripts" / "prose_lint.py")
real_eval = load_module("real_article_eval_under_test", ROOT / "tools" / "run_real_article_eval.py")
agent_eval = load_module("agent_eval_under_test", ROOT / "tools" / "run_agent_ablation.py")


class ProseLintStructureTests(unittest.TestCase):
    def test_duplicate_detection_stays_within_heading_section(self) -> None:
        text = (
            "### A\n"
            "第一段围绕项目建设、数据贯通、责任分工、验收安排、运行监测和整改反馈进行说明，"
            "明确材料清单、反馈时限、联系人、后续管理要求和风险控制措施。\n\n"
            "### B\n"
            "第二段围绕项目建设、数据贯通、责任分工、验收安排、运行监测和整改反馈进行说明，"
            "明确材料清单、反馈时限、联系人、后续管理要求和风险控制措施。\n"
        )

        findings = prose_lint.scan("<test>", text, include_structure=True)

        self.assertFalse([item for item in findings if item.label == "adjacent-duplicate-matter"])

    def test_duplicate_detection_still_flags_same_section_repetition(self) -> None:
        text = (
            "第一段围绕项目建设、数据贯通、责任分工、验收安排、运行监测和整改反馈进行说明，"
            "明确材料清单、反馈时限、联系人、后续管理要求和风险控制措施。\n\n"
            "第二段围绕项目建设、数据贯通、责任分工、验收安排、运行监测和整改反馈进行说明，"
            "明确材料清单、反馈时限、联系人、后续管理要求和风险控制措施。\n"
        )

        findings = prose_lint.scan("<test>", text, include_structure=True)

        self.assertTrue([item for item in findings if item.label == "adjacent-duplicate-matter"])


class RealArticleEvalAuditTests(unittest.TestCase):
    def test_placeholder_echo_terms_are_reported(self) -> None:
        text = "发文机关以发文字号印发工作方案，主送单位包括有关部门。"

        self.assertEqual(real_eval.placeholder_echo_terms(text), ["主送单位", "发文字号", "发文机关"])

    def test_exact_term_hits_are_counted_separately_from_coverage(self) -> None:
        points = [{"terms": ["发文机关", "发文字号"]}, {"terms": ["主送单位", "有关部门"]}]

        hits, total = real_eval.exact_term_hits(points, "发文机关以发文字号印发工作方案。")

        self.assertEqual(hits, ["发文字号", "发文机关"])
        self.assertEqual(total, 4)


class AgentEvalSummaryTests(unittest.TestCase):
    def test_winner_counts_parse_writer_format(self) -> None:
        review = "Overall winner count: Writer A 10, Writer B 0, Tie 0."

        self.assertEqual(agent_eval.parse_winner_counts([review]), {"A": 10, "B": 0, "Tie": 0})


if __name__ == "__main__":
    unittest.main()
