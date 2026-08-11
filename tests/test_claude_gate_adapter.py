import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).parents[1]
SKILL_ROOT = ROOT / "chinese-official-writing"
ADAPTER_ROOT = SKILL_ROOT / "hooks" / "claude-code"
MODULE_PATH = ADAPTER_ROOT / "scripts" / "gate_stop_hook.py"
HOOKS_PATH = ADAPTER_ROOT / "hooks" / "hooks.json"
CAPABILITIES_PATH = SKILL_ROOT / "hooks" / "host-capabilities.json"
PLAN_PATH = SKILL_ROOT / "hooks" / "AGENT_GLUE.md"
PREFLIGHT_PATH = ROOT / "tools" / "preflight_claude_hooks.py"


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ADAPTER = load_module("cow_claude_gate_adapter", MODULE_PATH)
PREFLIGHT = load_module("cow_claude_gate_preflight", PREFLIGHT_PATH)


class ClaudeGateAdapterTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.data_root = Path(self.temp.name) / "plugin-data"
        self.old_environment = {
            key: os.environ.get(key)
            for key in ("CLAUDE_PLUGIN_ROOT", "CLAUDE_PLUGIN_DATA", "COW_GATE_HOOK_DATA", "PLUGIN_ROOT")
        }
        os.environ["CLAUDE_PLUGIN_ROOT"] = str(ADAPTER_ROOT)
        os.environ["CLAUDE_PLUGIN_DATA"] = str(self.data_root)
        self.addCleanup(self._restore_environment)

    def _restore_environment(self):
        for key, value in self.old_environment.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

    def _event(self, name, **extra):
        event = {
            "hook_event_name": name,
            "session_id": "claude-session-1",
            "cwd": str(ROOT),
        }
        event.update(extra)
        return event

    def test_contract_manifest_and_capabilities_are_explicitly_opt_in(self):
        capabilities = json.loads(CAPABILITIES_PATH.read_text(encoding="utf-8"))
        self.assertFalse(capabilities["activation"]["ordinary_skill_install_enables_hooks"])
        self.assertEqual("verified", capabilities["hosts"]["codex"]["status"])
        claude = capabilities["hosts"]["claude_code"]
        self.assertEqual("registration_verified", claude["status"])
        self.assertEqual(["UserPromptSubmit"], claude["verified_events"])
        self.assertEqual(["PostToolUse:Bash|Read", "Stop"], claude["unverified_events"])
        self.assertEqual("metadata_only", capabilities["hosts"]["openclaw"]["status"])
        self.assertEqual("unknown", capabilities["hosts"]["workbuddy"]["status"])
        hooks = json.loads(HOOKS_PATH.read_text(encoding="utf-8"))["hooks"]
        self.assertEqual(["UserPromptSubmit", "PostToolUse", "Stop"], list(hooks))
        self.assertEqual("Bash|Read", hooks["PostToolUse"][0]["matcher"])
        for groups in hooks.values():
            command = groups[0]["hooks"][0]["command"]
            self.assertIn("CLAUDE_PLUGIN_ROOT", command)
            self.assertNotIn("PLUGIN_ROOT", command.replace("CLAUDE_PLUGIN_ROOT", ""))
        plan = PLAN_PATH.read_text(encoding="utf-8")
        self.assertIn("ordinary Skill and its mirrors do not enable hooks", plan)
        self.assertIn("session-only plugin registration", plan)
        self.assertIn("remain unverified", plan)
        self.assertIn("WorkBuddy remains `unknown`", plan)

    def test_read_event_arms_existing_core_and_stop_uses_plugin_data(self):
        prompt = self._event("UserPromptSubmit", prompt="请起草一份情况报告。")
        self.assertTrue(ADAPTER.handle(prompt)["continue"])
        skill_path = SKILL_ROOT / "SKILL.md"
        result = ADAPTER.handle(
            self._event(
                "PostToolUse",
                tool_name="Read",
                tool_input={"file_path": str(skill_path)},
                tool_response={"success": True},
            )
        )
        self.assertTrue(result["continue"])
        stopped = ADAPTER.handle(
            self._event(
                "Stop",
                stop_hook_active=False,
                last_assistant_message="情况报告\n\n测试工作已完成。",
            )
        )
        self.assertEqual("block", stopped["decision"])
        self.assertIn("Hook 完成 emit", stopped["reason"])
        records = list((self.data_root / ADAPTER.CORE_DATA_DIRECTORY).rglob("*.json"))
        self.assertTrue(records)

    def test_each_prompt_gets_a_new_active_turn_without_prompt_id(self):
        first = self._event("UserPromptSubmit", prompt="相同请求")
        second = self._event("UserPromptSubmit", prompt="相同请求")
        self.assertTrue(ADAPTER.handle(first)["continue"])
        first_turn = ADAPTER._active_turn(self.data_root, "claude-session-1")
        self.assertTrue(ADAPTER.handle(second)["continue"])
        second_turn = ADAPTER._active_turn(self.data_root, "claude-session-1")
        self.assertNotEqual(first_turn, second_turn)

    def test_unsupported_event_or_wrong_host_fails_open_without_core_state(self):
        self.assertTrue(
            ADAPTER.handle(
                self._event(
                    "PostToolUse",
                    tool_name="Write",
                    tool_input={"file_path": "C:/example.txt"},
                )
            )["continue"]
        )
        self.assertFalse(self.data_root.exists())
        os.environ["CLAUDE_PLUGIN_ROOT"] = str(ROOT)
        self.assertTrue(
            ADAPTER.handle(self._event("UserPromptSubmit", prompt="请起草一份报告。"))["continue"]
        )
        self.assertFalse(self.data_root.exists())

    def test_external_core_data_environment_is_not_used(self):
        external = Path(self.temp.name) / "external"
        os.environ["COW_GATE_HOOK_DATA"] = str(external)
        ADAPTER.handle(self._event("UserPromptSubmit", prompt="请起草一份情况报告。"))
        skill_path = SKILL_ROOT / "SKILL.md"
        ADAPTER.handle(
            self._event(
                "PostToolUse",
                tool_name="Read",
                tool_input={"file_path": str(skill_path)},
                tool_response={"success": True},
            )
        )
        ADAPTER.handle(
            self._event(
                "Stop",
                stop_hook_active=False,
                last_assistant_message="情况报告\n\n测试工作已完成。",
            )
        )
        self.assertFalse(external.exists())
        self.assertTrue((self.data_root / ADAPTER.CORE_DATA_DIRECTORY).exists())

    def test_preflight_contract_supports_the_fixed_local_version(self):
        self.assertEqual([], PREFLIGHT.validate_plugin_layout(ADAPTER_ROOT))
        self.assertEqual((2, 1, 195), PREFLIGHT.parse_version("2.1.195 (Claude Code)"))
        self.assertIsNone(PREFLIGHT.parse_version("not a version"))


if __name__ == "__main__":
    unittest.main()
