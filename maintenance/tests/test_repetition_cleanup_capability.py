from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

from maintenance.tests.hook_companion_support import ASSEMBLER


ROOT = Path(__file__).resolve().parents[2]
CONTRACT_PATH = ROOT / "chinese-official-writing/hooks/capabilities/protective_expansion/contract.py"
CORE_PATH = ROOT / "chinese-official-writing/hooks/core/gate_stop_hook.py"
HOST_ADAPTER_PATH = ROOT / "chinese-official-writing/hooks/adapters/host_gate_adapter.py"
CLAUDE_ADAPTER_PATH = ROOT / "chinese-official-writing/hooks/adapters/claude-code/gate_stop_hook.py"
REAL_CASES_PATH = ROOT / "maintenance/tests/evidence/repetition-real-first/cases.json"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


CONTRACT = load_module("cow_repetition_contract_test", CONTRACT_PATH)
CORE = load_module("cow_repetition_core_test", CORE_PATH)
HOST_ADAPTER = load_module("cow_repetition_host_adapter_test", HOST_ADAPTER_PATH)
CLAUDE_ADAPTER = load_module("cow_repetition_claude_adapter_test", CLAUDE_ADAPTER_PATH)


def repetition_response(packet: dict, target_id: str, preserved_id: str) -> dict:
    return {
        "schema_version": CONTRACT.RESPONSE_SCHEMA_VERSION,
        "packet_sha256": packet["packet_sha256"],
        "request_sha256": packet["request_sha256"],
        "draft_sha256": packet["draft_sha256"],
        "decision": "DELETE_SPANS",
        "selections": [
            {
                "segment_id": target_id,
                "preserved_segment_id": preserved_id,
                "family": "semantic_repetition",
                "reason": "两句主体、对象、状态和办理作用相同，保留句已完整承载信息。",
                "assertions": {
                    key: True for key in CONTRACT.REQUIRED_ASSERTIONS
                },
            }
        ],
    }


