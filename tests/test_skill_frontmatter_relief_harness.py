from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import unittest


HARNESS = Path(__file__).parent / "evidence" / "skill-frontmatter-relief-v1602" / "harness.py"
SPEC = importlib.util.spec_from_file_location("skill_frontmatter_relief_harness", HARNESS)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class SkillFrontmatterReliefHarnessTests(unittest.TestCase):
    def test_plan_has_nine_pairs_and_balanced_orders_to_the_possible_limit(self) -> None:
        plan = MODULE.build_plan()
        self.assertEqual(len(plan), 9)
        self.assertEqual({row["task_id"] for row in plan}, {"N1", "R1", "V1"})
        for provider in MODULE.MODELS:
            self.assertEqual(sum(row["provider"] == provider for row in plan), 3)
        orders = [row["order"] for row in plan]
        self.assertLessEqual(abs(orders.count("AB") - orders.count("BA")), 1)
        self.assertEqual(sum(len(row["arms"]) for row in plan), 18)

    def test_trace_binding_requires_a_real_read_command(self) -> None:
        path = Path(r"F:\frozen\chinese-official-writing\SKILL.md")
        prompt_only = json.dumps({"type": "message", "text": str(path)})
        self.assertEqual(MODULE.trace_read_binding(prompt_only, path), [])
        trace = json.dumps({"type": "item.completed", "item": {"type": "command_execution", "command": MODULE.read_command(path)}})
        self.assertEqual(MODULE.trace_read_binding(trace, path), [0])

    def test_metadata_leaks_and_review_rewrites_are_hard_failures(self) -> None:
        review = next(task for task in MODULE.TASKS if task.id == "V1")
        findings = MODULE.evaluate_hard(review, "问题位置：第二段\n风险层级：中\n修改建议：补充联系人。\nMIT-0")
        self.assertIn("forbidden:联系人", findings)
        self.assertIn("metadata_leak:MIT-0", findings)
        self.assertIn("review_rewrites_full_text", MODULE.evaluate_hard(review, "问题位置\n风险层级\n修改建议\n关于报送档案整理情况的通知"))


if __name__ == "__main__":
    unittest.main()
