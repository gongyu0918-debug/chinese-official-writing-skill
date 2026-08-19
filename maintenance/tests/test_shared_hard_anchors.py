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
        self.assertEqual(
            ("项目名称",),
            ANCHORS.snapshot("项目名称：档案数字化。").fields,
        )
        self.assertIsNone(
            ANCHORS.compare(
                "会议指出：要抓好落实；同时强调：要压实责任。",
                "会议指出：要抓好落实；并强调：要压实责任。",
            )["reason"]
        )
        self.assertIsNone(
            ANCHORS.compare(
                "会议指出：要抓好落实；同时强调：要压实责任",
                "会议指出：要抓好落实；并强调：要压实责任",
            )["reason"]
        )
        self.assertEqual(
            (),
            ANCHORS.snapshot("现将有关情况说明如下：目前已完成核验。").fields,
        )
        self.assertEqual(
            ("项目名称",),
            ANCHORS.snapshot(
                "会议指出：要抓好落实；项目名称：档案数字化"
            ).fields,
        )
        for indentation in ("\t", "　"):
            with self.subTest(indentation=repr(indentation)):
                self.assertEqual(
                    ("项目名称",),
                    ANCHORS.snapshot(
                        f"{indentation}项目名称：档案数字化"
                    ).fields,
                )
        self.assertEqual(
            "fields",
            ANCHORS.compare(
                "会议指出：要抓好落实；项目名称：档案数字化",
                "会议指出：要抓好落实",
            )["reason"],
        )
        self.assertIsNone(
            ANCHORS.compare(
                "",
                "项目名称：甲。\n项目名称：乙。",
                "项目名称：甲。\n项目名称：乙。",
            )["reason"]
        )

    def test_existing_field_authority_does_not_allow_a_duplicate(self) -> None:
        self.assertEqual(
            "fields",
            ANCHORS.compare(
                "项目名称：设备采购",
                "项目名称：设备采购；项目名称：设备采购",
                allowed_field_labels={"项目名称"},
            )["reason"],
        )
        self.assertEqual(
            "fields",
            ANCHORS.compare(
                "",
                "项目名称：档案数字化。\n项目名称：档案数字化。",
                "项目名称：档案数字化。",
                allowed_field_labels={"项目名称"},
            )["reason"],
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
        for original, candidate in (
            ("该项工作十分重要。", "该项工作非常重要。"),
            ("一个个难题得到解决。", "难题逐个得到解决。"),
        ):
            with self.subTest(original=original):
                self.assertIsNone(ANCHORS.compare(original, candidate)["reason"])

    def test_under_length_routes_explicit_cjk_item_summary_to_semantic_review(self) -> None:
        request = (
            "材料：近期完成两方面工作。第一，更新办事指南。第二，开展窗口培训。"
            "请扩写到180—230字。"
        )
        original = "近期完成办事指南更新和窗口培训工作。一是更新指南。二是开展培训。"
        candidate = (
            "近期完成两项工作，分别为办事指南更新和窗口培训。"
            "一是完成指南更新。二是完成窗口培训。前一项明确办事内容，后一项对应培训事项。"
        )
        strict = ANCHORS.compare(original, candidate, request)
        self.assertEqual("quantities", strict["reason"])

        relaxed = ANCHORS.compare(
            original,
            candidate,
            request,
            allow_transparent_quantity_summaries=True,
        )
        self.assertIsNone(relaxed["reason"])
        self.assertEqual("semantic_review_required", relaxed["status"])
        self.assertEqual(
            ["quantity_summary"],
            [item["kind"] for item in relaxed["relation_packet"]],
        )
        self.assertEqual((), ANCHORS.snapshot("前一项完成，后一项推进。").quantities)
        self.assertEqual(
            ("第一项",),
            tuple(item.value for item in ANCHORS.snapshot("第一项工作已完成。").quantities),
        )

    def test_anaphoric_relief_does_not_hide_real_counts_or_rhetorical_aspects(self) -> None:
        self.assertEqual(
            "quantities",
            ANCHORS.compare("会后三天内报送。", "会后两天内报送。")['reason'],
        )
        self.assertEqual(
            "quantities",
            ANCHORS.compare("前三项已完成。", "前五项已完成。")['reason'],
        )
        rhetorical = "一方面要核对设备，另一方面要完善台账。"
        self.assertEqual((), ANCHORS.snapshot(rhetorical).quantities)
        self.assertIsNone(
            ANCHORS.compare(rhetorical, "要核对设备并完善台账。")['reason']
        )

    def test_ordinal_items_do_not_use_transparent_summary_relief(self) -> None:
        result = ANCHORS.compare(
            "材料明确两方面工作。",
            "材料明确两方面工作。第二项工作已完成。",
            allow_transparent_quantity_summaries=True,
        )
        self.assertEqual("quantities", result["reason"])
        self.assertEqual(["第二项"], result["violations"]["added_quantities"])
        self.assertEqual([], result["relation_packet"])

    def test_transparent_summary_never_changes_the_authoritative_count(self) -> None:
        request = "材料分两方面，请扩写到80—120字。"
        self.assertEqual(
            "quantities",
            ANCHORS.compare(
                "现将两方面情况说明如下。",
                "现将三项情况说明如下。",
                request,
                allow_transparent_quantity_summaries=True,
            )["reason"],
        )
        self.assertEqual(
            "quantities",
            ANCHORS.compare(
                "涉及两个小区。",
                "涉及三个小区。",
                request,
                allow_transparent_quantity_summaries=True,
            )["reason"],
        )

    def test_real_under_length_d1_reaches_semantic_verifier_after_summary_relief(self) -> None:
        request = (
            "根据以下材料起草一份工作情况说明，正文180—230字。材料："
            "市政务服务中心近期完成两方面工作。第一，更新线上办事指南，"
            "补充申请材料清单、办理步骤和咨询电话，8月15日上线。第二，"
            "开展窗口业务培训，共4场，参加人员86人，培训内容为新指南使用和咨询答复口径。"
            "两方面工作均已完成。"
        )
        original = (
            "市政务服务中心近期完成服务指引更新和窗口培训工作。一是更新线上办事指南，"
            "补充申请材料清单、办理步骤和咨询电话，新指南于8月15日上线。二是开展窗口业务培训，"
            "共4场、86人参加，培训内容为新指南使用和咨询答复口径。"
        )
        candidate = (
            "市政务服务中心近期完成两项服务工作，分别为线上办事指南更新和窗口业务培训，"
            "现将有关情况说明如下。一是完成线上办事指南更新，补充申请材料清单、办理步骤和咨询电话，"
            "更新后的新指南于8月15日上线。二是完成窗口业务培训，共开展4场，参加人员86人，"
            "培训内容为新指南使用和咨询答复口径。线上办事指南更新工作和窗口业务培训工作均已完成，"
            "前一项工作明确了指南补充内容及上线日期，后一项工作明确了培训场次、参加人员及培训内容。"
        )
        spec = {"minimum": 180, "maximum": 230, "scope": "body"}
        self.assertIsNone(UNDER.mechanical_reason(original, candidate, spec, request))
        prompt = UNDER._verdict_instruction(
            request,
            original,
            candidate,
            spec,
            UNDER._increment_items(original, candidate),
        )
        self.assertIn("quantity_summary", prompt)

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
        self.assertEqual(
            {"请求事项", "项目名称"},
            UNDER._required_field_labels(
                "字段包括项目名称、请求事项，请扩写。"
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
        self.assertIsNone(
            ANCHORS.compare(
                "活动筹备工作正在推进。",
                "活动筹备工作正在推进，已有100人报名。",
                "请写明已有100人报名，扩写到100—200字。",
                ignored_authority_values={"100", "200"},
            )["reason"]
        )
        self.assertIsNone(
            ANCHORS.compare(
                "设备采购正在办理。",
                "拟购置H100设备。",
                "材料指定H100设备，请扩写到100—200字。",
                ignored_authority_values={"100", "200"},
            )["reason"]
        )

    def test_compare_failure_and_second_load_failure_fall_back(self) -> None:
        broken = type("BrokenAnchors", (), {"compare": staticmethod(lambda *args, **kwargs: 1 / 0)})()
        with patch.object(UNDER, "_load_hard_anchor_contract", return_value=broken):
            self.assertEqual(
                "under_length_hard_anchor_contract_unavailable",
                UNDER.mechanical_reason(
                    "原稿。", "候选稿。", {"minimum": 1, "maximum": 100, "scope": "full"}, ""
                ),
            )

        class BreakOnSecondCompare:
            def __init__(self) -> None:
                self.calls = 0

            def compare(self, *args, **kwargs):
                self.calls += 1
                if self.calls == 1:
                    return {"reason": None, "relation_packet": []}
                raise RuntimeError("second compare failed")

        second = BreakOnSecondCompare()
        record = {
            "request": "",
            "under_length": {
                "phase": UNDER.PHASE_REVISION,
                "original": "原稿。",
                "original_count": 3,
                "spec": {"minimum": 1, "maximum": 100, "scope": "full"},
            },
        }
        with patch.object(UNDER, "_load_hard_anchor_contract", return_value=second):
            result = UNDER.advance(
                {"last_assistant_message": "候选稿。"}, record
            )
        self.assertEqual("block", result["decision"])
        self.assertEqual("D0", record["under_length"]["audit"]["selection"])
        self.assertEqual(
            "under_length_hard_anchor_contract_unavailable",
            record["under_length"]["audit"]["reason"],
        )

        over_record = {
            "request": "",
            "over_length": {
                "original": "原稿。",
                "original_count": 3,
                "spec": {"minimum": 0, "maximum": 100, "scope": "full"},
            },
        }
        with patch.object(OVER, "_verdict_instruction", return_value=None):
            result = OVER._begin_verdict(over_record, "候选稿。")
        self.assertEqual("block", result["decision"])
        self.assertEqual("D0", over_record["over_length"]["audit"]["selection"])
        self.assertEqual(
            "over_length_hard_anchor_contract_unavailable",
            over_record["over_length"]["audit"]["reason"],
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
