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


real_prompt_eval = load_module("real_prompt_ablation_under_test", ROOT / "tools" / "run_real_prompt_ablation.py")


class RealPromptAblationTests(unittest.TestCase):
    def test_cases_cover_create_and_revision_prompts(self) -> None:
        kinds = {case.kind for case in real_prompt_eval.CASES}
        prompts = "\n".join(case.prompt for case in real_prompt_eval.CASES)

        self.assertEqual(kinds, {"create", "revise"})
        self.assertIn("帮我起草", prompts)
        self.assertIn("写一份采购公告", prompts)
        self.assertIn("请把这段顺成正式报告", prompts)
        self.assertIn("审一下这段能不能进正文", prompts)
        self.assertIn("不要新增小标题", prompts)
        self.assertIn("不要加接收方", prompts)
        self.assertIn("内部 WPS 会员采购申请", prompts)
        self.assertIn("不写主送机关", prompts)
        self.assertIn("不要改成请示", prompts)
        self.assertIn("包在代码块", prompts)
        self.assertIn("维护期限为XXXX年", prompts)

    def test_current_skill_passes_real_prompt_cases(self) -> None:
        rows = real_prompt_eval.evaluate_root(ROOT, "current_test")
        failures = {row["id"]: row["failures"] for row in rows if not row["passed"]}

        self.assertEqual(failures, {})

    def test_case_set_includes_recent_review_regressions(self) -> None:
        checks_by_id = {case.id: case.checks for case in real_prompt_eval.CASES}

        self.assertIn("采购公告", checks_by_id["P002"]["description_terms"])
        self.assertIn("征求意见函", checks_by_id["P001"]["checklist_sections"])
        self.assertIn("公示", checks_by_id["P003"]["handling_rows"])
        self.assertIn("thought-leak", checks_by_id["P007"]["lint_present_labels"])
        self.assertIn("viewpoint-risk", checks_by_id["P006"]["lint_absent_labels"])
        self.assertIn("改稿前小标题清单", checks_by_id["P009"]["review_checklist_terms"])
        self.assertIn("说明", checks_by_id["P010"]["description_terms"])
        self.assertIn("申请", checks_by_id["P011"]["description_terms"])
        self.assertIn("chinese-official-writing/references/final-review-layers.md", checks_by_id["P012"]["file_terms"])
        self.assertIn("chinese-official-writing/references/formal-addressing.md", checks_by_id["P013"]["file_terms"])
        self.assertIn("unfinished-placeholder", checks_by_id["P014"]["lint_present_labels"])
        self.assertIn("unfinished-placeholder", checks_by_id["P015"]["lint_present_labels"])

    def test_heading_lock_detects_added_subheading(self) -> None:
        before = """一、整改进展
二、存在问题
三、原因分析
四、下一步安排"""
        after = """一、整改进展
二、存在问题
三、原因分析
四、数据口径影响
五、下一步安排"""

        self.assertNotEqual(real_prompt_eval.numbered_headings(before), real_prompt_eval.numbered_headings(after))

    def test_heading_lock_reads_markdown_numbered_headings(self) -> None:
        markdown = """### 一、整改进展
### 二、存在问题
### 三、原因分析
### 四、下一步安排"""

        self.assertEqual(
            real_prompt_eval.numbered_headings(markdown),
            ["一、整改进展", "二、存在问题", "三、原因分析", "四、下一步安排"],
        )


if __name__ == "__main__":
    unittest.main()
