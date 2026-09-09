from __future__ import annotations

import hashlib
from pathlib import Path
import tempfile
import unittest

from maintenance.tools import sync_adapters


class PackageGenerationTests(unittest.TestCase):
    def test_selected_package_preserves_source_and_excludes_hook(self):
        before = {p.relative_to(sync_adapters.CANONICAL): hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in sync_adapters.CANONICAL.rglob("*") if p.is_file() and "__pycache__" not in p.parts}
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "build"
            targets = sync_adapters.build_packages(root, ("openclaw",))
            self.assertEqual(set(targets), {"openclaw"})
            package = targets["openclaw"]
            self.assertTrue((package / "scripts/prose_lint.py").is_file())
            self.assertFalse((package / "hooks").exists())
            self.assertFalse((root / "agent-skills").exists())
            self.assertIn('name: chinese_official_writing', (package / "SKILL.md").read_text("utf-8"))
        after = {p.relative_to(sync_adapters.CANONICAL): hashlib.sha256(p.read_bytes()).hexdigest()
                 for p in sync_adapters.CANONICAL.rglob("*") if p.is_file() and "__pycache__" not in p.parts}
        self.assertEqual(before, after)

    def test_existing_output_is_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "build"
            package = root / "agent-skills/skills/chinese-official-writing"
            package.mkdir(parents=True)
            sentinel = package / "local.txt"
            sentinel.write_text("keep", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                sync_adapters.build_packages(root)
            self.assertEqual(sentinel.read_text("utf-8"), "keep")
            self.assertFalse((root / "qwen-code").exists())

    def test_source_locations_are_rejected(self):
        for root in (sync_adapters.ROOT, sync_adapters.CANONICAL,
                     sync_adapters.ROOT / "packages", sync_adapters.ROOT / "packages/new"):
            with self.subTest(root=root), self.assertRaises(ValueError):
                sync_adapters.build_packages(root)


if __name__ == "__main__":
    unittest.main()
