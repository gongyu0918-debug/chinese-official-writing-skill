import errno
import importlib.util
import itertools
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
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

    def _assert_gate_root_omits(self, *needles):
        data_root = HOOK._data_root()
        self.assertIsNotNone(data_root)
        leaks = []
        for path in data_root.rglob("*"):
            if not path.is_file():
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeError):
                continue
            if any(needle in text for needle in needles):
                leaks.append(path.relative_to(data_root).as_posix())
        self.assertEqual([], leaks)

    def test_non_gate_tool_does_not_arm(self):
        result = HOOK.handle(
            self._event("PostToolUse", tool_input={"cmd": "git status"})
        )
        self.assertTrue(result["continue"])
        self.assertTrue(HOOK.handle(self._event("Stop"))["continue"])

    def test_host_abort_redacts_one_exact_pending_turn(self):
        request = "敏感的待处理写稿请求"
        self._record_prompt_and_skill_read(request)
        record_path = HOOK._record_path(self._event("HostAbort"))
        self.assertIsNotNone(record_path)
        self.assertIn(request, record_path.read_text(encoding="utf-8"))

        result = HOOK.handle(
            self._event("HostAbort", abort_reason="turn_changed")
        )

        self.assertTrue(result["continue"])
        record = json.loads(record_path.read_text(encoding="utf-8"))
        self.assertEqual("raw_turn_data_redacted", record["data_retention_state"])
        self.assertEqual("turn_changed", record["host_abort_reason"])
        self.assertEqual("failed_open_host_abort", record["hook_phase"])
        self._assert_gate_root_omits(request)

    def test_host_abort_during_bootstrap_input_write_cleans_after_owner_exits(self):
        request = "请起草包含内部编号HK008-CANCEL的情况报告。"
        draft = "情况报告\n\n内部编号HK008-CANCEL已完成核验。"
        self._record_prompt_and_skill_read(request)
        record_path = HOOK._record_path(self._event("Stop"))
        entered, resume = threading.Event(), threading.Event()
        original_write = HOOK._atomic_write_text
        results, errors = [], []

        def paused_write(path, text):
            if not entered.is_set():
                entered.set()
                if not resume.wait(5):
                    raise RuntimeError("bootstrap test scheduler timed out")
            return original_write(path, text)

        def bootstrap():
            try:
                results.append(HOOK.handle(self._event("Stop", last_assistant_message=draft)))
            except BaseException as exc:
                errors.append(exc)

        with mock.patch.object(HOOK, "_atomic_write_text", side_effect=paused_write), \
                mock.patch.object(HOOK, "RECORD_LOCK_TIMEOUT_SECONDS", 0.03), \
                mock.patch.object(HOOK, "_run_review_gate_subprocess", wraps=HOOK._run_review_gate_subprocess) as detect:
            worker = threading.Thread(target=bootstrap)
            worker.start()
            self.assertTrue(entered.wait(5))
            try:
                response = HOOK.handle(self._event("HostAbort", abort_reason="turn_changed"))
                self.assertEqual({"continue": True}, response)
                self.assertTrue(HOOK._host_abort_marker_path(record_path).is_file())
                self.assertNotEqual(HOOK.REDACTED_RECORD_STATE, HOOK._read_json(record_path).get("data_retention_state"))
            finally:
                resume.set()
                worker.join(10)
            self.assertFalse(worker.is_alive())
            self.assertEqual([], errors)
            detect.assert_not_called()
        self.assertEqual([{"continue": True}], results)
        record = HOOK._read_json(record_path)
        self.assertEqual(HOOK.REDACTED_RECORD_STATE, record["data_retention_state"])
        self.assertEqual("turn_changed", record["host_abort_reason"])
        self.assertEqual(0, record["raw_artifact_delete_failures"])
        self.assertFalse(HOOK._host_abort_marker_path(record_path).exists())
        self._assert_gate_root_omits(request, draft, "HK008-CANCEL")

    def test_host_abort_state_lock_failure_is_consumed_by_later_turn_event(self):
        request = "请起草包含内部编号HK008-RETRY的情况报告。"
        self._record_prompt_and_skill_read(request)
        record_path = HOOK._record_path(self._event("HostAbort"))
        other_turn = HOOK._record_path(self._event("Stop", turn_id="other-turn"))
        HOOK._atomic_write(other_turn, {"request": "另一任务原文"})
        with HOOK._record_lock(record_path), mock.patch.object(HOOK, "RECORD_LOCK_TIMEOUT_SECONDS", 0.03):
            response = HOOK.handle(self._event("HostAbort", abort_reason="turn_changed"))
        self.assertEqual({"continue": True}, response)
        self.assertEqual(request, HOOK._read_json(record_path)["request"])
        self.assertEqual("turn_changed", HOOK._pending_host_abort(record_path))
        response = HOOK.handle(self._event("PostToolUse", tool_input={"cmd": "Get-Content late.txt"}, tool_response={"exit_code": 0}))
        self.assertEqual({"continue": True}, response)
        self.assertEqual(HOOK.REDACTED_RECORD_STATE, HOOK._read_json(record_path)["data_retention_state"])
        self.assertFalse(HOOK._host_abort_marker_path(record_path).exists())
        self.assertEqual({"request": "另一任务原文"}, HOOK._read_json(other_turn))
        self._assert_gate_root_omits(request, "HK008-RETRY")

    def test_host_abort_lock_io_error_recovers_on_stop_without_new_emit(self):
        request = "请起草包含内部编号HK008-IO的情况报告。"
        self._record_prompt_and_skill_read(request)
        record_path = HOOK._record_path(self._event("HostAbort"))
        with mock.patch.object(HOOK, "_acquire_file_lock", side_effect=OSError(errno.EIO, "lock I/O")):
            response = HOOK.handle(self._event("HostAbort", abort_reason="host_ceiling"))
        self.assertEqual({"continue": True}, response)
        self.assertEqual(request, HOOK._read_json(record_path)["request"])
        self.assertEqual("host_ceiling", HOOK._pending_host_abort(record_path))
        with mock.patch.object(HOOK, "_run_review_gate_subprocess", wraps=HOOK._run_review_gate_subprocess) as gate:
            response = HOOK.handle(self._event("Stop", last_assistant_message="情况报告\n\n内部编号HK008-IO。"))
            gate.assert_not_called()
        self.assertEqual({"continue": True}, response)
        self.assertEqual(HOOK.REDACTED_RECORD_STATE, HOOK._read_json(record_path)["data_retention_state"])
        self._assert_gate_root_omits(request, "HK008-IO")

    def test_redacted_stop_retries_exact_late_bootstrap_paths(self):
        self._record_prompt_and_skill_read("请起草内部编号HK008-ORPHAN的情况报告。")
        HOOK.handle(self._event("Stop", last_assistant_message="情况报告\n\n内部编号HK008-ORPHAN。"))
        HOOK.handle(self._event("HostAbort", abort_reason="turn_changed"))
        record_path = HOOK._record_path(self._event("Stop"))
        self.assertTrue(HOOK._read_json(record_path)["bootstrap_artifacts"])
        txn = HOOK._data_root() / "transactions" / record_path.parent.name / record_path.stem
        inputs = txn.parent / f"{txn.name}-inputs"
        txn.mkdir(parents=True)
        inputs.mkdir()
        (txn / "late.txt").write_text("HK008-ORPHAN原文", encoding="utf-8")
        (inputs / "draft.txt").write_text("HK008-ORPHAN原稿", encoding="utf-8")
        other = txn.parent / "other-turn-inputs"
        other.mkdir()
        (other / "draft.txt").write_text("其他任务原稿", encoding="utf-8")
        response = HOOK.handle(self._event("Stop", last_assistant_message="HK008-ORPHAN原稿"))
        self.assertEqual({"continue": True}, response)
        self.assertFalse(txn.exists())
        self.assertFalse(inputs.exists())
        self.assertEqual("其他任务原稿", (other / "draft.txt").read_text(encoding="utf-8"))
        self._assert_gate_root_omits("HK008-ORPHAN")

    def test_late_host_abort_and_stop_preserve_unverified_terminal(self):
        record_path = HOOK._record_path(self._event("Stop"))
        record = {
            "hook_phase": "failed_bounded",
            "failure_reason": "hook_selected_output_echo_budget_exhausted",
            "delivery_verified": False,
        }
        HOOK._atomic_write(record_path, record)
        self.assertFalse(HOOK.handle(self._event("HostAbort", abort_reason="turn_changed"))["continue"])
        self.assertEqual("failed_bounded", HOOK._read_json(record_path)["hook_phase"])
        before = record_path.read_bytes()
        for event in (
            self._event("HostAbort", abort_reason="turn_changed"),
            self._event("Stop"),
            self._event("Stop"),
        ):
            self.assertFalse(HOOK.handle(event)["continue"])
            self.assertEqual(before, record_path.read_bytes())

    def test_redacted_failure_receipt_survives_stop_or_abort_refresh_error(self):
        for trigger in ("Stop", "HostAbort"):
            with self.subTest(trigger=trigger):
                event = self._event(trigger, turn_id=f"refresh-{trigger}", abort_reason="turn_changed")
                record_path = HOOK._record_path(event)
                HOOK._atomic_write(record_path, {
                    "data_retention_state": HOOK.REDACTED_RECORD_STATE,
                    "raw_artifact_delete_failures": 0,
                    "hook_phase": "failed_bounded",
                    "failure_reason": "hook_selected_output_echo_budget_exhausted",
                    "delivery_verified": False,
                })
                before = record_path.read_bytes()
                with mock.patch.object(HOOK.os, "replace", side_effect=OSError("one receipt refresh failure")):
                    self.assertFalse(HOOK.handle(event)["continue"])
                self.assertEqual(before, record_path.read_bytes())
                self.assertFalse(HOOK.handle({**event, "hook_event_name": "Stop"})["continue"])
                self.assertEqual(before, record_path.read_bytes())

    def test_unbootstrapped_abort_does_not_own_neighbor_turn_transaction(self):
        draft = "情况报告\n\n测试工作已完成。"
        self._record_prompt_and_skill_read(turn_id="t-inputs")
        first = HOOK.handle(self._event("Stop", turn_id="t-inputs", last_assistant_message=draft))
        self.assertEqual("block", first["decision"])
        other_record_path = HOOK._record_path(self._event("Stop", turn_id="t-inputs"))
        other_record = HOOK._read_json(other_record_path)
        txn = Path(other_record["txn"])
        before = {path.relative_to(txn): path.read_bytes() for path in txn.rglob("*") if path.is_file()}
        self._record_prompt_and_skill_read(turn_id="t")
        response = HOOK.handle(self._event("HostAbort", turn_id="t", abort_reason="turn_changed"))
        self.assertEqual({"continue": True}, response)
        self.assertEqual(before, {path.relative_to(txn): path.read_bytes() for path in txn.rglob("*") if path.is_file()})
        cancelled = HOOK._read_json(HOOK._record_path(self._event("Stop", turn_id="t")))
        self.assertNotIn("bootstrap_artifacts", cancelled)
        final = HOOK.handle(self._event("Stop", turn_id="t-inputs", last_assistant_message=other_record["emitted_output"]))
        self.assertEqual({"continue": True}, final)
        self.assertTrue(HOOK._read_json(other_record_path)["delivery_verified"])

    def test_bootstrap_finally_keeps_original_exception_when_cleanup_lock_fails(self):
        self._record_prompt_and_skill_read()
        event = self._event("Stop", last_assistant_message="情况报告\n\n测试工作已完成。")
        record_path = HOOK._record_path(event)
        record = HOOK._read_json(record_path)

        def failed_bootstrap(*args):
            HOOK._mark_host_abort(record_path, "turn_changed")
            raise RuntimeError("original producer failure")

        with mock.patch.object(HOOK, "_bootstrap_transaction_locked", side_effect=failed_bootstrap), \
                mock.patch.object(HOOK, "_redact_turn_data", side_effect=HOOK.RecordLockUnavailable("still locked")):
            with self.assertRaisesRegex(RuntimeError, "original producer failure"):
                HOOK._bootstrap_transaction(event, record_path, record)
        self.assertEqual("turn_changed", HOOK._pending_host_abort(record_path))
        self.assertNotEqual(HOOK.REDACTED_RECORD_STATE, HOOK._read_json(record_path).get("data_retention_state"))
        lock = HOOK._acquire_bootstrap_lock(record_path)
        self.assertIsNotNone(lock)
        HOOK._release_bootstrap_lock(*lock)

    def test_bootstrap_finally_pending_cleanup_cannot_emit(self):
        self._record_prompt_and_skill_read()
        event = self._event("Stop", last_assistant_message="情况报告\n\n测试工作已完成。")
        record_path = HOOK._record_path(event)

        def completed_bootstrap(*args):
            HOOK._mark_host_abort(record_path, "turn_changed")
            return {"state": "TERMINAL_D0", "run_id": "synthetic-cleanup-control"}

        with mock.patch.object(HOOK, "_bootstrap_transaction_locked", side_effect=completed_bootstrap), \
                mock.patch.object(HOOK, "_redact_turn_data", side_effect=HOOK.RecordLockUnavailable("still locked")), \
                mock.patch.object(HOOK, "_run_review_gate_subprocess") as gate:
            response = HOOK.handle(event)
        self.assertFalse(response["continue"])
        gate.assert_not_called()
        self.assertEqual("turn_changed", HOOK._pending_host_abort(record_path))
        self.assertNotEqual(HOOK.REDACTED_RECORD_STATE, HOOK._read_json(record_path).get("data_retention_state"))
        self.assertEqual({"continue": True}, HOOK.handle(event))
        self.assertEqual(HOOK.REDACTED_RECORD_STATE, HOOK._read_json(record_path)["data_retention_state"])

    def test_abort_delete_failure_receipt_and_marker_retry_truthfully(self):
        self._record_prompt_and_skill_read("请起草内部编号HK008-DELETE的情况报告。")
        HOOK.handle(self._event("Stop", last_assistant_message="情况报告\n\n内部编号HK008-DELETE。"))
        record_path = HOOK._record_path(self._event("Stop"))
        self.assertTrue(HOOK._read_json(record_path)["bootstrap_artifacts"])
        inputs = HOOK._data_root() / "transactions" / record_path.parent.name / f"{record_path.stem}-inputs"
        with mock.patch.object(HOOK, "_remove_turn_artifact", return_value=False):
            response = HOOK.handle(self._event("HostAbort", abort_reason="turn_changed"))
        self.assertEqual({"continue": True}, response)
        record = HOOK._read_json(record_path)
        self.assertEqual(HOOK.REDACTED_RECORD_STATE, record["data_retention_state"])
        self.assertEqual(2, record["raw_artifact_delete_failures"])
        self.assertNotIn("request", record)
        self.assertTrue(inputs.is_dir())
        self.assertEqual("turn_changed", HOOK._pending_host_abort(record_path))
        HOOK.handle(self._event("Stop"))
        self.assertFalse(inputs.exists())
        self.assertEqual(0, HOOK._read_json(record_path)["raw_artifact_delete_failures"])
        self.assertFalse(HOOK._host_abort_marker_path(record_path).exists())
        self._assert_gate_root_omits("HK008-DELETE")

    def test_cleanup_cannot_unlink_a_held_bootstrap_lock(self):
        record_path = HOOK._record_path(self._event("Stop"))
        lock = HOOK._acquire_bootstrap_lock(record_path)
        self.assertIsNotNone(lock)
        try:
            HOOK._cleanup_bootstrap_lock_file(record_path)
            self.assertTrue(HOOK._bootstrap_lock_path(record_path).exists())
            self.assertIsNone(HOOK._acquire_bootstrap_lock(record_path))
        finally:
            HOOK._release_bootstrap_lock(*lock)
        recovered = HOOK._acquire_bootstrap_lock(record_path)
        self.assertIsNotNone(recovered)
        HOOK._release_bootstrap_lock(*recovered)

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

    def test_delivery_review_restores_one_source_bound_news_date_before_detect(self):
        prompt = (
            "请根据材料起草一则活动新闻，只输出可直接使用的正文。\n"
            "2026年9月2日，临江区政务服务中心举办培训，47名工作人员参加。"
        )
        draft = "培训活动举行\n\n9月2日，临江区政务服务中心举办培训，47名工作人员参加。"
        expected = draft.replace("9月2日", "2026年9月2日", 1)
        with mock.patch.dict(
            os.environ, {"COW_GATE_CAPABILITY": "delivery_review"}, clear=False
        ):
            self._record_prompt_and_skill_read(prompt=prompt)
            first = HOOK.handle(
                self._event(
                    "Stop",
                    stop_hook_active=False,
                    last_assistant_message=draft,
                )
            )
        self.assertEqual("block", first["decision"])
        self.assertIn(expected, first["reason"])
        record_path = HOOK._record_path(self._event("Stop"))
        record = HOOK._read_json(record_path)
        self.assertIsNotNone(record)
        self.assertTrue(record["source_bound_date"]["selected"])
        txn = Path(record["txn"])
        self.assertEqual(
            expected,
            (txn / "d0.snapshot.txt").read_text(encoding="utf-8"),
        )

        final = HOOK.handle(self._event("Stop", last_assistant_message=expected))
        self.assertEqual({"continue": True}, final)
        redacted = HOOK._read_json(record_path)
        self.assertEqual(HOOK.REDACTED_RECORD_STATE, redacted["data_retention_state"])
        self.assertTrue(redacted["source_bound_date"]["selected"])
        self.assertNotIn(draft, json.dumps(redacted, ensure_ascii=False))

    def test_source_bound_date_preflight_is_default_delivery_review_only(self):
        request = "请起草活动新闻。材料日期为2026年9月2日。"
        draft = "活动举行\n\n9月2日，活动举行。"
        with mock.patch.dict(
            os.environ, {"COW_GATE_CAPABILITY": "delivery_cleanliness"}, clear=False
        ):
            output, audit = HOOK._source_bound_date_input(request, draft)
        self.assertEqual(draft, output)
        self.assertIsNone(audit)

    def test_source_bound_date_module_failure_preserves_original_d0(self):
        request = "请起草活动新闻。材料日期为2026年9月2日。"
        draft = "活动举行\n\n9月2日，活动举行。"
        with mock.patch.dict(
            os.environ, {"COW_GATE_CAPABILITY": "delivery_review"}, clear=False
        ), mock.patch.object(HOOK, "_load_source_bound_dates", return_value=None):
            output, audit = HOOK._source_bound_date_input(request, draft)
        self.assertEqual(draft, output)
        self.assertIsNone(audit)

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

    def test_bootstrap_detect_nonzero_redacts_provisional_raw_inputs(self):
        prompt = "请起草包含内部编号A-17的情况报告。"
        draft = "情况报告\n\n内部编号A-17的核验工作已完成。"
        self._record_prompt_and_skill_read(prompt=prompt)

        completed = mock.Mock(returncode=1, stdout="", stderr="detect failed")
        with mock.patch.object(HOOK.subprocess, "run", return_value=completed):
            result = HOOK.handle(
                self._event("Stop", last_assistant_message=draft)
            )

        self.assertEqual({"continue": True}, result)
        record = HOOK._read_json(HOOK._record_path(self._event("Stop")))
        self.assertIsNotNone(record)
        self.assertEqual(HOOK.REDACTED_RECORD_STATE, record["data_retention_state"])
        self._assert_gate_root_omits(prompt, draft, "内部编号A-17")

    def test_one_stop_shares_a_bounded_review_gate_subprocess_budget(self):
        clock = [100.0]
        timeouts = []

        def fake_run(*_args, **kwargs):
            timeout = float(kwargs["timeout"])
            timeouts.append(timeout)
            clock[0] += timeout
            return mock.Mock(returncode=1, stdout="", stderr="timeout probe")

        def consume_three_gate_calls(_event):
            HOOK._run_gate(self.txn, "emit")
            HOOK._abort(self.txn, "timeout_probe")
            HOOK._run_gate(self.txn, "emit")
            return {"continue": True}

        def consume_one_gate_call(_event):
            HOOK._run_gate(self.txn, "emit")
            return {"continue": True}

        with mock.patch.object(HOOK.time, "monotonic", side_effect=lambda: clock[0]), \
             mock.patch.object(HOOK.subprocess, "run", side_effect=fake_run), \
             mock.patch.object(HOOK, "_handle_stop", side_effect=consume_three_gate_calls):
            first = HOOK.handle_stop(self._event("Stop"))

        self.assertEqual({"continue": True}, first)
        self.assertEqual(2, len(timeouts))
        self.assertLessEqual(sum(timeouts), HOOK.STOP_SUBPROCESS_BUDGET_SECONDS)
        self.assertAlmostEqual(HOOK.GATE_SUBPROCESS_TIMEOUT_SECONDS, timeouts[0])
        self.assertAlmostEqual(
            HOOK.STOP_SUBPROCESS_BUDGET_SECONDS
            - HOOK.GATE_SUBPROCESS_TIMEOUT_SECONDS,
            timeouts[1],
        )

        with mock.patch.object(HOOK.time, "monotonic", side_effect=lambda: clock[0]), \
             mock.patch.object(HOOK.subprocess, "run", side_effect=fake_run), \
             mock.patch.object(HOOK, "_handle_stop", side_effect=consume_one_gate_call):
            second = HOOK.handle_stop(self._event("Stop"))

        self.assertEqual({"continue": True}, second)
        self.assertEqual(3, len(timeouts))
        self.assertAlmostEqual(HOOK.GATE_SUBPROCESS_TIMEOUT_SECONDS, timeouts[2])

    def test_expired_stop_budget_redacts_exhausted_nonterminal_transaction(self):
        request = "请根据内部材料起草情况报告，保留尚未形成结论的状态。"
        draft = "情况报告\n\n当前事项仍在核查，尚未形成结论。"
        data_root = HOOK._data_root()
        self.assertIsNotNone(data_root)
        txn = data_root / "transactions" / "expired-budget" / "turn"
        inputs = txn.parent / f"{txn.name}-inputs"
        txn.mkdir(parents=True)
        inputs.mkdir(parents=True)
        run_id = "run-expired-budget"
        HOOK._atomic_write(
            txn / "state.json",
            {"state": "AWAITING_REPAIR", "run_id": run_id},
        )
        (txn / "d0.snapshot.txt").write_text(draft, encoding="utf-8")
        (inputs / "request.txt").write_text(request, encoding="utf-8")
        (inputs / "draft.txt").write_text(draft, encoding="utf-8")

        event = self._event(
            "Stop",
            turn_id="expired-budget",
            stop_hook_active=True,
            last_assistant_message="{不是有效的修订响应",
        )
        record_path = HOOK._record_path(event)
        self.assertIsNotNone(record_path)
        HOOK._atomic_write(
            record_path,
            {
                "schema_version": 1,
                "request": request,
                "txn": str(txn.resolve()),
                "run_id": run_id,
                "hook_phase": "awaiting_repair",
                "stop_attempts": HOOK.MAX_STOP_ATTEMPTS,
                "skill_seen": True,
            },
        )

        with mock.patch.object(
            HOOK.time, "monotonic", side_effect=itertools.chain([100.0], itertools.repeat(126.0))
        ), mock.patch.object(HOOK.subprocess, "run") as runner:
            result = HOOK.handle_stop(event)

        self.assertEqual({"continue": True}, result)
        runner.assert_not_called()
        redacted = HOOK._read_json(record_path)
        self.assertIsNotNone(redacted)
        self.assertEqual("failed_bounded", redacted["hook_phase"])
        self.assertFalse(redacted["delivery_verified"])
        self.assertEqual(
            "hook_stop_budget_exhausted_abort_failed",
            redacted["failure_reason"],
        )
        self.assertEqual(HOOK.REDACTED_RECORD_STATE, redacted["data_retention_state"])
        self.assertFalse(txn.exists())
        self.assertFalse(inputs.exists())
        serialized = json.dumps(redacted, ensure_ascii=False)
        self.assertNotIn(request, serialized)
        self.assertNotIn(draft, serialized)

    def test_all_review_gate_subprocesses_use_the_budgeted_runner(self):
        source = MODULE_PATH.read_text(encoding="utf-8")
        self.assertEqual(1, source.count("subprocess.run("))

    def test_emit_timeout_recovers_trusted_d0_and_redacts_after_exact_echo(self):
        original = "情况报告\n\n当前事项仍在核查，尚未形成结论。"
        self._state(name="TERMINAL_D0")
        state = HOOK._read_json(self.txn / "state.json")
        self.assertIsNotNone(state)
        state.update({"selected": "D0", "d0_sha256": HOOK._sha256_text(original)})
        HOOK._atomic_write(self.txn / "state.json", state)
        (self.txn / "d0.snapshot.txt").write_text(original, encoding="utf-8")

        event = self._event("Stop", turn_id="emit-timeout")
        record_path = HOOK._record_path(event)
        self.assertIsNotNone(record_path)
        record = {
            "schema_version": 1,
            "request": "请改写情况报告，只输出正文。",
            "txn": str(self.txn.resolve()),
            "hook_phase": "awaiting_verdict",
            "stop_attempts": 2,
        }
        HOOK._atomic_write(record_path, record)

        with mock.patch.object(HOOK, "_run_gate", return_value=(1, "")), \
             mock.patch.object(HOOK, "_load_review_gate_module", return_value=None):
            response = HOOK._emit_and_request_exact_output(
                self.txn, record_path, record
            )

        self.assertEqual("block", response["decision"])
        self.assertIn(original, response["reason"])
        self.assertEqual(HOOK._sha256_text(original), record["emitted_sha256"])

        echo = HOOK._handle_selected_output_echo(
            self._event(
                "Stop", turn_id="emit-timeout", last_assistant_message=original
            ),
            record_path,
            record,
            attempts=3,
        )
        self.assertEqual({"continue": True}, echo)
        final = HOOK._finish_stop_response(record_path, record, echo)
        self.assertEqual({"continue": True}, final)
        redacted = HOOK._read_json(record_path)
        self.assertIsNotNone(redacted)
        self.assertEqual(HOOK.REDACTED_RECORD_STATE, redacted["data_retention_state"])
        serialized = json.dumps(redacted, ensure_ascii=False)
        self.assertNotIn(original, serialized)
        self.assertNotIn("请改写情况报告", serialized)

    def test_emit_timeout_never_downgrades_terminal_d1_to_d0(self):
        original = "情况报告\n\n当前事项仍在核查，尚未形成结论。"
        data_root = HOOK._data_root()
        self.assertIsNotNone(data_root)
        txn = data_root / "transactions" / "emit-timeout-d1"
        txn.mkdir(parents=True)
        HOOK._atomic_write(
            txn / "state.json",
            {"state": "TERMINAL_D1", "run_id": "run-emit-timeout-d1"},
        )
        state = HOOK._read_json(txn / "state.json")
        self.assertIsNotNone(state)
        state.update(
            {
                "selected": "D1",
                "d0_sha256": HOOK._sha256_text(original),
                "d1_sha256": HOOK._sha256_text(original + "候选"),
            }
        )
        HOOK._atomic_write(txn / "state.json", state)
        (txn / "d0.snapshot.txt").write_text(original, encoding="utf-8")

        event = self._event("Stop", turn_id="emit-timeout-d1")
        record_path = HOOK._record_path(event)
        self.assertIsNotNone(record_path)
        record = {
            "schema_version": 1,
            "request": "请改写情况报告，只输出正文。",
            "txn": str(txn.resolve()),
            "hook_phase": "awaiting_verdict",
            "stop_attempts": 2,
        }
        HOOK._atomic_write(record_path, record)

        with mock.patch.object(HOOK, "_run_gate", return_value=(1, "")):
            response = HOOK._emit_and_request_exact_output(
                txn, record_path, record
            )

        self.assertEqual("block", response["decision"])
        self.assertIn("停止自动交付", response["reason"])
        self.assertNotIn(original, response["reason"])
        redacted = HOOK._read_json(record_path)
        self.assertIsNotNone(redacted)
        self.assertEqual(HOOK.REDACTED_RECORD_STATE, redacted["data_retention_state"])
        self.assertFalse(txn.exists())
        serialized = json.dumps(redacted, ensure_ascii=False)
        self.assertNotIn(original, serialized)
        self.assertNotIn("请改写情况报告", serialized)

    def test_bootstrap_detect_oserror_redacts_provisional_raw_inputs(self):
        prompt = "请起草包含内部编号B-23的情况报告。"
        draft = "情况报告\n\n内部编号B-23的核验工作已完成。"
        self._record_prompt_and_skill_read(prompt=prompt)

        with mock.patch.object(
            HOOK.subprocess, "run", side_effect=OSError("detect unavailable")
        ):
            result = HOOK.handle(
                self._event("Stop", last_assistant_message=draft)
            )

        self.assertEqual({"continue": True}, result)
        record = HOOK._read_json(HOOK._record_path(self._event("Stop")))
        self.assertIsNotNone(record)
        self.assertEqual(HOOK.REDACTED_RECORD_STATE, record["data_retention_state"])
        self._assert_gate_root_omits(prompt, draft, "内部编号B-23")

    def test_bootstrap_success_without_state_redacts_provisional_raw_inputs(self):
        prompt = "请起草包含内部编号D-52的情况报告。"
        draft = "情况报告\n\n内部编号D-52的核验工作已完成。"
        self._record_prompt_and_skill_read(prompt=prompt)

        completed = mock.Mock(returncode=0, stdout="", stderr="")
        with mock.patch.object(HOOK.subprocess, "run", return_value=completed):
            result = HOOK.handle(self._event("Stop", last_assistant_message=draft))

        self.assertEqual({"continue": True}, result)
        record = HOOK._read_json(HOOK._record_path(self._event("Stop")))
        self.assertIsNotNone(record)
        self.assertEqual(HOOK.REDACTED_RECORD_STATE, record["data_retention_state"])
        self._assert_gate_root_omits(prompt, draft, "内部编号D-52")

    def test_bootstrap_failure_preserves_other_session_and_plugin_data(self):
        prompt = "请起草包含内部编号E-64的情况报告。"
        draft = "情况报告\n\n内部编号E-64的核验工作已完成。"
        self._record_prompt_and_skill_read(prompt=prompt)
        data_root = HOOK._data_root()
        self.assertIsNotNone(data_root)
        other_session = data_root / "transactions" / "session-other" / "keep.txt"
        other_session.parent.mkdir(parents=True)
        other_session.write_text("保留相邻会话", encoding="utf-8")
        other_plugin = data_root.parent / "other-plugin" / "keep.txt"
        other_plugin.parent.mkdir(parents=True)
        other_plugin.write_text("保留其他插件", encoding="utf-8")

        completed = mock.Mock(returncode=1, stdout="", stderr="detect failed")
        with mock.patch.object(HOOK.subprocess, "run", return_value=completed):
            result = HOOK.handle(self._event("Stop", last_assistant_message=draft))

        self.assertEqual({"continue": True}, result)
        self.assertTrue(data_root.is_dir())
        self.assertEqual("保留相邻会话", other_session.read_text(encoding="utf-8"))
        self.assertEqual("保留其他插件", other_plugin.read_text(encoding="utf-8"))
        self._assert_gate_root_omits(prompt, draft, "内部编号E-64")

    def test_concurrent_stop_uses_single_bootstrap_owner(self):
        prompt = "请起草包含内部编号F-75的情况报告。"
        draft = "情况报告\n\n内部编号F-75的核验工作已完成。"
        self._record_prompt_and_skill_read(prompt=prompt)
        entered = threading.Event()
        release = threading.Event()
        original_run = HOOK.subprocess.run
        results = []
        failures = []

        def slow_run(*args, **kwargs):
            if not entered.is_set():
                entered.set()
                self.assertTrue(release.wait(timeout=5))
            return original_run(*args, **kwargs)

        def first_stop():
            try:
                results.append(
                    HOOK.handle(self._event("Stop", last_assistant_message=draft))
                )
            except BaseException as exc:  # pragma: no cover - surfaced below
                failures.append(exc)

        with mock.patch.object(HOOK.subprocess, "run", side_effect=slow_run):
            worker = threading.Thread(target=first_stop)
            worker.start()
            self.assertTrue(entered.wait(timeout=5))
            concurrent = HOOK.handle(
                self._event("Stop", last_assistant_message=draft)
            )
            release.set()
            worker.join(timeout=10)

        self.assertFalse(worker.is_alive())
        self.assertEqual([], failures)
        self.assertEqual("block", concurrent["decision"])
        self.assertIn("正在启动", concurrent["reason"])
        self.assertEqual(1, len(results))
        self.assertEqual("block", results[0]["decision"])
        record_path = HOOK._record_path(self._event("Stop"))
        record = HOOK._read_json(record_path)
        self.assertIsNotNone(record)
        self.assertNotIn("bootstrap_pending", record)
        self.assertTrue(Path(record["txn"]).is_dir())

        terminal = HOOK.handle(self._event("Stop", last_assistant_message=draft))
        self.assertEqual({"continue": True}, terminal)
        redacted = HOOK._read_json(record_path)
        self.assertEqual(HOOK.REDACTED_RECORD_STATE, redacted["data_retention_state"])
        self.assertFalse(HOOK._bootstrap_lock_path(record_path).exists())
        self._assert_gate_root_omits(prompt, draft, "内部编号F-75")

    def test_bootstrap_lock_open_error_redacts_and_allows(self):
        prompt = "请起草包含内部编号G-86的情况报告。"
        draft = "情况报告\n\n内部编号G-86的核验工作已完成。"
        self._record_prompt_and_skill_read(prompt=prompt)

        with mock.patch.object(
            HOOK,
            "_acquire_bootstrap_lock",
            side_effect=OSError(errno.EIO, "lock I/O"),
        ):
            result = HOOK.handle(self._event("Stop", last_assistant_message=draft))

        self.assertEqual({"continue": True}, result)
        record = HOOK._read_json(HOOK._record_path(self._event("Stop")))
        self.assertIsNotNone(record)
        self.assertEqual(HOOK.REDACTED_RECORD_STATE, record["data_retention_state"])
        self._assert_gate_root_omits(prompt, draft, "内部编号G-86")

    def test_pending_bootstrap_lock_error_redacts_and_allows(self):
        prompt = "请起草包含内部编号H-97的情况报告。"
        draft = "情况报告\n\n内部编号H-97的核验工作已完成。"
        self._record_prompt_and_skill_read(prompt=prompt)
        record_path = HOOK._record_path(self._event("Stop"))
        record = HOOK._read_json(record_path)
        self.assertIsNotNone(record)
        data_root = HOOK._data_root()
        self.assertIsNotNone(data_root)
        txn = data_root / "transactions" / "session-1" / "turn-1"
        inputs = txn.parent / "turn-1-inputs"
        HOOK._atomic_write_text(inputs / "request.txt", prompt)
        HOOK._atomic_write_text(inputs / "draft.txt", draft)
        record.update({"txn": str(txn.resolve()), "bootstrap_pending": True})
        HOOK._atomic_write(record_path, record)

        with mock.patch.object(
            HOOK,
            "_acquire_bootstrap_lock",
            side_effect=OSError(errno.EIO, "lock I/O"),
        ):
            result = HOOK.handle(self._event("Stop", last_assistant_message=draft))

        self.assertEqual({"continue": True}, result)
        redacted = HOOK._read_json(record_path)
        self.assertIsNotNone(redacted)
        self.assertEqual(HOOK.REDACTED_RECORD_STATE, redacted["data_retention_state"])
        self._assert_gate_root_omits(prompt, draft, "内部编号H-97")

    def test_bootstrap_lock_open_error_is_not_reported_as_contention(self):
        record_path = HOOK._record_path(self._event("Stop", turn_id="lock-io"))
        self.assertIsNotNone(record_path)
        with mock.patch.object(
            HOOK.Path, "open", side_effect=OSError(errno.EIO, "lock open failed")
        ):
            with self.assertRaises(OSError):
                HOOK._acquire_bootstrap_lock(record_path)

    @unittest.skipUnless(os.name == "nt", "Windows lock API test")
    def test_bootstrap_lock_api_io_error_is_not_reported_as_contention(self):
        record_path = HOOK._record_path(self._event("Stop", turn_id="lock-api-io"))
        self.assertIsNotNone(record_path)
        with mock.patch(
            "msvcrt.locking", side_effect=OSError(errno.EIO, "lock API failed")
        ):
            with self.assertRaises(OSError):
                HOOK._acquire_bootstrap_lock(record_path)

    def test_released_owner_cannot_unlock_replacement_owner(self):
        record_path = HOOK._record_path(self._event("Stop", turn_id="lock-owner"))
        self.assertIsNotNone(record_path)
        first = HOOK._acquire_bootstrap_lock(record_path)
        self.assertIsNotNone(first)
        first_path, first_handle = first
        self.assertIsNone(HOOK._acquire_bootstrap_lock(record_path))
        HOOK._release_bootstrap_lock(first_path, first_handle)

        replacement = HOOK._acquire_bootstrap_lock(record_path)
        self.assertIsNotNone(replacement)
        replacement_path, replacement_handle = replacement
        HOOK._release_bootstrap_lock(first_path, first_handle)
        self.assertIsNone(HOOK._acquire_bootstrap_lock(record_path))
        HOOK._release_bootstrap_lock(replacement_path, replacement_handle)

        final = HOOK._acquire_bootstrap_lock(record_path)
        self.assertIsNotNone(final)
        HOOK._release_bootstrap_lock(*final)
        HOOK._cleanup_bootstrap_lock_file(record_path)
        self.assertFalse(first_path.exists())

    def test_process_exit_releases_bootstrap_lock(self):
        record_path = HOOK._record_path(self._event("Stop", turn_id="process-lock"))
        self.assertIsNotNone(record_path)
        script = (
            "import importlib.util, os, pathlib, sys; "
            f"p=pathlib.Path({str(MODULE_PATH)!r}); "
            "s=importlib.util.spec_from_file_location('g',p); "
            "m=importlib.util.module_from_spec(s); s.loader.exec_module(m); "
            f"lock=m._acquire_bootstrap_lock(pathlib.Path({str(record_path)!r})); "
            "assert lock is not None; print('READY', flush=True); "
            "sys.stdin.readline(); os._exit(0)"
        )
        process = subprocess.Popen(
            [sys.executable, "-c", script],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        def close_process():
            if process.poll() is None:
                process.kill()
                process.wait(timeout=5)
            for stream in (process.stdin, process.stdout, process.stderr):
                if stream is not None and not stream.closed:
                    stream.close()

        self.addCleanup(close_process)
        self.assertEqual("READY", process.stdout.readline().strip())
        self.assertIsNone(HOOK._acquire_bootstrap_lock(record_path))
        process.stdin.write("\n")
        process.stdin.flush()
        exit_code = process.wait(timeout=5)
        stderr = process.stderr.read()
        self.assertEqual(0, exit_code, stderr)

        recovered = HOOK._acquire_bootstrap_lock(record_path)
        self.assertIsNotNone(recovered)
        HOOK._release_bootstrap_lock(*recovered)
        HOOK._cleanup_bootstrap_lock_file(record_path)

    def test_posix_cleanup_keeps_shared_lock_inode(self):
        record_path = HOOK._record_path(self._event("Stop", turn_id="posix-lock"))
        self.assertIsNotNone(record_path)
        lock_path = HOOK._bootstrap_lock_path(record_path)
        lock_path.parent.mkdir(parents=True, exist_ok=True)
        lock_path.write_bytes(b"0")
        self.addCleanup(lambda: lock_path.unlink(missing_ok=True))

        with mock.patch.object(HOOK.os, "name", "posix"):
            HOOK._cleanup_bootstrap_lock_file(record_path)

        self.assertEqual(b"0", lock_path.read_bytes())

    def test_interrupted_bootstrap_is_cleaned_without_redetect_on_resume(self):
        prompt = "请起草包含内部编号C-41的情况报告。"
        draft = "情况报告\n\n内部编号C-41的核验工作已完成。"
        self._record_prompt_and_skill_read(prompt=prompt)

        with mock.patch.object(
            HOOK.subprocess, "run", side_effect=KeyboardInterrupt()
        ):
            with self.assertRaises(KeyboardInterrupt):
                HOOK.handle(self._event("Stop", last_assistant_message=draft))

        data_root = HOOK._data_root()
        self.assertIsNotNone(data_root)
        input_dir = data_root / "transactions" / "session-1" / "turn-1-inputs"
        self.assertTrue(input_dir.is_dir())

        with mock.patch.object(HOOK.subprocess, "run") as redetect:
            resumed = HOOK.handle(
                self._event("Stop", last_assistant_message=draft)
            )

        self.assertEqual({"continue": True}, resumed)
        redetect.assert_not_called()
        record = HOOK._read_json(HOOK._record_path(self._event("Stop")))
        self.assertIsNotNone(record)
        self.assertEqual(HOOK.REDACTED_RECORD_STATE, record["data_retention_state"])
        self._assert_gate_root_omits(prompt, draft, "内部编号C-41")

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
            "请检查这份材料，不修改文件，只列出问题和建议。",
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
            (
                "请使用当前插件中的公文 Skill 起草一份设备采购申请。只读取指定"
                " reference，不调用 Shell，不修改文件。品牌和供应商尚未确定，"
                "采购方式待审核；只输出完整正文，不解释过程。"
            ),
            "请根据材料形成一份采购申请，采购方式待审核，不修改任何文件。",
            "请起草设备采购申请，不修改本地文件，采购方式待审核。",
            "请起草设备采购申请，不修改 文件，采购方式待审核。",
            "请起草设备采购申请，不修改源代码，采购方式待审核。",
            "请根据材料形成一份采购申请，采购方式待审核，不改文件。",
            "请根据材料形成一份采购申请，采购方式待审核，不修改工作区文件。",
            "请根据材料形成一份采购申请，采购方式待审核，不修改项目中的文件。",
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

    def test_exhausted_wrong_echo_stops_and_replay_cannot_allow_it(self):
        self._record_prompt_and_skill_read()
        draft = "情况报告\n\n测试工作已完成。"
        HOOK.handle(self._event("Stop", last_assistant_message=draft))
        for _ in range(HOOK.MAX_STOP_ATTEMPTS - 1):
            response = HOOK.handle(self._event("Stop", stop_hook_active=True, last_assistant_message="错误回显"))
            self.assertEqual("block", response["decision"])
        response = HOOK.handle(self._event("Stop", stop_hook_active=True, last_assistant_message="错误回显"))
        self.assertIs(response["continue"], False)
        self.assertIn("未通过", response["stopReason"])
        self.assertNotIn("decision", response)
        path = HOOK._record_path(self._event("Stop"))
        terminal = HOOK._read_json(path)
        self.assertFalse(terminal["delivery_verified"])
        self.assertEqual(HOOK.REDACTED_RECORD_STATE, terminal["data_retention_state"])
        for text in ("错误回显", draft):
            replay = HOOK.handle(self._event("Stop", stop_hook_active=True, last_assistant_message=text))
            self.assertEqual(response, replay)
            self.assertEqual(terminal, HOOK._read_json(path))
        self._assert_gate_root_omits(draft, "请起草一份情况报告。")

    def test_stop_record_lock_contention_is_a_bounded_failure_not_allow(self):
        self._record_prompt_and_skill_read()
        draft = "情况报告\n\n测试工作已完成。"
        HOOK.handle(self._event("Stop", last_assistant_message=draft))
        path = HOOK._record_path(self._event("Stop"))
        before = HOOK._read_json(path)
        lock = HOOK._acquire_file_lock(path.with_suffix(".state-lock"))
        self.assertIsNotNone(lock)
        try:
            completed = subprocess.run([sys.executable, "-B", str(MODULE_PATH)],
                                       input=json.dumps(self._event("Stop", stop_hook_active=True, last_assistant_message="错误回显")),
                                       text=True, encoding="utf-8", capture_output=True, check=True, timeout=8)
            response = json.loads(completed.stdout)
            self.assertIs(response["continue"], False)
            self.assertIn("暂不可写", response["stopReason"])
            self.assertEqual(before, HOOK._read_json(path))
        finally:
            HOOK._release_bootstrap_lock(*lock)
        retry = HOOK.handle(self._event("Stop", stop_hook_active=True, last_assistant_message=draft))
        self.assertTrue(retry["continue"])

    def test_stop_record_lock_io_error_does_not_allow_unverified_output(self):
        self._record_prompt_and_skill_read()
        draft = "情况报告\n\n测试工作已完成。"
        HOOK.handle(self._event("Stop", last_assistant_message=draft))
        with mock.patch.object(HOOK, "_acquire_file_lock", side_effect=OSError("unavailable")):
            response = HOOK.handle_stop(self._event("Stop", stop_hook_active=True, last_assistant_message="错误回显"))
        self.assertIs(response["continue"], False)

    def test_explicit_optout_is_not_blocked_by_unavailable_cleanup_lock(self):
        prompt = "本次关闭Hook。请写情况说明。材料：测试工作已完成。"
        for failure in ("contention", "io_error"):
            with self.subTest(failure=failure):
                event = self._event("Stop", turn_id="optout-" + failure,
                                    last_assistant_message="测试工作已完成。")
                HOOK.handle({**event, "hook_event_name": "UserPromptSubmit", "prompt": prompt})
                path = HOOK._record_path(event)
                # A delayed Skill-read marker must not override explicit opt-out.
                HOOK._mark_skill_seen(path)
                if failure == "contention":
                    with HOOK._record_lock(path), mock.patch.object(HOOK, "RECORD_LOCK_TIMEOUT_SECONDS", 0.02):
                        response = HOOK.handle_stop(event)
                else:
                    with mock.patch.object(HOOK, "_acquire_file_lock", side_effect=OSError("unavailable")):
                        response = HOOK.handle_stop(event)
                self.assertEqual({"continue": True}, response)
                self.assertNotIn("txn", HOOK._read_json(path))
                self.assertEqual({"continue": True}, HOOK.handle_stop(event))
                final = HOOK._read_json(path)
                self.assertEqual(HOOK.REDACTED_RECORD_STATE, final["data_retention_state"])
                self.assertNotIn("request", final)

    def test_stale_echo_writer_cannot_reopen_completed_delivery(self):
        self._record_prompt_and_skill_read()
        draft = "情况报告\n\n测试工作已完成。"
        event = self._event("Stop", stop_hook_active=True, last_assistant_message="错误回显")
        HOOK.handle(self._event("Stop", last_assistant_message=draft))
        path = HOOK._record_path(event)
        stale = HOOK._read_json(path)
        HOOK.handle(self._event("Stop", stop_hook_active=True, last_assistant_message=draft))
        terminal = HOOK._read_json(path)
        response = HOOK._handle_selected_output_echo(event, path, stale, 1)
        final = HOOK._finish_stop_response(path, stale, response)
        self.assertEqual({"continue": True}, final)
        self.assertEqual(terminal, HOOK._read_json(path))
        self.assertNotIn("emitted_output", stale)

    def test_terminal_user_and_tool_replay_do_not_restore_raw_or_marker(self):
        prompt = "本次关闭Hook。请写情况说明。材料：测试工作已完成。"
        event = self._event("UserPromptSubmit", prompt=prompt)
        for payload in (event, self._event("Stop", last_assistant_message="测试工作已完成。"), event):
            completed = subprocess.run([sys.executable, "-B", str(MODULE_PATH)], input=json.dumps(payload),
                                       text=True, encoding="utf-8", capture_output=True, check=True)
            self.assertEqual({"continue": True}, json.loads(completed.stdout))
        path = HOOK._record_path(event)
        terminal = HOOK._read_json(path)
        self.assertEqual(HOOK.REDACTED_RECORD_STATE, terminal["data_retention_state"])
        self.assertNotIn("request", terminal)
        self._record_prompt_and_skill_read(prompt)
        self.assertEqual(terminal, HOOK._read_json(path))
        self.assertFalse(HOOK._skill_seen_marker_path(path).exists())

    def test_late_post_tool_commit_cannot_overwrite_terminal_cleanup(self):
        self._record_prompt_and_skill_read()
        draft = "情况报告\n\n测试工作已完成。"
        HOOK.handle(self._event("Stop", last_assistant_message=draft))
        paused, resume = threading.Event(), threading.Event()
        errors = []
        original = HOOK._write_record

        def delayed(*args, **kwargs):
            if threading.current_thread().name == "late-tool":
                paused.set()
                if not resume.wait(5):
                    raise RuntimeError("scheduler timeout")
            return original(*args, **kwargs)

        def worker():
            try:
                HOOK.handle(self._event("PostToolUse", tool_input={"cmd": "Get-Content material.txt"},
                                        tool_response={"exit_code": 0}))
            except Exception as exc:
                errors.append(exc)

        with mock.patch.object(HOOK, "_write_record", side_effect=delayed):
            thread = threading.Thread(target=worker, name="late-tool")
            thread.start()
            try:
                self.assertTrue(paused.wait(5))
                result = HOOK.handle(self._event("Stop", stop_hook_active=True, last_assistant_message=draft))
                self.assertTrue(result["continue"])
            finally:
                resume.set()
                thread.join(5)
        self.assertFalse(thread.is_alive())
        self.assertEqual([], errors)
        terminal = HOOK._read_json(HOOK._record_path(self._event("Stop")))
        self.assertTrue(terminal["delivery_verified"])
        self.assertEqual(HOOK.REDACTED_RECORD_STATE, terminal["data_retention_state"])
        self._assert_gate_root_omits(draft, "请起草一份情况报告。")

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
