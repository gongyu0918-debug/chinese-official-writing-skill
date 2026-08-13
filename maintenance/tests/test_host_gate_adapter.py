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

from maintenance.tests.hook_companion_support import ASSEMBLER, HookCompanionTestMixin


ROOT = Path(__file__).resolve().parents[2]
SKILL_ROOT = ROOT / "chinese-official-writing"
def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class HostGateAdapterTests(HookCompanionTestMixin, unittest.TestCase):
    def setUp(self) -> None:
        self.setUpHookCompanions()
        self.PLUGIN_ROOTS = {
            "codex": self.companion_roots["codex"],
            "workbuddy": self.companion_roots["codebuddy"],
        }
        self.ADAPTER_PATHS = {
            host: plugin_root / "scripts" / "host_gate_adapter.py"
            for host, plugin_root in self.PLUGIN_ROOTS.items()
        }
        self.HOOKS_PATHS = {
            host: plugin_root / "hooks" / "hooks.json"
            for host, plugin_root in self.PLUGIN_ROOTS.items()
        }
        self.MANIFEST_PATHS = {
            "codex": self.PLUGIN_ROOTS["codex"] / ".codex-plugin" / "plugin.json",
            "workbuddy": self.PLUGIN_ROOTS["workbuddy"] / ".codebuddy-plugin" / "plugin.json",
        }
        self.ADAPTERS = {
            host: load_module(f"cow_{host}_gate_adapter_{id(self)}", path)
            for host, path in self.ADAPTER_PATHS.items()
        }
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
        plugin_root = self.PLUGIN_ROOTS[host]
        if host == "codex":
            values = {
                "PLUGIN_ROOT": str(plugin_root),
                "PLUGIN_DATA": str(self.data_root),
                "CODEBUDDY_PLUGIN_ROOT": "",
                "CODEBUDDY_PLUGIN_DATA": "",
            }
        else:
            values = {
                "PLUGIN_ROOT": "",
                "PLUGIN_DATA": "",
                "CODEBUDDY_PLUGIN_ROOT": str(plugin_root),
                "CODEBUDDY_PLUGIN_DATA": str(self.data_root),
            }
        return mock.patch.dict(os.environ, values, clear=False)

    def _arm_and_stop(self, host: str):
        adapter = self.ADAPTERS[host]
        plugin_root = self.PLUGIN_ROOTS[host]
        with self._host_environment(host):
            prompt = self._event(
                "UserPromptSubmit",
                prompt="根据材料起草一份简短通知。",
            )
            read = self._event(
                "PostToolUse",
                tool_name="Read",
                tool_input={
                    "file_path": str(
                        plugin_root / "skills" / "chinese-official-writing" / "SKILL.md"
                    )
                },
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
            self.assertEqual({"continue": True}, adapter.handle(prompt))
            self.assertEqual({"continue": True}, adapter.handle(read))
            return adapter.handle(stop)

    def _run_configured_event(self, host: str, event: dict[str, object]):
        if host == "codex":
            hooks_path = self.HOOKS_PATHS[host]
            root_variable = "PLUGIN_ROOT"
            data_variable = "PLUGIN_DATA"
            placeholder = "${PLUGIN_ROOT}"
        else:
            hooks_path = self.HOOKS_PATHS[host]
            root_variable = "CODEBUDDY_PLUGIN_ROOT"
            data_variable = "CODEBUDDY_PLUGIN_DATA"
            placeholder = "${CODEBUDDY_PLUGIN_ROOT}"
        hooks = json.loads(hooks_path.read_text(encoding="utf-8"))["hooks"]
        command = hooks[event["hook_event_name"]][0]["hooks"][0]["command"]
        self.assertIn(placeholder, command)
        plugin_root = self.PLUGIN_ROOTS[host]
        expanded = command.replace(placeholder, plugin_root.as_posix())
        self.assertNotIn("${", expanded)
        argv = shlex.split(expanded, posix=True)
        self.assertEqual("python3", argv[0])
        self.assertEqual(self.ADAPTER_PATHS[host].resolve(), Path(argv[1]).resolve())

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
        environment[root_variable] = str(plugin_root)
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
        codex = json.loads(self.MANIFEST_PATHS["codex"].read_text(encoding="utf-8"))
        workbuddy = json.loads(self.MANIFEST_PATHS["workbuddy"].read_text(encoding="utf-8"))
        codex_hooks = json.loads(self.HOOKS_PATHS["codex"].read_text(encoding="utf-8"))["hooks"]
        workbuddy_hooks = json.loads(self.HOOKS_PATHS["workbuddy"].read_text(encoding="utf-8"))["hooks"]

        self.assertEqual("chinese-official-writing", codex["name"])
        self.assertEqual("chinese-official-writing", workbuddy["name"])
        self.assertEqual("./skills/", codex["skills"])
        self.assertEqual(["./skills/"], workbuddy["skills"])
        self.assertEqual("./hooks/hooks.json", workbuddy["hooks"])
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
                self.assertIn("scripts/host_gate_adapter.py", command)
                self.assertNotIn("prose_lint", command)

    def test_each_plugin_contains_a_full_skill_without_parent_traversal(self):
        canonical = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        for host, plugin_root in self.PLUGIN_ROOTS.items():
            with self.subTest(host=host):
                packaged_root = plugin_root / "skills" / "chinese-official-writing"
                packaged_skill = (packaged_root / "SKILL.md").read_text(encoding="utf-8")
                self.assertEqual(canonical, packaged_skill)
                self.assertIn("## 硬边界", packaged_skill)
                self.assertNotIn("../", packaged_skill)
                self.assertFalse((packaged_root / "plugins").exists())
                self.assertFalse((packaged_root / ".codex-plugin").exists())
                self.assertFalse((packaged_root / ".codebuddy-plugin").exists())

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
        turn = self.ADAPTERS["workbuddy"]._active_workbuddy_turn(
            self.data_root, "host-session-1"
        )
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
                    tool_input={
                        "file_path": str(
                            self.PLUGIN_ROOTS[host]
                            / "skills"
                            / "chinese-official-writing"
                            / "SKILL.md"
                        )
                    },
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
            adapter = self.ADAPTERS["workbuddy"]
            self.assertEqual(
                {"continue": True},
                adapter.handle(
                    self._event(
                        "UserPromptSubmit",
                        prompt="根据材料起草通知。",
                    )
                ),
            )
            self.assertEqual(
                {"continue": True},
                adapter.handle(
                    self._event("Stop", stop_hook_active=False)
                ),
            )

    def test_workbuddy_recovers_first_prompt_when_plugin_hooks_register_late(self):
        with self._host_environment("workbuddy"):
            adapter = self.ADAPTERS["workbuddy"]
            session_id = "late-plugin-session"
            transcript = self.data_root / f"{session_id}.jsonl"
            transcript.write_text(
                json.dumps(
                    {
                        "type": "message",
                        "role": "user",
                        "sessionId": session_id,
                        "content": [
                            {
                                "type": "input_text",
                                "text": "根据材料起草一份450—550字的工作总结。",
                            }
                        ],
                    },
                    ensure_ascii=False,
                )
                + "\n",
                encoding="utf-8",
            )
            plugin_root = self.PLUGIN_ROOTS["workbuddy"]
            read = self._event(
                "PostToolUse",
                session_id=session_id,
                transcript_path=str(transcript),
                tool_name="Read",
                tool_input={
                    "file_path": str(
                        plugin_root / "skills" / "chinese-official-writing" / "SKILL.md"
                    )
                },
                tool_response={"success": True},
            )
            self.assertEqual({"continue": True}, adapter.handle(read))
            result = adapter.handle(
                self._event(
                    "Stop",
                    session_id=session_id,
                    transcript_path=str(transcript),
                    stop_hook_active=False,
                    last_assistant_message="工作总结\n\n本年度完成有关工作。",
                )
            )
            self.assertEqual(False, result.get("continue"))
            turn_id = adapter._active_workbuddy_turn(self.data_root, session_id)
            self.assertTrue(turn_id and turn_id.startswith("workbuddy-1-"))
            core_record = next(
                (self.data_root / "shared-gate-core").rglob(f"{turn_id}.json")
            )
            record = json.loads(core_record.read_text(encoding="utf-8"))
            self.assertEqual(
                "根据材料起草一份450—550字的工作总结。", record.get("request")
            )
            self.assertTrue(record.get("bootstrapped_by_stop"))

    def test_workbuddy_late_registration_rejects_foreign_transcript(self):
        with self._host_environment("workbuddy"):
            adapter = self.ADAPTERS["workbuddy"]
            transcript = self.data_root / "other-session.jsonl"
            transcript.write_text(
                '{"type":"message","role":"user","sessionId":"other-session",'
                '"content":[{"type":"input_text","text":"起草450—550字总结"}]}\n',
                encoding="utf-8",
            )
            result = adapter.handle(
                self._event(
                    "Stop",
                    session_id="expected-session",
                    transcript_path=str(transcript),
                    stop_hook_active=False,
                    last_assistant_message="短稿",
                )
            )
            self.assertEqual({"continue": True}, result)

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
            result = self.ADAPTERS["codex"].handle(
                self._event(
                    "UserPromptSubmit",
                    turn_id="codex-turn-1",
                    prompt="起草通知。",
                )
            )
        self.assertEqual({"continue": True}, result)
        self.assertEqual([], list(self.data_root.rglob("*")))

    def test_static_capability_selection_reaches_protective_observer(self):
        with tempfile.TemporaryDirectory() as temporary:
            for host in ("codex", "workbuddy"):
                with self.subTest(host=host):
                    target = Path(temporary) / host
                    ASSEMBLER.assemble(
                        "codex" if host == "codex" else "codebuddy",
                        target,
                        "protective_expansion",
                    )
                    adapter_path = target / "scripts/host_gate_adapter.py"
                    adapter = load_module(
                        f"cow_{host}_protective_adapter_{id(self)}", adapter_path
                    )
                    previous_root = self.PLUGIN_ROOTS[host]
                    previous_adapter = self.ADAPTERS[host]
                    self.PLUGIN_ROOTS[host] = target
                    self.ADAPTERS[host] = adapter
                    try:
                        result = self._arm_and_stop(host)
                        self.assertIn("观察包如下", result.get("reason", ""))
                    finally:
                        self.PLUGIN_ROOTS[host] = previous_root
                        self.ADAPTERS[host] = previous_adapter

    def test_static_delivery_review_overrides_ambient_protective_capability(self):
        with tempfile.TemporaryDirectory() as temporary:
            for host in ("codex", "workbuddy"):
                with self.subTest(host=host):
                    target = Path(temporary) / host
                    ASSEMBLER.assemble(
                        "codex" if host == "codex" else "codebuddy",
                        target,
                        "delivery_review",
                    )
                    adapter = load_module(
                        f"cow_{host}_ambient_adapter_{id(self)}",
                        target / "scripts/host_gate_adapter.py",
                    )
                    previous_root = self.PLUGIN_ROOTS[host]
                    previous_adapter = self.ADAPTERS[host]
                    self.PLUGIN_ROOTS[host] = target
                    self.ADAPTERS[host] = adapter
                    try:
                        with mock.patch.dict(
                            os.environ,
                            {"COW_GATE_CAPABILITY": "protective_expansion"},
                            clear=False,
                        ):
                            result = self._arm_and_stop(host)
                        self.assertNotIn("观察包如下", result.get("reason", ""))
                    finally:
                        self.PLUGIN_ROOTS[host] = previous_root
                        self.ADAPTERS[host] = previous_adapter


if __name__ == "__main__":
    unittest.main()
