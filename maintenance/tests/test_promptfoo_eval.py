from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
FINAL_REVIEW_PATHS = [
    "references/final-review-layers.md",
    "references/anti-ai-patterns.md",
    "references/prose-lint-usage.md",
    "references/delivery.md",
]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


provider = load_module(
    "official_promptfoo_provider_under_test",
    ROOT / "maintenance" / "evals" / "official-writing" / "providers" / "agent_writer.py",
)


class PromptfooProviderTests(unittest.TestCase):
    def test_primary_genres_select_one_dedicated_leaf(self) -> None:
        expected = {
            "报告": "references/genre-playbook-report.md",
            "请示": "references/genre-playbook-request.md",
            "通知": "references/genre-playbook-notice.md",
            "函": "references/genre-playbook-correspondence.md",
            "会议纪要": "references/genre-playbook-minutes.md",
            "方案": "references/genre-playbook-plan-construction.md",
            "调研报告": "references/genre-playbook-research.md",
            "讲话稿": "references/genre-playbook-speech-address.md",
            "制度": "references/genre-playbook-institution-rules.md",
            "采购审查": "references/genre-playbook-procurement-review.md",
            "决定": "references/genre-playbook-decision.md",
            "批复": "references/genre-playbook-reply.md",
            "意见": "references/genre-playbook-opinion.md",
            "说明": "references/genre-playbook-explanation.md",
            "新闻消息": "references/genre-playbook-news-message.md",
            "新闻评论": "references/genre-playbook-news-commentary.md",
        }
        for genre, leaf in expected.items():
            with self.subTest(genre=genre):
                refs = provider._reference_paths_for_genres([genre])
                self.assertIn(leaf, refs)
                self.assertNotIn("references/genre-playbooks.md", refs)

    def test_distinct_primary_genres_do_not_share_mixed_skeleton_pages(self) -> None:
        expected = {
            "公告": "references/genre-playbook-publication.md",
            "可研报告": "references/genre-playbook-feasibility.md",
            "采购公告": "references/genre-playbook-procurement-announcement.md",
            "部署": "references/genre-playbook-deployment.md",
            "意见建议": "references/genre-playbook-advisory-feedback.md",
            "投诉": "references/genre-playbook-complaint-reflection.md",
            "整改方案": "references/genre-playbook-remediation-plan.md",
            "项目申请": "references/genre-playbook-project-application.md",
        }
        for genre, leaf in expected.items():
            with self.subTest(genre=genre):
                refs = provider._reference_paths_for_genres([genre], [f"起草{genre}"])
                self.assertIn(leaf, refs)
                self.assertNotIn("references/genre-playbooks.md", refs)

    def test_decision_family_drafting_and_natural_review_read_one_genre_leaf(self) -> None:
        expected = {
            "决定": "references/genre-playbook-decision.md",
            "决议": "references/genre-playbook-resolution.md",
            "议案": "references/genre-playbook-motion.md",
            "公报": "references/genre-playbook-communique.md",
            "命令": "references/genre-playbook-order.md",
        }
        for genre, leaf in expected.items():
            with self.subTest(genre=genre, mode="draft"):
                refs = provider._reference_paths_for_genres([genre], [f"请按材料起草这份{genre}。"])
                self.assertEqual(refs, ["SKILL.md", "references/information-selection.md", leaf] + FINAL_REVIEW_PATHS)
            with self.subTest(genre=genre, mode="review"):
                refs = provider._reference_paths_for_genres([genre], [f"帮我审核这份{genre}。"])
                self.assertEqual(refs, ["SKILL.md", leaf, "references/review-checklist.md"] + FINAL_REVIEW_PATHS)

    def test_reply_opinion_explanation_are_independent_from_generic_checklist(self) -> None:
        for genre, leaf in {
            "批复": "references/genre-playbook-reply.md",
            "意见": "references/genre-playbook-opinion.md",
            "说明": "references/genre-playbook-explanation.md",
        }.items():
            with self.subTest(genre=genre):
                refs = provider._reference_paths_for_genres([genre], [f"起草{genre}"])
                self.assertEqual(refs, ["SKILL.md", "references/information-selection.md", leaf] + FINAL_REVIEW_PATHS)
                self.assertNotIn("references/genre-checklist.md", refs)

    def test_unknown_genre_uses_router_and_minimal_checklist(self) -> None:
        refs = provider._reference_paths_for_genres(["未知材料"])
        self.assertEqual(
            refs,
            ["SKILL.md", "references/information-selection.md", "references/genre-routing.md", "references/genre-checklist.md"] + FINAL_REVIEW_PATHS,
        )

    def test_deleted_mixed_directory_is_never_selected(self) -> None:
        for genre, task in [
            ("请示", "请起草请示"),
            ("通知", "请起草通知"),
            ("通用材料", "写一份材料"),
            ("模型服务技术需求", "写技术需求"),
        ]:
            with self.subTest(genre=genre):
                self.assertNotIn(
                    "references/genre-playbooks.md",
                    provider._reference_paths_for_genres([genre], [task]),
                )

    def test_compute_is_an_overlay_after_a_primary_leaf(self) -> None:
        refs = provider._reference_paths_for_genres(
            ["报告"], ["请起草一份 AI 模型服务报告，只输出正文。"]
        )
        self.assertIn("references/genre-playbook-report.md", refs)
        self.assertIn("references/ai-compute-docs.md", refs)
        self.assertNotIn("references/genre-playbooks.md", refs)

        exact = provider._reference_paths_for_genres(["算力服务可研报告"])
        self.assertEqual(
            exact,
            ["SKILL.md", "references/information-selection.md", "references/genre-playbook-feasibility.md", "references/ai-compute-docs.md"] + FINAL_REVIEW_PATHS,
        )

    def test_non_ai_cloud_task_does_not_load_compute_overlay(self) -> None:
        refs = provider._reference_paths_for_genres(
            ["说明"], ["普通政务网站部署在云端，需要说明 SLA 和并发，不涉及 AI、模型或 GPU。"]
        )
        self.assertNotIn("references/ai-compute-docs.md", refs)

    def test_speech_person_order_is_a_conditional_overlay(self) -> None:
        base = provider._reference_paths_for_genres(["讲话稿"])
        ordered = provider._reference_paths_for_genres(
            ["讲话稿"], ["写讲话稿，开场按职务排序。"]
        )
        self.assertNotIn("references/speech-person-order.md", base)
        self.assertIn("references/speech-person-order.md", ordered)
        self.assertIn("references/genre-playbook-speech-address.md", ordered)

    def test_complex_work_uses_composable_common_pages_without_retired_workflow(self) -> None:
        complex_refs = provider._reference_paths_for_genres(
            ["报告"], ["请把多材料合稿整理成一份800字完整报告。"]
        )
        self.assertEqual(
            complex_refs,
            [
                "SKILL.md",
                "references/information-selection.md",
                "references/genre-playbook-report.md",
                "references/handling-elements.md",
                "references/argument-chains.md",
                "references/compression-details.md",
                *FINAL_REVIEW_PATHS,
            ],
        )
        self.assertNotIn("references/workflow.md", complex_refs)

        format_refs = provider._reference_paths_for_genres(
            ["通知"], ["按 GB/T 9704 排成 Word 正式文件。"]
        )
        self.assertIn("references/format-gbt9704.md", format_refs)
        self.assertNotIn("references/genre-playbooks.md", format_refs)

    def test_sparse_and_minutes_routes_do_not_mix_other_genres(self) -> None:
        sparse = provider._reference_paths_for_genres(
            ["报告"], ["材料只有两项事实，请写简短报告，不新增事实。"]
        )
        self.assertEqual(
            sparse,
            [
                "SKILL.md",
                "references/information-selection.md",
                "references/task-route-cards.md",
                "references/short-draft-naturalness.md",
                "references/genre-playbook-report.md",
                *FINAL_REVIEW_PATHS,
            ],
        )
        minutes = provider._reference_paths_for_genres(
            ["会议纪要"], ["材料只有建议，未形成决定，请写简短会议纪要。"]
        )
        self.assertEqual(minutes, ["SKILL.md", "references/information-selection.md", "references/genre-playbook-minutes.md"] + FINAL_REVIEW_PATHS)

    def test_short_route_is_a_mode_overlay_on_the_primary_genre(self) -> None:
        short_application = provider._reference_paths_for_genres(
            ["申请"], ["请起草一份简短申请，只按已给字段，不新增事实。"]
        )
        self.assertEqual(
            short_application,
            [
                "SKILL.md",
                "references/information-selection.md",
                "references/task-route-cards.md",
                "references/short-draft-naturalness.md",
                "references/genre-playbook-request.md",
                *FINAL_REVIEW_PATHS,
            ],
        )
        long_application = provider._reference_paths_for_genres(
            ["申请"], ["请起草一份完整申请，说明用途、金额和实施安排。"]
        )
        self.assertNotIn("references/task-route-cards.md", long_application)
        self.assertIn("references/genre-playbook-request.md", long_application)

    def test_natural_review_requests_keep_one_primary_and_full_review(self) -> None:
        cases = [
            ("通知", "帮我审核一下这份通知。", "references/genre-playbook-notice.md"),
            ("会议纪要", "帮我复核这份会议纪要。", "references/genre-playbook-minutes.md"),
            ("报告", "请审校这份报告的事实和状态。", "references/genre-playbook-report.md"),
            ("采购审查", "帮我把关这份采购审查稿件。", "references/genre-playbook-procurement-review.md"),
        ]
        for genre, task, leaf in cases:
            with self.subTest(genre=genre, task=task):
                refs = provider._reference_paths_for_genres([genre], [task])
                self.assertEqual(refs, ["SKILL.md", leaf, "references/review-checklist.md"] + FINAL_REVIEW_PATHS)

    def test_explicit_review_scope_keeps_common_review_stages(self) -> None:
        refs = provider._reference_paths_for_genres(
            ["通知"], ["只审不改，检查这份通知的格式和语气。"]
        )
        self.assertEqual(
            refs,
            ["SKILL.md", "references/genre-playbook-notice.md", "references/review-checklist.md"] + FINAL_REVIEW_PATHS,
        )

    def test_review_and_rewrite_keep_the_same_primary_scene(self) -> None:
        review = provider._reference_paths_for_genres(
            ["采购审查"], ["只审不改，检查这份采购审查的字段和结论状态。"]
        )
        rewrite = provider._reference_paths_for_genres(
            ["采购审查"], ["根据材料改写采购审查正文。"]
        )
        leaf = "references/genre-playbook-procurement-review.md"
        self.assertIn(leaf, review)
        self.assertIn(leaf, rewrite)
        self.assertNotIn("references/genre-playbook-notice.md", review)

    def test_all_deliveries_keep_mandatory_review_and_delivery_stages(self) -> None:
        for task in ["请起草一份意见。", "请起草一份意见，只输出完整正文。"]:
            with self.subTest(task=task):
                self.assertEqual(
                    provider._reference_paths_for_genres(["意见"], [task]),
                    ["SKILL.md", "references/information-selection.md", "references/genre-playbook-opinion.md"] + FINAL_REVIEW_PATHS,
                )

    def test_natural_delivery_phrasing_uses_the_same_final_delivery_page(self) -> None:
        for task in ["帮我写完整稿子。", "帮我写完整稿子，不需要解释。"]:
            with self.subTest(task=task):
                refs = provider._reference_paths_for_genres(["报告"], [task])
                self.assertEqual(refs[-4:], FINAL_REVIEW_PATHS)
                self.assertNotIn("references/delivery-body-only.md", refs)

    def test_skill_prompt_does_not_inject_length_or_suppress_notes(self) -> None:
        cases = [{"vars": {"case_id": "C001", "genre": "报告", "task": "帮我写完整稿子。"}}]
        with mock.patch.object(provider, "_load_skill_context_from_paths", return_value="test skill context"):
            prompt = provider._skill_prompt(cases, {"repoRoot": str(ROOT)})
        self.assertIn("帮我写完整稿子。", prompt)
        self.assertNotRegex(prompt, r"160\s*[-—～至]\s*260")
        for suppression in ["省略文后提示", "不附文后提示", "只输出正文"]:
            self.assertNotIn(suppression, prompt)

    def test_length_check_precedes_common_final_stages(self) -> None:
        for genre, task in [
            ("报告", "起草800字报告"),
            ("新闻消息", "起草300字新闻消息"),
            ("通知", "审核这份通知的格式并核对字数"),
        ]:
            with self.subTest(genre=genre, task=task):
                refs = provider._reference_paths_for_genres([genre], [task])
                self.assertEqual(refs[-5:], ["references/compression-details.md"] + FINAL_REVIEW_PATHS)
                self.assertEqual(len(refs), len(set(refs)))

    def test_transaction_names_keep_a_primary_leaf(self) -> None:
        meeting_notice = provider._reference_paths_for_genres(["通知"], ["起草会议通知"])
        procurement_application = provider._reference_paths_for_genres(
            ["申请"], ["起草采购申请，列明品名、数量和预算"]
        )
        self.assertEqual(meeting_notice, ["SKILL.md", "references/information-selection.md", "references/genre-playbook-notice.md"] + FINAL_REVIEW_PATHS)
        self.assertIn("references/genre-playbook-request.md", procurement_application)
        self.assertNotIn("references/compatibility-scene-routing.md", procurement_application)

    def test_report_transaction_overlays_keep_report_as_primary(self) -> None:
        remediation = provider._reference_paths_for_genres(
            ["报告"], ["起草整改进展报告，只输出正文。"]
        )
        feedback = provider._reference_paths_for_genres(
            ["反馈报告"], ["起草反馈情况报告，只输出正文。"]
        )
        self.assertEqual(remediation[2], "references/genre-playbook-report.md")
        self.assertIn("references/transaction-remediation-report.md", remediation)
        self.assertEqual(feedback[2], "references/genre-playbook-report.md")
        self.assertIn("references/transaction-feedback-report.md", feedback)
        self.assertNotIn("references/genre-playbook-remediation-plan.md", remediation)

    def test_external_research_is_explicit(self) -> None:
        ordinary = provider._reference_paths_for_genres(
            ["报告"], ["根据给定材料起草报告。"]
        )
        ordinary_state = provider._reference_paths_for_genres(
            ["讲话稿"], ["围绕当前工作考虑起草讲话稿。"]
        )
        current = provider._reference_paths_for_genres(
            ["报告"], ["核验现行政策和最新公开来源后起草报告。"]
        )
        self.assertNotIn("references/external-research.md", ordinary)
        self.assertNotIn("references/external-research.md", ordinary_state)
        self.assertIn("references/external-research.md", current)

    def test_context_loader_is_flat_and_fails_closed(self) -> None:
        refs = provider._reference_paths_for_genres(["通知"])
        context = provider._load_skill_context(ROOT, ["通知"])
        self.assertLessEqual(len(context), provider.MAX_SKILL_CONTEXT_CHARS)
        for relative in refs:
            self.assertIn((ROOT / "packages/agent-skills/skills/chinese-official-writing" / relative).read_text(encoding="utf-8"), context)
        with mock.patch.object(provider, "_reference_paths_for_genres", return_value=["SKILL.md", "references/missing-route.md"]):
            with self.assertRaisesRegex(provider.ProviderError, "selected skill reference does not exist"):
                provider._load_skill_context(ROOT, ["通用材料"])

    def test_context_budget_failure_is_explicit(self) -> None:
        with mock.patch.object(provider, "MAX_SKILL_CONTEXT_CHARS", 10):
            with self.assertRaisesRegex(provider.ProviderError, "selected skill context exceeds 10 characters"):
                provider._load_skill_context(ROOT, ["通用材料"])

    def test_model_stderr_does_not_enter_draft_text(self) -> None:
        completed = mock.Mock(returncode=0, stdout="### C001\n正文", stderr="cli warning")
        with mock.patch.object(provider.subprocess, "run", return_value=completed):
            output, code, _ = provider.call_model_prompt(
                "prompt",
                ROOT,
                5,
                config={"commandTemplate": "agent"},
                retries=0,
            )
        self.assertEqual(code, 0)
        self.assertEqual(output, "### C001\n正文")
        self.assertNotIn("cli warning", output)

    def test_batching_keeps_reference_signatures_separate(self) -> None:
        cases = [
            {"vars": {"case_id": "R1", "genre": "报告", "task": "材料只有事实，请写简短报告。"}},
            {"vars": {"case_id": "R2", "genre": "报告", "task": "写一份多材料合稿的800字完整报告。"}},
            {"vars": {"case_id": "R3", "genre": "通知", "task": "只审不改，检查格式。"}},
        ]
        batches = provider._batch_cases("skill", cases, batch_size=10)
        self.assertEqual(len(batches), 3)
        for batch in batches:
            self.assertEqual(len({tuple(provider._case_reference_paths(case)) for case in batch}), 1)

    def test_ai_negation_boundary(self) -> None:
        self.assertFalse(provider._is_ai_compute("说明", ["不涉及 AI 或 GPU。"]))
        self.assertTrue(provider._is_ai_compute("说明", ["说明本地模型推理服务。"]))


if __name__ == "__main__":
    unittest.main()
