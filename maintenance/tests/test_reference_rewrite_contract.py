from __future__ import annotations

import re
import subprocess
import unittest
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / "chinese-official-writing" / "SKILL.md"
REFS = ROOT / "chinese-official-writing" / "references"


class ReferenceRewriteContractTests(unittest.TestCase):
    def test_spec_and_architecture_are_present(self) -> None:
        spec = (ROOT / "maintenance" / "specs" / "reference-rewrite-20260912.md").read_text(encoding="utf-8")
        architecture = (ROOT / "maintenance" / "docs" / "reference-rewrite-architecture-20260912.md").read_text(encoding="utf-8")
        for text, terms in [
            (spec, ["整体对照重写", "不重写：", "Hook 目录冻结", "真实写稿验收", "候选独有硬回退"]),
            (architecture, ["两条轴", "四层页", "唯一首叶", "脚本负责可观测检查"]),
        ]:
            for term in terms:
                self.assertIn(term, text)

    def test_entry_uses_mode_and_genre_axes(self) -> None:
        skill = SKILL.read_text(encoding="utf-8")
        for term in [
            "交付模式",
            "文种首叶",
            "information-selection.md",
            "task-route-cards.md",
            "ai-compute-docs.md",
            "prose-lint-usage.md",
            "Hook 仅在用户明确要求交付门禁时启用",
        ]:
            self.assertIn(term, skill)

    def test_compute_rules_are_one_scenario_overlay(self) -> None:
        dispatch = (REFS / "ai-compute-docs.md").read_text(encoding="utf-8")
        for term in ["不是文种页", "叠加", "主文种", "业务场景", "SLA", "验收"]:
            self.assertIn(term, dispatch)
        self.assertNotIn("ai-compute-feasibility.md", dispatch)
        self.assertNotIn("ai-compute-procurement.md", dispatch)
        self.assertNotIn("ai-compute-technical-requirements.md", dispatch)

    def test_reference_graph_is_acyclic_and_local(self) -> None:
        link_re = re.compile(r"`(?:references/)?([^`/]+\.md)`")
        graph: dict[str, set[str]] = {}
        for source in REFS.glob("*.md"):
            graph[source.name] = {
                match.group(1)
                for match in link_re.finditer(source.read_text(encoding="utf-8"))
                if (REFS / match.group(1)).is_file()
            }
        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(node: str) -> None:
            if node in visiting:
                self.fail(f"reference cycle at {node}")
            if node in visited:
                return
            visiting.add(node)
            for target in graph.get(node, set()):
                visit(target)
            visiting.remove(node)
            visited.add(node)

        for node in graph:
            visit(node)

    def test_hook_tree_is_unchanged_from_main(self) -> None:
        result = subprocess.run(
            ["git", "diff", "--quiet", "main", "--", "chinese-official-writing/hooks"],
            cwd=ROOT,
            check=False,
        )
        self.assertEqual(result.returncode, 0)

    def test_mirror_contains_rewritten_overlay(self) -> None:
        mirror = ROOT / "packages" / "agent-skills" / "skills" / "chinese-official-writing" / "references"
        for name in ["reference-index.md", "task-route-cards.md", "ai-compute-docs.md"]:
            self.assertEqual((REFS / name).read_bytes(), (mirror / name).read_bytes(), name)

    def test_eval_router_uses_compute_overlay_and_minutes_leaf(self) -> None:
        provider_path = ROOT / "maintenance" / "evals" / "official-writing" / "providers" / "agent_writer.py"
        spec = importlib.util.spec_from_file_location("rewrite_agent_writer", provider_path)
        self.assertIsNotNone(spec)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        for genre, task in [("报告", "写 AI 算力报告，比较云端和租赁成本"), ("采购方案", "写 GPU 采购预算和服务范围"), ("技术需求", "写 AI GPU 技术需求、SLA、接口和验收")]:
            self.assertIn("references/ai-compute-docs.md", module._reference_paths_for_genres([genre], [task]))
        self.assertEqual(module._reference_paths_for_genres(["会议纪要"], ["只记录建议和待评估事项"]), ["SKILL.md", "references/genre-playbook-minutes.md"])

    def test_compute_overlay_requires_scene_signal(self) -> None:
        provider_path = ROOT / "maintenance" / "evals" / "official-writing" / "providers" / "agent_writer.py"
        spec = importlib.util.spec_from_file_location("rewrite_agent_writer_signal", provider_path)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        ordinary = module._reference_paths_for_genres(["采购公告"], ["核对安全、SLA和验收条款"])
        self.assertNotIn("references/ai-compute-docs.md", ordinary)
        compute = module._reference_paths_for_genres(["报告"], ["起草GPU模型推理服务试用报告，写明并发和验收"])
        self.assertIn("references/genre-checklist-report.md", compute)
        self.assertIn("references/ai-compute-docs.md", compute)

    def test_formulaic_reference_is_a_capability_page(self) -> None:
        text = (REFS / "formulaic-language.md").read_text(encoding="utf-8")
        self.assertIn("本页不替代文种路由", text)
        self.assertIn("历史模板", text)
        self.assertNotIn("20类事务文体", text)
        self.assertLess(len(text), 4000)


if __name__ == "__main__":
    unittest.main()
