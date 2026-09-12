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
        self.assertIn("最终消息直接承载标题或正文首句", skill)
        self.assertIn("交付模式本身不回显已读页、参考路径、路由说明", skill)
        self.assertIn("采用正文交付模式", skill)

    def test_compute_rules_are_one_scenario_overlay(self) -> None:
        dispatch = (REFS / "ai-compute-docs.md").read_text(encoding="utf-8")
        for term in ["不是文种页", "叠加", "主文种", "业务场景", "Token", "成本", "SLA", "安全", "验收"]:
            self.assertIn(term, dispatch)
        self.assertNotIn("ai-compute-feasibility.md", dispatch)
        self.assertNotIn("ai-compute-procurement.md", dispatch)
        self.assertNotIn("ai-compute-technical-requirements.md", dispatch)
        self.assertIn("同一稿件同时出现可研、采购和技术需求时", dispatch)
        self.assertIn("实际数据、估算数据、建议值和待核字段分开", dispatch)

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

    def test_anti_ai_reference_retains_semantic_risk_families(self) -> None:
        text = (REFS / "anti-ai-patterns.md").read_text(encoding="utf-8")
        for term in ["连续否定", "采购正在推进", "资金充分性", "非正文", "结构化草稿腔", "句群节奏", "思考泄露", "算力", "格式"]:
            self.assertIn(term, text)
        self.assertIn("质量建议层", text)

    def test_argument_reference_retains_genre_chain_semantics(self) -> None:
        text = (REFS / "argument-chains.md").read_text(encoding="utf-8")
        for term in ["请示、申请", "报告、总结", "通知、函、复函", "方案、实施方案", "可研、调研", "AI 算力", "讲话、致辞"]:
            self.assertIn(term, text)
        self.assertIn("不替代算力附加页", text)

    def test_final_review_reference_retains_three_layers_and_stop(self) -> None:
        text = (REFS / "final-review-layers.md").read_text(encoding="utf-8")
        for term in ["第一层：硬边界", "第二层：稿内质量", "第三层：场景交付", "多轮修改", "重复", "脚本只提示风险", "复核完成即停止"]:
            self.assertIn(term, text)

    def test_review_checklist_retains_scope_specific_checks(self) -> None:
        text = (REFS / "review-checklist.md").read_text(encoding="utf-8")
        for term in ["定稿前高风险", "段落复核", "小节复核", "全文复核", "长文压缩", "联网只在", "AI 算力材料", "独立复核"]:
            self.assertIn(term, text)

    def test_information_and_handling_pages_keep_fact_and_element_boundaries(self) -> None:
        information = (REFS / "information-selection.md").read_text(encoding="utf-8")
        handling = (REFS / "handling-elements.md").read_text(encoding="utf-8")
        for term in ["材料事实", "直接分析", "状态信息", "实质缺项", "时间锚", "合理推断"]:
            self.assertIn(term, information)
        for term in ["通用要素", "文种重点", "算力和技术服务", "不编造真实单位", "停止本页"]:
            self.assertIn(term, handling)

    def test_style_and_addressing_pages_keep_relation_and_strength_boundaries(self) -> None:
        style = (REFS / "official-style.md").read_text(encoding="utf-8")
        addressing = (REFS / "formal-addressing.md").read_text(encoding="utf-8")
        for term in ["主体视角", "段落", "证据", "上行文", "下行文", "平行文"]:
            self.assertIn(term, style + addressing)
        self.assertIn("不编造机关名称", addressing)


if __name__ == "__main__":
    unittest.main()
