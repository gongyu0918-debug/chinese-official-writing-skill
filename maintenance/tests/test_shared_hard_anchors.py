from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[2]
ANCHOR_PATH = ROOT / "chinese-official-writing/hooks/shared/hard_anchors.py"
OVER_PATH = ROOT / "chinese-official-writing/hooks/capabilities/over_length/runtime.py"
UNDER_PATH = ROOT / "chinese-official-writing/hooks/capabilities/under_length/runtime.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


ANCHORS = load_module("cow_shared_hard_anchor_tests", ANCHOR_PATH)
OVER = load_module("cow_shared_over_length_tests", OVER_PATH)
UNDER = load_module("cow_shared_under_length_tests", UNDER_PATH)


class SharedHardAnchorTests(unittest.TestCase):
    def test_missing_or_added_values_fall_back(self) -> None:
        original = "运行管理科核验12件，客户服务科核验21件。"
        self.assertEqual("numbers", ANCHORS.compare(original, "运行管理科核验12件。")['reason'])
        self.assertEqual(
            "numbers",
            ANCHORS.compare(original, original + "另有3件待办。")["reason"],
        )

    def test_exact_quotes_and_field_order_are_stable(self) -> None:
        quoted = "王明强调：‘数据必须真实、准确、完整。’"
        self.assertEqual(
            "quotes",
            ANCHORS.compare(quoted, '王明强调：“数据必须真实、准确、完整。”')["reason"],
        )
        fields = "项目名称：档案数字化\n申请数量：6台\n预算金额：25200元"
        reordered = "申请数量：6台\n项目名称：档案数字化\n预算金额：25200元"
        self.assertEqual("fields", ANCHORS.compare(fields, reordered)["reason"])

    def test_prose_colon_is_not_a_field_but_inline_form_fields_are_complete(self) -> None:
        self.assertEqual(
            (),
            ANCHORS.snapshot("现将有关情况说明如下：\n一、基本情况").fields,
        )
        self.assertEqual(
            ("姓名", "部门"),
            ANCHORS.snapshot("姓名：甲；部门：乙").fields,
        )
        self.assertEqual(
            "fields",
            ANCHORS.compare("姓名：甲；部门：乙", "姓名：甲；科室：乙")["reason"],
        )

    def test_ascii_identifiers_and_common_cjk_quantities_are_hard_anchors(self) -> None:
        for original, candidate, reason in (
            ("设备型号H100。", "设备型号H200。", "numbers"),
            ("批次A12正在核验。", "批次A13正在核验。", "numbers"),
            ("涉及两个小区。", "涉及三个小区。", "quantities"),
            ("开展两场活动。", "开展三场活动。", "quantities"),
        ):
            with self.subTest(original=original):
                self.assertEqual(reason, ANCHORS.compare(original, candidate)["reason"])

    def test_count_reduction_requires_relation_review(self) -> None:
        original = "本次共核验75件工单。经逐项核对，75件工单均已纳入本次核验范围，其中22件需要补充材料。"
        candidate = "本次共核验75件工单，其中22件需要补充材料。"
        result = ANCHORS.compare(original, candidate)
        self.assertEqual("semantic_review_required", result["status"])
        self.assertEqual(
            [{"kind": "number", "value": "75件", "before": 2, "after": 1}],
            result["count_reductions"],
        )
        self.assertTrue(result["relation_packet"])

    def test_relation_swap_is_not_mechanically_approved(self) -> None:
        original = "运行管理科核验12件，客户服务科核验21件。"
        candidate = "运行管理科核验21件，客户服务科核验12件。"
        result = ANCHORS.compare(original, candidate)
        self.assertTrue(result["mechanical_ok"])
        self.assertEqual("semantic_review_required", result["status"])
        self.assertEqual({"12件", "21件"}, {item["value"] for item in result["relation_packet"]})

    def test_both_length_capabilities_use_shared_contract(self) -> None:
        over_spec = {"minimum": 0, "maximum": 80, "scope": "full"}
        original = "项目名称：档案数字化\n申请数量：6台\n预算金额：25200元"
        reordered = "申请数量：6台\n项目名称：档案数字化\n预算金额：25200元"
        self.assertEqual(
            "over_length_field_order_or_name_changed",
            OVER.mechanical_reason(original, reordered, over_spec),
        )
        under_spec = {"minimum": 1, "maximum": 100, "scope": "full"}
        self.assertEqual(
            "under_length_field_order_or_name_changed",
            UNDER.mechanical_reason(original, reordered, under_spec, "扩写到1—100字"),
        )

    def test_under_length_allows_authoritative_request_value_but_not_length_bound(self) -> None:
        spec = {"minimum": 20, "maximum": 100, "scope": "full"}
        original = "已核验12件工单，现将有关情况说明如下。"
        allowed = "已核验12件工单，材料另载3件待办，现将有关情况说明如下。"
        request = "材料另有3件待办，请扩写到20—100字。"
        self.assertIsNone(UNDER.mechanical_reason(original, allowed, spec, request))
        added_bound = allowed + "正文共20字。"
        self.assertEqual(
            "under_length_number_added_dropped_or_changed",
            UNDER.mechanical_reason(original, added_bound, spec, request),
        )

    def test_under_length_allows_only_requested_new_fields(self) -> None:
        spec = {"minimum": 1, "maximum": 100, "scope": "full"}
        original = "采购事项正在办理。"
        requested = "项目名称：设备采购\n采购事项正在办理。"
        request = "字段包括项目名称，请扩写到1—100字。"
        self.assertIsNone(UNDER.mechanical_reason(original, requested, spec, request))
        self.assertEqual(
            "under_length_field_order_or_name_changed",
            UNDER.mechanical_reason(
                original,
                "内部备注：待定\n采购事项正在办理。",
                spec,
                request,
            ),
        )
        self.assertEqual(
            {"申请数量", "采购请示", "项目名称"},
            UNDER._required_labels(
                "标题为采购请示，字段包括项目名称、申请数量，请扩写。"
            ),
        )

    def test_length_bound_with_unit_does_not_authorize_a_new_fact(self) -> None:
        result = ANCHORS.compare(
            "采购事项正在办理。",
            "采购事项正在办理，共300个。",
            "请扩写到300—400个字。",
            ignored_authority_values={"300", "400"},
        )
        self.assertEqual("numbers", result["reason"])

    def test_contract_load_is_stable_and_compare_failure_falls_back(self) -> None:
        self.assertIs(UNDER._load_hard_anchor_contract(), UNDER._load_hard_anchor_contract())
        self.assertIs(OVER._load_hard_anchor_contract(), OVER._load_hard_anchor_contract())
        broken = type("BrokenAnchors", (), {"compare": staticmethod(lambda *args, **kwargs: 1 / 0)})()
        with patch.object(UNDER, "_load_hard_anchor_contract", return_value=broken):
            self.assertEqual(
                "under_length_hard_anchor_contract_unavailable",
                UNDER.mechanical_reason(
                    "原稿。", "候选稿。", {"minimum": 1, "maximum": 100, "scope": "full"}, ""
                ),
            )
        with patch.object(OVER, "_load_hard_anchor_contract", return_value=broken):
            self.assertEqual(
                "over_length_hard_anchor_contract_unavailable",
                OVER.mechanical_reason(
                    "原稿。", "候选稿。", {"minimum": 0, "maximum": 100, "scope": "full"}
                ),
            )

    def test_semantic_verifiers_accept_equivalent_total_scope_without_relation_loss(self) -> None:
        original = "本次共核验75件工单。经逐项核对，75件工单均已纳入本次核验范围，其中22件需要补充材料。"
        candidate = "本次共核验75件工单，经逐项核对，其中22件需补充材料。"
        over_prompt = OVER._verdict_instruction(
            "压缩至100字以内。", original, candidate, {"minimum": 0, "maximum": 100, "scope": "full"}
        )
        under_prompt = UNDER._verdict_instruction(
            "扩写到80—100字。",
            original,
            candidate,
            {"minimum": 80, "maximum": 100, "scope": "full"},
            UNDER._increment_items(original, candidate),
        )
        for prompt in (over_prompt, under_prompt):
            self.assertIn("等义总量句明确承载同一主体、对象和范围", prompt)
            self.assertIn("范围缩小、主体或对象换位", prompt)
        self.assertIn("‘涉及两个小区’、‘86人参加’", under_prompt)


if __name__ == "__main__":
    unittest.main()
