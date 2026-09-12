from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]


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
            "报告": "references/genre-checklist-report.md",
            "请示": "references/genre-playbook-request.md",
            "通知": "references/genre-playbook-notice.md",
            "函": "references/genre-playbook-correspondence.md",
            "会议纪要": "references/genre-playbook-minutes.md",
            "方案": "references/genre-playbook-plan-construction.md",
            "调研报告": "references/genre-playbook-research.md",
            "讲话稿": "references/genre-playbook-speech-address.md",
            "制度": "references/genre-playbook-institution-rules.md",
            "采购审查": "references/genre-playbook-procurement-review.md",
            "决定": "references/genre-playbook-deliberation.md",
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

    def test_reply_opinion_explanation_are_independent_from_generic_checklist(self) -> None:
        for genre, leaf in {
            "批复": "references/genre-playbook-reply.md",
            "意见": "references/genre-playbook-opinion.md",
            "说明": "references/genre-playbook-explanation.md",
        }.items():
            with self.subTest(genre=genre):
                refs = provider._reference_paths_for_genres([genre], [f"起草{genre}"])
                self.assertEqual(refs, ["SKILL.md", leaf])
                self.assertNotIn("references/genre-checklist.md", refs)

    def test_unknown_genre_uses_router_and_minimal_checklist(self) -> None:
        refs = provider._reference_paths_for_genres(["未知材料"])
        self.assertEqual(
            refs,
            ["SKILL.md", "references/genre-routing.md", "references/genre-checklist.md"],
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
        self.assertIn("references/genre-checklist-report.md", refs)
        self.assertIn("references/ai-compute-docs.md", refs)
        self.assertNotIn("references/genre-playbooks.md", refs)

        exact = provider._reference_paths_for_genres(["算力服务可研报告"])
        self.assertEqual(exact, ["SKILL.md", "references/ai-compute-docs.md"])

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

    def test_workflow_overlays_are_signal_gated(self) -> None:
        complex_refs = provider._reference_paths_for_genres(
            ["报告"], ["请把多材料合稿整理成一份800字完整报告。"]
        )
        self.assertIn("references/workflow.md", complex_refs)
        self.assertIn("references/handling-elements.md", complex_refs)
        self.assertIn("references/argument-chains.md", complex_refs)

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
                "references/genre-checklist-report.md",
            ],
        )
        minutes = provider._reference_paths_for_genres(
            ["会议纪要"], ["材料只有建议，未形成决定，请写简短会议纪要。"]
        )
        self.assertEqual(minutes, ["SKILL.md", "references/genre-playbook-minutes.md"])

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
            ],
        )
        long_application = provider._reference_paths_for_genres(
            ["申请"], ["请起草一份完整申请，说明用途、金额和实施安排。"]
        )
        self.assertNotIn("references/task-route-cards.md", long_application)
        self.assertIn("references/genre-playbook-request.md", long_application)

    def test_review_route_does_not_force_drafting_layers(self) -> None:
        refs = provider._reference_paths_for_genres(
            ["通知"], ["只审不改，检查这份通知的格式和语气。"]
        )
        self.assertIn("references/review-checklist.md", refs)
        self.assertIn("references/genre-playbook-notice.md", refs)
        self.assertNotIn("references/workflow.md", refs)

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

    def test_body_only_delivery_adds_anti_narration_overlay(self) -> None:
        ordinary = provider._reference_paths_for_genres(["意见"], ["请起草一份意见。"])
        body_only = provider._reference_paths_for_genres(
            ["意见"], ["请起草一份意见，只输出完整正文。"]
        )
        self.assertNotIn("references/anti-ai-patterns.md", ordinary)
        self.assertIn("references/genre-playbook-opinion.md", body_only)
        self.assertIn("references/anti-ai-patterns.md", body_only)

    def test_transaction_names_keep_a_primary_leaf(self) -> None:
        meeting_notice = provider._reference_paths_for_genres(["通知"], ["起草会议通知"])
        procurement_application = provider._reference_paths_for_genres(
            ["申请"], ["起草采购申请，列明品名、数量和预算"]
        )
        self.assertEqual(meeting_notice, ["SKILL.md", "references/genre-playbook-notice.md"])
        self.assertIn("references/genre-playbook-request.md", procurement_application)
        self.assertNotIn("references/compatibility-scene-routing.md", procurement_application)

    def test_external_research_is_explicit(self) -> None:
        ordinary = provider._reference_paths_for_genres(
            ["报告"], ["根据给定材料起草报告。"]
        )
        current = provider._reference_paths_for_genres(
            ["报告"], ["核验现行政策和最新公开来源后起草报告。"]
        )
        self.assertNotIn("references/external-research.md", ordinary)
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
