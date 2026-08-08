from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "deterministic_capture.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


capture_tool = load_module("deterministic_capture_under_test", SCRIPT)


class DeterministicCaptureTests(unittest.TestCase):
    def test_capture_preserves_body_and_verifies_hash(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "input.json"
            output = root / "capture.json"
            body = "第一行\r\n第二行\u00a0保留"
            source.write_text(
                json.dumps(
                    {"task_id": "M1", "request_sha256": "abc", "assistant_body": body},
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            receipt = capture_tool.capture(source, output)

            self.assertEqual(receipt["assistant_body"], body)
            self.assertEqual(receipt["generation_attempt"], 1)
            self.assertEqual(receipt["request_sha256"], "abc")
            self.assertEqual(capture_tool.verify(output), {"status": "PASS", "issues": []})

    def test_existing_capture_is_never_overwritten(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "input.json"
            output = root / "capture.json"
            source.write_text(
                json.dumps({"task_id": "M1", "assistant_body": "first"}),
                encoding="utf-8",
            )
            capture_tool.capture(source, output)
            frozen = output.read_bytes()
            source.write_text(
                json.dumps({"task_id": "M1", "assistant_body": "second"}),
                encoding="utf-8",
            )

            completed = subprocess.run(
                [sys.executable, str(SCRIPT), "capture", "--input", str(source), "--out", str(output)],
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(completed.returncode, 3)
            self.assertEqual(output.read_bytes(), frozen)

    def test_tampered_capture_fails_verification(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "input.json"
            output = root / "capture.json"
            source.write_text(
                json.dumps({"task_id": "M1", "assistant_body": "original"}),
                encoding="utf-8",
            )
            capture_tool.capture(source, output)
            receipt = json.loads(output.read_text(encoding="utf-8"))
            receipt["assistant_body"] = "changed"
            output.write_text(json.dumps(receipt), encoding="utf-8")

            result = capture_tool.verify(output)

            self.assertEqual(result["status"], "FAIL")
            self.assertIn("assistant_body_sha256_mismatch", result["issues"])

    def test_count_uses_unicode_whitespace_and_keeps_zero_width_space(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "input.json"
            output = root / "capture.json"
            body = "A B\t中\r\n\u00a0\u3000\u200bＡ"
            source.write_text(
                json.dumps({"task_id": "L1", "assistant_body": body}, ensure_ascii=False),
                encoding="utf-8",
            )
            capture_tool.capture(source, output)

            result = capture_tool.count_non_whitespace(output)

            self.assertEqual(result["status"], "PASS")
            self.assertEqual(result["unicode_non_whitespace_count"], 5)
            self.assertEqual(result["assistant_body_sha256"], capture_tool._body_sha256(body))

    def test_amount_check_uses_decimal_and_explicit_source_quotes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            packet = Path(temp_dir) / "packet.json"
            packet.write_text(
                json.dumps(
                    {
                        "fact_packet_text": "单价0.1万元，数量3项，合计0.3万元。",
                        "amounts": {
                            "unit_price": {"value": "0.1", "source_quote": "单价0.1万元"},
                            "quantity": {"value": "3", "source_quote": "数量3项"},
                            "total": {"value": "0.3", "source_quote": "合计0.3万元"},
                        },
                        "assertions": [
                            {"id": "total_math", "op": "mul", "left": "unit_price", "right": "quantity", "expected": "total"},
                            {"id": "unit_lt_total", "op": "lt", "left": "unit_price", "right": "total"},
                        ],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            result = capture_tool.check_amounts(packet)

            self.assertEqual(result["status"], "PASS")
            self.assertEqual(result["assertions"][0]["actual"], "0.3")

    def test_amount_check_reports_failed_relation(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            packet = Path(temp_dir) / "packet.json"
            packet.write_text(
                json.dumps(
                    {
                        "fact_packet_text": "甲项2元，乙项3元。",
                        "amounts": {
                            "left": {"value": "2", "source_quote": "甲项2元"},
                            "right": {"value": "3", "source_quote": "乙项3元"},
                        },
                        "assertions": [{"id": "equal", "op": "eq", "left": "left", "right": "right"}],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            result = capture_tool.check_amounts(packet)

            self.assertEqual(result["status"], "FAIL")
            self.assertEqual(result["assertions"][0]["status"], "FAIL")

    def test_amount_check_rejects_unanchored_quote_and_division_by_zero(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            packet = Path(temp_dir) / "packet.json"
            packet.write_text(
                json.dumps(
                    {
                        "fact_packet_text": "金额1元。",
                        "amounts": {"one": {"value": "1", "source_quote": "不存在"}},
                        "assertions": [{"id": "same", "op": "eq", "left": "one", "right": "one"}],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "source_quote"):
                capture_tool.check_amounts(packet)

            packet.write_text(
                json.dumps(
                    {
                        "fact_packet_text": "金额1元，数量0项。",
                        "amounts": {
                            "one": {"value": "1", "source_quote": "金额1元"},
                            "zero": {"value": "0", "source_quote": "数量0项"},
                        },
                        "assertions": [{"id": "divide", "op": "div", "left": "one", "right": "zero", "expected": "one"}],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "divides by zero"):
                capture_tool.check_amounts(packet)


if __name__ == "__main__":
    unittest.main()
