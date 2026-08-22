import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "chinese-official-writing" / "hooks" / "core" / "gate_stop_hook.py"
HOOK_CONFIG_PATH = ROOT / "chinese-official-writing" / "hooks" / "adapters" / "codex" / "hooks.json"
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

    def _record_prompt_and_skill_read(self, prompt="请起草一份情况报告。", **common):
        HOOK.handle(self._event("UserPromptSubmit", prompt=prompt, **common))
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
                **common,
            )
        )

    def test_non_gate_tool_does_not_arm(self):
        result = HOOK.handle(
            self._event("PostToolUse", tool_input={"cmd": "git status"})
        )
        self.assertTrue(result["continue"])
        self.assertTrue(HOOK.handle(self._event("Stop"))["continue"])

    def test_co_located_skill_root_is_recognized_for_flat_packages(self):
        skill = MODULE_PATH.parents[1] / "SKILL.md"
        self.assertTrue(HOOK._reads_this_skill(f'Get-Content "{skill}"'))
        self.assertFalse(HOOK._reads_this_skill('Get-Content "C:/other/SKILL.md"'))

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

    def test_terminal_delivery_redacts_raw_turn_data_and_transaction(self):
        draft = "情况报告\n\n测试工作已完成。"
        self._record_prompt_and_skill_read()
        first = HOOK.handle(
            self._event(
                "Stop",
                stop_hook_active=False,
                last_assistant_message=draft,
            )
        )
        self.assertEqual("block", first["decision"])
        record_path = HOOK._record_path(self._event("Stop"))
        self.assertIsNotNone(record_path)
        record = HOOK._read_json(record_path)
        self.assertIsNotNone(record)
        txn = Path(record["txn"])
        inputs = txn.parent / f"{txn.name}-inputs"
        self.assertTrue(txn.is_dir())
        self.assertTrue(inputs.is_dir())

        final = HOOK.handle(
            self._event("Stop", last_assistant_message=draft)
        )
        self.assertEqual({"continue": True}, final)
        redacted = HOOK._read_json(record_path)
        self.assertIsNotNone(redacted)
        self.assertEqual(HOOK.REDACTED_RECORD_STATE, redacted["data_retention_state"])
        self.assertEqual(0, redacted["raw_artifact_delete_failures"])
        self.assertNotIn("request", redacted)
        self.assertNotIn("txn", redacted)
        serialized = json.dumps(redacted, ensure_ascii=False)
        self.assertNotIn("请起草一份情况报告", serialized)
        self.assertNotIn("测试工作已完成", serialized)
        self.assertFalse(txn.exists())
        self.assertFalse(inputs.exists())
        self.assertFalse(HOOK._skill_seen_marker_path(record_path).exists())

        duplicate = HOOK.handle(
            self._event("Stop", last_assistant_message=draft)
        )
        self.assertEqual({"continue": True}, duplicate)

    def test_skill_read_marker_survives_concurrent_material_record_overwrite(self):
        self._record_prompt_and_skill_read()
        record_path = HOOK._record_path(self._event("Stop"))
        self.assertIsNotNone(record_path)
        record = HOOK._read_json(record_path)
        self.assertIsNotNone(record)
        self.assertTrue(HOOK._skill_seen_marker_path(record_path).is_file())

        stale_material_record = dict(record)
        stale_material_record["skill_seen"] = False
        stale_material_record["external_material_read"] = True
        HOOK._atomic_write(record_path, stale_material_record)

        result = HOOK.handle(
            self._event(
                "Stop",
                stop_hook_active=False,
                last_assistant_message="情况报告\n\n测试工作已完成。",
            )
        )
        self.assertEqual("block", result["decision"])
        recovered = HOOK._read_json(record_path)
        self.assertTrue(recovered["skill_seen"])
        self.assertTrue(recovered["external_material_read"])

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
        record = HOOK._read_json(HOOK._record_path(self._event("Stop")))
        self.assertEqual(HOOK.REDACTED_RECORD_STATE, record["data_retention_state"])
        self.assertNotIn("request", record)

    def test_review_only_requests_allow_nonempty_review_without_transaction(self):
        prompts = (
            "只审查这份采购申请，列出问题和建议。",
            "只复核这份通知的格式和语气。",
            "请审查这份报告，不要代改。",
            "请检查这份请示，不重写全文。",
            "只审不改这份采购申请。",
            "仅审不改这份通知。",
            "只检查不修改正文，列出问题。",
            "请只读审核这份材料，列出问题。",
            "帮我审核一下这份稿子。",
            "请审一下稿，看看哪里有问题。",
            "请进入审稿模式看看这份报告。",
            "帮我看看这段稿子哪里有问题。",
            (
                "帮我看看下面这段稿子哪里有问题，按位置、问题、建议给我审核意见，"
                "不要替我改正文。"
            ),
        )
        review = "审查意见：结尾表述“尚不能据此形成采购结论”较空泛，建议说明当前未决事项。"
        skill = (
            Path(os.environ["PLUGIN_ROOT"])
            / "skills"
            / "chinese-official-writing"
            / "SKILL.md"
        )
        for index, prompt in enumerate(prompts, start=1):
            with self.subTest(prompt=prompt):
                common = {"turn_id": f"review-{index}"}
                HOOK.handle(self._event("UserPromptSubmit", prompt=prompt, **common))
                HOOK.handle(
                    self._event(
                        "PostToolUse",
                        tool_input={"cmd": f'Get-Content "{skill}"'},
                        tool_response={"exit_code": 0},
                        **common,
                    )
                )
                result = HOOK.handle(
                    self._event(
                        "Stop",
                        stop_hook_active=False,
                        last_assistant_message=review,
                        **common,
                    )
                )
                self.assertTrue(result["continue"])
                record = HOOK._read_json(HOOK._record_path(self._event("Stop", **common)))
                self.assertIsNotNone(record)
                self.assertNotIn("txn", record)
                self.assertNotIn("request", record)
                self.assertEqual(
                    HOOK.REDACTED_RECORD_STATE, record["data_retention_state"]
                )

        transactions = self.root / "candidate-ai-gate-hook" / "transactions"
        self.assertFalse(transactions.exists())

    def test_review_only_short_form_does_not_bypass_followup_writing_or_quoted_material(self):
        prompts = (
            "只审不改后按建议改写这份报告。",
            "请先审再改这份报告。",
            "请审完改写这份报告。",
            "这不是只审不改，请输出修改后的正文。",
            "请起草通知，材料中写有“只审不改”四字。",
            "帮我审核后直接改好这份报告。",
            "审核并优化这份通知。",
            "帮我看看哪里有问题，之后整理成正式稿。",
            "帮我审核这份材料，写份通知。",
            "这次不是审稿，是修改。",
            "请起草通知，材料中写有“帮我审核这段稿子哪里有问题”。",
        )
        for index, prompt in enumerate(prompts, start=1):
            with self.subTest(prompt=prompt):
                common = {"turn_id": f"review-followup-{index}"}
                self._record_prompt_and_skill_read(prompt, **common)
                result = HOOK.handle(
                    self._event(
                        "Stop",
                        stop_hook_active=False,
                        last_assistant_message="关于有关事项的报告\n\n情况正在办理。",
                        **common,
                    )
                )
                self.assertEqual("block", result["decision"])
                record = HOOK._read_json(HOOK._record_path(self._event("Stop", **common)))
                self.assertIn("txn", record)

    def test_explicit_task_hook_opt_out_allows_without_transaction(self):
        prompts = (
            "请关闭 Hook，按普通 Skill 起草一份通知。",
            "本次不要用hooks，直接完成情况报告。",
            "这次跳过交付门禁，修改后只输出正文。",
        )
        for index, prompt in enumerate(prompts, start=1):
            with self.subTest(prompt=prompt):
                common = {"turn_id": f"opt-out-{index}"}
                self._record_prompt_and_skill_read(prompt, **common)
                result = HOOK.handle(
                    self._event(
                        "Stop",
                        stop_hook_active=False,
                        last_assistant_message="关于有关事项的通知\n\n请按要求办理。",
                        **common,
                    )
                )
                self.assertTrue(result["continue"])
                record = HOOK._read_json(
                    HOOK._record_path(self._event("Stop", **common))
                )
                self.assertIsNotNone(record)
                self.assertEqual("user_requested", record["bypass"])
                self.assertNotIn("txn", record)
                self.assertNotIn("request", record)
                self.assertEqual(
                    HOOK.REDACTED_RECORD_STATE, record["data_retention_state"]
                )

    def test_redaction_never_deletes_transaction_outside_plugin_data_root(self):
        outside = self.root / "outside-transaction"
        outside.mkdir()
        (outside / "draft.txt").write_text("不得删除", encoding="utf-8")
        record_path = HOOK._record_path(self._event("Stop", turn_id="outside"))
        self.assertIsNotNone(record_path)
        record = {
            "schema_version": 1,
            "request": "敏感请求",
            "txn": str(outside.resolve()),
            "hook_phase": "complete",
        }
        HOOK._atomic_write(record_path, record)

        response = HOOK._finish_stop_response(record_path, record, {"continue": True})

        self.assertEqual({"continue": True}, response)
        self.assertTrue((outside / "draft.txt").is_file())
        redacted = HOOK._read_json(record_path)
        self.assertNotIn("request", redacted)
        self.assertNotIn("txn", redacted)

    def test_redaction_write_failure_removes_exact_raw_record(self):
        record_path = HOOK._record_path(self._event("Stop", turn_id="write-failure"))
        self.assertIsNotNone(record_path)
        record = {
            "schema_version": 1,
            "request": "敏感请求",
            "hook_phase": "complete",
        }
        HOOK._atomic_write(record_path, record)

        with mock.patch.object(
            HOOK, "_atomic_write", side_effect=OSError("write denied")
        ):
            response = HOOK._finish_stop_response(
                record_path, record, {"continue": True}
            )

        self.assertEqual({"continue": True}, response)
        self.assertFalse(record_path.exists())

    def test_hook_opt_out_does_not_match_negated_or_generic_instructions(self):
        for prompt in (
            "不要关闭 Hook，请继续使用 Hook 起草通知。",
            "请保持交付门禁启用并起草通知。",
            "请起草通知，不要用脚本。",
            "请起草通知，不要过度复核。",
        ):
            with self.subTest(prompt=prompt):
                self.assertFalse(HOOK._requests_hook_opt_out(prompt))

    def test_drafting_revision_and_review_then_rewrite_still_bootstrap(self):
        prompts = (
            "请起草一份情况报告。",
            "请起草一份检查报告，只检查设备运行情况。",
            "请修改这份采购申请并输出改后正文。",
            "请先只复核这份通知，再按建议改写全文。",
        )
        skill = (
            Path(os.environ["PLUGIN_ROOT"])
            / "skills"
            / "chinese-official-writing"
            / "SKILL.md"
        )
        for index, prompt in enumerate(prompts, start=1):
            with self.subTest(prompt=prompt):
                common = {"turn_id": f"draft-{index}"}
                HOOK.handle(self._event("UserPromptSubmit", prompt=prompt, **common))
                HOOK.handle(
                    self._event(
                        "PostToolUse",
                        tool_input={"cmd": f'Get-Content "{skill}"'},
                        tool_response={"exit_code": 0},
                        **common,
                    )
                )
                result = HOOK.handle(
                    self._event(
                        "Stop",
                        stop_hook_active=False,
                        last_assistant_message="关于设备采购情况的报告\n\n尚不能据此形成采购结论。",
                        **common,
                    )
                )
                self.assertEqual("block", result["decision"])
                record = HOOK._read_json(HOOK._record_path(self._event("Stop", **common)))
                self.assertIsNotNone(record)
                self.assertIn("txn", record)

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

    def test_mismatched_terminal_echo_requests_the_same_selected_output(self):
        self._record_prompt_and_skill_read()
        draft = "情况报告\n\n测试工作已完成。"
        first = HOOK.handle(
            self._event(
                "Stop", stop_hook_active=False, last_assistant_message=draft
            )
        )
        self.assertEqual("block", first["decision"])
        selected = first["reason"].split("不要加说明：\n", 1)[1]

        second = HOOK.handle(
            self._event(
                "Stop", stop_hook_active=True, last_assistant_message="错误回显"
            )
        )
        self.assertEqual("block", second["decision"])
        self.assertEqual(selected, second["reason"].split("不要加说明：\n", 1)[1])

        third = HOOK.handle(
            self._event(
                "Stop", stop_hook_active=True, last_assistant_message=selected
            )
        )
        self.assertTrue(third["continue"])
        record = HOOK._read_json(HOOK._record_path(self._event("Stop")))
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
        self.assertIn("保持材料已有的事实和判断强度", first["reason"])
        self.assertNotIn("调查、核查等进行态", first["reason"])
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
        self.assertNotIn("视为未决状态保留", second["reason"])
        self.assertNotIn("不计为新增动作", second["reason"])
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
