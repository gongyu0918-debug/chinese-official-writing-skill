from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class ProductSurfaceAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        spec = importlib.util.spec_from_file_location("product_surface_audit", ROOT / "maintenance/tools/audit_product_surface.py")
        cls.audit_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.audit_module)

    def test_current_product_paths_are_reachable(self) -> None:
        self.assertEqual(self.audit_module.audit(), [])

    def test_rewording_sections_does_not_change_path_validation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            product = Path(directory)
            (product / "references").mkdir()
            (product / "references/leaf.md").write_text("# 一份参考\n正文规则。", encoding="utf-8")
            for heading in ("## 选择文种", "## 按用途选择所需参考", "## 写作准备"):
                for link in ("`references/leaf.md`", "[所需参考](references/leaf.md)"):
                    (product / "SKILL.md").write_text(heading + "\n读取 " + link + "。", encoding="utf-8")
                    with self.subTest(heading=heading, link=link):
                        self.assertEqual(self.audit_module.audit(product), [])

    def test_missing_link_and_orphan_are_detected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            product = Path(directory)
            (product / "references").mkdir()
            (product / "references/orphan.md").write_text("独立参考。", encoding="utf-8")
            (product / "SKILL.md").write_text("读取 `references/missing.md`。", encoding="utf-8")
            errors = self.audit_module.audit(product)
            self.assertTrue(any("missing linked file" in item for item in errors))
            self.assertTrue(any("unreachable reference" in item for item in errors))

    def test_developer_command_is_detected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            product = Path(directory)
            (product / "SKILL.md").write_text("执行 git commit 提交构建。", encoding="utf-8")
            self.assertTrue(any("developer command" in item for item in self.audit_module.audit(product)))


if __name__ == "__main__":
    unittest.main()
