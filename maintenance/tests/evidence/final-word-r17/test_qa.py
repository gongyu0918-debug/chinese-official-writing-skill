"""Preparation-only helper checks; never reads the active R17 batch or a DOCX file."""

import importlib.util
from pathlib import Path
import sys
import unittest


sys.dont_write_bytecode = True
path = Path(__file__).with_name("qa.py")
spec = importlib.util.spec_from_file_location("word_r17_qa_helpers", path)
qa = importlib.util.module_from_spec(spec)
spec.loader.exec_module(qa)


class QaHelperTests(unittest.TestCase):
    def test_xml_run_spaces_and_empty_date_are_retained(self):
        xml = ('<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
               '<w:body><w:p><w:r><w:t xml:space="preserve">预算 1800 </w:t></w:r>'
               '<w:r><w:t>元</w:t></w:r></w:p><w:p><w:r><w:t>日期：____年__月__日</w:t>'
               '</w:r></w:p></w:body></w:document>').encode()
        self.assertEqual(qa.paragraphs_from_xml(xml), ["预算 1800 元", "日期：____年__月__日"])

    def test_empty_layout_paragraphs_do_not_hide_changed_internal_spaces(self):
        expected = ["标题", "预算 1800 元", "日期：____年__月__日"]
        self.assertTrue(qa.exact_paragraph_check(expected, ["", *expected, ""])['exact'])
        self.assertFalse(qa.exact_paragraph_check(expected, ["标题", "预算1800元", expected[-1]])['exact'])
        self.assertFalse(qa.exact_paragraph_check(expected, ["标题", expected[1], "日期：2026年9月13日"])['exact'])

    def test_tabs_are_text_not_collapsed_spacing(self):
        xml = ('<w:p xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
               '<w:r><w:t>单位</w:t><w:tab/><w:t>教务处</w:t></w:r></w:p>').encode()
        self.assertEqual(qa.paragraphs_from_xml(xml), ["单位\t教务处"])

    def test_nested_textbox_paragraph_is_not_duplicated(self):
        xml = ('<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
               '<w:body><w:p><w:r><w:txbxContent><w:p><w:r><w:t>文字</w:t></w:r></w:p>'
               '</w:txbxContent></w:r></w:p></w:body></w:document>').encode()
        self.assertEqual(qa.nonempty_paragraphs(qa.paragraphs_from_xml(xml)), ["文字"])

    def test_final_link_keeps_debug_file_distinct(self):
        workspace = qa.ROOT / "output/unit-only-runtime/call/workspace"
        allowed = [workspace, workspace.parent / "tmp"]
        documents = [
            {"original": str(workspace / "申请.docx"), "document_id": "docx-001", "docx_sha256": "a"},
            {"original": str(workspace / "test.docx"), "document_id": "docx-002", "docx_sha256": "b"},
        ]
        found = qa.resolve_link("申请.docx", workspace, allowed, documents)
        self.assertTrue(found["resolved"])
        self.assertEqual(found["document_id"], "docx-001")
        self.assertEqual(found["kind"], "workspace-relative")
        self.assertFalse(qa.resolve_link("/abs/path/申请.docx", workspace, allowed, documents)["resolved"])
        self.assertFalse(qa.resolve_link("../../other/workspace/申请.docx", workspace, allowed, documents)["resolved"])

    def test_markdown_angle_paths_and_native_citations_are_extracted(self):
        text = '[Word](</C:/bound/workspace/申请.docx>)\n:codex-file-citation{path="C:/bound/tmp/备用.docx" purpose="output"}'
        targets = qa.final_link_targets(text)
        self.assertIn("/C:/bound/workspace/申请.docx", targets)
        self.assertIn("C:/bound/tmp/备用.docx", targets)

    def test_format_only_uses_all_five_source_paragraphs_without_trimming(self):
        paragraphs = ["购置打印机申请", "学校：", "预算 1800 元。请予批准。", "申请单位：教务处", "日期：____年__月__日"]
        content = {"paragraphs": paragraphs, "other_story_text": {}}
        check = qa.text_checks("scope_word_format_only", "只排版。\n\n" + "\n".join(paragraphs), content, "2026-09-13")
        self.assertTrue(check["format_only"]["exact"])
        self.assertTrue(check["source_has_five_paragraphs"])
        self.assertTrue(check["empty_date_exact"])

    def test_factual_probes_do_not_claim_full_acceptance(self):
        content = {"paragraphs": ["申请", "学校：", "8月20日维修后仍卡纸，申请购置一台打印机，预算1800元。", "教务处", "2026年9月13日"], "other_story_text": {}}
        check = qa.text_checks("scope_word_today", "材料", content, "2026-09-13")
        self.assertTrue(check["anchor_probes"]["budget_1800_mentioned"])
        self.assertTrue(check["anchor_probes"]["repair_date_mentioned"])
        self.assertTrue(check["manual_fact_and_layout_review_required"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
