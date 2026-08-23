from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest

from maintenance.tests.hook_companion_support import ASSEMBLER


ROOT = Path(__file__).resolve().parents[2]
RUNTIME_PATH = ROOT / "chinese-official-writing/hooks/capabilities/delivery_cleanliness/runtime.py"
CORE_PATH = ROOT / "chinese-official-writing/hooks/core/gate_stop_hook.py"
HOST_ADAPTER_PATH = ROOT / "chinese-official-writing/hooks/adapters/host_gate_adapter.py"
CLAUDE_ADAPTER_PATH = ROOT / "chinese-official-writing/hooks/adapters/claude-code/gate_stop_hook.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


RUNTIME = load_module("cow_delivery_cleanliness_test_runtime", RUNTIME_PATH)
CORE = load_module("cow_delivery_cleanliness_test_core", CORE_PATH)
HOST_ADAPTER = load_module("cow_delivery_cleanliness_test_host_adapter", HOST_ADAPTER_PATH)
CLAUDE_ADAPTER = load_module("cow_delivery_cleanliness_test_claude_adapter", CLAUDE_ADAPTER_PATH)


class DeliveryCleanlinessCapabilityTests(unittest.TestCase):
    def test_both_static_adapter_families_accept_the_capability(self):
        self.assertIn("delivery_cleanliness", HOST_ADAPTER.SUPPORTED_CAPABILITIES)
        self.assertIn("delivery_cleanliness", CLAUDE_ADAPTER.SUPPORTED_CAPABILITIES)

    def _verdict(self, record: dict) -> str:
        state = record["delivery_cleanliness"]
        return json.dumps(
            {
                "schema_version": 1,
                "request_sha256": RUNTIME._sha256_text(record["request"]),
                "d0_sha256": RUNTIME._sha256_text(state["original"]),
                "d1_sha256": RUNTIME._sha256_text(state["candidate"]),
                "verdict": "PASS",
                "checks": {
                    "only_unrequested_non_body_removed": True,
                    "body_facts_states_and_order_preserved": True,
                    "requested_format_preserved": True,
                    "candidate_directly_usable": True,
                },
                "deletions": [
                    {**item, "category": "process_narration"}
                    for item in state["deletions"]
                ],
            },
            ensure_ascii=False,
        )

    def test_dirty_draft_reaches_hash_verified_d1(self):
        original = (
            "由于当前环境无法调用外部工具，以下内容已改为人工核对。以下直接交付正文。\n\n"
            "情况说明\n\n经核查，系统于8月12日出现短时异常。目前，技术人员正在核查。"
        )
        candidate = "情况说明\n\n经核查，系统于8月12日出现短时异常。目前，技术人员正在核查。"
        record = {"request": "请起草一份情况说明，只输出正文。"}
        started = RUNTIME.start({"last_assistant_message": original}, record)
        self.assertIn("交付洁净度", started["reason"])
        verdict_request = RUNTIME.advance({"last_assistant_message": candidate}, record)
        self.assertIn("只读核验", verdict_request["reason"])
        selected = RUNTIME.advance(
            {"last_assistant_message": self._verdict(record)}, record
        )
        self.assertIn(candidate, selected["reason"])
        self.assertEqual("D1", record["delivery_cleanliness"]["audit"]["selection"])
        completed = RUNTIME.advance({"last_assistant_message": candidate}, record)
        self.assertTrue(completed["continue"])
        self.assertTrue(record["delivery_cleanliness"]["audit"]["delivery_verified"])

    def test_clean_and_requested_markdown_are_byte_identical_d0(self):
        for request, original in (
            ("请起草情况说明，只输出正文。", "情况说明\n\n经核查，系统运行正常。"),
            (
                "请用 Markdown 输出以下通知，保留标题层级。",
                "# 通知\n\n## 一、时间\n\n8月15日。",
            ),
        ):
            with self.subTest(request=request):
                record = {"request": request}
                RUNTIME.start({"last_assistant_message": original}, record)
                selected = RUNTIME.advance({"last_assistant_message": original}, record)
                self.assertIn(original, selected["reason"])
                self.assertEqual("D0", record["delivery_cleanliness"]["audit"]["selection"])

    def test_any_insertion_or_rewrite_falls_back_to_d0(self):
        original = "情况说明\n\n系统正在核查。"
        record = {"request": "请起草情况说明。"}
        RUNTIME.start({"last_assistant_message": original}, record)
        RUNTIME.advance(
            {"last_assistant_message": "情况说明\n\n系统正在全面核查。"}, record
        )
        audit = record["delivery_cleanliness"]["audit"]
        self.assertEqual("D0", audit["selection"])
        self.assertEqual("delivery_cleanliness_not_deletion_only", audit["reason"])

    def test_core_selection_and_user_opt_out_are_independent(self):
        with tempfile.TemporaryDirectory() as temporary:
            old = {
                key: os.environ.get(key)
                for key in ("COW_GATE_HOOK_DATA", "COW_GATE_CAPABILITY")
            }
            os.environ["COW_GATE_HOOK_DATA"] = temporary
            os.environ["COW_GATE_CAPABILITY"] = "delivery_cleanliness"
            try:
                base = {
                    "session_id": "clean-session",
                    "turn_id": "clean-turn",
                    "cwd": temporary,
                }
                CORE.handle({**base, "hook_event_name": "UserPromptSubmit", "prompt": "请起草情况说明。"})
                CORE.handle(
                    {
                        **base,
                        "hook_event_name": "PostToolUse",
                        "tool_input": {"cmd": f'Get-Content "{ROOT / "chinese-official-writing/SKILL.md"}"'},
                        "tool_response": {"exit_code": 0},
                    }
                )
                stopped = CORE.handle(
                    {
                        **base,
                        "hook_event_name": "Stop",
                        "stop_hook_active": False,
                        "last_assistant_message": "情况说明\n\n系统正在核查。",
                    }
                )
                self.assertIn("交付洁净度", stopped["reason"])

                bypass = {**base, "turn_id": "bypass-turn"}
                CORE.handle(
                    {
                        **bypass,
                        "hook_event_name": "UserPromptSubmit",
                        "prompt": "本次关闭 Hook，请起草情况说明。",
                    }
                )
                CORE.handle(
                    {
                        **bypass,
                        "hook_event_name": "PostToolUse",
                        "tool_input": {"cmd": f'Get-Content "{ROOT / "chinese-official-writing/SKILL.md"}"'},
                        "tool_response": {"exit_code": 0},
                    }
                )
                allowed = CORE.handle(
                    {
                        **bypass,
                        "hook_event_name": "Stop",
                        "stop_hook_active": False,
                        "last_assistant_message": "情况说明\n\n系统正在核查。",
                    }
                )
                self.assertEqual({"continue": True}, allowed)
            finally:
                for key, value in old.items():
                    if value is None:
                        os.environ.pop(key, None)
                    else:
                        os.environ[key] = value

    def test_core_terminal_delivery_redacts_cleanliness_text(self):
        with tempfile.TemporaryDirectory() as temporary:
            old = {
                key: os.environ.get(key)
                for key in ("COW_GATE_HOOK_DATA", "COW_GATE_CAPABILITY")
            }
            os.environ["COW_GATE_HOOK_DATA"] = temporary
            os.environ["COW_GATE_CAPABILITY"] = "delivery_cleanliness"
            try:
                base = {
                    "session_id": "clean-redact-session",
                    "turn_id": "clean-redact-turn",
                    "cwd": temporary,
                }
                request = "请起草情况说明，只输出正文。"
                original = (
                    "以下是处理说明，请核对。\n\n"
                    "情况说明\n\n系统于8月12日出现短时异常，目前正在核查。"
                )
                candidate = "情况说明\n\n系统于8月12日出现短时异常，目前正在核查。"
                CORE.handle(
                    {**base, "hook_event_name": "UserPromptSubmit", "prompt": request}
                )
                CORE.handle(
                    {
                        **base,
                        "hook_event_name": "PostToolUse",
                        "tool_input": {
                            "cmd": f'Get-Content "{ROOT / "chinese-official-writing/SKILL.md"}"'
                        },
                        "tool_response": {"exit_code": 0},
                    }
                )
                first = CORE.handle(
                    {
                        **base,
                        "hook_event_name": "Stop",
                        "stop_hook_active": False,
                        "last_assistant_message": original,
                    }
                )
                self.assertEqual("block", first["decision"])
                second = CORE.handle(
                    {
                        **base,
                        "hook_event_name": "Stop",
                        "last_assistant_message": candidate,
                    }
                )
                self.assertIn("只读核验", second["reason"])
                record_path = CORE._record_path(
                    {**base, "hook_event_name": "Stop"}
                )
                record = CORE._read_json(record_path)
                third = CORE.handle(
                    {
                        **base,
                        "hook_event_name": "Stop",
                        "last_assistant_message": self._verdict(record),
                    }
                )
                self.assertIn(candidate, third["reason"])
                final = CORE.handle(
                    {
                        **base,
                        "hook_event_name": "Stop",
                        "last_assistant_message": candidate,
                    }
                )
                self.assertEqual({"continue": True}, final)
                redacted = CORE._read_json(record_path)
                self.assertEqual(
                    CORE.REDACTED_RECORD_STATE, redacted["data_retention_state"]
                )
                self.assertNotIn("request", redacted)
                self.assertNotIn("original", redacted["delivery_cleanliness"])
                self.assertNotIn("candidate", redacted["delivery_cleanliness"])
                self.assertNotIn("deletions", redacted["delivery_cleanliness"])
                serialized = json.dumps(redacted, ensure_ascii=False)
                self.assertNotIn("处理说明", serialized)
                self.assertNotIn("短时异常", serialized)
            finally:
                for key, value in old.items():
                    if value is None:
                        os.environ.pop(key, None)
                    else:
                        os.environ[key] = value

    def test_all_static_companions_include_the_selected_capability(self):
        with tempfile.TemporaryDirectory() as temporary:
            for host in ("codex", "codebuddy", "claude-code", "zcode"):
                with self.subTest(host=host):
                    output = Path(temporary) / host
                    result = ASSEMBLER.assemble(host, output, "delivery_cleanliness")
                    self.assertEqual("delivery_cleanliness", result["capability"])
                    packaged = output / "skills/chinese-official-writing"
                    self.assertTrue(
                        (packaged / "hooks/capabilities/delivery_cleanliness/runtime.py").is_file()
                    )
                    self.assertFalse(result["installed"])
                    self.assertFalse(result["enabled"])


if __name__ == "__main__":
    unittest.main()
