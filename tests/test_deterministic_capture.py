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


if __name__ == "__main__":
    unittest.main()
