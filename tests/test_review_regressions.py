from __future__ import annotations

import importlib.util
from pathlib import Path
import subprocess
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

    def test_content_tokens_filters_only_low_information_terms(self) -> None:
        tokens = prose_lint.content_tokens("有效积极全面持续推动完善确保 数据系统平台服务管理实施保障")

        for term in ["有效", "积极", "全面", "持续", "推动", "完善", "确保"]:
            self.assertNotIn(term, tokens)
        for term in ["数据", "系统", "平台", "服务", "管理", "实施", "保障"]:
            self.assertIn(term, tokens)


class ProseLintCliTests(unittest.TestCase):
    def test_missing_file_reports_error_without_traceback(self) -> None:
        script = ROOT / "chinese-official-writing" / "scripts" / "prose_lint.py"
        missing = ROOT / "missing-for-prose-lint-test.md"

        result = subprocess.run(
            [sys.executable, str(script), str(missing)],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

        self.assertEqual(result.returncode, 2)
        self.assertIn("ERROR: 文件不存在", result.stderr)
        self.assertNotIn("Traceback", result.stderr + result.stdout)
        self.assertEqual(result.stdout, "")

    def test_bad_docx_reports_error_without_polluting_json_stdout(self) -> None:
        script = ROOT / "chinese-official-writing" / "scripts" / "prose_lint.py"
        bad_docx = Path.home() / "AppData" / "Local" / "Temp" / "bad-docx-for-prose-lint-test.docx"
        bad_docx.write_text("not a zip file", encoding="utf-8")
        self.addCleanup(lambda: bad_docx.unlink(missing_ok=True))

        result = subprocess.run(
            [sys.executable, str(script), str(bad_docx), "--json"],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

        self.assertEqual(result.returncode, 2)
        self.assertIn("ERROR: 文件损坏或不是有效 DOCX", result.stderr)
        self.assertNotIn("Traceback", result.stderr + result.stdout)
        self.assertEqual(result.stdout.strip(), "[]")


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
