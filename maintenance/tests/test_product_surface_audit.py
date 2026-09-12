from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class ProductSurfaceAuditTests(unittest.TestCase):
    def test_user_facing_surface_has_no_engineering_commands(self) -> None:
        path = ROOT / "maintenance/tools/audit_product_surface.py"
        spec = importlib.util.spec_from_file_location("product_surface_audit", path)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.assertEqual(module.audit(), [])


if __name__ == "__main__":
    unittest.main()
