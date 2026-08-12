import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest

from maintenance.tests.hook_companion_support import ASSEMBLER


ROOT = Path(__file__).parents[2]
SKILL_ROOT = ROOT / "chinese-official-writing"
CAPABILITIES_PATH = SKILL_ROOT / "hooks" / "host-capabilities.json"
PLAN_PATH = SKILL_ROOT / "hooks" / "README.md"
PREFLIGHT_PATH = ROOT / "maintenance" / "tools" / "preflight_claude_hooks.py"


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


PREFLIGHT = load_module("cow_claude_gate_preflight", PREFLIGHT_PATH)


class ClaudeGateAdapterTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.adapter_root = Path(self.temp.name) / "claude-code"
        ASSEMBLER.assemble("claude-code", self.adapter_root)
        self.packaged_skill_root = self.adapter_root / "skills" / "chinese-official-writing"
        self.module_path = self.adapter_root / "scripts" / "gate_stop_hook.py"
        self.hooks_path = self.adapter_root / "hooks" / "hooks.json"
        self.adapter = load_module(f"cow_claude_gate_adapter_{id(self)}", self.module_path)
        self.data_root = Path(self.temp.name) / "plugin-data"
        self.old_environment = {
            key: os.environ.get(key)
            for key in ("CLAUDE_PLUGIN_ROOT", "CLAUDE_PLUGIN_DATA", "COW_GATE_HOOK_DATA", "PLUGIN_ROOT")
        }
        os.environ["CLAUDE_PLUGIN_ROOT"] = str(self.adapter_root)
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
        codex = capabilities["hosts"]["codex"]
        self.assertEqual("package_registration_verified", codex["status"])
        claude = capabilities["hosts"]["claude_code"]
        self.assertEqual("lifecycle_verified", claude["status"])
        self.assertEqual(["UserPromptSubmit", "PostToolUse:Read", "Stop"], claude["verified_events"])
        self.assertEqual(["PostToolUse:Bash"], claude["unverified_events"])
        self.assertEqual("anthropic_messages_gateway", claude["verified_transport"])
        self.assertFalse(claude["first_party_login_required"])
        self.assertEqual("skill_only", capabilities["hosts"]["openclaw"]["status"])
        self.assertEqual("package_manifest_verified", capabilities["hosts"]["codebuddy"]["status"])
        self.assertFalse(capabilities["length_gate"]["automatic_expansion"])
        hooks = json.loads(self.hooks_path.read_text(encoding="utf-8"))["hooks"]
        self.assertEqual(["UserPromptSubmit", "PostToolUse", "Stop"], list(hooks))
        self.assertEqual("Bash|Read", hooks["PostToolUse"][0]["matcher"])
        for groups in hooks.values():
            command = groups[0]["hooks"][0]["command"]
            self.assertIn("CLAUDE_PLUGIN_ROOT", command)
            self.assertIn("CLAUDE_PLUGIN_DATA", command)
            self.assertIn("sys.argv[1]", command)
            self.assertIn("sys.argv[2]", command)
            self.assertNotIn("PLUGIN_ROOT", command.replace("CLAUDE_PLUGIN_ROOT", ""))
        plan = PLAN_PATH.read_text(encoding="utf-8")
        self.assertIn("下载、安装或调用普通 Skill 不会自动启用 Hook", plan)
        self.assertIn("重要材料仍建议由责任人员完成事实核对和正式审签", plan)
        self.assertIn("组装、安装、启用和宿主信任确认分开进行", plan)
        self.assertIn("无法确认运行条件时使用普通 Skill", plan)

    def test_read_event_arms_existing_core_and_stop_uses_plugin_data(self):
        prompt = self._event("UserPromptSubmit", prompt="请起草一份情况报告。")
        self.assertTrue(self.adapter.handle(prompt)["continue"])
        skill_path = self.packaged_skill_root / "SKILL.md"
        result = self.adapter.handle(
            self._event(
                "PostToolUse",
                tool_name="Read",
                tool_input={"file_path": str(skill_path)},
                tool_response={"success": True},
            )
        )
        self.assertTrue(result["continue"])
        stopped = self.adapter.handle(
            self._event(
                "Stop",
                stop_hook_active=False,
                last_assistant_message="情况报告\n\n测试工作已完成。",
            )
        )
        self.assertEqual("block", stopped["decision"])
        self.assertIn("Hook 完成 emit", stopped["reason"])
        records = list((self.data_root / self.adapter.CORE_DATA_DIRECTORY).rglob("*.json"))
        self.assertTrue(records)

    def test_review_only_request_allows_without_core_transaction(self):
        self.assertTrue(
            self.adapter.handle(
                self._event(
                    "UserPromptSubmit",
                    prompt="请复核这份采购申请，不要代改，不重写全文。",
                )
            )["continue"]
        )
        skill_path = self.packaged_skill_root / "SKILL.md"
        self.assertTrue(
            self.adapter.handle(
                self._event(
                    "PostToolUse",
                    tool_name="Read",
                    tool_input={"file_path": str(skill_path)},
                    tool_response={"success": True},
                )
            )["continue"]
        )
        stopped = self.adapter.handle(
            self._event(
                "Stop",
                stop_hook_active=False,
                last_assistant_message=(
                    "审查意见：结尾表述“尚不能据此形成采购结论”较空泛，"
                    "建议说明当前未决事项。"
                ),
            )
        )
        self.assertTrue(stopped["continue"])
        transactions = (
            self.data_root
            / self.adapter.CORE_DATA_DIRECTORY
            / "candidate-ai-gate-hook"
            / "transactions"
        )
        self.assertFalse(transactions.exists())

    def test_review_then_rewrite_still_uses_core_transaction(self):
        self.assertTrue(
            self.adapter.handle(
                self._event(
                    "UserPromptSubmit",
                    prompt="请先复核这份采购申请，再按建议改写全文。",
                )
            )["continue"]
        )
        skill_path = self.packaged_skill_root / "SKILL.md"
        self.adapter.handle(
            self._event(
                "PostToolUse",
                tool_name="Read",
                tool_input={"file_path": str(skill_path)},
                tool_response={"success": True},
            )
        )
        stopped = self.adapter.handle(
            self._event(
                "Stop",
                stop_hook_active=False,
                last_assistant_message="采购结论尚不能据此形成。",
            )
        )
        self.assertEqual("block", stopped["decision"])
        states = list(
            (self.data_root / self.adapter.CORE_DATA_DIRECTORY).rglob("state.json")
        )
        self.assertEqual(1, len(states))

    def test_each_prompt_gets_a_new_active_turn_without_prompt_id(self):
        first = self._event("UserPromptSubmit", prompt="相同请求")
        second = self._event("UserPromptSubmit", prompt="相同请求")
        self.assertTrue(self.adapter.handle(first)["continue"])
        first_turn = self.adapter._active_turn(self.data_root, "claude-session-1")
        self.assertTrue(self.adapter.handle(second)["continue"])
        second_turn = self.adapter._active_turn(self.data_root, "claude-session-1")
        self.assertNotEqual(first_turn, second_turn)

    def test_unsupported_event_or_wrong_host_fails_open_without_core_state(self):
        self.assertTrue(
            self.adapter.handle(
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
            self.adapter.handle(self._event("UserPromptSubmit", prompt="请起草一份报告。"))["continue"]
        )
        self.assertFalse(self.data_root.exists())

    def test_external_core_data_environment_is_not_used(self):
        external = Path(self.temp.name) / "external"
        os.environ["COW_GATE_HOOK_DATA"] = str(external)
        self.adapter.handle(self._event("UserPromptSubmit", prompt="请起草一份情况报告。"))
        skill_path = self.packaged_skill_root / "SKILL.md"
        self.adapter.handle(
            self._event(
                "PostToolUse",
                tool_name="Read",
                tool_input={"file_path": str(skill_path)},
                tool_response={"success": True},
            )
        )
        self.adapter.handle(
            self._event(
                "Stop",
                stop_hook_active=False,
                last_assistant_message="情况报告\n\n测试工作已完成。",
            )
        )
        self.assertFalse(external.exists())
        self.assertTrue((self.data_root / self.adapter.CORE_DATA_DIRECTORY).exists())

    def test_preflight_contract_supports_the_fixed_local_version(self):
        self.assertEqual([], PREFLIGHT.validate_plugin_layout(self.adapter_root))
        self.assertEqual((2, 1, 195), PREFLIGHT.parse_version("2.1.195 (Claude Code)"))
        self.assertIsNone(PREFLIGHT.parse_version("not a version"))


if __name__ == "__main__":
    unittest.main()

