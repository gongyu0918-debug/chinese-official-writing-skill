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


if __name__ == "__main__":
    unittest.main()
