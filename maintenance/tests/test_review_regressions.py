from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
import zipfile


ROOT = Path(__file__).resolve().parents[2]
NEGATIVE_TAIL_CASES = (
    ("protective-negative-inference", "项目仍在评估中，尚不能据此推定预算已经落实。"),
    ("unresolved-conclusion-tail", "核对意见尚未形成明确结论。"),
    ("negative-boundary-tail", "已完成材料登记，但不代表已经通过审批。"),
)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


prose_lint = load_module("prose_lint_under_test", ROOT / "chinese-official-writing" / "scripts" / "prose_lint.py")
real_eval = load_module("real_article_eval_under_test", ROOT / "maintenance" / "tools" / "run_real_article_eval.py")
agent_eval = load_module("agent_eval_under_test", ROOT / "maintenance" / "tools" / "run_agent_ablation.py")
revision_eval = load_module(
    "revision_eval_under_test",
    ROOT / "maintenance" / "tools" / "run_revision_instruction_eval.py",
)


class ProseLintStructureTests(unittest.TestCase):
    def test_generic_vague_claims_do_not_inject_compute_guidance(self):
        for text in (
            "这次活动为企业交流搭建了强大平台。",
            "本次维修成本更低，能够满足未来发展需要。",
        ):
            with self.subTest(text=text):
                findings = prose_lint.scan("<test>", text, delivery_mode="draft-body")
                self.assertTrue(findings)
                self.assertTrue(all(f.label == "vague-claim" for f in findings))
                advice = " ".join(f.excerpt for f in findings)
                for unrelated in ("GPU", "Token", "SLA", "调度", "监控", "并发"):
                    self.assertNotIn(unrelated, advice)
                self.assertIn("材料", advice)

    def test_compute_evaluation_still_reports_material_based_guidance(self):
        findings = prose_lint.scan("<test>", "拟建设先进算力服务。", delivery_mode="draft-body")
        self.assertEqual([f.label for f in findings], ["ai-compute-vague"])
        self.assertIn("材料已有", findings[0].excerpt)

    def test_unfinished_reason_sentence_is_detected_in_both_body_modes(self):
        texts = (
            "因＿＿＿＿＿＿＿＿，申请延期至9月27日。",
            "原定9月20日完成，现因____，申请延期至9月27日。",
            "由于＿＿＿，现申请延期。",
            "〔延期原因〕，现申请延期至9月27日。",
            "原定9月20日完成。鉴于〔申请理由〕，现申请延期。",
            "申请理由写为“因＿＿＿，现申请延期。”",
            "原定9月20日完成，因（延期原因待补），现申请延期至9月27日。",
            "材料原文：“原定9月20日完成。”改稿写为“因＿＿＿，现申请延期。”",
            "材料原文：“原定9月20日完成。”\n改稿写为“因＿＿＿，现申请延期。”",
            "材料原文：“原定9月20日完成。”\n  \n改稿写为“因＿＿＿，现申请延期。”",
        )
        for text in texts:
            for mode in ("draft-body", "gap-note-allowed"):
                with self.subTest(text=text, mode=mode):
                    findings = prose_lint.scan("<test>", text, delivery_mode=mode)
                    hits = [f for f in findings if f.label == "unfinished-reason-placeholder"]
                    self.assertEqual(len(hits), 1)
                    self.assertEqual(hits[0].severity, "medium")

    def test_reason_probe_preserves_fields_separators_and_real_reasons(self):
        texts = (
            "材料原文：“因＿＿＿，现申请延期。”",
            "延期原因：＿＿＿＿＿＿＿＿", "延期原因：因＿＿＿，申请延期。",
            "| 延期原因 | ＿＿＿＿ |", "| 原因句 | 因＿＿＿，申请延期。 |",
            "＿＿＿＿＿＿＿＿\n申请延期。", "---\n申请延期。",
            "因资料尚未收到，申请延期至9月27日。",
            "因现有办公椅较为破旧，为满足日常办公需要，现申请购置4把。",
        )
        for text in texts:
            with self.subTest(text=text):
                findings = prose_lint.scan("<test>", text, include_format=True, delivery_mode="draft-body")
                self.assertNotIn("unfinished-reason-placeholder", {f.label for f in findings})

    def test_reason_probe_preserves_attributed_quotes_and_postscript(self):
        texts = (
            "材料原文：“原定9月20日完成，因＿＿＿，现申请延期。”",
            "原句如下：“资料核对工作原定9月20日完成。\n因＿＿＿，现申请延期。”",
            "现申请将资料核对延至9月27日。\n\n文后提示\n因＿＿＿，这处原因空位需补充。",
        )
        for text in texts:
            with self.subTest(text=text):
                findings = prose_lint.scan("<test>", text, delivery_mode="gap-note-allowed")
                self.assertNotIn("unfinished-reason-placeholder", {f.label for f in findings})
        for mode in ("generic", "review-only"):
            findings = prose_lint.scan("<test>", "因＿＿＿，现申请延期。", delivery_mode=mode)
            self.assertNotIn("unfinished-reason-placeholder", {f.label for f in findings})

    def test_postscript_heading_separates_body_and_notes(self) -> None:
        body = "情况说明\n\n7月8日页面出现6次短时空白，13名用户反映无法登录，异常原因正在调查中。"
        note = "文后提示\n现有材料未说明提交对象。"
        clean = body + "\n\n" + note
        source = prose_lint.prepare_scan_source(clean, "gap-note-allowed")
        self.assertEqual(source.text_to_scan.rstrip(), body)
        labels = {item.label for item in prose_lint.scan("<test>", clean, delivery_mode="gap-note-allowed")}
        self.assertNotIn("external-note-boundary", labels)
        self.assertNotIn("material-reading-narration", labels)
        forbidden = {item.label for item in prose_lint.scan("<test>", clean, delivery_mode="draft-body")}
        self.assertIn("unexpected-external-note", forbidden)

    def test_postscript_cannot_continue_body_numbering_or_attach_to_last_paragraph(self) -> None:
        for separator, heading in (
            ("\n", "文后提示"), ("\n\n", "三、文后提示"), ("\n\n", "第三章 文后提示"),
            ("\n\n", "2. 文后提示"), ("\n\n", "2) 文后提示"), ("\n\n", "（二）文后提示"),
            ("\n\n", "## 二、文后提示"),
            ("\n\n", "二、**文后提示**"), ("\n\n", "## （二）*文后提示*"),
        ):
            with self.subTest(separator=separator, heading=heading):
                text = "异常原因正在调查中。" + separator + heading + "\n提交对象待确认。"
                labels = {item.label for item in prose_lint.scan("<test>", text, delivery_mode="gap-note-allowed")}
                self.assertIn("external-note-boundary", labels)

    def test_postscript_words_in_business_content_do_not_hide_body(self) -> None:
        for text in ("文后提示模块建设情况\n模块尚在测试。", "一、文后提示功能\n已完成2项核对。", "系统显示文后提示，原因仍待核对。"):
            with self.subTest(text=text):
                self.assertEqual(prose_lint.body_lines(text.splitlines()), text.splitlines())

    def test_postscript_still_checks_identity_leak(self) -> None:
        text = "异常原因正在调查中。\n\n文后提示\n本审稿意见由AI生成。"
        findings = prose_lint.scan("<test>", text, delivery_mode="gap-note-allowed")
        self.assertIn("thought-leak", {item.label for item in findings})

    def test_wrapped_standard_postscript_is_separate_and_keeps_format_findings(self):
        cases = (
            ("**文后提示**", {"markdown-bold"}),
            ("*文后提示*", {"markdown-emphasis"}),
            ("__文后提示__", {"markdown-bold"}),
            ("_文后提示_", {"markdown-emphasis"}),
            ("## 文后提示", {"markdown-heading"}),
            ("## **文后提示**", {"markdown-heading", "markdown-bold"}),
        )
        for heading, expected in cases:
            text = f"已完成核对。\n\n{heading}\n[具体项目名称]待确认。\n本审稿意见由AI生成。"
            with self.subTest(heading=heading):
                source = prose_lint.prepare_scan_source(text, "gap-note-allowed")
                self.assertEqual(source.text_to_scan.rstrip(), "已完成核对。")
                findings = prose_lint.scan("<test>", text, include_format=True, delivery_mode="gap-note-allowed")
                labels = {item.label for item in findings}
                self.assertTrue(expected.issubset(labels))
                self.assertNotIn("unfinished-placeholder", labels)
                self.assertIn("thought-leak", labels)
                for item in findings:
                    if item.label in expected:
                        self.assertEqual(item.line, 3)
                        self.assertEqual(item.severity, "low")
                without_format = prose_lint.scan("<test>", text, delivery_mode="gap-note-allowed")
                self.assertTrue(expected.isdisjoint({item.label for item in without_format}))

    def test_wrapped_business_titles_are_not_postscript_boundaries(self):
        for heading in (
            "**文后提示模块**", "*文后提示功能*", "## 文后提示模块",
            "**风险提醒**", "*补充信息*", "## **补充信息**",
        ):
            text = f"模块建设情况\n\n{heading}\n预算仍为XXXX万元。"
            with self.subTest(heading=heading):
                self.assertEqual(prose_lint.body_lines(text.splitlines()), text.splitlines())
                labels = {item.label for item in prose_lint.scan("<test>", text, delivery_mode="gap-note-allowed")}
                self.assertIn("unfinished-placeholder", labels)
                self.assertNotIn("external-note-boundary", labels)

    def test_generic_note_headings_keep_every_business_line(self) -> None:
        headings = (
            "风险提醒", "二、风险提醒", "补充信息", "三、补充信息",
            "待确认事项", "二、待确认事项", "第七章 待确认事项", "2. 待确认事项",
            "（二）待确认事项", "核验提示", "需补充信息", "待补充事项", "需确认事项",
        )
        for heading in headings:
            text = f"一、核对进展\n已完成核对。\n\n{heading}\n预算仍为XXXX万元。\n\n三、后续事项\n拟继续核对。"
            with self.subTest(heading=heading):
                self.assertEqual(prose_lint.body_lines(text.splitlines()), text.splitlines())
                for mode in ("draft-body", "gap-note-allowed"):
                    labels = {item.label for item in prose_lint.scan("<test>", text, delivery_mode=mode)}
                    self.assertIn("unfinished-placeholder", labels)
                    self.assertNotIn("unexpected-external-note", labels)
                    self.assertNotIn("external-note-boundary", labels)

    def test_explicit_legacy_note_titles_remain_compatible(self) -> None:
        headings = (
            "正文外提示", "正文外待确认", "影响正式报送的待确认事项", "待用户确认事项",
            "待确认事项（正文外）", "待确认事项（正文外，供用户确认）", "（正文外提示）",
            "风险提醒（正文外）", "补充信息（供用户确认）",
        )
        for heading in headings:
            text = f"已完成核对。\n\n{heading}\n[具体项目名称]待确认。\n本审稿意见由AI生成。"
            with self.subTest(heading=heading):
                self.assertEqual("\n".join(prose_lint.body_lines(text.splitlines())).rstrip(), "已完成核对。")
                labels = {item.label for item in prose_lint.scan("<test>", text, delivery_mode="gap-note-allowed")}
                self.assertNotIn("unfinished-placeholder", labels)
                self.assertIn("thought-leak", labels)

    def test_negative_tail_checks_match_across_body_delivery_modes(self) -> None:
        for label, text in NEGATIVE_TAIL_CASES:
            with self.subTest(label=label):
                draft = prose_lint.scan("<test>", text, delivery_mode="draft-body")
                allowed = prose_lint.scan("<test>", text, delivery_mode="gap-note-allowed")
                self.assertIn(label, {item.label for item in draft})
                self.assertEqual(allowed, draft)
                for mode in ("generic", "review-only"):
                    self.assertNotIn(label, {item.label for item in prose_lint.scan("<test>", text, delivery_mode=mode)})

    def test_postscript_negative_tails_are_exempt_but_identity_leaks_are_not(self) -> None:
        notes = "\n".join(text for _, text in NEGATIVE_TAIL_CASES)
        for wrapped in (notes, f"```text\n{notes}\n```"):
            text = f"已完成材料登记。\n\n文后提示\n{wrapped}\n[具体项目名称]待确认。\n本审稿意见由AI生成。"
            with self.subTest(notes=wrapped):
                findings = prose_lint.scan("<test>", text, delivery_mode="gap-note-allowed")
                labels = {item.label for item in findings}
                self.assertTrue({label for label, _ in NEGATIVE_TAIL_CASES}.isdisjoint(labels))
                self.assertNotIn("unfinished-placeholder", labels)
                self.assertIn("thought-leak", labels)

    def test_delivery_mode_flags_narration_self_certification_and_english_thought(self) -> None:
        text = (
            "由于现有材料仅反映阶段性情况，暂无法形成完整判断。\n"
            "本稿不新增原文外事实。\n"
            "We need to draft a concise report before the final answer.\n"
            "As an AI language model, I cannot verify the source.\n"
            "以下为最终正文：\n"
            "本报告仅反映7月核查结果，不对责任归属作延伸判断。\n"
            "上述情况不扩大为其他系统的结论。"
        )

        default_labels = {item.label for item in prose_lint.scan("<test>", text)}
        delivery_findings = prose_lint.scan("<test>", text, delivery_mode="draft-body")
        delivery_labels = {item.label for item in delivery_findings}

        self.assertNotIn("material-reading-narration", default_labels)
        self.assertNotIn("constraint-self-certification", default_labels)
        self.assertNotIn("english-thought-fragment", default_labels)
        self.assertTrue(
            {
                "material-reading-narration",
                "constraint-self-certification",
                "english-thought-fragment",
                "delivery-explanation",
            }.issubset(delivery_labels)
        )
        severities_by_label = {
            label: {item.severity for item in delivery_findings if item.label == label}
            for label in delivery_labels
        }
        self.assertEqual(severities_by_label["material-reading-narration"], {"medium"})
        self.assertEqual(severities_by_label["constraint-self-certification"], {"high", "medium"})
        for label in ["english-thought-fragment", "delivery-explanation"]:
            self.assertEqual(severities_by_label[label], {"high"})
        self.assertEqual(
            {item.severity for item in delivery_findings if item.line == 2},
            {"high"},
        )
        self.assertGreaterEqual(
            len([item for item in delivery_findings if item.label == "constraint-self-certification"]),
            3,
        )

    def test_review_only_allows_material_gap_analysis_but_not_ai_identity(self) -> None:
        text = "现有材料未说明验收结论，建议列为高风险。本审稿意见由AI生成。"

        labels = {item.label for item in prose_lint.scan("<test>", text, delivery_mode="review-only")}

        self.assertNotIn("material-reading-narration", labels)
        self.assertIn("thought-leak", labels)

    def test_review_only_does_not_treat_quoted_problem_sentence_as_agent_leak(self) -> None:
        text = "位置：“本方案重点说明三个问题。”\n风险层级：高\n修改建议：删除写作说明。"

        review_labels = {item.label for item in prose_lint.scan("<test>", text, delivery_mode="review-only")}
        draft_labels = {item.label for item in prose_lint.scan("<test>", text, delivery_mode="draft-body")}

        self.assertNotIn("side-commentary", review_labels)
        self.assertIn("side-commentary", draft_labels)

    def test_review_only_does_not_treat_multiline_quote_as_agent_leak(self) -> None:
        text = "位置：“本方案重点说明\n三个问题。”\n风险层级：高\n修改建议：删除写作说明。"

        labels = {item.label for item in prose_lint.scan("<test>", text, delivery_mode="review-only")}

        self.assertNotIn("side-commentary", labels)

    def test_unclosed_quote_does_not_hide_later_delivery_leaks(self) -> None:
        text = (
            "位置：“本方案重点说明三个问题。\n"
            "We need to review the draft.\n"
            "本审稿意见由AI生成。\n"
            "本稿不新增原文外事实。"
        )

        labels = {item.label for item in prose_lint.scan("<test>", text, delivery_mode="review-only")}

        self.assertIn("side-commentary", labels)
        self.assertIn("english-thought-fragment", labels)
        self.assertIn("thought-leak", labels)
        self.assertIn("constraint-self-certification", labels)

    def test_review_only_still_scans_unquoted_leaks_and_content_after_note_heading(self) -> None:
        text = (
            "We need to review the draft.\n"
            "文后提示\n资金来源待确认。\n本审稿意见由AI生成。"
        )

        labels = {item.label for item in prose_lint.scan("<test>", text, delivery_mode="review-only")}

        self.assertIn("english-thought-fragment", labels)
        self.assertIn("thought-leak", labels)

    def test_gap_note_mode_scans_body_but_stops_before_external_note(self) -> None:
        body_leak = (
            "从已给材料看，项目尚处于准备阶段。\n\n"
            "文后提示\n现有材料未说明资金来源。"
        )
        note_only = "项目拟于8月启动。\n\n文后提示\n现有材料未说明资金来源。"

        body_labels = {
            item.label for item in prose_lint.scan("<test>", body_leak, delivery_mode="gap-note-allowed")
        }
        note_labels = {
            item.label for item in prose_lint.scan("<test>", note_only, delivery_mode="gap-note-allowed")
        }

        self.assertIn("material-reading-narration", body_labels)
        self.assertNotIn("material-reading-narration", note_labels)

    def test_gap_note_mode_requires_a_separate_unnumbered_note_region(self) -> None:
        clean = (
            "关于采购设备的请示\n\n妥否，请批示。\n\n综合服务中心\n2026年8月18日\n\n"
            "待确认事项（正文外）：\n1. 主送机关。"
        )
        blurred = [
            "关于采购设备的请示\n\n妥否，请批示。\n文后提示\n1. 主送机关。",
            "关于采购设备的请示\n\n妥否，请批示。\n\n四、文后提示\n1. 主送机关。",
            "关于采购设备的请示\n\n妥否，请批示。\n\n---\n\n文后提示\n1. 主送机关。",
            "关于采购设备的请示\n\n妥否，请批示。\n\n---\n\n影响正式报送的待确认事项：\n1. 主送机关。",
        ]

        clean_labels = {
            item.label for item in prose_lint.scan("<test>", clean, delivery_mode="gap-note-allowed")
        }
        self.assertNotIn("external-note-boundary", clean_labels)
        for text in blurred:
            with self.subTest(text=text):
                labels = {
                    item.label
                    for item in prose_lint.scan("<test>", text, delivery_mode="gap-note-allowed")
                }
                self.assertIn("external-note-boundary", labels)

    def test_gap_note_mode_still_flags_model_leaks_after_note_heading(self) -> None:
        text = (
            "项目拟于8月启动。\n\n文后提示\n资金来源待确认。\n"
            "我的思路是先补齐预算。\n本稿不新增原文外事实。"
        )

        findings = prose_lint.scan("<test>", text, delivery_mode="gap-note-allowed")
        labels = {item.label for item in findings}

        self.assertIn("thought-leak", labels)
        self.assertNotIn("constraint-self-certification", labels)

    def test_delivery_mode_avoids_common_business_and_english_false_positives(self) -> None:
        text = "已根据要求完成调整。\nI will attend the meeting."

        labels = {item.label for item in prose_lint.scan("<test>", text, delivery_mode="draft-body")}

        self.assertNotIn("delivery-explanation", labels)
        self.assertNotIn("english-thought-fragment", labels)

    def test_draft_body_note_heading_requires_a_heading_boundary(self) -> None:
        text = "风险提醒机制建设情况\n已完成制度修订。"

        labels = {item.label for item in prose_lint.scan("<test>", text, delivery_mode="draft-body")}

        self.assertNotIn("unexpected-external-note", labels)

    def test_gap_note_mode_allows_quoted_or_inline_leak_examples(self) -> None:
        text = (
            "项目拟于8月启动。\n\n文后提示\n"
            "原句：“本稿不新增原文外事实。”\n"
            "命令示例：`We need to draft the report.`"
        )

        labels = {item.label for item in prose_lint.scan("<test>", text, delivery_mode="gap-note-allowed")}

        self.assertNotIn("constraint-self-certification", labels)
        self.assertNotIn("english-thought-fragment", labels)

    def test_draft_body_delivery_checks_scan_code_fences_without_format_flag(self) -> None:
        text = "```text\nWe need to draft the report.\n本稿不新增原文外事实。\n```"

        labels = {item.label for item in prose_lint.scan("<test>", text, delivery_mode="draft-body")}

        self.assertIn("english-thought-fragment", labels)
        self.assertIn("constraint-self-certification", labels)

    def test_draft_body_mode_rejects_external_note_region(self) -> None:
        texts = [
            "项目拟于8月启动。\n\n文后提示\n资金来源待确认。",
            "项目拟于8月启动。\n\n正文外提示：\n资金来源待确认。",
            "项目拟于8月启动。\n\n待用户确认事项：\n引用出处待核验。",
            "项目拟于8月启动。\n\n## 文后提示\n资金来源待确认。",
            "项目拟于8月启动。\n\n七、文后提示\n资金来源待确认。",
            "项目拟于8月启动。\n\n第七章 文后提示\n资金来源待确认。",
            "项目拟于8月启动。\n\n2. 文后提示\n资金来源待确认。",
            "项目拟于8月启动。\n\n（二）文后提示\n资金来源待确认。",
        ]

        for text in texts:
            with self.subTest(text=text):
                findings = prose_lint.scan("<test>", text, delivery_mode="draft-body")
                self.assertIn("unexpected-external-note", {item.label for item in findings})

    def test_numbered_business_headings_with_note_words_stay_in_body(self) -> None:
        texts = [
            "一、待确认事项办理情况\n已完成三项核对。",
            "第二章 补充信息管理办法\n本章规定信息补录流程。",
            "1.补充信息：本节说明接口补录范围和办理程序。\n后续内容仍属正文。",
            "经核查，待确认事项已全部确认。",
        ]

        for text in texts:
            with self.subTest(text=text):
                findings = prose_lint.scan("<test>", text, delivery_mode="draft-body")
                self.assertNotIn("unexpected-external-note", {item.label for item in findings})

    def test_delivery_mode_covers_common_narration_and_english_variants(self) -> None:
        text = (
            "从已有材料看，项目尚处于准备阶段。\n"
            "已根据用户要求完成修改。\n"
            "I will draft the final report."
        )

        findings = prose_lint.scan("<test>", text, delivery_mode="draft-body")
        by_line = {line: [item for item in findings if item.line == line] for line in range(1, 4)}

        self.assertTrue(any(item.label == "material-reading-narration" and item.severity == "medium" for item in by_line[1]))
        self.assertTrue(any(item.label == "delivery-explanation" and item.severity == "high" for item in by_line[2]))
        self.assertTrue(any(item.label == "english-thought-fragment" and item.severity == "high" for item in by_line[3]))

    def test_delivery_mode_catches_skill_reading_prefaces(self) -> None:
        texts = [
            "已按要求读取 Skill入口与文种路由，并对照决定骨架，正文如下：",
            "已按 Skill 起草并复核完成，以下为正文：",
            "已读取 Skill 主文件与命中资料，成稿如下：",
            "本轮按任务要求复核完成，稿件如下：",
        ]

        for text in texts:
            with self.subTest(text=text):
                findings = prose_lint.scan("<test>", text, delivery_mode="draft-body")
                self.assertTrue(
                    any(
                        item.label == "delivery-explanation" and item.severity == "high"
                        for item in findings
                    )
                )

    def test_draft_body_flags_common_delivery_metadata_without_a_raw_word_ban(self) -> None:
        leaked = [
            "本稿为脱敏版，仅供内部核对。",
            "以下为修改版，请领导审阅。",
            "这是给领导看的版本。",
            "当前工作流仅作只读核对。",
            "以下内容已经过内部校验。",
            "已通过内容门禁，可以交付。",
            "审核通过，以下为定稿版。",
        ]

        for text in leaked:
            with self.subTest(text=text):
                generic_labels = {item.label for item in prose_lint.scan("<test>", text)}
                findings = prose_lint.scan("<test>", text, delivery_mode="draft-body")
                metadata = [item for item in findings if item.label == "delivery-metadata"]

                self.assertNotIn("delivery-metadata", generic_labels)
                self.assertTrue(metadata)
                self.assertTrue({item.severity for item in metadata} <= {"medium", "high"})

    def test_delivery_metadata_rule_preserves_business_facts_and_visible_document_states(self) -> None:
        legitimate = [
            "根据领导要求，项目组已完成风险排查。",
            "本次调研使用脱敏数据，校验结果作为业务分析依据。",
            "《实施方案（征求意见稿）》",
            "项目通过内部审核后，由办公室按程序印发。",
            "本次只读接口核对发现3项字段差异。",
        ]

        for text in legitimate:
            with self.subTest(text=text):
                findings = prose_lint.scan("<test>", text, delivery_mode="draft-body")
                self.assertFalse([item for item in findings if item.label == "delivery-metadata"])

    def test_ambiguous_visible_labels_and_business_states_are_not_high_blockers(self) -> None:
        legitimate_or_ambiguous = [
            "本稿为脱敏版。",
            "本稿为送审稿。",
            "仅供内部人员审阅。",
            "项目已通过内部审核，可以报送省厅。",
            "以上材料已经过内部校验。",
            "本次处理流程包括数据归集和内部校验。",
        ]

        for text in legitimate_or_ambiguous:
            with self.subTest(text=text):
                findings = prose_lint.scan("<test>", text, delivery_mode="draft-body")
                metadata = [item for item in findings if item.label == "delivery-metadata"]
                self.assertFalse([item for item in metadata if item.severity == "high"])

    def test_draft_body_flags_delivery_boilerplate_and_exact_repeated_title(self) -> None:
        boilerplate = [
            "说明：以上内容已按用户要求整理，可直接使用。",
            "（小字说明：以上结论仅供参考，以实际审核结果为准。）",
            "免责声明：本文不构成正式意见。",
            "边界说明：本文仅依据已提供材料，不对事实真实性负责。",
            "方法说明：本稿先核对事实，再调整结构和表述。",
            "以上说明与正文内容一致，不再赘述。",
        ]
        for text in boilerplate:
            with self.subTest(text=text):
                findings = prose_lint.scan("<test>", text, delivery_mode="draft-body")
                self.assertTrue([item for item in findings if item.label == "delivery-boilerplate"])

        repeated_title = "关于开展安全检查的通知\n\n关于开展安全检查的通知\n\n各单位：\n请按要求开展检查。"
        findings = prose_lint.scan("<test>", repeated_title, delivery_mode="draft-body")
        self.assertTrue(any(item.label == "duplicate-title" and item.severity == "high" for item in findings))

    def test_delivery_boilerplate_only_applies_to_delivered_body(self) -> None:
        text = (
            "系统运行情况说明\n\n系统运行正常。\n\n"
            "文后提示\n免责声明：本文仅供参考，不构成正式意见。"
        )

        generic = prose_lint.scan("<test>", text)
        review = prose_lint.scan("<test>", text, delivery_mode="review-only")
        gap_allowed = prose_lint.scan("<test>", text, delivery_mode="gap-note-allowed")

        for findings in [generic, review, gap_allowed]:
            self.assertFalse([item for item in findings if item.label in {"delivery-boilerplate", "duplicate-title"}])

    def test_delivery_boilerplate_rule_preserves_real_scope_and_method_content(self) -> None:
        legitimate = [
            "本说明仅反映截至7月12日的检查情况。",
            "检查采用现场抽查和台账核验相结合的方式。",
            "责任边界：甲方负责设备维护，乙方负责现场管理。",
            "关于开展安全检查的通知\n各单位：\n请按要求开展检查。",
        ]

        for text in legitimate:
            with self.subTest(text=text):
                findings = prose_lint.scan("<test>", text, delivery_mode="draft-body")
                self.assertFalse([item for item in findings if item.label in {"delivery-boilerplate", "duplicate-title"}])

    def test_review_only_can_quote_delivery_metadata_without_flagging_the_reviewer(self) -> None:
        text = "位置：“本稿为脱敏版，仅供内部核对。”\n风险层级：高\n修改建议：删除制作说明。"

        findings = prose_lint.scan("<test>", text, delivery_mode="review-only")

        self.assertFalse([item for item in findings if item.label == "delivery-metadata"])

    def test_delivery_mode_does_not_flag_clean_official_material_references(self) -> None:
        text = (
            "报送材料应与业务系统现行字段保持一致。"
            "上述材料尚未完成归档，请责任单位于7月20日前补齐。"
        )

        findings = prose_lint.scan("<test>", text, delivery_mode="draft-body")

        self.assertFalse([item for item in findings if item.label == "material-reading-narration"])

    def test_source_backed_scope_language_is_advisory_not_a_high_leak(self) -> None:
        text = (
            "本次调研未覆盖乡镇窗口，现有材料未提供满意度数据，"
            "相关结论不扩大为全市基层服务窗口的整体结论。"
        )

        findings = prose_lint.scan("<test>", text, delivery_mode="draft-body")
        scoped = [
            item
            for item in findings
            if item.label in {"material-reading-narration", "constraint-self-certification"}
        ]

        self.assertTrue(scoped)
        self.assertEqual({item.severity for item in scoped}, {"medium"})

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

        overlapping = [
            item
            for item in prose_lint.scan("<test>", "XX项目拟于8月启动。")
            if item.label == "unfinished-placeholder"
        ]
        self.assertEqual(len(overlapping), 1)

    def test_parenthesized_instructions_are_not_treated_as_placeholders(self) -> None:
        text = (
            "请按要求办理（请于7月30日前确认反馈）。"
            "材料报送要求（请确认后反馈）。"
            "附件处理要求（请补充盖章）。"
        )

        placeholder_matches = [
            item.match
            for item in prose_lint.scan("<test>", text)
            if item.label == "unfinished-placeholder"
        ]

        self.assertEqual(placeholder_matches, [])

    def test_parenthesized_placeholder_phrases_remain_detectable(self) -> None:
        text = (
            "正文仍有（签发日期）、（会议时间）、（成文日期）、"
            "（待确认）、（项目金额待补充）、（联系人待填写）、"
            "（待签发）和（成文日期待确认）。"
        )

        placeholder_matches = [
            item.match
            for item in prose_lint.scan("<test>", text)
            if item.label == "unfinished-placeholder"
        ]

        self.assertEqual(len(placeholder_matches), 8)

    def test_external_confirmation_notes_are_not_treated_as_body_placeholders(self) -> None:
        text = (
            "关于事项的请示\n\n"
            "正文已按已知材料说明申请事项。\n\n"
            "待确认事项（正文外，供用户确认）：\n"
            "1. 成文日期待确认。\n"
            "2. [具体项目名称]和XXXX万元另行确认。"
        )

        labels = {item.label for item in prose_lint.scan("<test>", text, include_format=True)}

        self.assertNotIn("unfinished-placeholder", labels)
        self.assertNotIn("western-bullet", labels)
        self.assertIn(
            "unfinished-placeholder",
            {item.label for item in prose_lint.scan("<test>", "正文内仍有（成文日期待确认）。")},
        )

    def test_bracketed_confirmation_notes_are_not_treated_as_body_placeholders(self) -> None:
        text = (
            "正文已按已知材料完成。\n\n"
            "（正文外提示）\n"
            "1. [具体项目名称]待确认。\n\n"
            "待补充事项：预算口径待确认。"
        )

        labels = {item.label for item in prose_lint.scan("<test>", text, include_format=True)}

        self.assertNotIn("unfinished-placeholder", labels)
        self.assertNotIn("western-bullet", labels)

    def test_field_style_materials_do_not_block_medium_strict_lint(self) -> None:
        script = ROOT / "chinese-official-writing" / "scripts" / "prose_lint.py"
        text = (
            "项目名称：某单位办公自动化升级项目\n"
            "建设单位：某单位信息中心\n"
            "建设周期：2026年8月至2027年7月\n"
            "总投资：80万元\n"
        )

        findings = prose_lint.scan("<test>", text, include_format=True, include_structure=True)
        blocking = [item for item in findings if item.severity in {"medium", "high"}]
        card_findings = [item for item in findings if item.label == "project-card-summary"]

        self.assertEqual(blocking, [])
        self.assertTrue(card_findings)
        self.assertEqual({item.severity for item in card_findings}, {"low"})

        with tempfile.TemporaryDirectory() as temp_dir:
            sample = Path(temp_dir) / "field-style.md"
            sample.write_text(text, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(script), str(sample), "--format", "--structure", "--strict", "--fail-on", "medium"],
                capture_output=True,
                text=True,
                encoding="utf-8",
            )

        self.assertEqual(result.returncode, 0)

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

    def test_code_fence_does_not_hide_format_marks_when_format_checking(self) -> None:
        text = "```\n这里有半角,标点🙂 和 **加粗**。\n```"

        findings = prose_lint.scan("<test>", text, include_format=True)
        line_two_labels = {item.label for item in findings if item.line == 2}

        self.assertIn("halfwidth-punctuation", line_two_labels)
        self.assertIn("emoji-marker", line_two_labels)
        self.assertIn("markdown-bold", line_two_labels)

    def test_anti_ai_reference_high_frequency_phrases_are_linted(self) -> None:
        phrases = [
            "可以说，项目建设很有必要。",
            "综上所述，本项工作意义重大。",
            "这不仅是落实部署的需要，更是提升治理能力的需要。",
            "提供有力支撑。",
            "奠定坚实基础。",
            "有关方面认为，工作基础较好。",
            "业内专家指出，未来可期。",
            "未来可期。",
            "高度重视。",
            "再上新台阶。",
            "未发现重大隐患。",
            "总体较好，能够正常开展。",
            "持续推进。",
        ]

        findings = prose_lint.scan("<test>", "\n".join(phrases))
        matched_lines = {item.line for item in findings}

        self.assertEqual(matched_lines, set(range(1, len(phrases) + 1)))

    def test_side_commentary_boundaries_do_not_flag_negative_or_section_reference(self) -> None:
        text = "不可以说这个方案没有问题。\n本文综上所述部分如下。"

        findings = prose_lint.scan("<test>", text)

        self.assertFalse([item for item in findings if item.label == "side-commentary"])

    def test_summary_transition_flags_common_terminal_punctuation(self) -> None:
        text = "\n".join(
            [
                "综上所述，本项工作意义重大。",
                "综上所述。本项工作意义重大。",
                "综上所述：本项工作意义重大。",
                "综上所述；本项工作意义重大。",
                "本文综上所述部分如下。",
            ]
        )

        findings = prose_lint.scan("<test>", text)
        side_commentary_lines = {item.line for item in findings if item.label == "side-commentary"}

        self.assertEqual(side_commentary_lines, {1, 2, 3, 4})

    def test_unsupported_conclusion_keeps_warning_unless_check_basis_is_explicit(self) -> None:
        unsupported = prose_lint.scan("<test>", "未发现重大隐患。")
        supported = prose_lint.scan("<test>", "经现场检查，未发现重大隐患。")

        self.assertTrue([item for item in unsupported if item.label == "unsupported-conclusion"])
        self.assertFalse([item for item in supported if item.label == "unsupported-conclusion"])

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


