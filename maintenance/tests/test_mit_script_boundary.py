from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[2]
SKILL_ROOT = ROOT / "chinese-official-writing"
SCRIPT_NAMES = ("draft_length.py", "prose_lint.py")
REMOVED_GATE_PATHS = (
    "hooks",
    "scripts/review_gate.py",
    "references/delivery-review-gate.md",
)


class MitScriptBoundaryTests(unittest.TestCase):
    def test_plain_skill_packages_remain_hook_free_and_keep_scripts(self) -> None:
        surfaces = (
            SKILL_ROOT,
            ROOT / "packages/agent-skills/skills/chinese-official-writing",
            ROOT / "packages/qwen-code/skills/chinese-official-writing",
            ROOT / "packages/qwenwork/skills/chinese-official-writing",
            ROOT / "packages/hermes/skills/chinese-official-writing",
            ROOT / "packages/openclaw/skills/chinese_official_writing",
        )
        for surface in surfaces:
            with self.subTest(surface=surface):
                for relative in REMOVED_GATE_PATHS:
                    self.assertFalse((surface / relative).exists(), relative)
                for script in SCRIPT_NAMES:
                    self.assertTrue((surface / "scripts" / script).is_file(), script)
                self.assertNotIn(
                    "hooks/README.md", (surface / "SKILL.md").read_text(encoding="utf-8")
                )

    def test_drafting_instructions_keep_fact_selection_without_gate_commands(self) -> None:
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        information = (SKILL_ROOT / "references/information-selection.md").read_text(
            encoding="utf-8"
        )
        for instruction in (
            "当前宿主具备命令执行能力且门禁脚本可用时",
            "执行一次写后只标记复看",
            "把两份文本交给 `references/delivery-review-gate.md`",
            "把 `emit` 标准输出逐字作为本轮整条最终回复",
            "⟦OWG-DROP⟧",
            "scripts/review_gate.py",
            "先建立含原始请求、用户材料和 D0 的一次性事务",
            "最多提交一个局部补丁包",
        ):
            self.assertNotIn(instruction, skill)
            self.assertNotIn(instruction, information)
        entry = skill.split("## 入口契约", 1)[1].split("## 路由主线", 1)[0]
        for action in ("用户需求", "起草", "改写", "审核", "格式处理"):
            self.assertIn(action, entry)
        self.assertLess(entry.index("用户需求"), entry.index("references/reference-index.md"))
        self.assertIn("不影响文种功能或办理落地的外围事项，直接省略", information)
        self.assertIn("正文已经承载的状态不在同句、相邻句或文后换词重复", information)

    def test_length_check_precedes_review_and_lint_scan(self) -> None:
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        routes = (
            "scripts/draft_length.py",
            "references/final-review-layers.md",
            "scripts/prose_lint.py",
            "references/delivery.md",
        )
        for route in routes:
            self.assertIn(route, skill)
        positions = [skill.index(route) for route in routes]
        self.assertEqual(positions, sorted(positions))

    def test_plain_script_clis_run_without_hooks(self) -> None:
        for script in SCRIPT_NAMES:
            with self.subTest(script=script):
                completed = subprocess.run(
                    [sys.executable, "-B", str(SKILL_ROOT / "scripts" / script), "--help"],
                    cwd=ROOT,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    timeout=30,
                )
                self.assertEqual(completed.returncode, 0, completed.stderr)
                if script == "prose_lint.py":
                    options = ("--json", "--format", "--structure", "--strict")
                    for length_option in ("--min-chars", "--max-chars", "--count-mode"):
                        self.assertNotIn(length_option, completed.stdout)
                else:
                    options = ("--min-chars", "--max-chars", "--count-mode", "--json")
                for option in options:
                    self.assertIn(option, completed.stdout)


if __name__ == "__main__":
    unittest.main()
