from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest

from maintenance.tests.hook_companion_support import ASSEMBLER


ROOT = Path(__file__).parents[2]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class QwenGateAdapterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.adapter_root = self.root / "qwen-code"
        ASSEMBLER.assemble("qwen-code", self.adapter_root, "delivery_cleanliness")
        self.adapter = load_module(
            f"cow_qwen_gate_adapter_{id(self)}",
            self.adapter_root / "scripts" / "gate_stop_hook.py",
        )
        self.runtime_root = self.root / "qwen-runtime"
        self.old_environment = {
            key: os.environ.get(key)
            for key in ("QWEN_RUNTIME_DIR", "QWEN_HOME")
        }
        os.environ["QWEN_RUNTIME_DIR"] = str(self.runtime_root)
        os.environ.pop("QWEN_HOME", None)
        self.addCleanup(self._restore_environment)

    def _restore_environment(self) -> None:
        for key, value in self.old_environment.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

    def _event(self, name: str, **extra):
        event = {
            "hook_event_name": name,
            "session_id": "qwen-session-1",
            "cwd": str(ROOT),
        }
        event.update(extra)
        return event

    def test_native_extension_manifest_and_hooks_are_self_contained(self) -> None:
        manifests = [
            path.relative_to(self.adapter_root).as_posix()
            for path in self.adapter_root.rglob("*")
            if path.is_file()
            and path.name in {"plugin.json", "qwen-extension.json", "kimi.plugin.json"}
        ]
        self.assertEqual(["qwen-extension.json"], manifests)
        manifest = json.loads(
            (self.adapter_root / "qwen-extension.json").read_text(encoding="utf-8")
        )
        self.assertEqual("skills", manifest["skills"])
        self.assertEqual("hooks/hooks.json", manifest["hooks"])
        hooks = json.loads(
            (self.adapter_root / "hooks/hooks.json").read_text(encoding="utf-8")
        )["hooks"]
        self.assertEqual(["UserPromptSubmit", "PostToolUse", "Stop"], list(hooks))
        self.assertEqual(
            "^(skill|read_file|run_shell_command)$",
            hooks["PostToolUse"][0]["matcher"],
        )
        for event, timeout in (
            ("UserPromptSubmit", 10000),
            ("PostToolUse", 10000),
            ("Stop", 30000),
        ):
            hook = hooks[event][0]["hooks"][0]
            self.assertEqual("command", hook["type"])
            self.assertEqual("powershell", hook["shell"])
            self.assertIn("${CLAUDE_PLUGIN_ROOT}/scripts/gate_stop_hook.py", hook["command"])
            self.assertEqual(timeout, hook["timeout"])

    def test_submitted_prompt_and_stop_positions_close_one_transaction(self) -> None:
        prompt = "/chinese-official-writing 请起草一份情况报告，只输出正文。"
        started = self.adapter.handle(
            self._event(
                "UserPromptSubmit",
                submitted_prompt=prompt,
                prompt="扩展后的 Skill 全文不得成为原始请求",
            )
        )
        self.assertTrue(started["continue"])

        internal = self.adapter.handle(
            self._event("UserPromptSubmit", prompt="Stop 续写理由")
        )
        self.assertTrue(internal["continue"])
        turn_path = (
            self.runtime_root
            / self.adapter.PLUGIN_DATA_DIRECTORY
            / self.adapter.TURN_STATE_DIRECTORY
            / "qwen-session-1.json"
        )
        self.assertEqual(1, json.loads(turn_path.read_text(encoding="utf-8"))["counter"])

        body = "情况报告\n\n测试工作已完成。"
        first = self.adapter.handle(
            self._event(
                "Stop", stop_hook_active=True, last_assistant_message=body
            )
        )
        second = self.adapter.handle(
            self._event(
                "Stop", stop_hook_active=True, last_assistant_message=body
            )
        )
        third = self.adapter.handle(
            self._event(
                "Stop", stop_hook_active=True, last_assistant_message=body
            )
        )
        self.assertEqual("block", first["decision"])
        self.assertEqual("block", second["decision"])
        self.assertTrue(third["continue"])

        turn = json.loads(turn_path.read_text(encoding="utf-8"))
        self.assertEqual(1, turn["counter"])
        self.assertEqual(3, turn["stop_events"])
        records = list(
            (
                self.runtime_root
                / self.adapter.PLUGIN_DATA_DIRECTORY
                / self.adapter.CORE_DATA_DIRECTORY
            ).rglob("*.json")
        )
        self.assertEqual(1, len(records))
        record = json.loads(records[0].read_text(encoding="utf-8"))
        self.assertTrue(record["skill_seen"])
        self.assertEqual("raw_turn_data_redacted", record["data_retention_state"])
        self.assertNotIn("request", record)
        self.assertNotIn("original", record["delivery_cleanliness"])

    def test_direct_skill_marker_requires_a_complete_slash_command(self) -> None:
        self.assertTrue(
            self.adapter._direct_skill_invocation(
                {"submitted_prompt": "/chinese-official-writing 起草通知"}
            )
        )
        self.assertFalse(
            self.adapter._direct_skill_invocation(
                {"submitted_prompt": "/chinese-official-writing-extra 起草通知"}
            )
        )


if __name__ == "__main__":
    unittest.main()
