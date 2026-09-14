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
    def test_replaced_mixed_directory_is_absent_from_all_packages(self) -> None:
        roots = [
            ROOT / "chinese-official-writing",
            ROOT / "packages/agent-skills/skills/chinese-official-writing",
            ROOT / "packages/qwen-code/skills/chinese-official-writing",
            ROOT / "packages/hermes/skills/chinese-official-writing",
            ROOT / "packages/openclaw/skills/chinese_official_writing",
        ]
        for root in roots:
            with self.subTest(root=root):
                self.assertFalse((root / "references/genre-playbooks.md").exists())

    def test_report_leaf_and_unknown_route_are_separate(self) -> None:
        report = PROVIDER._reference_paths_for_genres(
            ["报告"], ["根据给定材料起草一份完整情况报告，只输出正文。"]
        )
        unknown = PROVIDER._reference_paths_for_genres(
            ["备忘"], ["根据给定材料起草一份备忘，只输出正文。"]
        )
        notice = PROVIDER._reference_paths_for_genres(
            ["通知"], ["起草一份会议通知，只输出正文。"]
        )

        self.assertIn("references/genre-playbook-report.md", report)
        self.assertNotIn("references/genre-playbooks.md", report)
        self.assertEqual(
            unknown[1:3],
            ["references/genre-routing.md", "references/genre-checklist.md"],
        )
        self.assertIn("references/genre-playbook-notice.md", notice)
        self.assertNotIn("references/genre-checklist-report.md", notice)

    def test_report_leaf_keeps_fact_and_status_boundaries(self) -> None:
        text = (ROOT / "chinese-official-writing/references/genre-playbook-report.md").read_text(
            encoding="utf-8"
        )
        for phrase in ["报告事项与范围", "报告不写请批语或审批请求", "使用报告、体验报告"]:
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
