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
        self.assertEqual(text.count("用户需求 → 选择文种 → 写稿或改稿 → 按步骤检查 → 交付"), 1)
        self.assertNotIn("## 任务模式路由与写作主线", text)
        scope = text.split("## 入口契约", 1)[0]
        self.assertIn("README.md", scope)
        self.assertNotIn("references/", scope)
        self.assertNotIn("compatibility-scene-routing.md", scope)
        self.assertNotIn("hooks/README.md", scope)

    def test_tool_routes_name_their_single_entry_pages(self) -> None:
        text = (ROOT / "chinese-official-writing/SKILL.md").read_text(encoding="utf-8")
        self.assertEqual(text.count("references/prose-lint-usage.md"), 1)
        self.assertNotIn("hooks/", text)
        self.assertNotIn("references/delivery-review-gate.md", text)
        usage = (ROOT / "chinese-official-writing/references/prose-lint-usage.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("scripts/prose_lint.py", usage)


if __name__ == "__main__":
    unittest.main()
