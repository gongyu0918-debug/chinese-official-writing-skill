from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "chinese-official-writing/hooks/capabilities/protective_expansion/contract.py"
CASES_PATH = ROOT / "maintenance/tests/evidence/v164-protective-expansion-gate-v2/cases-v2.json"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


CONTRACT = load_module("editorial_delete_contract", MODULE_PATH)
CASES = json.loads(CASES_PATH.read_text(encoding="utf-8"))


def response_for(packet: dict, segment_ids: list[str], family: str = "serial_self_certification") -> dict:
    return {
        "schema_version": CONTRACT.RESPONSE_SCHEMA_VERSION,
        "packet_sha256": packet["packet_sha256"],
        "request_sha256": packet["request_sha256"],
        "draft_sha256": packet["draft_sha256"],
        "decision": "DELETE_SPANS" if segment_ids else "CLEAR",
        "selections": [
            {
                "segment_id": segment_id,
                "family": family,
                "reason": "该片段在当前题面中没有独立正文作用，删除不改变事实状态。",
                "assertions": {key: True for key in CONTRACT.REQUIRED_ASSERTIONS},
            }
            for segment_id in segment_ids
        ],
    }


class EditorialDeleteContractTests(unittest.TestCase):
    def packet_for(self, case: dict) -> dict:
        return CONTRACT.build_packet(
            case["request"],
            case["draft"],
            case.get("source", ""),
            authority_scope=case.get("authority_scope"),
        )

    def test_required_delete_targets_are_exact_prebuilt_segments(self) -> None:
        for case in CASES["required_delete"]:
            with self.subTest(case=case["id"]):
                packet = self.packet_for(case)
                by_text = {}
                for segment in packet["segments"]:
                    by_text.setdefault(segment["text"], []).append(segment)
                selected = []
                for target in case["targets"]:
                    matches = [item for item in by_text.get(target, []) if item["eligible"]]
                    self.assertEqual(1, len(matches), target)
                    selected.append(matches[0]["segment_id"])
                result = CONTRACT.apply_response(packet, response_for(packet, selected))
                self.assertEqual("edited", result["status"])
                self.assertEqual("E1", result["selection"])
                self.assertEqual(case["expected"], result["output"])

    def test_keep_and_ambiguous_cases_remain_byte_exact_on_clear(self) -> None:
        for group in ("required_keep", "ambiguous_fallback"):
            for case in CASES[group]:
                with self.subTest(group=group, case=case["id"]):
                    packet = self.packet_for(case)
                    result = CONTRACT.apply_response(packet, response_for(packet, []))
                    self.assertEqual("clear", result["status"])
                    self.assertEqual("E0", result["selection"])
                    self.assertEqual(case["draft"], result["output"])

    def test_exact_source_and_request_text_are_not_eligible(self) -> None:
        target = "供应商尚未确定。"
        source_packet = CONTRACT.build_packet("起草采购衔接通知。", target, target)
        request_packet = CONTRACT.build_packet(f"请逐字保留：{target}", target)
        for packet in (source_packet, request_packet):
            sentence = next(item for item in packet["segments"] if item["kind"] == "sentence")
            self.assertFalse(sentence["eligible"])
            result = CONTRACT.apply_response(packet, response_for(packet, [sentence["segment_id"]]))
            self.assertEqual("fallback", result["status"])
            self.assertEqual(target, result["output"])

    def test_response_cannot_select_arbitrary_text_or_skip_assertions(self) -> None:
        packet = CONTRACT.build_packet("起草情况说明。", "已完成核对。其他事项均无需核对。")
        segment = next(item for item in packet["segments"] if item["text"] == "其他事项均无需核对。")
        unknown = response_for(packet, ["S999"])
        self.assertEqual("unknown_segment", CONTRACT.apply_response(packet, unknown)["reason"])
        incomplete = response_for(packet, [segment["segment_id"]])
        incomplete["selections"][0]["assertions"].pop("authority_sufficient")
        result = CONTRACT.apply_response(packet, incomplete)
        self.assertEqual("fallback", result["status"])
        self.assertEqual("incomplete_assertions", result["reason"])

    def test_unavailable_external_source_forces_e0_even_if_observer_selects(self) -> None:
        packet = CONTRACT.build_packet(
            "根据附件起草采购情况说明。",
            "供应商尚未确定、验收尚未实施。",
            "",
            authority_scope="request_only",
        )
        sentence = next(item for item in packet["segments"] if item["kind"] == "sentence")
        self.assertTrue(packet["authority_incomplete"])
        result = CONTRACT.apply_response(packet, response_for(packet, [sentence["segment_id"]]))
        self.assertEqual("fallback", result["status"])
        self.assertEqual("authority_incomplete", result["reason"])
        self.assertEqual(packet["draft"], result["output"])

        observed = CONTRACT.build_packet(
            "起草项目进展情况说明。",
            "项目按计划推进。验收尚未完成。",
            "",
            authority_scope="external_material_observed",
        )
        target = next(
            item for item in observed["segments"] if item["text"] == "验收尚未完成。"
        )
        result = CONTRACT.apply_response(
            observed, response_for(observed, [target["segment_id"]])
        )
        self.assertTrue(observed["authority_incomplete"])
        self.assertEqual("authority_incomplete", result["reason"])
        self.assertEqual(observed["draft"], result["output"])

    def test_overlap_packet_tamper_empty_and_unique_anchor_fail_to_e0(self) -> None:
        packet = CONTRACT.build_packet("起草。", "本次核对48条记录，其他事项无需核对。")
        sentence = next(item for item in packet["segments"] if item["kind"] == "sentence")
        tail = next(item for item in packet["segments"] if item["kind"] == "tail")
        overlap = CONTRACT.apply_response(packet, response_for(packet, [sentence["segment_id"], tail["segment_id"]]))
        self.assertEqual("overlapping_spans", overlap["reason"])
        anchor = CONTRACT.apply_response(packet, response_for(packet, [sentence["segment_id"]]))
        self.assertEqual("empty_candidate", anchor["reason"])
        tampered = dict(packet)
        tampered["draft"] = packet["draft"] + "篡改"
        result = CONTRACT.apply_response(tampered, response_for(packet, []))
        self.assertEqual("packet_hash_mismatch", result["reason"])

        anchored = CONTRACT.build_packet("起草。", "已完成工作。仅核对48条记录。")
        unique = next(item for item in anchored["segments"] if item["text"] == "仅核对48条记录。")
        result = CONTRACT.apply_response(anchored, response_for(anchored, [unique["segment_id"]]))
        self.assertEqual("unique_anchor_removed", result["reason"])
        self.assertEqual(anchored["draft"], result["output"])

    def test_contract_is_not_a_lexical_detector(self) -> None:
        drafts = (
            "本次说明不构成承诺，不表示认可。",
            "犯罪嫌疑人尚未抓获。",
            "供应商尚未确定、验收尚未实施。",
        )
        for draft in drafts:
            with self.subTest(draft=draft):
                packet = CONTRACT.build_packet("起草正式材料。", draft)
                self.assertNotIn("findings", packet)
                self.assertNotIn("decision", packet)
                self.assertTrue(packet["segments"])

    def test_observer_instruction_exposes_exact_decision_schema_and_semantic_source_rule(self) -> None:
        packet = CONTRACT.build_packet(
            "按给定事实起草情况说明。",
            "已完成核对。其他事项均无需核对。",
        )
        instruction = CONTRACT.observer_instruction(packet)
        self.assertIn("decision 只允许 CLEAR 或 DELETE_SPANS", instruction)
        self.assertIn('"decision": "DELETE_SPANS"', instruction)
        self.assertIn('"assertions":', instruction)
        self.assertIn("语义事实在 source 中得到支持", instruction)
        self.assertIn("request 已明确列出可用事实并明确不写某类过程", instruction)
        self.assertIn("没有材料依据", instruction)
        self.assertIn("无依据未来治理元信息", instruction)
        self.assertIn("没有专项资金、监督、公开、验收或其他安排", instruction)
        self.assertIn("覆盖全部无依据分句的最宽 eligible tail", instruction)
        self.assertIn("状态本身有信息作用时，不得据此删除", instruction)

    def test_cli_is_json_only_and_invalid_input_fails_closed_to_e0_selection(self) -> None:
        completed = subprocess.run(
            [sys.executable, "-B", str(MODULE_PATH)],
            input=json.dumps({"mode": "packet", "request": "起草。", "draft": "已完成。", "source": ""}, ensure_ascii=False),
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        self.assertEqual(0, completed.returncode)
        self.assertEqual("", completed.stderr)
        self.assertEqual("ready", json.loads(completed.stdout)["status"])

        invalid = subprocess.run(
            [sys.executable, "-B", str(MODULE_PATH)],
            input="not-json",
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        self.assertEqual("E0", json.loads(invalid.stdout)["selection"])


if __name__ == "__main__":
    unittest.main()
