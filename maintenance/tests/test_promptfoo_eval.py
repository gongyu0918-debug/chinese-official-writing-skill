from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
# SKILL.md's four-step contract is owned by writing-rules.md; its review step
# requires anti-ai-patterns and prose-lint-usage. Keep this oracle independent
# of the provider's route tables.
COMMON_WRITING_PATHS = [
    "references/writing-rules.md",
    "references/anti-ai-patterns.md",
    "references/prose-lint-usage.md",
]
PROCUREMENT_OVERLAY = "references/genre-playbook-procurement-review.md"


def primary_leaves(reference_paths: list[str]) -> list[str]:
    """Inspect deterministic fixture paths; this does not observe model reads."""
    return [
        path for path in reference_paths
        if path.startswith("references/genre-playbook-") and path != PROCUREMENT_OVERLAY
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
            "采购审查": "references/genre-playbook-review-opinion.md",
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
                self.assertEqual(primary_leaves(refs), [leaf])
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
                self.assertEqual(refs, ["SKILL.md", leaf] + COMMON_WRITING_PATHS)
            with self.subTest(genre=genre, mode="review"):
                refs = provider._reference_paths_for_genres([genre], [f"帮我审核这份{genre}。"])
                self.assertEqual(refs, ["SKILL.md", leaf, "references/review-checklist.md"] + COMMON_WRITING_PATHS)

    def test_reply_opinion_explanation_are_independent_from_generic_checklist(self) -> None:
        for genre, leaf in {
            "批复": "references/genre-playbook-reply.md",
            "意见": "references/genre-playbook-opinion.md",
            "说明": "references/genre-playbook-explanation.md",
        }.items():
            with self.subTest(genre=genre):
                refs = provider._reference_paths_for_genres([genre], [f"起草{genre}"])
                self.assertEqual(refs, ["SKILL.md", leaf] + COMMON_WRITING_PATHS)
                self.assertNotIn("references/genre-checklist.md", refs)

    def test_unknown_genre_uses_router_and_minimal_checklist(self) -> None:
        refs = provider._reference_paths_for_genres(["未知材料"])
        self.assertEqual(
            refs,
            ["SKILL.md", "references/genre-routing.md", "references/genre-checklist.md"] + COMMON_WRITING_PATHS,
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
            ["SKILL.md", "references/genre-playbook-feasibility.md", "references/ai-compute-docs.md"] + COMMON_WRITING_PATHS,
        )

    def test_non_ai_cloud_task_does_not_load_compute_overlay(self) -> None:
        refs = provider._reference_paths_for_genres(
            ["说明"], ["普通政务网站部署在云端，需要说明 SLA 和并发，不涉及 AI、模型或 GPU。"]
        )
        self.assertNotIn("references/ai-compute-docs.md", refs)

    def test_reorganized_genres_keep_their_primary_across_draft_review_and_rewrite(self) -> None:
        expected = {
            "审查意见": "review-opinion",
            "评审材料": "review-opinion",
            "责任书": "responsibility-letter",
            "倡议书": "initiative",
            "公开信": "open-letter",
            "讲解稿": "narration",
            "宣传手册": "information-materials",
            "宣传材料": "information-materials",
            "情况综合": "report",
            "建议信": "advisory-feedback",
        }
        for genre, suffix in expected.items():
            for task in [f"按材料起草{genre}。", f"帮我审核这份{genre}。", f"请按原事实和状态改写这份{genre}。"]:
                with self.subTest(genre=genre, task=task):
                    refs = provider._reference_paths_for_genres([genre], [task])
                    self.assertEqual(primary_leaves(refs), [f"references/genre-playbook-{suffix}.md"])
                    self.assertEqual(refs[-len(COMMON_WRITING_PATHS):], COMMON_WRITING_PATHS)
                    self.assertNotIn(PROCUREMENT_OVERLAY, refs)
                    self.assertNotIn("references/genre-checklist.md", refs)
                    self.assertNotIn("references/ai-compute-docs.md", refs)
                    if "审核" in task:
                        self.assertIn("references/review-checklist.md", refs)
                    else:
                        self.assertIn("references/writing-rules.md", refs)

    def test_procurement_subject_keeps_deliverable_primary_and_conditional_overlay(self) -> None:
        cases = [
            ("采购方案", "起草采购方案，说明预算和采购安排。", "plan-construction", False, False),
            ("采购审查", "审核采购方案，只给问题和修改建议。", "plan-construction", True, False),
            ("采购方案", "审核采购方案，并核对规格报价和履约条件。", "plan-construction", True, True),
            ("采购方案", "根据采购评审记录起草审查意见，保留未形成结论的状态。", "review-opinion", False, True),
            ("审查意见", "依据初步设计评审记录起草审查意见。", "review-opinion", False, False),
            ("采购审查", "根据原材料改写采购审查正文。", "review-opinion", False, True),
        ]
        for genre, task, suffix, review, procurement in cases:
            with self.subTest(genre=genre, task=task):
                refs = provider._reference_paths_for_genres([genre], [task])
                self.assertEqual(primary_leaves(refs), [f"references/genre-playbook-{suffix}.md"])
                self.assertEqual("references/review-checklist.md" in refs, review)
                self.assertEqual(PROCUREMENT_OVERLAY in refs, procurement)
                self.assertEqual(refs[-len(COMMON_WRITING_PATHS):], COMMON_WRITING_PATHS)

    def test_technical_requirements_use_a_shared_primary_and_scene_only_compute_overlay(self) -> None:
        cases = [
            ("技术需求", "起草普通服务器技术需求，写明接口、安全、SLA和验收。", False),
            ("服务器技术需求", "帮我审核这份普通服务器技术需求，不涉及 AI、模型或 GPU。", False),
            ("软件需求说明", "按材料改写软件需求说明，保留待定接口和验收条件。", False),
            ("接口需求", "起草接口需求，说明输入输出及权限。", False),
            ("技术需求", "起草 AI 模型推理服务技术需求，写明资源及验收要求。", True),
            ("GPU/服务器租赁技术需求", "帮我审核这份模型推理服务技术需求。", True),
        ]
        for genre, task, compute in cases:
            with self.subTest(genre=genre, task=task):
                refs = provider._reference_paths_for_genres([genre], [task])
                self.assertEqual(primary_leaves(refs), ["references/genre-playbook-technical-requirements.md"])
                self.assertEqual("references/ai-compute-docs.md" in refs, compute)
                self.assertNotIn(PROCUREMENT_OVERLAY, refs)
                self.assertNotIn("references/genre-checklist.md", refs)
                self.assertEqual(refs[-len(COMMON_WRITING_PATHS):], COMMON_WRITING_PATHS)
        plan = provider._reference_paths_for_genres(["建设方案"], ["起草建设方案，其中包含技术需求和接口内容。"])
        self.assertEqual(primary_leaves(plan), ["references/genre-playbook-plan-construction.md"])

    def test_situation_explanation_title_follows_the_stated_use(self) -> None:
        for task, suffix in [
            ("起草情况说明，解释具体事实并回应疑问。", "explanation"),
            ("起草情况说明，汇报当前工作进展和问题处置。", "report"),
        ]:
            with self.subTest(task=task):
                refs = provider._reference_paths_for_genres(["情况说明"], [task])
                self.assertEqual(primary_leaves(refs), [f"references/genre-playbook-{suffix}.md"])

    def test_speech_person_order_is_a_conditional_overlay(self) -> None:
        base = provider._reference_paths_for_genres(["讲话稿"])
        ordered = provider._reference_paths_for_genres(
            ["讲话稿"], ["写讲话稿，开场按职务排序。"]
        )
        host_base = provider._reference_paths_for_genres(["主持词"])
        host_ordered = provider._reference_paths_for_genres(
            ["主持词"], ["写主持词，开场按职务排序。"]
        )
        duty_ordered = provider._reference_paths_for_genres(
            ["述职报告"], ["写述职报告，开场按职务排序。"]
        )
        self.assertNotIn("references/speech-person-order.md", base)
        self.assertIn("references/speech-person-order.md", ordered)
        self.assertIn("references/genre-playbook-speech-address.md", ordered)
        self.assertNotIn("references/speech-person-order.md", host_base)
        self.assertIn("references/speech-person-order.md", host_ordered)
        self.assertIn("references/genre-playbook-meeting-host.md", host_ordered)
        self.assertNotIn("references/speech-person-order.md", duty_ordered)

    def test_host_and_duty_genres_keep_one_primary_across_modes(self) -> None:
        expected = {
            "会议主持词": "references/genre-playbook-meeting-host.md",
            "主持词": "references/genre-playbook-meeting-host.md",
            "主持串词": "references/genre-playbook-meeting-host.md",
            "书面述职": "references/genre-playbook-duty-report.md",
            "述职报告": "references/genre-playbook-duty-report.md",
            "履职情况报告": "references/genre-playbook-duty-report.md",
            "现场述职发言": "references/genre-playbook-duty-report.md",
        }
        for genre, leaf in expected.items():
            for mode, task in {
                "draft": f"请按材料起草这份{genre}。",
                "review": f"帮我审核这份{genre}。",
                "rewrite": f"帮我审核这份{genre}，并重写全文。",
            }.items():
                with self.subTest(genre=genre, mode=mode):
                    refs = provider._reference_paths_for_genres([genre], [task])
                    primary = [
                        path
                        for path in refs
                        if path.startswith("references/genre-playbook-")
                    ]
                    self.assertEqual(primary, [leaf])

    def test_summary_priorities_and_periodic_reports_keep_one_primary_across_modes(self) -> None:
        expected = {
            "工作要点": "references/genre-playbook-work-priorities.md",
            "工作总结": "references/genre-playbook-work-summary.md",
            "周报": "references/genre-playbook-report.md",
            "月报": "references/genre-playbook-report.md",
        }
        for genre, leaf in expected.items():
            for mode, task in {
                "draft": f"请按材料起草这份{genre}。",
                "review": f"帮我审核这份{genre}。",
                "rewrite": f"帮我审核这份{genre}，并重写全文。",
            }.items():
                with self.subTest(genre=genre, mode=mode):
                    refs = provider._reference_paths_for_genres([genre], [task])
                    primary = [
                        path
                        for path in refs
                        if path.startswith("references/genre-playbook-")
                    ]
                    self.assertEqual(primary, [leaf])

    def test_periodic_report_field_editing_is_conditional(self) -> None:
        plain = provider._reference_paths_for_genres(
            ["周报"], ["请按材料起草本周周报。"]
        )
        weekly_fields = provider._reference_paths_for_genres(
            ["周报"], ["请起草字段式周报，保留字段名、字段顺序和字段换行。"]
        )
        monthly_fields = provider._reference_paths_for_genres(
            ["月报"], ["请审核这份月报，按字段处理并保留字段名。"]
        )
        summary_fields = provider._reference_paths_for_genres(
            ["工作总结"], ["请按字段整理工作总结。"]
        )
        plain_summary = provider._reference_paths_for_genres(
            ["工作总结"], ["请按材料整理工作总结。"]
        )
        self.assertNotIn("references/field-editing.md", plain)
        self.assertIn("references/field-editing.md", weekly_fields)
        self.assertIn("references/field-editing.md", monthly_fields)
        # SKILL.md routes explicit field actions regardless of the genre;
        # the report leaf's conditional reminder is not an exclusive scope.
        self.assertIn("references/field-editing.md", summary_fields)
        self.assertNotIn("references/field-editing.md", plain_summary)
        for refs in (summary_fields, plain_summary):
            self.assertEqual(primary_leaves(refs), ["references/genre-playbook-work-summary.md"])
        for refs in (plain, weekly_fields, monthly_fields):
            self.assertIn("references/genre-playbook-report.md", refs)
            self.assertNotIn("references/genre-playbook-work-summary.md", refs)
            self.assertNotIn("references/genre-playbook-work-priorities.md", refs)

    def test_complex_work_uses_composable_common_pages_without_retired_workflow(self) -> None:
        complex_refs = provider._reference_paths_for_genres(
            ["报告"], ["请把多材料合稿整理成一份800字完整报告。"]
        )
        self.assertEqual(
            complex_refs,
            [
                "SKILL.md",
                "references/genre-playbook-report.md",
                "references/argument-chains.md",
                *COMMON_WRITING_PATHS,
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
                "references/genre-playbook-report.md",
                *COMMON_WRITING_PATHS,
            ],
        )
        minutes = provider._reference_paths_for_genres(
            ["会议纪要"], ["材料只有建议，未形成决定，请写简短会议纪要。"]
        )
        self.assertEqual(minutes, ["SKILL.md", "references/genre-playbook-minutes.md"] + COMMON_WRITING_PATHS)

    def test_short_route_is_a_mode_overlay_on_the_primary_genre(self) -> None:
        short_application = provider._reference_paths_for_genres(
            ["申请"], ["请起草一份简短申请，只按已给字段，不新增事实。"]
        )
        self.assertEqual(
            short_application,
            [
                "SKILL.md",
                "references/genre-playbook-request.md",
                *COMMON_WRITING_PATHS,
            ],
        )
        long_application = provider._reference_paths_for_genres(
            ["申请"], ["请起草一份完整申请，说明用途、金额和实施安排。"]
        )
        self.assertNotIn("references/task-route-cards.md", long_application)
        self.assertIn("references/genre-playbook-request.md", long_application)
        # Short-form handling now belongs to the request leaf and the common
        # writing page; it must not replace or add a second primary genre.
        self.assertEqual(long_application, short_application)

    def test_natural_review_requests_keep_one_primary_and_full_review(self) -> None:
        cases = [
            ("通知", "帮我审核一下这份通知。", "references/genre-playbook-notice.md"),
            ("会议纪要", "帮我复核这份会议纪要。", "references/genre-playbook-minutes.md"),
            ("报告", "请审校这份报告的事实和状态。", "references/genre-playbook-report.md"),
            ("采购审查", "帮我把关这份采购审查稿件。", "references/genre-playbook-review-opinion.md"),
        ]
        for genre, task, leaf in cases:
            with self.subTest(genre=genre, task=task):
                refs = provider._reference_paths_for_genres([genre], [task])
                overlay = [PROCUREMENT_OVERLAY] if genre == "采购审查" else []
                self.assertEqual(refs, ["SKILL.md", leaf] + overlay + ["references/review-checklist.md"] + COMMON_WRITING_PATHS)

    def test_explicit_review_scope_keeps_common_review_stages(self) -> None:
        refs = provider._reference_paths_for_genres(
            ["通知"], ["只审不改，检查这份通知的格式和语气。"]
        )
        self.assertEqual(
            refs,
            ["SKILL.md", "references/genre-playbook-notice.md", "references/review-checklist.md"] + COMMON_WRITING_PATHS,
        )

    def test_review_and_rewrite_keep_the_same_primary_scene(self) -> None:
        review = provider._reference_paths_for_genres(
            ["采购审查"], ["只审不改，检查这份采购审查的字段和结论状态。"]
        )
        rewrite = provider._reference_paths_for_genres(
            ["采购审查"], ["根据材料改写采购审查正文。"]
        )
        leaf = "references/genre-playbook-review-opinion.md"
        self.assertEqual(primary_leaves(review), [leaf])
        self.assertEqual(primary_leaves(rewrite), [leaf])
        self.assertIn(PROCUREMENT_OVERLAY, review)
        self.assertIn(PROCUREMENT_OVERLAY, rewrite)
        self.assertNotIn("references/genre-playbook-notice.md", review)

    def test_all_deliveries_keep_mandatory_review_and_delivery_stages(self) -> None:
        for task in ["请起草一份意见。", "请起草一份意见，只输出完整正文。"]:
            with self.subTest(task=task):
                self.assertEqual(
                    provider._reference_paths_for_genres(["意见"], [task]),
                    ["SKILL.md", "references/genre-playbook-opinion.md"] + COMMON_WRITING_PATHS,
                )
        for relative in COMMON_WRITING_PATHS:
            self.assertTrue((ROOT / "chinese-official-writing" / relative).is_file(), relative)

    def test_natural_delivery_phrasing_uses_the_same_final_delivery_page(self) -> None:
        for task in ["帮我写完整稿子。", "帮我写完整稿子，不需要解释。"]:
            with self.subTest(task=task):
                refs = provider._reference_paths_for_genres(["报告"], [task])
                self.assertEqual(refs[-len(COMMON_WRITING_PATHS):], COMMON_WRITING_PATHS)
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
                self.assertEqual(refs[-len(COMMON_WRITING_PATHS):], COMMON_WRITING_PATHS)
                self.assertNotIn("references/compression-details.md", refs)
                self.assertEqual(len(refs), len(set(refs)))
        # Ordinary limits use writing-rules step 2. Compression and complex
        # counting still add the dedicated page before the common final flow.
        for genre, task in [
            ("报告", "请将报告压缩到800字。"),
            ("新闻消息", "请核对新闻消息的计数口径。"),
            ("通知", "审核这份通知并处理超限。"),
        ]:
            with self.subTest(genre=genre, task=task):
                refs = provider._reference_paths_for_genres([genre], [task])
                suffix = ["references/compression-details.md"] + COMMON_WRITING_PATHS
                self.assertEqual(refs[-len(suffix):], suffix)
                self.assertEqual(len(refs), len(set(refs)))

    def test_transaction_names_keep_a_primary_leaf(self) -> None:
        meeting_notice = provider._reference_paths_for_genres(["通知"], ["起草会议通知"])
        procurement_application = provider._reference_paths_for_genres(
            ["申请"], ["起草采购申请，列明品名、数量和预算"]
        )
        self.assertEqual(meeting_notice, ["SKILL.md", "references/genre-playbook-notice.md"] + COMMON_WRITING_PATHS)
        self.assertIn("references/genre-playbook-request.md", procurement_application)
        self.assertNotIn("references/compatibility-scene-routing.md", procurement_application)

    def test_report_transaction_overlays_keep_report_as_primary(self) -> None:
        remediation = provider._reference_paths_for_genres(
            ["报告"], ["起草整改进展报告，只输出正文。"]
        )
        feedback = provider._reference_paths_for_genres(
            ["反馈报告"], ["起草反馈情况报告，只输出正文。"]
        )
        self.assertEqual(primary_leaves(remediation), ["references/genre-playbook-report.md"])
        self.assertIn("references/transaction-remediation-report.md", remediation)
        self.assertLess(remediation.index("references/genre-playbook-report.md"), remediation.index("references/transaction-remediation-report.md"))
        self.assertEqual(primary_leaves(feedback), ["references/genre-playbook-report.md"])
        self.assertIn("references/transaction-feedback-report.md", feedback)
        self.assertLess(feedback.index("references/genre-playbook-report.md"), feedback.index("references/transaction-feedback-report.md"))
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
