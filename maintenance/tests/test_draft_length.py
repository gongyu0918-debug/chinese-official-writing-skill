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
