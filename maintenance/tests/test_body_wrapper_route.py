"""Default routing and terminal replay of genuine cleanliness model replies."""
import importlib.util
import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "body_wrapper_core", ROOT / "chinese-official-writing/hooks/core/gate_stop_hook.py"
)
HOOK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(HOOK)


class BodyWrapperRouteTests(unittest.TestCase):
    def test_narrow_delivery_boundary(self):
        for request, draft, expected in [
            ("只发正文。", "下面是压缩后的完整稿。\n\n报告", True),
            ("直接发纪要正文。", "压缩到 468 字，已在 500 字以内。\n\n纪要", True),
            ("只发正文。", "关于整改工作的报告\n\n下面是有关情况。", False),
            ("请只审稿，不要改写。", "下面是压缩后的完整稿。", False),
            ("请保留前导语与改动说明，直接返回全文。", "下面是压缩后的完整稿。", False),
            ("只发正文，但保留前言。", "下面是压缩后的完整稿。", False),
            ("用 Markdown 给出报告。", "下面是压缩后的完整稿。", False),
        ]:
            with self.subTest(request=request, draft=draft):
                self.assertEqual(HOOK._body_only_has_wrapper(request, draft), expected)

    def test_user_opt_out_and_absent_skill_are_not_routed(self):
        for extra in ({"bypass": "user_requested", "skill_seen": True}, {"skill_seen": False}):
            with tempfile.TemporaryDirectory() as directory, patch.dict(
                os.environ, {"COW_GATE_HOOK_DATA": directory, "COW_GATE_CAPABILITY": "delivery_review"}
            ):
                record = {"request": "只发正文。", **extra}
                result = HOOK._handle_delivery_cleanliness_capability(
                    {"last_assistant_message": "下面是压缩后的完整稿。\n\n报告", "stop_hook_active": False},
                    Path(directory) / "record.json", record,
                )
                self.assertIsNone(result)
                self.assertNotIn("delivery_cleanliness", record)

    def prepass_record(self, phase="delivery_cleanliness_awaiting_output"):
        draft = "报告正文"
        digest = hashlib.sha256(draft.encode()).hexdigest()
        return {"request": "只发正文。", "skill_seen": True, "cleanliness_prepass": True,
                "delivery_cleanliness": {"phase": phase, "original": draft,
                    "audit": {"selection": "D1", "delivery_verified": False}},
                "delivery_cleanliness_selected_output": draft,
                "delivery_cleanliness_selected_sha256": digest}

    def test_verified_prepass_continues_existing_gate(self):
        with tempfile.TemporaryDirectory() as directory, patch.dict(
            os.environ, {"COW_GATE_HOOK_DATA": directory, "COW_GATE_CAPABILITY": "delivery_review"}
        ):
            event = {"hook_event_name": "Stop", "session_id": "s", "turn_id": "1", "cwd": directory,
                     "stop_hook_active": True, "last_assistant_message": "报告正文"}
            path = HOOK._record_path(event)
            HOOK._write_record(path, self.prepass_record())
            with patch.object(HOOK, "_bootstrap_transaction", return_value=None) as bootstrap:
                HOOK.handle(event)
            bootstrap.assert_called_once()
            saved = HOOK._read_json(path)
            self.assertTrue(saved["cleanliness_prepass_audit"]["delivery_verified"])
            self.assertNotIn("delivery_cleanliness", saved)

    def test_failed_prepass_is_not_verified_or_reopened(self):
        with tempfile.TemporaryDirectory() as directory, patch.dict(
            os.environ, {"COW_GATE_HOOK_DATA": directory, "COW_GATE_CAPABILITY": "delivery_review"}
        ):
            event = {"hook_event_name": "Stop", "session_id": "s", "turn_id": "1", "cwd": directory,
                     "stop_hook_active": True, "last_assistant_message": "错误回显"}
            path = HOOK._record_path(event)
            record = self.prepass_record()
            record["delivery_cleanliness"]["audit"]["selection"] = "D0"
            record["delivery_cleanliness"]["output_reprompts"] = 1
            HOOK._write_record(path, record)
            self.assertFalse(HOOK.handle(event)["continue"])
            self.assertFalse(HOOK.handle(event)["continue"])
            saved = HOOK._read_json(path)
            self.assertEqual(saved["data_retention_state"], HOOK.REDACTED_RECORD_STATE)
            self.assertNotIn("original", saved["delivery_cleanliness"])


if __name__ == "__main__":
    unittest.main()
