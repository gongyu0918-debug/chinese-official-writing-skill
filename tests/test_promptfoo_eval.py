from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


grader = load_module(
    "official_promptfoo_grader_under_test",
    ROOT / "evals" / "official-writing" / "graders" / "official_writing_rubric.py",
)
run_eval = load_module(
    "official_promptfoo_runner_under_test",
    ROOT / "evals" / "official-writing" / "run_eval.py",
)
provider = load_module(
    "official_promptfoo_provider_under_test",
    ROOT / "evals" / "official-writing" / "providers" / "agent_writer.py",
)


class PromptfooDatasetTests(unittest.TestCase):
    def test_dataset_has_full_and_smoke_shape(self) -> None:
        lines = (ROOT / "evals" / "official-writing" / "datasets" / "cases.jsonl").read_text(encoding="utf-8").splitlines()
        cases = [json.loads(line) for line in lines if line.strip()]

        self.assertEqual(len(cases), 270)
        smoke = cases[:10]
        self.assertEqual({item["metadata"]["tier"] for item in smoke}, {"smoke"})
        self.assertEqual(
            [(item["vars"]["genre"], item["vars"]["scenario"]) for item in smoke],
            [
                ("通知", "报送材料"),
                ("通知", "专项启动"),
                ("请示", "报送材料"),
                ("请示", "专项启动"),
                ("报告", "报送材料"),
                ("报告", "专项启动"),
                ("说明", "报送材料"),
                ("说明", "专项启动"),
                ("方案", "报送材料"),
                ("方案", "专项启动"),
            ],
        )


class PromptfooGraderTests(unittest.TestCase):
    def test_ablation_assertion_does_not_fail_nonempty_baseline_quality(self) -> None:
        weak_request = "围绕专项启动事项，相关工作要全面赋能、不断提升，形成一批成果。各单位要高度重视，加强统筹协调。"

        scored = grader.score_text(weak_request, {"case_id": "C004", "genre": "请示"})
        asserted = grader.assert_official_writing(weak_request, {"vars": {"case_id": "C004", "genre": "请示"}})

        self.assertFalse(scored["pass"])
        self.assertIn("request_missing_approval_language", scored["hard_rule_failures"])
        self.assertTrue(asserted["pass"])

    def test_report_with_approval_request_is_a_hard_rule_failure(self) -> None:
        report = "现将专项启动情况报告如下：已完成材料核验、责任分工和阶段安排。为便于后续推进，申请批准该事项并请予批复。"

        result = grader.score_text(report, {"case_id": "C006", "genre": "报告"})

        self.assertIn("report_contains_approval_request", result["hard_rule_failures"])


