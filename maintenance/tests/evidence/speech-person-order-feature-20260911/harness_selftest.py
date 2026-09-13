"""Offline receipt-boundary tests; no model, proxy or network call is made."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location("speech_harness", Path(__file__).with_name("harness_qwen.py"))
H = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(H)


class ReceiptBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="speech-harness-offline-")
        self.addCleanup(self.temp.cleanup)
        self.run = Path(self.temp.name)
        self.snapshot = self.run / "workspace/input"
        self.snapshot.mkdir(parents=True)
        self.page = self.snapshot / "SKILL.md"
        self.page.write_text("具体称呼先于泛称。\n", encoding="utf-8")
        for name in ("prompt.txt", "stderr.txt"):
            (self.run / name).write_text("", encoding="utf-8")

    def collect(self, *, model=None, outside=False, result=True, version="0.22.0", body="尊敬的陈主任："):
        route = H.WRITERS[0]
        path = self.run / "outside.md" if outside else self.page
        events = [
            {"type": "system", "subtype": "init", "model": model or route, "qwen_code_version": version},
            {"type": "assistant", "message": {"content": [
                {"type": "tool_use", "id": "read-1", "name": "read_file",
                 "input": {"file_path": str(path), "offset": 2, "limit": 4}}]}},
            {"type": "user", "message": {"content": [
                {"type": "tool_result", "tool_use_id": "read-1", "is_error": False,
                 "content": "具体称呼先于泛称。"}]}},
        ]
        if result:
            events.append({"type": "result", "subtype": "success", "is_error": False, "result": body})
        (self.run / "stdout.jsonl").write_text("\n".join(json.dumps(e, ensure_ascii=False) for e in events), encoding="utf-8")
        return H.collect(self.run, self.snapshot, route, 0, False, None, 0.01,
                         H.settings(route, 240, 12000, "max"), {"installed_package_version": "0.22.0"})

    def test_success_preserves_read_span_content_and_hash(self):
        receipt = self.collect()
        self.assertEqual(receipt["status"], "COMPLETE")
        self.assertEqual(receipt["configured_effort"], "max")
        self.assertEqual(receipt["actual_read_pages"][0]["input"]["offset"], 2)
        self.assertEqual(receipt["actual_read_pages"][0]["file_sha256"], H.sha(self.page.read_bytes()))
        trace = H.read(self.run / "tool-trace.json")
        self.assertEqual(trace[0]["results"][0]["content"], "具体称呼先于泛称。")
        self.assertEqual((self.run / "final.md").read_text(encoding="utf-8"), "尊敬的陈主任：")

    def test_wrong_route_is_unavailable_despite_successful_body(self):
        self.assertEqual(self.collect(model=H.WRITERS[1])["status"], "UNAVAILABLE")

    def test_version_mismatch_is_unavailable(self):
        self.assertEqual(self.collect(version="0.21.0")["status"], "UNAVAILABLE")

    def test_outside_read_is_invalid_and_not_hashed(self):
        receipt = self.collect(outside=True)
        self.assertEqual(receipt["status"], "INVALID")
        self.assertNotIn("file_sha256", receipt["actual_read_pages"][0])

    def test_missing_native_result_does_not_pass(self):
        self.assertEqual(self.collect(result=False)["status"], "INVALID")

    def test_real_prior_api_placeholder_invalidates_writer_and_keeps_native_success(self):
        # Verbatim prior final: speech-salutation-20260911/output/
        # speech-salutation-20260911/cold/glm-first-1/final.md, line 1.
        placeholder = "[API Error: Model stream ended after a tool result without visible progress.]"
        receipt = self.collect(body=placeholder)
        self.assertEqual(receipt["status"], "INVALID")
        self.assertFalse(receipt["technical_valid"])
        self.assertTrue(receipt["api_error_placeholder"])
        self.assertEqual(receipt["native_result_subtype"], "success")
        self.assertEqual(receipt["result_event"]["result"], placeholder)
        self.assertEqual((self.run / "final.md").read_text(encoding="utf-8"), placeholder)


if __name__ == "__main__":
    unittest.main()
