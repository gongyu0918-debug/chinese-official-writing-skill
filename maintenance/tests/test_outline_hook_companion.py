from __future__ import annotations

from contextlib import redirect_stdout
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from maintenance.tests.hook_companion_support import ASSEMBLER, load_module


ROOT = Path(__file__).resolve().parents[2]
OUTLINE_MODULE = load_module(
    "outline_prompt_contract",
    ROOT
    / "chinese-official-writing"
    / "hooks"
    / "capabilities"
    / "outline_assist"
    / "outline_prompt_hook.py",
)
CODEX_MODULE = load_module(
    "cow_codex_outline_prompt_hook",
    ROOT
    / "chinese-official-writing"
    / "hooks"
    / "capabilities"
    / "outline_assist"
    / "codex_outline_prompt_hook.py",
)


def _root_prompt(text: str) -> dict[str, object]:
    return {
        "type": "user",
        "isSynthetic": False,
        "message": {"role": "user", "content": text},
    }


def _completed_outline_call(tool_id: str = "outline-call") -> list[dict[str, object]]:
    return [
        {
            "type": "assistant",
            "message": {
                "role": "assistant",
                "content": [
                    {
                        "type": "tool_use",
                        "id": tool_id,
                        "name": "Agent",
                        "input": {
                            "subagent_type": OUTLINE_MODULE.OUTLINE_AGENT,
                            "prompt": "task",
                        },
                    }
                ],
            },
        },
        {
            "type": "user",
            "message": {
                "role": "user",
                "content": [{"type": "tool_result", "tool_use_id": tool_id}],
            },
            "toolUseResult": {
                "status": "completed",
                "agentType": OUTLINE_MODULE.OUTLINE_AGENT,
            },
        },
    ]


def _codebuddy_completed_outline_call(
    call_id: str = "outline-call",
) -> list[dict[str, object]]:
    return [
        {
            "type": "function_call",
            "name": "Agent",
            "callId": call_id,
            "arguments": json.dumps(
                {"subagent_type": "outline-planner", "prompt": "task"}
            ),
        },
        {
            "type": "function_call_result",
            "name": "Agent",
            "callId": call_id,
            "status": "completed",
        },
    ]


