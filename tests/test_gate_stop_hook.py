import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest


MODULE_PATH = (
    Path(__file__).parents[1]
    / "chinese-official-writing"
    / "scripts"
    / "gate_stop_hook.py"
)
HOOK_CONFIG_PATH = Path(__file__).parents[1] / "hooks" / "hooks.json"
SPEC = importlib.util.spec_from_file_location("candidate_ai_gate_stop_hook", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
HOOK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(HOOK)


class GateStopHookTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.old_data = os.environ.get("COW_GATE_HOOK_DATA")
        self.old_plugin_root = os.environ.get("PLUGIN_ROOT")
        os.environ["COW_GATE_HOOK_DATA"] = self.temp.name
        os.environ["PLUGIN_ROOT"] = str(self.root / "plugin")
        self.addCleanup(self._restore_env)
        self.txn = self.root / "txn"
        self.txn.mkdir()
        self.cwd = self.root / "cwd"
        self.cwd.mkdir()

    def _restore_env(self):
        if self.old_data is None:
            os.environ.pop("COW_GATE_HOOK_DATA", None)
        else:
            os.environ["COW_GATE_HOOK_DATA"] = self.old_data
        if self.old_plugin_root is None:
            os.environ.pop("PLUGIN_ROOT", None)
        else:
            os.environ["PLUGIN_ROOT"] = self.old_plugin_root

    def _state(self, name="AWAITING_REPAIR", run_id="run-1"):
        (self.txn / "state.json").write_text(
            json.dumps({"state": name, "run_id": run_id}), encoding="utf-8"
        )

    def _event(self, name, **extra):
        event = {
            "hook_event_name": name,
            "session_id": "session-1",
            "turn_id": "turn-1",
            "cwd": str(self.cwd),
        }
        event.update(extra)
        return event

    def _record_detect(self):
        self._state()
        command = f'python review_gate.py detect --txn "{self.txn}"'
        result = HOOK.handle(
            self._event(
                "PostToolUse",
                tool_input={"cmd": command},
                tool_response={"exit_code": 0},
            )
        )
        self.assertTrue(result["continue"])

    def _record_prompt_and_skill_read(self, prompt="请起草一份情况报告。"):
        HOOK.handle(self._event("UserPromptSubmit", prompt=prompt))
        skill = (
            Path(os.environ["PLUGIN_ROOT"])
            / "skills"
            / "chinese-official-writing"
            / "SKILL.md"
        )
        HOOK.handle(
            self._event(
                "PostToolUse",
                tool_input={"cmd": f'Get-Content "{skill}"'},
                tool_response={"exit_code": 0},
            )
        )

    def test_non_gate_tool_does_not_arm(self):
        result = HOOK.handle(
            self._event("PostToolUse", tool_input={"cmd": "git status"})
        )
        self.assertTrue(result["continue"])
        self.assertTrue(HOOK.handle(self._event("Stop"))["continue"])

    def test_stop_bootstraps_detect_after_real_skill_read(self):
        self._record_prompt_and_skill_read()
        result = HOOK.handle(
            self._event(
                "Stop",
                stop_hook_active=False,
                last_assistant_message="情况报告\n\n测试工作已完成。",
            )
        )
        self.assertEqual("block", result["decision"])
        self.assertIn("Hook 完成 emit", result["reason"])
        record = HOOK._read_json(HOOK._record_path(self._event("Stop")))
        self.assertIsNotNone(record)
        self.assertTrue(record["bootstrapped_by_stop"])
        self.assertEqual("emit", record["last_action"])
        txn = Path(record["txn"])
        state = HOOK._read_json(txn / "state.json")
        self.assertEqual("TERMINAL_D0", state["state"])
        self.assertEqual(
            "情况报告\n\n测试工作已完成。",
            (txn / "d0.snapshot.txt").read_text(encoding="utf-8"),
        )

    def test_stop_does_not_bootstrap_when_skill_was_not_read(self):
        HOOK.handle(self._event("UserPromptSubmit", prompt="请起草一份情况报告。"))
        result = HOOK.handle(
            self._event(
                "Stop",
                stop_hook_active=False,
                last_assistant_message="情况报告\n\n测试工作已完成。",
            )
        )
        self.assertTrue(result["continue"])

    def test_continuation_prompt_does_not_replace_original_request(self):
        self._record_prompt_and_skill_read("原始公文任务")
        HOOK.handle(self._event("UserPromptSubmit", prompt="仅调用 emit"))
        record = HOOK._read_json(HOOK._record_path(self._event("Stop")))
        self.assertEqual("原始公文任务", record["request"])

    def test_failed_gate_call_does_not_arm(self):
        self._state()
        command = f'python review_gate.py detect --txn "{self.txn}"'
        HOOK.handle(
            self._event(
                "PostToolUse",
                tool_input={"cmd": command},
                tool_response={"exit_code": 1},
            )
        )
        self.assertTrue(HOOK.handle(self._event("Stop"))["continue"])

    def test_unfinished_transaction_requests_one_repair_packet(self):
        self._record_prompt_and_skill_read()
        first = HOOK.handle(
            self._event(
                "Stop",
                stop_hook_active=False,
                last_assistant_message="现有情况尚不能据此形成采购结论。",
            )
        )
        self.assertEqual("block", first["decision"])
        self.assertIn("只输出一个 JSON 对象", first["reason"])
        record = HOOK._read_json(HOOK._record_path(self._event("Stop")))
        self.assertEqual("awaiting_repair", record["hook_phase"])

    def test_terminal_is_emitted_by_hook_and_exact_echo_allows(self):
        self._record_prompt_and_skill_read()
        draft = "情况报告\n\n测试工作已完成。"
        first = HOOK.handle(
            self._event(
                "Stop", stop_hook_active=False, last_assistant_message=draft
            )
        )
        self.assertEqual("block", first["decision"])
        self.assertIn("Hook 完成 emit", first["reason"])
        second = HOOK.handle(
            self._event("Stop", stop_hook_active=True, last_assistant_message=draft)
        )
        self.assertTrue(second["continue"])
        record = HOOK._read_json(HOOK._record_path(self._event("Stop")))
        self.assertTrue(record["emit_seen"])
        self.assertTrue(record["delivery_verified"])

    def test_hook_drives_one_repair_finalize_and_emit_without_agent_tool_call(self):
        self._record_prompt_and_skill_read()
        first = HOOK.handle(
            self._event(
                "Stop",
                stop_hook_active=False,
                last_assistant_message=(
                    "关于设备采购情况的报告\n\n"
                    "尚不能据此形成采购结论。"
                ),
            )
        )
        self.assertEqual("block", first["decision"])
        repair_text = first["reason"].split("响应骨架如下：\n", 1)[1].split(
            "\n检测包如下：\n", 1
        )[0]
        repair = json.loads(repair_text)
        self.assertEqual(1, len(repair["repairs"]))
        self.assertIsNone(repair["repairs"][0]["decision"])
        self.assertIsNone(repair["repairs"][0]["replacement"])
        self.assertIn("null 不是默认答案", first["reason"])
        self.assertIn("无需与原句等长", first["reason"])
        self.assertIn("避免复述上下文已有事实", first["reason"])
        self.assertIn("不扩展方法", first["reason"])
        self.assertIn("不把未确定事项改成新的研究承诺", first["reason"])
        self.assertIn("确需原样保留时选择 KEEP", first["reason"])
        repair["repairs"][0]["decision"] = "REWRITE"
        repair["repairs"][0]["replacement"] = "采购结论正在研究中。"

        second = HOOK.handle(
            self._event(
                "Stop",
                stop_hook_active=True,
                last_assistant_message=json.dumps(repair, ensure_ascii=False),
            )
        )
        self.assertEqual("block", second["decision"])
        self.assertIn("只读核验", second["reason"])
        self.assertIn("以 D0 为比较基准", second["reason"])
        self.assertIn("视为未决状态保留", second["reason"])
        verdict_text = second["reason"].split("响应骨架如下：\n", 1)[1].split(
            "\n核验包如下：\n", 1
        )[0]
        verdict = json.loads(verdict_text)

        third = HOOK.handle(
            self._event(
                "Stop",
                stop_hook_active=True,
                last_assistant_message=json.dumps(verdict, ensure_ascii=False),
            )
        )
        self.assertEqual("block", third["decision"])
        self.assertIn("Hook 完成 emit", third["reason"])
        selected = third["reason"].split("不要加说明：\n", 1)[1]
        self.assertEqual("关于设备采购情况的报告\n\n采购结论正在研究中。", selected)

        fourth = HOOK.handle(
            self._event(
                "Stop", stop_hook_active=True, last_assistant_message=selected
            )
        )
        self.assertTrue(fourth["continue"])
        record = HOOK._read_json(HOOK._record_path(self._event("Stop")))
        self.assertTrue(record["delivery_verified"])

    def test_terminal_d0_with_emit_allows(self):
        self._record_detect()
        self._state("TERMINAL_D0")
        command = f'python review_gate.py emit --txn "{self.txn}"'
        HOOK.handle(
            self._event(
                "PostToolUse",
                tool_input={"cmd": command},
                tool_response={"exit_code": 0},
            )
        )
        self.assertTrue(HOOK.handle(self._event("Stop"))["continue"])

    def test_terminal_d1_with_emit_allows(self):
        self._record_detect()
        self._state("TERMINAL_D1")
        command = f'python review_gate.py emit --txn "{self.txn}"'
        HOOK.handle(
            self._event(
                "PostToolUse",
                tool_input={"command": command},
                tool_result={"exit_code": 0},
            )
        )
        self.assertTrue(HOOK.handle(self._event("Stop"))["continue"])

    def test_relative_transaction_path_is_bound_to_cwd(self):
        txn = self.cwd / "relative-txn"
        txn.mkdir()
        (txn / "state.json").write_text(
            json.dumps({"state": "AWAITING_REPAIR", "run_id": "relative"}),
            encoding="utf-8",
        )
        command = "python review_gate.py detect --txn relative-txn"
        HOOK.handle(self._event("PostToolUse", tool_input={"cmd": command}))
        result = HOOK.handle(self._event("Stop"))
        self.assertTrue(result["continue"])

    def test_corrupt_or_mismatched_state_fails_open(self):
        self._record_detect()
        (self.txn / "state.json").write_text("{broken", encoding="utf-8")
        self.assertTrue(HOOK.handle(self._event("Stop"))["continue"])
        self._state(run_id="different")
        self.assertTrue(HOOK.handle(self._event("Stop"))["continue"])

    def test_missing_plugin_data_fails_open(self):
        os.environ.pop("COW_GATE_HOOK_DATA", None)
        os.environ.pop("PLUGIN_DATA", None)
        self.assertTrue(HOOK.handle(self._event("Stop"))["continue"])

    def test_windows_hook_reads_plugin_root_without_shell_expansion(self):
        config = json.loads(HOOK_CONFIG_PATH.read_text(encoding="utf-8"))
        commands = [
            handler["commandWindows"]
            for groups in config["hooks"].values()
            for group in groups
            for handler in group["hooks"]
        ]
        self.assertTrue(commands)
        self.assertTrue(all("os.environ['PLUGIN_ROOT']" in command for command in commands))
        self.assertTrue(all("%PLUGIN_ROOT%" not in command for command in commands))
        self.assertTrue(all("$env:PLUGIN_ROOT" not in command for command in commands))


if __name__ == "__main__":
    unittest.main()
