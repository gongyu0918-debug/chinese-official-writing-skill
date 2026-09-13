from __future__ import annotations

import re
import subprocess
import unittest
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / "chinese-official-writing" / "SKILL.md"
REFS = ROOT / "chinese-official-writing" / "references"
REFERENCE_BASELINE = "1ce7112303172478faa2392667a2de1098eb912c"
FINAL_REVIEW_PATHS = [
    "references/writing-rules.md",
    "references/anti-ai-patterns.md",
    "references/prose-lint-usage.md",
]
RETIRED_COMMON_PAGES = {
    "information-selection.md", "final-review-layers.md", "delivery.md",
    "short-draft-naturalness.md", "task-route-cards.md",
    "handling-elements.md", "official-style.md",
}


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
        mapping = (ROOT / "maintenance/docs/reference-rewrite-page-map-20260912.md").read_text(encoding="utf-8")
        rows = re.findall(r"^\|\s*\d+\s*\|\s*`([^`]+\.md)`\s*\|", mapping, re.MULTILINE)
        baseline = {
            Path(line).name
            for line in subprocess.check_output(
                ["git", "ls-tree", "-r", "--name-only", REFERENCE_BASELINE, "chinese-official-writing/references"],
                cwd=ROOT, text=True,
            ).splitlines()
        }
        actual = {path.name for path in REFS.glob("*.md")}
        self.assertEqual(set(rows), baseline)
        self.assertEqual(len(rows), len(baseline))
        active_links = set(re.findall(r"\]\(\.\./\.\./chinese-official-writing/references/([^/)]+\.md)\)", mapping))
        self.assertEqual(active_links, actual)
        new_section = mapping.split("## 新构造页", 1)[1].split("\n## ", 1)[0]
        generated = set(re.findall(r"\]\(\.\./\.\./chinese-official-writing/references/([^/)]+\.md)\)", new_section))
        self.assertEqual(actual - baseline, generated)
        self.assertIn("writing-rules.md", generated)
        self.assertFalse(RETIRED_COMMON_PAGES & active_links)

    def test_entry_uses_task_and_genre_axes_with_reachable_routes(self) -> None:
        skill = SKILL.read_text(encoding="utf-8")
        for task in ["起草", "改写", "局部修改", "压缩", "审核", "格式交付"]:
            self.assertIn(task, skill)
        for relative in ["references/reference-index.md", "references/genre-routing.md", "references/writing-rules.md", "references/ai-compute-docs.md"]:
            self.assertIn(relative, skill)
            self.assertTrue((SKILL.parent / relative).is_file(), relative)
        common = (REFS / "writing-rules.md").read_text(encoding="utf-8")
        for relative in FINAL_REVIEW_PATHS[1:]:
            self.assertIn(Path(relative).name, common)
            self.assertTrue((SKILL.parent / relative).is_file(), relative)
        selection = skill.split("### 第二步：选择文种", 1)[1].split("### 第三步：按任务加读", 1)[0]
        self.assertIn("为每份稿件选定一个主叶", selection)
        self.assertRegex(selection, r"先读 `references/genre-routing\.md` 判定，再选主叶")
        workflow_heading = "## 写作与交付步骤"
        self.assertLess(skill.index("references/reference-index.md"), skill.index(workflow_heading))
        self.assertLess(skill.index("选定主文种后"), skill.index(workflow_heading))
        workflow = skill.split(workflow_heading, 1)[1].split("\n## ", 1)[0]
        self.assertIn("`references/writing-rules.md`", workflow)
        for relative in ["scripts/draft_length.py", "scripts/prose_lint.py", "references/prose-lint-usage.md"]:
            self.assertIn(f"`{relative}`", workflow)
            self.assertTrue((SKILL.parent / relative).is_file(), relative)

    def test_common_flow_keeps_checks_and_delivery_last(self) -> None:
        common = (REFS / "writing-rules.md").read_text(encoding="utf-8")
        sections = re.findall(r"^## ([^\n]+)\n(.*?)(?=^## |\Z)", common, re.MULTILINE | re.DOTALL)
        self.assertEqual([title for title, _ in sections], [
            "第一步：材料与分析", "第二步：成稿与篇幅", "第三步：复核", "第四步：交付",
        ])
        workflow = SKILL.read_text(encoding="utf-8").split("## 写作与交付步骤", 1)[1]
        self.assertEqual(re.findall(r"^\d+\. ([^：\n]+)：", workflow, re.M),
                         [title.split("：", 1)[1] for title, _ in sections])
        length_section = next(body for title, body in sections if "篇幅" in title)
        review_section = next(body for title, body in sections if "复核" in title)
        for relative in ["scripts/draft_length.py", "references/compression-details.md"]:
            self.assertIn(Path(relative).name, length_section)
            self.assertTrue((SKILL.parent / relative).is_file(), relative)
        self.assertRegex(length_section, r"普通完整短稿.*至少\s*80\s*字")
        self.assertRegex(length_section, r"仍不足.*实际差额.*所需材料.*不报达标")
        for name in ["anti-ai-patterns.md", "proofreading-checklist.md", "prose-lint-usage.md"]:
            self.assertIn(name, review_section)
        self.assertRegex(review_section, r"所有成稿、改后稿和审核任务读取 `anti-ai-patterns\.md` 检查语言")
        self.assertLess(review_section.index("anti-ai-patterns.md"), review_section.index("prose-lint-usage.md"))
        for scope in ["全文", "局部", "关联", "本轮"]:
            self.assertIn(scope, review_section)
        delivery = sections[-1][1]
        for concept in ["完整稿件", "审核", "文后提示", "默认", "正文编号", "落款", "附件", "文件交付", "消息", "省略"]:
            self.assertIn(concept, delivery)
        self.assertRegex(delivery, r"正文编号、落款和附件.*提示前结束")
        self.assertRegex(delivery, r"文件交付.*提示留在消息中")
        self.assertRegex(length_section, r"文后提示.*单列")
        compression = (REFS / "compression-details.md").read_text(encoding="utf-8")
        self.assertRegex(compression, r"上下限.*用户要求.*共性写作页.*适用范围")
        self.assertRegex(compression, r"用户只给上限.*保留适用的默认下限")
        self.assertNotIn("只有一侧限制时只传对应参数", compression)

    def test_delivery_examples_keep_review_business_statements_and_usage_notes(self) -> None:
        skill = SKILL.read_text(encoding="utf-8")
        common = (REFS / "writing-rules.md").read_text(encoding="utf-8")
        delivery = common.split("## 第四步：交付", 1)[1]
        examples = re.findall(r"^- “([^”]+)”", delivery, re.M)
        self.assertEqual(len(examples), 2)
        for pattern in [r"读取.*技能.*审核改写", r"非空白字符.*脚本校验.*文稿扫描"]:
            self.assertTrue(any(re.search(pattern, example) for example in examples), pattern)
        for example in examples:
            self.assertNotIn(example, skill)
        self.assertRegex(delivery, r"交付消息从[^。]*稿件[^。]*审核意见[^。]*文件链接[^。]*开始")
        self.assertRegex(delivery, r"开头、文后提示或结束语[^。]*同样要删除")
        self.assertRegex(delivery, r"旁白禁令.*适用于整条交付消息")
        self.assertRegex(delivery, r"审核时说明[^。]*原句[^。]*问题[^。]*依据[^。]*怎样改[^。]*应交付的意见")
        self.assertRegex(delivery, r"影响稿件使用的缺项、风险及未完成检查[^。]*文后提示")
        for concept in ["上轮未解决事项", "已发现未处理错误", "未处理原因", "下一步",
                        "文件交付时提示留在消息中", "明确只要稿件或省略说明时省略提示"]:
            self.assertIn(concept, delivery)
        anti_ai = (REFS / "anti-ai-patterns.md").read_text(encoding="utf-8")
        for concept in ["材料中的真实领导要求和批示按其业务含义保留",
                        "版本标识、流转对象、保密和适用范围声明", "按实际用途保留"]:
            self.assertIn(concept, anti_ai)

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
        primary_pages = {page["path"] for page in manifest["pages"] if page["kind"] == "genre"}
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
            self.assertEqual(
                set(page["forbidden_reads"]),
                primary_pages - set(page["allowed_reads"]),
                page["path"],
            )
        for route in manifest["routes"]:
            self.assertEqual(len(route["primary"]), 1)
            self.assertIn(route["primary"][0], primary_pages, route["id"])
            self.assertEqual(route["review"], FINAL_REVIEW_PATHS, route["id"])
        # Check real leaf coverage, including the previously omitted bulletin,
        # rather than accepting a target number of routes.
        self.assertEqual({route["primary"][0] for route in manifest["routes"]}, primary_pages)
        self.assertEqual(len({route["id"] for route in manifest["routes"]}), len(manifest["routes"]))

        pages = {page["path"]: page for page in manifest["pages"]}
        for legacy, owner in [
            ("handling-elements.md", "writing-rules.md"),
            ("official-style.md", "anti-ai-patterns.md"),
            ("review-direct-checklist.md", "review-checklist.md"),
            ("workflow.md", "writing-rules.md"),
        ]:
            self.assertIn(legacy, pages[f"references/{owner}"]["legacy_coverage"])
        mapping = (ROOT / "maintenance/docs/reference-rewrite-page-map-20260912.md").read_text(encoding="utf-8")
        baseline_pages = set(re.findall(r"^\|\s*\d+\s*\|\s*`([^`]+\.md)`", mapping, re.MULTILINE))
        active_coverage = {legacy for page in pages.values() for legacy in page["legacy_coverage"]}
        # The Pro-only gate is archived, not assigned to an active MIT owner.
        self.assertLessEqual(baseline_pages - {"delivery-review-gate.md"}, active_coverage)

    def test_reorganized_leaf_manifest_keeps_procurement_as_overlay(self) -> None:
        # Deterministic metadata closure is separate from native model routing evidence.
        manifest = __import__("json").loads(
            (ROOT / "maintenance/specs/reference-route-manifest.json").read_text(encoding="utf-8")
        )
        pages = {page["path"]: page for page in manifest["pages"]}
        routes = {route["id"]: route for route in manifest["routes"]}
        procurement = "references/genre-playbook-procurement-review.md"
        self.assertEqual(pages[procurement]["kind"], "overlay")
        for suffix in ["review-opinion", "technical-requirements", "responsibility-letter", "initiative", "open-letter", "narration", "information-materials", "editorial-note", "bulletin"]:
            path = f"references/genre-playbook-{suffix}.md"
            self.assertEqual(pages[path]["kind"], "genre")
            self.assertEqual(routes[suffix.replace("-", "_")]["primary"], [path])
        self.assertIn("情况综合", routes["report"]["triggers"])
        self.assertIn("建议信", routes["advisory"]["triggers"])
        self.assertIn("采购方案", routes["plan"]["triggers"])
        self.assertEqual(routes["procurement_review"]["primary"], ["references/genre-playbook-review-opinion.md"])
        self.assertIn(procurement, routes["procurement_review"]["overlays"])
        for route in routes.values():
            self.assertNotIn(procurement, route["primary"])

    def test_index_conflict_and_uncovered_pages_have_distinct_roles(self) -> None:
        index = (REFS / "reference-index.md").read_text(encoding="utf-8")
        conflict = (REFS / "genre-routing.md").read_text(encoding="utf-8")
        uncovered = (REFS / "genre-checklist.md").read_text(encoding="utf-8")
        for leaf in ["genre-playbook-bulletin.md", "genre-playbook-editorial-note.md", "genre-playbook-project-application.md"]:
            self.assertIn(leaf, index)
        for concept in ["标题", "模板", "用途", "行文关系", "请求批准", "权限", "上级答复下级请示"]:
            self.assertIn(concept, conflict)
        for concept in ["用户模板", "材料", "通用写法", "主体", "接收对象", "用途", "字段"]:
            self.assertIn(concept, uncovered)
        for page in [conflict, uncovered]:
            self.assertNotRegex(page, r"`(?:references/)?genre-playbook-[^`]+\.md`")

    def test_editorial_note_keeps_editor_voice_and_requested_delivery(self) -> None:
        text = (REFS / "genre-playbook-editorial-note.md").read_text(encoding="utf-8")
        for concept in ["编辑或编发者身份", "为何编发", "阅读重点", "保留其归属", "具体栏目沿革", "本轮只要按语", "同时需要被编发正文", "按要求照录"]:
            self.assertIn(concept, text)
        self.assertIn("任选一种清楚标示即可", text)
        self.assertIn("通常无需另套消息标题、导语和事件报道结构", text)
        news = (REFS / "genre-playbook-news-message.md").read_text(encoding="utf-8")
        self.assertNotIn("编者按", news)

    def test_procurement_purpose_and_correspondence_authority_are_preserved(self) -> None:
        procurement = (REFS / "genre-playbook-procurement-announcement.md").read_text(encoding="utf-8")
        for concept in ["发布目的", "征集响应", "结果告知", "终止事项", "预算或上限", "估算价", "成交金额不互换", "只提示影响当前发布目的的缺项"]:
            self.assertIn(concept, procurement)
        self.assertIn("不把响应条件、递交期限等征集要素强加给结果或终止公告", procurement)
        letter = (REFS / "genre-playbook-correspondence.md").read_text(encoding="utf-8")
        for concept in ["不相隶属", "请求批准", "审批答复", "有权范围", "缺少授权或结论依据", "不代作批准", "尚待批准", "上级答复下级请示用批复"]:
            self.assertIn(concept, letter)

    def test_new_primary_pages_preserve_subject_state_and_delivery_boundaries(self) -> None:
        expected = {
            "review-opinion": ["审查主体", "审查范围", "专家个人意见", "共同意见", "正式结论", "保留意见", "待核", "review-checklist.md"],
            "technical-requirements": ["功能", "接口", "运行条件", "交付", "验收", "已确认要求", "拟议选项", "待定参数", "现有问题"],
            "responsibility-letter": ["共同事项", "责任主体", "拟议状态", "签署", "日期", "奖惩", "追责"],
            "initiative": ["发起者", "倡议对象", "自愿参与", "处罚", "考核", "已取得成效", "日期"],
            "open-letter": ["发信主体", "受众", "发信方、执行方", "具体承诺", "仍在考虑", "日期"],
            "narration": ["讲解者身份", "受众", "路线", "顺序", "数字", "人物故事", "现场事实"],
            "information-materials": ["受众", "要求", "方法", "渠道", "适用范围", "处罚", "额外责任", "原状态"],
        }
        for suffix, concepts in expected.items():
            with self.subTest(page=suffix):
                text = (REFS / f"genre-playbook-{suffix}.md").read_text(encoding="utf-8")
                for concept in concepts:
                    self.assertIn(concept, text)
                self.assertRegex(text, r"共性写作页.*复核.*交付")
        procurement = (REFS / "genre-playbook-procurement-review.md").read_text(encoding="utf-8")
        for boundary in ["主文种已经确定", "预算与测算有别", "缺项", "未定状态", "建议与已定要求分开", "field-editing.md"]:
            self.assertIn(boundary, procurement)

    def test_retired_workflow_is_replaced_by_shared_common_rules(self) -> None:
        product = SKILL.read_text(encoding="utf-8") + "\n".join(
            page.read_text(encoding="utf-8") for page in REFS.glob("*.md")
        )
        for name in RETIRED_COMMON_PAGES | {"workflow.md"}:
            self.assertFalse((REFS / name).exists(), name)
            self.assertNotIn(name, product)
        skill_and_index = SKILL.read_text(encoding="utf-8") + (REFS / "reference-index.md").read_text(encoding="utf-8")
        for name in ["writing-rules.md", "argument-chains.md", "structure-editing.md", "compression-details.md"]:
            self.assertIn(name, skill_and_index)
        mapping = (ROOT / "maintenance/docs/reference-rewrite-page-map-20260912.md").read_text(encoding="utf-8")
        workflow_row = next(line for line in mapping.splitlines() if "`workflow.md`" in line and line.startswith("|"))
        for owner in ["SKILL.md", "writing-rules.md", "structure-editing.md", "field-editing.md", "compression-details.md"]:
            self.assertIn(owner, workflow_row)

    def test_mit_product_keeps_ordinary_scripts_and_moves_hooks_to_pro(self) -> None:
        for relative in ["hooks", "scripts/review_gate.py", "references/delivery-review-gate.md"]:
            self.assertFalse((SKILL.parent / relative).exists(), relative)
        for relative in ["scripts/draft_length.py", "scripts/prose_lint.py"]:
            self.assertTrue((SKILL.parent / relative).is_file(), relative)
        note = ROOT / "maintenance/docs/pro-hooks-next.md"
        self.assertTrue(note.is_file())
        text = note.read_text(encoding="utf-8")
        for asset in ["codex/pro-hooks-preserved-20260912", "v1.6.34", "MIT"]:
            self.assertIn(asset, text)

    def test_mirror_contains_rewritten_overlay(self) -> None:
        mirror = ROOT / "packages" / "agent-skills" / "skills" / "chinese-official-writing" / "references"
        for name in ["reference-index.md", "writing-rules.md", "ai-compute-docs.md"]:
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
        self.assertEqual(module._reference_paths_for_genres(["会议纪要"], ["只记录建议和待评估事项"]), ["SKILL.md", "references/genre-playbook-minutes.md"] + FINAL_REVIEW_PATHS)

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
        self.assertIn("按已选文种", text)
        self.assertIn("不用某个固定词反推文种", text)
        self.assertIn("历史模板", text)
        self.assertNotIn("20类事务文体", text)

    def test_common_rules_retain_natural_paragraph_compression(self) -> None:
        text = (REFS / "writing-rules.md").read_text(encoding="utf-8")
        for concept in ["章节功能", "自然段", "一两句话", "标题", "编号", "上限无需填满"]:
            self.assertIn(concept, text)
        self.assertRegex(text, r"保留用户的[^。]*模板")
        anti_ai = (REFS / "anti-ai-patterns.md").read_text(encoding="utf-8")
        self.assertIn("没有新增信息或不同作用", anti_ai)

    def test_local_tasks_keep_scope_without_a_separate_short_route(self) -> None:
        skill = SKILL.read_text(encoding="utf-8")
        common = (REFS / "writing-rules.md").read_text(encoding="utf-8")
        for reference in ["references/structure-editing.md", "references/field-editing.md"]:
            self.assertIn(reference, skill)
        for concept in ["修改范围", "逐字保留", "局部替换", "字段处理"]:
            self.assertIn(concept, common)
        self.assertRegex(common, r"局部查改动[及与]关联内容")
        spec = importlib.util.spec_from_file_location("rewrite_common_writer", ROOT / "maintenance/evals/official-writing/providers/agent_writer.py")
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        short = module._reference_paths_for_genres(["请示"], ["写一份 80 字采购请示"])
        ordinary = module._reference_paths_for_genres(["请示"], ["写一份采购请示"])
        self.assertEqual(short, ordinary)
        for relative in FINAL_REVIEW_PATHS:
            self.assertEqual(short.count(relative), 1)
        for references in module.GENRE_REFERENCES.values():
            self.assertFalse({Path(relative).name for relative in references} & RETIRED_COMMON_PAGES)
        self.assertEqual([ref for ref in short if "genre-playbook-" in ref], ["references/genre-playbook-request.md"])

    def test_anti_ai_reference_retains_semantic_risk_families(self) -> None:
        text = (REFS / "anti-ai-patterns.md").read_text(encoding="utf-8")
        for concept in ["必要否定", "供应商未定", "充分性自证", "起草过程", "隐藏推理", "句群", "专业术语", "否定范围", "论断强度", "标点", "版本标识"]:
            self.assertIn(concept, text)
        self.assertRegex(text, r"不按词表.*机械替换")
        self.assertIn("没有新增信息或不同作用", text)

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

    def test_common_review_preserves_fact_genre_template_and_modification_scope(self) -> None:
        common = (REFS / "writing-rules.md").read_text(encoding="utf-8")
        review = common.split("## 第三步：复核", 1)[1].split("## 第四步：交付", 1)[0]
        for concept in ["事实", "状态", "主文种", "要素", "局部", "关联内容", "附件", "批注", "修订", "交付前修正"]:
            self.assertIn(concept, review)
        self.assertIn("最新版底稿", common)
        self.assertIn("待核", common)
        self.assertNotRegex(common, r"`(?:references/)?genre-playbook-[^`]+\.md`")
        self.assertNotIn("复核完成即停止", review)

    def test_review_checklist_covers_full_review_without_excessive_gates(self) -> None:
        text = (REFS / "review-checklist.md").read_text(encoding="utf-8")
        self.assertFalse((REFS / "review-direct-checklist.md").exists())
        self.assertIn("审核默认检查全文", text)
        self.assertIn("`writing-rules.md`", text)
        # The review leaf owns issue judgment; shared checks stay on the linked workflow.
        for term in ["已确认错误", "待核实风险", "可选表达建议", "原句", "段落", "标题", "字段", "附件", "依据", "病句", "搭配"]:
            self.assertIn(term, text)
        for preserved_judgment in ["材料与常识", "条件性结论", "合理建议", "可选补充", "各自角色", "不确定性"]:
            self.assertIn(preserved_judgment, text)
        self.assertIn("可核算的数值用工具复算", text)
        self.assertIn("仅要求审核时交付意见", text)
        for revised_draft in ["审核后修改、复核后修改或优化稿件", "交付完整改后稿", "有充分依据的问题", "本轮范围内"]:
            self.assertIn(revised_draft, text)
        delivery = (REFS / "writing-rules.md").read_text(encoding="utf-8")
        for shared_check in ["事实", "状态", "主文种", "要素", "附件", "主体", "最新版底稿", "anti-ai-patterns.md", "prose-lint-usage.md"]:
            self.assertIn(shared_check, delivery)
        self.assertIn("Word按模板核样式", delivery)
        self.assertIn("模板", delivery.split("## 第二步：成稿与篇幅", 1)[1])
        for delivery_element in ["完整稿件", "审核", "位置", "问题", "建议改法", "替代表达", "范围内"]:
            self.assertIn(delivery_element, delivery)
        self.assertNotRegex(text, r"`(?:references/)?genre-playbook-[^`]+\.md`")
        product = SKILL.read_text(encoding="utf-8") + "\n".join(
            page.read_text(encoding="utf-8") for page in REFS.glob("*.md")
        )
        self.assertNotIn("review-direct-checklist.md", product)
        commentary = (REFS / "genre-playbook-news-commentary.md").read_text(encoding="utf-8")
        self.assertIn("事实段保持来源口径，按本轮范围修正语言与篇幅", commentary)
        self.assertIn("保留有实际作用的否定与比较", commentary)
        self.assertNotIn("事实段只核对，不重写", commentary)

    def test_prose_lint_modes_follow_text_type_and_recheck_script_edits(self) -> None:
        text = (REFS / "prose-lint-usage.md").read_text(encoding="utf-8")
        for text_type, mode in [("稿件正文", "draft-body"), ("正文连同独立文后提示", "gap-note-allowed"), ("审稿意见本身", "review-only")]:
            self.assertRegex(text, rf"{text_type}[^。]*`{mode}`")
        for command in ["scripts/prose_lint.py", "--structure", "--format"]:
            self.assertIn(command, text)
        for concept in ["原文件保留", "另存新稿", "复扫", "已检查文本", "未完成"]:
            self.assertIn(concept, text)
        common = (REFS / "writing-rules.md").read_text(encoding="utf-8")
        for concept in ["关联内容", "影响篇幅时另测字数", "范围内已确认的问题"]:
            self.assertIn(concept, common)

    def test_common_owner_keeps_fact_and_handling_element_boundaries(self) -> None:
        common = (REFS / "writing-rules.md").read_text(encoding="utf-8")
        self.assertFalse((REFS / "handling-elements.md").exists())
        for concept in ["材料与常识", "不确定性", "实质缺项", "拟", "建议", "待核", "未决定", "范围", "强度"]:
            self.assertIn(concept, common)
        self.assertRegex(common, r"只有主题或方向.*功能.*拟议")
        self.assertRegex(common, r"当天日期.*草稿日期")
        self.assertRegex(common, r"指定留空、待确认.*按要求保留")
        self.assertRegex(common, r"业务日期沿用材料")
        for term in ["主体", "对象", "事项", "依据", "状态", "期限", "金额", "附件", "落款", "日期", "信息未给", "矛盾", "主文种", "用户模板"]:
            self.assertIn(term, common)
        self.assertIn("分清信息未给与业务未定", common)
        self.assertRegex(common, r"保留用户的[^。]*字段、表格及指定空位")
        self.assertRegex(common, r"主体、对象、数字、金额、业务日期、引语、来源[及和]事实状态.*照实保留")
        correspondence = next(line for line in common.splitlines() if "正文、表格、附件" in line)
        for term in ["核对", "主体", "名称", "数值", "顺序", "期限", "结论", "状态", "指向"]:
            self.assertIn(term, correspondence)
        self.assertIn("分清实测、测算和估算", common)
        # Optional contact/feedback details belong to the chosen genre, rather
        # than requiring another common table or restoring the retired page.
        letter = (REFS / "genre-playbook-correspondence.md").read_text(encoding="utf-8")
        for term in ["期限", "方式", "联系人", "附件", "材料未给且不影响办理时"]:
            self.assertIn(term, letter)
        self.assertIn("references/external-research.md", SKILL.read_text(encoding="utf-8"))
        self.assertNotRegex(common, r"\|\s*文种(?:/材料)?\s*\|")

    def test_style_and_addressing_pages_keep_relation_and_strength_boundaries(self) -> None:
        style = (REFS / "anti-ai-patterns.md").read_text(encoding="utf-8")
        self.assertFalse((REFS / "official-style.md").exists())
        addressing = (REFS / "formal-addressing.md").read_text(encoding="utf-8")
        for term in ["段落", "证据", "上行文", "下行文", "平行文"]:
            self.assertIn(term, style + addressing)
        for term in ["叙述身份", "同义正式语体", "否定范围", "先后", "论断强度"]:
            self.assertIn(term, style)
        self.assertIn("不编造机关名称", addressing)

    def test_speech_page_keeps_sparse_theme_material_at_original_strength(self) -> None:
        text = (REFS / "genre-playbook-speech-address.md").read_text(encoding="utf-8")
        self.assertIn("材料只给主题、工作考虑、下一步方向和未定状态", text)
        self.assertIn("主题词不单独证明已有基础、具体问题、实施路径或已定安排", text)

    def test_sparse_plan_can_omit_unprovided_structure_sections(self) -> None:
        text = (REFS / "genre-playbook-plan-construction.md").read_text(encoding="utf-8")
        self.assertIn("围绕已有目标、范围、步骤和期限成稿", text)
        self.assertIn("相邻内容可合成自然段", text)
        self.assertIn("未提供的信息按 `writing-rules.md` 处理", text)
        self.assertNotIn("人员、设备、扫描方式、质量控制、周报、签字、经费、风险处置和量化验收沿用待确认状态", text)


if __name__ == "__main__":
    unittest.main()