class PromptfooRunnerTests(unittest.TestCase):
    def tearDown(self) -> None:
        for name in run_eval.THRESHOLD_ENV_VARS.values():
            os.environ.pop(name, None)

    def test_randomized_pair_maps_display_labels_back_to_modes(self) -> None:
        case = {"vars": {"case_id": "C001", "genre": "通知", "scenario": "报送材料", "task": "任务"}}
        pair = {"baseline": {"text": "baseline"}, "skill": {"text": "skill"}}

        first = run_eval.randomized_pair(case, pair, 0)
        second = run_eval.randomized_pair(case, pair, 1)

        self.assertEqual(set(first["label_map"].values()), {"baseline", "skill"})
        self.assertEqual(first["label_map"]["A"], second["label_map"]["B"])
        self.assertEqual(first["label_map"]["B"], second["label_map"]["A"])

    def valid_summary(self) -> dict:
        return {
            "suite": "full",
            "pairwise": {
                "counts": {"invalid": 0, "needs_manual_review": 0},
                "needs_manual_review_rate": 0.0,
                "skill_win_rate": 0.9,
                "tie_rate": 0.1,
            },
            "deterministic": {
                "missing_output_cases": [],
                "by_mode": {
                    "baseline": {"avg_lint_risk_weight": 2.0},
                    "skill": {
                        "hard_rule_pass_rate": 1.0,
                        "placeholder_risk_rate": 0.0,
                        "avg_lint_risk_weight": 1.0,
                    },
                },
            },
        }

    def test_release_policy_fails_current_skill_hard_rule_regression(self) -> None:
        summary = self.valid_summary()
        summary["deterministic"]["by_mode"]["skill"]["hard_rule_pass_rate"] = 0.97

        with self.assertRaises(run_eval.EvalError):
            run_eval.enforce_failure_policy(summary)

    def test_release_policy_fails_placeholder_risk(self) -> None:
        summary = self.valid_summary()
        summary["deterministic"]["by_mode"]["skill"]["placeholder_risk_rate"] = 0.01

        with self.assertRaises(run_eval.EvalError):
            run_eval.enforce_failure_policy(summary)

    def test_release_policy_fails_pairwise_loss_regression(self) -> None:
        summary = self.valid_summary()
        summary["pairwise"]["skill_win_rate"] = 0.5
        summary["pairwise"]["tie_rate"] = 0.2

        with self.assertRaises(run_eval.EvalError):
            run_eval.enforce_failure_policy(summary)

    def test_release_policy_thresholds_can_be_overridden_for_real_model_probe(self) -> None:
        summary = self.valid_summary()
        summary["deterministic"]["by_mode"]["skill"]["hard_rule_pass_rate"] = 0.95
        summary["deterministic"]["by_mode"]["skill"]["placeholder_risk_rate"] = 0.02
        summary["pairwise"]["skill_win_rate"] = 0.6
        summary["pairwise"]["tie_rate"] = 0.2

        os.environ["OFFICIAL_WRITING_SKILL_HARD_RULE_PASS_RATE_MIN"] = "0.90"
        os.environ["OFFICIAL_WRITING_SKILL_PLACEHOLDER_RISK_RATE_MAX"] = "0.05"
        os.environ["OFFICIAL_WRITING_SKILL_WIN_OR_TIE_RATE_MIN"] = "0.75"

        run_eval.enforce_failure_policy(summary)

    def test_invalid_threshold_override_fails_cleanly(self) -> None:
        summary = self.valid_summary()
        os.environ["OFFICIAL_WRITING_SKILL_WIN_OR_TIE_RATE_MIN"] = "not-a-float"

        with self.assertRaisesRegex(run_eval.EvalError, "must be a float"):
            run_eval.enforce_failure_policy(summary)


