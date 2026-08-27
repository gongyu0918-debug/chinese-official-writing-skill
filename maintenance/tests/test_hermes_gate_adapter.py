from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import threading
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from maintenance.tests.hook_companion_support import ASSEMBLER


ROOT = Path(__file__).resolve().parents[2]
CORE_PATH = (
    ROOT
    / "chinese-official-writing"
    / "hooks"
    / "core"
    / "single_pass_final_review.py"
)
EVIDENCE_FIXTURES = (
    ROOT / "maintenance" / "tests" / "evidence" / "hk004-hermes-r2" / "fixtures"
)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class FakeLlm:
    def __init__(self, response: str):
        self.response = response
        self.calls: list[tuple[list[dict[str, str]], dict[str, object]]] = []

    def complete(self, messages, **kwargs):
        self.calls.append((messages, kwargs))
        return SimpleNamespace(text=self.response)


class FakeContext:
    def __init__(self, response: str):
        self.llm = FakeLlm(response)
        self.hooks = {}
        self.skill = None

    def register_skill(self, *args):
        self.skill = args

    def register_hook(self, name, callback):
        self.hooks[name] = callback


class HermesSinglePassCoreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.core = load_module("cow_test_single_pass_review", CORE_PATH)

    def test_keep_uses_empty_final_text_without_echoing_draft(self) -> None:
        draft = "关于工作进展的情况说明\n\n数据接口联调已完成。"
        raw = '{"action":"KEEP","issues":[],"final_text":""}'
        selection = self.core.parse_selection(raw, draft, "请起草情况说明")
        self.assertEqual("KEEP", selection.action)
        self.assertEqual(draft, selection.text)
        self.assertEqual("model_keep", selection.reason)

    def test_keep_with_draft_echo_fails_open(self) -> None:
        draft = "关于工作进展的情况说明\n\n数据接口联调已完成。"
        raw = json.dumps(
            {"action": "KEEP", "issues": [], "final_text": draft},
            ensure_ascii=False,
        )
        selection = self.core.parse_selection(raw, draft, "请起草情况说明")
        self.assertEqual("KEEP", selection.action)
        self.assertEqual(draft, selection.text)
        self.assertEqual("invalid_keep", selection.reason)

    def test_safe_title_cleanup_can_replace(self) -> None:
        draft = "关于有关工作进展的情况说明\n\n数据接口联调已完成。"
        candidate = "关于工作进展的情况说明\n\n数据接口联调已完成。"
        raw = json.dumps(
            {
                "action": "REPLACE",
                "issues": ["REPETITION_OR_TITLE"],
                "final_text": candidate,
            },
            ensure_ascii=False,
        )
        selection = self.core.parse_selection(raw, draft, "请起草情况说明")
        self.assertEqual("REPLACE", selection.action)
        self.assertEqual(candidate, selection.text)

    def test_missing_number_or_changed_state_fails_open(self) -> None:
        draft = "共52人参加。岗位培训尚未开展。"
        request = "共52人参加；岗位培训尚未开展。"
        missing_number = (
            '{"action":"REPLACE","issues":["REPETITION_OR_TITLE"],'
            '"final_text":"人员参加。岗位培训尚未开展。"}'
        )
        changed_state = (
            '{"action":"REPLACE","issues":["STATE_UPGRADE"],'
            '"final_text":"共52人参加。岗位培训已经开展。"}'
        )
        for raw in (missing_number, changed_state):
            with self.subTest(raw=raw):
                selection = self.core.parse_selection(raw, draft, request)
                self.assertEqual("KEEP", selection.action)
                self.assertEqual(draft, selection.text)

    def test_merged_anchor_sentence_fails_open(self) -> None:
        draft = (EVIDENCE_FIXTURES / "h1-unsafe-redundancy-d0.txt").read_text(
            encoding="utf-8"
        )
        candidate = (
            EVIDENCE_FIXTURES / "h1-rejected-merged-d1.txt"
        ).read_text(encoding="utf-8")
        request = (
            "某中心现有两台推理服务器，过去10个工作日平均利用率为93%，"
            "工作日每天约16项任务等待；拟增购两台推理服务器用于缓解资源紧张，"
            "预算额度、采购方式和供应商均未确定。请写采购申请正文。"
        )
        raw = json.dumps(
            {
                "action": "REPLACE",
                "issues": ["NEW_FACT_OR_PROCEDURE"],
                "final_text": candidate,
            },
            ensure_ascii=False,
        )
        selection = self.core.parse_selection(raw, draft, request)
        self.assertEqual("KEEP", selection.action)
        self.assertEqual("anchor_relation_unverified", selection.reason)
        self.assertEqual(draft, selection.text)

    def test_minimal_redundancy_cleanup_passes_hard_anchors(self) -> None:
        draft = (EVIDENCE_FIXTURES / "h1-unsafe-redundancy-d0.txt").read_text(
            encoding="utf-8"
        )
        candidate = (
            EVIDENCE_FIXTURES / "h1-accepted-minimal-d1.txt"
        ).read_text(encoding="utf-8")
        request = (
            "某中心现有两台推理服务器，过去10个工作日平均利用率为93%，"
            "工作日每天约16项任务等待；拟增购两台推理服务器用于缓解资源紧张，"
            "预算额度、采购方式和供应商均未确定。请写采购申请正文。"
        )
        raw = json.dumps(
            {
                "action": "REPLACE",
                "issues": ["NEW_FACT_OR_PROCEDURE"],
                "final_text": candidate,
            },
            ensure_ascii=False,
        )
        selection = self.core.parse_selection(raw, draft, request)
        self.assertEqual("REPLACE", selection.action)
        self.assertEqual(candidate, selection.text)

    def test_malformed_or_extra_fields_fail_open(self) -> None:
        draft = "完整正文。"
        for raw in (
            "not json",
            '{"action":"KEEP","issues":[],"final_text":"","note":"x"}',
            '{"action":"REPLACE","issues":[],"final_text":"另一稿。"}',
        ):
            with self.subTest(raw=raw):
                self.assertEqual(
                    draft,
                    self.core.parse_selection(raw, draft, "请起草正文").text,
                )


