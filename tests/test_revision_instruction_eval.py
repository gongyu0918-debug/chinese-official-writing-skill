from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


revision_eval = load_module("revision_instruction_eval_under_test", ROOT / "tools" / "run_revision_instruction_eval.py")


class RevisionInstructionEvalTests(unittest.TestCase):
    def test_cases_cover_structural_genres_and_operations(self) -> None:
        genres = {case.genre for case in revision_eval.CASES}
        operations = {turn.operation for case in revision_eval.CASES for turn in case.turns}

        self.assertEqual(genres, {"通知", "请示", "申请", "报告", "会议纪要", "实施方案", "函"})
        for operation in [
            "remove_natural_paragraph",
            "add_natural_paragraph",
            "change_title",
            "change_subheading_outline",
            "outline_change",
            "delete_add_points",
            "reorder_paragraphs",
            "change_sender_receiver",
            "recipient_position",
            "closing_position",
            "preserve_real_application_template",
            "field_value_change",
            "change_sender_date",
        ]:
            self.assertIn(operation, operations)

    def test_report_format_flags_approval_language(self) -> None:
        case = next(item for item in revision_eval.CASES if item.genre == "报告")
        text = """关于专项整改工作进展情况的报告

市政府办公室：
现将专项整改工作进展情况报告如下。

一、整改进展
已完成整改。

妥否，请批示。

专项整改工作专班
2026年6月1日"""

        issues = revision_eval.genre_format_issues(text, case)

        self.assertIn("genre_function_mixed", {item["label"] for item in issues})

    def test_meeting_minutes_format_requires_fixed_elements(self) -> None:
        case = next(item for item in revision_eval.CASES if item.genre == "会议纪要")
        text = """项目推进协调会议纪要

一、关于任务分工
会议明确相关单位责任。

二、关于后续督办
会议要求按周反馈。"""

        issues = revision_eval.genre_format_issues(text, case)
        details = "\n".join(item["detail"] for item in issues)

        self.assertIn("会议时间", details)
        self.assertIn("会议地点", details)
        self.assertIn("参会人员", details)

    def test_semantic_present_accepts_formal_equivalents(self) -> None:
        self.assertTrue(revision_eval.semantic_term_present("原因分析", "经分析，主要原因是材料归集口径不一致。"))
        self.assertTrue(revision_eval.semantic_term_present("原因分析", "上述问题主要由于部门协同链条较长。"))
        self.assertTrue(revision_eval.semantic_term_present("反馈渠道", "问题反馈由综合部门统一接收，并按要求补充材料。"))
        self.assertTrue(revision_eval.semantic_term_present("每周反馈", "每周向牵头部门反馈办理进展。"))
        self.assertTrue(revision_eval.semantic_term_present("反馈期限", "请于2026年6月10日前反馈相关材料。联系人：办公室。"))
        self.assertTrue(revision_eval.semantic_term_present("授权使用范围", "本次采购授权主要用于文档编辑、协同办公等工作场景。"))

    def test_notice_revision_checks_recipient_and_deleted_content(self) -> None:
        case = next(item for item in revision_eval.CASES if item.id == "R001")
        turn = case.turns[2]
        text = """关于报送季度项目资料的通知

各有关单位：
请报送相关材料。

综合管理部
2026年6月1日"""

        issues = revision_eval.evaluate_turn(text, turn, case)
        labels = {item["label"] for item in issues}

        self.assertIn("recipient_mismatch", labels)
        self.assertIn("sender_mismatch", labels)
        self.assertIn("forbidden_content_retained", labels)

    def test_request_flags_extra_salutation_before_required_title(self) -> None:
        case = next(item for item in revision_eval.CASES if item.id == "R007")
        turn = case.turns[0]
        text = """尊敬的领导：

关于解决政务大厅设备更新经费的请示

市财政局：
拟申请设备更新经费。

妥否，请批示。

区政务服务中心
2026年6月1日"""

        issues = revision_eval.evaluate_turn(text, turn, case)
        labels = {item["label"] for item in issues}

        self.assertIn("title_mismatch", labels)
        self.assertNotIn("forbidden_content_retained", labels)

    def test_request_flags_approval_closing_after_date(self) -> None:
        case = next(item for item in revision_eval.CASES if item.id == "R007")
        turn = case.turns[1]
        text = """关于解决政务大厅设备更新经费的请示

市财政局：
拟申请设备更新经费。

区政务服务中心
2026年6月1日

以上请示，请予审定。"""

        issues = revision_eval.evaluate_turn(text, turn, case)
        labels = {item["label"] for item in issues}

        self.assertIn("closing_position_wrong", labels)

    def test_request_accepts_approval_review_closing(self) -> None:
        case = next(item for item in revision_eval.CASES if item.id == "R007")
        text = """关于解决政务大厅设备更新经费的请示

市财政局：
拟申请设备更新经费。

以上请示，请予审定。

区政务服务中心
2026年6月1日"""

        issues = revision_eval.genre_format_issues(text, case)

        self.assertNotIn("请示缺少请批语", "\n".join(item["detail"] for item in issues))

    def test_application_genre_requires_application_shape(self) -> None:
        case = next(item for item in revision_eval.CASES if item.genre == "申请")
        text = """办公设备购置经费申请

总经理办公会：
现将办公设备购置情况报告如下。

运营管理部
2026年6月1日"""

        issues = revision_eval.genre_format_issues(text, case)
        labels = {item["label"] for item in issues}

        self.assertIn("genre_function_mixed", labels)

    def test_application_accepts_approval_closing_when_before_signature(self) -> None:
        case = next(item for item in revision_eval.CASES if item.id == "R008")
        turn = case.turns[0]
        text = """办公设备购置经费申请

公司领导班子：
拟申请购置打印机、扫描仪和配套耗材。

一、申请事项
申请安排办公设备购置经费18万元。

妥否，请批示。

综合服务中心
2026年6月1日"""

        issues = revision_eval.evaluate_turn(text, turn, case)
        labels = {item["label"] for item in issues}

        self.assertNotIn("missing_required_content", labels)
        self.assertNotIn("closing_position_wrong", labels)

    def test_real_application_split_title_and_salutation_are_valid(self) -> None:
        case = next(item for item in revision_eval.CASES if item.id == "R011")
        turn = case.turns[0]
        text = """示例科技有限公司
软件采购申请

尊敬的领导：
拟采购办公软件会员一年期授权。

本次采购具体情况如下：
办公软件会员一年期授权：6套
单价：198元/套
合计费用：1188元

授权使用范围为文档编辑、排版、协同办公和文件处理岗位。

妥否，请领导批示。

技术应用部
2026年3月13日"""

        genre_issues = revision_eval.genre_format_issues(text, case)
        issues = revision_eval.evaluate_turn(text, turn, case)
        labels = {item["label"] for item in issues}

        self.assertNotIn("申请标题未保留申请文种。", "\n".join(item["detail"] for item in genre_issues))
        self.assertNotIn("title_mismatch", labels)
        self.assertNotIn("closing_position_wrong", labels)


if __name__ == "__main__":
    unittest.main()
