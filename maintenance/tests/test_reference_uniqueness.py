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

    def test_final_delivery_step_owns_delivery_behavior(self) -> None:
        common = (ROOT / "chinese-official-writing/references/writing-rules.md").read_text(
            encoding="utf-8"
        )
        before, delivery = common.split("## 第四步：交付", 1)
        self.assertIn("只要稿件", delivery)
        self.assertIn("省略提示", delivery)
        self.assertIn("文后提示", delivery)
        self.assertNotIn("只要稿件", before)


if __name__ == "__main__":
    unittest.main()
