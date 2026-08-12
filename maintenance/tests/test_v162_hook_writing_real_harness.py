from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
HARNESS_PATH = ROOT / "maintenance/tests/evidence/v162-hook-writing-real-ab/harness.py"
SPEC = importlib.util.spec_from_file_location("v162_hook_writing_real_harness", HARNESS_PATH)
assert SPEC is not None and SPEC.loader is not None
HARNESS = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = HARNESS
SPEC.loader.exec_module(HARNESS)


class V162HookWritingRealHarnessTests(unittest.TestCase):
    def test_matrix_and_exact_models_are_frozen(self) -> None:
        self.assertEqual(3, HARNESS.MAX_PROVIDER_LANES)
        self.assertEqual(9, len(HARNESS.PAIR_SPECS))
        self.assertEqual(9, len(HARNESS.BLIND_PLAN))
        self.assertEqual(
            {
                "opencode": "opencode-go/deepseek-v4-flash-0731",
                "ollama": "ollama-cloud/deepseek-v4-flash-0731",
                "alibaba2": "alibaba-token-plan-2/deepseek-v4-flash-0731",
            },
            HARNESS.MODELS,
        )
        for provider in HARNESS.MODELS:
            pairs = [item for item in HARNESS.PAIR_SPECS if item["provider"] == provider]
            self.assertEqual(3, len(pairs))
            self.assertEqual({"T1", "T2", "T3"}, {item["case_id"] for item in pairs})
            for pair in pairs:
                self.assertEqual({"disabled", "enabled"}, set(pair["order"]))

    def test_enabled_command_only_adds_plugin_dir(self) -> None:
        for model in HARNESS.MODELS.values():
            disabled = HARNESS.build_command("claude", model, False)
            enabled = HARNESS.build_command("claude", model, True)
            self.assertEqual(disabled, HARNESS.without_plugin(enabled))
            self.assertEqual(["--plugin-dir", str(HARNESS.PLUGIN_DIR.resolve())], enabled[-2:])
            self.assertIn("max", enabled)
            self.assertNotIn("--dangerously-skip-permissions", enabled)

    def test_environment_contract_removes_user_auth(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            old = {key: os.environ.get(key) for key in HARNESS.SENSITIVE_ENV_KEYS}
            try:
                for key in HARNESS.SENSITIVE_ENV_KEYS:
                    os.environ[key] = "must-not-leak"
                first = HARNESS.build_run_environment("model", root / "a", root / "ta")
                second = HARNESS.build_run_environment("model", root / "b", root / "tb")
                self.assertEqual(HARNESS.normalized_environment_contract(first), HARNESS.normalized_environment_contract(second))
                self.assertNotIn("must-not-leak", first.values())
                auth = HARNESS.auth_environment(root / "a")
                self.assertNotIn("ANTHROPIC_AUTH_TOKEN", auth)
                self.assertNotIn("CLAUDE_CODE_OAUTH_TOKEN", auth)
            finally:
                for key, value in old.items():
                    if value is None:
                        os.environ.pop(key, None)
                    else:
                        os.environ[key] = value

    def test_stream_parser_captures_skill_hook_and_final(self) -> None:
        records = [
            {"type": "system", "subtype": "hook_started", "hook_event": "UserPromptSubmit"},
            {"type": "system", "subtype": "hook_response", "hook_event": "UserPromptSubmit", "output": "{\"continue\":true}", "exit_code": 0, "outcome": "success"},
            {"type": "system", "subtype": "init", "model": "m", "apiKeySource": "none", "plugins": [{"name": HARNESS.GATE_PLUGIN_NAME}]},
            {"type": "assistant", "message": {"model": "m", "content": [{"type": "tool_use", "name": "Read", "input": {"file_path": str(HARNESS.SKILL_PATH)}}]}},
            {"type": "system", "subtype": "hook_started", "hook_event": "Stop"},
            {"type": "system", "subtype": "hook_response", "hook_event": "Stop", "output": "{\"decision\":\"block\"}", "exit_code": 0, "outcome": "success"},
            {"type": "result", "subtype": "success", "is_error": False, "result": "正文", "modelUsage": {"m": {}}, "num_turns": 2},
        ]
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "stream.jsonl"
            path.write_text("\n".join(json.dumps(item, ensure_ascii=False) for item in records) + "\n", encoding="utf-8")
            parsed = HARNESS.parse_stream(path)
        self.assertEqual("正文", parsed["final"])
        self.assertEqual(["m"], parsed["init_models"])
        self.assertEqual([str(HARNESS.SKILL_PATH)], parsed["reads"])
        self.assertTrue(any(item["decision_block"] for item in parsed["hook_responses"]))

    def test_cases_and_blind_mapping_are_complete(self) -> None:
        cases = HARNESS.load_cases()
        self.assertEqual({"T1", "T2", "T3"}, set(cases))
        self.assertIn("制度正文", cases["T2"]["title"])
        self.assertIn("活动新闻稿", cases["T3"]["title"])
        mapping = HARNESS.build_mapping()
        self.assertEqual(9, len(mapping["groups"]))
        self.assertEqual(9, len({item["group"] for item in mapping["groups"]}))
        for item in mapping["groups"]:
            self.assertEqual({"disabled", "enabled"}, {item["稿件甲_treatment"], item["稿件乙_treatment"]})

    def test_execute_requires_explicit_authorization_and_new_output(self) -> None:
        old = os.environ.pop(HARNESS.AUTHORIZATION_ENV, None)
        try:
            with tempfile.TemporaryDirectory() as temporary:
                with self.assertRaises(SystemExit):
                    HARNESS.execute("claude", Path(temporary) / "run")
        finally:
            if old is not None:
                os.environ[HARNESS.AUTHORIZATION_ENV] = old


if __name__ == "__main__":
    unittest.main()
