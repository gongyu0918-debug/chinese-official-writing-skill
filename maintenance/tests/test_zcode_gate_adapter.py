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


class ZCodeGateAdapterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.adapter_root = Path(self.temp.name) / "zcode"
        ASSEMBLER.assemble("zcode", self.adapter_root, "delivery_cleanliness")
        self.adapter = load_module(
            f"cow_zcode_gate_adapter_{id(self)}",
            self.adapter_root / "scripts" / "gate_stop_hook.py",
        )
        self.data_root = Path(self.temp.name) / "plugin-data"
        self.old_environment = {
            key: os.environ.get(key)
            for key in (
                "CLAUDE_PLUGIN_ROOT",
                "CLAUDE_PLUGIN_DATA",
                "ZCODE_PLUGIN_ROOT",
                "ZCODE_PLUGIN_DATA",
            )
        }
        os.environ.pop("CLAUDE_PLUGIN_ROOT", None)
        os.environ.pop("CLAUDE_PLUGIN_DATA", None)
        os.environ["ZCODE_PLUGIN_ROOT"] = str(self.adapter_root)
        os.environ["ZCODE_PLUGIN_DATA"] = str(self.data_root)
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
            "session_id": "zcode-session-1",
            "cwd": str(ROOT),
        }
        event.update(extra)
        return event

    def test_native_manifest_and_process_hooks_are_self_contained(self) -> None:
        manifests = [
            path.relative_to(self.adapter_root).as_posix()
            for path in self.adapter_root.rglob("plugin.json")
        ]
        self.assertEqual([".zcode-plugin/plugin.json"], manifests)
        hooks = json.loads(
            (self.adapter_root / "hooks" / "hooks.json").read_text(encoding="utf-8")
        )["hooks"]
        self.assertEqual(["UserPromptSubmit", "PostToolUse", "Stop"], list(hooks))
        self.assertEqual("Bash|Read", hooks["PostToolUse"][0]["matcher"])
        for event, timeout in (
            ("UserPromptSubmit", 10000),
            ("PostToolUse", 10000),
            ("Stop", 30000),
        ):
            hook = hooks[event][0]["hooks"][0]
            self.assertEqual("process", hook["type"])
            self.assertEqual("py", hook["command"])
            self.assertEqual(
                ["-3", "${ZCODE_PLUGIN_ROOT}/scripts/gate_stop_hook.py"],
                hook["args"],
            )
            self.assertEqual(timeout, hook["timeoutMs"])

    def test_zcode_root_and_data_fields_reach_existing_core(self) -> None:
        self.assertTrue(
            self.adapter.handle(
                self._event("UserPromptSubmit", prompt="请起草一份情况报告。")
            )["continue"]
        )
        skill_path = self.adapter_root / "skills" / "chinese-official-writing" / "SKILL.md"
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
                last_assistant_message="情况报告\n\n测试工作已完成。",
            )
        )
        self.assertEqual("block", stopped["decision"])
        records = list((self.data_root / self.adapter.CORE_DATA_DIRECTORY).rglob("*.json"))
        self.assertTrue(records)


if __name__ == "__main__":
    unittest.main()
