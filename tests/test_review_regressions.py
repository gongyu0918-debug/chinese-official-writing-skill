from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
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
    def test_formal_leadership_phrases_are_not_flagged_as_process_leaks(self) -> None:
        text = "根据领导要求，项目组已完成风险排查。领导关心的交付节点已纳入每周调度。"

        findings = prose_lint.scan("<test>", text)

        self.assertFalse([item for item in findings if item.label in {"viewpoint-risk", "casual"}])

    def test_model_identity_and_user_process_phrases_are_still_flagged(self) -> None:
        text = "本材料由 AI 起草。根据用户要求修改如下：这版文章将压缩为三段。"

        findings = prose_lint.scan("<test>", text)
        labels = {item.label for item in findings}

        self.assertIn("thought-leak", labels)
        self.assertIn("viewpoint-risk", labels)

    def test_aigc_business_terms_are_not_flagged_as_thought_leak(self) -> None:
        text = "本平台面向AI生成内容业务，支撑AI辅助生成内容的并发推理。"

        findings = prose_lint.scan("<test>", text)

        self.assertFalse([item for item in findings if item.label == "thought-leak"])

    def test_ai_authorship_disclaimers_are_still_flagged_as_thought_leak(self) -> None:
        examples = [
            "本文由AI辅助生成。",
            "本材料系AI生成。",
            "本报告系AI辅助生成，仅供参考。",
            "该方案为AI生成初稿。",
        ]

        for text in examples:
            with self.subTest(text=text):
                findings = prose_lint.scan("<test>", text)
                self.assertTrue([item for item in findings if item.label == "thought-leak"])

    def test_common_placeholders_are_flagged_without_blocking_document_numbers(self) -> None:
        text = (
            "项目名称为[具体项目名称]，预算为XXXX万元，整改事项共X项，"
            "期限为XXXX年，设备为XXXX张，支持XXXX并发请求，计划于YYYY年MM月DD日完成。"
            "（签发日期）另行确认。"
        )

        findings = prose_lint.scan("<test>", text)
        placeholder_matches = [item.match for item in findings if item.label == "unfinished-placeholder"]

        self.assertGreaterEqual(len(placeholder_matches), 8)
        self.assertFalse(
            [
                item
                for item in prose_lint.scan("<test>", "发文字号为XX发〔2026〕1号。")
                if item.label == "unfinished-placeholder"
            ]
        )

    def test_markdown_format_marks_are_flagged_in_formal_output(self) -> None:
        text = "**一、需求来源**\n### 业务需求与服务保障\n正文内容。\n```text\n关于事项的报告\n```"

        findings = prose_lint.scan("<test>", text, include_format=True)
        labels = {item.label for item in findings}

        self.assertIn("markdown-bold", labels)
        self.assertIn("markdown-heading", labels)
        self.assertIn("markdown-code-fence", labels)

    def test_paired_summary_is_quality_risk_not_hard_leak(self) -> None:
        findings = prose_lint.scan("<test>", "项目不是单一事项，而是系统工程。")
        paired = [item for item in findings if item.label == "paired-summary"]

        self.assertTrue(paired)
        self.assertEqual({item.severity for item in paired}, {"medium"})

    def test_code_fence_does_not_hide_placeholders_when_format_checking(self) -> None:
        text = "```text\n项目名称为[具体项目名称]，期限为XXXX年，计划于YYYY年MM月DD日完成。\n```"

        findings = prose_lint.scan("<test>", text, include_format=True)
        labels = [item.label for item in findings]

        self.assertIn("markdown-code-fence", labels)
        self.assertGreaterEqual(labels.count("unfinished-placeholder"), 3)

    def test_attachment_numbered_list_is_not_western_bullet_noise(self) -> None:
        attachment = "附件：\n1. 项目清单\n2. 联系方式"
        ordinary = "1. 项目清单\n2. 联系方式"

        attachment_labels = {item.label for item in prose_lint.scan("<test>", attachment, include_format=True)}
        ordinary_labels = {item.label for item in prose_lint.scan("<test>", ordinary, include_format=True)}

        self.assertNotIn("western-bullet", attachment_labels)
        self.assertIn("western-bullet", ordinary_labels)

    def test_supported_necessity_listing_is_not_flagged_as_empty_roman_list(self) -> None:
        supported = (
            "一、项目建设必要性\n"
            "一是流程节点配置与新发布的集中审批规则不一致，平均办理时长由2.4个工作日延长至4.1个工作日。"
            "二是现有系统接口无法覆盖跨部门材料流转需求，退回补正事项占比连续三个季度高于15%。"
            "三是项目实施后可统一材料清单、办理时限和责任分工，支撑后续验收、运行监测和问题闭环整改。"
        )
        unsupported = "一、项目建设必要性\n一是强化统筹。二是提升能力。三是完善机制。"

        supported_labels = {item.label for item in prose_lint.scan("<test>", supported, include_structure=True)}
        unsupported_labels = {item.label for item in prose_lint.scan("<test>", unsupported, include_structure=True)}

        self.assertNotIn("necessity-listing", supported_labels)
        self.assertIn("necessity-listing", unsupported_labels)

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

    def test_term_overuse_message_is_chinese(self) -> None:
        text = "边界" * 10

        findings = prose_lint.scan("<test>", text)
        term_findings = [item for item in findings if item.label == "term-overuse"]

        self.assertTrue(term_findings)
        self.assertIn("出现 10 次", term_findings[0].excerpt)
        self.assertIn("具体的事项", term_findings[0].excerpt)
        self.assertNotIn("appears", term_findings[0].excerpt)


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
        with tempfile.TemporaryDirectory() as temp_dir:
            bad_docx = Path(temp_dir) / "bad-docx-for-prose-lint-test.docx"
            bad_docx.write_text("not a zip file", encoding="utf-8")

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

    def test_strict_can_ignore_low_severity_findings(self) -> None:
        script = ROOT / "chinese-official-writing" / "scripts" / "prose_lint.py"
        with tempfile.TemporaryDirectory() as temp_dir:
            low_only = Path(temp_dir) / "low-only.md"
            low_only.write_text("边界" * 10, encoding="utf-8")

            strict_low = subprocess.run(
                [sys.executable, str(script), str(low_only), "--strict"],
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
            strict_medium = subprocess.run(
                [sys.executable, str(script), str(low_only), "--strict", "--fail-on", "medium"],
                capture_output=True,
                text=True,
                encoding="utf-8",
            )

        self.assertEqual(strict_low.returncode, 1)
        self.assertEqual(strict_medium.returncode, 0)
        self.assertNotIn("Traceback", strict_medium.stderr + strict_medium.stdout)

    def test_strict_fail_on_medium_still_blocks_medium_findings(self) -> None:
        script = ROOT / "chinese-official-writing" / "scripts" / "prose_lint.py"
        with tempfile.TemporaryDirectory() as temp_dir:
            medium = Path(temp_dir) / "medium.md"
            medium.write_text("项目名称为[具体项目名称]。", encoding="utf-8")

            result = subprocess.run(
                [sys.executable, str(script), str(medium), "--strict", "--fail-on", "medium"],
                capture_output=True,
                text=True,
                encoding="utf-8",
            )

        self.assertEqual(result.returncode, 1)
        self.assertIn("unfinished-placeholder", result.stdout)


class CleanProseCorpusTests(unittest.TestCase):
    def test_clean_corpus_has_no_medium_or_high_findings(self) -> None:
        corpus_path = ROOT / "tests" / "fixtures" / "clean_prose_corpus.json"
        corpus = json.loads(corpus_path.read_text(encoding="utf-8"))
        items = corpus["items"]

        self.assertIn("脱敏改写", corpus["source_note"])
        self.assertIn("medium/high", corpus["blocking_policy"])
        self.assertGreaterEqual(len(items), 10)
        for item in items:
            with self.subTest(item=item["id"]):
                findings = prose_lint.scan(
                    item["id"],
                    item["text"],
                    include_format=True,
                    include_structure=True,
                )
                blocking = [finding for finding in findings if finding.severity in {"medium", "high"}]

                self.assertEqual(blocking, [])

    def test_clean_corpus_sentinel_placeholder_is_detected(self) -> None:
        corpus_path = ROOT / "tests" / "fixtures" / "clean_prose_corpus.json"
        corpus = json.loads(corpus_path.read_text(encoding="utf-8"))

        for item in corpus["items"]:
            with self.subTest(item=item["id"]):
                sentinel_text = f'{item["text"]} 本事项预算为XXXX万元。'
                findings = prose_lint.scan(
                    item["id"],
                    sentinel_text,
                    include_format=True,
                    include_structure=True,
                )
                labels = {finding.label for finding in findings}

                self.assertIn("unfinished-placeholder", labels)


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