class PromptfooProviderTests(unittest.TestCase):
    def test_ai_compute_genre_loads_only_relevant_extra_reference(self) -> None:
        refs = provider._reference_paths_for_genres(["算力资源采购方案"])

        self.assertEqual(refs[0], "SKILL.md")
        self.assertIn("references/genre-playbooks.md", refs)
        self.assertIn("references/ai-compute-docs.md", refs)
        self.assertNotIn("references/task-route-cards.md", refs)
        self.assertNotIn("references/genre-checklist.md", refs)
        self.assertNotIn("references/anti-ai-patterns.md", refs)
        self.assertNotIn("references/format-gbt9704.md", refs)

    def test_known_genres_use_playbook_without_preloading_other_routes(self) -> None:
        refs = provider._reference_paths_for_genres(["通知", "函", "复函", "征求意见函", "采购公告", "公示", "会议纪要"])

        self.assertIn("references/genre-playbooks.md", refs)
        self.assertNotIn("references/argument-chains.md", refs)
        self.assertNotIn("references/task-route-cards.md", refs)

    def test_each_supported_legal_genre_can_reach_the_playbook(self) -> None:
        genres = ["通知", "请示", "报告", "函", "复函", "公告", "通告", "通报", "决定", "决议", "议案", "公报", "命令（令）"]
        for genre in genres:
            with self.subTest(genre=genre):
                refs = provider._reference_paths_for_genres([genre])
                self.assertIn("references/genre-playbooks.md", refs)

    def test_task_text_can_upgrade_complex_and_format_routes(self) -> None:
        complex_refs = provider._reference_paths_for_genres(
            ["报告"],
            ["把多材料合稿整理成一份1200字完整报告。"],
        )
        format_refs = provider._reference_paths_for_genres(
            ["通知"],
            ["按 GB/T 9704 排成 Word 正式文件。"],
        )

        self.assertIn("references/workflow.md", complex_refs)
        self.assertIn("references/handling-elements.md", complex_refs)
        self.assertIn("references/argument-chains.md", complex_refs)
        self.assertNotIn("references/task-route-cards.md", complex_refs)
        self.assertIn("references/format-gbt9704.md", format_refs)

    def test_external_research_leaf_is_loaded_only_for_explicit_research_tasks(self) -> None:
        ordinary_refs = provider._reference_paths_for_genres(
            ["报告"],
            ["根据给定材料起草一份1200字完整报告。"],
        )
        research_refs = provider._reference_paths_for_genres(
            ["通知"],
            ["核验现行政策和公开来源后起草通知。"],
        )

        self.assertNotIn("references/external-research.md", ordinary_refs)
        self.assertIn("references/external-research.md", research_refs)

    def test_complex_unknown_genre_keeps_an_explicit_argument_route(self) -> None:
        refs = provider._reference_paths_for_genres(
            ["通用材料"],
            ["写1000字可行性论证。"],
        )

        self.assertIn("references/workflow.md", refs)
        self.assertIn("references/handling-elements.md", refs)
        self.assertIn("references/argument-chains.md", refs)

    def test_plain_unknown_genre_does_not_load_playbook(self) -> None:
        refs = provider._reference_paths_for_genres(["通用材料"])

        self.assertEqual(refs, ["SKILL.md", "references/task-route-cards.md"])

    def test_common_known_genres_stop_at_the_playbook(self) -> None:
        refs = provider._reference_paths_for_genres(["通知", "请示", "报告", "说明", "方案"])

        self.assertEqual(refs, ["SKILL.md", "references/genre-playbooks.md"])
        self.assertNotIn("references/genre-routing.md", refs)
        self.assertNotIn("references/handling-elements.md", refs)
        self.assertNotIn("references/genre-checklist.md", refs)
        self.assertNotIn("references/formal-addressing.md", refs)
        self.assertNotIn("references/anti-ai-patterns.md", refs)

    def test_unresolved_minutes_stop_at_the_sparse_card(self) -> None:
        refs = provider._reference_paths_for_genres(
            ["会议纪要"],
            ["材料只有议题和建议，未形成决定、责任分工或期限，请写简短会议纪要。"],
        )

        self.assertEqual(
            refs,
            ["SKILL.md", "references/task-route-cards.md"],
        )

    def test_complete_minutes_upgrade_to_the_playbook(self) -> None:
        refs = provider._reference_paths_for_genres(
            ["会议纪要"],
            ["写一份完整会议纪要，已形成三项议定事项、责任单位和完成期限。"],
        )

        self.assertEqual(refs, ["SKILL.md", "references/genre-playbooks.md"])

    def test_short_but_complete_minutes_still_include_the_playbook(self) -> None:
        refs = provider._reference_paths_for_genres(
            ["会议纪要"],
            ["请写一份简短但完整的会议纪要，已形成三项决定、责任单位和期限。"],
        )

        self.assertEqual(refs, ["SKILL.md", "references/genre-playbooks.md"])

    def test_unresolved_minutes_wording_does_not_force_the_playbook(self) -> None:
        tasks = (
            "议定事项尚未形成，责任单位待明确，完成期限待评估，请写简短会议纪要。",
            "无议定事项，责任单位和完成期限均未明确，请写简短会议纪要。",
            "不要写会议决定，只记录建议，请写简短会议纪要。",
            "已形成初步建议，仍待评估，请写简短会议纪要。",
            "目前只有建议，事项待评估，请写会议纪要。",
            "会议明确提出建议，待进一步评估，请写简短会议纪要。",
            "会议明确尚未形成决定，责任单位待研究，请写简短会议纪要。",
            "会议确定下次再议，请写简短会议纪要。",
            "会议明确该事项待评估，请写简短会议纪要。",
            "不需要完整会议纪要，只记录建议和待议事项。",
            "不是完整会议纪要，只记录建议和待议事项。",
        )

        for task in tasks:
            with self.subTest(task=task):
                refs = provider._reference_paths_for_genres(["会议纪要"], [task])
                self.assertEqual(refs, ["SKILL.md", "references/task-route-cards.md"])

    def test_resolved_or_formal_minutes_upgrade_to_the_playbook(self) -> None:
        tasks = (
            "请写简短但完整正式会议纪要。",
            "请写简短会议纪要，会议已决定先行试点。",
            "请写简短会议纪要，会议已明确责任单位为信息中心。",
            "请写简短会议纪要，完成期限为7月20日。",
            "请写简短会议纪要，会议形成决定如下。",
            "请写简短会议纪要，会议通过了三项议定事项。",
            "请写简短会议纪要，会议无异议通过该事项。",
            "请写简短会议纪要，责任单位已明确。",
            "请写简短会议纪要，完成期限已明确。",
            "请写简短会议纪要，责任分工如下。",
            "请写简短会议纪要，会上形成了决定：先行试点。",
            "请写简短会议纪要，经研究决定先行试点。",
            "请写简短会议纪要，明确由信息中心负责，7月20日前完成。",
            "请写简短会议纪要，议定由信息中心牵头，7月20日前完成。",
            "请按完整、正式的会议纪要起草，篇幅简短。",
            "请写一份简短会议纪要。",
            "材料未说明是否形成决定，请写简短会议纪要。",
            "原记录未提供责任单位和期限，请写简短会议纪要。",
            "请写简短会议纪要，虽未形成决定但已明确责任单位为信息中心。",
            "请写简短会议纪要，虽未形成决定，但明确由信息中心负责。",
            "请写简短会议纪要，建议继续研究但责任单位为信息中心。",
            "请写简短会议纪要，会议建议先行试点，并决定由信息中心负责。",
            "不是未决事项而是要求完整正式会议纪要。",
            "不要理解为未形成决定，请按完整正式会议纪要写。",
            "无需按未决轻卡处理，应起草完整正式会议纪要。",
            "会议形成一致意见，责任分工待明确，请写简短会议纪要。",
            "会议已形成结论，但完成期限待定，请写简短会议纪要。",
            "会议已达成共识，责任单位待明确，请写简短会议纪要。",
        )

        for task in tasks:
            with self.subTest(task=task):
                refs = provider._reference_paths_for_genres(["会议纪要"], [task])
                self.assertEqual(refs, ["SKILL.md", "references/genre-playbooks.md"])

    def test_review_only_task_loads_the_review_leaf(self) -> None:
        refs = provider._reference_paths_for_genres(
            ["通知"],
            ["只审不改，检查这份通知的格式、语气和办理要素。"],
        )

        self.assertEqual(refs, ["SKILL.md", "references/review-checklist.md"])

    def test_review_then_rewrite_is_not_classified_as_review_only(self) -> None:
        for task in (
            "请先检查这份通知，再按建议重写全文。",
            "请检查这份通知并修改全文。",
            "审一下这份通知，直接改写成正式稿。",
            "请审一下这份报告并帮我改写全文。",
            "检查这份通知后帮我重写一版。",
            "复核这份材料，再帮我改一版。",
        ):
            with self.subTest(task=task):
                refs = provider._reference_paths_for_genres(["通知"], [task])
                self.assertIn("references/genre-playbooks.md", refs)
                self.assertNotEqual(refs, ["SKILL.md", "references/review-checklist.md"])

    def test_review_only_language_does_not_treat_modification_advice_as_rewrite(self) -> None:
        for task in (
            "只审格式，不重写全文，只给修改建议。",
            "只检查这份改写稿是否保真，不改写，不输出修改稿。",
        ):
            with self.subTest(task=task):
                refs = provider._reference_paths_for_genres(["通知"], [task])
                self.assertEqual(refs, ["SKILL.md", "references/review-checklist.md"])

    def test_anti_ai_review_adds_only_the_language_leaf(self) -> None:
        refs = provider._reference_paths_for_genres(
            ["报告"],
            ["只审 AI 味，不重写全文，检查这份报告是否模板化。"],
        )

        self.assertEqual(
            refs,
            ["SKILL.md", "references/review-checklist.md", "references/anti-ai-patterns.md"],
        )

    def test_style_task_loads_the_official_style_leaf(self) -> None:
        refs = provider._reference_paths_for_genres(
            ["报告"],
            ["请把这份报告去口语化，只统一语气，不改变事实。"],
        )

        self.assertEqual(
            refs,
            ["SKILL.md", "references/genre-playbooks.md", "references/official-style.md"],
        )

    def test_non_ai_server_rental_does_not_load_ai_compute_reference(self) -> None:
        refs = provider._reference_paths_for_genres(
            ["申请"],
            ["租用普通档案备份服务器，不涉及 AI、模型、GPU 或推理。"],
        )

        self.assertIn("references/genre-playbooks.md", refs)
        self.assertNotIn("references/ai-compute-docs.md", refs)

    def test_ai_route_keeps_positive_requirements_after_a_negated_clause(self) -> None:
        for task in (
            "本项目不涉及数据库迁移，但需要 GPU 模型推理服务。",
            "本项目不涉及数据库迁移，而是需要 GPU 模型推理服务。",
            "本项目不涉及数据库迁移，却需要 GPU 模型推理服务。",
            "本项目不涉及数据库迁移，仍需 GPU 模型推理服务。",
        ):
            with self.subTest(task=task):
                refs = provider._reference_paths_for_genres(["方案"], [task])
                self.assertIn("references/ai-compute-docs.md", refs)

    def test_cloud_local_cost_comparison_loads_the_ai_compute_leaf(self) -> None:
        refs = provider._reference_paths_for_genres(
            ["说明"],
            ["比较云端与本地部署成本，并说明 SLA 和峰值并发。"],
        )

        self.assertIn("references/ai-compute-docs.md", refs)

    def test_generic_cloud_service_with_explicit_non_ai_boundary_stays_out(self) -> None:
        refs = provider._reference_paths_for_genres(
            ["说明"],
            ["普通政务网站部署在云端，需要说明 SLA 和并发，不涉及 AI、模型或 GPU。"],
        )

        self.assertNotIn("references/ai-compute-docs.md", refs)

    def test_case_reference_paths_keep_sparse_full_and_review_routes_distinct(self) -> None:
        sparse = {
            "vars": {
                "genre": "会议纪要",
                "task": "材料只有建议，未形成决定、责任分工或期限，请写简短会议纪要。",
            }
        }
        complete = {
            "vars": {
                "genre": "会议纪要",
                "task": "写一份完整会议纪要，已形成议定事项、责任单位和完成期限。",
            }
        }
        review = {
            "vars": {
                "genre": "会议纪要",
                "task": "只审不改，检查这份会议纪要的格式和语气。",
            }
        }

        self.assertEqual(
            provider._case_reference_paths(sparse),
            ["SKILL.md", "references/task-route-cards.md"],
        )
        self.assertEqual(
            provider._case_reference_paths(complete),
            ["SKILL.md", "references/genre-playbooks.md"],
        )
        self.assertEqual(
            provider._case_reference_paths(review),
            ["SKILL.md", "references/review-checklist.md"],
        )

    def test_skill_batches_never_mix_reference_signatures(self) -> None:
        cases = [
            {
                "vars": {
                    "case_id": "R001",
                    "genre": "会议纪要",
                    "task": "材料只有建议，未形成决定、责任分工或期限，请写简短会议纪要。",
                }
            },
            {
                "vars": {
                    "case_id": "R002",
                    "genre": "会议纪要",
                    "task": "写一份完整会议纪要，已形成议定事项、责任单位和完成期限。",
                }
            },
            {
                "vars": {
                    "case_id": "R003",
                    "genre": "会议纪要",
                    "task": "只审不改，检查这份会议纪要的格式和语气。",
                }
            },
        ]

        batches = provider._batch_cases("skill", cases, batch_size=10)

        self.assertEqual(len(batches), 3)
        for batch in batches:
            signatures = {tuple(provider._case_reference_paths(case)) for case in batch}
            self.assertEqual(len(signatures), 1)

    def test_review_prompt_does_not_force_drafting_or_argument_steps(self) -> None:
        case = {
            "vars": {
                "case_id": "R001",
                "genre": "通知",
                "task": "只审不改，检查这份通知的格式、语气和办理要素。",
            }
        }
        config = {"basePath": str(ROOT / "evals" / "official-writing"), "repoRoot": str(ROOT)}

        prompt = provider._skill_prompt([case], config)

        self.assertIn("只审不改时不得重写全文", prompt)
        self.assertIn("references/review-checklist.md", prompt)
        self.assertNotIn("组织论证链条", prompt)
        self.assertNotIn("输出一段中文正式材料初稿", prompt)

    def test_skill_prompt_rejects_a_mixed_route_batch(self) -> None:
        review = {
            "vars": {
                "case_id": "R001",
                "genre": "通知",
                "task": "只审不改，检查这份通知的格式和语气。",
            }
        }
        draft = {
            "vars": {
                "case_id": "R002",
                "genre": "通知",
                "task": "写一份完整通知。",
            }
        }
        config = {"basePath": str(ROOT / "evals" / "official-writing"), "repoRoot": str(ROOT)}

        with self.assertRaisesRegex(provider.ProviderError, "mixed reference routes"):
            provider._skill_prompt([review, draft], config)

    def test_skill_context_is_complete_and_within_eval_budget(self) -> None:
        context = provider._load_skill_context(ROOT, ["通知", "请示", "报告", "说明", "方案"])
        canonical = (ROOT / "chinese-official-writing" / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn(canonical, context)
        for relative in provider._reference_paths_for_genres(["通知", "请示", "报告", "说明", "方案"]):
            selected = provider._skill_root(ROOT) / relative
            self.assertIn(selected.read_text(encoding="utf-8"), context)
        self.assertNotIn("[truncated]", context)
        self.assertLessEqual(len(context), provider.MAX_SKILL_CONTEXT_CHARS)

    def test_missing_selected_reference_fails_instead_of_skipping(self) -> None:
        with mock.patch.object(
            provider,
            "_reference_paths_for_genres",
            return_value=["SKILL.md", "references/missing-route.md"],
        ):
            with self.assertRaisesRegex(provider.ProviderError, "selected skill reference does not exist"):
                provider._load_skill_context(ROOT, ["通用材料"])

    def test_context_budget_failure_is_explicit_instead_of_truncating(self) -> None:
        with mock.patch.object(provider, "MAX_SKILL_CONTEXT_CHARS", 10):
            with self.assertRaisesRegex(provider.ProviderError, "selected skill context exceeds 10 characters"):
                provider._load_skill_context(ROOT, ["通用材料"])

    def test_full_dataset_batches_stay_within_provider_safety_budget(self) -> None:
        config = {
            "basePath": str(ROOT / "evals" / "official-writing"),
            "datasetPath": "datasets/cases.jsonl",
        }
        cases = provider._load_cases(config)
        observed: list[int] = []
        for chunk in provider._batch_cases("skill", cases, batch_size=10):
            paths = provider._skill_batch_reference_paths(chunk)
            observed.append(len(provider._load_skill_context_from_paths(ROOT, paths)))
            self.assertEqual(
                {tuple(provider._case_reference_paths(case)) for case in chunk},
                {tuple(paths)},
            )

        self.assertEqual(len(observed), 27)
        self.assertLessEqual(max(observed), provider.MAX_SKILL_CONTEXT_CHARS)

    def test_skill_cache_key_hashes_every_case_route_leaf(self) -> None:
        cases = [
            {
                "vars": {
                    "case_id": "R001",
                    "genre": "通知",
                    "task": "只审不改，检查这份通知的格式和语气。",
                }
            },
            {
                "vars": {
                    "case_id": "R002",
                    "genre": "通知",
                    "task": "写一份完整通知。",
                }
            },
        ]
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            skill = root / "chinese-official-writing"
            references = skill / "references"
            references.mkdir(parents=True)
            (skill / "SKILL.md").write_text("entry", encoding="utf-8")
            (references / "review-checklist.md").write_text("review-v1", encoding="utf-8")
            (references / "genre-playbooks.md").write_text("playbook", encoding="utf-8")
            config = {"basePath": str(root), "repoRoot": str(root), "commandTemplate": "agent"}

            first = provider._cache_key("skill", cases, config)
            (references / "review-checklist.md").write_text("review-v2", encoding="utf-8")
            second = provider._cache_key("skill", cases, config)

        self.assertNotEqual(first, second)

    def test_cache_key_changes_with_command_and_batch_configuration(self) -> None:
        config = {
            "basePath": str(ROOT / "evals" / "official-writing"),
            "datasetPath": "datasets/cases.jsonl",
        }
        cases = provider._load_cases(config)
        key_a = provider._cache_key(
            "skill",
            cases,
            {**config, "batchSize": 10, "commandTemplate": "agent-A"},
        )
        key_b = provider._cache_key(
            "skill",
            cases,
            {**config, "batchSize": 20, "commandTemplate": "agent-B"},
        )

        self.assertNotEqual(key_a, key_b)

    def test_prebatch_execution_groups_cases_by_actual_route(self) -> None:
        cases = [
            {"vars": {"case_id": "R001", "genre": "通知", "task": "写一份完整通知。"}},
            {
                "vars": {
                    "case_id": "R002",
                    "genre": "通知",
                    "task": "只审不改，检查这份通知的格式和语气。",
                }
            },
            {
                "vars": {
                    "case_id": "R003",
                    "genre": "报告",
                    "task": "请把这份报告去口语化，只统一语气，不改变事实。",
                }
            },
        ]
        config = {
            "basePath": str(ROOT / "evals" / "official-writing"),
            "repoRoot": str(ROOT),
            "commandTemplate": "agent",
            "batchSize": 10,
        }

        provider._BATCH_CACHE.clear()
        with (
            mock.patch.object(provider, "_load_cases", return_value=cases),
            mock.patch.object(provider, "_load_cache", return_value=None),
            mock.patch.object(provider, "_write_cache"),
            mock.patch.object(
                provider,
                "_run_batch",
                side_effect=lambda _mode, chunk, _config: {
                    provider._case_id(case): "draft" for case in chunk
                },
            ) as run_batch,
        ):
            outputs = provider._ensure_batch_cache("skill", config)

        self.assertEqual(set(outputs), {"R001", "R002", "R003"})
        self.assertEqual(run_batch.call_count, 3)
        for call in run_batch.call_args_list:
            chunk = call.args[1]
            self.assertEqual(
                len({tuple(provider._case_reference_paths(case)) for case in chunk}),
                1,
            )
        provider._BATCH_CACHE.clear()

    def test_call_api_reports_the_route_used_for_the_case(self) -> None:
        case_vars = {
            "case_id": "R001",
            "genre": "通知",
            "task": "只审不改，检查这份通知的格式和语气。",
        }
        options = {"config": {"mode": "skill"}}
        context = {"vars": case_vars, "test": {"metadata": {}}}

        with mock.patch.object(provider, "_ensure_batch_cache", return_value={"R001": "审稿结果"}):
            result = provider.call_api("", options, context)

        self.assertEqual(
            result["metadata"]["selected_references"],
            ["SKILL.md", "references/review-checklist.md"],
        )

    def test_default_timeout_matches_cache_and_model_execution(self) -> None:
        case = {"vars": {"case_id": "C001", "genre": "通知", "scenario": "报送材料", "task": "任务"}}
        config = {
            "basePath": str(ROOT / "evals" / "official-writing"),
            "repoRoot": str(ROOT),
            "commandTemplate": "agent {prompt}",
        }

        default_key = provider._cache_key("baseline", [case], config)
        explicit_key = provider._cache_key(
            "baseline",
            [case],
            {**config, "timeoutSeconds": provider.DEFAULT_TIMEOUT_SECONDS},
        )
        with mock.patch.object(provider, "call_model_prompt", return_value=("正文", 0, 2)) as call:
            provider._run_single("baseline", case, config)

        self.assertEqual(default_key, explicit_key)
        self.assertEqual(call.call_args.args[2], provider.DEFAULT_TIMEOUT_SECONDS)

    def test_ai_compute_markers_cover_model_platform_language(self) -> None:
        for genre in ["模型服务技术需求", "智算中心建设方案", "大模型本地化部署成本说明", "AI平台推理服务", "GPU推理服务保障方案"]:
            with self.subTest(genre=genre):
                refs = provider._reference_paths_for_genres([genre])
                self.assertIn("references/genre-playbooks.md", refs)
                self.assertIn("references/ai-compute-docs.md", refs)

    def test_reply_letter_stub_satisfies_common_hard_rule(self) -> None:
        scenarios = [
            "报送材料",
            "专项启动",
            "阶段进展",
            "情况补充",
            "协同联调",
            "年度安排",
            "整改复核",
            "征求意见",
            "验收归档",
            "运行优化",
        ]
        for scenario in scenarios:
            with self.subTest(scenario=scenario):
                case = {"vars": {"case_id": "C071", "genre": "复函", "scenario": scenario}}
                draft = provider._stub_draft("skill", case)
                scored = grader.score_text(draft, case["vars"])

                self.assertTrue(scored["hard_rule_pass"])
                self.assertNotIn("reply_letter_missing_receipt_or_reply", scored["hard_rule_failures"])
                self.assertTrue(scored["required_elements"]["pass"])


if __name__ == "__main__":
    unittest.main()
