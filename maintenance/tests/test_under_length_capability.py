from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
CORE_PATH = ROOT / "chinese-official-writing/hooks/core/gate_stop_hook.py"
RUNTIME_PATH = ROOT / "chinese-official-writing/hooks/capabilities/under_length/runtime.py"
SKILL_PATH = ROOT / "chinese-official-writing/SKILL.md"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


CORE = load_module("under_length_core", CORE_PATH)
RUNTIME = load_module("under_length_runtime", RUNTIME_PATH)


class UnderLengthCapabilityTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.previous = {
            key: os.environ.get(key)
            for key in ("COW_GATE_HOOK_DATA", "COW_GATE_CAPABILITY")
        }
        os.environ["COW_GATE_HOOK_DATA"] = str(self.root / "data")
        os.environ["COW_GATE_CAPABILITY"] = "under_length"
        self.addCleanup(self.restore_environment)

    def restore_environment(self) -> None:
        for key, value in self.previous.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

    def event(self, name: str, **extra) -> dict:
        value = {
            "hook_event_name": name,
            "session_id": "under-session",
            "turn_id": "under-turn",
            "cwd": str(ROOT),
        }
        value.update(extra)
        return value

    def arm(self, request: str) -> None:
        CORE.handle(self.event("UserPromptSubmit", prompt=request))
        CORE.handle(
            self.event(
                "PostToolUse",
                tool_input={"cmd": f'Get-Content "{SKILL_PATH}"'},
                tool_response={"exit_code": 0},
            )
        )

    def record(self) -> dict:
        record_path = next((self.root / "data").rglob("under-turn.json"))
        return json.loads(record_path.read_text(encoding="utf-8"))

    def test_explicit_under_range_completes_hash_bound_d1(self) -> None:
        request = (
            "请起草120—180字通知。事实：组织业务培训，内容围绕日常业务；"
            "要求各部门统筹工作与学习，参训人员完成学习任务并学以致用。只输出正文。"
        )
        d0 = "关于开展业务培训的通知\n\n各部门：\n为提升业务能力，现组织业务培训，请按要求参加。"
        d1 = (
            "关于开展业务培训的通知\n\n各部门：\n为提升业务能力，现组织业务培训。培训内容围绕日常业务展开，"
            "注重学习内容与实际工作的衔接。各部门要统筹工作与学习安排，参训人员应认真完成学习任务，"
            "并把所学内容用于改进日常工作。请各部门结合工作安排组织参训，确保培训学习与日常业务有序衔接。"
        )
        self.assertGreaterEqual(RUNTIME.count_text(d1, "full"), 120)
        self.arm(request)
        first = CORE.handle(self.event("Stop", stop_hook_active=False, last_assistant_message=d0))
        self.assertEqual("block", first["decision"])
        second = CORE.handle(self.event("Stop", last_assistant_message=d1))
        self.assertEqual("block", second["decision"])
        state = self.record()["under_length"]
        increments = state["increments"]
        verdict = {
            "schema_version": 1,
            "request_sha256": RUNTIME._sha256_text(request),
            "d0_sha256": RUNTIME._sha256_text(d0),
            "d1_sha256": RUNTIME._sha256_text(d1),
            "verdict": "PASS",
            "checks": {
                "no_new_specific_fact": True,
                "facts_and_states_preserved": True,
                "length_genre_and_naturalness_preserved": True,
            },
            "increments": [{**item, "category": "transparent_derivation"} for item in increments],
        }
        third = CORE.handle(
            self.event("Stop", last_assistant_message=json.dumps(verdict, ensure_ascii=False))
        )
        self.assertIn(d1, third["reason"])
        final = CORE.handle(self.event("Stop", last_assistant_message=d1))
        self.assertTrue(final["continue"])
        self.assertTrue(self.record()["under_length"]["audit"]["delivery_verified"])

    def test_within_range_material_quote_review_and_opt_out_do_not_start(self) -> None:
        within = "内容" * 70
        for index, request in enumerate(
            (
                "请起草100—180字通知，只输出正文。",
                "请解释制度中正文不少于100字的含义。",
                "请审核这份100—180字通知，不要改正文。",
                "请起草100—180字通知，本次关闭 Hook。",
            )
        ):
            with self.subTest(request=request):
                event = {"session_id": f"s{index}", "turn_id": f"t{index}", "cwd": str(ROOT)}
                CORE.handle({**event, "hook_event_name": "UserPromptSubmit", "prompt": request})
                CORE.handle(
                    {
                        **event,
                        "hook_event_name": "PostToolUse",
                        "tool_input": {"cmd": f'Get-Content "{SKILL_PATH}"'},
                        "tool_response": {"exit_code": 0},
                    }
                )
                result = CORE.handle(
                    {**event, "hook_event_name": "Stop", "stop_hook_active": False, "last_assistant_message": within}
                )
                record_path = next((self.root / "data").rglob(f"t{index}.json"))
                record = json.loads(record_path.read_text(encoding="utf-8"))
                self.assertNotIn("under_length", record)
                if "关闭 Hook" in request:
                    self.assertTrue(result["continue"])

    def test_explicit_permission_to_miss_lower_bound_does_not_start(self) -> None:
        request = (
            "请起草800—900字通知。材料不足时宁可短于下限，不得重复凑字。"
        )
        self.arm(request)
        result = CORE.handle(
            self.event(
                "Stop",
                stop_hook_active=False,
                last_assistant_message="会议通知\n\n各部门：\n定于明日召开会议。特此通知。",
            )
        )
        self.assertIsInstance(result, dict)
        record = self.record()
        self.assertNotIn("under_length", record)
        self.assertEqual("user_allows_shortfall", record["under_length_bypass"])

    def test_material_explanation_is_not_an_output_length_spec(self) -> None:
        self.assertIsNone(RUNTIME.parse_spec("请解释制度中正文不少于100字的含义。"))
        self.assertEqual(
            {"minimum": 280, "maximum": 360, "scope": "full"},
            RUNTIME.parse_spec("请根据材料起草一篇280—360字的新闻消息，只输出正文。"),
        )

    def test_mechanical_gate_rejects_new_number_and_status_upgrade(self) -> None:
        spec = {"minimum": 1, "maximum": 0, "scope": "full"}
        self.assertEqual(
            "under_length_number_added_dropped_or_changed",
            RUNTIME.mechanical_reason("正在核查。", "正在核查，共3项。", spec, ""),
        )
        self.assertEqual(
            "under_length_status_upgraded",
            RUNTIME.mechanical_reason("事项正在核查。", "事项核查完成。", spec, ""),
        )

    def test_request_supplied_numbers_and_transparent_count_reach_semantic_verifier(self) -> None:
        spec = {"minimum": 1, "maximum": 0, "scope": "full"}
        request = "起草800—900字通知。会议时间为9月15日9时，议程共四项。"
        original = "会议定于9月15日9时召开。议程如下。"
        candidate = "会议定于9月15日9时召开。本次议程共四项，具体如下。"
        self.assertIsNone(RUNTIME.mechanical_reason(original, candidate, spec, request))
        self.assertEqual(
            "under_length_number_added_dropped_or_changed",
            RUNTIME.mechanical_reason(original, candidate + "共3个环节。", spec, request),
        )

    def test_planned_improvement_equivalent_is_not_mechanically_rejected(self) -> None:
        spec = {"minimum": 1, "maximum": 0, "scope": "full"}
        original = "下一年度拟完善培训安排。"
        candidate = "将在下一年度改进培训安排，并结合既有工作逐步优化培训内容。"
        self.assertIsNone(RUNTIME.mechanical_reason(original, candidate, spec, ""))

    def test_unsupported_added_process_is_rejected_but_request_grounded_action_is_allowed(self) -> None:
        original = "会议安排四项议程。"
        unsafe = "会议安排四项议程。请各部门提前通知参会人员，并保持通讯畅通。"
        unsafe_items = RUNTIME._increment_items(original, unsafe)
        self.assertEqual(
            "under_length_unsupported_added_process",
            RUNTIME._unsupported_added_process("会议安排四项议程。", original, unsafe_items),
        )

        request = "会议安排四项议程，请各部门提前通知参会人员。"
        grounded = original + "请各部门提前通知参会人员。"
        grounded_items = RUNTIME._increment_items(original, grounded)
        self.assertIsNone(
            RUNTIME._unsupported_added_process(request, original, grounded_items)
        )

    def test_ongoing_investigation_equivalent_reaches_semantic_verifier(self) -> None:
        spec = {"minimum": 1, "maximum": 0, "scope": "full"}
        original = "目前，事故原因正在调查中。"
        candidate = "目前，事故原因正在进一步调查中，相关情况将根据调查进展说明。"
        self.assertIsNone(RUNTIME.mechanical_reason(original, candidate, spec, ""))
