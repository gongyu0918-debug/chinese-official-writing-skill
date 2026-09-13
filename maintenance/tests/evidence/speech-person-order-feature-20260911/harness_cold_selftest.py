"""Offline tests of cold-host error, identity, no-tool and anonymous-input boundaries."""
import importlib.util
import json
from pathlib import Path
import re
import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location("cold_test_host", Path(__file__).with_name("harness_cold_inline.py"))
C = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(C)


class InlineColdBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="person-order-cold-offline-")
        self.addCleanup(self.temp.cleanup)
        self.run = Path(self.temp.name)
        self.response = {"cases": [{"id": "P1", "preference": "tie",
            "A": {"facts_state": "事实状态保持。", "ordering": "符合原题。", "delivery": "直接正文。"},
            "B": {"facts_state": "事实状态保持。", "ordering": "符合原题。", "delivery": "直接正文。"},
            "material_differences": [], "confidence": "high"}]}

    def verify(self, body=None, *, advertised=None, calls=0, status="COMPLETE"):
        (self.run / "final.md").write_text(body if body is not None else json.dumps(self.response, ensure_ascii=False), encoding="utf-8")
        receipt = {"status": status, "technical_valid": status == "COMPLETE", "tool_calls_count": calls,
                   "init": {"tools": [] if advertised is None else advertised}}
        C.verify(receipt, self.run, "P1")
        return receipt

    def test_valid_review_and_exact_zero_tools(self):
        receipt = self.verify()
        self.assertEqual(receipt["status"], "COMPLETE")
        self.assertTrue(receipt["cold_json_valid"])
        self.assertTrue(receipt["zero_tool_calls"])

    def test_api_error_placeholder_never_complete(self):
        receipt = self.verify("APIError: routed provider request failed")
        self.assertEqual(receipt["status"], "INVALID")
        self.assertEqual(receipt["cold_json_error"], "NON_JSON_RESPONSE")

    def test_structured_api_error_placeholder_never_complete(self):
        self.response["cases"][0]["A"]["facts_state"] = "APIError: no response"
        self.assertEqual(self.verify()["cold_json_error"], "API_ERROR_PLACEHOLDER")

    def test_non_json_prose_cannot_be_a_completed_review(self):
        self.assertFalse(self.verify("两稿似乎相当。") ["technical_valid"])

    def test_wrong_pair_or_invalid_preference_cannot_pass(self):
        self.response["cases"][0]["id"] = "P2"
        self.assertEqual(self.verify()["status"], "INVALID")
        self.response["cases"][0]["id"], self.response["cases"][0]["preference"] = "P1", ["tie"]
        self.assertEqual(self.verify()["status"], "INVALID")

    def test_registered_both_need_revision_is_valid(self):
        self.response["cases"][0]["preference"] = "both_need_revision"
        self.assertEqual(self.verify()["status"], "COMPLETE")

    def test_advertised_read_tool_invalid_even_without_call(self):
        self.assertEqual(self.verify(advertised=["read_file"])["status"], "INVALID")

    def test_actual_tool_call_invalid_even_if_not_advertised(self):
        self.assertEqual(self.verify(calls=1)["status"], "INVALID")

    def test_validation_never_overwrites_native_unavailable(self):
        self.assertEqual(self.verify(status="UNAVAILABLE")["status"], "UNAVAILABLE")

    def test_fenced_json_parsing_does_not_change_raw(self):
        for language in ("json", "JSON", ""):
            raw = "```" + language + "\n" + json.dumps(self.response, ensure_ascii=False) + "\n```"
            receipt = self.verify(raw)
            self.assertTrue(receipt["outer_json_fence_removed_for_parsing_only"])
            self.assertEqual((self.run / "final.md").read_text(encoding="utf-8"), raw)

    def test_packet_rejects_multi_pair_and_writer_metadata(self):
        pair = {"id": "P1", "task": "原题", "A": "稿一", "B": "稿二"}
        with self.assertRaises(AssertionError):
            C.validate_packet({"cases": [pair, pair]})
        with self.assertRaises(AssertionError):
            C.validate_packet({"cases": [{**pair, "writer_reasoning": "禁止带入"}]})
        prompt = C.build_prompt({"cases": [pair]}, "只根据原题比较。")
        self.assertIn("原题", prompt)
        self.assertIn("稿一", prompt)
        self.assertNotIn("instructions.md", prompt)

    def test_explicit_effort_and_disabled_registry_match_installed_qwen(self):
        config = C.H.settings(C.H.REVIEWER, 240, 6000, "max", mode="inline_cold")
        self.assertEqual(config["modelProviders"]["openai"][0]["generationConfig"]["samplingParams"]["reasoning_effort"], "max")
        self.assertEqual(config["permissions"]["allow"], [])
        self.assertTrue(config["disableAllHooks"])
        source = Path("C:/Users/admin/AppData/Roaming/npm/node_modules/@qwen-code/qwen-code/chunks/chunk-6NFAEG54.js")
        self.assertTrue(source.is_file(), "Installed 0.22.0 registry source unavailable; revisit host evidence")
        enum = source.read_text(encoding="utf-8").split("var ToolNames = {", 1)[1].split("\n};", 1)[0]
        names = set(re.findall(r'^  [A-Z_]+: "([a-z_]+)"', enum, re.M))
        self.assertGreater(len(names), 40)
        self.assertEqual(names - set(config["tools"]["disabled"]), set())


if __name__ == "__main__":
    unittest.main()
