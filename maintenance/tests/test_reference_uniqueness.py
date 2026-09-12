from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class ReferenceUniquenessTests(unittest.TestCase):
    def test_rules_have_one_canonical_home(self) -> None:
        path = ROOT / "maintenance/tools/audit_reference_uniqueness.py"
        spec = importlib.util.spec_from_file_location("reference_uniqueness", path)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.assertEqual(module.audit(), [])

    def test_body_only_page_owns_delivery_behavior(self) -> None:
        delivery = (ROOT / "chinese-official-writing/references/delivery-body-only.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("只要稿件", delivery)
        self.assertIn("省略通常交付中的文后提示", delivery)


if __name__ == "__main__":
    unittest.main()
