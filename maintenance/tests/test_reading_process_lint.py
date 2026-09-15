"""CLI behavior checks for witnessed reading-process narration and close controls."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "chinese-official-writing/scripts/prose_lint.py"
LABEL = "reading-process-narration"


class ReadingProcessLintTests(unittest.TestCase):
    def findings(self, text: str, mode: str = "draft-body") -> list[dict]:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--delivery-mode", mode, "--json", "-"],
            input=text, text=True, encoding="utf-8", capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def test_witnessed_process_only_reply_is_detected(self):
        text = '我需要继续阅读相关的参考文件，特别是关于"议案"文种的规范。'
        for mode in ("draft-body", "gap-note-allowed"):
            with self.subTest(mode=mode):
                self.assertTrue(any(f["label"] == LABEL for f in self.findings(text, mode)))

    def test_entry_reading_variants_are_detected(self):
        for text in (
            "我先读取 SKILL.md，再开始写稿。",
            "让我先阅读该技能说明。",
            "我需要先查看写作规则，然后整理正文。",
        ):
            with self.subTest(text=text):
                self.assertTrue(any(f["label"] == LABEL for f in self.findings(text)))

    def test_business_reading_and_attributed_quotes_are_preserved(self):
        for text in (
            "我将阅读设备检修记录，核对既往故障情况。",
            "培训要求新员工阅读岗位手册后参加考核。",
            '负责人说：“我会继续阅读文种规范，准备下周的培训。”',
            '负责人说：“\n我会继续阅读文种规范，准备下周的培训。\n”',
        ):
            with self.subTest(text=text):
                self.assertFalse(any(f["label"] == LABEL for f in self.findings(text)))

    def test_review_quotes_and_generic_mode_keep_their_scope(self):
        text = '原句：“我需要继续阅读相关的参考文件，特别是关于议案文种的规范。”建议直接交付稿件。'
        self.assertFalse(any(f["label"] == LABEL for f in self.findings(text, "review-only")))
        self.assertFalse(any(f["label"] == LABEL for f in self.findings("我先读取 SKILL.md。", "generic")))


if __name__ == "__main__":
    unittest.main()
