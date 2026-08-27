from __future__ import annotations

import os
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


if __name__ == "__main__":
    unittest.main()
