from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "chinese-official-writing" / "scripts" / "review_gate.py"
SPEC = importlib.util.spec_from_file_location("review_gate_request_safety", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
GATE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = GATE
SPEC.loader.exec_module(GATE)


def decision_packet(detection, decisions):
    return {
        "schema_version": 2,
        "run_id": detection["run_id"],
        "request_sha256": detection["request_sha256"],
        "source_sha256": detection["source_sha256"],
        "draft_sha256": detection["draft_sha256"],
        "guided_marker_sha256": detection.get("guided_marker_sha256"),
        "revision_count": 1,
        "repair_mode": GATE.REPAIR_MODE_DECISIONS,
        "repairs": decisions,
    }


class ReviewGateRequestFactSafetyTests(unittest.TestCase):
    def detection(self, request: str, draft: str, source: str = ""):
        result = GATE.locate_candidates(request, draft, source)
        result["run_id"] = "request-fact-safety"
        return result

    def test_required_negative_result_is_not_a_review_finding(self):
        request = (
            "材料：已核查8月10日9时00分至9时30分的48条调用记录，未发现同类现象。"
            "要求完整保留核查范围、数量和未发现同类现象的含义。"
        )
        draft = (
            "预约接口异常情况说明\n\n"
            "已对8月10日9时00分至9时30分的48条调用记录进行核查，均未发现同类异常现象。"
        )
        self.assertEqual([], self.detection(request, draft)["findings"])

    def test_user_quoted_delete_target_remains_deletable(self):
        request = "请删除“未发现同类现象。”，其余文字保持不变。"
        draft = (
            "情况说明\n\n"
            "8月10日完成接口恢复，相关时间记录已经核对。"
            "未发现同类现象。"
        )
        detection = self.detection(request, draft)
        finding = detection["findings"][0]
        packet = decision_packet(
            detection,
            [{
                "finding_id": finding["finding_id"],
                "target": finding["target"],
                "decision": GATE.DECISION_DELETE,
                "replacement": "",
            }],
        )
        result = GATE.evaluate_candidate(
            request, "", draft, detection["run_id"], detection, packet
        )
        self.assertEqual("D1", result.selected)
        self.assertNotIn("未发现同类现象", result.text)

    def test_unsupported_pure_negative_result_remains_deletable(self):
        request = "根据给定恢复时间写一份情况说明，只使用已给事实。"
        draft = (
            "情况说明\n\n"
            "8月10日完成接口恢复，相关时间记录已经核对。"
            "未发现同类现象。"
        )
        detection = self.detection(request, draft)
        finding = detection["findings"][0]
        allowed, reason = GATE._finding_action_contract(finding, draft)
        self.assertIn(GATE.DECISION_DELETE, allowed)
        self.assertIsNone(reason)

    def test_explicit_cause_investigation_status_does_not_overtrigger(self):
        request = "材料：原因尚未查明，技术人员正在核查。请据此写情况说明。"
        draft = "情况说明\n\n异常原因尚未查明，技术人员正在核查。"
        self.assertEqual([], self.detection(request, draft)["findings"])

    def test_source_absent_rewrite_cannot_swap_pending_procurement_objects(self):
        request = (
            "材料：尚未形成采购决定，审批意见、责任分工和完成期限均未确定。"
            "请保持这些未决状态。"
        )
        draft = (
            "采购事项说明\n\n"
            "本次仅说明现有材料记录的事项状态。有关数据和时间已经逐项核对。"
            "正文其余内容保持原有范围，不增加新的办理安排。"
            "目前尚未形成采购决定，审批意见、责任分工和完成期限均未确定。"
        )
        detection = self.detection(request, draft)
        self.assertTrue(detection["findings"])
        finding = detection["findings"][0]
        packet = decision_packet(
            detection,
            [{
                "finding_id": finding["finding_id"],
                "target": finding["target"],
                "decision": GATE.DECISION_REWRITE,
                "replacement": "设备调整范围正在研究中。",
            }],
        )
        result = GATE.evaluate_candidate(
            request, "", draft, detection["run_id"], detection, packet
        )
        self.assertEqual("D0", result.selected)
        self.assertEqual(draft, result.text)


if __name__ == "__main__":
    unittest.main()
