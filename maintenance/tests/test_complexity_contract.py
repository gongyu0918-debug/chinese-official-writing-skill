from __future__ import annotations

import ast
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
NEW_ARCHITECTURE_FILES = (
    ROOT / "maintenance/tools/assemble_hook_companion.py",
    ROOT / "chinese-official-writing/hooks/adapters/host_gate_adapter.py",
    ROOT / "chinese-official-writing/hooks/adapters/claude-code/gate_stop_hook.py",
)
KNOWN_COMPLEXITY_DEBT = {
    "chinese-official-writing/scripts/review_gate.py:evaluate_candidate": (250, 80),
    "chinese-official-writing/scripts/review_gate.py:detect_transaction": (150, 20),
    "chinese-official-writing/hooks/core/gate_stop_hook.py:handle_stop": (100, 35),
}


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

    def test_length_hook_is_not_shipped(self) -> None:
        self.assertFalse(
            (ROOT / "chinese-official-writing/hooks/length_band.py").exists()
        )
        self.assertFalse(
            (ROOT / "chinese-official-writing/hooks/core/length_band.py").exists()
        )
        capabilities = (
            ROOT / "chinese-official-writing/hooks/host-capabilities.json"
        ).read_text(encoding="utf-8")
        self.assertIn('"automatic_expansion": false', capabilities)
        self.assertIn('"automatic_compression": false', capabilities)


if __name__ == "__main__":
    unittest.main()
