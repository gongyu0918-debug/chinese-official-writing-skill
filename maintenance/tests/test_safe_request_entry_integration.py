from __future__ import annotations

import hashlib
import importlib.util
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
CANONICAL = ROOT / "chinese-official-writing"
PERSISTENT_MIRROR_ROOTS = (
    ROOT / "packages" / "agent-skills" / "skills" / "chinese-official-writing",
    ROOT / "packages" / "qwen-code" / "skills" / "chinese-official-writing",
    ROOT / "packages" / "hermes" / "skills" / "chinese-official-writing",
    ROOT / "packages" / "openclaw" / "skills" / "chinese_official_writing",
)
REQUEST_LEAF = "references/genre-playbook-request.md"
FINAL_REVIEW_REFS = [
    "references/final-review-layers.md",
    "references/anti-ai-patterns.md",
    "references/prose-lint-usage.md",
    "references/delivery.md",
]
REQUEST_DRAFT_REFS = [
    "SKILL.md",
    "references/information-selection.md",
    REQUEST_LEAF,
    *FINAL_REVIEW_REFS,
]
COMPLEX_REFS = {
    "references/handling-elements.md",
    "references/argument-chains.md",
}


def _load_provider():
    path = ROOT / "maintenance" / "evals" / "official-writing" / "providers" / "agent_writer.py"
    spec = importlib.util.spec_from_file_location("safe_request_provider_under_test", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


provider = _load_provider()


def _load_prose_lint():
    path = CANONICAL / "scripts" / "prose_lint.py"
    spec = importlib.util.spec_from_file_location("safe_request_prose_lint_under_test", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


prose_lint = _load_prose_lint()


class SafeRequestEntryIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.mirror_roots = PERSISTENT_MIRROR_ROOTS

    def test_request_drafts_load_only_the_dedicated_leaf_by_default(self) -> None:
        for genre in ("请示", "申请"):
            with self.subTest(genre=genre):
                self.assertEqual(
                    provider._reference_paths_for_genres(
                        [genre],
                        [f"请起草一份{genre}，写清请批事项。"],
                    ),
                    REQUEST_DRAFT_REFS,
                )

    def test_simple_and_negated_procurement_requests_stay_on_request_leaf(self) -> None:
        tasks = (
            "起草采购申请：购买一台打印机，单价3000元，总价3000元。",
            "起草采购请示：本次不是多品类采购，不需要分项核算，不含报价、验收或技术附件，只申请购置一台打印机。",
            "起草纯软件订阅采购申请，材料未给询价和验收信息，按现有事实成稿。",
            "按字段式材料起草采购申请：用途：办公；品名：打印机；数量：1台；单价：3000元；总价：3000元。",
        )
        for task in tasks:
            with self.subTest(task=task):
                refs = provider._reference_paths_for_genres(["申请"], [task])
                self.assertEqual(refs, REQUEST_DRAFT_REFS)

    def test_complex_procurement_markers_upgrade_request_route(self) -> None:
        tasks = (
            "起草采购请示：采购多品类设备，规格不同。",
            "起草采购申请：设备价格不同，须分项核算。",
            "起草采购请示：附三家报价并写明验收标准。",
            "起草采购申请：设备已询价，请写清报价情况。",
            "起草购置申请：随文提交技术附件。",
            "起草一份800字采购申请，购买一台打印机。",
        )
        for task in tasks:
            with self.subTest(task=task):
                refs = provider._reference_paths_for_genres(["请示"], [task])
                self.assertEqual(
                    [ref for ref in refs if ref.startswith("references/genre-playbook-")],
                    [REQUEST_LEAF],
                )
                self.assertTrue(COMPLEX_REFS.issubset(refs))
                self.assertNotIn("references/workflow.md", refs)
                self.assertNotIn("references/genre-playbooks.md", refs)
                self.assertNotIn("references/task-route-cards.md", refs)

    def test_procurement_markers_do_not_upgrade_notifications(self) -> None:
        refs = provider._reference_paths_for_genres(
            ["通知"],
            ["起草采购验收通知，附报价单和技术附件。"],
        )
        self.assertEqual(
            [ref for ref in refs if ref.startswith("references/genre-playbook-")],
            ["references/genre-playbook-notice.md"],
        )
        self.assertTrue(COMPLEX_REFS.isdisjoint(refs))
        self.assertNotIn(REQUEST_LEAF, refs)

    def test_request_leaf_compact_and_escalation_shape_is_identical_in_all_mirrors(self) -> None:
        relative = Path("references/genre-playbook-request.md")
        canonical_bytes = (CANONICAL / relative).read_bytes()
        canonical_text = canonical_bytes.decode("utf-8")
        request_rules = [
            line
            for line in canonical_text.splitlines()
            if line.startswith("- 单项采购请示或申请")
        ]
        self.assertEqual(len(request_rules), 1)
        request_rule = request_rules[0]
        self.assertIn("可用一至两个自然段", request_rule)
        self.assertIn("段内写清缘由与使用需要", request_rule)
        self.assertIn("拟购品名规格和数量金额、请批事项", request_rule)
        self.assertIn("具体故障、损失、政策条款、采购程序或审批结论仍以材料为准", request_rule)
        self.assertIn("`handling-elements.md`", request_rule)
        self.assertIn("`argument-chains.md`", request_rule)
        self.assertNotIn("workflow.md", request_rule)
        self.assertIn("字段表格保持原结构", request_rule)
        for reason_contract in (
            "现状、用途、使用需要或制度依据",
            "自然的原因句，与申请事项连贯表达",
            "常识支持的一般必要性也可写入",
            "正文保留已知事项和请求，文后提示询问具体缘由",
            "为满足日常办公需要",
            "现有设备已不能满足日常办公需要",
        ):
            self.assertIn(reason_contract, canonical_text)
        expected_hash = hashlib.sha256(canonical_bytes).hexdigest()
        for mirror in self.mirror_roots:
            with self.subTest(mirror=mirror):
                self.assertEqual(hashlib.sha256((mirror / relative).read_bytes()).hexdigest(), expected_hash)

    def test_entry_relief_and_placeholder_relocation_remain_covered(self) -> None:
        skill = (CANONICAL / "SKILL.md").read_text(encoding="utf-8")
        handling = (CANONICAL / "references" / "handling-elements.md").read_text(encoding="utf-8")
        final_review = (CANONICAL / "references" / "final-review-layers.md").read_text(encoding="utf-8")
        format_rules = (CANONICAL / "references" / "format-gbt9704.md").read_text(encoding="utf-8")

        self.assertIn("英文、文学、营销软文、社交媒体文案、个人求职信和代码说明", skill)
        self.assertNotIn("闲聊回复", skill)
        self.assertNotIn("通用翻译", skill)
        placeholders = (
            "〔签发日期〕",
            "〔会议时间〕",
            "[具体项目名称]",
            "XXXX万元",
            "YYYY年MM月DD日",
        )
        for example in placeholders:
            with self.subTest(example=example):
                self.assertNotIn(example, skill)
        for example in placeholders[:2]:
            self.assertIn(example, format_rules)
        self.assertIn("正式稿清理无用途的占位", handling)
        self.assertIn("模板稿或用户指定空字段按原要求保留", handling)
        self.assertIn("正式成稿清理未完成占位", final_review)
        self.assertIn("用户要求模板或保留空字段时按其用途处理", final_review)

        findings = prose_lint.scan(
            "placeholder-probe.txt",
            "\n".join(placeholders),
            delivery_mode="draft-body",
        )
        placeholder_matches = {
            finding.match
            for finding in findings
            if finding.label == "unfinished-placeholder"
        }
        self.assertEqual(placeholder_matches, set(placeholders))


if __name__ == "__main__":
    unittest.main()
