from __future__ import annotations

import re
import subprocess
import unittest
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / "chinese-official-writing" / "SKILL.md"
REFS = ROOT / "chinese-official-writing" / "references"
FINAL_REVIEW_PATHS = [
    "references/final-review-layers.md",
    "references/anti-ai-patterns.md",
    "references/prose-lint-usage.md",
    "references/delivery.md",
]


class ReferenceRewriteContractTests(unittest.TestCase):
    def test_spec_and_architecture_are_present(self) -> None:
        spec = (ROOT / "maintenance" / "specs" / "reference-rewrite-20260912.md").read_text(encoding="utf-8")
        architecture = (ROOT / "maintenance" / "docs" / "reference-rewrite-architecture-20260912.md").read_text(encoding="utf-8")
        for text, terms in [
            (spec, ["整体对照重写", "普通脚本", "Pro", "真实写稿验收", "候选独有硬回退"]),
            (architecture, ["五类规则页", "单叶隔离协议", "路由清单", "脚本"]),
        ]:
            for term in terms:
                self.assertIn(term, text)

    def test_all_reference_pages_have_explicit_architecture_mapping(self) -> None:
        mapping = (ROOT / "maintenance" / "docs" / "reference-rewrite-page-map-20260912.md").read_text(encoding="utf-8")
        rows = re.findall(r"^\|\s*\d+\s*\|\s*`([^`]+\.md)`\s*\|.*\|\s*(rewrite|retain|delete)\s*\|", mapping, re.MULTILINE)
        actual = sorted(path.name for path in REFS.glob("*.md"))
        baseline = sorted(
            Path(line).name
            for line in subprocess.check_output(
                ["git", "ls-tree", "-r", "--name-only", "main", "chinese-official-writing/references"],
                text=True,
            ).splitlines()
        )
        self.assertEqual(len(rows), 50)
        self.assertEqual(sorted(name for name, _ in rows), baseline)
        generated = {
            "genre-playbook-notice.md",
            "genre-playbook-publication.md",
            "genre-playbook-bulletin.md",
            "genre-playbook-research.md",
            "genre-playbook-feasibility.md",
            "genre-playbook-procurement-announcement.md",
            "genre-playbook-decision.md",
            "genre-playbook-resolution.md",
            "genre-playbook-motion.md",
            "genre-playbook-communique.md",
            "genre-playbook-order.md",
            "genre-playbook-deployment.md",
            "genre-playbook-reply.md",
            "genre-playbook-opinion.md",
            "genre-playbook-explanation.md",
            "genre-playbook-report.md",
            "transaction-remediation-report.md",
            "transaction-feedback-report.md",
            "delivery.md",
        }
        self.assertEqual(set(actual) - set(baseline), generated)
        self.assertTrue(set(actual) - generated <= set(baseline))
        self.assertEqual(len({name for name, _ in rows}), 50)

    def test_entry_uses_task_and_genre_axes_with_reachable_routes(self) -> None:
        skill = SKILL.read_text(encoding="utf-8")
        for task in ["起草", "整体改写", "局部修改", "压缩", "审核", "格式交付"]:
            self.assertIn(task, skill)
        self.assertRegex(
            skill,
            r"起草、改写、压缩和合稿读取 `references/information-selection\.md`",
        )
        for relative in [
            "references/reference-index.md",
            "references/genre-routing.md",
            "references/information-selection.md",
            "references/task-route-cards.md",
            "references/ai-compute-docs.md",
            *FINAL_REVIEW_PATHS,
        ]:
            self.assertIn(relative, skill)
            self.assertTrue((SKILL.parent / relative).is_file(), relative)

    def test_final_checks_are_numbered_and_delivery_is_last(self) -> None:
        skill = SKILL.read_text(encoding="utf-8")
        final_section = skill[skill.index("## 正文形态"):]
        steps = re.findall(
            r"^### 第([一二三四五])步：([^\n]+)\n(.*?)(?=^### |\Z)",
            final_section,
            re.MULTILINE | re.DOTALL,
        )
        self.assertEqual([number for number, _, _ in steps], list("一二三四五"))
        for (_, _, content), references in zip(steps, [
            ["references/compression-details.md", "scripts/draft_length.py"],
            ["references/final-review-layers.md"],
            ["references/anti-ai-patterns.md", "references/proofreading-checklist.md"],
            ["references/prose-lint-usage.md", "scripts/prose_lint.py"],
            ["references/delivery.md"],
        ]):
            for relative in references:
                self.assertIn(relative, content)
                self.assertTrue((SKILL.parent / relative).is_file(), relative)
        before_steps = final_section[:final_section.index("### 第一步")]
        self.assertNotIn("references/delivery.md", before_steps)
        for scope in ["全文", "局部修改", "关联段落", "审核范围"]:
            self.assertIn(scope, before_steps)

    def test_product_pages_do_not_expose_build_or_maintenance_commands(self) -> None:
        texts = [SKILL.read_text(encoding="utf-8")]
        texts.extend(path.read_text(encoding="utf-8") for path in REFS.glob("*.md"))
        joined = "\n".join(texts).lower()
        for operational in [
            "git commit",
            "git push",
            "pytest",
            "python -m unittest",
            "worktree",
            "maintenance/",
            "开发命令",
            "构建命令",
        ]:
            self.assertNotIn(operational.lower(), joined, operational)
        for retired_route in ["hooks/", "review_gate.py", "delivery-review-gate.md"]:
            self.assertNotIn(retired_route, joined)

    def test_compute_rules_are_one_scenario_overlay(self) -> None:
        text = (REFS / "ai-compute-docs.md").read_text(encoding="utf-8")
        for term in ["主文种", "业务场景", "Token", "TOPS/TFLOPS", "实际数据", "估算数据", "建议值", "待核", "成本", "SLA", "安全", "验收"]:
            self.assertIn(term, text)
        for boundary in ["服务期限", "成本口径", "风险假设", "权限", "数据类型", "拟议"]:
            self.assertIn(boundary, text)
        for unrelated_route in [
            "ai-compute-feasibility.md", "ai-compute-procurement.md", "ai-compute-technical-requirements.md",
            "genre-routing.md", "genre-checklist-feasibility-review.md",
        ]:
            self.assertNotIn(unrelated_route, text)
        self.assertNotRegex(text, r"\|\s*主交付对象\s*\|")
        self.assertNotRegex(text, r"`(?:references/)?genre-playbook-[^`]+\.md`")
        links = re.findall(r"`(?:references/)?([^`/]+\.md)`", text)
        self.assertEqual(links, ["technical-terms.md", "ai-compute-examples.md"])
        self.assertRegex(text, r"需要统一英文术语.*technical-terms\.md")
        self.assertRegex(text, r"用户要求参考段落示例.*ai-compute-examples\.md")

    def test_decision_family_keeps_separate_genre_authority_and_state(self) -> None:
        expected = {
            "genre-playbook-decision.md": ["主体", "权限", "决定对象", "执行", "拟议"],
            "genre-playbook-resolution.md": ["会议", "通过", "日期", "审议", "待表决"],
            "genre-playbook-motion.md": ["人民政府", "同级人民代表大会", "提请审议", "附件", "批准结论"],
            "genre-playbook-communique.md": ["发布主体", "公开范围", "各方立场", "共识", "磋商"],
            "genre-playbook-order.md": ["发令主体", "权限", "令号", "施行", "签署人"],
        }
        for name, concepts in expected.items():
            with self.subTest(page=name):
                text = (REFS / name).read_text(encoding="utf-8")
                for concept in concepts:
                    self.assertIn(concept, text)
                self.assertNotRegex(text, r"`(?:references/)?genre-playbook-(?:decision|resolution|motion|communique|order)\.md`")
        self.assertFalse((REFS / "genre-playbook-deliberation.md").exists())
        product = SKILL.read_text(encoding="utf-8") + "\n".join(
            page.read_text(encoding="utf-8") for page in REFS.glob("*.md")
        )
        self.assertNotIn("genre-playbook-deliberation.md", product)

    def test_reference_graph_is_acyclic_and_local(self) -> None:
        link_re = re.compile(r"`(?:references/)?([^`/]+\.md)`")
        graph: dict[str, set[str]] = {}
        for source in REFS.glob("*.md"):
            targets = {
                match.group(1)
                for match in link_re.finditer(source.read_text(encoding="utf-8"))
            }
            for target in targets:
                destination = SKILL if target == "SKILL.md" else REFS / target
                self.assertTrue(destination.is_file(), f"broken reference: {source.name} -> {target}")
            graph[source.name] = {target for target in targets if target != "SKILL.md"}
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

    def test_machine_readable_manifest_closes_current_leaf_set(self) -> None:
        validator_path = ROOT / "maintenance" / "tools" / "validate_reference_manifest.py"
        spec = importlib.util.spec_from_file_location("reference_manifest_validator", validator_path)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.assertEqual(module.validate(), [])

        manifest = __import__("json").loads(
            (ROOT / "maintenance/specs/reference-route-manifest.json").read_text(encoding="utf-8")
        )
        self.assertEqual(len(manifest["pages"]), len(list(REFS.glob("*.md"))))
        link_re = re.compile(r"`(?:references/)?([^`/]+\.md)`")
        for page in manifest["pages"]:
            text = (SKILL.parent / page["path"]).read_text(encoding="utf-8")
            direct_reads = {
                "SKILL.md" if match.group(1) == "SKILL.md" else f"references/{match.group(1)}"
                for match in link_re.finditer(text)
            }
            self.assertEqual(
                set(page["allowed_reads"]),
                {"SKILL.md", page["path"]} | direct_reads,
                page["path"],
            )
        for route in manifest["routes"]:
            self.assertEqual(len(route["primary"]), 1)

    def test_retired_workflow_is_replaced_by_composable_common_pages(self) -> None:
        self.assertFalse((REFS / "workflow.md").exists())
        product = SKILL.read_text(encoding="utf-8") + "\n".join(
            page.read_text(encoding="utf-8") for page in REFS.glob("*.md")
        )
        self.assertNotIn("workflow.md", product)

        skill = SKILL.read_text(encoding="utf-8")
        for replacement in [
            "references/information-selection.md",
            "references/handling-elements.md",
            "references/argument-chains.md",
            "references/structure-editing.md",
            "references/compression-details.md",
        ]:
            self.assertIn(replacement, skill)

        mapping = (ROOT / "maintenance/docs/reference-rewrite-page-map-20260912.md").read_text(
            encoding="utf-8"
        )
        workflow_row = next(
            line for line in mapping.splitlines() if "| 50 | `workflow.md` |" in line
        )
        self.assertIn("| delete |", workflow_row)
        for owner in [
            "SKILL.md",
            "information-selection.md",
            "structure-editing.md",
            "compression-details.md",
            "handling-elements.md",
            "argument-chains.md",
        ]:
            self.assertIn(owner, workflow_row)

    def test_mit_product_keeps_ordinary_scripts_and_moves_hooks_to_pro(self) -> None:
        for relative in ["hooks", "scripts/review_gate.py", "references/delivery-review-gate.md"]:
            self.assertFalse((SKILL.parent / relative).exists(), relative)
        for relative in ["scripts/draft_length.py", "scripts/prose_lint.py"]:
            self.assertTrue((SKILL.parent / relative).is_file(), relative)
        note = ROOT / "maintenance/docs/pro-hooks-next.md"
        self.assertTrue(note.is_file())
        text = note.read_text(encoding="utf-8")
        for asset in ["codex/pro-hooks-preserved-20260912", "v1.6.34", "MIT", "All rights reserved"]:
            self.assertIn(asset, text)

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
        self.assertEqual(module._reference_paths_for_genres(["会议纪要"], ["只记录建议和待评估事项"]), ["SKILL.md", "references/information-selection.md", "references/genre-playbook-minutes.md"] + FINAL_REVIEW_PATHS)

    def test_compute_overlay_requires_scene_signal(self) -> None:
        provider_path = ROOT / "maintenance" / "evals" / "official-writing" / "providers" / "agent_writer.py"
        spec = importlib.util.spec_from_file_location("rewrite_agent_writer_signal", provider_path)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        ordinary = module._reference_paths_for_genres(["采购公告"], ["核对安全、SLA和验收条款"])
        self.assertNotIn("references/ai-compute-docs.md", ordinary)
        compute = module._reference_paths_for_genres(["报告"], ["起草GPU模型推理服务试用报告，写明并发和验收"])
        self.assertIn("references/genre-playbook-report.md", compute)
        self.assertIn("references/ai-compute-docs.md", compute)

    def test_formulaic_reference_is_a_capability_page(self) -> None:
        text = (REFS / "formulaic-language.md").read_text(encoding="utf-8")
        self.assertIn("本页不替代文种路由", text)
        self.assertIn("历史模板", text)
        self.assertNotIn("20类事务文体", text)
        self.assertLess(len(text), 4000)

    def test_short_draft_retains_natural_paragraph_compression(self) -> None:
        text = (REFS / "short-draft-naturalness.md").read_text(encoding="utf-8")
        for term in ["章节、小标题和分项", "自然段", "一两句话", "不保留无信息增量"]:
            self.assertIn(term, text)

    def test_light_task_routes_have_independent_short_and_local_conditions(self) -> None:
        text = (REFS / "task-route-cards.md").read_text(encoding="utf-8")
        choices = re.findall(r"^- (.+)$", text, re.MULTILINE)
        self.assertEqual(len(choices), 2)
        self.assertRegex(choices[0], r"简短.*或.*材料较少")
        self.assertIn("主文种", choices[0])
        self.assertIn("short-draft-naturalness.md", choices[0])
        self.assertIn("只改", choices[1])
        self.assertIn("structure-editing.md", choices[1])
        self.assertIn("field-editing.md", choices[1])
        self.assertIn("分别成立", text)
        self.assertIn("检查步骤", text)
        self.assertIn("本轮范围", text)
        self.assertNotIn("一两句话", text)
        self.assertNotIn("章节、小标题和分项", text)

    def test_anti_ai_reference_retains_semantic_risk_families(self) -> None:
        text = (REFS / "anti-ai-patterns.md").read_text(encoding="utf-8")
        for term in ["连续否定", "采购正在推进", "资金充分性", "非正文", "结构化草稿腔", "句群节奏", "思考泄露", "算力", "格式"]:
            self.assertIn(term, text)
        self.assertIn("质量建议层", text)

    def test_argument_reference_handles_evidence_and_paragraph_relations(self) -> None:
        text = (REFS / "argument-chains.md").read_text(encoding="utf-8")
        for term in ["判断", "事实", "条件", "原因", "影响", "预测", "建议", "表述强度", "必要性", "措施", "实测", "测算", "估算", "假设", "待核"]:
            self.assertIn(term, text)
        for old_mixed_genres in ["请示、申请", "报告、总结", "通知、函、复函", "方案、实施方案", "可研、调研", "讲话、致辞"]:
            self.assertNotIn(old_mixed_genres, text)
        self.assertNotRegex(text, r"`(?:references/)?genre-playbook-[^`]+\.md`")

    def test_genre_chains_remain_in_their_primary_pages(self) -> None:
        expected = {
            "genre-playbook-request.md": ["缘由", "事项", "请批", "金额"],
            "genre-playbook-report.md": ["范围", "事实", "进展", "问题", "处置"],
            "genre-playbook-notice.md": ["对象", "事项", "时限", "渠道"],
            "genre-playbook-correspondence.md": ["来文", "商请", "答复", "反馈"],
            "genre-playbook-plan-construction.md": ["目标", "任务", "路径", "进度", "验收"],
            "genre-playbook-feasibility.md": ["需求", "方案比较", "投资", "风险", "条件性"],
            "genre-playbook-research.md": ["对象", "方法", "发现", "原因", "建议"],
            "genre-playbook-speech-address.md": ["场合", "身份", "主题", "事实", "任务"],
        }
        for name, concepts in expected.items():
            with self.subTest(page=name):
                text = (REFS / name).read_text(encoding="utf-8")
                for concept in concepts:
                    self.assertIn(concept, text)
        request = (REFS / "genre-playbook-request.md").read_text(encoding="utf-8")
        self.assertNotRegex(request, r"argument-chains\.md`?\s*的请示部分")

    def test_final_review_preserves_fact_genre_template_and_modification_scope(self) -> None:
        text = (REFS / "final-review-layers.md").read_text(encoding="utf-8")
        items = re.findall(r"^## 第([一二三])项：([^\n]+)$", text, re.MULTILINE)
        self.assertEqual([number for number, _ in items], list("一二三"))
        for (_, title), concepts in zip(items, [("事实", "状态"), ("文种", "结构"), ("模板", "完整性")]):
            for concept in concepts:
                self.assertIn(concept, title)
        for term in ["最新版底稿", "局部修改", "关联段落", "重复", "修改范围", "待核", "附件", "批注", "修订痕迹"]:
            self.assertIn(term, text)
        self.assertNotRegex(text, r"`(?:references/)?genre-playbook-[^`]+\.md`")
        for premature_delivery in ["直接输出完整正文", "复核完成即停止", "delivery.md"]:
            self.assertNotIn(premature_delivery, text)
        index = (REFS / "reference-index.md").read_text(encoding="utf-8")
        self.assertIn("首页第二步事实与文种复核", index)
        self.assertIn("核对事实、状态、文种、结构和文内完整性", index)
        self.assertNotIn("全文交付前综合总审", index)

    def test_review_checklist_covers_full_review_without_excessive_gates(self) -> None:
        text = (REFS / "review-checklist.md").read_text(encoding="utf-8")
        self.assertFalse((REFS / "review-direct-checklist.md").exists())
        self.assertRegex(text, r"默认检查整篇稿件")
        for term in ["事实", "状态", "文种", "结构", "抗 AI 味", "格式", "一致性", "最新版底稿", "关键事实", "可选表达建议"]:
            self.assertIn(term, text)
        for preserved_judgment in ["事实和常识", "条件性结论", "合理建议", "可选补充", "已知主体关系", "不确定性"]:
            self.assertIn(preserved_judgment, text)
        self.assertRegex(text, r"用户要求审核意见.*问题与建议")
        for review_only in ["审核、指出问题、给修改建议", "交付问题位置、依据和建议改法"]:
            self.assertIn(review_only, text)
        for revised_draft in ["审核后修改、复核后修改、优化稿件", "交付修改后的全文"]:
            self.assertIn(revised_draft, text)
        self.assertIn("有充分依据的问题直接改入正文", text)
        delivery = (REFS / "delivery.md").read_text(encoding="utf-8")
        for delivery_element in ["完整稿件或审稿意见", "原句或具体位置", "问题表现", "建议改法", "替代表达", "用户限定审核范围"]:
            self.assertIn(delivery_element, delivery)
        self.assertNotRegex(text, r"`(?:references/)?genre-playbook-[^`]+\.md`")
        product = SKILL.read_text(encoding="utf-8") + "\n".join(
            page.read_text(encoding="utf-8") for page in REFS.glob("*.md")
        )
        self.assertNotIn("review-direct-checklist.md", product)

    def test_prose_lint_modes_follow_text_type_and_recheck_script_edits(self) -> None:
        text = (REFS / "prose-lint-usage.md").read_text(encoding="utf-8")
        for text_type, mode in [
            ("审核任务收到的原稿、修改后的稿件", "draft-body"),
            ("稿件正文和独立的文后提示", "gap-note-allowed"),
            ("审稿意见本身", "review-only"),
        ]:
            self.assertRegex(text, rf"{text_type}.*`{mode}`")
        for check in ["事实", "状态", "主体", "否定范围", "文种要素", "复扫变动文本"]:
            self.assertIn(check, text)

    def test_information_and_handling_pages_keep_fact_and_element_boundaries(self) -> None:
        information = (REFS / "information-selection.md").read_text(encoding="utf-8")
        handling = (REFS / "handling-elements.md").read_text(encoding="utf-8")
        for term in ["材料事实", "直接分析", "状态信息", "实质缺项", "时间锚", "合理推断"]:
            self.assertIn(term, information)
        self.assertIn("只有主题、目标、方向或任务名称时", information)
        self.assertIn("主题词可以承接一般方向", information)
        for term in ["主体", "对象", "事项", "依据", "状态", "期限", "金额", "附件", "联系人", "反馈", "落款", "日期", "未提供", "尚未确定", "矛盾"]:
            self.assertIn(term, handling)
        self.assertIn("当前主文种", handling)
        self.assertIn("用户模板", handling)
        links = re.findall(r"`(?:references/)?([^`/]+\.md)`", handling)
        self.assertEqual(links, ["external-research.md", "information-selection.md"])
        self.assertNotRegex(handling, r"\|\s*文种(?:/材料)?\s*\|")
        self.assertNotIn("默认不外搜", handling)
        self.assertIn("具体业务信息仍取自材料", handling)

    def test_style_and_addressing_pages_keep_relation_and_strength_boundaries(self) -> None:
        style = (REFS / "official-style.md").read_text(encoding="utf-8")
        addressing = (REFS / "formal-addressing.md").read_text(encoding="utf-8")
        for term in ["视角", "段落", "证据", "上行文", "下行文", "平行文"]:
            self.assertIn(term, style + addressing)
        self.assertIn("不编造机关名称", addressing)

    def test_speech_page_keeps_sparse_theme_material_at_original_strength(self) -> None:
        text = (REFS / "genre-playbook-speech-address.md").read_text(encoding="utf-8")
        self.assertIn("材料只给主题、工作考虑、下一步方向和未定状态", text)
        self.assertIn("主题词本身不等于已有基础或已经决定的安排", text)

    def test_sparse_plan_can_omit_unprovided_structure_sections(self) -> None:
        text = (REFS / "genre-playbook-plan-construction.md").read_text(encoding="utf-8")
        self.assertIn("未提供保障、风险、组织、进度或预算细节时可以省略相应章节", text)
        self.assertIn("可直接按这五类要素收束", text)


if __name__ == "__main__":
    unittest.main()
