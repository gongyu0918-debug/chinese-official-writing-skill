from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "chinese-official-writing/scripts/prose_lint.py"
spec = importlib.util.spec_from_file_location("script_quality_r1_prose_lint", SCRIPT)
if spec is None or spec.loader is None:
    raise RuntimeError(f"cannot import {SCRIPT}")
prose_lint = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = prose_lint
spec.loader.exec_module(prose_lint)


class ScriptQualityR1Tests(unittest.TestCase):
    def scan(self, text: str, **kwargs):
        return prose_lint.scan("<quality-r1>", text, **kwargs)

    def test_note_heading_inside_markdown_fence_does_not_partition_body(self):
        fenced = "正文第一段。\n```text\n文后提示\n代码示例\n```\n正文第二段。"
        source = prose_lint.prepare_scan_source(fenced, "gap-note-allowed")
        self.assertEqual(source.body_only_lines, fenced.splitlines())
        labels = {item.label for item in self.scan(
            fenced,
            include_format=True,
            delivery_mode="gap-note-allowed",
            allow_markdown=True,
        )}
        self.assertNotIn("external-note-boundary", labels)

        with_note = fenced + "\n\n文后提示\n资金来源待确认。"
        source = prose_lint.prepare_scan_source(with_note, "gap-note-allowed")
        self.assertEqual(source.body_only_lines[: len(fenced.splitlines())], fenced.splitlines())
        self.assertEqual(source.body_only_lines[-1], "")
        labels = {item.label for item in self.scan(with_note, delivery_mode="gap-note-allowed")}
        self.assertNotIn("external-note-boundary", labels)
        self.assertNotIn("资金来源待确认。", source.body_only_lines)
        draft_labels = {item.label for item in self.scan(with_note, delivery_mode="draft-body")}
        self.assertIn("unexpected-external-note", draft_labels)

        nested_fence = "正文第一段。\n````text\n文后提示\n```\n正文第二段。\n````\n正文第三段。"
        source = prose_lint.prepare_scan_source(nested_fence, "gap-note-allowed")
        self.assertEqual(source.body_only_lines, nested_fence.splitlines())
        labels = {item.label for item in self.scan(
            nested_fence,
            include_format=True,
            delivery_mode="gap-note-allowed",
            allow_markdown=True,
        )}
        self.assertNotIn("external-note-boundary", labels)

    def test_markdown_plus_and_underscore_styles_are_checked_or_allowed(self):
        text = "__正文标题__\n_重点事项_\n*另一重点*\n+ 事项"
        labels = {item.label for item in self.scan(text, include_format=True, delivery_mode="draft-body")}
        self.assertTrue({"markdown-bold", "markdown-emphasis", "western-bullet"} <= labels)

        identifiers_and_math = "model_name_version\nfile__name__v2\na * b * c"
        labels = {item.label for item in self.scan(
            identifiers_and_math,
            include_format=True,
            delivery_mode="draft-body",
        )}
        self.assertNotIn("markdown-bold", labels)
        self.assertNotIn("markdown-emphasis", labels)

        allowed = {item.label for item in self.scan(
            text,
            include_format=True,
            delivery_mode="draft-body",
            allow_markdown=True,
        )}
        self.assertTrue({"markdown-bold", "markdown-emphasis", "western-bullet"}.isdisjoint(allowed))

    def test_long_attachment_numbering_is_exempt_but_ordinary_numbering_is_not(self):
        attachment = "附件：\n" + "\n".join(f"{index}. 项目{index}" for index in range(1, 9))
        attachment_labels = {
            item.label for item in self.scan(attachment, include_format=True)
        }
        self.assertNotIn("western-bullet", attachment_labels)
        self.assertNotIn("frequent-list-markers", attachment_labels)

        ordinary = "\n".join(f"{index}. 项目{index}" for index in range(1, 9))
        ordinary_labels = {
            item.label for item in self.scan(ordinary, include_format=True)
        }
        self.assertIn("western-bullet", ordinary_labels)
        self.assertIn("frequent-list-markers", ordinary_labels)

    def test_overlapping_fence_placeholder_matches_are_deduplicated(self):
        findings = self.scan(
            "```text\n经费XXXX万元\n```",
            include_format=True,
            delivery_mode="draft-body",
        )
        placeholders = [item for item in findings if item.label == "unfinished-placeholder"]
        self.assertEqual([(item.line, item.match) for item in placeholders], [(2, "XXXX万元")])

    def test_unknown_encoding_is_a_friendly_input_error(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "sample.txt"
            path.write_text("正文。", encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(SCRIPT),
                    "--encoding",
                    "not-a-real-codec",
                    "--json",
                    str(path),
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
            )

        self.assertEqual(result.returncode, 2)
        self.assertIn("ERROR: 不支持的文本编码", result.stderr)
        self.assertNotIn("Traceback", result.stderr + result.stdout)
        self.assertEqual(json.loads(result.stdout), [])


if __name__ == "__main__":
    unittest.main()
