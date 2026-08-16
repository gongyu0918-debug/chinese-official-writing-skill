from __future__ import annotations

import ast
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
NEW_ARCHITECTURE_FILES = (
    ROOT / "maintenance/tools/assemble_hook_companion.py",
    ROOT / "chinese-official-writing/hooks/core/gate_stop_hook.py",
    ROOT / "chinese-official-writing/hooks/adapters/host_gate_adapter.py",
    ROOT / "chinese-official-writing/hooks/adapters/claude-code/gate_stop_hook.py",
    ROOT / "chinese-official-writing/hooks/capabilities/protective_expansion/contract.py",
    ROOT / "chinese-official-writing/hooks/capabilities/protective_expansion/runtime.py",
    ROOT / "chinese-official-writing/hooks/capabilities/delivery_cleanliness/runtime.py",
)
KNOWN_COMPLEXITY_DEBT = {
    "chinese-official-writing/scripts/review_gate.py:locate_candidates": (100, 25),
}
DETECTION_PIPELINE_FUNCTIONS = (
    "_validated_detection_timeouts",
    "_read_detection_inputs",
    "_resume_detection_transaction",
    "_assert_empty_transaction",
    "_build_detection_backup",
    "_build_initial_detection_state",
    "_write_detection_snapshots",
    "_validate_guided_marker_for_detection",
    "_locate_and_stage_repair",
    "detect_transaction",
)
CANDIDATE_PIPELINE_FUNCTIONS = (
    "_verified_candidate_findings",
    "_verified_repair_envelope",
    "_indexed_candidate_findings",
    "_candidate_envelope",
    "_candidate_repair_identity",
    "_candidate_repair_action",
    "_candidate_repair_span",
    "_candidate_replacement_reason",
    "_plan_candidate_repair",
    "_apply_candidate_operations",
    "_request_anchored_change_reason",
    "_guided_anchor_change_reason",
    "_candidate_anchor_reason",
    "_candidate_success_reason",
    "evaluate_candidate",
)
DISPATCH_PIPELINE_FUNCTIONS = (
    "_dispatch_bound_input_hashes",
    "_complete_repair_bridge",
    "_claim_repair_bridge",
    "_complete_verdict_bridge",
    "_claim_verdict_bridge",
    "_abort_matching_dispatch",
    "_dispatch_transaction_locked",
)


def function_metrics(path: Path) -> dict[str, tuple[int, int]]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    metrics: dict[str, tuple[int, int]] = {}
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        decisions = sum(
            isinstance(
                child,
                (
                    ast.If,
                    ast.For,
                    ast.While,
                    ast.Try,
                    ast.With,
                    ast.Match,
                    ast.BoolOp,
                    ast.IfExp,
                    ast.comprehension,
                ),
            )
            for child in ast.walk(node)
        )
        end = getattr(node, "end_lineno", node.lineno)
        metrics[node.name] = (end - node.lineno + 1, decisions)
    return metrics


class ComplexityContractTests(unittest.TestCase):
    def test_new_architecture_does_not_add_god_functions(self) -> None:
        for path in NEW_ARCHITECTURE_FILES:
            for name, (lines, decisions) in function_metrics(path).items():
                with self.subTest(path=path, function=name):
                    self.assertLessEqual(lines, 80)
                    self.assertLessEqual(decisions, 25)

    def test_known_complexity_debt_stays_explicit(self) -> None:
        for key, minimum in KNOWN_COMPLEXITY_DEBT.items():
            relative, function = key.split(":", 1)
            actual = function_metrics(ROOT / relative)[function]
            with self.subTest(key=key):
                self.assertGreaterEqual(actual[0], minimum[0])
                self.assertGreaterEqual(actual[1], minimum[1])

    def test_detection_pipeline_has_no_god_functions(self) -> None:
        metrics = function_metrics(
            ROOT / "chinese-official-writing/scripts/review_gate.py"
        )
        for name in DETECTION_PIPELINE_FUNCTIONS:
            with self.subTest(function=name):
                lines, decisions = metrics[name]
                self.assertLessEqual(lines, 80)
                self.assertLessEqual(decisions, 25)

    def test_candidate_pipeline_has_no_god_functions(self) -> None:
        metrics = function_metrics(
            ROOT / "chinese-official-writing/scripts/review_gate.py"
        )
        for name in CANDIDATE_PIPELINE_FUNCTIONS:
            with self.subTest(function=name):
                lines, decisions = metrics[name]
                self.assertLessEqual(lines, 80)
                self.assertLessEqual(decisions, 25)

    def test_dispatch_pipeline_has_no_god_functions(self) -> None:
        metrics = function_metrics(
            ROOT / "chinese-official-writing/scripts/review_gate.py"
        )
        for name in DISPATCH_PIPELINE_FUNCTIONS:
            with self.subTest(function=name):
                lines, decisions = metrics[name]
                self.assertLessEqual(lines, 80)
                self.assertLessEqual(decisions, 25)

    def test_hook_thresholds_are_named_constants(self) -> None:
        core = ast.parse(
            (ROOT / "chinese-official-writing/hooks/core/gate_stop_hook.py").read_text(
                encoding="utf-8"
            )
        )
        names = {
            target.id
            for node in core.body
            if isinstance(node, ast.Assign)
            for target in node.targets
            if isinstance(target, ast.Name)
        }
        for required in (
            "MAX_STOP_ATTEMPTS",
            "SAFE_KEY_MAX_LENGTH",
            "GATE_SUBPROCESS_TIMEOUT_SECONDS",
            "MIN_FENCED_JSON_LINES",
        ):
            self.assertIn(required, names)

    def test_legacy_length_hook_is_absent_and_current_capability_is_explicit(self) -> None:
        self.assertFalse(
            (ROOT / "chinese-official-writing/hooks/length_band.py").exists()
        )
        self.assertFalse(
            (ROOT / "chinese-official-writing/hooks/core/length_band.py").exists()
        )
        capabilities = (
            ROOT / "chinese-official-writing/hooks/host-capabilities.json"
        ).read_text(encoding="utf-8")
        self.assertTrue(
            (
                ROOT
                / "chinese-official-writing/hooks/capabilities/under_length/runtime.py"
            ).is_file()
        )
        self.assertIn('"automatic_expansion": true', capabilities)
        self.assertIn('"status": "candidate"', capabilities)
        self.assertIn('"automatic_compression": false', capabilities)


if __name__ == "__main__":
    unittest.main()
