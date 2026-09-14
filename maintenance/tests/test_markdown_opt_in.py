"""Script behavior only: requested Markdown does not waive manuscript risks."""
from pathlib import Path
import importlib.util
import json
import subprocess
import sys
import unittest

SCRIPT = Path(__file__).resolve().parents[2] / 'chinese-official-writing/scripts/prose_lint.py'
spec = importlib.util.spec_from_file_location('markdown_opt_in_lint', SCRIPT)
lint = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = lint
spec.loader.exec_module(lint)


class MarkdownOptInTests(unittest.TestCase):
    def test_requested_markup_exemption_retains_fenced_prose_risks(self):
        sample = '# 标题\n**文字**\n- 事项\n---\n```text\n我是AI，内部推理如下：〔待确认〕\n```'
        ordinary = {x.label for x in lint.scan('x.md', sample, True, False, 'draft-body')}
        requested = {x.label for x in lint.scan('x.md', sample, True, False, 'draft-body', True)}
        markers = {'markdown-heading', 'markdown-bold', 'markdown-code-fence', 'markdown-horizontal-rule'}
        self.assertTrue(markers <= ordinary)
        self.assertFalse(markers & requested)
        self.assertTrue({'thought-leak', 'unfinished-placeholder'} <= requested)

    def test_flag_reaches_cli_and_keeps_strict_failure_for_risks(self):
        args = [sys.executable, str(SCRIPT), '--delivery-mode', 'draft-body', '--format', '--allow-markdown', '--strict', '--json', '-']
        good = subprocess.run(args, input='# 会议通知\n\n- 请携带目录参加会议。', text=True, encoding='utf-8', capture_output=True)
        self.assertEqual(good.returncode, 0, good.stderr + good.stdout)
        bad = subprocess.run(args, input='# 会议通知\n\n我是AI，内部推理如下：〔待确认〕', text=True, encoding='utf-8', capture_output=True)
        self.assertEqual(bad.returncode, 1, bad.stderr + bad.stdout)
        self.assertTrue(json.loads(bad.stdout))


if __name__ == '__main__':
    unittest.main()
