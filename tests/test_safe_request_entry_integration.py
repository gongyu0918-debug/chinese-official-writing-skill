from __future__ import annotations

import hashlib
import importlib.util
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
CANONICAL = ROOT / "chinese-official-writing"
MIRROR_ROOTS = (
    ROOT / "skills" / "chinese-official-writing",
    ROOT / ".agents" / "skills" / "chinese-official-writing",
    ROOT / ".qwen" / "skills" / "chinese-official-writing",
    ROOT / "hermes" / "skills" / "chinese-official-writing",
    ROOT / "openclaw" / "skills" / "chinese_official_writing",
)
REQUEST_LEAF = "references/genre-playbook-request.md"
COMPLEX_REFS = {
    "references/workflow.md",
    "references/handling-elements.md",
    "references/argument-chains.md",
}


def _load_provider():
    path = ROOT / "evals" / "official-writing" / "providers" / "agent_writer.py"
    spec = importlib.util.spec_from_file_location("safe_request_provider_under_test", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


provider = _load_provider()


class SafeRequestEntryIntegrationTests(unittest.TestCase):
    def test_request_drafts_load_only_the_dedicated_leaf_by_default(self) -> None:
        for genre in ("请示", "申请"):
            with self.subTest(genre=genre):
                self.assertEqual(
                    provider._reference_paths_for_genres(
                        [genre],
                        [f"请起草一份{genre}，写清请批事项。"],
                    ),
                    ["SKILL.md", REQUEST_LEAF],
                )

    def test_simple_and_negated_procurement_requests_stay_on_request_leaf(self) -> None:
        tasks = (
            "起草采购申请：购买一台打印机，单价3000元，总价3000元。",
            "起草采购请示：本次不是多品类采购，不需要分项核算，不含报价、验收或技术附件，只申请购置一台打印机。",
        )
        for task in tasks:
            with self.subTest(task=task):
                refs = provider._reference_paths_for_genres(["申请"], [task])
                self.assertEqual(refs, ["SKILL.md", REQUEST_LEAF])

    def test_complex_procurement_markers_upgrade_request_route(self) -> None:
        tasks = (
            "起草采购请示：采购多品类设备，规格不同。",
            "起草采购申请：设备价格不同，须分项核算。",
            "起草采购请示：附三家报价并写明验收标准。",
            "起草购置申请：随文提交技术附件。",
        )
        for task in tasks:
            with self.subTest(task=task):
                refs = provider._reference_paths_for_genres(["请示"], [task])
                self.assertIn(REQUEST_LEAF, refs)
                self.assertTrue(COMPLEX_REFS.issubset(refs))
                self.assertNotIn("references/genre-playbooks.md", refs)
                self.assertNotIn("references/task-route-cards.md", refs)

    def test_procurement_markers_do_not_upgrade_notifications(self) -> None:
        refs = provider._reference_paths_for_genres(
            ["通知"],
            ["起草采购验收通知，附报价单和技术附件。"],
        )
        self.assertIn("references/genre-playbooks.md", refs)
        self.assertTrue(COMPLEX_REFS.isdisjoint(refs))
        self.assertNotIn(REQUEST_LEAF, refs)

    def test_request_leaf_compact_shape_is_identical_in_all_mirrors(self) -> None:
        relative = Path("references/genre-playbook-request.md")
        canonical_bytes = (CANONICAL / relative).read_bytes()
        expected_line = (
            "单项采购申请以一至两个自然段连贯写清已给的用途、品名规格、数量、单价、总价和经费来源；"
            "同一事项的品名、数量和金额连续呈现。多品类、分项核算、比价验收或用户字段表格按原结构展开。"
        )
        self.assertIn(expected_line, canonical_bytes.decode("utf-8"))
        expected_hash = hashlib.sha256(canonical_bytes).hexdigest()
        for mirror in MIRROR_ROOTS:
            with self.subTest(mirror=mirror):
                self.assertEqual(hashlib.sha256((mirror / relative).read_bytes()).hexdigest(), expected_hash)

    def test_entry_relief_and_placeholder_relocation_remain_covered(self) -> None:
        skill = (CANONICAL / "SKILL.md").read_text(encoding="utf-8")
        handling = (CANONICAL / "references" / "handling-elements.md").read_text(encoding="utf-8")
        final_review = (CANONICAL / "references" / "final-review-layers.md").read_text(encoding="utf-8")

        self.assertIn("英文写作、文学创作、营销软文、社交媒体文案、代码说明", skill)
        self.assertNotIn("闲聊回复", skill)
        self.assertNotIn("通用翻译", skill)
        for example in (
            "〔签发日期〕",
            "〔会议时间〕",
            "[具体项目名称]",
            "XXXX万元",
            "YYYY年MM月DD日",
            "（签发日期）",
            "（成文日期待确认）",
        ):
            with self.subTest(example=example):
                self.assertNotIn(example, skill)
                self.assertIn(example, handling)
                self.assertIn(example, final_review)


if __name__ == "__main__":
    unittest.main()