class HermesAdapterTests(unittest.TestCase):
    def setUp(self) -> None:
        argv_patch = patch.object(
            sys,
            "argv",
            ["hermes", "chat", "-q", "fresh query"],
        )
        argv_patch.start()
        self.addCleanup(argv_patch.stop)
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.companion = Path(self.temporary.name) / "hermes-agent"
        ASSEMBLER.assemble("hermes-agent", self.companion)
        self.plugin = load_module(
            f"cow_test_hermes_adapter_{id(self)}", self.companion / "__init__.py"
        )

    def test_assembled_plugin_runs_one_same_turn_replacement(self) -> None:
        response = json.dumps(
            {
                "action": "REPLACE",
                "issues": ["REPETITION_OR_TITLE"],
                "final_text": "关于工作进展的情况说明\n\n数据接口联调已完成。",
            },
            ensure_ascii=False,
        )
        ctx = FakeContext(response)
        self.plugin.register(ctx)
        self.assertEqual(
            "root",
            self.plugin.logger.name,
        )
        self.assertEqual(
            "chinese-official-writing",
            ctx.skill[0],
        )
        self.assertTrue(ctx.skill[1].is_file())

        ctx.hooks["on_skill_lifecycle"](
            action="loaded",
            skill_name=self.plugin.PLUGIN_SKILL,
            session_id="",
            task_id="session-1",
        )
        ctx.hooks["on_session_start"](session_id="session-1", platform="cli")
        ctx.hooks["pre_llm_call"](
            session_id="session-1",
            task_id="task-1",
            turn_id="turn-1",
            user_message="请起草一份情况说明。",
        )
        draft = "关于有关工作进展的情况说明\n\n数据接口联调已完成。"
        selected = ctx.hooks["transform_llm_output"](
            response_text=draft, session_id="session-1"
        )
        self.assertEqual(
            "关于工作进展的情况说明\n\n数据接口联调已完成。", selected
        )
        self.assertEqual(1, len(ctx.llm.calls))
        self.assertIsNone(
            ctx.hooks["transform_llm_output"](
                response_text=draft, session_id="session-1"
            )
        )
        ctx.hooks["post_llm_call"](
            session_id="session-1",
            task_id="task-1",
            turn_id="turn-1",
            assistant_response="关于工作进展的情况说明\n\n数据接口联调已完成。",
            conversation_history=[
                {
                    "role": "assistant",
                    "content": draft,
                }
            ],
        )
        self.assertNotIn("session-1", self.plugin._active_sessions)
        self.assertNotIn("session-1", self.plugin._disabled_sessions)

    def test_cross_thread_preload_binds_exact_fresh_cli_session_only(self) -> None:
        ctx = FakeContext('{"action":"KEEP","issues":[],"final_text":""}')
        self.plugin.register(ctx)

        preload = threading.Thread(
            target=lambda: ctx.hooks["on_skill_lifecycle"](
                action="loaded",
                skill_name=self.plugin.PLUGIN_SKILL,
                session_id="",
                task_id="cli",
            )
        )
        preload.start()
        preload.join()

        ctx.hooks["on_session_start"](session_id="other", platform="cli")
        ctx.hooks["pre_llm_call"](session_id="other", user_message="请起草报告。")
        self.assertIsNone(
            ctx.hooks["transform_llm_output"](
                response_text="正文。", session_id="other"
            )
        )

        ctx.hooks["on_session_start"](session_id="cli", platform="cli")
        ctx.hooks["pre_llm_call"](
            session_id="cli",
            task_id="task-cli",
            turn_id="turn-cli",
            user_message="请起草报告。",
        )
        self.assertIsNone(
            ctx.hooks["transform_llm_output"](
                response_text="正文。", session_id="cli"
            )
        )
        self.assertEqual(1, len(ctx.llm.calls))

    def test_empty_mismatched_and_non_cli_preloads_fail_open(self) -> None:
        ctx = FakeContext('{"action":"KEEP","issues":[],"final_text":""}')
        self.plugin.register(ctx)

        for task_id in ("", "expected"):
            ctx.hooks["on_skill_lifecycle"](
                action="loaded",
                skill_name=self.plugin.PLUGIN_SKILL,
                session_id="",
                task_id=task_id,
            )
        ctx.hooks["on_session_start"](session_id="different", platform="cli")
        ctx.hooks["pre_llm_call"](
            session_id="different",
            task_id="task-different",
            turn_id="turn-different",
            user_message="请起草报告。",
        )
        self.assertIsNone(
            ctx.hooks["transform_llm_output"](
                response_text="正文。", session_id="different"
            )
        )

        ctx.hooks["on_skill_lifecycle"](
            action="loaded",
            skill_name=self.plugin.PLUGIN_SKILL,
            session_id="",
            task_id="non-cli",
        )
        ctx.hooks["on_session_start"](session_id="non-cli", platform="telegram")
        ctx.hooks["on_session_start"](session_id="non-cli", platform="cli")
        ctx.hooks["pre_llm_call"](
            session_id="non-cli",
            task_id="task-non-cli",
            turn_id="turn-non-cli",
            user_message="请起草报告。",
        )
        self.assertIsNone(
            ctx.hooks["transform_llm_output"](
                response_text="正文。", session_id="non-cli"
            )
        )
        self.assertEqual([], ctx.llm.calls)

    def test_two_pending_cli_sessions_bind_by_exact_id(self) -> None:
        ctx = FakeContext('{"action":"KEEP","issues":[],"final_text":""}')
        self.plugin.register(ctx)
        for session_id in ("session-a", "session-b"):
            ctx.hooks["on_skill_lifecycle"](
                action="loaded",
                skill_name=self.plugin.PLUGIN_SKILL,
                session_id="",
                task_id=session_id,
            )

        for session_id in ("session-b", "session-a"):
            ctx.hooks["on_session_start"](session_id=session_id, platform="cli")
            ctx.hooks["pre_llm_call"](
                session_id=session_id,
                task_id=f"task-{session_id}",
                turn_id=f"turn-{session_id}",
                user_message="请起草报告。",
            )
            self.assertIsNone(
                ctx.hooks["transform_llm_output"](
                    response_text="正文。", session_id=session_id
                )
            )
            ctx.hooks["post_llm_call"](
                session_id=session_id,
                task_id=f"task-{session_id}",
                turn_id=f"turn-{session_id}",
                assistant_response="正文。",
                conversation_history=[{"role": "assistant", "content": "正文。"}],
            )
        self.assertEqual(2, len(ctx.llm.calls))

    def test_interactive_and_resumed_cli_are_not_armed(self) -> None:
        for argv in (
            ["hermes", "chat"],
            ["hermes", "chat", "-q", "x", "--resume", "session"],
            ["hermes", "chat", "--query=x", "-c", "session"],
            ["hermes", "--oneshot", "x"],
        ):
            with self.subTest(argv=argv), patch.object(sys, "argv", argv):
                ctx = FakeContext('{"action":"KEEP","issues":[],"final_text":""}')
                self.plugin.register(ctx)
                ctx.hooks["on_skill_lifecycle"](
                    action="loaded",
                    skill_name=self.plugin.PLUGIN_SKILL,
                    session_id="",
                    task_id="session",
                )
                ctx.hooks["on_session_start"](session_id="session", platform="cli")
                ctx.hooks["pre_llm_call"](
                    session_id="session",
                    task_id="task",
                    turn_id="turn",
                    user_message="请起草报告。",
                )
                self.assertIsNone(
                    ctx.hooks["transform_llm_output"](
                        response_text="正文。", session_id="session"
                    )
                )
                self.assertEqual([], ctx.llm.calls)

    def test_post_requires_exact_ids_and_visible_response_hash(self) -> None:
        response = json.dumps(
            {
                "action": "REPLACE",
                "issues": ["REPETITION_OR_TITLE"],
                "final_text": "关于工作进展的情况说明\n\n数据接口联调已完成。",
            },
            ensure_ascii=False,
        )
        ctx = FakeContext(response)
        self.plugin.register(ctx)
        draft = "关于有关工作进展的情况说明\n\n数据接口联调已完成。"
        selected = "关于工作进展的情况说明\n\n数据接口联调已完成。"

        mismatches = (
            ("wrong-task", "turn", selected),
            ("task", "wrong-turn", selected),
            ("task", "turn", draft),
        )
        for index, (post_task, post_turn, post_response) in enumerate(mismatches):
            session_id = f"mismatch-{index}"
            ctx.hooks["on_skill_lifecycle"](
                action="loaded",
                skill_name=self.plugin.PLUGIN_SKILL,
                session_id=session_id,
            )
            ctx.hooks["pre_llm_call"](
                session_id=session_id,
                task_id="task",
                turn_id="turn",
                user_message="请起草情况说明。",
            )
            self.assertEqual(
                selected,
                ctx.hooks["transform_llm_output"](
                    response_text=draft,
                    session_id=session_id,
                ),
            )
            ctx.hooks["post_llm_call"](
                session_id=session_id,
                task_id=post_task,
                turn_id=post_turn,
                assistant_response=post_response,
                conversation_history=[{"role": "assistant", "content": draft}],
            )
            self.assertIn(session_id, self.plugin._disabled_sessions)

            ctx.hooks["on_skill_lifecycle"](
                action="loaded",
                skill_name=self.plugin.PLUGIN_SKILL,
                session_id=session_id,
            )
            ctx.hooks["pre_llm_call"](
                session_id=session_id,
                task_id="next-task",
                turn_id="next-turn",
                user_message="请起草情况说明。",
            )
            self.assertIsNone(
                ctx.hooks["transform_llm_output"](
                    response_text=draft,
                    session_id=session_id,
                )
            )
            ctx.hooks["on_session_finalize"](session_id=session_id)
        self.assertEqual(3, len(ctx.llm.calls))

    def test_overlapping_turns_disable_session_until_finalize(self) -> None:
        ctx = FakeContext('{"action":"KEEP","issues":[],"final_text":""}')
        self.plugin.register(ctx)
        session_id = "overlap"
        ctx.hooks["on_skill_lifecycle"](
            action="loaded",
            skill_name=self.plugin.PLUGIN_SKILL,
            session_id=session_id,
        )
        for index in (1, 2):
            ctx.hooks["pre_llm_call"](
                session_id=session_id,
                task_id=f"task-{index}",
                turn_id=f"turn-{index}",
                user_message="请起草报告。",
            )
        self.assertIsNone(
            ctx.hooks["transform_llm_output"](
                response_text="正文。", session_id=session_id
            )
        )
        self.assertEqual([], ctx.llm.calls)
        self.assertIn(session_id, self.plugin._disabled_sessions)

        ctx.hooks["on_session_finalize"](session_id=session_id)
        self.assertNotIn(session_id, self.plugin._disabled_sessions)

    def test_transform_in_flight_is_discarded_after_overlapping_turn(self) -> None:
        response = json.dumps(
            {
                "action": "REPLACE",
                "issues": ["REPETITION_OR_TITLE"],
                "final_text": "关于工作进展的情况说明\n\n数据接口联调已完成。",
            },
            ensure_ascii=False,
        )
        ctx = FakeContext(response)
        started = threading.Event()
        release = threading.Event()

        def blocking_complete(messages, **kwargs):
            ctx.llm.calls.append((messages, kwargs))
            started.set()
            if not release.wait(timeout=5):
                raise TimeoutError("test transform was not released")
            return SimpleNamespace(text=response)

        ctx.llm.complete = blocking_complete
        self.plugin.register(ctx)
        session_id = "overlap-in-flight"
        ctx.hooks["on_skill_lifecycle"](
            action="loaded",
            skill_name=self.plugin.PLUGIN_SKILL,
            session_id=session_id,
        )
        ctx.hooks["pre_llm_call"](
            session_id=session_id,
            task_id="task-1",
            turn_id="turn-1",
            user_message="请起草情况说明。",
        )
        draft = "关于有关工作进展的情况说明\n\n数据接口联调已完成。"
        selected: list[str | None] = []
        worker = threading.Thread(
            target=lambda: selected.append(
                ctx.hooks["transform_llm_output"](
                    response_text=draft,
                    session_id=session_id,
                )
            )
        )
        worker.start()
        self.assertTrue(started.wait(timeout=5))

        ctx.hooks["pre_llm_call"](
            session_id=session_id,
            task_id="task-2",
            turn_id="turn-2",
            user_message="请再起草情况说明。",
        )
        release.set()
        worker.join(timeout=5)

        self.assertFalse(worker.is_alive())
        self.assertEqual([None], selected)
        self.assertEqual(1, len(ctx.llm.calls))
        self.assertIn(session_id, self.plugin._disabled_sessions)
        self.assertNotIn(session_id, self.plugin._turns)

        ctx.hooks["on_session_finalize"](session_id=session_id)
        self.assertNotIn(session_id, self.plugin._disabled_sessions)

    def test_completed_turn_consumes_session_activation(self) -> None:
        ctx = FakeContext('{"action":"KEEP","issues":[],"final_text":""}')
        self.plugin.register(ctx)
        session_id = "one-turn"
        ctx.hooks["on_skill_lifecycle"](
            action="loaded",
            skill_name=self.plugin.PLUGIN_SKILL,
            session_id=session_id,
        )
        ctx.hooks["pre_llm_call"](
            session_id=session_id,
            task_id="task-1",
            turn_id="turn-1",
            user_message="请起草报告。",
        )
        self.assertIsNone(
            ctx.hooks["transform_llm_output"](
                response_text="正文。", session_id=session_id
            )
        )
        ctx.hooks["post_llm_call"](
            session_id=session_id,
            task_id="task-1",
            turn_id="turn-1",
            assistant_response="正文。",
            conversation_history=[{"role": "assistant", "content": "正文。"}],
        )
        ctx.hooks["pre_llm_call"](
            session_id=session_id,
            task_id="task-2",
            turn_id="turn-2",
            user_message="请再起草报告。",
        )
        self.assertIsNone(
            ctx.hooks["transform_llm_output"](
                response_text="第二份正文。", session_id=session_id
            )
        )
        self.assertEqual(1, len(ctx.llm.calls))

    def test_single_query_argv_classifier(self) -> None:
        self.assertTrue(
            self.plugin._is_new_single_query_cli(["chat", "-q", "prompt"])
        )
        self.assertTrue(
            self.plugin._is_new_single_query_cli(["chat", "--query=prompt"])
        )
        self.assertTrue(
            self.plugin._is_new_single_query_cli(
                ["chat", "--query-file", "prompt.txt"]
            )
        )
        self.assertTrue(
            self.plugin._is_new_single_query_cli(
                ["chat", "--query-file=prompt.txt"]
            )
        )
        for argv in (
            ["chat"],
            ["chat", "-q", "prompt", "--resume", "session"],
            ["chat", "--query=prompt", "--continue=session"],
            ["chat", "--query-file", "prompt.txt", "--resume", "session"],
            ["chat", "-q", "prompt", "--query-file", "prompt.txt"],
            ["chat", "--query=prompt", "--query-file=prompt.txt"],
            ["--oneshot", "prompt"],
            ["--oneshot", "one-shot prompt", "chat", "-q", "query prompt"],
            ["chat", "--query=prompt", "--oneshot=one-shot prompt"],
            ["gateway", "chat", "-q", "query prompt"],
        ):
            with self.subTest(argv=argv):
                self.assertFalse(self.plugin._is_new_single_query_cli(argv))

    def test_unsupported_invocation_does_not_leave_pending_preload(self) -> None:
        ctx = FakeContext('{"action":"KEEP","issues":[],"final_text":""}')
        self.plugin.register(ctx)
        with patch.object(sys, "argv", ["hermes", "--oneshot", "prompt"]):
            ctx.hooks["on_skill_lifecycle"](
                action="loaded",
                skill_name=self.plugin.PLUGIN_SKILL,
                session_id="",
                task_id="future-session",
            )
        self.assertNotIn("future-session", self.plugin._pending_cli_preloads)

        ctx.hooks["on_session_start"](
            session_id="future-session",
            platform="cli",
        )
        ctx.hooks["pre_llm_call"](
            session_id="future-session",
            task_id="task",
            turn_id="turn",
            user_message="请起草报告。",
        )
        self.assertIsNone(
            ctx.hooks["transform_llm_output"](
                response_text="正文。",
                session_id="future-session",
            )
        )
        self.assertEqual([], ctx.llm.calls)

    def test_wrong_skill_review_only_and_task_opt_out_do_not_call_llm(self) -> None:
        ctx = FakeContext('{"action":"KEEP","issues":[],"final_text":""}')
        self.plugin.register(ctx)

        ctx.hooks["on_session_start"](session_id="wrong-skill")
        ctx.hooks["pre_llm_call"](
            session_id="wrong-skill",
            user_message="请起草报告。",
        )
        self.assertIsNone(
            ctx.hooks["transform_llm_output"](
                response_text="正文。", session_id="wrong-skill"
            )
        )

        for session_id, request in (
            ("review-only", "只审不改这份采购申请。"),
            ("opt-out", "本次关闭 Hook，按普通 Skill 完成。"),
        ):
            ctx.hooks["on_skill_lifecycle"](
                action="loaded",
                skill_name=self.plugin.PLUGIN_SKILL,
                session_id=session_id,
                task_id="task",
            )
            ctx.hooks["pre_llm_call"](
                session_id=session_id,
                user_message=request,
            )
            self.assertIsNone(
                ctx.hooks["transform_llm_output"](
                    response_text="正文。", session_id=session_id
                )
            )
        self.assertEqual([], ctx.llm.calls)

    def test_non_delivery_capability_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaisesRegex(ValueError, "delivery_review only"):
                ASSEMBLER.assemble(
                    "hermes-agent",
                    Path(temporary) / "hermes-over-length",
                    "over_length",
                )


if __name__ == "__main__":
    unittest.main()
