from __future__ import annotations

from pathlib import Path
import json
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]


def relative_files(root: Path) -> list[str]:
    return sorted(
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc"
    )


class SkillBoundaryTests(unittest.TestCase):
    def test_only_one_agent_handoff_entrypoint_remains(self) -> None:
        self.assertTrue((ROOT / "AGENTS.md").is_file())
        self.assertFalse((ROOT / "agent.md").exists())

    def test_canonical_skill_declares_trigger_and_exclusion_boundaries(self) -> None:
        text = (ROOT / "chinese-official-writing" / "SKILL.md").read_text(encoding="utf-8")

        description = re.search(r"^description: (.+)$", text, re.M)
        self.assertIsNotNone(description)
        self.assertLessEqual(len(description.group(1)), 280)
        for keyword in ["申请", "请示", "报告", "通知", "通告", "意见", "决定", "函", "采购公告", "审查材料", "正式文本"]:
            self.assertIn(keyword, description.group(1))
        for excluded in ["营销", "社媒", "论文"]:
            self.assertIn(excluded, description.group(1))
        self.assertIn("当用户明确要求中文通知", text)
        self.assertIn("## 触发条件与边界", text)
        self.assertIn("批量语料生成", text)
        self.assertIn("规避人工审核", text)
        self.assertIn("替代法律/财务/采购/审计/政策依据判断", text)

    def test_adapter_skill_copies_keep_boundaries(self) -> None:
        paths = [
            ROOT / "skills" / "chinese-official-writing" / "SKILL.md",
            ROOT / ".agents" / "skills" / "chinese-official-writing" / "SKILL.md",
            ROOT / ".qwen" / "skills" / "chinese-official-writing" / "SKILL.md",
            ROOT / "hermes" / "skills" / "chinese-official-writing" / "SKILL.md",
            ROOT / "openclaw" / "skills" / "chinese_official_writing" / "SKILL.md",
        ]

        for path in paths:
            with self.subTest(path=path):
                text = path.read_text(encoding="utf-8")
                self.assertIn("批量语料生成", text)
                self.assertIn("规避人工审核", text)

    def test_drafting_rules_are_split_for_prompt_following(self) -> None:
        text = (ROOT / "chinese-official-writing" / "SKILL.md").read_text(encoding="utf-8")
        lines = text.splitlines()
        drafting_lines = [
            line
            for line in lines
            if line.startswith("- 起草或改写：") or line.startswith("  - ")
        ]

        self.assertTrue(any(line.startswith("- 起草或改写：") for line in drafting_lines))
        self.assertLess(max(len(line) for line in drafting_lines), 360)
        self.assertGreaterEqual(sum(1 for line in drafting_lines if line.startswith("  - ")), 4)

    def test_long_form_headings_warn_against_markdown_bold(self) -> None:
        text = (ROOT / "chinese-official-writing" / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn("Markdown 格式残留", text)
        self.assertIn("活动方案、实施方案等长稿正文的小标题", text)
        self.assertIn("不用 `**加粗**`", text)

    def test_primary_adapter_mirrors_match_canonical_bytes(self) -> None:
        canonical = ROOT / "chinese-official-writing"
        canonical_files = relative_files(canonical)
        for target in [
            ROOT / "skills" / "chinese-official-writing",
            ROOT / ".agents" / "skills" / "chinese-official-writing",
            ROOT / ".qwen" / "skills" / "chinese-official-writing",
        ]:
            with self.subTest(target=target):
                self.assertEqual(relative_files(target), canonical_files)
                for relative in canonical_files:
                    self.assertEqual((target / relative).read_bytes(), (canonical / relative).read_bytes(), relative)

    def test_packaged_resource_mirrors_match_canonical_bytes(self) -> None:
        canonical = ROOT / "chinese-official-writing"
        for target in [
            ROOT / "hermes" / "skills" / "chinese-official-writing",
            ROOT / "openclaw" / "skills" / "chinese_official_writing",
        ]:
            for folder in ["agents", "references", "scripts"]:
                canonical_folder = canonical / folder
                target_folder = target / folder
                with self.subTest(target=target, folder=folder):
                    files = relative_files(canonical_folder)
                    self.assertEqual(relative_files(target_folder), files)
                    for relative in files:
                        self.assertEqual(
                            (target_folder / relative).read_bytes(),
                            (canonical_folder / relative).read_bytes(),
                            f"{target}/{folder}/{relative}",
                        )

    def test_reference_loading_table_keeps_progressive_disclosure(self) -> None:
        text = (ROOT / "chinese-official-writing" / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn("按任务渐进读取资料，不要一次性加载全部文件", text)
        self.assertIn("| 文件 | 阶段 | 加载条件 |", text)
        self.assertIn("`references/task-route-cards.md` | 起草前/改稿前", text)
        self.assertIn("低上下文局部修改", text)
        self.assertIn("`references/genre-playbooks.md` | 按文种/专项选读", text)
        self.assertIn("`references/ai-compute-docs.md` | 专项选读", text)
        self.assertIn("仅在 AI 算力、GPU/服务器租赁、模型服务、采购、租赁、可研、成本比较、SLA、安全或验收材料中读取", text)

    def test_task_route_cards_keep_sparse_tasks_lightweight(self) -> None:
        skill = (ROOT / "chinese-official-writing" / "SKILL.md").read_text(encoding="utf-8")
        cards = (ROOT / "chinese-official-writing" / "references" / "task-route-cards.md").read_text(
            encoding="utf-8"
        )
        sync_script = (ROOT / "tools" / "sync_adapters.py").read_text(encoding="utf-8")

        for text in [skill, sync_script]:
            self.assertIn("references/task-route-cards.md", text)
            self.assertIn("材料稀疏", text)
            self.assertIn("不新增事实", text)
        for term in [
            "必须转读长 reference 的情况",
            "用户要求完整文种骨架",
            "800 字以上长文",
            "会议纪要/可研/采购/AI 算力等专项论证",
            "先写可用正文",
            "不补工作组、问题清单、统一共识、治理流程、整改路径",
            "保持未决口径",
            "不写“会议强调”“会议认为”“会议决定”",
            "宁可短写",
            "不补“认真落实、严肃处理、记录留痕、无论有无异常",
            "Markdown 加粗、标题井号、横线等属于格式噪点",
            "事实边界、要点置入和用户禁止项",
            "上一轮待确认事项仍是软提示",
        ]:
            self.assertIn(term, cards)
        self.assertLess(len(cards.splitlines()), 80)

    def test_light_route_is_terminal_until_an_explicit_escalation_condition(self) -> None:
        skill = (ROOT / "chinese-official-writing" / "SKILL.md").read_text(encoding="utf-8")
        cards = (ROOT / "chinese-official-writing" / "references" / "task-route-cards.md").read_text(
            encoding="utf-8"
        )
        playbooks = (ROOT / "chinese-official-writing" / "references" / "genre-playbooks.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("不因文种名称已知而自动预读下列全部长 reference", skill)
        self.assertIn("以本页结束 reference 路由", cards)
        self.assertIn("不因文种名称已知而继续预读", cards)
        self.assertIn("每个文种小节都是可从 `SKILL.md` 直接进入的叶子路由", playbooks)
        self.assertIn("不要求先完整读取 `workflow.md` 或 `genre-routing.md`", playbooks)
        self.assertIn("不要把每节末尾的“补充读取”当成固定加载清单", playbooks)

    def test_reference_links_form_an_acyclic_graph(self) -> None:
        refs = ROOT / "chinese-official-writing" / "references"
        graph: dict[str, set[str]] = {}
        link_re = re.compile(r"`(?:references/)?([^`/]+\.md)`")
        for source in refs.glob("*.md"):
            targets = {
                match.group(1)
                for match in link_re.finditer(source.read_text(encoding="utf-8"))
                if (refs / match.group(1)).is_file()
            }
            graph[source.name] = targets

        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(node: str, trail: tuple[str, ...]) -> None:
            if node in visiting:
                self.fail("reference cycle: " + " -> ".join((*trail, node)))
            if node in visited:
                return
            visiting.add(node)
            for target in graph.get(node, set()):
                visit(target, (*trail, node))
            visiting.remove(node)
            visited.add(node)

        for node in graph:
            visit(node, ())

        anti_ai = (refs / "anti-ai-patterns.md").read_text(encoding="utf-8")
        review = (refs / "review-checklist.md").read_text(encoding="utf-8")
        self.assertNotIn("`final-review-layers.md`", anti_ai)
        self.assertNotIn("`review-checklist.md`", anti_ai)
        self.assertNotIn("`final-review-layers.md`", review)
        self.assertNotIn("`anti-ai-patterns.md`", review)

    def test_trigger_description_covers_reported_genres(self) -> None:
        text = (ROOT / "chinese-official-writing" / "SKILL.md").read_text(encoding="utf-8")

        for keyword in ["复函", "公示", "通告", "意见", "决定", "决议", "议案", "公报", "命令", "工作要点", "审查材料"]:
            self.assertIn(keyword, text)

    def test_multi_round_revision_rules_keep_structure_and_genre_format(self) -> None:
        skill = (ROOT / "chinese-official-writing" / "SKILL.md").read_text(encoding="utf-8")
        workflow = (ROOT / "chinese-official-writing" / "references" / "workflow.md").read_text(encoding="utf-8")
        checklist = (ROOT / "chinese-official-writing" / "references" / "review-checklist.md").read_text(encoding="utf-8")

        for text in [skill, workflow, checklist]:
            self.assertIn("多轮", text)
            self.assertIn("增加自然段", text)
            self.assertIn("反馈渠道", text)
            self.assertIn("原因分析", text)
            self.assertIn("发送人", text)
            self.assertIn("接收方", text)
        self.assertIn("改稿前小标题清单", checklist)
        self.assertIn("改稿后小标题清单", checklist)
        self.assertIn("小标题数量", checklist)

    def test_legal_genres_have_checklist_and_handling_elements(self) -> None:
        checklist = (ROOT / "chinese-official-writing" / "references" / "genre-checklist.md").read_text(encoding="utf-8")
        elements = (ROOT / "chinese-official-writing" / "references" / "handling-elements.md").read_text(encoding="utf-8")

        self.assertIn("## 通告", checklist)
        for genre in ["决议", "公告", "通告", "意见"]:
            self.assertIn(f"| {genre} |", elements)

    def test_reported_genre_coverage_gaps_have_minimum_support(self) -> None:
        routing = (ROOT / "chinese-official-writing" / "references" / "genre-routing.md").read_text(encoding="utf-8")
        checklist = (ROOT / "chinese-official-writing" / "references" / "genre-checklist.md").read_text(encoding="utf-8")
        elements = (ROOT / "chinese-official-writing" / "references" / "handling-elements.md").read_text(encoding="utf-8")

        for keyword in ["工作要点：", "工作总结：", "审查材料：", "讲话稿/致辞/述职报告"]:
            self.assertIn(keyword, routing)
        for heading in ["## 征求意见函", "## 采购公告"]:
            self.assertIn(heading, checklist)
        for genre in ["公示", "征求意见函", "采购公告"]:
            self.assertIn(f"| {genre} |", elements)

    def test_format_reference_clarifies_document_number_brackets(self) -> None:
        text = (ROOT / "chinese-official-writing" / "references" / "format-gbt9704.md").read_text(encoding="utf-8")

        self.assertIn("年份使用六角括号 `〔〕`", text)
        self.assertIn("不要用方括号 `[]` 或圆括号 `()` 替代", text)

    def test_final_drafts_must_not_keep_unfinished_placeholders(self) -> None:
        skill = (ROOT / "chinese-official-writing" / "SKILL.md").read_text(encoding="utf-8")
        elements = (ROOT / "chinese-official-writing" / "references" / "handling-elements.md").read_text(encoding="utf-8")
        checklist = (ROOT / "chinese-official-writing" / "references" / "review-checklist.md").read_text(encoding="utf-8")

        for text in [skill, elements, checklist]:
            self.assertTrue("最终正文" in text or "交付正文" in text)
            self.assertIn("〔签发日期〕", text)
            self.assertIn("未完成占位", text)

        self.assertIn("当前日期不得替代维护时间", skill)
        self.assertIn("当前日期只可用于草稿落款", elements)
        self.assertIn("未把当前日期误用为维护时间", checklist)
        self.assertIn("[具体项目名称]", skill)
        self.assertIn("（成文日期待确认）", skill)
        self.assertIn("成文日期明示缺失或待确认时放正文外提示", skill)
        self.assertIn("不使用当前日期补落款", skill)
        self.assertIn("YYYY年MM月DD日", elements)

    def test_openclaw_marketplace_readme_is_user_facing(self) -> None:
        text = (ROOT / "openclaw" / "marketplace-readme.md").read_text(encoding="utf-8")

        self.assertIn("clawhub install chinese-official-writing", text)
        self.assertIn("其他平台", text)
        self.assertIn("GitHub 仓库 README", text)
        self.assertIn("安装包内包含精简入口和完整 `references/`", text)
        self.assertIn("关键边界以本入口规则和 `references/` 为准", text)
        self.assertNotIn("### Codex / OpenAI Skill", text)
        self.assertNotIn("npm run eval:official-writing", text)

    def test_readme_does_not_route_to_prompt_only_chatbot_repo(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("## 安装方式", readme)
        self.assertNotIn("## 安装 Prompt", readme)
        self.assertNotIn("轻量纯提示词版本", readme)
        self.assertNotIn("chinese-official-writing-chatbot-prompt", readme)

    def test_readme_documents_domestic_agent_install_paths(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        sync_script = (ROOT / "tools" / "sync_adapters.py").read_text(encoding="utf-8")
        skill = (ROOT / "chinese-official-writing" / "SKILL.md").read_text(encoding="utf-8")

        for term in [
            "Qwen Code",
            "通用 Agent Skills",
            "MiniMax Skills",
            "GLM Skills（Z.ai/智谱）",
            "AutoClaw",
            "Kimi Code CLI",
            "TRAE",
            "Baidu Comate AI IDE",
        ]:
            self.assertIn(term, readme)
        for path in [
            ".qwen/skills/chinese-official-writing/",
            "skills/chinese-official-writing/",
            ".agents/skills/chinese-official-writing/",
        ]:
            self.assertIn(path, readme)
        self.assertIn("npx skills add https://github.com/gongyu0918-debug/chinese-official-writing-skill --skill chinese-official-writing", readme)
        for mode in ['"qwen"']:
            self.assertIn(mode, sync_script)
        self.assertNotIn('"minimax"', sync_script)
        self.assertNotIn('"glm"', sync_script)
        for agent in [
            "qwen-code",
            "minimax-skills",
            "glm-skills",
            "autoclaw",
            "kimi-code-cli",
            "trae",
            "baidu-comate-ai-ide",
            "generic-agent-skills",
        ]:
            self.assertIn(agent, skill)

    def test_claude_plugin_manifest_version_matches_skill_and_sync_script(self) -> None:
        manifest = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
        skill = (ROOT / "chinese-official-writing" / "SKILL.md").read_text(encoding="utf-8")
        sync_script = (ROOT / "tools" / "sync_adapters.py").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        openclaw_readme = (ROOT / "openclaw" / "README.md").read_text(encoding="utf-8")
        marketplace_readme = (ROOT / "openclaw" / "marketplace-readme.md").read_text(encoding="utf-8")
        skill_card = (ROOT / "openclaw" / "skill-card.md").read_text(encoding="utf-8")

        skill_version = re.search(r'version: "([^"]+)"', skill)
        sync_version = re.search(r'VERSION = "([^"]+)"', sync_script)
        readme_version = re.search(r"chinese-official-writing@(\d+\.\d+\.\d+)", readme)
        openclaw_publish_version = re.search(r"--version\s+(\d+\.\d+\.\d+)", openclaw_readme)
        marketplace_version = re.search(r"chinese-official-writing@(\d+\.\d+\.\d+)", marketplace_readme)
        skill_card_version = re.search(r"^(\d+\.\d+\.\d+) \(source: server release metadata", skill_card, re.M)

        self.assertIsNotNone(skill_version)
        self.assertIsNotNone(sync_version)
        self.assertIsNotNone(readme_version)
        self.assertIsNotNone(openclaw_publish_version)
        self.assertIsNotNone(marketplace_version)
        self.assertIsNotNone(skill_card_version)
        self.assertEqual(manifest["version"], skill_version.group(1))
        self.assertEqual(manifest["version"], sync_version.group(1))
        self.assertEqual(manifest["version"], readme_version.group(1))
        self.assertEqual(manifest["version"], openclaw_publish_version.group(1))
        self.assertEqual(manifest["version"], marketplace_version.group(1))
        self.assertEqual(manifest["version"], skill_card_version.group(1))
        self.assertIn("ROOT_README", sync_script)
        self.assertIn("OPENCLAW_README", sync_script)
        self.assertIn("OPENCLAW_MARKETPLACE_README", sync_script)
        self.assertIn("OPENCLAW_SKILL_CARD", sync_script)

    def test_lint_strict_fail_on_is_documented(self) -> None:
        skill = (ROOT / "chinese-official-writing" / "SKILL.md").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("--strict --fail-on medium", skill)
        self.assertIn("--strict --fail-on medium", readme)

    def test_revision_workflow_forbids_new_unprovided_facts(self) -> None:
        skill = (ROOT / "chinese-official-writing" / "SKILL.md").read_text(encoding="utf-8")
        workflow = (ROOT / "chinese-official-writing" / "references" / "workflow.md").read_text(encoding="utf-8")
        checklist = (ROOT / "chinese-official-writing" / "references" / "review-checklist.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("未新增原文外事实", skill)
        self.assertIn("不新增原文没有交代的活动、依据、数据、成效或责任安排", workflow)
        self.assertIn("未新增原文外事实", workflow)
        self.assertIn("未新增原文外事实", checklist)
        self.assertIn("用户要求只输出正文时，不附自证说明", workflow)
        self.assertIn("除非用户同时明确允许文后待确认、风险或核验提示", workflow)
        self.assertIn("也不附其他正文外内容", workflow)
        self.assertIn("用户未要求只输出正文、只输出改后稿或不解释时", checklist)
        self.assertIn("用户只要求正文且未同时允许文后提示时", checklist)

    def test_v140_mode_routing_material_mapping_and_format_bridge_are_documented(self) -> None:
        skill = (ROOT / "chinese-official-writing" / "SKILL.md").read_text(encoding="utf-8")
        workflow = (ROOT / "chinese-official-writing" / "references" / "workflow.md").read_text(encoding="utf-8")
        checklist = (ROOT / "chinese-official-writing" / "references" / "review-checklist.md").read_text(
            encoding="utf-8"
        )
        anti_ai = (ROOT / "chinese-official-writing" / "references" / "anti-ai-patterns.md").read_text(
            encoding="utf-8"
        )
        format_ref = (ROOT / "chinese-official-writing" / "references" / "format-gbt9704.md").read_text(
            encoding="utf-8"
        )

        for text in [skill, workflow]:
            self.assertIn("任务模式路由", text)
            self.assertIn("起草", text)
            self.assertIn("改稿", text)
            self.assertIn("复核", text)
            self.assertIn("排版交付", text)
        self.assertIn("原文已有事实", workflow)
        self.assertIn("压实合并表达", workflow)
        self.assertIn("待确认补充", workflow)
        self.assertIn("数据冲突不得默认就高", workflow)
        self.assertIn("空章节不直接编实", workflow)
        self.assertIn("原文已有事实", checklist)
        self.assertIn("未默认就高或自选最优", checklist)
        for term in ["夸大意义", "宣传腔", "模糊归因", "公式化未来展望", "同义词循环", "机械三段式", "过度抽象词互相解释"]:
            self.assertIn(term, anti_ai)
        self.assertIn("不新增硬清洗", anti_ai)
        self.assertIn("Word/排版交付衔接", format_ref)
        self.assertIn("DOCX/document 技能", format_ref)
        self.assertIn("不得编造文号", format_ref)
        self.assertIn("Markdown `**加粗**`", format_ref)

    def test_v141_formal_delivery_review_and_tone_rules_are_documented(self) -> None:
        skill = (ROOT / "chinese-official-writing" / "SKILL.md").read_text(encoding="utf-8")
        checklist = (ROOT / "chinese-official-writing" / "references" / "review-checklist.md").read_text(
            encoding="utf-8"
        )
        official_style = (ROOT / "chinese-official-writing" / "references" / "official-style.md").read_text(
            encoding="utf-8"
        )
        format_ref = (ROOT / "chinese-official-writing" / "references" / "format-gbt9704.md").read_text(
            encoding="utf-8"
        )
        sync_script = (ROOT / "tools" / "sync_adapters.py").read_text(encoding="utf-8")

        for text in [skill, format_ref, checklist, sync_script]:
            self.assertIn("正式交付前要素核对", text)
            self.assertIn("签发", text)
            self.assertIn("版记", text)
        self.assertIn("缺项清单", format_ref)
        self.assertIn("不得用 `[依据/背景]`", format_ref)
        self.assertIn("未编造文号、签发人、印章或版记", checklist)
        self.assertIn("用户可读格式复核项", checklist)
        for term in ["标题", "文种", "主送/受文对象", "发文字号", "日期", "附件", "落款", "结尾语", "层级编号"]:
            self.assertIn(term, checklist)
        self.assertIn("位置、风险层级、修改建议", checklist)
        self.assertIn("未默认重写全文", checklist)
        self.assertIn("不做 0-100 分评分", checklist)
        self.assertIn("轻量语气替换建议", official_style)
        for term in ["我觉得", "搞", "差不多", "马上", "然后"]:
            self.assertIn(term, official_style)
        self.assertIn("保留原文事实", official_style)
        self.assertIn("不新增硬清洗", official_style)
        self.assertIn("不新增硬清洗", skill)

        skill_files = relative_files(ROOT / "chinese-official-writing")
        for forbidden in ["document_generator.py", "generate_official_doc.py", "install_fonts.py", "format_docx.py"]:
            self.assertNotIn(forbidden, skill_files)

    def test_v141_search_boundary_stays_lightweight_and_opt_in(self) -> None:
        skill = (ROOT / "chinese-official-writing" / "SKILL.md").read_text(encoding="utf-8")
        workflow = (ROOT / "chinese-official-writing" / "references" / "workflow.md").read_text(encoding="utf-8")
        elements = (ROOT / "chinese-official-writing" / "references" / "handling-elements.md").read_text(
            encoding="utf-8"
        )
        checklist = (ROOT / "chinese-official-writing" / "references" / "review-checklist.md").read_text(
            encoding="utf-8"
        )
        openclaw_skill = (ROOT / "openclaw" / "skills" / "chinese_official_writing" / "SKILL.md").read_text(
            encoding="utf-8"
        )

        for text in [skill, workflow, checklist, openclaw_skill]:
            self.assertIn("联网搜索", text)
        self.assertIn("联网核验", elements)
        self.assertIn("默认不外搜", skill)
        self.assertIn("不把联网搜索作为起草、改稿或复核的默认步骤", workflow)
        for term in ["最新", "当前", "今日", "现行政策", "近期数据"]:
            self.assertIn(term, workflow)
        self.assertIn("搜索结果只作为来源参考", skill)
        self.assertIn("来源、日期或检索口径", skill)
        self.assertIn("发布日期、访问日期或检索口径", workflow)
        self.assertIn("来源冲突、无法核验或工具不可用", workflow)
        self.assertIn("默认不外搜补缺项", elements)
        self.assertIn("未因单位名称自动搜索单位公开样文", checklist)
        for text in [skill, elements, openclaw_skill]:
            self.assertIn("不因出现单位名称就搜索单位公开样文", text)
        self.assertIn("只出现单位名称，不触发搜索单位公开样文", workflow)
        skill_files = relative_files(ROOT / "chinese-official-writing")
        for forbidden in ["search_units.py", "unit_style_cache.json", "unit-style-registry.md"]:
            self.assertNotIn(forbidden, skill_files)

    def test_v144_common_real_writing_risks_and_adoption_gate_are_documented(self) -> None:
        skill = (ROOT / "chinese-official-writing" / "SKILL.md").read_text(encoding="utf-8")
        workflow = (ROOT / "chinese-official-writing" / "references" / "workflow.md").read_text(encoding="utf-8")
        checklist = (ROOT / "chinese-official-writing" / "references" / "review-checklist.md").read_text(
            encoding="utf-8"
        )
        official_style = (ROOT / "chinese-official-writing" / "references" / "official-style.md").read_text(
            encoding="utf-8"
        )
        genre_checklist = (ROOT / "chinese-official-writing" / "references" / "genre-checklist.md").read_text(
            encoding="utf-8"
        )
        anti_ai = (ROOT / "chinese-official-writing" / "references" / "anti-ai-patterns.md").read_text(
            encoding="utf-8"
        )
        format_ref = (ROOT / "chinese-official-writing" / "references" / "format-gbt9704.md").read_text(
            encoding="utf-8"
        )
        agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")

        for text in [skill, workflow, checklist]:
            self.assertIn("指定渠道", text)
            self.assertIn("截止时间前", text)
            self.assertIn("联系人沟通", text)
        self.assertIn("事实充分性软处理", workflow)
        self.assertIn("正文泛占位", checklist)
        self.assertIn("新增字段没有用户提供值", workflow)
        self.assertIn("即使用分号写在一行", workflow)
        self.assertIn("不合并成连续句", workflow)
        self.assertIn("不推断发票、票据、邮箱、截止日期", workflow)
        self.assertIn("字段值未知", checklist)
        self.assertIn("分号串写的“字段名：字段值”序列", checklist)
        self.assertIn("字数自检", skill)
        self.assertIn("5%-10% 余量", skill)
        self.assertIn("去空行后的正文计数", workflow)
        self.assertIn("5%-10% 余量", workflow)
        self.assertIn("避免静默超字数", checklist)
        self.assertIn("长篇限字稿件", skill)
        self.assertIn("篇幅预算", workflow)
        self.assertIn("背景现状", workflow)
        self.assertIn("问题原因", workflow)
        self.assertIn("措施安排", workflow)
        self.assertIn("结尾落点", workflow)
        self.assertIn("避免头重脚轻", skill)
        self.assertIn("草草收尾", checklist)
        self.assertIn("不要写成“已确认可作为 Word 稿基础”", format_ref)
        self.assertIn("评价强度", official_style)
        self.assertIn("评价强度超过证据", anti_ai)
        self.assertIn("证据强度", checklist)
        self.assertIn("来源名称、发布机关或发布主体、文号或链接", workflow)
        self.assertIn("搜索来源清单", checklist)
        self.assertIn("正文内容已经定稿", format_ref)
        self.assertIn("默认另存新版本", format_ref)
        for text in [skill, workflow, checklist, agents]:
            self.assertIn("prompt/markdown", text)
            self.assertTrue(
                "不复制" in text or "不直接复制" in text or "未复制" in text or "不直接誊抄" in text or "禁止直接誊抄" in text
            )
        self.assertIn("禁止直接誊抄代码、脚本、正则、模板库、大段 prompt、固定话术或模板正文", agents)

    def test_fact_sufficiency_guidance_is_soft_and_non_blocking(self) -> None:
        skill = (ROOT / "chinese-official-writing" / "SKILL.md").read_text(encoding="utf-8")
        workflow = (ROOT / "chinese-official-writing" / "references" / "workflow.md").read_text(encoding="utf-8")
        checklist = (ROOT / "chinese-official-writing" / "references" / "review-checklist.md").read_text(
            encoding="utf-8"
        )

        self.assertNotIn("暂停确认", skill)
        self.assertNotIn("暂停确认", workflow)
        self.assertNotIn("可补充后更完整的关键事实", skill)
        self.assertNotIn("可补充后更完整的关键事实", workflow)
        self.assertNotIn("可补充后更完整的关键事实", checklist)
        self.assertIn("事实不足不作为默认中断理由", skill)
        self.assertIn("补充以下信息后，文章会更完整", skill)
        self.assertIn("不要做调查问卷式问题清单", skill)
        self.assertIn("不把上一轮待确认事项升级为阻断条件", skill)
        self.assertIn("材料未给风险结论", skill)
        self.assertIn("未发现重大隐患", skill)
        self.assertIn("材料只给问题清单", skill)
        self.assertIn("能够正常开展", skill)
        self.assertIn("不在正文前中断成稿", workflow)
        self.assertIn("不连续追问", workflow)
        self.assertIn("先按用户已给材料完成正文", workflow)
        self.assertIn("不做调查问卷", workflow)
        self.assertIn("补充以下信息后，文章会更完整", workflow)
        self.assertIn("写稿人可安排事项", workflow)
        self.assertIn("待确认事项仍是软提示", workflow)
        self.assertIn("仍先执行本轮修改请求", workflow)
        self.assertIn("从已给材料看，问题集中于", workflow)
        self.assertIn("结论口径列入正文外待确认", workflow)
        self.assertIn("概括性正向判断", workflow)
        self.assertIn("未在正文前中断成稿或连续追问", checklist)
        self.assertIn("补充以下信息后，文章会更完整", checklist)
        self.assertIn("未做调查问卷式问题清单", checklist)
        self.assertIn("转嫁给用户", checklist)
        self.assertIn("不把待确认事项升级成阻断链路", checklist)
        self.assertIn("事实强判断", checklist)
        self.assertIn("总体较好", checklist)

    def test_v147_minimal_borrowing_rules_stay_soft_and_prompt_based(self) -> None:
        skill = (ROOT / "chinese-official-writing" / "SKILL.md").read_text(encoding="utf-8")
        workflow = (ROOT / "chinese-official-writing" / "references" / "workflow.md").read_text(encoding="utf-8")
        checklist = (ROOT / "chinese-official-writing" / "references" / "review-checklist.md").read_text(
            encoding="utf-8"
        )
        format_ref = (ROOT / "chinese-official-writing" / "references" / "format-gbt9704.md").read_text(
            encoding="utf-8"
        )
        anti_ai = (ROOT / "chinese-official-writing" / "references" / "anti-ai-patterns.md").read_text(
            encoding="utf-8"
        )
        official_style = (ROOT / "chinese-official-writing" / "references" / "official-style.md").read_text(
            encoding="utf-8"
        )
        genre_checklist = (ROOT / "chinese-official-writing" / "references" / "genre-checklist.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("正式交付前要素核对卡", skill)
        self.assertIn("正式交付前要素核对卡", format_ref)
        self.assertIn("不因缺这些正式要素阻断成稿", format_ref)
        self.assertIn("发文机关", format_ref)
        self.assertIn("印章或签署信息", format_ref)
        self.assertIn("优先只列用户点名缺项", format_ref)
        self.assertIn("其他正式要素按单位模板另行核对", format_ref)
        self.assertIn("核对卡优先只列这些点名要素", skill)
        self.assertIn("未变成正文占位", checklist)
        self.assertIn("未扩展成长清单", checklist)

        self.assertIn("修改模式只以用户最新版底稿", skill)
        self.assertIn("不自动回流为正文事实", skill)
        self.assertIn("旧稿、参考样文、过往材料和公开网页材料", workflow)
        self.assertIn("不把旧金额、旧主送、旧落款、旧政策口号或旧结论带回最新版正文", workflow)
        self.assertIn("修改模式是否以最新版底稿为主线", checklist)

        self.assertIn("成簇问题", skill)
        self.assertIn("不因单个正式词、单个转折或一次排比就硬清洗", skill)
        self.assertIn("审稿时看成簇问题", anti_ai)
        self.assertIn("单独出现 `高度重视`", anti_ai)
        self.assertIn("不足以判为 AI 味或套话", anti_ai)
        self.assertIn("保留公文必要的正式语气", anti_ai)
        self.assertIn("需说明资金使用必要性和预期效果", anti_ai)
        self.assertIn("相关负责人关注该事项", anti_ai)
        self.assertIn("不要无依据升级为 `领导高度关注`", anti_ai)
        self.assertIn("去 AI 味或语气审稿应匹配文体", official_style)
        self.assertIn("不为了显得像人写而加入第一人称", official_style)
        self.assertIn("单个正式词或单个转折不作为硬清洗理由", official_style)
        self.assertIn("不得为显得完整而补造未提供的牵头部门、责任部门、管理动作、整改动作、成果总结或跟踪督办安排", skill)
        self.assertIn("不为显得完整而补造牵头部门、责任部门、管理动作、整改动作、成果总结、跟踪督办、后续处理进展", workflow)
        self.assertIn("正式化新增事实", checklist)
        self.assertIn("正式化改写只压实原文已有事实", official_style)
        self.assertIn("口语来源不等于事实授权", official_style)
        for term in ["老板关心", "钱花得值", "马上要搞", "领导高度关注", "投入产出清晰", "推进较为紧迫", "按程序推进"]:
            self.assertIn(term, official_style)
        self.assertIn("不得自动升级", official_style)
        self.assertIn("审批态度留给用户确认", official_style)
        self.assertIn("用户要求“位置”时，优先逐项引用原文短语或句子", skill)
        self.assertIn("未只给笼统段落评价", checklist)
        self.assertIn("整体归纳可放在逐项意见之后", anti_ai)

        self.assertIn("定稿前高风险先查", checklist)
        self.assertIn("其余按文种/风险面", checklist)
        self.assertIn("不把它改成新的阻断流程", checklist)
        self.assertIn("不扩展成调查问卷或新确认流程", checklist)
        self.assertIn("只审不改场景", checklist)

        self.assertIn("## 函\n", genre_checklist)
        self.assertNotIn("## 函数", genre_checklist)
        self.assertIn("可参考顺序", genre_checklist)
        self.assertIn("不写成正文标签", genre_checklist)
        self.assertIn("不覆盖用户模板", genre_checklist)
        for section in ["通知", "请示", "报告", "方案", "申请", "函"]:
            self.assertIn(f"## {section}", genre_checklist)
        for term in ["目的或背景", "请批事项", "结论或总体情况", "责任分工", "申请主体", "商请或告知事项"]:
            self.assertIn(term, genre_checklist)

    def test_v148_anti_ai_borrowing_stays_soft_and_official(self) -> None:
        anti_ai = (ROOT / "chinese-official-writing" / "references" / "anti-ai-patterns.md").read_text(
            encoding="utf-8"
        )
        official_style = (ROOT / "chinese-official-writing" / "references" / "official-style.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("句群节奏和模板化痕迹", anti_ai)
        for term in ["句首重复", "连接词链", "句长同质化", "口号式收束", "清单堆叠替代论证"]:
            self.assertIn(term, anti_ai)
        self.assertIn("只作软性审稿项，不作为硬门禁", anti_ai)
        self.assertIn("公文去 AI 味不是聊天化", anti_ai)
        self.assertIn("不得为了显得“像人写”而加入第一人称、反问、口语插入", anti_ai)
        self.assertIn("保留公文骨架和用户模板", anti_ai)
        self.assertIn("用户只要求审稿时，仍输出位置、风险层级和修改建议", anti_ai)
        self.assertIn("不为了显得像人写而加入第一人称", official_style)
        self.assertIn("正式化改写只压实原文已有事实", official_style)

    def test_v150_genre_playbooks_keep_minimal_borrowing_boundaries(self) -> None:
        skill = (ROOT / "chinese-official-writing" / "SKILL.md").read_text(encoding="utf-8")
        playbooks = (ROOT / "chinese-official-writing" / "references" / "genre-playbooks.md").read_text(
            encoding="utf-8"
        )
        handling = (ROOT / "chinese-official-writing" / "references" / "handling-elements.md").read_text(
            encoding="utf-8"
        )
        anti_ai = (ROOT / "chinese-official-writing" / "references" / "anti-ai-patterns.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("references/genre-playbooks.md", skill)
        self.assertIn("## 目录", playbooks)
        for heading in [
            "## 会议纪要",
            "## 报告/情况说明",
            "## 函/复函/征求意见函",
            "## 工作总结/工作要点/周报",
            "## 调研报告/研究报告/可研报告/建设方案",
            "## 采购公告/审查材料",
            "## AI 算力与技术服务",
        ]:
            self.assertIn(heading, playbooks)
        for term in [
            "不复制社区模板正文",
            "不新增默认联网、API、Word/PDF 或脚本硬门禁",
            "用户已有模板和字段顺序优先",
            "只替换该字段内容，不把多字段合并成一句",
            "拆成独立字段行后不要保留行尾分号或造成 `。；`",
            "字段式周报保留字段和换行，不散文化、不合并字段",
            "字段式审查材料只改用户指定字段",
            "未给会议判断",
            "不自行补受众称呼",
            "不补服务单位责任",
            "责任或期限未给时留空或列为待确认",
            "普通采购公告不默认进入 AI 算力语境",
            "详细结构转读 `references/ai-compute-docs.md`",
        ]:
            self.assertIn(term, playbooks)
        self.assertIn("会议判断、受众称呼、角色分工、合同义务或服务单位责任", skill)
        self.assertIn("详细测算和参数转读 `ai-compute-docs.md`", handling)
        self.assertIn("专项结构和指标写法转读 `ai-compute-docs.md`", anti_ai)

    def test_weak_model_suggestion_boundaries_stay_soft(self) -> None:
        skill = (ROOT / "chinese-official-writing" / "SKILL.md").read_text(encoding="utf-8")
        workflow = (ROOT / "chinese-official-writing" / "references" / "workflow.md").read_text(
            encoding="utf-8"
        )
        playbooks = (ROOT / "chinese-official-writing" / "references" / "genre-playbooks.md").read_text(
            encoding="utf-8"
        )
        review = (ROOT / "chinese-official-writing" / "references" / "review-checklist.md").read_text(
            encoding="utf-8"
        )

        for text in [skill, workflow]:
            self.assertIn("考察、评估、建议、拟测试、考虑尝试或下一步设想", text)
            self.assertIn("不改写成已定实施方案、执行命令", text)
        self.assertIn("成本考察、成本评估", playbooks)
        self.assertIn("不自动改题为“调研报告”“考核说明”或“实施方案”", playbooks)
        self.assertIn("不写成已经确定的执行路线、责任命令或反馈时限", playbooks)
        self.assertIn("按 `workflow.md` 的事实映射式二次修改删掉未支持推断", playbooks)
        self.assertIn("每个实质句只保留“用户已给事实”和“直接概括”", workflow)
        self.assertIn("不用 Markdown `**` 加粗包装标签", skill)
        self.assertIn("未用 Markdown `**` 加粗包装标签", review)

    def test_proofreading_layer_stays_ai_writing_quality_only(self) -> None:
        skill = (ROOT / "chinese-official-writing" / "SKILL.md").read_text(encoding="utf-8")
        checklist = (ROOT / "chinese-official-writing" / "references" / "review-checklist.md").read_text(
            encoding="utf-8"
        )
        proofreading = (
            ROOT / "chinese-official-writing" / "references" / "proofreading-checklist.md"
        ).read_text(encoding="utf-8")

        self.assertIn("references/proofreading-checklist.md", skill)
        for text in [skill, checklist, proofreading]:
            self.assertIn("AI 写稿轻量校对", text)
            self.assertIn("引用保真", text)
            self.assertIn("稿内一致性", text)
        for term in [
            "不审核人类稿件事实真伪",
            "不核验新闻真实性",
            "不默认联网反查",
            "不新增模型、API、默认联网",
            "真实性核验不属于本技能的默认修正范围",
        ]:
            self.assertIn(term, proofreading)
        for term in [
            "领导讲话、古诗词、名言、政策原文",
            "同语境原样保留",
            "成语默认同语境保留",
            "低语境符合",
            "引用表述、出处和发布日期建议由用户按原始材料核实。",
            "不要改写成泛泛的 `请核实出处`",
        ]:
            self.assertTrue(term in proofreading or term in skill)
        for term in ["错别字错词", "的地得", "量词", "病句", "数据一致性", "逻辑一致性"]:
            self.assertIn(term, proofreading)
        self.assertIn("不改变 `prose_lint.py` 为深度语法纠错器", proofreading)

    def test_formalization_keeps_only_explicit_literal_boundaries_verbatim(self) -> None:
        skill = (ROOT / "chinese-official-writing" / "SKILL.md").read_text(encoding="utf-8")
        proofreading = (
            ROOT / "chinese-official-writing" / "references" / "proofreading-checklist.md"
        ).read_text(encoding="utf-8")
        style = (ROOT / "chinese-official-writing" / "references" / "official-style.md").read_text(
            encoding="utf-8"
        )

        for text in [skill, proofreading]:
            self.assertIn("普通叙述中的口语称谓和表达可以按正式文稿语体调整", text)
            self.assertIn("引号内、明确标注为原文/引语或要求逐字保留的内容按字面边界保留", text)
        self.assertIn("`我觉得`：可按语境改为", style)
        self.assertIn("`差不多`：可改为", style)

    def test_review_command_includes_interpreter_and_draft_path(self) -> None:
        review = (
            ROOT / "chinese-official-writing" / "references" / "final-review-layers.md"
        ).read_text(encoding="utf-8")

        self.assertIn("python scripts/prose_lint.py --format --structure <draft>", review)
        self.assertIn("`<draft>` 替换为待检查文件路径", review)

    def test_ai_dedupe_prompt_fix_guidance_is_documented(self) -> None:
        skill = (ROOT / "chinese-official-writing" / "SKILL.md").read_text(encoding="utf-8")
        openclaw_skill = (ROOT / "openclaw" / "skills" / "chinese_official_writing" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        sync_script = (ROOT / "tools" / "sync_adapters.py").read_text(encoding="utf-8")

        for text in [skill, openclaw_skill, sync_script]:
            self.assertIn("用户明示某些事项未提供", text)
            self.assertRegex(text, r"不(?:要)?扩展成调查问卷")
            self.assertIn("（成文日期待确认）", text)
            self.assertIn("不使用当前日期补落款", text)
        self.assertIn("去 AI 味、变换句式、拆分长句或调整清单结构", skill)
        self.assertIn("不得补写未给的解释、原因、影响范围、办理流程、责任人员、字段示例或整改动作", skill)
        self.assertIn("用户只给问题清单、任务清单或明确要求不新增事实时", skill)
        self.assertIn("不为显得自然或完整而补解释", skill)
        self.assertIn("不得补写未给解释、原因、影响、流程、人员、字段或整改动作", openclaw_skill)

    def test_openclaw_agent_rules_include_v140_routing_and_format_bridge(self) -> None:
        text = (ROOT / "openclaw" / "skills" / "chinese_official_writing" / "SKILL.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("任务模式", text)
        self.assertIn("references/workflow.md", text)
        self.assertIn("原文已有事实", text)
        self.assertIn("待确认补充", text)
        self.assertIn("数据冲突不得默认就高", text)
        self.assertIn("references/format-gbt9704.md", text)
        self.assertIn("正式 Word 输出前不得残留 Markdown", text)
        self.assertIn("包内 `references/`", text)
        self.assertNotIn("canonical `SKILL.md` 的“硬边界”段", text)

    def test_openclaw_skill_card_source_is_tracked_but_not_packaged_directly(self) -> None:
        source = (ROOT / "openclaw" / "skill-card.md").read_text(encoding="utf-8")
        packaged_path = ROOT / "openclaw" / "skills" / "chinese_official_writing" / "skill-card.md"

        self.assertIn("Known Risks and Mitigations", source)
        self.assertFalse(packaged_path.exists())

    def test_openclaw_skill_card_uses_absolute_links_and_key_genres(self) -> None:
        skill = (ROOT / "chinese-official-writing" / "SKILL.md").read_text(encoding="utf-8")
        source = (ROOT / "openclaw" / "skill-card.md").read_text(encoding="utf-8")

        self.assertNotIn("](references/", source)
        self.assertIn("https://github.com/gongyu0918-debug/chinese-official-writing-skill/blob/main/", source)
        for keyword in ["通知", "请示", "报告", "函", "复函", "批复", "方案", "说明", "申请", "采购公告", "审查材料"]:
            with self.subTest(keyword=keyword):
                self.assertIn(keyword, skill)
                self.assertIn(keyword, source)

    def test_readme_discloses_stub_eval_and_deepseek_column_sources(self) -> None:
        text = (ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("默认本地运行使用确定性本地草稿", text)
        self.assertIn("OFFICIAL_WRITING_AGENT_COMMAND", text)
        self.assertIn("风险数来自本地合成消融", text)
        self.assertIn("DeepSeek 列只记录 A/B 样稿生成数量和 C 轮评估是否形成有效结论", text)
        self.assertIn("文档自述噪音", text)
        self.assertIn("不等同于草稿正文缺陷", text)


if __name__ == "__main__":
    unittest.main()
