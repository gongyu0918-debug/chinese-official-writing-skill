from __future__ import annotations

from pathlib import Path
import unittest

from maintenance.tests.hook_companion_support import HookCompanionTestMixin


ROOT = Path(__file__).resolve().parents[2]
CANONICAL = ROOT / "chinese-official-writing"
PERSISTENT_MIRROR_ROOTS = (
    ROOT / "packages" / "agent-skills" / "skills" / "chinese-official-writing",
    ROOT / "packages" / "qwen-code" / "skills" / "chinese-official-writing",
    ROOT / "packages" / "hermes" / "skills" / "chinese-official-writing",
    ROOT / "packages" / "openclaw" / "skills" / "chinese_official_writing",
)
RELATIVE = Path("references/information-selection.md")
CLASSIFICATION_RULE = (
    "事实之间的时间、因果、分类和归属关系以材料明确关系为准；"
    "总量与子项差额只用于合计校核，不据此补写“其余均正常、未发现其他问题、均无异常”等材料未给结论。"
)


class InformationSelectionClassificationTests(HookCompanionTestMixin, unittest.TestCase):
    def setUp(self) -> None:
        self.setUpHookCompanions()
        self.mirror_roots = (
            *(
                self.companion_roots[host] / "skills/chinese-official-writing"
                for host in ("codex", "codebuddy", "claude-code")
            ),
            *PERSISTENT_MIRROR_ROOTS,
        )

    def test_unclassified_remainder_is_reconciled_without_static_classification(self) -> None:
        text = (CANONICAL / RELATIVE).read_text(encoding="utf-8")

        self.assertEqual(text.count(CLASSIFICATION_RULE), 1)
        self.assertNotIn("总量与子项差额归入", text)
        self.assertNotIn("总量与子项差额归为", text)
        self.assertNotIn("总量与子项差额视为", text)
        cards = (CANONICAL / "references/task-route-cards.md").read_text(encoding="utf-8")
        self.assertIn("不用差额补写“其余均正常、未发现其他异常”", cards)
        self.assertIn("不再写“处理工作正在进行”等同义句凑字", cards)

    def test_explicit_classification_control_remains_material_bound_in_all_mirrors(self) -> None:
        canonical_bytes = (CANONICAL / RELATIVE).read_bytes()
        canonical_text = canonical_bytes.decode("utf-8")

        self.assertIn("分类和归属关系以材料明确关系为准", canonical_text)
        for mirror in self.mirror_roots:
            with self.subTest(mirror=mirror):
                self.assertEqual((mirror / RELATIVE).read_bytes(), canonical_bytes)


if __name__ == "__main__":
    unittest.main()
