from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile

from maintenance.tools import evidence_archive as archive


class EvidenceArchiveTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.data = "真实原稿\r\n保留缺失状态。\n".encode()
        self.item = {"path": "maintenance/tests/evidence/sample/final.txt",
                     "size": len(self.data), "sha256": hashlib.sha256(self.data).hexdigest()}
        self.package = self.root / "archive.zip"
        with zipfile.ZipFile(self.package, "w") as package:
            package.writestr(self.item["path"], self.data)

    def test_extract_preserves_bytes_and_refuses_overwrite(self):
        with patch.object(archive, "ROOT", self.root):
            result = archive.extract(self.item, self.root / "output/restored", self.package)
            self.assertEqual(result.read_bytes(), self.data)
            with self.assertRaises(FileExistsError):
                archive.extract(self.item, self.root / "output/restored", self.package)

    def test_corrupt_bytes_are_rejected_before_writing(self):
        with zipfile.ZipFile(self.package, "w") as package:
            package.writestr(self.item["path"], b"changed")
        with patch.object(archive, "ROOT", self.root), self.assertRaisesRegex(ValueError, "checksum"):
            archive.extract(self.item, self.root / "output/restored", self.package)
        self.assertFalse((self.root / "output").exists())

    def test_extraction_cannot_escape_output(self):
        with patch.object(archive, "ROOT", self.root), self.assertRaisesRegex(ValueError, "output"):
            archive.extract(self.item, self.root / "product", self.package)

    def test_index_rejects_traversal_and_duplicate_paths(self):
        index = self.root / "index.jsonl"
        for names in [["maintenance/tests/evidence/../../outside"],
                      [self.item["path"], self.item["path"]]]:
            index.write_text("\n".join(json.dumps({"path": name}) for name in names))
            with self.assertRaises(ValueError):
                archive.load_index(index)


if __name__ == "__main__":
    unittest.main()
