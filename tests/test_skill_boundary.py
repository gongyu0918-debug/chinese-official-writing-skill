from __future__ import annotations

from pathlib import Path
import json
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
OPENCLAW_SKILL_EXCLUDES = {
    "references/delivery-review-gate.md",
    "scripts/gate_stop_hook.py",
    "scripts/review_gate.py",
}


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
        readme = (ROOT / "README.md").read_text(encoding="utf-8")

        description = re.search(r"^description: (.+)$", text, re.M)
        self.assertIsNotNone(description)
        self.assertLessEqual(len(description.group(1)), 280)
        for keyword in ["申请", "请示", "报告", "通知", "通告", "意见", "决定", "函", "采购公告", "审查材料", "正式文本"]:
            self.assertIn(keyword, description.group(1))
        for excluded in ["营销", "社媒", "论文"]:
            self.assertIn(excluded, description.group(1))
        self.assertIn("当用户明确要求中文通知", text)
        self.assertIn("## 触发条件与边界", text)
        self.assertNotIn("批量语料生成", text)
        self.assertNotIn("规避人工审核", text)
        self.assertIn("批量语料生成", readme)
        self.assertIn("规避人工审核", readme)
        self.assertNotIn("本技能只提供写作和复核辅助", text)
        self.assertIn("没有用户提供依据时，不编造真实单位", text)
        self.assertIn("法律、财务、采购、审计、政策适用、保密审查和正式签发结论由相应责任主体确认", readme)

    def test_ai_compute_detail_is_loaded_from_specialty_reference(self) -> None:
        skill = (ROOT / "chinese-official-writing" / "SKILL.md").read_text(encoding="utf-8")
        specialty = (ROOT / "chinese-official-writing" / "references" / "ai-compute-docs.md").read_text(
            encoding="utf-8"
        )

        self.assertNotIn("起草算力、采购、租赁或服务器租赁材料时", skill)
        self.assertIn("references/ai-compute-docs.md", skill)
        self.assertIn("Token、并发、存储、带宽", specialty)
        self.assertIn("SLA", specialty)
        self.assertIn("验收", specialty)

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
                self.assertNotIn("批量语料生成", text)
                self.assertNotIn("规避人工审核", text)
                self.assertNotIn("本技能只提供写作和复核辅助", text)
                self.assertIn("没有用户提供依据时，不编造真实单位", text)

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
        self.assertIn("正式正文的小标题和段落标签按上文交付模式使用普通文本", text)
        self.assertIn("不用 Markdown `**` 加粗、`###`、代码块或 `---` 横线包装", text)

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

    def test_second_revision_fact_mapping_has_one_complete_entry_rule(self) -> None:
        text = (ROOT / "chinese-official-writing" / "SKILL.md").read_text(encoding="utf-8")

        self.assertEqual(text.count("事实映射式二次修改"), 1)
        for phrase in [
            "用户已给事实",
            "直接概括",
            "未支持推断",
            "只处理本轮修改",
            "不作为默认成稿前阶段",
            "不暂停交付",
            "不循环追问",
            "不输出映射表",
        ]:
            self.assertIn(phrase, text)

    def test_packaged_resource_mirrors_match_canonical_bytes(self) -> None:
        canonical = ROOT / "chinese-official-writing"
        targets = [
            (ROOT / "hermes" / "skills" / "chinese-official-writing", set()),
            (ROOT / "openclaw" / "skills" / "chinese_official_writing", OPENCLAW_SKILL_EXCLUDES),
        ]
        for target, excludes in targets:
            for folder in ["agents", "references", "scripts"]:
                canonical_folder = canonical / folder
                target_folder = target / folder
                with self.subTest(target=target, folder=folder):
                    files = [
                        relative
                        for relative in relative_files(canonical_folder)
                        if f"{folder}/{relative}" not in excludes
                    ]
                    self.assertEqual(relative_files(target_folder), files)
                    for relative in files:
                        self.assertEqual(
                            (target_folder / relative).read_bytes(),
                            (canonical_folder / relative).read_bytes(),
                            f"{target}/{folder}/{relative}",
                        )

    def test_openclaw_skill_excludes_codex_gate_runtime(self) -> None:
        packaged = ROOT / "openclaw" / "skills" / "chinese_official_writing"
        for relative in OPENCLAW_SKILL_EXCLUDES:
            self.assertFalse((packaged / relative).exists(), relative)
        self.assertTrue((packaged / "scripts" / "prose_lint.py").is_file())

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
        information_selection = (
            ROOT / "chinese-official-writing" / "references" / "information-selection.md"
        ).read_text(encoding="utf-8")
        self.assertIn("references/task-route-cards.md", skill)
        self.assertIn("材料稀疏", skill)
        self.assertIn("不新增事实", skill)
        for term in [
            "必须转读长 reference 的情况",
            "用户要求完整文种骨架",
            "800 字以上长文",
            "会议已形成决定、议定事项、结论或一致意见、责任分工或期限",
            "用户要求完整正式会议纪要",
            "任务属于可研、采购、AI 算力等专项论证",
            "先写可用正文",
            "不补工作组、问题清单、统一共识、治理流程、整改路径",
            "保持未决口径",
            "不写“会议强调”“会议认为”“会议决定”",
            "按已给内容和语气成稿",
            "不补“认真落实、严肃处理、记录留痕、无论有无异常",
            "Markdown 加粗、标题井号、横线等属于格式噪点",
            "用户没补齐上一轮信息时，仍执行本轮明确修改请求",
        ]:
            self.assertIn(term, cards)
        self.assertIn("信息进入正文、保持状态、省略或短列缺口，统一按 `information-selection.md` 处理", cards)
        self.assertIn("上一轮未补齐的缺口不阻断后续修改", information_selection)
        self.assertLess(len(cards.splitlines()), 80)

    def test_sparse_length_rule_keeps_fact_boundary_without_short_first_priority(self) -> None:
        relative_paths = [
            "chinese-official-writing/SKILL.md",
            "chinese-official-writing/references/workflow.md",
            "chinese-official-writing/references/genre-playbooks.md",
            "chinese-official-writing/references/task-route-cards.md",
        ]
        texts = [(ROOT / path).read_text(encoding="utf-8") for path in relative_paths]
        for text in texts:
            self.assertNotIn("宁可短写", text)
        self.assertIn("篇幅要求不改变事实边界", texts[0])
        self.assertIn("不为凑篇幅补主体、流程、产物、范围、责任或联系方式", texts[0])
        self.assertIn("基础底稿、基础清单、台账化、过程可追踪、统一督导流程", texts[0])
        self.assertNotIn("基础底稿、基础清单、台账化、过程可追踪、统一督导流程", texts[1])
        self.assertIn("按已给内容和语气成稿", texts[3])

    def test_light_route_is_terminal_until_an_explicit_escalation_condition(self) -> None:
        skill = (ROOT / "chinese-official-writing" / "SKILL.md").read_text(encoding="utf-8")
        cards = (ROOT / "chinese-official-writing" / "references" / "task-route-cards.md").read_text(
            encoding="utf-8"
        )
        playbooks = (ROOT / "chinese-official-writing" / "references" / "genre-playbooks.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("不因文种名称已知而自动预读下列全部长 reference", skill)
        self.assertIn("先确定创作、修改、只审不改等输出模式", skill)
        self.assertIn("未命中时不扩大轻量卡的适用范围", skill)
        self.assertIn("以本页结束 reference 路由", cards)
        self.assertIn("不因文种名称已知而继续预读", cards)
        self.assertIn("未命中时不扩大本页适用范围", cards)
        self.assertIn("任一事项已经形成", cards)
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

    def test_report_checklist_is_routed_as_an_atomic_leaf(self) -> None:
        skill = (ROOT / "chinese-official-writing" / "SKILL.md").read_text(encoding="utf-8")
        playbooks = (ROOT / "chinese-official-writing" / "references" / "genre-playbooks.md").read_text(
            encoding="utf-8"
        )
        common = (ROOT / "chinese-official-writing" / "references" / "genre-checklist.md").read_text(
            encoding="utf-8"
        )
        report = (ROOT / "chinese-official-writing" / "references" / "genre-checklist-report.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("references/genre-checklist-report.md", skill)
        self.assertIn("`genre-checklist-report.md`", playbooks)
        self.assertNotIn("## 报告\n", common)
        self.assertIn("使用事实性汇报语言", report)
        self.assertIn("专题报告先给结论", report)

    def test_institution_rules_have_a_dedicated_routed_leaf(self) -> None:
        skill = (ROOT / "chinese-official-writing" / "SKILL.md").read_text(encoding="utf-8")
        leaf = (
            ROOT
            / "chinese-official-writing"
            / "references"
            / "genre-playbook-institution-rules.md"
        ).read_text(encoding="utf-8")

        for keyword in ["制度", "规定", "办法", "管理办法", "实施细则", "操作规程"]:
            self.assertIn(keyword, skill.split("---", 2)[1])
        self.assertIn("references/genre-playbook-institution-rules.md", skill)
        self.assertIn("内容较短、事项单一时连续列条", leaf)
        self.assertIn("通知壳只写发布对象、执行要求和附件关系", leaf)
        self.assertIn("围绕实际操作顺序写清主体、触发条件、步骤、时限、结果和记录", leaf)
        self.assertIn("仅在材料明确时写入", leaf)
        self.assertIn("同时读取 `format-gbt9704.md`", leaf)

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
        self.assertIn("当前日期是否未被误用为维护时间", checklist)
        self.assertIn("[具体项目名称]", skill)
        self.assertIn("（成文日期待确认）", skill)
        self.assertEqual(skill.count("（成文日期待确认）"), 1)
        self.assertIn("交付前按上文硬边界清理占位", skill)
        self.assertIn("明示成文日期缺失、待确认或需另行确认时，不使用当前日期补落款", skill)
        self.assertIn("识别为正式报送结构缺口", skill)
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

    def test_openclaw_publish_command_uses_current_cli_and_safe_windows_flags(self) -> None:
        readme = (ROOT / "openclaw" / "README.md").read_text(encoding="utf-8")
        sync_script = (ROOT / "tools" / "sync_adapters.py").read_text(encoding="utf-8")

        self.assertIn("clawhub skill publish", readme)
        for flag in ["--slug=chinese-official-writing", "--name=中文公文写作", "--version="]:
            self.assertIn(flag, readme)
        self.assertIn("'--tags=chinese,official-document,writing,gongwen,ai-compute'", readme)
        self.assertNotIn(" --tags=chinese,official-document,writing,gongwen,ai-compute", readme)
        self.assertNotIn("clawhub publish ", readme)
        self.assertIn('f"--version={VERSION}"', sync_script)

    def test_readme_does_not_route_to_prompt_only_chatbot_repo(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("## 快速安装", readme)
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
        openclaw_publish_version = re.search(r"--version(?:\s+|=)(\d+\.\d+\.\d+)", openclaw_readme)
        marketplace_version = re.search(r"chinese-official-writing@(\d+\.\d+\.\d+)", marketplace_readme)
        skill_card_version = re.search(r"^(\d+\.\d+\.\d+) \(source: skill frontmatter and release candidate metadata", skill_card, re.M)

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

    def test_skill_packages_use_mit_0_while_repository_materials_use_mit(self) -> None:
        license_text = (ROOT / "LICENSE").read_text(encoding="utf-8")
        skill_license_text = (ROOT / "LICENSE-SKILL").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        sync_script = (ROOT / "tools" / "sync_adapters.py").read_text(encoding="utf-8")
        manifest = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))

        self.assertTrue(license_text.startswith("MIT License\n"))
        self.assertIn("subject to the\nfollowing conditions:", license_text)
        self.assertIn("The above copyright notice and this permission notice", license_text)
        self.assertTrue(skill_license_text.startswith("MIT No Attribution\n"))
        self.assertNotIn("The above copyright notice and this permission notice", skill_license_text)
        self.assertEqual(manifest["license"], "MIT-0")
        self.assertIn("## 开源许可", readme)
        self.assertIn("可直接安装的技能包", readme)
        self.assertIn("包外维护材料", readme)
        self.assertIn("MIT-0", readme)
        self.assertIn("[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)", readme)

        repository_skill_paths = [
            "chinese-official-writing/SKILL.md",
            "skills/chinese-official-writing/SKILL.md",
            ".agents/skills/chinese-official-writing/SKILL.md",
            ".qwen/skills/chinese-official-writing/SKILL.md",
            "hermes/skills/chinese-official-writing/SKILL.md",
        ]
        for relative_path in repository_skill_paths:
            text = (ROOT / relative_path).read_text(encoding="utf-8")
            self.assertIn("license: MIT-0\n", text, relative_path)

        openclaw_paths = [
            "openclaw/skills/chinese_official_writing/SKILL.md",
            "openclaw/skills/chinese_official_writing/README.md",
            "openclaw/marketplace-readme.md",
            "openclaw/skill-card.md",
        ]
        for relative_path in openclaw_paths:
            self.assertIn("MIT-0", (ROOT / relative_path).read_text(encoding="utf-8"), relative_path)

        self.assertIn('SKILL_LICENSE = "MIT-0"', sync_script)
        self.assertNotIn("OPENCLAW_LICENSE", sync_script)
        self.assertNotIn("redskill", sync_script.lower())

    def test_lint_strict_fail_on_stays_in_skill_not_public_readme(self) -> None:
        skill = (ROOT / "chinese-official-writing" / "SKILL.md").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("--strict --fail-on medium", skill)
        self.assertNotIn("--strict --fail-on medium", readme)

    def test_revision_workflow_forbids_new_unprovided_facts(self) -> None:
        skill = (ROOT / "chinese-official-writing" / "SKILL.md").read_text(encoding="utf-8")
        workflow = (ROOT / "chinese-official-writing" / "references" / "workflow.md").read_text(encoding="utf-8")
        checklist = (ROOT / "chinese-official-writing" / "references" / "review-checklist.md").read_text(
            encoding="utf-8"
        )
        information_selection = (
            ROOT / "chinese-official-writing" / "references" / "information-selection.md"
        ).read_text(encoding="utf-8")

        self.assertIn("不新增原文没有交代的活动、依据、数据、成效或责任安排", workflow)
        self.assertIn("不附事实边界自证", workflow)
        self.assertIn("只输出正文或改后稿时只交正文", information_selection)
        self.assertIn("在只输出正文模式下附加提示", checklist)
        self.assertIn("不附任何正文外说明或提示", skill)
        for text in [skill, workflow, checklist]:
            self.assertNotIn("未新增原文外事实", text)

    def test_staged_review_workflow_remains_intact(self) -> None:
        skill = (ROOT / "chinese-official-writing" / "SKILL.md").read_text(encoding="utf-8")
        workflow = (ROOT / "chinese-official-writing" / "references" / "workflow.md").read_text(encoding="utf-8")
        checklist = (ROOT / "chinese-official-writing" / "references" / "review-checklist.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("小段写完先审，小节写完再审，全文合并后做总审", skill)
        self.assertIn("每个小节完成后先复核", workflow)
        self.assertIn("全文合并后按 `final-review-layers.md` 做总审", workflow)
        self.assertIn("用于段落、小节和全文交付前核对", checklist)
        for rejected_rule in ["小节完成后不另行", "最多局部修订一次", "只执行一次"]:
            self.assertNotIn(rejected_rule, skill + workflow + checklist)

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
        information_selection = (
            ROOT / "chinese-official-writing" / "references" / "information-selection.md"
        ).read_text(encoding="utf-8")

        for text in [skill, workflow]:
            self.assertIn("任务模式路由", text)
            self.assertIn("起草", text)
            self.assertIn("改稿", text)
            self.assertIn("复核", text)
            self.assertIn("排版交付", text)
        self.assertIn("原文已有事实", workflow)
        self.assertIn("压实合并表达", workflow)
        self.assertIn("信息是否进入正文、按原状态承载、省略或作为实质缺口短列", workflow)
        self.assertIn("材料已给且与当前主旨相关的事实进入正文", information_selection)
        self.assertIn("视为实质缺口", information_selection)
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
        self.assertIn("references/format-gbt9704.md", skill)
        for text in [format_ref, checklist]:
            self.assertIn("正式交付前要素核对", text)
        for text in [skill, format_ref, checklist]:
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
        external_research = (
            ROOT / "chinese-official-writing" / "references" / "external-research.md"
        ).read_text(encoding="utf-8")
        elements = (ROOT / "chinese-official-writing" / "references" / "handling-elements.md").read_text(
            encoding="utf-8"
        )
        checklist = (ROOT / "chinese-official-writing" / "references" / "review-checklist.md").read_text(
            encoding="utf-8"
        )
        openclaw_skill = (ROOT / "openclaw" / "skills" / "chinese_official_writing" / "SKILL.md").read_text(
            encoding="utf-8"
        )

        for text in [skill, workflow, external_research, checklist, openclaw_skill]:
            self.assertIn("联网搜索", text)
        self.assertIn("联网核验", elements)
        self.assertIn("默认不外搜", skill)
        self.assertIn("普通起草、改稿和复核沿用入口的默认不外搜边界", workflow)
        for term in ["最新", "当前", "今日", "现行政策", "近期数据"]:
            self.assertIn(term, external_research)
        self.assertIn("搜索结果只作为来源参考", skill)
        self.assertIn("来源、日期或检索口径", skill)
        self.assertIn("发布日期、访问日期或检索口径", external_research)
        self.assertIn("来源冲突、无法核验或工具不可用", external_research)
        self.assertIn("默认不外搜补缺项", elements)
        self.assertIn("未因单位名称自动搜索单位公开样文", checklist)
        for text in [skill, elements, openclaw_skill]:
            self.assertIn("不因出现单位名称就搜索单位公开样文", text)
        self.assertIn("只出现单位名称，不触发搜索单位公开样文", external_research)
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
        genre_playbooks = (ROOT / "chinese-official-writing" / "references" / "genre-playbooks.md").read_text(
            encoding="utf-8"
        )
        anti_ai = (ROOT / "chinese-official-writing" / "references" / "anti-ai-patterns.md").read_text(
            encoding="utf-8"
        )
        format_ref = (ROOT / "chinese-official-writing" / "references" / "format-gbt9704.md").read_text(
            encoding="utf-8"
        )
        information_selection = (
            ROOT / "chinese-official-writing" / "references" / "information-selection.md"
        ).read_text(encoding="utf-8")
        external_research = (
            ROOT / "chinese-official-writing" / "references" / "external-research.md"
        ).read_text(encoding="utf-8")
        agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")

        self.assertIn("不使用泛称或占位符补齐未给要素", skill)
        self.assertIn("材料不足不作为中断成稿或连续追问的理由", workflow)
        self.assertIn("实质缺口只在输出模式允许时短列", checklist)
        self.assertIn("直接影响当前文种成立、请批事项或执行落地", information_selection)
        self.assertIn("新增字段没有用户提供值时只写字段名并留空", workflow)
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
        self.assertIn("来源名称、发布机关或发布主体、文号或链接", external_research)
        self.assertIn("搜索来源清单", checklist)
        self.assertIn("正文内容已经定稿", format_ref)
        self.assertIn("默认另存新版本", format_ref)
        self.assertIn("prompt/markdown", agents)
        self.assertIn("禁止直接誊抄代码、脚本、正则、模板库、大段 prompt、固定话术或模板正文", agents)
        for maintenance_gate in [
            "不新增重排版引擎",
            "不扩大默认联网",
            "不默认强制确认",
            "不破坏用户模板和字段式材料",
            "落地后必须和上一基线做消融",
        ]:
            self.assertIn(maintenance_gate, agents)
        for runtime_prompt in [skill, workflow, checklist, genre_checklist, genre_playbooks]:
            self.assertNotIn("社区技能", runtime_prompt)
            self.assertNotIn("prompt/markdown", runtime_prompt)
        self.assertNotIn("不复制社区模板正文", genre_playbooks)
        self.assertNotIn("联网和社区高频", checklist)

    def test_candidate_ac_anchors_fact_relations_to_explicit_material(self) -> None:
        skill = (ROOT / "chinese-official-writing" / "SKILL.md").read_text(encoding="utf-8")
        information_selection = (
            ROOT / "chinese-official-writing" / "references" / "information-selection.md"
        ).read_text(encoding="utf-8")

        self.assertIn(
            "保持主体、对象、数字、日期、状态和结论强度；事实之间的时间、因果和归属关系以材料明确关系为准",
            information_selection,
        )
        self.assertIn(
            "每段只服务一个论点，通常按“结论前置、事实支撑、判断归纳、事项落点”展开",
            skill,
        )

    def test_fact_sufficiency_guidance_is_soft_and_non_blocking(self) -> None:
        skill = (ROOT / "chinese-official-writing" / "SKILL.md").read_text(encoding="utf-8")
        workflow = (ROOT / "chinese-official-writing" / "references" / "workflow.md").read_text(encoding="utf-8")
        checklist = (ROOT / "chinese-official-writing" / "references" / "review-checklist.md").read_text(
            encoding="utf-8"
        )
        information_selection = (
            ROOT / "chinese-official-writing" / "references" / "information-selection.md"
        ).read_text(encoding="utf-8")

        self.assertNotIn("暂停确认", skill)
        self.assertNotIn("暂停确认", workflow)
        self.assertIn("先服从用户指定的输出模式，再按材料状态、事项关联性和办理必要性选择信息", skill)
        self.assertIn("起草、改稿、压缩或合稿时读取 `references/information-selection.md`", skill)
        self.assertIn("普通起草和顺稿不在正文前暂停或连续追问", workflow)
        self.assertIn("本文件不重复规定正文、文后提示和省略边界", workflow)
        self.assertIn("材料只给问题清单", skill)
        self.assertIn("正文列明已确认问题及其对象、数量和状态", skill)
        self.assertIn("信息选择是否符合 `information-selection.md`", checklist)
        for term in [
            "材料已给且与当前主旨相关的事实进入正文",
            "材料明确记载未定状态且与当前主旨相关时",
            "材料虽有记载但与当前主旨无关",
            "视为实质缺口",
            "只输出正文或改后稿时只交正文",
            "上一轮未补齐的缺口不阻断后续修改",
            "用户要求先确认时，再在正文前提出必要问题",
        ]:
            self.assertIn(term, information_selection)
        for legacy_duplicate in [
            "补充以下信息后，文章会更完整",
            "缺项说明放在正文外",
            "待确认事项仍是软提示",
            "未新增原文外事实",
        ]:
            self.assertNotIn(legacy_duplicate, skill + workflow + checklist)
        self.assertIn("事实强判断", checklist)
        self.assertIn("总体较好", checklist)
        runtime_prompts = [
            skill,
            workflow,
            (ROOT / "chinese-official-writing" / "references" / "official-style.md").read_text(
                encoding="utf-8"
            ),
        ]
        for runtime_prompt in runtime_prompts:
            self.assertNotIn("未发现重大隐患", runtime_prompt)
            self.assertNotIn("未影响核心业务", runtime_prompt)
            self.assertNotIn("能够正常开展", runtime_prompt)

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
        report_checklist = (
            ROOT / "chinese-official-writing" / "references" / "genre-checklist-report.md"
        ).read_text(encoding="utf-8")
        genre_checklist_coverage = genre_checklist + "\n" + report_checklist

        self.assertNotIn("正式交付前要素核对卡", skill)
        self.assertIn("references/format-gbt9704.md", skill)
        self.assertIn("标题用 2 号小标宋", skill)
        self.assertIn("页码用 4 号半角宋体并加一字线", skill)
        self.assertIn("正式交付前要素核对卡", format_ref)
        self.assertIn("不因缺这些正式要素阻断成稿", format_ref)
        self.assertIn("发文机关", format_ref)
        self.assertIn("印章或签署信息", format_ref)
        self.assertIn("4 号半角宋体阿拉伯数字", format_ref)
        self.assertIn("回行保持词意完整", format_ref)
        self.assertIn("不改写已定稿正文的用词、数字、标点和字符", format_ref)
        self.assertIn("优先只列用户点名缺项", format_ref)
        self.assertIn("其他正式要素按单位模板另行核对", format_ref)
        self.assertNotIn("核对卡优先只列这些点名要素", skill)
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
        self.assertIn("正式化只压实已给事实，不补未给的原因、效果、处置、责任、流程、结论或后续动作", skill)
        self.assertIn("正式化、顺稿和报告化不补牵头部门、责任部门、管理动作、整改动作、成果总结、跟踪督办或后续进展", workflow)
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
            self.assertIn(f"## {section}", genre_checklist_coverage)
        for term in ["目的或背景", "请批事项", "结论或总体情况", "责任分工", "申请主体", "商请或告知事项"]:
            self.assertIn(term, genre_checklist_coverage)

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

    def test_v1511_anti_ai_frequency_review_is_prompt_driven_and_local(self) -> None:
        anti_ai = (ROOT / "chinese-official-writing" / "references" / "anti-ai-patterns.md").read_text(
            encoding="utf-8"
        )
        final_review = (
            ROOT / "chinese-official-writing" / "references" / "final-review-layers.md"
        ).read_text(encoding="utf-8")

        for term in [
            "本项由模型通读全文后判断，不按固定词表自动替换",
            "无前文依据的否定",
            "虚假对比",
            "机械重复",
            "出现次数只用于发现线索",
            "单个正式词、单个句式或达到某个次数都不能直接判错",
            "事实、引用、术语、否定范围和论断强度",
            "只改确认有问题的句子及必要衔接",
            "未确认有问题的句子、真实比较和必要否定保持原样",
            "严格服从其指定的字段、顺序和格式",
            "未指定时仍按位置、风险层级和修改建议输出",
        ]:
            self.assertIn(term, anti_ai)
        self.assertIn("真实方案比较、法律政策要求、职责边界、风险提示", anti_ai)
        self.assertIn("不得把 `未`、`不`、`不得` 移到别的对象", anti_ai)
        self.assertIn("只语义重写确认有问题的局部", final_review)
        self.assertNotIn("自动批量替换", final_review)

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
            "不新增默认联网、API、Word/PDF 或脚本硬门禁",
            "用户已有模板和字段顺序优先",
            "只替换该字段内容，不把多字段合并成一句",
            "拆成独立字段行后不要保留行尾分号或造成 `。；`",
            "字段式周报保留字段和换行，不散文化、不合并字段",
            "字段式审查材料只改用户指定字段",
            "未给会议判断",
            "不自行补受众称呼",
            "不补服务单位责任",
            "责任或期限未给时不使用“按审核执行”“后续推进”等泛口径补齐",
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
        self.assertIn("不改写成已定实施方案、执行命令", skill)
        self.assertIn("不升级成已定实施方案、命令或已安排动作", workflow)
        self.assertIn("成本考察、成本评估", playbooks)
        self.assertIn("不自动改题为“调研报告”“考核说明”或“实施方案”", playbooks)
        self.assertIn("不写成已经确定的执行路线、责任命令或反馈时限", playbooks)
        self.assertIn("按 `workflow.md` 的事实映射式二次修改删掉未支持推断", playbooks)
        self.assertIn("每个实质句只保留用户已给事实和直接概括", workflow)
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
        self.assertIn("`我觉得`：材料只表达初步意见时", style)
        self.assertIn("`差不多`：可改为", style)

    def test_v1510_sentence_fixes_keep_sparse_and_field_tasks_fact_bounded(self) -> None:
        skill = (ROOT / "chinese-official-writing" / "SKILL.md").read_text(encoding="utf-8")
        style = (ROOT / "chinese-official-writing" / "references" / "official-style.md").read_text(
            encoding="utf-8"
        )
        anti_ai = (ROOT / "chinese-official-writing" / "references" / "anti-ai-patterns.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("按已给事实之间的关系简短成稿", skill)
        self.assertIn("缺少某一环节时，不补齐固定章节", skill)
        self.assertNotIn("已完成事项 -> 发现问题 -> 已组织协调", skill)
        self.assertIn("只有材料确有研究过程或事实依据时", style)
        self.assertIn("字段式底稿默认保留字段名、顺序和单元边界", anti_ai)
        self.assertIn("只有用户要求成篇正文且这些字段仅作为素材时", anti_ai)
        self.assertIn("不保留字段标签或机械转述字段名", anti_ai)

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
        information_selection = (
            ROOT / "chinese-official-writing" / "references" / "information-selection.md"
        ).read_text(encoding="utf-8")
        for text in [skill, openclaw_skill]:
            self.assertIn("用户点名禁止编造的字段写成正文中的“未提供”说明", text)
            self.assertIn("识别为正式报送结构缺口", text)
            self.assertIn("（成文日期待确认）", text)
            self.assertIn("不使用当前日期补落款", text)
        self.assertIn("用户要求先确认时，再在正文前提出必要问题", information_selection)
        self.assertIn("文后提示使用少量短项", information_selection)
        self.assertIn("去 AI 味、变换句式、拆分长句或调整清单结构", skill)
        self.assertIn("不得补写未给的解释、原因、影响范围、办理流程、责任人员、字段示例或整改动作", skill)
        self.assertIn("用户只给问题清单、任务清单或明确要求不新增事实时", skill)
        self.assertIn("不为显得自然或完整而补解释", skill)
        self.assertIn("不得补写未给的解释、原因、影响范围、办理流程、责任人员、字段示例或整改动作", openclaw_skill)

    def test_openclaw_agent_rules_include_v140_routing_and_format_bridge(self) -> None:
        canonical = (ROOT / "chinese-official-writing" / "SKILL.md").read_text(encoding="utf-8")
        text = (ROOT / "openclaw" / "skills" / "chinese_official_writing" / "SKILL.md").read_text(
            encoding="utf-8"
        )

        self.assertEqual(text.split("---", 2)[2].strip(), canonical.split("---", 2)[2].strip())
        self.assertIn("任务模式", text)
        self.assertIn("references/workflow.md", text)
        self.assertIn("references/information-selection.md", text)
        self.assertIn("按材料状态、事项关联性和办理必要性选择信息", text)
        self.assertIn("材料只给问题清单时，正文列明已确认问题及其对象、数量和状态", text)
        self.assertIn("稿内一致性风险", text)
        self.assertIn("references/format-gbt9704.md", text)
        format_ref = (
            ROOT / "openclaw" / "skills" / "chinese_official_writing" / "references" / "format-gbt9704.md"
        ).read_text(encoding="utf-8")
        self.assertIn("不得把 Markdown `**加粗**`", format_ref)
        self.assertIn("除非同时明确允许文后待确认、风险或核验提示", text)
        self.assertIn("缺失事实不补造，也不在正文中解释“未提供”", text)
        self.assertIn("用户同时明确允许某类文后提示时", text)
        self.assertIn("按任务渐进读取资料", text)

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

    def test_readme_summarizes_current_engineering_and_real_writing_evidence(self) -> None:
        text = (ROOT / "README.md").read_text(encoding="utf-8")

        for term in [
            "15 个真实用户式任务",
            "60 份成稿",
            "270 个任务",
            "540 段对比材料",
            "353/353",
            "108/108",
            "Promptfoo 20/20",
            "Candidate V 信息选择收口",
            "3 组同模型 A/B",
            "真实模型小样本评测",
            "渐进式路由",
            "路由 14/16",
            "1.5.14 为 8/8",
            "事实、文种与格式",
            "输出模式",
            "多轮与长稿",
            "同题独立写作节选",
            "无 Skill 成稿",
            "带 Skill 成稿",
            "并非同一随机 seed",
            "无 Skill 组使用 projectless 裸任务",
            "两名独立匿名评审均将带 Skill 稿排在无 Skill 稿之前",
            "readme-same-task-comparison-20260717.md",
            "原始任务 → 隔离 writer → 匿名映射 → 独立 verifier → 汇总报告 → 发布回执",
        ]:
            self.assertIn(term, text)
        self.assertNotIn("每类文种 10 次，共 270 个任务", text)
        self.assertNotIn("共 540 段对比样稿", text)
        self.assertNotIn("baseline-1.2.26", text)
        self.assertNotIn("常用验证命令", text)
        self.assertNotIn("python -B -m unittest discover", text)
        self.assertNotIn("### DeepSeek A/B/C", text)
        self.assertNotIn("无 Skill 样稿未进入该轮候选/基线双盲排序", text)
        for term in [
            "## 它怎么解决这些问题",
            "## 实现与技术栈",
            "## 核心能力",
            "## 适用范围",
            "## 快速安装",
            "Markdown-first",
            "中文 Markdown",
            "渐进式路由",
            "轻量审查层",
            "材料暂缺时正文优先完成",
            "scripts/prose_lint.py",
        ]:
            self.assertIn(term, text)
        for term in [
            "## 文稿检查脚本",
            "sync_adapters.py",
            "发布前检查",
            "复跑命令",
            "| 平台 | 目录 |",
        ]:
            self.assertNotIn(term, text)


if __name__ == "__main__":
    unittest.main()
