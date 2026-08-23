from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
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


class KimiGateAdapterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.adapter_root = self.root / "kimi-code"
        ASSEMBLER.assemble("kimi-code", self.adapter_root, "delivery_cleanliness")
        self.adapter = load_module(
            f"cow_kimi_gate_adapter_{id(self)}",
            self.adapter_root / "scripts" / "gate_stop_hook.py",
        )
        self.kimi_home = self.root / "kimi-home"
        self.session_id = "session-kimi-1"
        self.sessions_root = self.kimi_home / "sessions"
        self.session_dir = self.sessions_root / "workspace" / self.session_id
        self.wire = self.session_dir / "agents" / "main" / "wire.jsonl"
        self.wire.parent.mkdir(parents=True)
        self._append_step("old-step", "旧会话正文")
        self.kimi_home.mkdir(exist_ok=True)
        (self.kimi_home / "session_index.jsonl").write_text(
            json.dumps(
                {
                    "sessionId": self.session_id,
                    "sessionDir": str(self.session_dir),
                    "workDir": str(ROOT),
                },
                ensure_ascii=False,
            )
            + "\n",
            encoding="utf-8",
        )
        self.old_environment = {
            key: os.environ.get(key)
            for key in ("KIMI_PLUGIN_ROOT", "KIMI_CODE_HOME")
        }
        os.environ["KIMI_PLUGIN_ROOT"] = str(self.adapter_root.resolve())
        os.environ["KIMI_CODE_HOME"] = str(self.kimi_home.resolve())
        self.addCleanup(self._restore_environment)

    def _restore_environment(self) -> None:
        for key, value in self.old_environment.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

    def _append_records(self, records: list[dict]) -> None:
        with self.wire.open("a", encoding="utf-8", newline="\n") as handle:
            for record in records:
                json.dump(record, handle, ensure_ascii=False, separators=(",", ":"))
                handle.write("\n")

    def _append_step(self, step: str, text: str) -> None:
        self._append_records(
            [
                {
                    "type": "context.append_loop_event",
                    "event": {"type": "step.begin", "stepUuid": step},
                },
                {
                    "type": "context.append_loop_event",
                    "event": {
                        "type": "content.part",
                        "stepUuid": step,
                        "part": {"type": "text", "text": text},
                    },
                },
                {
                    "type": "context.append_loop_event",
                    "event": {
                        "type": "step.end",
                        "stepUuid": step,
                        "finishReason": "end_turn",
                    },
                },
            ]
        )

    def _event(self, name: str, **extra):
        event = {
            "hook_event_name": name,
            "session_id": self.session_id,
            "cwd": str(ROOT),
        }
        event.update(extra)
        return event

    def test_native_plugin_manifest_uses_inline_hooks(self) -> None:
        manifests = [
            path.relative_to(self.adapter_root).as_posix()
            for path in self.adapter_root.rglob("*")
            if path.is_file()
            and path.name in {"plugin.json", "qwen-extension.json", "kimi.plugin.json"}
        ]
        self.assertEqual(["kimi.plugin.json"], manifests)
        self.assertFalse((self.adapter_root / "hooks/hooks.json").exists())
        manifest = json.loads(
            (self.adapter_root / "kimi.plugin.json").read_text(encoding="utf-8")
        )
        self.assertEqual("./skills/", manifest["skills"])
        hooks = {hook["event"]: hook for hook in manifest["hooks"]}
        self.assertEqual({"UserPromptSubmit", "PostToolUse", "Stop"}, set(hooks))
        self.assertEqual("^(Skill|Read|ReadFile|Bash)$", hooks["PostToolUse"]["matcher"])
        self.assertEqual(10, hooks["UserPromptSubmit"]["timeout"])
        self.assertEqual(10, hooks["PostToolUse"]["timeout"])
        self.assertEqual(30, hooks["Stop"]["timeout"])

    def test_exact_current_wire_d0_reaches_first_stop_block(self) -> None:
        prompt = "请起草一份情况报告，只输出正文。"
        started = self.adapter.handle(
            self._event(
                "UserPromptSubmit",
                prompt=[{"type": "text", "text": prompt}],
            )
        )
        self.assertEqual({}, started)
        skill = self.adapter.handle(
            self._event(
                "PostToolUse",
                tool_name="Skill",
                tool_input={"skill": "chinese-official-writing"},
                tool_output="Skill loaded inline.",
            )
        )
        self.assertEqual({}, skill)

        body = "情况报告\n\n测试工作已完成。"
        self._append_step("current-step", f"<think>内部推理</think>\n{body}")
        stopped = self.adapter.handle(
            self._event("Stop", stop_hook_active=False)
        )
        output = stopped["hookSpecificOutput"]
        self.assertEqual("deny", output["permissionDecision"])
        self.assertTrue(output["permissionDecisionReason"])

        data_root = self.kimi_home / self.adapter.PLUGIN_DATA_DIRECTORY
        records = list((data_root / self.adapter.CORE_DATA_DIRECTORY).rglob("*.json"))
        self.assertEqual(1, len(records))
        record = json.loads(records[0].read_text(encoding="utf-8"))
        self.assertTrue(record["skill_seen"])
        self.assertEqual(body, record["delivery_cleanliness"]["original"])
        self.assertEqual(
            "delivery_cleanliness_awaiting_revision",
            record["delivery_cleanliness"]["phase"],
        )

    def test_allow_path_writes_no_stdout(self) -> None:
        event = self._event("Unknown")
        environment = os.environ.copy()
        result = subprocess.run(
            [sys.executable, str(self.adapter_root / "scripts/gate_stop_hook.py")],
            input=json.dumps(event, ensure_ascii=False),
            text=True,
            capture_output=True,
            env=environment,
            check=False,
        )
        self.assertEqual(0, result.returncode)
        self.assertEqual("", result.stdout)
        self.assertEqual("", result.stderr)

    def test_session_index_cannot_escape_kimi_sessions_root(self) -> None:
        outside = self.root / self.session_id
        (outside / "agents/main").mkdir(parents=True)
        (outside / "agents/main/wire.jsonl").write_text("", encoding="utf-8")
        with (self.kimi_home / "session_index.jsonl").open(
            "a", encoding="utf-8", newline="\n"
        ) as handle:
            json.dump(
                {"sessionId": self.session_id, "sessionDir": str(outside)},
                handle,
            )
            handle.write("\n")
        self.assertIsNone(self.adapter._session_wire(self.kimi_home, self.session_id))

    def test_current_session_is_found_in_a_bounded_index_tail(self) -> None:
        self.adapter.MAX_SESSION_INDEX_TAIL_BYTES = 512
        current = json.dumps(
            {"sessionId": self.session_id, "sessionDir": str(self.session_dir)}
        )
        (self.kimi_home / "session_index.jsonl").write_text(
            ("old-entry\n" * 100) + current + "\n",
            encoding="utf-8",
        )
        self.assertEqual(
            self.wire.resolve(),
            self.adapter._session_wire(self.kimi_home, self.session_id),
        )


if __name__ == "__main__":
    unittest.main()
