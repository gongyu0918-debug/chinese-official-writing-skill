from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[2]


def load_provider():
    path = ROOT / "maintenance" / "evals" / "official-writing" / "providers" / "agent_writer.py"
    spec = importlib.util.spec_from_file_location("report_relief_agent_writer", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


PROVIDER = load_provider()


class ReportGenericBlockReliefTests(unittest.TestCase):
    def test_generic_playbook_drops_only_the_out_of_scope_report_block(self) -> None:
        relative = Path("references/genre-playbooks.md")
        roots = [
            ROOT / "chinese-official-writing",
            ROOT / "packages/agent-skills/skills/chinese-official-writing",
            ROOT / "packages/qwen-code/skills/chinese-official-writing",
            ROOT / "packages/hermes/skills/chinese-official-writing",
        ]
        canonical = (roots[0] / relative).read_bytes()
        for root in roots:
            with self.subTest(root=root):
                data = (root / relative).read_bytes()
                self.assertEqual(data, canonical)
                text = data.decode("utf-8")
                self.assertNotIn("## 报告/情况说明", text)
                self.assertNotIn("- 报告/情况说明", text)
                self.assertIn("## 函/复函/征求意见函", text)
                self.assertIn("## 通知/通告/公告/公示/通报", text)

    def test_direct_report_leaf_keeps_the_complete_report_contract(self) -> None:
        relative = Path("references/genre-checklist-report.md")
        roots = [
            ROOT / "chinese-official-writing",
            ROOT / "packages/agent-skills/skills/chinese-official-writing",
            ROOT / "packages/qwen-code/skills/chinese-official-writing",
            ROOT / "packages/hermes/skills/chinese-official-writing",
        ]
        canonical = (roots[0] / relative).read_bytes()
        for root in roots:
            with self.subTest(root=root):
                data = (root / relative).read_bytes()
                self.assertEqual(data, canonical)
                text = data.decode("utf-8")
                for phrase in [
                    "## 报告/情况说明",
                    "报告事项和范围",
                    "使用/体验/评估报告或成本考察",
                    "报告不写审批请求",
                    "材料只说接口、系统、页面异常时",
                    "补充读取",
                ]:
                    self.assertIn(phrase, text)

    def test_report_and_generic_routes_remain_separate(self) -> None:
        report = PROVIDER._reference_paths_for_genres(
            ["报告"], ["根据给定材料起草一份完整情况报告，只输出正文。"]
        )
        situation = PROVIDER._reference_paths_for_genres(
            ["情况说明"], ["根据给定材料起草一份常规情况说明，只输出正文。"]
        )
        notice = PROVIDER._reference_paths_for_genres(
            ["通知"], ["起草一份会议通知，只输出正文。"]
        )

        for refs in [report, situation]:
            self.assertIn("references/genre-checklist-report.md", refs)
            self.assertNotIn("references/genre-playbooks.md", refs)
        self.assertIn("references/genre-playbooks.md", notice)
        self.assertNotIn("references/genre-checklist-report.md", notice)


if __name__ == "__main__":
    unittest.main()
