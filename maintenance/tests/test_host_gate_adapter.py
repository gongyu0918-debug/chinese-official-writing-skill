from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import shlex
import subprocess
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[2]
SKILL_ROOT = ROOT / "chinese-official-writing"
ADAPTER_PATH = SKILL_ROOT / "hooks" / "host_gate_adapter.py"
HOOKS_PATH = SKILL_ROOT / "hooks" / "hooks.json"
WORKBUDDY_HOOKS_PATH = SKILL_ROOT / "hooks" / "workbuddy" / "hooks.json"
CODEX_MANIFEST_PATH = SKILL_ROOT / ".codex-plugin" / "plugin.json"
WORKBUDDY_MANIFEST_PATH = SKILL_ROOT / ".codebuddy-plugin" / "plugin.json"
SHIM_PATH = SKILL_ROOT / "skills" / "chinese-official-writing" / "SKILL.md"


def load_module():
    spec = importlib.util.spec_from_file_location("cow_host_gate_adapter", ADAPTER_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ADAPTER = load_module()


class HostGateAdapterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.data_root = Path(self.temporary.name)
        self.addCleanup(self.temporary.cleanup)

    def _event(self, name: str, **overrides):
        event = {
            "hook_event_name": name,
            "session_id": "host-session-1",
            "cwd": str(ROOT),
        }
        event.update(overrides)
        return event

    def _host_environment(self, host: str):
        if host == "codex":
            values = {
                "PLUGIN_ROOT": str(SKILL_ROOT),
                "PLUGIN_DATA": str(self.data_root),
                "CODEBUDDY_PLUGIN_ROOT": "",
                "CODEBUDDY_PLUGIN_DATA": "",
            }
        else:
            values = {
                "PLUGIN_ROOT": "",
                "PLUGIN_DATA": "",
                "CODEBUDDY_PLUGIN_ROOT": str(SKILL_ROOT),
                "CODEBUDDY_PLUGIN_DATA": str(self.data_root),
            }
        return mock.patch.dict(os.environ, values, clear=False)

    def _arm_and_stop(self, host: str):
        with self._host_environment(host):
            prompt = self._event(
                "UserPromptSubmit",
                prompt="根据材料起草一份简短通知。",
            )
            read = self._event(
                "PostToolUse",
                tool_name="Read",
                tool_input={"file_path": str(SKILL_ROOT / "SKILL.md")},
                tool_response={"success": True},
            )
            stop = self._event(
                "Stop",
                stop_hook_active=False,
                last_assistant_message="关于有关事项的通知\n\n请按材料所列时间办理。",
            )
            if host == "codex":
                for event in (prompt, read, stop):
                    event["turn_id"] = "codex-turn-1"
            self.assertEqual({"continue": True}, ADAPTER.handle(prompt))
            self.assertEqual({"continue": True}, ADAPTER.handle(read))
            return ADAPTER.handle(stop)

    def _run_configured_event(self, host: str, event: dict[str, object]):
        if host == "codex":
            hooks_path = HOOKS_PATH
            root_variable = "PLUGIN_ROOT"
            data_variable = "PLUGIN_DATA"
        else:
            hooks_path = WORKBUDDY_HOOKS_PATH
            root_variable = "CODEBUDDY_PLUGIN_ROOT"
            data_variable = "CODEBUDDY_PLUGIN_DATA"
        hooks = json.loads(hooks_path.read_text(encoding="utf-8"))["hooks"]
        command = hooks[event["hook_event_name"]][0]["hooks"][0]["command"]
        placeholder = "${" + root_variable + "}"
        self.assertIn(placeholder, command)
        expanded = command.replace(placeholder, SKILL_ROOT.as_posix())
        self.assertNotIn("${", expanded)
        argv = shlex.split(expanded, posix=True)
        self.assertEqual("python3", argv[0])
        self.assertEqual(ADAPTER_PATH.resolve(), Path(argv[1]).resolve())

        environment = os.environ.copy()
        for key in (
            "PLUGIN_ROOT",
            "PLUGIN_DATA",
            "CODEBUDDY_PLUGIN_ROOT",
            "CODEBUDDY_PLUGIN_DATA",
            "CLAUDE_PLUGIN_ROOT",
            "CLAUDE_PLUGIN_DATA",
            "COW_GATE_HOOK_DATA",
        ):
            environment.pop(key, None)
        environment[root_variable] = str(SKILL_ROOT)
        environment[data_variable] = str(self.data_root / f"{host}-subprocess-data")
        completed = subprocess.run(
            argv,
            input=json.dumps(event, ensure_ascii=False),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            cwd=ROOT,
            env=environment,
            timeout=30,
            check=False,
        )
        self.assertEqual(0, completed.returncode, completed.stderr)
        return json.loads(completed.stdout)

    def test_package_root_has_native_per_host_commands_and_one_shared_adapter(self):
        codex = json.loads(CODEX_MANIFEST_PATH.read_text(encoding="utf-8"))
        workbuddy = json.loads(WORKBUDDY_MANIFEST_PATH.read_text(encoding="utf-8"))
        codex_hooks = json.loads(HOOKS_PATH.read_text(encoding="utf-8"))["hooks"]
        workbuddy_hooks = json.loads(WORKBUDDY_HOOKS_PATH.read_text(encoding="utf-8"))["hooks"]

        self.assertEqual("chinese-official-writing", codex["name"])
        self.assertEqual("chinese-official-writing", workbuddy["name"])
        self.assertEqual("./skills/", codex["skills"])
        self.assertEqual(["./skills/"], workbuddy["skills"])
        self.assertEqual("./hooks/workbuddy/hooks.json", workbuddy["hooks"])
        self.assertEqual("MIT", codex["license"])
        self.assertEqual("MIT", workbuddy["license"])
        for hooks in (codex_hooks, workbuddy_hooks):
            self.assertEqual(["UserPromptSubmit", "PostToolUse", "Stop"], list(hooks))
            self.assertEqual("Bash|Read", hooks["PostToolUse"][0]["matcher"])
        for groups in codex_hooks.values():
            command = groups[0]["hooks"][0]["command"]
            self.assertIn("${PLUGIN_ROOT}", command)
            self.assertNotIn("CODEBUDDY_PLUGIN_ROOT", command)
            self.assertNotIn("CLAUDE_PLUGIN_ROOT", command)
        for groups in workbuddy_hooks.values():
            command = groups[0]["hooks"][0]["command"]
            self.assertIn("${CODEBUDDY_PLUGIN_ROOT}", command)
            self.assertNotIn("${PLUGIN_ROOT}", command)
            self.assertNotIn("CLAUDE_PLUGIN_ROOT", command)
        for hooks in (codex_hooks, workbuddy_hooks):
            for groups in hooks.values():
                command = groups[0]["hooks"][0]["command"]
                self.assertIn("hooks/host_gate_adapter.py", command)
                self.assertNotIn("prose_lint", command)

    def test_plugin_skill_shim_keeps_canonical_description_and_routes_to_top_level(self):
        canonical = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        shim = SHIM_PATH.read_text(encoding="utf-8")
        canonical_description = canonical.split("description: ", 1)[1].splitlines()[0]
        shim_description = shim.split("description: ", 1)[1].splitlines()[0]

        self.assertEqual(canonical_description, shim_description)
        self.assertIn("../../SKILL.md", shim)
        self.assertNotIn("## 硬边界", shim)

    def test_codex_maps_documented_turn_and_preserves_core_block_shape(self):
        result = self._arm_and_stop("codex")
        self.assertEqual("block", result.get("decision"))
        self.assertIsInstance(result.get("reason"), str)
        self.assertNotIn("continue", result)

    def test_workbuddy_allocates_turn_and_translates_stop_continuation(self):
        result = self._arm_and_stop("workbuddy")
        self.assertEqual(False, result.get("continue"))
        self.assertIsInstance(result.get("reason"), str)
        self.assertNotIn("decision", result)
        turn = ADAPTER._active_workbuddy_turn(self.data_root, "host-session-1")
        self.assertTrue(turn and turn.startswith("workbuddy-1-"))

    def test_real_configured_commands_expand_and_run_three_event_subprocesses(self):
        for host in ("codex", "workbuddy"):
            with self.subTest(host=host):
                prompt = self._event(
                    "UserPromptSubmit",
                    prompt="根据材料起草一份简短通知。",
                )
                read = self._event(
                    "PostToolUse",
                    tool_name="Read",
                    tool_input={"file_path": str(SKILL_ROOT / "SKILL.md")},
                    tool_response={"success": True},
                )
                stop = self._event(
                    "Stop",
                    stop_hook_active=False,
                    last_assistant_message="关于有关事项的通知\n\n请按材料所列时间办理。",
                )
                if host == "codex":
                    for event in (prompt, read, stop):
                        event["turn_id"] = "codex-subprocess-turn-1"
                self.assertEqual({"continue": True}, self._run_configured_event(host, prompt))
                self.assertEqual({"continue": True}, self._run_configured_event(host, read))
                result = self._run_configured_event(host, stop)
                if host == "codex":
                    self.assertEqual("block", result.get("decision"))
                else:
                    self.assertEqual(False, result.get("continue"))

    def test_workbuddy_missing_stop_message_fails_open(self):
        with self._host_environment("workbuddy"):
            self.assertEqual(
                {"continue": True},
                ADAPTER.handle(
                    self._event(
                        "UserPromptSubmit",
                        prompt="根据材料起草通知。",
                    )
                ),
            )
            self.assertEqual(
                {"continue": True},
                ADAPTER.handle(
                    self._event("Stop", stop_hook_active=False)
                ),
            )

    def test_wrong_plugin_root_and_missing_data_fail_open_without_writes(self):
        with mock.patch.dict(
            os.environ,
            {
                "PLUGIN_ROOT": str(ROOT),
                "PLUGIN_DATA": "",
                "CODEBUDDY_PLUGIN_ROOT": "",
                "CODEBUDDY_PLUGIN_DATA": "",
            },
            clear=False,
        ):
            result = ADAPTER.handle(
                self._event(
                    "UserPromptSubmit",
                    turn_id="codex-turn-1",
                    prompt="起草通知。",
                )
            )
        self.assertEqual({"continue": True}, result)
        self.assertEqual([], list(self.data_root.rglob("*")))


if __name__ == "__main__":
    unittest.main()
