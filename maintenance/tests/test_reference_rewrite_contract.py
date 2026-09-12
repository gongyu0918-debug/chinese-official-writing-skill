from __future__ import annotations

import re
import subprocess
import unittest
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

    def test_compute_dispatch_has_three_atomic_leaves(self) -> None:
        dispatch = (REFS / "ai-compute-docs.md").read_text(encoding="utf-8")
        for name in ["ai-compute-feasibility.md", "ai-compute-procurement.md", "ai-compute-technical-requirements.md"]:
            self.assertIn(name, dispatch)
            self.assertTrue((REFS / name).is_file())
        self.assertNotIn("### 算力服务可研报告", dispatch)
        self.assertNotIn("### 算力资源采购或租赁方案", dispatch)
        self.assertNotIn("### GPU/服务器租赁技术需求", dispatch)

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

    def test_mirror_contains_new_compute_leaves(self) -> None:
        mirror = ROOT / "packages" / "agent-skills" / "skills" / "chinese-official-writing" / "references"
        for name in ["reference-index.md", "task-route-cards.md", "ai-compute-feasibility.md", "ai-compute-procurement.md", "ai-compute-technical-requirements.md"]:
            self.assertEqual((REFS / name).read_bytes(), (mirror / name).read_bytes(), name)


if __name__ == "__main__":
    unittest.main()