class RepetitionCleanupCapabilityTests(unittest.TestCase):
    def test_frozen_real_drafts_replay_through_contract(self):
        cases = json.loads(REAL_CASES_PATH.read_text(encoding="utf-8"))["cases"]
        for case in cases:
            with self.subTest(case_id=case["id"]):
                draft = "\n".join(case["draft_lines"])
                packet = CONTRACT.build_packet(
                    case["request"], draft, capability="repetition_cleanup"
                )
                sentences = [
                    item for item in packet["segments"] if item["kind"] == "sentence"
                ]
                if case["id"] == "R1":
                    target_text = "请各部门于8月20日17时前报送参会名单。"
                    matches = [
                        item
                        for item in sentences
                        if item["text"].strip() == target_text
                    ]
                    response = repetition_response(
                        packet, matches[1]["segment_id"], matches[0]["segment_id"]
                    )
                elif case["id"] == "R2":
                    first = next(
                        item
                        for item in sentences
                        if item["text"].strip().startswith("请各承办岗位依照")
                    )
                    second = next(
                        item
                        for item in sentences
                        if item["text"].strip().startswith("各承办岗位要按照")
                    )
                    response = repetition_response(
                        packet, second["segment_id"], first["segment_id"]
                    )
                elif case["id"] == "R4":
                    matches = [
                        item
                        for item in sentences
                        if item["text"].strip().startswith(
                            "本年度围绕系统运行保障、业务培训和内部服务三项工作有序推进"
                        )
                    ]
                    response = repetition_response(
                        packet, matches[0]["segment_id"], matches[1]["segment_id"]
                    )
                else:
                    response = {
                        "schema_version": CONTRACT.RESPONSE_SCHEMA_VERSION,
                        "packet_sha256": packet["packet_sha256"],
                        "request_sha256": packet["request_sha256"],
                        "draft_sha256": packet["draft_sha256"],
                        "decision": "CLEAR",
                        "selections": [],
                    }
                result = CONTRACT.apply_response(packet, response)
                expected = (
                    draft
                    if case.get("expected_same_as_draft")
                    else "\n".join(case["expected_lines"])
                )
                self.assertEqual(expected, result["output"])

    def test_exact_duplicate_can_delete_one_even_when_request_contains_sentence(self):
        sentence = "请各部门于8月20日17时前报送参会名单。"
        draft = sentence + sentence
        packet = CONTRACT.build_packet(
            f"请逐字写明：{sentence}",
            draft,
            capability="repetition_cleanup",
        )
        matches = [
            item for item in packet["segments"] if item["text"] == sentence
        ]
        self.assertEqual(2, len(matches))
        self.assertTrue(all(item["eligible"] for item in matches))
        result = CONTRACT.apply_response(
            packet,
            repetition_response(
                packet, matches[1]["segment_id"], matches[0]["segment_id"]
            ),
        )
        self.assertEqual("E1", result["selection"])
        self.assertEqual(sentence, result["output"])

    def test_semantic_duplicate_deletes_only_selected_sentence(self):
        first = "请各承办岗位依照本通知要求推进在办工单，按期完成办理。"
        second = "各承办岗位要按照本通知要求持续推进在办工单办理，确保按期完成。"
        packet = CONTRACT.build_packet(
            "检查短通知中的零增量重复。",
            first + second,
            capability="repetition_cleanup",
        )
        segments = {
            item["text"]: item
            for item in packet["segments"]
            if item["kind"] == "sentence"
        }
        result = CONTRACT.apply_response(
            packet,
            repetition_response(
                packet,
                segments[second]["segment_id"],
                segments[first]["segment_id"],
            ),
        )
        self.assertEqual(first, result["output"])

    def test_different_time_or_state_clear_is_byte_identical(self):
        for draft in (
            "会前请做好参会材料准备。会后请做好会议材料归档。",
            "系统访问现已恢复，异常原因仍在核查。",
        ):
            with self.subTest(draft=draft):
                packet = CONTRACT.build_packet(
                    "检查重复句。", draft, capability="repetition_cleanup"
                )
                response = {
                    "schema_version": 1,
                    "packet_sha256": packet["packet_sha256"],
                    "request_sha256": packet["request_sha256"],
                    "draft_sha256": packet["draft_sha256"],
                    "decision": "CLEAR",
                    "selections": [],
                }
                result = CONTRACT.apply_response(packet, response)
                self.assertEqual("E0", result["selection"])
                self.assertEqual(draft, result["output"])

    def test_missing_self_or_deleted_preserved_segment_falls_back(self):
        sentence = "按计划推进。"
        packet = CONTRACT.build_packet(
            "检查重复。", sentence + sentence, capability="repetition_cleanup"
        )
        matches = [item for item in packet["segments"] if item["text"] == sentence]
        missing = repetition_response(packet, matches[1]["segment_id"], "S999")
        self.assertEqual(
            "invalid_preserved_segment", CONTRACT.apply_response(packet, missing)["reason"]
        )
        same = repetition_response(
            packet, matches[1]["segment_id"], matches[1]["segment_id"]
        )
        self.assertEqual(
            "invalid_preserved_segment", CONTRACT.apply_response(packet, same)["reason"]
        )

    def test_observer_is_semantic_and_not_similarity_threshold(self):
        packet = CONTRACT.build_packet(
            "检查重复。",
            "会前准备材料。会后归档材料。",
            capability="repetition_cleanup",
        )
        instruction = CONTRACT.observer_instruction(packet)
        self.assertEqual(["semantic_repetition"], packet["allowed_families"])
        self.assertIn("完全相同的句子只是候选", instruction)
        self.assertIn("preserved_segment_id", instruction)
        self.assertIn("小标题", instruction)
        self.assertNotIn("相似度阈值", instruction)

    def test_core_lifecycle_selects_repetition_profile_and_verifies_echo(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            plugin = root / "plugin"
            skill = plugin / "skills/chinese-official-writing"
            skill.mkdir(parents=True)
            (skill / "SKILL.md").write_text(
                "---\nname: chinese-official-writing\n---\n", encoding="utf-8"
            )
            previous = {
                key: os.environ.get(key)
                for key in ("COW_GATE_HOOK_DATA", "PLUGIN_ROOT", "COW_GATE_CAPABILITY")
            }
            os.environ["COW_GATE_HOOK_DATA"] = str(root / "data")
            os.environ["PLUGIN_ROOT"] = str(plugin)
            os.environ["COW_GATE_CAPABILITY"] = "repetition_cleanup"
            try:
                base = {
                    "session_id": "s1",
                    "turn_id": "t1",
                    "cwd": str(root),
                }
                CORE.handle(
                    {**base, "hook_event_name": "UserPromptSubmit", "prompt": "检查短通知重复句。"}
                )
                CORE.handle(
                    {
                        **base,
                        "hook_event_name": "PostToolUse",
                        "tool_input": {"cmd": f'Get-Content "{skill / "SKILL.md"}"'},
                        "tool_response": {"exit_code": 0},
                    }
                )
                sentence = "请按时报送名单。"
                draft = sentence + sentence
                first = CORE.handle(
                    {
                        **base,
                        "hook_event_name": "Stop",
                        "stop_hook_active": False,
                        "last_assistant_message": draft,
                    }
                )
                self.assertIn("重复句语义观察", first["reason"])
                skeleton = json.loads(
                    first["reason"].split("CLEAR 骨架如下：\n", 1)[1].split(
                        "\nDELETE_SPANS 骨架", 1
                    )[0]
                )
                packet = json.loads(first["reason"].split("\n观察包如下：\n", 1)[1])
                matches = [item for item in packet["segments"] if item["text"] == sentence]
                response = repetition_response(
                    packet, matches[1]["segment_id"], matches[0]["segment_id"]
                )
                response.update(
                    {
                        "schema_version": skeleton["schema_version"],
                        "packet_sha256": skeleton["packet_sha256"],
                        "request_sha256": skeleton["request_sha256"],
                        "draft_sha256": skeleton["draft_sha256"],
                    }
                )
                second = CORE.handle(
                    {
                        **base,
                        "hook_event_name": "Stop",
                        "stop_hook_active": True,
                        "last_assistant_message": json.dumps(response, ensure_ascii=False),
                    }
                )
                self.assertIn(sentence, second["reason"])
                third = CORE.handle(
                    {
                        **base,
                        "hook_event_name": "Stop",
                        "stop_hook_active": True,
                        "last_assistant_message": sentence,
                    }
                )
                self.assertTrue(third["continue"])
                record = CORE._read_json(
                    CORE._record_path({**base, "hook_event_name": "Stop"})
                )
                self.assertEqual("repetition_cleanup", record["protective_capability"])
                self.assertTrue(record["protective_delivery_verified"])
            finally:
                for key, value in previous.items():
                    if value is None:
                        os.environ.pop(key, None)
                    else:
                        os.environ[key] = value

    def test_adapters_and_all_static_companions_accept_profile(self):
        self.assertIn("repetition_cleanup", HOST_ADAPTER.SUPPORTED_CAPABILITIES)
        self.assertIn("repetition_cleanup", CLAUDE_ADAPTER.SUPPORTED_CAPABILITIES)
        with tempfile.TemporaryDirectory() as temporary:
            for host in ("codex", "codebuddy", "claude-code"):
                output = Path(temporary) / host
                result = ASSEMBLER.assemble(host, output, "repetition_cleanup")
                self.assertEqual("repetition_cleanup", result["capability"])
                self.assertFalse(result["installed"])
                self.assertFalse(result["enabled"])


if __name__ == "__main__":
    unittest.main()