class UnresolvedStateChainTests(unittest.TestCase):
    CHAIN = "供应商尚未确定，合同尚未签订，设备尚未到货，验收尚未实施，付款尚未发生。"

    def chain_findings(self, text, *, mode="draft-body", structure=True):
        return [
            item for item in prose_lint.scan(
                "<test>", text, include_format=True, include_structure=structure, delivery_mode=mode
            ) if item.label == "unresolved-state-chain"
        ]

    def test_same_sentence_unresolved_states_are_only_low_hints(self):
        cases = (
            (self.CHAIN, 5),
            ("审批尚未办结，资料仍未补齐，负责人还未签字。", 3),
            ("该项目尚未立项，仍未明确负责人，暂未安排经费。", 3),
            ("审批尚未办结，\n资料仍未补齐，\n负责人还未签字。", 3),
            ("甲站传感器尚未送达，乙站检验记录仍未完成，丙站负责人暂未到岗。", 3),
        )
        for text, count in cases:
            with self.subTest(text=text):
                findings = self.chain_findings("进展记录。\n" + text)
                self.assertEqual(len(findings), 1)
                self.assertEqual(findings[0].severity, "low")
                self.assertEqual(findings[0].line, 2)
                self.assertIn(f"{count} 项未决谓语", findings[0].excerpt)
                self.assertIn("有独立事实或办理作用时可保留", findings[0].excerpt)

    def test_short_or_separate_states_are_not_accumulated(self):
        for text in (
            "供应商尚未确定。",
            "供应商尚未确定，合同尚未签订。",
            "审批尚未办结。资料仍未补齐。负责人还未签字。",
            "审批尚未办结，\n\n资料仍未补齐，\n\n负责人还未签字。",
            "合同尚未签订，付款已经安排。\n\n设备尚未到货，验收尚未实施。",
        ):
            with self.subTest(text=text):
                self.assertEqual(self.chain_findings(text), [])

    def test_fields_lists_and_code_are_exempt(self):
        for text in (
            "供应商：尚未确定，合同：尚未签订，设备：尚未到货。",
            "供应商：尚未确定\n合同：尚未签订\n设备：尚未到货",
            "| 供应商 | 尚未确定 | 合同 | 尚未签订 | 设备 | 尚未到货 |",
            "供应商\t尚未确定\t合同\t尚未签订\t设备\t尚未到货",
            "- 供应商尚未确定，\n- 合同尚未签订，\n- 设备尚未到货。",
            "1. 供应商尚未确定，\n2. 合同尚未签订，\n3. 设备尚未到货。",
            f"```text\n{self.CHAIN}\n```",
            f"句式示例：`{self.CHAIN}`",
        ):
            with self.subTest(text=text):
                self.assertEqual(self.chain_findings(text), [])

    def test_source_quotes_are_exempt_without_hiding_unquoted_body(self):
        for text in (
            f"用户原文：“{self.CHAIN}”",
            f'材料原句："{self.CHAIN}"',
            "原句：“供应商尚未确定，\n合同尚未签订，设备尚未到货。”",
            f"> {self.CHAIN}",
            f"用户原文：\n{self.CHAIN}",
            f"原句如下：{self.CHAIN}",
            "材料写明“审批尚未办结，资料仍未补齐”，负责人还未签字。",
        ):
            with self.subTest(text=text):
                self.assertEqual(self.chain_findings(text), [])
        mixed = f"用户原文：“{self.CHAIN}”\n{self.CHAIN}"
        findings = self.chain_findings(mixed)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].line, 2)

    def test_hint_respects_structure_mode_and_postscript_boundaries(self):
        self.assertEqual(self.chain_findings(self.CHAIN, structure=False), [])
        for mode in ("generic", "review-only"):
            self.assertEqual(self.chain_findings(f"审稿意见：{self.CHAIN}", mode=mode), [])
        expected = self.chain_findings(self.CHAIN)
        self.assertEqual(self.chain_findings(self.CHAIN, mode="gap-note-allowed"), expected)
        for mode in ("draft-body", "gap-note-allowed"):
            with self.subTest(mode=mode):
                note_only = f"已完成核对。\n\n文后提示\n{self.CHAIN}"
                self.assertEqual(self.chain_findings(note_only, mode=mode), [])
                with_note = self.CHAIN + "\n\n文后提示\n" + self.CHAIN
                self.assertEqual(self.chain_findings(with_note, mode=mode), expected)

    def test_cli_modes_agree_without_medium_strict_failure(self):
        script = ROOT / "chinese-official-writing/scripts/prose_lint.py"
        reports = []
        for mode in ("draft-body", "gap-note-allowed"):
            result = subprocess.run(
                [sys.executable, str(script), "--structure", "--format", "--json", "--strict",
                 "--fail-on", "medium", "--delivery-mode", mode, "-"],
                input=self.CHAIN, text=True, encoding="utf-8", capture_output=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            reports.append(json.loads(result.stdout))
        self.assertEqual(reports[0], reports[1])
        self.assertEqual(len(reports[0]), 1)
        self.assertEqual(reports[0][0]["label"], "unresolved-state-chain")
        self.assertEqual(reports[0][0]["severity"], "low")


class ProseLintCliTests(unittest.TestCase):
    def test_cli_markdown_postscript_keeps_partition_and_low_format_risks(self):
        script = ROOT / "chinese-official-writing/scripts/prose_lint.py"
        for heading, expected_label in (
            ("**文后提示**", "markdown-bold"),
            ("*文后提示*", "markdown-emphasis"),
            ("## 文后提示", "markdown-heading"),
        ):
            with self.subTest(heading=heading):
                result = subprocess.run(
                    [sys.executable, str(script), "--json", "--format", "--delivery-mode", "gap-note-allowed",
                     "--strict", "--fail-on", "medium", "-"],
                    input=f"已完成核对。\n\n{heading}\n[具体项目名称]待确认。",
                    text=True, encoding="utf-8", capture_output=True,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                findings = json.loads(result.stdout)
                self.assertIn(expected_label, {item["label"] for item in findings})
                self.assertNotIn("unfinished-placeholder", {item["label"] for item in findings})

    def test_normal_chapters_and_body_tails_are_scanned_in_both_delivery_modes(self) -> None:
        script = ROOT / "chinese-official-writing/scripts/prose_lint.py"
        tails = "\n".join(text for _, text in NEGATIVE_TAIL_CASES)
        text = f"一、进展\n已完成核对。\n\n二、风险提醒\n预算仍为XXXX万元。\n{tails}\n\n三、补充信息\n联系地址待确认。"
        reports = []
        for mode in ("draft-body", "gap-note-allowed"):
            result = subprocess.run(
                [sys.executable, str(script), "--json", "--delivery-mode", mode, "-"],
                input=text, text=True, encoding="utf-8", capture_output=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            reports.append(json.loads(result.stdout))
        self.assertEqual(reports[0], reports[1])
        labels = {item["label"] for item in reports[1]}
        self.assertIn("unfinished-placeholder", labels)
        self.assertTrue({label for label, _ in NEGATIVE_TAIL_CASES}.issubset(labels))
        self.assertNotIn("external-note-boundary", labels)
        self.assertNotIn("unexpected-external-note", labels)

    def test_cli_postscript_exempts_body_risks_and_retains_identity_checks(self) -> None:
        script = ROOT / "chinese-official-writing/scripts/prose_lint.py"
        notes = "\n".join(text for _, text in NEGATIVE_TAIL_CASES)
        text = f"已完成核对。\n\n文后提示\n{notes}\n[具体项目名称]待确认。\n本审稿意见由AI生成。"
        result = subprocess.run(
            [sys.executable, str(script), "--json", "--delivery-mode", "gap-note-allowed", "-"],
            input=text, text=True, encoding="utf-8", capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        labels = {item["label"] for item in json.loads(result.stdout)}
        self.assertTrue({label for label, _ in NEGATIVE_TAIL_CASES}.isdisjoint(labels))
        self.assertNotIn("unfinished-placeholder", labels)
        self.assertIn("thought-leak", labels)

    def test_delivery_mode_cli_is_opt_in_and_can_fail_on_high(self) -> None:
        script = ROOT / "chinese-official-writing" / "scripts" / "prose_lint.py"
        with tempfile.TemporaryDirectory() as temp_dir:
            draft = Path(temp_dir) / "draft.md"
            draft.write_text(
                "由于现有材料仅反映阶段性情况，暂无法形成完整判断。\n"
                "本稿不新增原文外事实。",
                encoding="utf-8",
            )

            default_result = subprocess.run(
                [sys.executable, str(script), str(draft), "--strict", "--fail-on", "high"],
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
            delivery_result = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    str(draft),
                    "--delivery-mode",
                    "draft-body",
                    "--strict",
                    "--fail-on",
                    "high",
                    "--json",
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
            )

        self.assertEqual(default_result.returncode, 0)
        self.assertEqual(delivery_result.returncode, 1)
        self.assertIn("material-reading-narration", delivery_result.stdout)
        self.assertIn("constraint-self-certification", delivery_result.stdout)

    def test_cli_is_read_only_even_for_quoted_colloquial_text(self) -> None:
        script = ROOT / "chinese-official-writing" / "scripts" / "prose_lint.py"
        with tempfile.TemporaryDirectory() as temp_dir:
            draft = Path(temp_dir) / "quoted-source.md"
            original = "原文引语：\u201c我觉得这个方案差不多能用，老板也挺关心。\u201d\n"
            draft.write_text(original, encoding="utf-8")

            subprocess.run(
                [sys.executable, str(script), "--format", "--structure", str(draft)],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )

            self.assertEqual(draft.read_text(encoding="utf-8"), original)

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

    def test_docx_lint_reads_headers_and_footers_beyond_first_three(self) -> None:
        script = ROOT / "chinese-official-writing" / "scripts" / "prose_lint.py"
        namespace = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
        with tempfile.TemporaryDirectory() as temp_dir:
            draft = Path(temp_dir) / "multiple-sections.docx"
            with zipfile.ZipFile(draft, "w") as archive:
                for name, root, text in (
                    ("document", "document", "正文内容。"),
                    ("header4", "hdr", "作为AI"),
                    ("footer12", "ftr", "我的思路是"),
                ):
                    archive.writestr(
                        f"word/{name}.xml",
                        f'<w:{root} xmlns:w="{namespace}"><w:p><w:r><w:t>'
                        f"{text}</w:t></w:r></w:p></w:{root}>",
                    )
            result = subprocess.run(
                [sys.executable, str(script), str(draft), "--json"],
                capture_output=True,
                text=True,
                encoding="utf-8",
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        findings = json.loads(result.stdout)
        self.assertEqual(
            {item["match"] for item in findings if item["label"] == "thought-leak"},
            {"作为AI", "我的思路"},
        )
        self.assertEqual(result.stderr, "")

    def test_docx_without_main_document_reports_error_in_default_lint(self) -> None:
        script = ROOT / "chinese-official-writing" / "scripts" / "prose_lint.py"
        with tempfile.TemporaryDirectory() as temp_dir:
            draft = Path(temp_dir) / "missing-main.docx"
            with zipfile.ZipFile(draft, "w") as archive:
                archive.writestr("word/header1.xml", "<hdr/>")
            result = subprocess.run(
                [sys.executable, str(script), str(draft), "--json"],
                capture_output=True,
                text=True,
                encoding="utf-8",
            )

        self.assertEqual(result.returncode, 2)
        self.assertIn("ERROR: DOCX 缺少主文档内容", result.stderr)
        self.assertNotIn("Traceback", result.stderr + result.stdout)
        self.assertEqual(json.loads(result.stdout), [])

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

    def test_markdown_horizontal_rule_is_format_finding(self) -> None:
        text = "关于开展网络安全自查工作的通知\n\n各部门：\n请按期反馈。\n\n---\n\n说明：已压缩。"

        findings = prose_lint.scan("<test>", text, include_format=True)
        labels = {item.label for item in findings}

        self.assertIn("markdown-horizontal-rule", labels)

    def test_yaml_frontmatter_delimiters_are_not_horizontal_rule_findings(self) -> None:
        text = "---\nname: sample\ndescription: test\n---\n\n正文内容。"

        findings = prose_lint.scan("<test>", text, include_format=True)
        labels = {item.label for item in findings}

        self.assertNotIn("markdown-horizontal-rule", labels)


class CleanProseCorpusTests(unittest.TestCase):
    def test_clean_corpus_has_no_medium_or_high_findings(self) -> None:
        corpus_path = ROOT / "maintenance" / "tests" / "fixtures" / "clean_prose_corpus.json"
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

    def test_clean_corpus_has_no_delivery_mode_high_findings(self) -> None:
        corpus_path = ROOT / "maintenance" / "tests" / "fixtures" / "clean_prose_corpus.json"
        corpus = json.loads(corpus_path.read_text(encoding="utf-8"))

        for item in corpus["items"]:
            with self.subTest(item=item["id"]):
                findings = prose_lint.scan(
                    item["id"],
                    item["text"],
                    include_format=True,
                    include_structure=True,
                    delivery_mode="draft-body",
                )
                high = [finding for finding in findings if finding.severity == "high"]

                self.assertEqual(high, [])

    def test_clean_corpus_sentinel_placeholder_is_detected(self) -> None:
        corpus_path = ROOT / "maintenance" / "tests" / "fixtures" / "clean_prose_corpus.json"
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
    def test_evaluate_uses_draft_body_delivery_mode(self) -> None:
        class LintProbe:
            kwargs: dict[str, object] = {}

            def scan(self, *args, **kwargs):
                self.kwargs = kwargs
                return []

        probe = LintProbe()
        profile = {"genre": "报告", "required_points": []}
        draft = {"id": "sample", "mode": "skill", "text": "关于有关事项的报告"}

        real_eval.evaluate(profile, draft, probe)

        self.assertEqual(probe.kwargs["delivery_mode"], "draft-body")

    def test_placeholder_echo_terms_are_reported(self) -> None:
        text = "发文机关以发文字号印发工作方案，主送单位包括有关部门。"

        self.assertEqual(real_eval.placeholder_echo_terms(text), ["主送单位", "发文字号", "发文机关"])

    def test_exact_term_hits_are_counted_separately_from_coverage(self) -> None:
        points = [{"terms": ["发文机关", "发文字号"]}, {"terms": ["主送单位", "有关部门"]}]

        hits, total = real_eval.exact_term_hits(points, "发文机关以发文字号印发工作方案。")

        self.assertEqual(hits, ["发文字号", "发文机关"])
        self.assertEqual(total, 4)

    def test_required_point_matching_ignores_punctuation_boundaries(self) -> None:
        self.assertTrue(real_eval.point_covered({"terms": ["请示收悉"]}, "《请示》收悉。"))
        self.assertTrue(real_eval.point_covered({"terms": ["曝光问责"]}, "媒体曝光、问责。"))


class AgentEvalSummaryTests(unittest.TestCase):
    def test_winner_counts_parse_writer_format(self) -> None:
        review = "Overall winner count: Writer A 10, Writer B 0, Tie 0."

        self.assertEqual(agent_eval.parse_winner_counts([review]), {"A": 10, "B": 0, "Tie": 0})

    def test_agent_ablation_timeout_returns_124_without_traceback(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            out_path = Path(temp_dir) / "out.md"
            timeout = subprocess.TimeoutExpired(cmd=["agent"], timeout=1, output="partial", stderr="late")
            with mock.patch.object(agent_eval, "external_cmd", return_value=["agent"]), mock.patch.object(
                agent_eval.subprocess, "run", side_effect=timeout
            ):
                code = agent_eval.call_external("prompt", ROOT, 1, out_path)

            self.assertEqual(code, 124)
            text = out_path.read_text(encoding="utf-8")
            self.assertIn("partial", text)
            self.assertIn("timed out", text)
            self.assertIn("late", text)

    def test_revision_command_timeout_returns_124_without_traceback(self) -> None:
        timeout = subprocess.TimeoutExpired(cmd=["agent"], timeout=1, output="partial", stderr="late")
        with mock.patch.object(revision_eval, "agent_command", return_value=["agent"]), mock.patch.object(
            revision_eval.subprocess, "run", side_effect=timeout
        ):
            output, code, stderr = revision_eval.call_command("prompt", "agent", 1)

        self.assertEqual(code, 124)
        self.assertIn("partial", output)
        self.assertIn("timed out", stderr)
        self.assertIn("late", stderr)

    def test_revision_codex_timeout_returns_124_without_traceback(self) -> None:
        timeout = subprocess.TimeoutExpired(cmd=["codex"], timeout=1, output="partial", stderr="late")
        with mock.patch.object(revision_eval.shutil, "which", return_value="codex"), mock.patch.object(
            revision_eval.subprocess, "run", side_effect=timeout
        ):
            output, code, stderr = revision_eval.call_codex("prompt", 1)

        self.assertEqual(code, 124)
        self.assertIn("partial", output)
        self.assertIn("timed out", stderr)
        self.assertIn("late", stderr)


if __name__ == "__main__":
    unittest.main()
