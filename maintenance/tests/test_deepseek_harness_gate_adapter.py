from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from maintenance.tests.hook_companion_support import ASSEMBLER


ROOT = Path(__file__).resolve().parents[2]
SMOKE = ROOT / "maintenance/tests/deepseek_harness_adapter_smoke.mjs"


class DeepSeekHarnessGateAdapterTests(unittest.TestCase):
    def setUp(self) -> None:
        node = shutil.which("node")
        if node is None:
            self.skipTest("node is unavailable")
        self.node = node
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.companion = self.root / "companion"
        ASSEMBLER.assemble("deepseek-harness", self.companion)

    def test_bundle_manifest_and_javascript_are_valid(self) -> None:
        manifest = json.loads(
            (self.companion / "package.json").read_text(encoding="utf-8")
        )
        self.assertEqual("chinese-official-writing-gate-dsh", manifest["name"])
        self.assertEqual(
            "./cordis.patch.yml", manifest["dsh"]["bundle"]["patch"]
        )
        subprocess.run(
            [self.node, "--check", str(self.companion / "index.mjs")],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

    def test_native_lifecycle_blocks_then_allows_and_redacts(self) -> None:
        result = subprocess.run(
            [
                self.node,
                str(SMOKE),
                str(self.companion),
                str(self.root / "data"),
            ],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            env=os.environ.copy(),
            timeout=45,
        )
        value = json.loads(result.stdout)
        self.assertTrue(value["firstBlocked"])
        self.assertTrue(value["terminalAllowed"])
        self.assertTrue(value["redacted"])
        self.assertFalse(value["rawRetained"])
        self.assertTrue(value["externalSkillRejected"])
        self.assertTrue(value["turnChangeRedacted"])

    def _halt_protocol(self, source: str, mode: str = "hard-stop") -> dict:
        (self.companion / "skills/chinese-official-writing/hooks/gate_stop_hook.py").write_text(
            source, encoding="utf-8"
        )
        result = subprocess.run(
            [self.node, str(SMOKE), str(self.companion), str(self.root / ("data-" + mode)), mode],
            check=True, capture_output=True, text=True, encoding="utf-8", timeout=30,
        )
        return json.loads(result.stdout)

    def test_hard_stop_cancels_once_before_block_and_retains_failure(self) -> None:
        response = {"continue": False, "decision": "block", "reason": "do not steer", "stopReason": "终稿回显未验证"}
        value = self._halt_protocol(
            "import json,sys\ne=json.load(sys.stdin)\nprint(json.dumps("
            + repr(response) + " if e['hook_event_name']=='Stop' else {'continue':True}))\n"
        )
        self.assertEqual(0, value["steers"])
        self.assertEqual([{"kind": "hook", "reason": "终稿回显未验证"}], value["cancels"])
        self.assertEqual([{"keepInbox": True}], value["cancelOptions"])
        self.assertEqual(["halt"], [row["decision"] for row in value["receipts"]])
        self.assertFalse(value["receipts"][0]["delivery_verified"])

    def test_hard_stop_invalid_message_keeps_explicit_failure(self) -> None:
        value = self._halt_protocol(
            "import json,sys\ne=json.load(sys.stdin)\nprint(json.dumps("
            "{'continue':False,'stopReason':2,'systemMessage':' '} if e['hook_event_name']=='Stop' else {'continue':True}))\n"
        )
        self.assertEqual([{"kind": "hook", "reason": "交付门禁已停止自动交付。"}], value["cancels"])
        self.assertEqual(0, value["steers"])

    def test_submit_hard_stop_cannot_enter_a_normal_gate_turn(self) -> None:
        value = self._halt_protocol("print('{\"continue\":false,\"stopReason\":\"状态不可写\"}')\n")
        self.assertEqual([{"kind": "hook", "reason": "状态不可写"}], value["cancels"])
        self.assertEqual([{"keepInbox": True}], value["cancelOptions"])
        self.assertEqual([], value["receipts"])
        self.assertEqual(0, value["steers"])

    def test_late_hard_stop_cannot_cancel_a_new_user_turn(self) -> None:
        value = self._halt_protocol(
            "import json,sys,time\ne=json.load(sys.stdin)\n"
            "if e['hook_event_name']=='Stop': time.sleep(0.2)\n"
            "print(json.dumps({'continue':False,'stopReason':'old turn failed'} if e['hook_event_name']=='Stop' else {'continue':True}))\n",
            "late-halt",
        )
        self.assertEqual([], value["cancels"])
        self.assertEqual(0, value["steers"])

    def test_fallback_echo_mismatch_halts_but_exact_d0_can_end(self) -> None:
        source = (
            "import json,sys\ne=json.load(sys.stdin)\n"
            "if e['hook_event_name']=='Stop' and e.get('stop_hook_active'): sys.exit(1)\n"
            "print(json.dumps({'decision':'block','reason':'repair'} if e['hook_event_name']=='Stop' else {'continue':True}))\n"
        )
        value = self._halt_protocol(source, "fallback-mismatch")
        self.assertEqual(2, value["steers"])
        self.assertEqual([{"kind": "hook", "reason": "原稿回显校验未通过，已停止自动重试。"}], value["cancels"])
        self.assertEqual([{"keepInbox": True}], value["cancelOptions"])
        self.assertEqual("halt_fallback_mismatch", value["receipts"][-1]["decision"])
        value = self._halt_protocol(source, "fallback-exact")
        self.assertEqual(2, value["steers"])
        self.assertEqual([], value["cancels"])
        self.assertEqual("allow_d0_fallback", value["receipts"][-1]["decision"])


if __name__ == "__main__":
    unittest.main()
