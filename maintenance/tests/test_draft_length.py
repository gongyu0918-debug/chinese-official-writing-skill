from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "chinese-official-writing/scripts"
WORD_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


def xml_part(root: str, text: str) -> str:
    content = f"<w:p><w:r><w:t>{text}</w:t></w:r></w:p>"
    if root == "document":
        content = f"<w:body>{content}</w:body>"
    return f'<w:{root} xmlns:w="{WORD_NS}">{content}</w:{root}>'


def write_docx(path: Path, document_xml: str, **extra_parts: str) -> None:
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("word/document.xml", document_xml)
        for name, content in extra_parts.items():
            archive.writestr(f"word/{name.replace('_', '.')}.xml", content)


class DraftLengthTests(unittest.TestCase):
    def run_count(self, *args: str, text: str | None = None):
        return subprocess.run([sys.executable, str(SCRIPTS / "draft_length.py"), *args], input=text, text=True, encoding="utf-8", capture_output=True)

    def test_count_conventions_and_postscript_exclusion(self):
        for mode, count in (("nonspace", 9), ("cjk", 4)):
            with self.subTest(mode=mode):
                result = self.run_count("--json", "--count-mode", mode, "-", text="测试 A12，完成。\n\n文后提示\n日期待核对。")
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(json.loads(result.stdout)[0]["count"], count)

    def test_numbered_business_chapters_are_counted_before_postscript(self):
        text = (
            "一、进展\n已完成核对。\n\n二、风险提醒\n预算仍为XXXX万元。"
            "\n\n三、补充信息\n联系地址待确认。\n\n文后提示\n主送对象待确认。"
        )
        for mode, expected in (("nonspace", 41), ("cjk", 31)):
            with self.subTest(mode=mode):
                result = self.run_count("--json", "--count-mode", mode, "--max-chars", str(expected - 1), "-", text=text)
                self.assertEqual(result.returncode, 0, result.stderr)
                report = json.loads(result.stdout)[0]
                self.assertEqual(report["count"], expected)
                self.assertEqual(report["status"], "above")
                self.assertEqual(report["above_by"], 1)

    def test_generic_note_words_and_business_names_are_counted(self):
        for heading in (
            "风险提醒", "二、风险提醒", "补充信息", "三、补充信息",
            "待确认事项", "二、待确认事项", "文后提示模块", "一、文后提示功能",
            "文后提示（后台模块）", "待确认事项（正文外管理模块）",
        ):
            text = f"已核对。\n\n{heading}\n预算待确认。"
            with self.subTest(heading=heading):
                result = self.run_count("--json", "-", text=text)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(json.loads(result.stdout)[0]["count"], sum(not char.isspace() for char in text))

    def test_standard_and_explicit_legacy_note_titles_are_excluded(self):
        for heading in (
            "文后提示", "二、文后提示", "2. 文后提示", "正文外提示",
            "待确认事项（正文外）", "（正文外提示）", "影响正式报送的待确认事项", "待用户确认事项",
        ):
            with self.subTest(heading=heading):
                result = self.run_count("--json", "-", text=f"已核对。\n\n{heading}\n预算待确认。")
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(json.loads(result.stdout)[0]["count"], 4)

    def test_markdown_postscript_is_excluded_but_business_modules_are_counted(self):
        for heading in ("**文后提示**", "*文后提示*", "__文后提示__", "_文后提示_", "## 文后提示", "## **文后提示**"):
            with self.subTest(heading=heading):
                result = self.run_count("--json", "-", text=f"已核对。\n\n{heading}\n主送对象待确认。")
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(json.loads(result.stdout)[0]["count"], 4)
        for heading in ("**文后提示模块**", "## 文后提示模块", "**风险提醒**", "*补充信息*"):
            text = f"已核对。\n\n{heading}\n主送对象待确认。"
            with self.subTest(heading=heading):
                result = self.run_count("--json", "-", text=text)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(json.loads(result.stdout)[0]["count"], sum(not char.isspace() for char in text))

    def test_length_bounds_are_per_draft_and_do_not_block_delivery(self):
        for low, high, status, delta in ((5, 8, "below", 1), (0, 3, "above", 1), (4, 4, "within", 0)):
            result = self.run_count("--json", "--min-chars", str(low), "--max-chars", str(high), "-", text="核实完成")
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)[0]
            self.assertEqual(report["status"], status)
            self.assertEqual(report["below_by"] + report["above_by"], delta)

    def test_real_txt_md_docx_inputs_and_separate_counts(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            txt = base / "草稿.txt"; txt.write_text("情况说明\n已核对。", encoding="utf-8")
            md = base / "草稿.md"; md.write_text("已核对。\n\n文后提示\n日期待确认。", encoding="utf-8")
            docx = base / "草稿.docx"
            with zipfile.ZipFile(docx, "w") as archive:
                archive.writestr("word/document.xml", '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body><w:p><w:r><w:t>已核对。</w:t></w:r></w:p></w:body></w:document>')
            result = self.run_count("--json", str(txt), str(md), str(docx))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual([item["count"] for item in json.loads(result.stdout)], [8, 4, 4])

    def test_docx_length_uses_only_main_document_while_lint_keeps_all_parts(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            body = "正文六字计数"
            txt = base / "same.txt"
            md = base / "same.md"
            docx = base / "same.docx"
            txt.write_text(body, encoding="utf-8")
            md.write_text(body, encoding="utf-8")
            write_docx(
                docx,
                xml_part("document", body),
                header1=xml_part("hdr", "页眉字"),
                footer1=xml_part("ftr", "作为AI"),
                footnotes=xml_part("footnotes", "脚注不计"),
                endnotes=xml_part("endnotes", "尾注不计"),
                comments=xml_part("comments", "批注不应计入正文长度中啊呀"),
            )

            for mode in ("nonspace", "cjk"):
                with self.subTest(mode=mode):
                    result = self.run_count(
                        "--json", "--count-mode", mode, str(txt), str(md), str(docx)
                    )
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual([item["count"] for item in json.loads(result.stdout)], [6, 6, 6])

            lint = subprocess.run(
                [sys.executable, str(SCRIPTS / "prose_lint.py"), "--json", str(docx)],
                text=True,
                encoding="utf-8",
                capture_output=True,
            )
            self.assertEqual(lint.returncode, 0, lint.stderr)
            self.assertIn("thought-leak", {item["label"] for item in json.loads(lint.stdout)})

    def test_docx_body_table_and_postscript_define_length_scope(self):
        body_and_table = f'''<w:document xmlns:w="{WORD_NS}"><w:body>
<w:p><w:r><w:t>正文六字计数</w:t></w:r></w:p>
<w:tbl><w:tr>
<w:tc><w:p><w:r><w:t>项目</w:t></w:r></w:p></w:tc>
<w:tc><w:p><w:r><w:t>数量</w:t></w:r></w:p></w:tc>
</w:tr><w:tr>
<w:tc><w:p><w:r><w:t>办公椅</w:t></w:r></w:p></w:tc>
<w:tc><w:p><w:r><w:t>4把</w:t></w:r></w:p></w:tc>
</w:tr></w:tbl>'''
        document_without_note = body_and_table + "</w:body></w:document>"
        document_with_note = body_and_table + '''
<w:p><w:r><w:t>文后提示</w:t></w:r></w:p>
<w:p><w:r><w:t>这一段不计入</w:t></w:r></w:p>
</w:body></w:document>'''
        with tempfile.TemporaryDirectory() as directory:
            for name, document in (
                ("table.docx", document_without_note),
                ("table-and-note.docx", document_with_note),
            ):
                docx = Path(directory) / name
                write_docx(
                    docx,
                    document,
                    header1=xml_part("hdr", "文后提示"),
                    comments=xml_part("comments", "文后提示"),
                )
                for mode, expected in (("nonspace", 15), ("cjk", 14)):
                    with self.subTest(name=name, mode=mode):
                        result = self.run_count("--json", "--count-mode", mode, str(docx))
                        self.assertEqual(result.returncode, 0, result.stderr)
                        self.assertEqual(json.loads(result.stdout)[0]["count"], expected)

    def test_bad_docx_inputs_are_technical_errors(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            damaged = base / "damaged.docx"
            damaged.write_bytes(b"not a zip archive")
            missing_main = base / "missing-main.docx"
            with zipfile.ZipFile(missing_main, "w") as archive:
                archive.writestr("word/header1.xml", xml_part("hdr", "只有页眉"))

            for path, message in (
                (damaged, "文件损坏或不是有效 DOCX"),
                (missing_main, "DOCX 缺少主文档内容"),
            ):
                with self.subTest(path=path.name):
                    result = self.run_count("--json", str(path))
                    self.assertEqual(result.returncode, 2)
                    self.assertEqual(json.loads(result.stdout), [])
                    self.assertIn(message, result.stderr)

    def test_invalid_bounds_and_missing_input_are_technical_errors(self):
        for args in (("--min-chars", "-1", "-"), ("--min-chars", "8", "--max-chars", "2", "-")):
            result = self.run_count(*args, text="测试")
            self.assertEqual(result.returncode, 2)
            self.assertEqual(result.stdout, "")
        result = self.run_count("--json", "absent-for-length-test.docx")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stdout), [])

    def test_counting_does_not_run_prose_review(self):
        result = self.run_count("--json", "-", text="以下为正文：作为AI，我将按要求起草。")
        report = json.loads(result.stdout)[0]
        self.assertEqual(result.returncode, 0)
        self.assertEqual(report["status"], "counted")
        self.assertNotIn("findings", report)
        self.assertNotIn("thought-leak", result.stdout)
        lint = subprocess.run([sys.executable, str(SCRIPTS / "prose_lint.py"), "--json", "--delivery-mode", "draft-body", "-"], input="以下为正文：作为AI，我将按要求起草。", text=True, encoding="utf-8", capture_output=True)
        self.assertIsInstance(json.loads(lint.stdout), list)
        self.assertTrue(json.loads(lint.stdout))


if __name__ == "__main__":
    unittest.main()
