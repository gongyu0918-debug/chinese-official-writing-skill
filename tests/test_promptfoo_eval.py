from __future__ import annotations

import importlib.util
import json
import os
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

        self.assertIn("references/genre-playbooks.md", refs)
        self.assertIn("references/ai-compute-docs.md", refs)
        self.assertIn("references/genre-checklist.md", refs)
        self.assertNotIn("references/format-gbt9704.md", refs)

    def test_coordination_genres_load_argument_chains(self) -> None:
        refs = provider._reference_paths_for_genres(["通知", "函", "复函", "征求意见函", "采购公告", "公示", "会议纪要"])

        self.assertIn("references/genre-playbooks.md", refs)
        self.assertIn("references/argument-chains.md", refs)

    def test_plain_unknown_genre_does_not_load_playbook(self) -> None:
        refs = provider._reference_paths_for_genres(["通用材料"])

        self.assertNotIn("references/genre-playbooks.md", refs)

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