class OutlineHookCompanionTests(unittest.TestCase):
    def test_assembler_builds_three_self_contained_host_companions(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            hosts = {
                "codex": (".codex-plugin/plugin.json", False, "spawn_agent"),
                "codebuddy": (".codebuddy-plugin/plugin.json", True, "Agent"),
                "claude-code": (".claude-plugin/plugin.json", True, "Agent"),
            }
            for host, (manifest, has_agent, matcher) in hosts.items():
                with self.subTest(host=host):
                    output = root / host
                    result = ASSEMBLER.assemble(host, output, "outline_assist")
                    self.assertEqual("outline_assist", result["capability"])
                    self.assertFalse(result["installed"])
                    self.assertFalse(result["enabled"])
                    self.assertFalse(result["network_used"])
                    self.assertTrue((output / manifest).is_file())
                    self.assertEqual(
                        has_agent, (output / "agents/outline-planner.md").is_file()
                    )
                    self.assertEqual(
                        host == "codex",
                        (output / "scripts/outline_prompt_contract.py").is_file(),
                    )
                    self.assertTrue((output / "scripts/outline_prompt_hook.py").is_file())
                    packaged = output / "skills/chinese-official-writing"
                    self.assertTrue((packaged / "SKILL.md").is_file())
                    self.assertTrue((packaged / "scripts/prose_lint.py").is_file())
                    self.assertFalse((packaged / "hooks").exists())
                    self.assertFalse((packaged / "scripts/review_gate.py").exists())
                    self.assertNotIn(
                        "hooks/README.md",
                        (packaged / "SKILL.md").read_text(encoding="utf-8"),
                    )
                    hooks = json.loads(
                        (output / "hooks/hooks.json").read_text(encoding="utf-8")
                    )["hooks"]
                    self.assertEqual(
                        ["UserPromptSubmit", "PostToolUse", "Stop"], list(hooks)
                    )
                    self.assertIn(matcher, hooks["PostToolUse"][0]["matcher"])

    def test_stop_scope_requires_a_completed_outline_call_in_current_turn(self) -> None:
        current = [_root_prompt("请起草通知"), *_completed_outline_call()]
        self.assertTrue(OUTLINE_MODULE._completed_outline_call(current))
        incomplete = [
            _root_prompt("请起草通知"),
            _completed_outline_call()[0],
        ]
        self.assertFalse(OUTLINE_MODULE._completed_outline_call(incomplete))
        later_turn = [*current, _root_prompt("请帮我审核这份稿件")]
        self.assertFalse(OUTLINE_MODULE._completed_outline_call(later_turn))

    def test_codebuddy_transcript_shape_completes_only_the_current_turn(self) -> None:
        prompt = {
            "type": "message",
            "role": "user",
            "content": [{"type": "input_text", "text": "请起草通知"}],
        }
        current = [prompt, *_codebuddy_completed_outline_call()]
        self.assertTrue(OUTLINE_MODULE._completed_outline_call(current))
        self.assertFalse(
            OUTLINE_MODULE._completed_outline_call([*current, {**prompt}])
        )

    def test_codebuddy_stop_feedback_does_not_reinject_the_outline_route(self) -> None:
        output = io.StringIO()
        with redirect_stdout(output):
            OUTLINE_MODULE.handle(
                {
                    "hook_event_name": "UserPromptSubmit",
                    "prompt": "Stop hook feedback:请核对提纲",
                }
            )
        self.assertEqual("", output.getvalue())

    def test_codebuddy_uses_its_local_agent_alias(self) -> None:
        output = io.StringIO()
        with patch.dict(os.environ, {"CODEBUDDY_PLUGIN_ROOT": "C:/plugin"}):
            with redirect_stdout(output):
                OUTLINE_MODULE.handle(
                    {"hook_event_name": "UserPromptSubmit", "prompt": "请起草通知"}
                )
        route = output.getvalue()
        self.assertIn("subagent_type `outline-planner`", route)
        self.assertNotIn(OUTLINE_MODULE.OUTLINE_AGENT, route)

    def test_codex_state_machine_reaches_one_bounded_stop_and_completion(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = {"session_id": "session", "turn_id": "turn"}
            with patch.dict(os.environ, {"PLUGIN_DATA": temporary}):
                output = io.StringIO()
                with redirect_stdout(output):
                    CODEX_MODULE.handle(
                        {**base, "hook_event_name": "UserPromptSubmit", "prompt": "请起草通知"}
                    )
                self.assertIn("chinese-official-writing-outline:chinese-official-writing", output.getvalue())
                CODEX_MODULE.handle(
                    {
                        **base,
                        "hook_event_name": "PostToolUse",
                        "tool_name": "spawn_agent",
                        "tool_input": {"message": f"{CODEX_MODULE.OUTLINE_MARKER}\ntask"},
                        "tool_response": json.dumps({"agent_id": "agent-1"}),
                    }
                )
                output = io.StringIO()
                with redirect_stdout(output):
                    CODEX_MODULE.handle(
                        {
                            **base,
                            "hook_event_name": "PostToolUse",
                            "tool_name": "multi_agent_v1wait_agent",
                            "tool_input": {"targets": ["agent-1"]},
                            "tool_response": json.dumps(
                                {"status": {"agent-1": {"completed": "outline"}}}
                            ),
                        }
                    )
                self.assertIn("hookSpecificOutput", output.getvalue())
                output = io.StringIO()
                with redirect_stdout(output):
                    CODEX_MODULE.handle(
                        {**base, "hook_event_name": "Stop", "stop_hook_active": False}
                    )
                self.assertIn('"decision": "block"', output.getvalue())
                CODEX_MODULE.handle(
                    {**base, "hook_event_name": "Stop", "stop_hook_active": True}
                )
                state = json.loads(
                    (
                        Path(temporary) / "outline-assist/session-turn.json"
                    ).read_text(encoding="utf-8")
                )
                self.assertEqual("complete", state["phase"])

    def test_explicit_task_opt_out_emits_no_outline_route(self) -> None:
        for prompt in (
            "本次关闭 Hook，按普通 Skill 起草通知",
            "这次不要用提纲 hooks，直接写报告",
            "跳过 Hook，起草方案",
        ):
            with self.subTest(prompt=prompt), io.StringIO() as output, redirect_stdout(output):
                OUTLINE_MODULE.handle(
                    {"hook_event_name": "UserPromptSubmit", "prompt": prompt}
                )
                self.assertEqual("", output.getvalue())

    def test_negated_or_generic_language_does_not_disable_outline_route(self) -> None:
        for prompt in (
            "不要关闭 Hook，请起草通知",
            "继续使用提纲 Hook 起草报告",
            "不要用脚本，直接起草方案",
        ):
            with self.subTest(prompt=prompt), io.StringIO() as output, redirect_stdout(output):
                OUTLINE_MODULE.handle(
                    {"hook_event_name": "UserPromptSubmit", "prompt": prompt}
                )
                self.assertIn("hookSpecificOutput", output.getvalue())

    def test_capability_manifest_exposes_only_bounded_events(self) -> None:
        source = (
            ROOT
            / "chinese-official-writing"
            / "hooks"
            / "capabilities"
            / "outline_assist"
        )
        hooks = json.loads((source / "hooks.json").read_text(encoding="utf-8"))["hooks"]
        self.assertEqual(["UserPromptSubmit", "PostToolUse", "Stop"], list(hooks))
        self.assertEqual("Agent", hooks["PostToolUse"][0]["matcher"])
        script = (source / "outline_prompt_hook.py").read_text(encoding="utf-8")
        self.assertNotIn("import requests", script)
        self.assertNotIn("from requests", script)
        self.assertNotIn("subprocess", script)
        self.assertNotIn("write_text", script)
        self.assertIn("不得为了精简而改写或删除", OUTLINE_MODULE.OUTLINE_REPAIR)
        self.assertIn("没有明确纲外内容时原样重发", OUTLINE_MODULE.OUTLINE_REPAIR)
        self.assertIn("只改局部时，标题写", OUTLINE_MODULE.OUTLINE_ROUTE)
        self.assertIn("只输出正文", OUTLINE_MODULE.OUTLINE_ROUTE)
        planner = (source / "outline-planner.md").read_text(encoding="utf-8")
        self.assertIn("derive one concise title", planner)
        self.assertIn("只输出正文", planner)
        self.assertIn("never split it merely to reach a section count", planner)
        self.assertIn("不得为了凑章节拆分", OUTLINE_MODULE.OUTLINE_ROUTE)
        self.assertIn("正文（不设小标题）", OUTLINE_MODULE.OUTLINE_ROUTE)
        self.assertIn("do not print it, number it", OUTLINE_MODULE.OUTLINE_FREEZE)


if __name__ == "__main__":
    unittest.main()
