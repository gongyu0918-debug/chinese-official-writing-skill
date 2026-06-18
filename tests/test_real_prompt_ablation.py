from __future__ import annotations

import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
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
        self.assertIn("AI生成内容业务", prompts)
        self.assertIn("本报告系AI辅助生成", prompts)
        self.assertIn("### 业务需求与服务保障", prompts)
        self.assertIn("不要补原文没有的事实", prompts)
        self.assertIn("clean corpus", prompts)
        self.assertIn("真实模型", prompts)
        self.assertIn("镜像不能静默分叉", prompts)
        self.assertIn("食品安全专项检查情况报告", prompts)
        self.assertIn("三个人写的年度总结材料", prompts)
        self.assertIn("GB/T 9704 排成 Word", prompts)
        self.assertIn("意义重大、亮点纷呈", prompts)
        self.assertIn("不要默认就高", prompts)
        self.assertIn("正式 Word 红头文件", prompts)
        self.assertIn("只审一下这段格式和语气", prompts)
        self.assertIn("我觉得这个事差不多", prompts)
        self.assertIn("政策依据我没给，也不要外搜", prompts)
        self.assertIn("请核验现行政策依据", prompts)
        self.assertIn("不要自动搜索单位风格", prompts)
        self.assertIn("清理网页元信息", prompts)
        self.assertIn("被印发方案第二部分", prompts)
        self.assertIn("压缩到500字以内", prompts)
        self.assertIn("多个责任主体不要压成笼统的有关单位", prompts)

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
        self.assertIn("thought-leak", checks_by_id["P016"]["lint_absent_labels"])
        self.assertIn("thought-leak", checks_by_id["P017"]["lint_present_labels"])
        self.assertIn("markdown-heading", checks_by_id["P018"]["lint_present_labels"])
        self.assertIn(
            "不新增原文没有交代的活动、依据、数据、成效或责任安排",
            checks_by_id["P019"]["file_terms"]["chinese-official-writing/references/workflow.md"],
        )
        self.assertIn("未新增原文外事实", checks_by_id["P019"]["file_terms"]["chinese-official-writing/SKILL.md"])
        self.assertIn(
            "notice-submit-materials",
            checks_by_id["P020"]["file_terms"]["tests/fixtures/clean_prose_corpus.json"],
        )
        self.assertIn("真实模型小样本评测", checks_by_id["P021"]["file_terms"]["README.md"])
        self.assertIn("THRESHOLD_ENV_VARS", checks_by_id["P021"]["file_terms"]["evals/official-writing/run_eval.py"])
        self.assertIn(
            "test_primary_adapter_mirrors_match_canonical_bytes",
            checks_by_id["P022"]["file_terms"]["tests/test_skill_boundary.py"],
        )
        self.assertIn("任务模式路由", checks_by_id["P023"]["file_terms"]["chinese-official-writing/SKILL.md"])
        self.assertIn("压实合并表达", checks_by_id["P024"]["file_terms"]["chinese-official-writing/references/workflow.md"])
        self.assertIn("Word/排版交付衔接", checks_by_id["P025"]["file_terms"]["chinese-official-writing/references/format-gbt9704.md"])
        self.assertIn("夸大意义", checks_by_id["P026"]["file_terms"]["chinese-official-writing/references/anti-ai-patterns.md"])
        self.assertIn("数据冲突不得默认就高", checks_by_id["P027"]["file_terms"]["chinese-official-writing/references/workflow.md"])
        self.assertIn("正式交付前要素核对", checks_by_id["P028"]["file_terms"]["chinese-official-writing/references/format-gbt9704.md"])
        self.assertIn("不默认重写全文", checks_by_id["P029"]["file_terms"]["chinese-official-writing/SKILL.md"])
        self.assertIn("轻量语气替换建议", checks_by_id["P030"]["file_terms"]["chinese-official-writing/references/official-style.md"])
        self.assertIn("默认不外搜", checks_by_id["P031"]["file_terms"]["chinese-official-writing/SKILL.md"])
        self.assertIn("现行政策", checks_by_id["P032"]["file_terms"]["chinese-official-writing/SKILL.md"])
        self.assertIn("只出现单位名称", checks_by_id["P033"]["file_terms"]["chinese-official-writing/references/workflow.md"])
        self.assertIn("通知壳", checks_by_id["P034"]["file_terms"]["chinese-official-writing/SKILL.md"])
        self.assertIn("被印发文件正文", checks_by_id["P034"]["file_terms"]["chinese-official-writing/references/workflow.md"])
        self.assertIn("不可丢要素", checks_by_id["P035"]["file_terms"]["chinese-official-writing/references/workflow.md"])
        self.assertIn("多主体分工", checks_by_id["P035"]["file_terms"]["chinese-official-writing/references/review-checklist.md"])

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

    def test_heading_lock_reads_bracketed_and_arabic_numbered_headings(self) -> None:
        text = """（一）整改进展
（二）存在问题
1. 原因分析
2、下一步安排
2026年6月30日前反馈材料。"""

        self.assertEqual(
            real_prompt_eval.numbered_headings(text),
            ["（一）整改进展", "（二）存在问题", "1. 原因分析", "2、下一步安排"],
        )

    def test_exit_code_fails_when_current_has_any_failure(self) -> None:
        results = {
            "old": [{"passed": False}, {"passed": False}],
            "current": [{"passed": True}, {"passed": False}],
        }

        self.assertEqual(real_prompt_eval.exit_code_for_results(results, "old"), 1)

    def test_missing_baseline_root_returns_clean_error(self) -> None:
        script = ROOT / "tools" / "run_real_prompt_ablation.py"
        with tempfile.TemporaryDirectory() as temp_dir:
            missing = Path(temp_dir) / "missing-baseline"
            out_dir = Path(temp_dir) / "out"
            result = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "--baseline-root",
                    str(missing),
                    "--current-root",
                    str(ROOT),
                    "--out",
                    str(out_dir),
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
            )

        self.assertEqual(result.returncode, 2)
        self.assertIn("ERROR:", result.stderr)
        self.assertIn("目录不存在", result.stderr)
        self.assertIn("git worktree add", result.stderr)
        self.assertNotIn("Traceback", result.stderr + result.stdout)


if __name__ == "__main__":
    unittest.main()
