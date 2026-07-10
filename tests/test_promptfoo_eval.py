from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import sys
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
        self.assertIn("references/task-route-cards.md", refs)
        self.assertIn("references/genre-playbooks.md", refs)
        self.assertIn("references/ai-compute-docs.md", refs)
        self.assertIn("references/argument-chains.md", refs)
        self.assertNotIn("references/genre-checklist.md", refs)
        self.assertNotIn("references/anti-ai-patterns.md", refs)
        self.assertNotIn("references/format-gbt9704.md", refs)

    def test_coordination_genres_load_argument_chains(self) -> None:
        refs = provider._reference_paths_for_genres(["通知", "函", "复函", "征求意见函", "采购公告", "公示", "会议纪要"])

        self.assertIn("references/genre-playbooks.md", refs)
        self.assertIn("references/argument-chains.md", refs)
        self.assertIn("references/task-route-cards.md", refs)

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
        self.assertIn("references/format-gbt9704.md", format_refs)

    def test_plain_unknown_genre_does_not_load_playbook(self) -> None:
        refs = provider._reference_paths_for_genres(["通用材料"])

        self.assertEqual(refs, ["SKILL.md", "references/task-route-cards.md"])

    def test_common_short_genres_do_not_preload_the_full_reference_stack(self) -> None:
        refs = provider._reference_paths_for_genres(["通知", "请示", "报告", "说明", "方案"])

        self.assertIn("references/task-route-cards.md", refs)
        self.assertIn("references/argument-chains.md", refs)
        self.assertIn("references/official-style.md", refs)
        self.assertNotIn("references/genre-routing.md", refs)
        self.assertNotIn("references/handling-elements.md", refs)
        self.assertNotIn("references/genre-checklist.md", refs)
        self.assertNotIn("references/formal-addressing.md", refs)
        self.assertNotIn("references/anti-ai-patterns.md", refs)

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

    def test_full_dataset_batches_stay_within_context_budget(self) -> None:
        config = {
            "basePath": str(ROOT / "evals" / "official-writing"),
            "datasetPath": "datasets/cases.jsonl",
        }
        cases = provider._load_cases(config)
        observed: list[int] = []
        for index in range(0, len(cases), 10):
            chunk = cases[index : index + 10]
            genres = sorted({provider._case_genre(case) for case in chunk if provider._case_genre(case)})
            tasks = [provider._case_task(case) for case in chunk if provider._case_task(case)]
            observed.append(len(provider._load_skill_context(ROOT, genres, tasks)))

        self.assertEqual(len(observed), 27)
        self.assertLessEqual(max(observed), provider.MAX_SKILL_CONTEXT_CHARS)
        self.assertLess(max(observed), 25_000)

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
        for genre in ["模型服务技术需求", "智算中心建设方案", "本地化部署成本说明", "AI平台推理服务", "SLA并发保障方案"]:
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
