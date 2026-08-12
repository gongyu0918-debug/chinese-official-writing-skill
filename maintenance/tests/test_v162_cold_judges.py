from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
RUNNER_PATH = ROOT / "maintenance/tests/evidence/v162-hook-writing-real-ab/run_cold_judges.py"
SPEC = importlib.util.spec_from_file_location("v162_cold_judges", RUNNER_PATH)
assert SPEC is not None and SPEC.loader is not None
RUNNER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = RUNNER
SPEC.loader.exec_module(RUNNER)


class V162ColdJudgeTests(unittest.TestCase):
    def test_exact_judge_routes_and_timeout_are_frozen(self) -> None:
        self.assertEqual(
            {"kimi": "kimi/k3", "qwen": "alibaba-token-plan-2/qwen3.8-max", "grok": "xai/grok-4.5"},
            RUNNER.JUDGES,
        )
        self.assertEqual(1200, RUNNER.TIMEOUT_SECONDS)

    def test_validator_requires_all_nine_writing_groups_and_diff_findings(self) -> None:
        value = {
            "writing_review": {"groups": [{"group": f"G{number:02d}"} for number in range(1, 10)]},
            "diff_review": {"findings": []},
        }
        self.assertTrue(RUNNER.validate_final(json.dumps(value))["valid"])
        value["writing_review"]["groups"].pop()
        self.assertFalse(RUNNER.validate_final(json.dumps(value))["valid"])

    def test_stream_parser_binds_model_and_first_final(self) -> None:
        records = [
            {"type": "system", "subtype": "init", "model": "m", "apiKeySource": "none"},
            {"type": "assistant", "message": {"model": "m", "content": []}},
            {"type": "result", "subtype": "success", "is_error": False, "result": "{}", "modelUsage": {"m": {}}},
        ]
        parsed = RUNNER.parse_stream("\n".join(json.dumps(item) for item in records))
        self.assertEqual(["m"], parsed["init_models"])
        self.assertEqual(["m"], parsed["assistant_models"])
        self.assertEqual(["m"], parsed["model_usage"])
        self.assertEqual("{}", parsed["final"])


if __name__ == "__main__":
    unittest.main()
