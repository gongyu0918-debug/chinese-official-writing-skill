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

    def test_homepage_keeps_one_route_spine(self) -> None:
        path = ROOT / "maintenance/tools/audit_product_surface.py"
        spec = importlib.util.spec_from_file_location("product_surface_audit_route", path)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        text = (ROOT / "chinese-official-writing/SKILL.md").read_text(encoding="utf-8")
        self.assertEqual(text.count("交付动作 → 主文种首叶"), 1)
        self.assertNotIn("## 任务模式路由与写作主线", text)
        scope = text.split("## 入口契约", 1)[0]
        self.assertIn("README.md", scope)
        self.assertNotIn("references/", scope)
        self.assertNotIn("compatibility-scene-routing.md", scope)
        self.assertNotIn("hooks/README.md", scope)

    def test_tool_routes_name_their_single_entry_pages(self) -> None:
        text = (ROOT / "chinese-official-writing/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("唯一脚本路由是 `references/prose-lint-usage.md`", text)
        self.assertIn("先读 `hooks/README.md`", text)
        self.assertIn("references/delivery-review-gate.md", text)


if __name__ == "__main__":
    unittest.main()
