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
RUNTIME_PATH = ROOT / "chinese-official-writing/hooks/capabilities/over_length/runtime.py"
SKILL_PATH = ROOT / "chinese-official-writing/SKILL.md"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


CORE = load_module("over_length_core", CORE_PATH)
RUNTIME = load_module("over_length_runtime", RUNTIME_PATH)


class OverLengthCapabilityTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.previous = {
            key: os.environ.get(key)
            for key in ("COW_GATE_HOOK_DATA", "COW_GATE_CAPABILITY")
        }
        os.environ["COW_GATE_HOOK_DATA"] = str(self.root / "data")
        os.environ["COW_GATE_CAPABILITY"] = "over_length"
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
            "session_id": "over-session",
            "turn_id": "over-turn",
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
        path = next((self.root / "data").rglob("over-turn.json"))
        return json.loads(path.read_text(encoding="utf-8"))

    @staticmethod
    def clear_response(packet: dict) -> dict:
        return {
            "schema_version": 1,
            "packet_sha256": packet["packet_sha256"],
            "request_sha256": packet["request_sha256"],
            "draft_sha256": packet["draft_sha256"],
            "decision": "CLEAR",
            "selections": [],
        }

    def test_clear_then_compress_completes_hash_bound_d1(self) -> None:
        request = "请将工作情况报告压缩到不超过420字，只输出正文。"
        sentence = (
            "运行管理科负责核对材料，业务科室负责补正，信息技术科负责系统配置，"
            "各项工作依照原有职责有序办理。"
        )
        d0 = "工作情况报告\n\n" + sentence * 12
        d1 = (
            "工作情况报告\n\n"
            "运行管理科负责核对材料，业务科室根据反馈完成补正，信息技术科据此进行系统配置。"
            "各环节依照原有职责衔接办理，材料核对、补正和配置结果分别由相应科室确认。"
        )
        self.assertGreater(RUNTIME.count_text(d0, "full"), 462)
        self.assertLessEqual(RUNTIME.count_text(d1, "full"), 420)
        self.arm(request)

        first = CORE.handle(
            self.event("Stop", stop_hook_active=False, last_assistant_message=d0)
        )
        self.assertEqual("block", first["decision"])
        packet = self.record()["over_length"]["repetition_packet"]

        second = CORE.handle(
            self.event(
                "Stop",
                last_assistant_message=json.dumps(
                    self.clear_response(packet), ensure_ascii=False
                ),
            )
        )
        self.assertIn("目标为", second["reason"])

        third = CORE.handle(self.event("Stop", last_assistant_message=d1))
        self.assertIn("只读核验压缩稿", third["reason"])
        verdict = {
            "schema_version": 1,
            "request_sha256": RUNTIME._sha256_text(request),
            "original_sha256": RUNTIME._sha256_text(d0),
            "candidate_sha256": RUNTIME._sha256_text(d1),
            "verdict": "PASS",
            "checks": {
                "no_new_specific_fact": True,
                "facts_and_states_complete": True,
                "responsibilities_and_relations_preserved": True,
                "genre_structure_preserved": True,
                "natural_and_non_repetitive": True,
            },
            "reason": "事实与职责关系完整，重复表述已合并。",
        }
        fourth = CORE.handle(
            self.event(
                "Stop", last_assistant_message=json.dumps(verdict, ensure_ascii=False)
            )
        )
        self.assertIn(d1, fourth["reason"])
        final = CORE.handle(self.event("Stop", last_assistant_message=d1))
        self.assertTrue(final["continue"])
        audit = self.record()["over_length"]["audit"]
        self.assertEqual("D1", audit["selection"])
        self.assertTrue(audit["delivery_verified"])

    def test_second_compression_is_bounded_and_then_falls_back(self) -> None:
        request = "请将情况说明压缩到不超过100字，只输出正文。"
        d0 = "情况说明\n\n" + "事项正在按原有安排办理，相关责任保持不变。" * 12
        record = {"request": request}
        first = RUNTIME.start(
            {"last_assistant_message": d0}, record
        )
        self.assertEqual("block", first["decision"])
        packet = record["over_length"]["repetition_packet"]
        RUNTIME.advance(
            {"last_assistant_message": json.dumps(self.clear_response(packet), ensure_ascii=False)},
            record,
        )
        still_long = "情况说明\n\n" + "事项正在按原有安排办理，相关责任保持不变。" * 8
        retry = RUNTIME.advance({"last_assistant_message": still_long}, record)
        self.assertIn("最后一次压缩", retry["reason"])
        fallback = RUNTIME.advance({"last_assistant_message": still_long}, record)
        self.assertIn(d0, fallback["reason"])
        self.assertEqual("D0", record["over_length"]["audit"]["selection"])
        self.assertEqual(2, record["over_length"]["audit"]["compression_attempts"])

    def test_trigger_requires_more_than_ten_percent_over(self) -> None:
        spec = RUNTIME.parse_spec("请起草一份不超过100字的通知。")
        self.assertEqual({"minimum": 0, "maximum": 100, "scope": "full"}, spec)
        self.assertIsNone(RUNTIME.start({"last_assistant_message": "甲" * 110}, {"request": "请起草一份不超过100字的通知。"}))
        record = {"request": "请起草一份不超过100字的通知。"}
        self.assertEqual(
            "block",
            RUNTIME.start({"last_assistant_message": "甲" * 111}, record)["decision"],
        )

    def test_range_and_material_mentions_are_distinguished(self) -> None:
        self.assertEqual(
            {"minimum": 300, "maximum": 420, "scope": "body"},
            RUNTIME.parse_spec("请起草情况报告，正文300—420字。"),
        )
        self.assertIsNone(
            RUNTIME.parse_spec("请解释附件中‘正文不超过420字’这一条要求。")
        )
        self.assertEqual(
            {"minimum": 0, "maximum": 420, "scope": "body"},
            RUNTIME.parse_spec(
                "初次回复不得改写、压缩、省略或解释；最终正文不超过420字。"
            ),
        )

    def test_mechanical_gate_preserves_anchors_and_real_headings(self) -> None:
        original = "工作报告\n\n一、办理情况\n共核对48件，事项仍在办理。"
        spec = {"minimum": 1, "maximum": 100, "scope": "full"}
        self.assertEqual(
            "over_length_number_added_dropped_or_changed",
            RUNTIME.mechanical_reason(
                original,
                "工作报告\n\n一、办理情况\n事项仍在办理。",
                spec,
            ),
        )
        self.assertEqual(
            "over_length_outline_heading_dropped",
            RUNTIME.mechanical_reason(
                original,
                "工作报告\n\n共核对48件，事项仍在办理。",
                spec,
            ),
        )
        article = "管理办法\n\n第一条 本办法适用于信息变更事项。"
        self.assertGreater(RUNTIME.count_text(article, "body"), 10)

    def test_internal_prompts_reject_relisted_responsibilities(self) -> None:
        instruction = RUNTIME._revision_instruction(
            "全文不超过420字。",
            "原稿",
            "待压缩稿",
            {"minimum": 0, "maximum": 420, "scope": "full"},
            1,
        )
        verdict = RUNTIME._verdict_instruction(
            "全文不超过420字。",
            "原稿",
            "压缩稿",
            {"minimum": 0, "maximum": 420, "scope": "full"},
        )
        self.assertIn("不得再以‘继续做好、持续推进、有序推进’", instruction)
        self.assertIn("natural_and_non_repetitive必须为false并FAIL", verdict)


if __name__ == "__main__":
    unittest.main()
