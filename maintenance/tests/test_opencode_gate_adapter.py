from __future__ import annotations

import os
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from maintenance.tests.hook_companion_support import ASSEMBLER


ROOT = Path(__file__).resolve().parents[2]
SMOKE = ROOT / "maintenance/tests/opencode_adapter_smoke.mjs"


class OpenCodeGateAdapterTests(unittest.TestCase):
    def setUp(self) -> None:
        node = shutil.which("node")
        if node is None:
            self.skipTest("node is unavailable")
        self.node = node
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.companion = self.root / "companion"
        ASSEMBLER.assemble("opencode", self.companion)
        self.plugin = (
            self.companion
            / ".opencode/plugins/chinese-official-writing-gate.js"
        )

    def test_plugin_is_valid_javascript(self) -> None:
        subprocess.run(
            [self.node, "--check", str(self.plugin)],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

    def test_interactive_idle_reaches_terminal_echo_and_redacts_raw_data(self) -> None:
        result = subprocess.run(
            [self.node, str(SMOKE), str(self.companion), str(self.root / "data")],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            env={**os.environ, "COW_OPENCODE_GATE_DELAY_MS": "0"},
            timeout=30,
        )
        self.assertIn('"prompts":1', result.stdout)
        self.assertIn('"rawRetained":false', result.stdout)
        self.assertIn('"restartReplayBlocked":true', result.stdout)

    def test_headless_run_does_not_arm_or_retain_raw_data(self) -> None:
        data = self.root / "headless-data"
        result = subprocess.run(
            [
                self.node,
                str(SMOKE),
                str(self.companion),
                str(data),
                "run",
            ],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            env={**os.environ, "COW_OPENCODE_GATE_DELAY_MS": "0"},
            timeout=30,
        )
        self.assertIn('"prompts":0', result.stdout)
        self.assertFalse(data.exists())

    def test_module_restart_aborts_pending_cycle_without_replay(self) -> None:
        result = subprocess.run(
            [
                self.node,
                str(SMOKE),
                str(self.companion),
                str(self.root / "restart-data"),
                "restart-pending",
            ],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            env={**os.environ, "COW_OPENCODE_GATE_DELAY_MS": "200"},
            timeout=30,
        )
        self.assertIn('"prompts":0', result.stdout)
        self.assertIn('"rawRetained":false', result.stdout)
        self.assertIn('"pendingReplayAborted":true', result.stdout)

    def test_delayed_continuation_cannot_enter_a_new_user_turn(self) -> None:
        result = subprocess.run(
            [
                self.node,
                str(SMOKE),
                str(self.companion),
                str(self.root / "turn-data"),
                "turn-changed",
            ],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            env={**os.environ, "COW_OPENCODE_GATE_DELAY_MS": "200"},
            timeout=30,
        )
        self.assertIn('"prompts":0', result.stdout)
        self.assertIn('"rawRetained":false', result.stdout)
        self.assertIn('"turnBound":true', result.stdout)

    def test_same_name_external_skill_fails_open_and_redacts_request(self) -> None:
        result = subprocess.run(
            [
                self.node,
                str(SMOKE),
                str(self.companion),
                str(self.root / "stale-skill-data"),
                "stale-skill",
            ],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            env={**os.environ, "COW_OPENCODE_GATE_DELAY_MS": "0"},
            timeout=30,
        )
        self.assertIn('"prompts":0', result.stdout)
        self.assertIn('"rawRetained":false', result.stdout)
        self.assertIn('"staleSkillRejected":true', result.stdout)

    def test_reload_during_prompt_dispatch_keeps_one_owner(self) -> None:
        result = subprocess.run(
            [
                self.node,
                str(SMOKE),
                str(self.companion),
                str(self.root / "dispatch-data"),
                "dispatch-reload",
            ],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            env={**os.environ, "COW_OPENCODE_GATE_DELAY_MS": "0"},
            timeout=30,
        )
        self.assertIn('"prompts":1', result.stdout)
        self.assertIn('"rawRetained":false', result.stdout)
        self.assertIn('"singleOwner":true', result.stdout)

    def _hard_stop_protocol(self, mode: str) -> dict:
        core = self.companion / ".opencode/skills/chinese-official-writing/hooks/gate_stop_hook.py"
        core.write_text(
            "import json,sys,os,pathlib\ne=json.load(sys.stdin)\n"
            "if e['hook_event_name']=='Stop':\n"
            " p=pathlib.Path(os.environ['COW_GATE_HOOK_DATA'])/'candidate-ai-gate-hook'/e['session_id']/(e['turn_id']+'.json')\n"
            " p.parent.mkdir(parents=True,exist_ok=True)\n"
            " p.write_text(json.dumps({'data_retention_state':'raw_turn_data_redacted','delivery_verified':False,'failure_reason':'hook_selected_output_echo_budget_exhausted'}))\n"
            " print(json.dumps({'continue':False,'decision':'block','reason':'do not retry','stopReason':'终稿回显未验证'}))\n"
            "else: print('{\"continue\":true}')\n",
            encoding="utf-8",
        )
        result = subprocess.run(
            [self.node, str(SMOKE), str(self.companion), str(self.root / "data"), mode],
            check=True, capture_output=True, text=True, encoding="utf-8",
            env={**os.environ, "COW_OPENCODE_GATE_DELAY_MS": "0"}, timeout=30,
        )
        return json.loads(result.stdout)

    def test_hard_stop_is_failure_without_retry_including_terminal_replay(self) -> None:
        value = self._hard_stop_protocol("hard-stop")
        self.assertEqual(0, value["prompts"])
        self.assertEqual(2, len(value["toasts"]))
        for toast in value["toasts"]:
            self.assertEqual("error", toast["body"]["variant"])
            self.assertEqual("终稿回显未验证", toast["body"]["message"])
        bodies = [entry["body"] for entry in value["logs"]]
        self.assertEqual(2, len(bodies))
        self.assertTrue(all(body["level"] == "error" for body in bodies))
        self.assertTrue(all(body["extra"]["decision"] == "halt" for body in bodies))
        self.assertTrue(all(body["extra"]["deliveryVerified"] is False for body in bodies))

    def test_unavailable_failure_notice_keeps_error_and_no_retry(self) -> None:
        value = self._hard_stop_protocol("hard-stop-no-notice")
        self.assertEqual(0, value["prompts"])
        self.assertEqual([], value["toasts"])
        bodies = [entry["body"] for entry in value["logs"]]
        self.assertTrue(all(body["level"] == "error" for body in bodies))
        self.assertEqual(2, sum(body["message"] == "delivery failure notification unavailable" for body in bodies))


if __name__ == "__main__":
    unittest.main()
