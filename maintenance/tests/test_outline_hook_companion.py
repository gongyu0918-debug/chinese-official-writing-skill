from __future__ import annotations

from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import tempfile
import unittest

from maintenance.tests.hook_companion_support import ASSEMBLER, load_module


ROOT = Path(__file__).resolve().parents[2]
OUTLINE_MODULE = load_module(
    "cow_outline_prompt_hook",
    ROOT
    / "chinese-official-writing"
    / "hooks"
    / "capabilities"
    / "outline_assist"
    / "outline_prompt_hook.py",
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


class OutlineHookCompanionTests(unittest.TestCase):
    def test_assembler_builds_a_claude_only_self_contained_companion(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "outline"
            result = ASSEMBLER.assemble("claude-code", output, "outline_assist")
            self.assertEqual("outline_assist", result["capability"])
            self.assertFalse(result["installed"])
            self.assertFalse(result["enabled"])
            self.assertFalse(result["network_used"])
            self.assertTrue((output / ".claude-plugin/plugin.json").is_file())
            self.assertTrue((output / "agents/outline-planner.md").is_file())
            self.assertTrue((output / "scripts/outline_prompt_hook.py").is_file())
            packaged = output / "skills/chinese-official-writing"
            self.assertTrue((packaged / "SKILL.md").is_file())
            self.assertTrue((packaged / "scripts/prose_lint.py").is_file())
            self.assertFalse((packaged / "hooks").exists())
            self.assertFalse((packaged / "scripts/review_gate.py").exists())
            self.assertNotIn(
                "hooks/README.md", (packaged / "SKILL.md").read_text(encoding="utf-8")
            )
            hooks = json.loads((output / "hooks/hooks.json").read_text(encoding="utf-8"))[
                "hooks"
            ]
            self.assertEqual(["UserPromptSubmit", "PostToolUse", "Stop"], list(hooks))
            self.assertEqual("Agent", hooks["PostToolUse"][0]["matcher"])

    def test_assembler_rejects_unverified_outline_hosts(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for host in ("codex", "codebuddy"):
                with self.subTest(host=host):
                    with self.assertRaisesRegex(ValueError, "Claude Code only"):
                        ASSEMBLER.assemble(host, root / host, "outline_assist")

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


if __name__ == "__main__":
    unittest.main()
