from __future__ import annotations

from pathlib import Path
import hashlib
import json
import re
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[2]
CANONICAL = ROOT / "chinese-official-writing"
HOOK_ADAPTERS = CANONICAL / "hooks" / "adapters"
OPTIONAL_GATE_FILES = {
    "hooks",
    "references/delivery-review-gate.md",
    "scripts/review_gate.py",
}
SKILLHUB_CLEAN_PACKAGE_EXCLUDES = {"agents/openai.yaml", "LICENSE"}
CURRENT_VERSION = "1.6.4"
PUBLISHED_VERSION = "1.6.4"


def relative_files(root: Path) -> list[str]:
    return sorted(
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc"
    )


def read_frontmatter(path: Path) -> dict[str, object]:
    text = path.read_text(encoding="utf-8")
    return yaml.safe_load(text.split("---", 2)[1])


def portable_tree_fingerprint(root: Path) -> str:
    digest = hashlib.sha256()
    for relative in sorted(relative_files(root), key=str.lower):
        payload = (root / relative).read_bytes().replace(b"\r\n", b"\n")
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(payload)
    return digest.hexdigest()


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
        self.assertNotIn("## 三层使用原则", text)
        self.assertNotIn("用户写明“材料只有”", text)
        self.assertIn("## 使用顺序", text)
        self.assertIn("先按用户指定的输出模式执行下文“硬边界”", text)
        for heading in ["## 硬边界", "## 质量建议", "## 参考资料"]:
            self.assertIn(heading, text)
        self.assertNotIn("模型训练", text)
        self.assertIn("没有用户提供依据时，不编造真实单位", text)
        self.assertIn("法律、财务、采购、审计、政策适用、保密审查和正式签发结论由相应责任主体确认", readme)

    def test_skill_frontmatter_keeps_only_discovery_fields_and_tags(self) -> None:
        paths = [
            CANONICAL / "SKILL.md",
            ROOT / "packages" / "agent-skills" / "skills" / "chinese-official-writing" / "SKILL.md",
            ROOT / "packages" / "qwen-code" / "skills" / "chinese-official-writing" / "SKILL.md",
            ROOT / "packages" / "hermes" / "skills" / "chinese-official-writing" / "SKILL.md",
        ]
        expected_tags = "chinese, official-document, writing, gongwen, ai-compute"

        for path in paths:
            with self.subTest(path=path):
                frontmatter = read_frontmatter(path)
                self.assertEqual(set(frontmatter), {"name", "description", "metadata"})
                self.assertEqual(frontmatter["metadata"], {"tags": expected_tags})
                self.assertNotIn("license", frontmatter)
                serialized = path.read_text(encoding="utf-8").split("---", 2)[1]
                for removed in ["compatible_agents", "qwen_code", "openclaw:", "hermes:", "install_personal"]:
                    self.assertNotIn(removed, serialized)

        for path in paths:
            self.assertEqual(read_frontmatter(path)["name"], "chinese-official-writing")

    def test_openclaw_github_package_is_current_mit_and_hook_free(self) -> None:
        package_root = ROOT / "packages" / "openclaw" / "skills" / "chinese_official_writing"
        skill = package_root / "SKILL.md"
        frontmatter = read_frontmatter(skill)

        self.assertEqual(frontmatter["name"], "chinese_official_writing")
        self.assertEqual(frontmatter["license"], "MIT")
        self.assertEqual(frontmatter["metadata"]["version"], CURRENT_VERSION)
        self.assertEqual(len(relative_files(package_root)), 31)
        self.assertEqual((package_root / "LICENSE").read_bytes(), (ROOT / "LICENSE").read_bytes())
        for forbidden in OPTIONAL_GATE_FILES | {"agents/openai.yaml", "README.md"}:
            self.assertFalse((package_root / forbidden).exists(), forbidden)

        sync_script = (ROOT / "maintenance" / "tools" / "sync_adapters.py").read_text(encoding="utf-8")
        self.assertIn('"openclaw": OPENCLAW_PACKAGE', sync_script)
        self.assertIn('"openclaw": OPTIONAL_GATE_FILES + ("agents/openai.yaml",)', sync_script)

    def test_ai_compute_detail_is_loaded_from_specialty_reference(self) -> None:
        skill = (ROOT / "chinese-official-writing" / "SKILL.md").read_text(encoding="utf-8")
        specialty = (ROOT / "chinese-official-writing" / "references" / "ai-compute-docs.md").read_text(
            encoding="utf-8"
        )

        self.assertNotIn("起草算力、采购、租赁或服务器租赁材料时", skill)
        self.assertIn("references/ai-compute-docs.md", skill)
        self.assertIn("AI 算力、GPU/服务器租赁、模型服务、智算中心、成本比较、SLA、安全或验收等专项直接读取", skill)
        self.assertIn("同时明确普通文种时，再按本表该文种的任务模式和加载条件叠加相应叶", skill)
        playbooks = (ROOT / "chinese-official-writing" / "references" / "genre-playbooks.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("Token、并发、存储、带宽", specialty)
        self.assertIn("## AI 算力与技术服务", specialty)
        self.assertEqual(specialty.count("## AI 算力与技术服务"), 1)
        self.assertIn("模型训练、推理、微调和多租户隔离需求", specialty)
        self.assertNotIn("## AI 算力与技术服务", playbooks)
        self.assertIn("详细结构见下文；本节只保留触发和边界", specialty)
        self.assertIn("SLA", specialty)
        self.assertIn("验收", specialty)

    def test_adapter_skill_copies_keep_boundaries(self) -> None:
        paths = [
            ROOT / "packages" / "agent-skills" / "skills" / "chinese-official-writing" / "SKILL.md",
            ROOT / "packages" / "qwen-code" / "skills" / "chinese-official-writing" / "SKILL.md",
            ROOT / "packages" / "hermes" / "skills" / "chinese-official-writing" / "SKILL.md",
            ROOT / "packages" / "openclaw" / "skills" / "chinese_official_writing" / "SKILL.md",
        ]

        for path in paths:
            with self.subTest(path=path):
                text = path.read_text(encoding="utf-8")
                self.assertNotIn("批量语料生成", text)
                self.assertNotIn("规避人工审核", text)
                self.assertNotIn("本技能只提供写作和复核辅助", text)
                self.assertNotIn("## 三层使用原则", text)
                self.assertNotIn("用户写明“材料只有”", text)
                self.assertIn("## 使用顺序", text)
                self.assertIn("没有用户提供依据时，不编造真实单位", text)

    def test_delivery_scope_rule_is_naturalized_across_current_skill_copies(self) -> None:
        expected = (
            "正式正文仅包含文种功能和用户要求需要的内容；制作版本、内部受众、操作方式、校验门禁、审核状态，"
            "以及与稿件事实无关的重复解释、括号式小字结论、制作说明、免责话术、写作边界和处理方法自述均省去，"
            "同一标题仅保留一次。正文外审稿意见单独处理；用户明确要求显示的声明、版本或保密标识，"
            "以及材料本身记载的业务事实，按用户要求和事实边界保留。"
        )
        legacy = "正式正文只保留文种功能和用户要求需要的内容"
        canonical = ROOT / "chinese-official-writing" / "SKILL.md"
        paths = [
            canonical,
            ROOT / "packages" / "agent-skills" / "skills" / "chinese-official-writing" / "SKILL.md",
            ROOT / "packages" / "qwen-code" / "skills" / "chinese-official-writing" / "SKILL.md",
            ROOT / "packages" / "hermes" / "skills" / "chinese-official-writing" / "SKILL.md",
        ]
        canonical_body = canonical.read_text(encoding="utf-8").split("---", 2)[2].strip()
        hook_route = (
            "\n\n用户明确要求处理交付门禁 Hook 时，读取 `hooks/README.md`。"
            "普通起草、改稿、压缩和复核不加载该页，也不自动启用 Hook。"
        )

        for path in paths:
            with self.subTest(path=path):
                text = path.read_text(encoding="utf-8")
                self.assertIn(expected, text)
                self.assertEqual(text.count(expected), 1)
                self.assertNotIn(legacy, text)
                body = text.split("---", 2)[2].strip()
                if "packages" in path.parts:
                    self.assertEqual(canonical_body.replace(hook_route, ""), body)
                else:
                    self.assertEqual(canonical_body, body)

    def test_entry_excludes_only_non_obvious_out_of_scope_tasks(self) -> None:
        text = (ROOT / "chinese-official-writing" / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn("英文写作、文学创作、营销软文、社交媒体文案、代码说明", text)
        self.assertNotIn("闲聊回复", text)
        self.assertNotIn("通用翻译", text)

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
        checklist = (ROOT / "chinese-official-writing" / "references" / "review-checklist.md").read_text(encoding="utf-8")

        self.assertNotIn("Markdown 格式残留", text)
        self.assertIn("不用 Markdown `**` 加粗、`###`、代码块或 `---` 横线包装", text)
        self.assertIn("Markdown 加粗、代码块、`###` 标题", checklist)

    def test_style_references_keep_precise_routes_without_common_error_catchall(self) -> None:
        text = (ROOT / "chinese-official-writing" / "SKILL.md").read_text(encoding="utf-8")

        self.assertNotIn("其他口语化、标题漂移、重复事项、格式噪点", text)
        self.assertNotIn("## 常见错误反例", text)
        self.assertIn("中文反例和修法见 `references/anti-ai-patterns.md`", text)
        self.assertIn("轻量语气替换见 `references/official-style.md`", text)
        self.assertIn("| `references/official-style.md` | 起草中 |", text)
        self.assertIn("| `references/anti-ai-patterns.md` | 复核时 |", text)

    def test_static_hook_adapters_do_not_duplicate_full_skill(self) -> None:
        for host in ("codex", "codebuddy", "claude-code"):
            with self.subTest(host=host):
                adapter = HOOK_ADAPTERS / host
                self.assertTrue((adapter / "README.md").is_file())
                self.assertTrue((adapter / "manifest.json").is_file())
                self.assertTrue((adapter / "hooks.json").is_file())
                self.assertFalse((adapter / "skills").exists())

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
            (ROOT / "packages" / "agent-skills" / "skills" / "chinese-official-writing", OPTIONAL_GATE_FILES),
            (ROOT / "packages" / "qwen-code" / "skills" / "chinese-official-writing", OPTIONAL_GATE_FILES),
            (ROOT / "packages" / "hermes" / "skills" / "chinese-official-writing", OPTIONAL_GATE_FILES),
        ]
        for target, excludes in targets:
            for folder in ["agents", "hooks", "references", "scripts"]:
                canonical_folder = canonical / folder
                target_folder = target / folder
                with self.subTest(target=target, folder=folder):
                    files = (
                        []
                        if folder in excludes
                        else [
                            relative
                            for relative in relative_files(canonical_folder)
                            if f"{folder}/{relative}" not in excludes
                        ]
                    )
                    self.assertEqual(relative_files(target_folder), files)
                    for relative in files:
                        self.assertEqual(
                            (target_folder / relative).read_bytes(),
                            (canonical_folder / relative).read_bytes(),
                            f"{target}/{folder}/{relative}",
                        )

    def test_only_canonical_keeps_gate_sources(self) -> None:
        gate_files = {
            "hooks/README.md",
            "hooks/host-capabilities.json",
            "hooks/core/gate_stop_hook.py",
            "hooks/adapters/host_gate_adapter.py",
            "references/delivery-review-gate.md",
            "scripts/review_gate.py",
        }
        for relative in gate_files:
            self.assertTrue((CANONICAL / relative).is_file(), relative)

        excluded_surfaces = [
            ROOT / "packages" / "agent-skills" / "skills" / "chinese-official-writing",
            ROOT / "packages" / "qwen-code" / "skills" / "chinese-official-writing",
            ROOT / "packages" / "hermes" / "skills" / "chinese-official-writing",
            ROOT / "packages" / "openclaw" / "skills" / "chinese_official_writing",
        ]
        for packaged in excluded_surfaces:
            with self.subTest(packaged=packaged):
                for relative in OPTIONAL_GATE_FILES:
                    self.assertFalse((packaged / relative).exists(), relative)
                self.assertTrue((packaged / "scripts" / "prose_lint.py").is_file())

    def test_skillhub_clean_package_allowlist_has_expected_file_count(self) -> None:
        canonical = ROOT / "chinese-official-writing"
        package_allowlist = [
            relative
            for relative in relative_files(canonical)
            if relative not in SKILLHUB_CLEAN_PACKAGE_EXCLUDES
        ]

        self.assertGreater(len(package_allowlist), 44)
        self.assertNotIn("agents/openai.yaml", package_allowlist)
        self.assertNotIn("LICENSE", package_allowlist)
        for relative in ("hooks/README.md", "hooks/host-capabilities.json", "hooks/core/gate_stop_hook.py"):
            self.assertIn(relative, package_allowlist)
        self.assertTrue(any(relative.startswith("hooks/adapters/") for relative in package_allowlist))

    def test_codex_plugin_version_and_hook_path_track_canonical_skill(self) -> None:
        sync_script = (ROOT / "maintenance" / "tools" / "sync_adapters.py").read_text(encoding="utf-8")
        sync_version = re.search(r'^VERSION = "([^"]+)"$', sync_script, re.M)
        self.assertIsNotNone(sync_version)
        manifest = json.loads((HOOK_ADAPTERS / "codex" / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["version"], sync_version.group(1))

        config = json.loads((HOOK_ADAPTERS / "codex" / "hooks.json").read_text(encoding="utf-8"))
        commands = [
            handler[key]
            for groups in config["hooks"].values()
            for group in groups
            for handler in group["hooks"]
            for key in ("command", "commandWindows")
        ]
        self.assertTrue(commands)
        self.assertTrue(
            all(
                "host_gate_adapter.py" in command
                and "skills/chinese-official-writing" not in command
                and "'skills','chinese-official-writing'" not in command
                for command in commands
            )
        )

    def test_reference_loading_table_keeps_progressive_disclosure(self) -> None:
        text = (ROOT / "chinese-official-writing" / "SKILL.md").read_text(encoding="utf-8")
        core = text.split("## 核心流程", 1)[1].split("## 硬边界", 1)[0]

        self.assertIn("按任务渐进读取资料，不要一次性加载全部文件", text)
        self.assertIn("| 文件 | 阶段 | 加载条件 |", text)
        self.assertIn("`references/task-route-cards.md` | 起草前/改稿前", text)
        self.assertIn("低上下文局部修改", text)
        self.assertIn("`references/genre-playbook-minutes.md` | 按文种选读", text)
        self.assertIn("`references/genre-playbook-plan-construction.md` | 按文种选读", text)
        self.assertIn("`references/genre-checklist-feasibility-review.md` | 按文种选读", text)
        self.assertIn("`references/genre-playbooks.md` | 按文种选读", text)
        self.assertIn("`references/ai-compute-docs.md` | 专项选读", text)
        self.assertIn("AI 算力、GPU/服务器租赁、模型服务、智算中心、成本比较、SLA、安全或验收等专项直接读取", text)
        self.assertIn("命中 `references/task-route-cards.md` 且卡片能够覆盖任务时", core)
        self.assertIn("由卡片完成，不再读取长 reference", core)
        self.assertIn("未命中、命中转读条件或卡片不能覆盖时", core)
        self.assertIn("一次只加载实际命中的表项", core)
        for duplicated_leaf in [
            "references/genre-playbook-minutes.md",
            "references/genre-checklist-report.md",
            "references/genre-playbook-request.md",
            "references/genre-checklist-request.md",
            "references/genre-playbook-correspondence.md",
            "references/genre-playbook-plan-construction.md",
            "references/genre-playbooks.md",
            "references/ai-compute-docs.md",
        ]:
            self.assertNotIn(duplicated_leaf, core)

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
        information_selection = (
            ROOT / "chinese-official-writing" / "references" / "information-selection.md"
        ).read_text(encoding="utf-8")
        for text in texts:
            self.assertNotIn("宁可短写", text)
        self.assertNotIn("篇幅要求不改变事实边界", texts[0])
        self.assertNotIn("基础底稿、基础清单、台账化、过程可追踪、统一督导流程", texts[0])
        self.assertIn("篇幅目标在上述信息范围内完成", information_selection)
        self.assertIn("不增加材料外的主体、流程、产物、范围、责任或联系方式", information_selection)
        self.assertIn("也不以同义概念补回", information_selection)
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
        self.assertIn("先确定起草、改稿、复核（默认只审不改）、排版交付模式", skill)
        self.assertIn("未命中时不扩大轻量卡的适用范围", skill)
        self.assertIn("以本页结束 reference 路由", cards)
        self.assertIn("不因文种名称已知而继续预读", cards)
        self.assertIn("未命中时不扩大本页适用范围", cards)
        self.assertIn("任一事项已经形成", cards)
        self.assertIn("每个文种小节都是可从 `SKILL.md` 直接进入的叶子路由", playbooks)
        self.assertIn("不要求先完整读取 `workflow.md` 或 `genre-routing.md`", playbooks)
        self.assertIn("不要把每节末尾的“补充读取”当成固定加载清单", playbooks)

    def test_workflow_sparse_line_relief_keeps_carriers_and_route_graph(self) -> None:
        skill = (ROOT / "chinese-official-writing" / "SKILL.md").read_text(encoding="utf-8")
        workflow = (ROOT / "chinese-official-writing" / "references" / "workflow.md").read_text(
            encoding="utf-8"
        )
        cards = (ROOT / "chinese-official-writing" / "references" / "task-route-cards.md").read_text(
            encoding="utf-8"
        )
        report = (
            ROOT / "chinese-official-writing" / "references" / "genre-checklist-report.md"
        ).read_text(encoding="utf-8")

        self.assertNotIn(
            "材料稀疏型通报或情况说明只按已给事实之间的关系成稿；缺少某一环节时不补固定章节。",
            workflow,
        )
        self.assertIn(
            "材料稀疏型通报或情况说明按已给事实之间的关系简短成稿；缺少某一环节时，不补齐固定章节。",
            skill,
        )
        self.assertIn("以本页结束 reference 路由", cards)
        self.assertIn("不用泛称、占位或未给流程补齐骨架", cards)
        self.assertIn("材料未给某一环节时，不为补齐骨架硬写", report)

        core = skill.split("## 核心流程", 1)[1].split("## 硬边界", 1)[0]
        self.assertIn("命中 `references/task-route-cards.md` 且卡片能够覆盖任务时", core)
        self.assertIn("由卡片完成，不再读取长 reference", core)
        self.assertIn("`references/workflow.md` | 起草前 | 长文、复杂改稿、多材料合稿", skill)
        self.assertIn(
            "`references/genre-checklist-report.md` | 按文种选读 | 报告、情况报告或情况说明需要常规或完整骨架",
            skill,
        )
        self.assertIn("材料稀疏任务仍按既有轻量路由处理，不重复加载本叶", report)

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
            self.assertIn("发送人", text)
            self.assertIn("接收方", text)
        self.assertIn("关键名词和结构标签一般保留原词", skill)
        for text in [workflow, checklist]:
            self.assertIn("原因分析", text)
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

    def test_genre_authority_uses_the_defined_routing_source(self) -> None:
        skill = (ROOT / "chinese-official-writing" / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn("文种判断以官方规范和 `references/genre-routing.md` 为准", skill)
        self.assertNotIn("社区模板不得替代文种功能", skill)

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
        self.assertIn("需要常规或完整骨架、专项写法或细查文种功能和结构时直接读取", skill)
        self.assertNotIn("`genre-checklist-report.md`", playbooks)
        self.assertNotIn("## 报告/情况说明", playbooks)
        self.assertNotIn("## 报告\n", common)
        self.assertIn("## 使用方式", report)
        self.assertIn("## 报告/情况说明", report)
        self.assertIn("使用事实性汇报语言", report)
        self.assertIn("专题报告先给结论", report)
        self.assertNotIn("`genre-checklist-report.md`", report)

        for phrase in [
            "报告事项和范围",
            "使用/体验/评估报告或成本考察",
            "报告不写审批请求",
            "材料只说接口、系统、页面异常时",
        ]:
            self.assertIn(phrase, report)

    def test_feasibility_review_checklist_is_an_atomic_leaf(self) -> None:
        skill = (ROOT / "chinese-official-writing" / "SKILL.md").read_text(encoding="utf-8")
        common = (
            ROOT / "chinese-official-writing" / "references" / "genre-checklist.md"
        ).read_text(encoding="utf-8")
        review = (
            ROOT
            / "chinese-official-writing"
            / "references"
            / "genre-checklist-feasibility-review.md"
        ).read_text(encoding="utf-8")

        self.assertIn("references/genre-checklist-feasibility-review.md", skill)
        self.assertIn("只审或细查可研、可行性研究报告", skill)
        self.assertNotIn("## 可行性研究报告\n", common)
        self.assertIn("## 可行性研究报告\n", review)
        self.assertIn("区分实际数据、测算数据和假设", review)
        self.assertIn("起草、改写或审后改写仍按既有可研 playbook", review)
        self.assertIn("主张本身及相互之间的内部一致性", review)
        self.assertNotIn("效果主张之间的内部一致性", review)

    def test_minutes_playbook_is_routed_as_an_atomic_leaf(self) -> None:
        skill = (ROOT / "chinese-official-writing" / "SKILL.md").read_text(encoding="utf-8")
        cards = (
            ROOT / "chinese-official-writing" / "references" / "task-route-cards.md"
        ).read_text(encoding="utf-8")
        common = (
            ROOT / "chinese-official-writing" / "references" / "genre-playbooks.md"
        ).read_text(encoding="utf-8")
        minutes = (
            ROOT / "chinese-official-writing" / "references" / "genre-playbook-minutes.md"
        ).read_text(encoding="utf-8")

        self.assertIn("references/genre-playbook-minutes.md", skill)
        self.assertIn("references/genre-playbook-minutes.md", cards)
        self.assertNotIn("## 会议纪要\n", common)
        self.assertIn("## 会议纪要\n", minutes)
        self.assertIn("重点是议定事项、责任、期限和后续动作", minutes)
        self.assertIn("不补写“会议认为”“会议强调”", minutes)

    def test_request_playbook_is_routed_as_an_atomic_leaf(self) -> None:
        skill = (ROOT / "chinese-official-writing" / "SKILL.md").read_text(encoding="utf-8")
        common = (
            ROOT / "chinese-official-writing" / "references" / "genre-playbooks.md"
        ).read_text(encoding="utf-8")
        request = (
            ROOT / "chinese-official-writing" / "references" / "genre-playbook-request.md"
        ).read_text(encoding="utf-8")

        self.assertIn("references/genre-playbook-request.md", skill)
        self.assertIn("请示、申请需要常规或完整骨架时直接读取", skill)
        self.assertNotIn("## 请示/申请\n", common)
        self.assertNotIn("- 请示/申请\n", common)
        self.assertIn("## 请示/申请\n", request)
        self.assertIn("请示一文一事", request)
        self.assertIn("主送机关、发文或申请单位、成文日期属于正式报送结构要素", request)
        self.assertIn("`argument-chains.md` 的请示和请批附件", request)

    def test_plan_construction_playbook_is_routed_as_an_atomic_leaf(self) -> None:
        skill = (ROOT / "chinese-official-writing" / "SKILL.md").read_text(encoding="utf-8")
        common = (
            ROOT / "chinese-official-writing" / "references" / "genre-playbooks.md"
        ).read_text(encoding="utf-8")
        leaf = (
            ROOT
            / "chinese-official-writing"
            / "references"
            / "genre-playbook-plan-construction.md"
        ).read_text(encoding="utf-8")
        research_skeleton = (
            "对象和范围 -> 事实、数据、样本 -> 发现和问题 -> 原因或方案比较 -> "
            "建议/可行性/建设内容 -> 条件和风险"
        )
        plan_skeleton = (
            "以目标、主要任务和实施路径为主线，责任、进度、保障、验收与风险控制"
            "按材料和用户模板落位"
        )

        self.assertIn("references/genre-playbook-plan-construction.md", skill)
        self.assertIn("方案、实施方案或建设方案需要常规或完整骨架时直接读取", skill)
        self.assertNotIn("## 调研报告/研究报告/可研报告/建设方案\n", common)
        self.assertIn("## 调研报告/研究报告/可研报告\n", common)
        self.assertIn("## 方案/实施方案/建设方案\n", leaf)
        self.assertIn(research_skeleton, common)
        self.assertNotIn(research_skeleton, leaf)
        self.assertIn(plan_skeleton, leaf)
        self.assertNotIn("建设方案先核对目标、范围、任务、进度、责任和验收", common)
        self.assertIn("建设方案先核对目标、范围、任务、进度、责任和验收", leaf)
        for forbidden in ["计划段展开", "计划补写", "篇幅", "字数", "P0"]:
            self.assertNotIn(forbidden, leaf)

    def test_request_review_checklist_is_routed_as_an_atomic_leaf(self) -> None:
        skill = (ROOT / "chinese-official-writing" / "SKILL.md").read_text(encoding="utf-8")
        common = (
            ROOT / "chinese-official-writing" / "references" / "genre-checklist.md"
        ).read_text(encoding="utf-8")
        draft = (
            ROOT / "chinese-official-writing" / "references" / "genre-playbook-request.md"
        ).read_text(encoding="utf-8")
        review = (
            ROOT / "chinese-official-writing" / "references" / "genre-checklist-request.md"
        ).read_text(encoding="utf-8")

        self.assertIn("references/genre-checklist-request.md", skill)
        self.assertIn("只审或细查请示、申请", skill)
        self.assertNotIn("## 请示\n", common)
        self.assertNotIn("## 申请\n", common)
        self.assertIn("## 请示\n", review)
        self.assertIn("## 申请\n", review)
        self.assertIn("一文一事，开头或前部明确请批事项", review)
        self.assertIn("两行标题", review)
        self.assertIn("不要只因出现 `妥否，请批示` 就判定为请示", review)
        self.assertNotIn("两行标题", draft)
        self.assertNotIn("genre-checklist-request.md", draft)

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

    def test_news_message_has_six_aliases_and_a_thin_fact_boundary_leaf(self) -> None:
        skill = (ROOT / "chinese-official-writing" / "SKILL.md").read_text(encoding="utf-8")
        leaf = (
            ROOT
            / "chinese-official-writing"
            / "references"
            / "genre-playbook-news-message.md"
        ).read_text(encoding="utf-8")

        aliases = ["新闻稿", "新闻消息", "快讯", "活动报道", "活动新闻稿", "新闻通稿"]
        frontmatter = skill.split("---", 2)[1]
        for alias in aliases:
            self.assertIn(alias, frontmatter)
        self.assertIn("references/genre-playbook-news-message.md", skill)
        self.assertIn("不因材料中偶然出现", skill)
        for rule in [
            "标题和导语先交代最重要的已给事实",
            "材料不足以安全达到下限时，优先交付事实完整的短消息",
            "材料明示且有新闻价值的单个未决状态应保留",
            "推断不得改变事实对象或范围",
            "活动新闻只展开材料已经给出的活动设置、参与主体、现场动作和统计状态",
            "合并成一至两个自然段",
            "普通消息不自行补“这不代表、这不表示、这不构成”",
        ]:
            self.assertIn(rule, leaf)
        self.assertNotIn("缺少某一项时直接省略", leaf)
        self.assertNotIn("流程清单", leaf)

    def test_news_commentary_has_three_precise_aliases_and_a_direct_leaf(self) -> None:
        skill_paths = [
            ROOT / "chinese-official-writing" / "SKILL.md",
            ROOT / "packages" / "agent-skills" / "skills" / "chinese-official-writing" / "SKILL.md",
            ROOT / "packages" / "qwen-code" / "skills" / "chinese-official-writing" / "SKILL.md",
            ROOT / "packages" / "hermes" / "skills" / "chinese-official-writing" / "SKILL.md",
            ROOT / "packages" / "openclaw" / "skills" / "chinese_official_writing" / "SKILL.md",
        ]
        reference = "references/genre-playbook-news-commentary.md"

        for path in skill_paths:
            with self.subTest(path=path):
                skill = path.read_text(encoding="utf-8")
                frontmatter = skill.split("---", 2)[1]
                for alias in ["新闻评论", "时评", "评论员文章"]:
                    self.assertIn(alias, frontmatter)
                self.assertNotIn("评论类", frontmatter)
                self.assertNotIn("各类评论", frontmatter)
                self.assertIn(reference, skill)
                self.assertIn(
                    "普通公文内容中出现这些词语，不改变原定文种",
                    skill,
                )
                self.assertIn(
                    "除用户明确要求撰写新闻评论、时评或评论员文章外",
                    skill,
                )

    def test_news_commentary_leaf_is_bounded_and_non_templated(self) -> None:
        leaf = (
            ROOT
            / "chinese-official-writing"
            / "references"
            / "genre-playbook-news-commentary.md"
        ).read_text(encoding="utf-8")

        for phrase in [
            "完整时间锚",
            "目标字数的约值",
            "每段推进不同论点",
            "直接判断、事实解释和自然衔接",
            "材料事实与评论推演",
            "公共价值、利弊和成立条件",
            "具体政策、数据、具名责任、期限或承诺",
            "自然结束",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, leaf)
        self.assertNotIn("示例：", leaf)
        self.assertNotIn("模板", leaf)
        self.assertNotIn("首先", leaf)
        self.assertNotIn("其次", leaf)

    def test_news_genres_are_defined_in_authoritative_routing(self) -> None:
        routing = (
            ROOT / "chinese-official-writing" / "references" / "genre-routing.md"
        ).read_text(encoding="utf-8")

        self.assertIn("### 新闻类文本", routing)
        self.assertIn("新闻消息：面向公开传播已发生事实", routing)
        self.assertIn("会议活动报道保持消息功能", routing)
        self.assertIn("新闻评论：围绕已给事实或公共议题提出观点并展开论证", routing)
        self.assertIn("评论判断保持为观点", routing)
        self.assertIn("机关决定、责任分工和执行安排以材料为准", routing)

    def test_format_reference_clarifies_document_number_brackets(self) -> None:
        text = (ROOT / "chinese-official-writing" / "references" / "format-gbt9704.md").read_text(encoding="utf-8")

        self.assertIn("年份使用六角括号 `〔〕`", text)
        self.assertIn("不要用方括号 `[]` 或圆括号 `()` 替代", text)

    def test_final_drafts_must_not_keep_unfinished_placeholders(self) -> None:
        skill = (ROOT / "chinese-official-writing" / "SKILL.md").read_text(encoding="utf-8")
        elements = (ROOT / "chinese-official-writing" / "references" / "handling-elements.md").read_text(encoding="utf-8")
        final_review = (
            ROOT / "chinese-official-writing" / "references" / "final-review-layers.md"
        ).read_text(encoding="utf-8")
        checklist = (ROOT / "chinese-official-writing" / "references" / "review-checklist.md").read_text(encoding="utf-8")

        for text in [skill, elements, final_review, checklist]:
            self.assertTrue("最终正文" in text or "交付正文" in text)
            self.assertIn("未完成占位", text)

        self.assertIn("最终正文不得残留未完成占位", skill)
        self.assertIn("当前日期不得替代维护时间", skill)
        self.assertIn("当前日期只可用于草稿落款", elements)
        self.assertIn("当前日期是否未被误用为维护时间", checklist)
        for example in [
            "〔签发日期〕",
            "〔会议时间〕",
            "[具体项目名称]",
            "XXXX万元",
            "YYYY年MM月DD日",
            "（签发日期）",
            "（成文日期待确认）",
        ]:
            with self.subTest(example=example):
                self.assertNotIn(example, skill)
                self.assertIn(example, elements)
                self.assertIn(example, final_review)
        self.assertNotIn("交付前按上文硬边界清理占位", skill)
        self.assertIn("明示成文日期缺失、待确认或需另行确认时，不使用当前日期补落款", skill)
        self.assertIn("识别为正式报送结构缺口", skill)
        self.assertIn("不使用当前日期补落款", skill)
        self.assertIn("YYYY年MM月DD日", elements)

    def test_clawhub_v160_page_copy_is_kept_only_as_internal_history(self) -> None:
        snapshot = ROOT / "maintenance" / "docs" / "platform-snapshots" / "clawhub-v1.6.0"
        marketplace = (snapshot / "marketplace-readme.md").read_text(encoding="utf-8")
        skill_card = (snapshot / "skill-card.md").read_text(encoding="utf-8")

        self.assertIn("chinese-official-writing@1.6.0", marketplace)
        self.assertIn("MIT-0", skill_card)
        self.assertFalse((ROOT / "packages" / "openclaw" / "marketplace-readme.md").exists())
        self.assertFalse((ROOT / "packages" / "openclaw" / "skill-card.md").exists())

    def test_openclaw_bundle_readme_is_current_and_contains_no_publish_command(self) -> None:
        readme = (ROOT / "packages" / "openclaw" / "README.md").read_text(encoding="utf-8")

        self.assertIn("当前 GitHub 版本为 `1.6.4`", readme)
        self.assertIn("MIT", readme)
        self.assertIn(r"python .\maintenance\tools\sync_adapters.py", readme)
        self.assertIn("packages/openclaw/", readme)
        self.assertNotIn("clawhub skill publish", readme)
        self.assertNotIn("clawhub publish ", readme)

    def test_readme_does_not_route_to_prompt_only_chatbot_repo(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("## 快速安装", readme)
        self.assertNotIn("## 安装 Prompt", readme)
        self.assertNotIn("轻量纯提示词版本", readme)
        self.assertNotIn("chinese-official-writing-chatbot-prompt", readme)

    def test_readme_documents_domestic_agent_install_paths(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        sync_script = (ROOT / "maintenance" / "tools" / "sync_adapters.py").read_text(encoding="utf-8")

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
            "packages/qwen-code/",
            "chinese-official-writing/hooks/adapters/",
            "packages/agent-skills/",
        ]:
            self.assertIn(path, readme)
        self.assertIn("npx skills add https://github.com/gongyu0918-debug/chinese-official-writing-skill --skill chinese-official-writing", readme)
        for mode in ['"qwen"']:
            self.assertIn(mode, sync_script)
        self.assertNotIn('"minimax"', sync_script)
        self.assertNotIn('"glm"', sync_script)
        frontmatter = read_frontmatter(ROOT / "chinese-official-writing" / "SKILL.md")
        self.assertEqual(set(frontmatter), {"name", "description", "metadata"})

    def test_claude_plugin_manifest_version_matches_skill_and_sync_script(self) -> None:
        manifest = json.loads((HOOK_ADAPTERS / "claude-code" / "manifest.json").read_text(encoding="utf-8"))
        sync_script = (ROOT / "maintenance" / "tools" / "sync_adapters.py").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        openclaw_readme = (ROOT / "packages" / "openclaw" / "README.md").read_text(encoding="utf-8")
        openclaw_skill = read_frontmatter(
            ROOT / "packages" / "openclaw" / "skills" / "chinese_official_writing" / "SKILL.md"
        )

        sync_version = re.search(r'VERSION = "([^"]+)"', sync_script)
        readme_version = re.search(r"chinese-official-writing@(\d+\.\d+\.\d+)", readme)
        openclaw_version = re.search(r"当前 GitHub 版本为 `(\d+\.\d+\.\d+)`", openclaw_readme)

        self.assertIsNotNone(sync_version)
        self.assertIsNotNone(readme_version)
        self.assertIsNotNone(openclaw_version)
        self.assertEqual(manifest["version"], sync_version.group(1))
        self.assertEqual(manifest["version"], openclaw_version.group(1))
        self.assertEqual(manifest["version"], openclaw_skill["metadata"]["version"])
        self.assertNotIn("ROOT_README", sync_script)
        self.assertEqual(PUBLISHED_VERSION, readme_version.group(1))
        self.assertIn("OPENCLAW_PACKAGE", sync_script)

    def test_repository_and_current_packages_use_mit(self) -> None:
        license_text = (ROOT / "LICENSE").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        sync_script = (ROOT / "maintenance" / "tools" / "sync_adapters.py").read_text(encoding="utf-8")

        self.assertTrue(license_text.startswith("MIT License\n"))
        self.assertIn("subject to the\nfollowing conditions:", license_text)
        self.assertIn("The above copyright notice and this permission notice", license_text)
        self.assertFalse((ROOT / "LICENSE-SKILL").exists())
        self.assertFalse((ROOT / "LICENSE-CLAWHUB").exists())
        self.assertFalse((ROOT / "LICENSE-SCOPE.md").exists())
        self.assertFalse((ROOT / "licenses").exists())
        self.assertIn("## 开源许可", readme)
        self.assertIn("本仓库采用 [MIT License](LICENSE)。", readme)
        self.assertNotIn("MIT-0", readme)
        self.assertNotIn("LICENSE-SCOPE", readme)
        self.assertIn("[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)", readme)
        package_json = json.loads((ROOT / "maintenance" / "package.json").read_text(encoding="utf-8"))
        package_lock = json.loads((ROOT / "maintenance" / "package-lock.json").read_text(encoding="utf-8"))
        self.assertEqual("MIT", package_json["license"])
        self.assertEqual("MIT", package_lock["packages"][""]["license"])

        mit_package_skill_paths = [
            "chinese-official-writing/SKILL.md",
            "packages/agent-skills/skills/chinese-official-writing/SKILL.md",
            "packages/qwen-code/skills/chinese-official-writing/SKILL.md",
            "packages/hermes/skills/chinese-official-writing/SKILL.md",
        ]
        for relative_path in mit_package_skill_paths:
            frontmatter = read_frontmatter(ROOT / relative_path)
            self.assertNotIn("license", frontmatter, relative_path)
            package_root = (ROOT / relative_path).parent
            self.assertEqual((package_root / "LICENSE").read_bytes(), (ROOT / "LICENSE").read_bytes())

        openclaw_frontmatter = read_frontmatter(
            ROOT / "packages" / "openclaw" / "skills" / "chinese_official_writing" / "SKILL.md"
        )
        self.assertEqual("MIT", openclaw_frontmatter["license"])
        self.assertEqual(
            (ROOT / "packages" / "openclaw" / "skills" / "chinese_official_writing" / "LICENSE").read_bytes(),
            (ROOT / "LICENSE").read_bytes(),
        )

        redskill_frontmatter = read_frontmatter(
            ROOT / "packages" / "red-skillhub" / "skills" / "chinese-official-writing" / "SKILL.md"
        )
        self.assertEqual("MIT", redskill_frontmatter["license"])

        full_package_manifests = [
            "chinese-official-writing/hooks/adapters/codex/manifest.json",
            "chinese-official-writing/hooks/adapters/codebuddy/manifest.json",
            "chinese-official-writing/hooks/adapters/claude-code/manifest.json",
        ]
        for relative_path in full_package_manifests:
            manifest = json.loads((ROOT / relative_path).read_text(encoding="utf-8"))
            self.assertEqual(manifest["license"], "MIT", relative_path)

        self.assertIn('REPOSITORY_LICENSE = "MIT"', sync_script)
        self.assertIn("TARGET_LICENSES = {", sync_script)
        self.assertIn("if set(TARGET_LICENSES) != set(TARGETS)", sync_script)
        self.assertIn("every GitHub package target must use the repository MIT license", sync_script)
        self.assertIn('shutil.copyfile(ROOT_LICENSE, target / "LICENSE")', sync_script)
        self.assertNotIn("PURE_SKILL_LICENSE", sync_script)
        self.assertNotIn("MIT-0", sync_script)
        self.assertNotIn("redskill", sync_script.lower())

    def test_lint_ci_invocation_stays_out_of_writer_context(self) -> None:
        skill = (ROOT / "chinese-official-writing" / "SKILL.md").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        lint_script = (
            ROOT / "chinese-official-writing" / "scripts" / "prose_lint.py"
        ).read_text(encoding="utf-8")

        self.assertNotIn("--strict --fail-on medium", skill)
        self.assertNotIn("--strict --fail-on medium", readme)
        self.assertIn('"--strict"', lint_script)
        self.assertIn('"--fail-on"', lint_script)

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
        self.assertIn("不附其他说明", skill)
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
        self.assertIn("以用户最新版底稿和本轮明确补充材料为事实源", workflow)
        self.assertIn("保持主体、对象、数字、状态、关系及其信息去向", workflow)
        self.assertIn("信息进入正文、保持原状态、省略或短列实质缺口", workflow)
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
        self.assertIn("优先保留来源模板", format_ref)
        self.assertIn("不得把 Markdown `**加粗**`", format_ref)
        self.assertNotIn("正式 Word 输出前是否已清除 Markdown", checklist)
        self.assertIn("Markdown 加粗、代码块、`###` 标题", checklist)
        self.assertIn("文号、密级、签发人、印章是否未被编造", checklist)
        self.assertNotIn("Word 格式是否保留来源模板", checklist)
        self.assertIn("未编造文号、签发人、印章或版记", checklist)
        self.assertIn("用户可读格式复核项", checklist)
        for term in ["标题", "文种", "主送/受文对象", "发文字号", "日期", "附件", "落款", "结尾语", "层级编号"]:
            self.assertIn(term, checklist)
        self.assertIn("位置、风险层级、修改建议", checklist)
        self.assertIn("未默认重写全文", checklist)
        self.assertIn("不做 0-100 分评分", checklist)
        self.assertNotIn("0-100 分式伪精确评分", skill)
        self.assertIn("用户只要求检查、审查、格式核验或语气检查且未要求代改时", skill)
        self.assertIn("具体定位、分级和格式按 `references/review-checklist.md` 执行", skill)
        self.assertIn("去 AI 味检查按 `references/anti-ai-patterns.md` 执行", skill)
        self.assertNotIn("事实不清审稿中", skill)
        self.assertIn("事实不清审稿中", checklist)
        self.assertNotIn("用户要求检查、审一下、格式核验或语气检查时", skill)
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
        openclaw_skill = (ROOT / "packages" / "openclaw" / "skills" / "chinese_official_writing" / "SKILL.md").read_text(
            encoding="utf-8"
        )

        for text in [skill, external_research, checklist, openclaw_skill]:
            self.assertIn("联网搜索", text)
        self.assertIn("联网核验", elements)
        self.assertIn("默认不外搜", skill)
        self.assertNotIn("### 联网搜索使用边界", workflow)
        self.assertNotIn("external-research.md", workflow)
        for term in ["最新", "当前", "今日", "现行政策", "近期数据"]:
            self.assertIn(term, external_research)
        self.assertIn("搜索结果只作为来源参考", skill)
        self.assertIn("来源、日期或检索口径", skill)
        self.assertIn("发布日期、访问日期或检索口径", external_research)
        self.assertIn("来源冲突、无法核验或工具不可用", external_research)
        self.assertIn("默认不外搜补缺项", elements)
        self.assertIn("未因单位名称自动搜索单位公开样文", checklist)
        for text in [elements]:
            self.assertIn("不因出现单位名称就搜索单位公开样文", text)
        self.assertIn("默认不外搜", skill)
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
        route_cards = (
            ROOT / "chinese-official-writing" / "references" / "task-route-cards.md"
        ).read_text(encoding="utf-8")
        external_research = (
            ROOT / "chinese-official-writing" / "references" / "external-research.md"
        ).read_text(encoding="utf-8")
        agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        maintenance_history = (
            ROOT / "maintenance" / "docs" / "evidence" / "AGENTS-history-through-v1.5.39.md"
        ).read_text(encoding="utf-8")

        self.assertIn("不使用泛称或占位符补齐未给要素", skill)
        self.assertIn("段落骨架只组织可核对内容", workflow)
        self.assertIn("材料少时先写可用正文", route_cards)
        self.assertIn("不用泛称、占位或未给流程补齐骨架", route_cards)
        self.assertIn("实质缺口只在输出模式允许时短列", checklist)
        self.assertIn("直接影响当前文种成立、请批事项或执行落地", information_selection)
        self.assertIn("新增字段没有用户提供值时只写字段名并留空", workflow)
        self.assertIn("即使用分号写在一行", workflow)
        self.assertIn("不合并成连续句", workflow)
        self.assertIn("不推断发票、票据、邮箱、截止日期", workflow)
        self.assertIn("字段值未知", checklist)
        self.assertIn("分号串写的“字段名：字段值”序列", checklist)
        self.assertIn("字数自检", skill)
        self.assertIn("尽量压到限制内", skill)
        self.assertNotIn("并留出 5%-10% 余量", skill)
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
        self.assertIn("prompt/markdown", maintenance_history)
        self.assertIn(
            "禁止直接誊抄代码、脚本、正则、模板库、大段 prompt、固定话术或模板正文",
            maintenance_history,
        )
        self.assertIn(
            "禁止直接誊抄第三方代码、脚本、正则、模板库、大段 prompt、固定话术或模板正文",
            agents,
        )
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
            "保持主体、对象、数字、日期、状态和结论强度；"
            "事实之间的时间、因果、分类和归属关系以材料明确关系为准；"
            "总量与子项差额只用于合计校核，不据此补写“其余均正常、未发现其他问题、均无异常”等材料未给结论",
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
        self.assertIn("普通起草和润色修改不在正文前暂停或连续追问", workflow)
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
        request_checklist = (
            ROOT / "chinese-official-writing" / "references" / "genre-checklist-request.md"
        ).read_text(encoding="utf-8")
        genre_checklist_coverage = genre_checklist + "\n" + report_checklist + "\n" + request_checklist

        self.assertNotIn("正式交付前要素核对卡", skill)
        self.assertIn("references/format-gbt9704.md", skill)
        self.assertNotIn("标题用 2 号小标宋", skill)
        self.assertNotIn("页码用 4 号半角宋体并加一字线", skill)
        self.assertIn("读取 `references/format-gbt9704.md` 锁定版式", skill)
        self.assertIn("2 号小标宋体", format_ref)
        self.assertIn("3 号仿宋体", format_ref)
        self.assertIn("一般两端对齐", format_ref)
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

        self.assertIn("审稿时看成簇问题", anti_ai)
        self.assertIn("单个正式词、单个句式或达到某个次数都不能直接判错", anti_ai)
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
        self.assertIn("以用户最新版底稿和本轮明确补充材料为事实源", workflow)
        self.assertIn("段落骨架只组织可核对内容", workflow)
        self.assertIn("正式化新增事实", checklist)
        self.assertIn("正式化改写只压实原文已有事实", official_style)
        self.assertIn("口语来源不等于事实授权", official_style)
        for term in ["老板关心", "钱花得值", "马上要搞", "领导高度关注", "投入产出清晰", "推进较为紧迫", "按程序推进"]:
            self.assertIn(term, official_style)
        self.assertIn("不得自动升级", official_style)
        self.assertIn("审批态度留给用户确认", official_style)
        self.assertIn("用户要求给出“位置”时，是否优先逐项引用原文短语或句子", checklist)
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
        for term in ["句首重复", "连接词链", "句长同质化", "口号式结尾", "清单堆叠替代论证"]:
            self.assertIn(term, anti_ai)
        self.assertIn("只作软性审稿项，不作为硬门禁", anti_ai)
        self.assertIn("公文去 AI 味不是聊天化", anti_ai)
        self.assertIn("不得为了显得“像人写”而加入第一人称、反问、口语插入", anti_ai)
        self.assertIn("保留公文骨架和用户模板", anti_ai)
        self.assertIn("未指定时仍按位置、风险层级和修改建议输出", anti_ai)
        self.assertIn("用户要求改写时，只改确认有问题的句子及必要衔接", anti_ai)
        self.assertIn("## 高频表达的语义复核", anti_ai)
        self.assertEqual(
            anti_ai.count("输出范围按“高频表达的语义复核”中的输出约定执行"),
            2,
        )
        self.assertNotIn("输出范围按“总体复核方法”执行", anti_ai)
        self.assertIn("不为了显得像人写而加入第一人称", official_style)
        self.assertIn("正式化改写只压实原文已有事实", official_style)

    def test_v1601_j1_writing_endings_use_natural_terms(self) -> None:
        refs = ROOT / "chinese-official-writing" / "references"
        news_commentary = (refs / "genre-playbook-news-commentary.md").read_text(encoding="utf-8")
        argument_chains = (refs / "argument-chains.md").read_text(encoding="utf-8")
        genre_playbooks = (refs / "genre-playbooks.md").read_text(encoding="utf-8")
        anti_ai = (refs / "anti-ai-patterns.md").read_text(encoding="utf-8")

        self.assertIn("论点已经充分展开时自然结束", news_commentary)
        self.assertIn("以“妥否，请批示”“请予审定”等作结", argument_chains)
        self.assertIn("结尾落在责任或目标上", genre_playbooks)
        for phrase in ["每段结尾都停留在口号层面", "口号式结尾", "将口号式结尾改为具体办理动作"]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, anti_ai)
        for text in [news_commentary, argument_chains, genre_playbooks, anti_ai]:
            self.assertNotIn("收束", text)

    def test_v1511_anti_ai_frequency_review_is_prompt_driven_and_local(self) -> None:
        anti_ai = (ROOT / "chinese-official-writing" / "references" / "anti-ai-patterns.md").read_text(
            encoding="utf-8"
        )
        final_review = (
            ROOT / "chinese-official-writing" / "references" / "final-review-layers.md"
        ).read_text(encoding="utf-8")

        for term in [
            "本项由模型通读全文后判断，不按固定词表自动替换",
            "`先……再……`",
            "**连续否定**",
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
        self.assertNotIn("**抽象两步流程**", anti_ai)
        self.assertIn("只语义重写确认有问题的局部", final_review)
        self.assertNotIn("自动批量替换", final_review)

    def test_continuous_negation_is_position_independent_without_word_ban(self) -> None:
        anti_ai = (ROOT / "chinese-official-writing" / "references" / "anti-ai-patterns.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("**连续否定**", anti_ai)
        self.assertIn("句中或相邻句出现两个以上否定分句", anti_ai)
        self.assertIn("保留材料明确且与主题直接相关的必要否定", anti_ai)
        self.assertIn("合并重复内容，省去主题外围的否定说明", anti_ai)
        self.assertNotIn("连续否定式收口", anti_ai)
        self.assertNotIn("不机械照抄这些尾句", anti_ai)
        self.assertIn("不按固定词表自动替换", anti_ai)
        self.assertIn("不得自动批量替换", anti_ai)
        self.assertIn("不得把 `未`、`不`、`不得` 移到别的对象", anti_ai)
        self.assertNotIn("馆务会未形成新增设备采购决定", anti_ai)
        self.assertNotIn("先全面梳理、再研究处置", anti_ai)

    def test_sustained_progress_example_is_removed_only_from_redundant_cliche_list(self) -> None:
        anti_ai = (ROOT / "chinese-official-writing" / "references" / "anti-ai-patterns.md").read_text(
            encoding="utf-8"
        )
        section_start = anti_ai.index("## 空泛套话")
        section_end = anti_ai.index("## 高频正式词")
        empty_cliche_section = anti_ai[section_start:section_end]

        self.assertNotIn("- `持续推进`", empty_cliche_section)
        for retained_example in [
            "不断提升",
            "充分发挥",
            "有力支撑",
            "全面赋能",
            "形成一批",
            "重点任务包括",
            "保障措施包括",
            "总体看",
        ]:
            self.assertIn(f"- `{retained_example}`", empty_cliche_section)
        self.assertIn("必须有具体对象、机制、目标或结果支撑", empty_cliche_section)
        self.assertIn("应删去或换成具体工作、责任、时限和成果", empty_cliche_section)
        self.assertEqual(anti_ai.count("持续推进"), 3)
        self.assertIn("公式化未来展望", anti_ai)
        self.assertIn("相邻段落反复以 `要坚持`、`要强化`、`持续推进`", anti_ai)

    def test_v150_genre_playbooks_keep_minimal_borrowing_boundaries(self) -> None:
        skill = (ROOT / "chinese-official-writing" / "SKILL.md").read_text(encoding="utf-8")
        playbooks = (ROOT / "chinese-official-writing" / "references" / "genre-playbooks.md").read_text(
            encoding="utf-8"
        )
        minutes = (
            ROOT / "chinese-official-writing" / "references" / "genre-playbook-minutes.md"
        ).read_text(encoding="utf-8")
        correspondence = (
            ROOT / "chinese-official-writing" / "references" / "genre-playbook-correspondence.md"
        ).read_text(encoding="utf-8")
        work_summary = (
            ROOT / "chinese-official-writing" / "references" / "genre-playbook-work-summary.md"
        ).read_text(encoding="utf-8")
        report = (
            ROOT / "chinese-official-writing" / "references" / "genre-checklist-report.md"
        ).read_text(encoding="utf-8")
        plan_construction = (
            ROOT
            / "chinese-official-writing"
            / "references"
            / "genre-playbook-plan-construction.md"
        ).read_text(encoding="utf-8")
        routed_playbooks = (
            playbooks
            + "\n"
            + minutes
            + "\n"
            + correspondence
            + "\n"
            + work_summary
            + "\n"
            + plan_construction
        )
        ai_compute = (
            ROOT / "chinese-official-writing" / "references" / "ai-compute-docs.md"
        ).read_text(encoding="utf-8")
        handling = (ROOT / "chinese-official-writing" / "references" / "handling-elements.md").read_text(
            encoding="utf-8"
        )
        anti_ai = (ROOT / "chinese-official-writing" / "references" / "anti-ai-patterns.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("references/genre-playbooks.md", skill)
        self.assertIn("references/genre-playbook-correspondence.md", skill)
        self.assertIn("references/genre-playbook-work-summary.md", skill)
        self.assertIn("references/genre-playbook-plan-construction.md", skill)
        self.assertIn("## 目录", playbooks)
        for heading in [
            "## 会议纪要",
            "## 函/复函/征求意见函",
            "## 工作总结/工作要点/周报",
            "## 调研报告/研究报告/可研报告",
            "## 方案/实施方案/建设方案",
            "## 采购公告/审查材料",
        ]:
            self.assertIn(heading, routed_playbooks)
        self.assertNotIn("## 报告/情况说明", playbooks)
        self.assertIn("## 报告/情况说明", report)
        self.assertIn("## AI 算力与技术服务", ai_compute)
        for term in [
            "不新增默认联网、API、Word/PDF 或脚本硬门禁",
            "只替换该字段内容，不把多字段合并成一句",
            "拆成独立字段行后不要保留行尾分号或造成 `。；`",
            "字段式周报保留字段和换行，不散文化、不合并字段",
            "字段式审查材料只改用户指定字段",
            "未给会议判断",
            "不自行补受众称呼",
            "不补服务单位责任",
            "责任或期限未给时不使用“按审核执行”“后续推进”等泛口径补齐",
            "普通采购公告不默认进入 AI 算力语境",
        ]:
            self.assertIn(term, routed_playbooks)
        self.assertIn("用户已有提纲、模板、标题顺序时优先保留", skill)
        self.assertIn("保留字段名、字段顺序和单元边界", skill)
        self.assertIn("详细结构见下文；本节只保留触发和边界", ai_compute)
        self.assertIn("会议判断、受众称呼、角色分工、合同义务或服务单位责任", skill)
        self.assertIn("详细测算和参数转读 `ai-compute-docs.md`", handling)
        self.assertIn("专项结构和指标写法转读 `ai-compute-docs.md`", anti_ai)

    def test_playbook_template_priority_uses_entry_semantics_without_leaf_duplication(self) -> None:
        duplicate = (
            "每节只用于确定材料骨架和风险点。用户已有模板和字段顺序优先，"
            "不因 playbook 改掉真实模板、主送、落款、字段或附件关系。"
        )
        leaf_paths = [
            "references/genre-playbooks.md",
            "references/genre-checklist-report.md",
            "references/genre-playbook-correspondence.md",
            "references/genre-playbook-minutes.md",
            "references/genre-playbook-plan-construction.md",
        ]
        roots = [
            ROOT / "chinese-official-writing",
            ROOT / "packages" / "agent-skills" / "skills" / "chinese-official-writing",
            ROOT / "packages" / "qwen-code" / "skills" / "chinese-official-writing",
            ROOT / "packages" / "hermes" / "skills" / "chinese-official-writing",
            ROOT / "packages" / "openclaw" / "skills" / "chinese_official_writing",
        ]

        for root in roots:
            with self.subTest(root=root):
                skill = (root / "SKILL.md").read_text(encoding="utf-8")
                self.assertIn("用户已有提纲、模板、标题顺序时优先保留", skill)
                self.assertIn("保留字段名、字段顺序和单元边界", skill)
                for relative in leaf_paths:
                    self.assertNotIn(duplicate, (root / relative).read_text(encoding="utf-8"))

    def test_work_summary_elaboration_stays_in_target_section(self) -> None:
        playbooks = (
            ROOT / "chinese-official-writing" / "references" / "genre-playbooks.md"
        ).read_text(encoding="utf-8")
        work_summary = (
            ROOT / "chinese-official-writing" / "references" / "genre-playbook-work-summary.md"
        ).read_text(encoding="utf-8")
        self.assertNotIn("## 工作总结/工作要点/周报", playbooks)
        for rule in [
            "材料已经给出下一步、未来安排或改进计划时",
            "材料未给实际运行、测评或业务反馈时",
            "总结段可将“下一年度拟完善、拟优化”自然归纳为“将在下一年度加以改进”",
            "需要概括前文时可以使用“综上所述”等承接语",
            "成效必须有事实支撑",
        ]:
            self.assertIn(rule, work_summary)

    def test_ordinary_letter_leaf_is_self_contained_without_default_supplemental_reads(self) -> None:
        skill = (ROOT / "chinese-official-writing" / "SKILL.md").read_text(encoding="utf-8")
        playbooks = (
            ROOT / "chinese-official-writing" / "references" / "genre-playbooks.md"
        ).read_text(encoding="utf-8")
        correspondence = (
            ROOT / "chinese-official-writing" / "references" / "genre-playbook-correspondence.md"
        ).read_text(encoding="utf-8")

        def section(text: str, heading: str, next_heading: str | None = None) -> str:
            body = text.split(heading, 1)[1]
            if next_heading is not None:
                body = body.split(next_heading, 1)[0]
            return body.strip()

        self.assertEqual(
            section(playbooks, "## 使用方式", "## 函/复函/征求意见函"),
            section(correspondence, "## 使用方式", "## 函/复函/征求意见函"),
        )
        playbook_section = section(
            playbooks,
            "## 函/复函/征求意见函",
            "## 通知/通告/公告/公示/通报",
        )
        correspondence_section = section(correspondence, "## 函/复函/征求意见函")
        for term in [
            "平行商洽",
            "函不写成命令",
        ]:
            self.assertIn(term, playbook_section)
            self.assertIn(term, correspondence_section)
        for term in [
            "称谓服从用户模板和已给主体",
            "不相隶属单位",
            "商请",
            "请予支持",
            "材料已给或办理确有需要时",
            "反馈期限",
            "联系人和附件",
            "专此函达",
            "请予支持为盼",
        ]:
            self.assertIn(term, correspondence_section)
        for supplemental_reference in [
            "formal-addressing.md",
            "genre-checklist.md",
        ]:
            self.assertNotIn(supplemental_reference, correspondence_section)
        self.assertIn(
            "普通函起草，以及只改错字、标点、格式或明确局部措辞时读取",
            skill,
        )
        self.assertIn(
            "用户提供既有普通函并要求重组事务动作、状态、条件、范围或结构时读取函规则",
            skill,
        )
        self.assertIn("通知、复函、征求意见函、讲话稿", skill)

    def test_weak_model_suggestion_boundaries_stay_soft(self) -> None:
        skill = (ROOT / "chinese-official-writing" / "SKILL.md").read_text(encoding="utf-8")
        workflow = (ROOT / "chinese-official-writing" / "references" / "workflow.md").read_text(
            encoding="utf-8"
        )
        route_cards = (
            ROOT / "chinese-official-writing" / "references" / "task-route-cards.md"
        ).read_text(encoding="utf-8")
        playbooks = (ROOT / "chinese-official-writing" / "references" / "genre-playbooks.md").read_text(
            encoding="utf-8"
        )
        report = (
            ROOT / "chinese-official-writing" / "references" / "genre-checklist-report.md"
        ).read_text(encoding="utf-8")
        review = (ROOT / "chinese-official-writing" / "references" / "review-checklist.md").read_text(
            encoding="utf-8"
        )

        for text in [skill, workflow]:
            self.assertIn("考察、评估、建议、拟测试、考虑尝试或下一步设想", text)
        self.assertIn("不改写成已定实施方案、执行命令", skill)
        self.assertIn("不升级成已定实施方案、命令或已安排动作", workflow)
        self.assertNotIn("成本考察、成本评估", playbooks)
        self.assertIn("成本考察、成本评估", report)
        self.assertIn("不自动改题为“调研报告”“考核说明”或“实施方案”", report)
        self.assertIn("不写成已经确定的执行路线、责任命令或反馈时限", report)
        self.assertIn("按 `workflow.md` 的事实映射式二次修改删掉未支持推断", playbooks)
        self.assertIn("二次局部修改已命中轻量任务卡时，转对应卡片处理", workflow)
        self.assertIn("优先直接改对应位置", route_cards)
        self.assertIn("本卡不重新定义信息去向", route_cards)
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
        ]:
            self.assertTrue(term in proofreading or term in skill)
        self.assertIn("不改写成 `请核实出处`", proofreading)
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

        self.assertNotIn("**引用误改和数据冲突**", skill)
        self.assertNotIn("引用表述、出处和发布日期建议由用户按原始材料核实。", skill)
        self.assertIn("普通叙述中的口语称谓和表达可以按正式文稿语体调整", proofreading)
        self.assertIn("引号内、明确标注为原文/引语或要求逐字保留的内容按字面边界保留", proofreading)
        self.assertIn("引用表述、出处和发布日期建议由用户按原始材料核实。", proofreading)
        self.assertIn("同一金额、日期、数量、比例、单位、主体", proofreading)
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

        self.assertIn(
            "python scripts/prose_lint.py --delivery-mode draft-body --format --structure <draft>",
            review,
        )
        self.assertIn("`<draft>` 替换为待检查文件路径", review)
        skill = (ROOT / "chinese-official-writing" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("检查终稿正文时按 `references/final-review-layers.md` 使用 `draft-body` 模式", skill)

    def test_ai_dedupe_prompt_fix_guidance_is_documented(self) -> None:
        skill = (ROOT / "chinese-official-writing" / "SKILL.md").read_text(encoding="utf-8")
        openclaw_skill = (ROOT / "packages" / "openclaw" / "skills" / "chinese_official_writing" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        information_selection = (
            ROOT / "chinese-official-writing" / "references" / "information-selection.md"
        ).read_text(encoding="utf-8")
        elements = (
            ROOT / "chinese-official-writing" / "references" / "handling-elements.md"
        ).read_text(encoding="utf-8")
        for text in [skill, openclaw_skill]:
            self.assertNotIn("用户点名禁止编造的字段写成正文中的“未提供”说明", text)
            self.assertIn("识别为正式报送结构缺口", text)
            self.assertIn("最终正文不得残留未完成占位", text)
            self.assertNotIn("（成文日期待确认）", text)
            self.assertIn("不使用当前日期补落款", text)
        self.assertIn("（成文日期待确认）", elements)
        self.assertIn("用户要求先确认时，再在正文前提出必要问题", information_selection)
        self.assertIn("文后提示使用少量短项", information_selection)
        self.assertIn("用户点名不得编造的字段按输出模式省略或短列", information_selection)
        self.assertIn("不在正文中解释为“未提供”", information_selection)
        self.assertIn("去 AI 味、变换句式、拆分长句或调整清单结构", skill)
        self.assertIn("不得补写未给的解释、原因、影响范围、办理流程、责任人员、字段示例或整改动作", skill)
        self.assertIn("用户只给问题清单、任务清单或明确要求不新增事实时", skill)
        self.assertIn("不为显得自然或完整而补解释", skill)
        self.assertIn("不得补写未给的解释、原因、影响范围、办理流程、责任人员、字段示例或整改动作", openclaw_skill)

    def test_openclaw_agent_rules_include_v140_routing_and_format_bridge(self) -> None:
        canonical = (ROOT / "chinese-official-writing" / "SKILL.md").read_text(encoding="utf-8")
        text = (ROOT / "packages" / "openclaw" / "skills" / "chinese_official_writing" / "SKILL.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("任务模式", text)
        self.assertIn("references/workflow.md", text)
        self.assertIn("references/information-selection.md", text)
        self.assertIn("按材料状态、事项关联性和办理必要性选择信息", text)
        self.assertIn("材料只给问题清单时，正文列明已确认问题及其对象、数量和状态", text)
        self.assertIn("稿内一致性风险", text)
        self.assertIn("references/format-gbt9704.md", text)
        format_ref = (
            ROOT / "packages" / "openclaw" / "skills" / "chinese_official_writing" / "references" / "format-gbt9704.md"
        ).read_text(encoding="utf-8")
        self.assertIn("不得把 Markdown `**加粗**`", format_ref)
        self.assertIn("交付范围以用户要求为准", text)
        self.assertIn("允许文后提示时，只列其指定事项", text)
        self.assertIn("材料没有的事实不补写，也不在正文说明材料缺失", text)
        self.assertIn("按任务渐进读取资料", text)

    def test_openclaw_skill_card_source_is_tracked_but_not_packaged_directly(self) -> None:
        source = (
            ROOT / "maintenance" / "docs" / "platform-snapshots" / "clawhub-v1.6.0" / "skill-card.md"
        ).read_text(encoding="utf-8")
        packaged_path = ROOT / "packages" / "openclaw" / "skills" / "chinese_official_writing" / "skill-card.md"

        self.assertIn("Known Risks and Mitigations", source)
        self.assertFalse(packaged_path.exists())

    def test_openclaw_skill_card_uses_absolute_links_and_key_genres(self) -> None:
        skill = (ROOT / "chinese-official-writing" / "SKILL.md").read_text(encoding="utf-8")
        source = (
            ROOT / "maintenance" / "docs" / "platform-snapshots" / "clawhub-v1.6.0" / "skill-card.md"
        ).read_text(encoding="utf-8")

        self.assertNotIn("](references/", source)
        self.assertIn("https://github.com/gongyu0918-debug/chinese-official-writing-skill/blob/main/", source)
        for keyword in ["通知", "请示", "报告", "函", "复函", "批复", "方案", "说明", "申请", "采购公告", "审查材料"]:
            with self.subTest(keyword=keyword):
                self.assertIn(keyword, skill)
                self.assertIn(keyword, source)

    def test_readme_summarizes_current_engineering_and_real_writing_evidence(self) -> None:
        text = (ROOT / "README.md").read_text(encoding="utf-8")

        for term in [
            "下表只保留最近 5 次版本验证",
            "1.6.4 保护性外扩收束、新闻边界与短稿质量",
            "1.6.2 Hook 架构与静态兼容层",
            "1.6.1 入口减载",
            "1.6.0 事实边界",
            "1.6.3 纯审稿 Hook 旁路与 SkillHub 检索信号",
            "同题独立写作节选",
            "明川市政务服务中心服务事项信息变更管理办法（试行）",
            "v164-under-length-three-host-live-result-20260814.md",
            "新增了“自收到材料之日起”的期限起算",
            "无 Skill 成稿",
            "带 Skill 成稿",
            "新闻与评论写作",
            "maintenance/tests/evidence",
            "maintenance/docs/evidence/README.md",
            "本仓库采用 [MIT License](LICENSE)。",
        ]:
            self.assertIn(term, text)
        recent_table = text.split("## 模型消融与真实写稿", 1)[1].split("### 同题独立写作节选", 1)[0]
        self.assertEqual(7, sum(1 for line in recent_table.splitlines() if line.startswith("|")))
        for removed in [
            "早期 270 任务模型消融",
            "60 份发布级真实写稿",
            "并非同一随机 seed",
            "不做事后加工",
            "主要证据：",
            "SkillHub 本次暂缓更新",
            "ClawHub/OpenClaw 继续固定",
            "从 GitHub 手动部署时",
            "MIT-0",
            "LICENSE-SCOPE",
        ]:
            self.assertNotIn(removed, text)
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
