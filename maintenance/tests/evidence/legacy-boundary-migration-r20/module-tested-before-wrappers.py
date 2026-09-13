from __future__ import annotations

from pathlib import Path
import hashlib
import json
import re
import shlex
import subprocess
import sys
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[2]
CANONICAL = ROOT / "chinese-official-writing"
OPTIONAL_GATE_FILES = {
    "hooks",
    "references/delivery-review-gate.md",
    "scripts/review_gate.py",
}
SKILLHUB_CLEAN_PACKAGE_EXCLUDES = {"agents/openai.yaml", "LICENSE"}
REFERENCE_LINK_RE = re.compile(r"`(?:references/)?([^`/]+\.md)`")
CURRENT_VERSION = "1.6.30"
PUBLISHED_VERSION = "1.6.30"


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


def read_routing_surfaces(skill_path: Path) -> str:
    """Follow the explicit entry -> index -> compatibility route, without fallback search."""
    homepage = skill_path.read_text(encoding="utf-8")
    index_relative = "references/reference-index.md"
    if f"`{index_relative}`" not in homepage:
        raise AssertionError(f"entry route missing: {skill_path}: {index_relative}")
    index_path = skill_path.parent / index_relative
    index = index_path.read_text(encoding="utf-8")
    compatibility = "compatibility-scene-routing.md"
    if compatibility not in REFERENCE_LINK_RE.findall(index):
        raise AssertionError(f"index route missing: {index_path}: {compatibility}")
    scene = (index_path.parent / compatibility).read_text(encoding="utf-8")
    return "\n".join((homepage, index, scene))


def read_field_boundary(skill_root: Path) -> str:
    """Resolve field editing through the current explicit homepage route."""
    home = (skill_root / "SKILL.md").read_text(encoding="utf-8")
    if "`references/field-editing.md`" not in home:
        raise AssertionError(f"field editing route missing: {skill_root}")
    return read_reference("field-editing.md", skill_root)


def skill_roots() -> list[Path]:
    return [CANONICAL] + [
        ROOT / "packages" / package / "skills" / name
        for package, name in (
            ("agent-skills", "chinese-official-writing"),
            ("qwen-code", "chinese-official-writing"),
            ("qwenwork", "chinese-official-writing"),
            ("hermes", "chinese-official-writing"),
            ("openclaw", "chinese_official_writing"),
        )
    ]


def read_reference(name: str, root: Path = CANONICAL) -> str:
    """Read the named owner, never aggregate leaves to satisfy a contract."""
    return (root / "references" / name).read_text(encoding="utf-8")


class SkillBoundaryTests(unittest.TestCase):
    def assert_rules(self, name: str, *rules: str, root: Path = CANONICAL) -> None:
        text = read_reference(name, root)
        for rule in rules:
            with self.subTest(owner=name, rule=rule, root=root):
                self.assertIn(rule, text)

    def assert_route(self, purpose: str, leaf: str, root: Path = CANONICAL) -> str:
        """Bind a function to an explicit index row and a real independent page."""
        home = (root / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("`references/reference-index.md`", home)
        rows = [line for line in read_reference("reference-index.md", root).splitlines()
                if purpose in line and f"`{leaf}`" in line]
        self.assertEqual(len(rows), 1, f"{purpose} must select {leaf} in one index row")
        self.assertTrue((root / "references" / leaf).is_file())
        return read_reference(leaf, root)

    def test_only_one_agent_handoff_entrypoint_remains(self) -> None:
        self.assertTrue((ROOT / "AGENTS.md").is_file())
        self.assertFalse((ROOT / "agent.md").exists())

    def test_canonical_skill_declares_positive_trigger_boundary(self) -> None:
        text = (CANONICAL / "SKILL.md").read_text(encoding="utf-8")
        description = read_frontmatter(CANONICAL / "SKILL.md")["description"]
        self.assertLessEqual(len(description), 280)
        for keyword in ["申请", "请示", "报告", "通知", "通告", "意见", "决定", "函", "公告", "审查材料", "正式文本"]:
            self.assertIn(keyword, description)
        for excluded in ["营销", "社媒", "论文", "个人求职"]:
            self.assertNotIn(excluded, description)
        for heading in ["## 适用范围", "## 入口契约", "## 正文形态"]:
            self.assertIn(heading, text)
        self.assertIn("读取 `references/writing-rules.md` 完成取材、成稿、复核及交付", text)
        self.assert_rules("writing-rules.md", "主体、对象、数字、金额、业务日期、引语、来源和事实状态照实保留",
                          "具体经历、数值、期限、程序、责任、决定和成效须有依据")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        for boundary in ["批量语料生成", "规避人工审核"]:
            self.assertNotIn(boundary, text)
            self.assertIn(boundary, readme)
        self.assertIn("法律、财务、采购、审计、政策适用、保密审查和正式签发结论由相应责任主体确认", readme)

    def test_skill_frontmatter_keeps_only_discovery_fields_and_tags(self) -> None:
        paths = [
            CANONICAL / "SKILL.md",
            ROOT / "packages" / "agent-skills" / "skills" / "chinese-official-writing" / "SKILL.md",
            ROOT / "packages" / "qwen-code" / "skills" / "chinese-official-writing" / "SKILL.md",
            ROOT / "packages" / "qwenwork" / "skills" / "chinese-official-writing" / "SKILL.md",
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
        exclusions = OPTIONAL_GATE_FILES | {"agents/openai.yaml"}
        expected_files = {
            relative
            for relative in relative_files(CANONICAL)
            if not any(relative == excluded or relative.startswith(f"{excluded}/") for excluded in exclusions)
        }
        self.assertEqual(set(relative_files(package_root)), expected_files)
        self.assertEqual((package_root / "LICENSE").read_bytes(), (ROOT / "LICENSE").read_bytes())
        self.assertEqual((package_root / "README.md").read_bytes(), (CANONICAL / "README.md").read_bytes())
        for forbidden in OPTIONAL_GATE_FILES | {"agents/openai.yaml"}:
            self.assertFalse((package_root / forbidden).exists(), forbidden)

        sync_script = (ROOT / "maintenance" / "tools" / "sync_adapters.py").read_text(encoding="utf-8")
        self.assertIn('"openclaw": OPENCLAW_PACKAGE', sync_script)
        self.assertIn('"openclaw": OPTIONAL_GATE_FILES + ("agents/openai.yaml",)', sync_script)

    def test_qwenwork_package_has_official_layout_and_bounded_claims(self) -> None:
        package_root = ROOT / "packages" / "qwenwork"
        skill_root = package_root / "skills" / "chinese-official-writing"
        readme = (package_root / "README.md").read_text(encoding="utf-8")
        sync_script = (ROOT / "maintenance" / "tools" / "sync_adapters.py").read_text(
            encoding="utf-8"
        )

        self.assertEqual(read_frontmatter(skill_root / "SKILL.md")["name"], "chinese-official-writing")
        self.assertIn("~/.qwenworkcn/skills/chinese-official-writing/", readme)
        self.assertIn("压缩包顶层只放一个 `chinese-official-writing/` 目录", readme)
        self.assertIn("QwenWork 与 Qwen Code 是两个宿主", readme)
        self.assertFalse((skill_root / "hooks").exists())
        self.assertIn('"qwenwork": PACKAGES / "qwenwork"', sync_script)
        self.assertIn('"qwenwork": OPTIONAL_GATE_FILES', sync_script)

    def test_ai_compute_detail_is_loaded_from_specialty_reference(self) -> None:
        home = (CANONICAL / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("在主文种叶上叠加 `references/ai-compute-docs.md`", home)
        self.assertIn("普通服务器、接口、安全、SLA 或验收内容单独出现时沿用主文种规则", home)
        self.assertIn("主文种已确定且稿件明确涉及 AI 算力、模型推理/训练、智算中心或模型服务资源时", home)
        self.assert_rules("reference-index.md", "按首页的场景条件叠加 `ai-compute-docs.md`", "算力页仍是附加规则")
        self.assert_route("技术需求书、软件需求说明、接口需求和技术需求附件", "genre-playbook-technical-requirements.md")
        self.assert_rules("ai-compute-docs.md", "Token", "并发", "存储", "带宽", "SLA", "验收")
        self.assert_rules("technical-terms.md", "图形处理器（Graphics Processing Unit，GPU）",
                          "应用编程接口（Application Programming Interface，API）",
                          "服务级别协议（Service Level Agreement，SLA）",
                          "数据中心电能利用效率（Power Usage Effectiveness，PUE）", "含义不明的缩写不自行展开")
        self.assert_rules("anti-ai-patterns.md", "含义未明的内部缩写先核查")
        self.assert_rules("ai-compute-docs.md", "技术、SLA、安全与验收", "需要统一英文术语时读取 `technical-terms.md`")
        self.assertFalse((CANONICAL / "references/genre-playbooks.md").exists())

    def test_adapter_skill_copies_keep_boundaries(self) -> None:
        for root in skill_roots()[1:]:
            with self.subTest(root=root):
                text = (root / "SKILL.md").read_text(encoding="utf-8")
                for boundary in ["批量语料生成", "规避人工审核", "本技能只提供写作和复核辅助", "## 三层使用原则"]:
                    self.assertNotIn(boundary, text)
                self.assertIn("## 入口契约", text)
                self.assertIn("`references/writing-rules.md`", text)
                self.assertIn("`references/format-gbt9704.md`", text)
                self.assert_rules("writing-rules.md", "主体、对象、数字、金额、业务日期、引语、来源和事实状态照实保留", root=root)
                self.assert_rules("format-gbt9704.md", "不得编造文号、密级、紧急程度、签发人、印章、正式签发日期和版记信息",
                                  "落款单位、联系人和联系电话采用已有信息", root=root)

    def test_delivery_scope_rule_is_naturalized_across_current_skill_copies(self) -> None:
        expected = "正式正文清除 AI 身份、提示词、隐藏推理、起草过程、脚本结果、制作说明、免责话术、连续追问或“正文如下”等旁白。"
        canonical_body = (CANONICAL / "SKILL.md").read_text(encoding="utf-8").split("---", 2)[2].strip()
        for root in skill_roots():
            with self.subTest(root=root):
                text = (root / "SKILL.md").read_text(encoding="utf-8")
                self.assertEqual(text.count(expected), 1)
                self.assertEqual(canonical_body, text.split("---", 2)[2].strip())
                self.assert_rules("anti-ai-patterns.md", "材料中的真实领导要求和批示按其业务含义保留",
                                  "版本标识、流转对象、保密和适用范围声明", "按实际用途保留", root=root)
                self.assert_rules("writing-rules.md", "保留用户的标题、顺序、模板、字段、表格及指定空位",
                                  "跨段、多主体及正文、表格、附件核对主体", "文件交付时提示留在消息中",
                                  "明确只要稿件或省略说明时省略提示", root=root)

    def test_entry_excludes_only_non_obvious_out_of_scope_tasks(self) -> None:
        """Out-of-scope examples stay concise and limited to adjacent writing tasks."""
        text = (CANONICAL / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("英文、文学、营销软文、社交媒体文案、个人求职信和代码说明走其他路径", text)
        self.assertNotIn("闲聊回复", text)
        self.assertNotIn("通用翻译", text)

    def test_drafting_rules_are_split_for_prompt_following(self) -> None:
        text = (CANONICAL / "SKILL.md").read_text(encoding="utf-8")
        headings = ["### 第一步：理解用户需求", "### 第二步：选择文种", "### 第三步：按任务加读"]
        self.assertEqual(sorted(text.index(h) for h in headings), [text.index(h) for h in headings])
        for field in ["任务与交付件", "稿件用途", "材料与修改范围", "篇幅与形式"]:
            self.assertIn(f"- **{field}**", text)
        section = text.split(headings[-1], 1)[1].split("## 路由主线", 1)[0]
        for mode in ["起草", "改写", "局部修改、重排或字段处理", "压缩或限字", "审核、复核、审校或把关", "格式交付"]:
            self.assertEqual(sum(line.startswith(f"- **{mode}**") for line in section.splitlines()), 1)
        self.assertIn("选定主文种后，读取 `references/writing-rules.md`", section)
        self.assertNotIn("task-route-cards.md", text)
        self.assertFalse((CANONICAL / "references/task-route-cards.md").exists())

    def test_long_form_headings_warn_against_markdown_bold(self) -> None:
        home = (CANONICAL / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("纯文本主标题独立成行", home)
        self.assertIn("用户明确要求 Markdown 时使用对应格式", home)
        self.assert_rules("format-gbt9704.md", "不得把 Markdown `**加粗**`、代码块或 `###` 标题标记原样带入正式 Word",
                          "段首题、编号正文句或用户模板明确接排时仍按正文标点处理")
        self.assert_rules("proofreading-checklist.md", "Markdown 残留是否符合交付形态")

    def test_plain_text_title_boundary_contract_is_explicit(self) -> None:
        home = (CANONICAL / "SKILL.md").read_text(encoding="utf-8")
        for rule in ["纯文本主标题独立成行，行末省略句号，标题后空一行",
                     "层级标题省略行末句号，与其统领的正文分段",
                     "编号内容本身是完整正文句时，保留正常句末标点",
                     "用户模板优先；用户明确要求 Markdown 时使用对应格式",
                     "Word 小标题是否独立成段按模板和实际统领关系判断"]:
            with self.subTest(responsibility=rule):
                self.assertIn(rule, home)

    def test_style_references_keep_precise_routes_without_common_error_catchall(self) -> None:
        home = (CANONICAL / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("`references/writing-rules.md`", home)
        self.assert_rules("writing-rules.md", "所有成稿、改后稿和审核任务读取 `anti-ai-patterns.md` 检查语言")
        self.assert_rules("anti-ai-patterns.md", "口语或情绪化表达用同义正式语体表述", "保留正式语气")
        self.assertFalse((CANONICAL / "references/official-style.md").exists())
        self.assertNotIn("其他口语化、标题漂移、重复事项、格式噪点", home)
        self.assertNotIn("## 常见错误反例", home)

    def test_second_revision_fact_mapping_has_one_complete_entry_rule(self) -> None:
        home = (CANONICAL / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("以最新版底稿为唯一主线", home)
        self.assertIn("`references/structure-editing.md`", home)
        self.assert_rules("writing-rules.md", "以本轮有效材料、最新版底稿和用户模板为准，落实补充、更正及修改范围",
                          "引用旧稿、样文或模型先前补写内容时重新核对依据",
                          "先完成可用正文", "上轮未解决事项和已发现未处理错误",
                          "路由、工具过程与自评留在内部")
        self.assert_rules("structure-editing.md", "以上一轮已确认正文为底稿，不回退到旧稿",
                          "不把旧主送、旧落款、旧标题带回正文")
        self.assertNotIn("映射表", home)

    def test_packaged_resource_mirrors_match_canonical_bytes(self) -> None:
        canonical = ROOT / "chinese-official-writing"
        targets = [
            (ROOT / "packages" / "agent-skills" / "skills" / "chinese-official-writing", OPTIONAL_GATE_FILES),
            (ROOT / "packages" / "qwen-code" / "skills" / "chinese-official-writing", OPTIONAL_GATE_FILES),
            (ROOT / "packages" / "qwenwork" / "skills" / "chinese-official-writing", OPTIONAL_GATE_FILES),
            (ROOT / "packages" / "hermes" / "skills" / "chinese-official-writing", OPTIONAL_GATE_FILES),
        ]
        for target, excludes in targets:
            for folder in ["agents", "references", "scripts"]:
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

    def test_canonical_and_plain_packages_exclude_gate_sources_and_keep_scripts(self) -> None:
        surfaces = [
            CANONICAL,
            ROOT / "packages" / "agent-skills" / "skills" / "chinese-official-writing",
            ROOT / "packages" / "qwen-code" / "skills" / "chinese-official-writing",
            ROOT / "packages" / "qwenwork" / "skills" / "chinese-official-writing",
            ROOT / "packages" / "hermes" / "skills" / "chinese-official-writing",
            ROOT / "packages" / "openclaw" / "skills" / "chinese_official_writing",
        ]
        for surface in surfaces:
            with self.subTest(surface=surface):
                for relative in OPTIONAL_GATE_FILES:
                    self.assertFalse((surface / relative).exists(), relative)
                for script in ("draft_length.py", "prose_lint.py"):
                    self.assertTrue((surface / "scripts" / script).is_file(), script)

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
        for relative in OPTIONAL_GATE_FILES:
            self.assertFalse(
                any(path == relative or path.startswith(f"{relative}/") for path in package_allowlist),
                relative,
            )
        for script in ("draft_length.py", "prose_lint.py"):
            self.assertIn(f"scripts/{script}", package_allowlist)


    def test_reference_loading_table_keeps_progressive_disclosure(self) -> None:
        home = (CANONICAL / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("为每份稿件选定一个主叶", home)
        for purpose, leaf in [("会议纪要", "genre-playbook-minutes.md"),
                              ("方案、实施方案、建设方案", "genre-playbook-plan-construction.md"),
                              ("只审可研", "genre-checklist-feasibility-review.md")]:
            self.assert_route(purpose, leaf)
        self.assert_rules("reference-index.md", "需要共性能力时按触发条件加读",
                          "需要展开方案比较、跨段论证或执行链条", "行文关系、敬语或称谓拿不准")
        self.assertIn("独立稿件及具有独立用途的附件分别选路", home)
        self.assertIn("选定主文种后，读取 `references/writing-rules.md` 完成取材、成稿、复核及交付", home)
        self.assertNotIn("genre-playbooks.md", read_reference("reference-index.md"))

    def test_lightened_routes_preserve_reviewed_conditions(self) -> None:
        """Replace obsolete row hashes with explicit primary-function and scene mappings."""
        for purpose, leaf in [("请示", "genre-playbook-request.md"), ("报告、情况报告", "genre-playbook-report.md"),
                              ("通知", "genre-playbook-notice.md"), ("公告、公示、通告", "genre-playbook-publication.md"),
                              ("会议纪要", "genre-playbook-minutes.md"), ("讲话稿、致辞", "speech-person-order.md"),
                              ("会议主持词、主持串词", "speech-person-order.md"),
                              ("独立审查意见、评审意见", "genre-playbook-review-opinion.md"),
                              ("采购需求、规格报价、响应规则或履约条件需要专项核对", "genre-playbook-procurement-review.md"),
                              ("采购公告", "genre-playbook-procurement-announcement.md")]:
            with self.subTest(purpose=purpose):
                self.assert_route(purpose, leaf)
        scenes = read_reference("compatibility-scene-routing.md")
        rows = [line for line in scenes.splitlines() if line.startswith("用户")]
        expected = {"genre-playbook-news-message.md", "genre-playbook-news-commentary.md",
                    "genre-playbook-advisory-feedback.md", "genre-playbook-remediation-plan.md",
                    "genre-playbook-complaint-reflection.md"}
        self.assertEqual(len(rows), 6)
        self.assertEqual({target for row in rows for target in REFERENCE_LINK_RE.findall(row)}, expected)
        self.assertEqual(sum("genre-playbook-advisory-feedback.md" in row for row in rows), 2)
        self.assertIn("用户以建议信向有权处理事项的对象提出合作性建议时", scenes)
        self.assert_rules("reference-index.md", "在已选主文种上叠加 `genre-playbook-procurement-review.md`",
                          "只做语言或格式审校时不因此加读")
        self.assertIn("不预读全部专页", scenes)
        self.assertIn("具有下行指导、监督整改或审计监督权力关系的意见按对应文种处理", scenes)

    def test_lightened_indices_resolve_from_each_skill_root_and_keep_quality_bridges(self) -> None:
        for root in skill_roots():
            with self.subTest(root=root):
                home = (root / "SKILL.md").read_text(encoding="utf-8")
                read_routing_surfaces(root / "SKILL.md")
                self.assertIn("标题、模板、正文用途或行文关系有冲突时，先读 `references/genre-routing.md` 判定", home)
                for name in ("reference-index.md", "compatibility-scene-routing.md", "writing-rules.md"):
                    text = read_reference(name, root)
                    for target in REFERENCE_LINK_RE.findall(text):
                        self.assertTrue(((root if target == "SKILL.md" else root / "references") / target).is_file(), target)
                    self.assertEqual(text, read_reference(name))
                self.assertIn("`references/writing-rules.md`", home)
                self.assertIn("`references/review-checklist.md`", home)
                self.assertIn("`references/format-gbt9704.md`", home)
                self.assert_rules("compatibility-scene-routing.md", "选定主文种后按首页的任务规则写稿", root=root)
                self.assert_rules("writing-rules.md", "`anti-ai-patterns.md`", "`proofreading-checklist.md`", "`prose-lint-usage.md`", root=root)
                for leaf in ("anti-ai-patterns.md", "proofreading-checklist.md", "prose-lint-usage.md", "review-checklist.md", "format-gbt9704.md"):
                    self.assertEqual(read_reference(leaf, root), read_reference(leaf))

    def test_task_route_cards_keep_sparse_tasks_lightweight(self) -> None:
        self.assertFalse((CANONICAL / "references/task-route-cards.md").exists())
        self.assert_rules("writing-rules.md", "普通完整短稿至少80字", "局部替换、字段处理或明确要求更短时按实际范围处理",
                          "整体查全文，局部查改动与关联内容", "先完成可用正文")
        self.assert_rules("field-editing.md", "改字段值只改指定字段")
        self.assert_rules("structure-editing.md", "用户要求“补一句”时只补一句或短句")
        self.assert_route("会议纪要", "genre-playbook-minutes.md")
        self.assert_route("通知", "genre-playbook-notice.md")
        self.assert_rules("genre-playbook-minutes.md", "建议、待议和未形成决定的内容保持相应状态", "不补写“会议认为”“会议强调”")
        self.assert_rules("genre-playbook-notice.md", "不为了形成通知格式补整改、会议、责任或期限", "不能为了显得完整新增办理承诺")

    def test_missing_metric_visibility_does_not_become_plan_state(self) -> None:
        self.assert_rules("writing-rules.md", "分清信息未给与业务未定、暂无结果与是否启动",
                          "拟、建议、可选、进行中、待核和未决定保持原程度",
                          "影响文种成立、请批、执行或用户明示要求的缺项", "移除已解决、已给定及无关事项")

    def test_sparse_length_rule_keeps_fact_boundary_without_short_first_priority(self) -> None:
        """Keep bounded length guidance and execute both real counter modes independently."""
        with self.subTest(contract="current length owner"):
            home = (CANONICAL / "SKILL.md").read_text(encoding="utf-8")
            common = read_reference("writing-rules.md")
            compression = read_reference("compression-details.md")
            self.assertIn("references/writing-rules.md", home)
            self.assertRegex(common, r"具体经历[^。]*须有依据")
            self.assertRegex(common, r"上限[^。]*无需填满")
            self.assertRegex(common, r"仍不足[^。]*实际差额[^。]*不报达标")
            self.assertIn("compression-details.md", common)
            self.assertIn("scripts/draft_length.py", compression)
            for option in ("--min-chars", "--max-chars", "--count-mode cjk", "--json", "`-`"):
                self.assertIn(option, compression)
        # A stale prose assertion must still fail, without hiding the executable contract.
        for mode, expected in [("nonspace", 8), ("cjk", 2)]:
            with self.subTest(count_mode=mode):
                run = subprocess.run(
                    [sys.executable, "-B", str(CANONICAL / "scripts/draft_length.py"),
                     "--count-mode", mode, "--min-chars", str(expected),
                     "--max-chars", str(expected), "--json", "-"],
                    input="正文ABC12。\n\n文后提示\n不计入123", encoding="utf-8",
                    capture_output=True, timeout=30,
                )
                self.assertEqual(run.returncode, 0, run.stderr)
                result = json.loads(run.stdout)
                self.assertEqual(len(result), 1)
                self.assertEqual(result[0]["count"], expected)
                self.assertEqual(result[0]["status"], "within")
                self.assertEqual(result[0]["scope"], "draft-before-postscript")

    def test_light_route_is_terminal_until_an_explicit_escalation_condition(self) -> None:
        home = (CANONICAL / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("以用户模板、最新版底稿、明确标题和用途选路", home)
        self.assertIn("选定主文种后，读取 `references/writing-rules.md`", home)
        self.assert_rules("writing-rules.md", "整体查全文，局部查改动与关联内容",
                          "实质修改后核对关联内容并复扫，影响篇幅时另测字数")
        self.assert_rules("review-checklist.md", "仅要求审核时交付意见", "要求审核后修改、复核后修改或优化稿件时",
                          "在本轮范围内直接修正有充分依据的问题", "交付完整改后稿")
        self.assertFalse((CANONICAL / "references/task-route-cards.md").exists())

    def test_sparse_notice_does_not_treat_delivery_channel_as_issuer(self) -> None:
        self.assert_route("通知", "genre-playbook-notice.md")
        self.assert_rules("genre-playbook-notice.md", "通知对象由材料或用户给出时保留原称谓",
                          "落款主体和文号采用已有信息",
                          "参加、报送、组织人员、反馈和办理等动作只在材料或用户明确给出时写入")
        self.assert_rules("writing-rules.md", "主体、对象、数字、金额、业务日期、引语、来源和事实状态照实保留")
        self.assert_rules("review-checklist.md", "发文主体和动作主体分别按材料核对", "保持各自角色与原有状态")

    def test_workflow_sparse_line_relief_keeps_carriers_and_route_graph(self) -> None:
        self.assertFalse((CANONICAL / "references/workflow.md").exists())
        self.assert_route("报告、情况报告", "genre-playbook-report.md")
        self.assert_rules("genre-playbook-report.md", "材料未给某一环节时，直接在已给事实处收束",
                          "不为填满骨架增加责任、流程、成效、期限或结论",
                          "字段式、表单式和清单式材料保留字段名、顺序、数字和换行")
        self.assert_rules("writing-rules.md", "围绕事项组织自然段", "完成文种动作即可收束")
        self.assert_rules("anti-ai-patterns.md", "同一事项只有换词重复、无新信息或不同作用时合并")

    def test_reference_links_form_an_acyclic_graph(self) -> None:
        refs = ROOT / "chinese-official-writing" / "references"
        graph: dict[str, set[str]] = {}
        link_re = REFERENCE_LINK_RE
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
        """Compact discovery delegates less common names to the explicit genre index."""
        home = (CANONICAL / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("`references/reference-index.md`", home)
        index = read_reference("reference-index.md")
        for keyword in ["复函", "公示", "通告", "意见", "决定", "决议", "议案", "公报", "命令", "工作要点", "评审意见"]:
            self.assertIn(keyword, index)
        self.assert_rules("genre-playbook-review-opinion.md", "依据评审记录整理采购、初步设计或一般项目材料的审查结论",
                          "保留被审稿件的主文种")

    def test_multi_round_revision_rules_keep_structure_and_genre_format(self) -> None:
        home = (CANONICAL / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("以最新版底稿为唯一主线", home)
        self.assertIn("`references/structure-editing.md`", home)
        self.assert_rules("structure-editing.md", "不回退到旧稿", "反馈渠道", "原因分析",
                          "增加独立段落", "小标题数量、名称和顺序", "只补一句或短句",
                          "新增一节/新增小标题", "同步改小标题序号和前后衔接",
                          "改变发送人、发文单位、主送、收文或接收方时",
                          "是否以换词方式保留被删除事项", "正文称谓、落款、行文关系和敬谦用语同步更新")
        self.assert_rules("writing-rules.md", "落实补充、更正及修改范围", "按材料和主文种核对事实、状态、要素及本轮改动",
                          "实质修改后核对关联内容并复扫")

    def test_legal_genres_have_checklist_and_handling_elements(self) -> None:
        for purpose, leaf, function in [("公告、公示、通告", "genre-playbook-publication.md", "应知、应遵或应办理"),
                                        ("决议", "genre-playbook-resolution.md", "通过"),
                                        ("意见", "genre-playbook-opinion.md", "指导")]:
            self.assertIn(function, self.assert_route(purpose, leaf))
        self.assert_rules("reference-index.md", "用途已明确且没有适用专页时，读取 `genre-checklist.md`")
        self.assert_rules("genre-checklist.md", "结合主体、接收对象和用途核对行文关系", "保留用户限定的标题和字段")
        self.assert_rules("genre-playbook-publication.md", "公示对象、期限、异议或反馈渠道及联系人", "材料未给期限或渠道时保留缺项，不编造")
        self.assert_rules("writing-rules.md", "按主文种写全要素、缘由、用途和合理衔接",
                          "影响文种成立、请批、执行或用户明示要求的缺项")

    def test_reported_genre_coverage_gaps_have_minimum_support(self) -> None:
        """Previously reported genres still route to pages with their own useful functions."""
        for purpose, leaf in [("工作总结", "genre-playbook-work-summary.md"),
                              ("工作要点", "genre-playbook-work-priorities.md"),
                              ("独立审查意见、评审意见", "genre-playbook-review-opinion.md"),
                              ("采购需求、规格报价、响应规则或履约条件需要专项核对", "genre-playbook-procurement-review.md"),
                              ("讲话稿、致辞", "genre-playbook-speech-address.md"),
                              ("征求意见函", "genre-playbook-correspondence.md"),
                              ("采购公告", "genre-playbook-procurement-announcement.md"),
                              ("公告、公示、通告", "genre-playbook-publication.md")]:
            self.assert_route(purpose, leaf)
        self.assert_rules("genre-playbook-correspondence.md", "需要对方反馈时写清反馈路径")
        self.assert_rules("genre-playbook-publication.md", "期限、异议或反馈渠道及联系人")
        self.assert_rules("genre-playbook-procurement-announcement.md", "响应期限和提交方式", "联系方式、公告期限、附件",
                          "只提示影响当前发布目的的缺项")

    def test_genre_authority_uses_the_defined_routing_source(self) -> None:
        home = (CANONICAL / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("标题、模板、正文用途或行文关系有冲突时，先读 `references/genre-routing.md` 判定，再选主叶", home)
        self.assert_rules("genre-routing.md", "依据主要办理或表达目的选文种", "结合收文方权限和行文关系确定文种",
                          "不相隶属单位间商洽、询答、请求批准或在权限范围内答复审批事项，按函或复函处理",
                          "上级答复下级请示按批复处理")
        self.assert_rules("external-research.md", "优先查看官方规范和公开正式文本", "用户业务事实仍以用户材料为准")

    def test_report_checklist_is_routed_as_an_atomic_leaf(self) -> None:
        draft = self.assert_route("报告、情况报告", "genre-playbook-report.md")
        self.assert_route("报告功能或状态表达拿不准时", "genre-checklist-report.md")
        self.assert_rules("genre-checklist-report.md", "文种核对", "没有夹带审批请求", "保留用户指定名称",
                          "接口、系统、页面、数字、日期、单位和进行中/待核/建议状态是否保持原词和原强度")
        self.assertNotIn("成稿骨架", read_reference("genre-checklist-report.md"))
        for rule in ["成稿骨架", "报告事项与范围", "使用事实性汇报语言", "结论先行或按时间顺序均可",
                     "不改题为调研、方案或考核说明", "原因、责任、损失或整改结论以材料为准"]:
            self.assertIn(rule, draft)
        self.assertFalse((CANONICAL / "references/genre-playbooks.md").exists())

    def test_feasibility_review_checklist_is_an_atomic_leaf(self) -> None:
        """Targeted feasibility review remains scoped to claims and evidence already supplied."""
        review = self.assert_route("只审可研", "genre-checklist-feasibility-review.md")
        for rule in ["只审既有可研摘要时", "主张本身及相互之间的内部一致性", "区分实际数据、测算数据和假设",
                     "起草、改写或审后改写仍按既有可研 playbook", "不扩展用户未点名的审查范围",
                     "尚未形成决定", "不代填市场价格结论、数值阈值、责任分工、合同条款或办理程序"]:
            self.assertIn(rule, review)
        self.assertNotIn("## 可行性研究报告", read_reference("genre-checklist.md"))

    def test_minutes_playbook_is_routed_as_an_atomic_leaf(self) -> None:
        leaf = self.assert_route("会议纪要", "genre-playbook-minutes.md")
        for rule in ["重点是议定事项、责任、期限和后续动作", "不补写“会议认为”“会议强调”",
                     "建议、待议和未形成决定的内容保持相应状态", "不编造“会议决定”",
                     "发言人的建议、判断和条件逐项对照记录，归属保持一致",
                     "责任或期限未给时不使用“按审核执行”“后续推进”等泛口径补齐"]:
            self.assertIn(rule, leaf)
        self.assertFalse((CANONICAL / "references/genre-playbooks.md").exists())

    def test_request_playbook_is_routed_as_an_atomic_leaf(self) -> None:
        leaf = self.assert_route("请示", "genre-playbook-request.md")
        for rule in ["请示一文一事", "申请写清原因、依据或必要性", "缘由到请求的关系仍要完整",
                     "常识支持的一般必要性也可写入", "原因完全无法推知时，正文保留已知事项和请求，文后提示询问具体缘由",
                     "单项采购请示或申请可用一至两个自然段", "根据有关休假规定",
                     "不用“因个人事务”“因身体原因”等泛称代填", "主送采用用户给出的接收对象",
                     "落款采用已给的发文或申请主体", "正式成稿清理无用途的占位", "`argument-chains.md`",
                     "未给的主送和申请单位按 `writing-rules.md` 核对缺项",
                     "材料只给工作交接时，不据此补“工作不受影响”、通讯承诺或代办责任",
                     "“批准后另行确定”“按规定办理”也属于后续安排，材料未给时不补入"]:
            self.assertIn(rule, leaf)
        self.assertNotIn("单项采购请示或申请用一至两个自然段", leaf)
        self.assertFalse((CANONICAL / "references/genre-playbooks.md").exists())

    def test_plan_construction_playbook_is_routed_as_an_atomic_leaf(self) -> None:
        """Plans keep their action skeleton distinct from research and feasibility decisions."""
        self.assert_route("方案、实施方案、建设方案", "genre-playbook-plan-construction.md")
        self.assert_route("调研、研究", "genre-playbook-research.md")
        self.assert_route("可研", "genre-playbook-feasibility.md")
        self.assert_rules("genre-playbook-plan-construction.md", "以目标、主要任务和实施路径为主线",
                          "责任、进度、保障、验收与风险控制按材料和用户模板落位",
                          "建设方案先核对目标、范围、任务、进度、责任和验收",
                          "围绕已有目标、范围、步骤和期限成稿，相邻内容可合成自然段",
                          "人员、设备、保障、预算和验收等要素按材料取舍",
                          "明确给出的“拟”“待定”等业务状态照原级别保留",
                          "行业通用做法可以用于分析建议，与已经确定的实施事项分开表达")
        self.assert_rules("genre-playbook-research.md", "对象与范围 → 方法、样本和资料来源",
                          "不把有限样本写成普遍结论")
        self.assert_rules("genre-playbook-feasibility.md", "可研材料为项目决策提供依据",
                          "围绕需求、可选方案和实施条件论证可行性", "不把建议写成已批项目",
                          "可以结合已有需求和常识提出比较、核实或验证建议",
                          "建议与已经确定的安排分开")
        self.assertFalse((CANONICAL / "references/genre-playbook-research-feasibility.md").exists())

    def test_remediation_plan_has_a_state_preserving_atomic_leaf(self) -> None:
        """Remediation retains state, bounded reasons and executable authorized future actions."""
        scenes = read_reference("compatibility-scene-routing.md")
        self.assertIn("用户明确要求根据检查、审计、督察、评估反馈或问题清单制定本单位整改方案", scenes)
        self.assertIn("`references/genre-playbook-remediation-plan.md`", scenes)
        self.assertIn("不因正文偶然出现“整改”改变原定文种", scenes)
        self.assertIn("只报告已有整改进展", scenes)
        self.assert_rules("genre-playbook-remediation-plan.md", "后文拟定措施的将来时不能代替或吞掉该状态",
                          "每个问题应有可执行的整改措施", "可以作一层归因或逆推",
                          "职责范围内的纠正、制度完善、执行复核和持续改进属于拟定的未来措施",
                          "不套用专班、月报、考核、销号等固定机制", "用户要求只交正文时，不附写作说明")
        path = CANONICAL / "references/genre-playbook-remediation-plan.md"
        for root in skill_roots()[1:]:
            with self.subTest(root=root):
                self.assertEqual(path.read_bytes(), (root / "references" / path.name).read_bytes())

    def test_request_review_checklist_is_routed_as_an_atomic_leaf(self) -> None:
        """Requests have a targeted review owner which preserves real internal templates."""
        review = self.assert_route("请批事项或必要要素拿不准时", "genre-checklist-request.md")
        for rule in ["只在请示、申请需要细查文种功能、办理要素", "或用户要求审稿、复核时读取",
                     "一文一事，开头或前部明确请批事项", "两行标题",
                     "不要只因出现 `妥否，请批示` 就判定为请示",
                     "不把缺失项补成正文事实", "结尾应放在落款和成文日期之前"]:
            self.assertIn(rule, review)
        self.assertNotIn("## 请示", read_reference("genre-checklist.md"))
        self.assertNotIn("两行标题", read_reference("genre-playbook-request.md"))

    def test_institution_rules_have_a_dedicated_routed_leaf(self) -> None:
        self.assertIn("制度", read_frontmatter(CANONICAL / "SKILL.md")["description"])
        leaf = self.assert_route("制度、规定、办法", "genre-playbook-institution-rules.md")
        for rule in ["管理办法", "实施细则", "内容较短、事项单一时连续列条", "通知壳只写发布对象、执行要求和附件关系",
                     "围绕实际操作顺序写清主体、触发条件、步骤、时限、结果和记录", "仅在材料明确时写入",
                     "同时读取 `format-gbt9704.md`", "不把建议或协助升级为审批权、处罚权或最终责任",
                     "制度正文作为附件独立成文、独立复核", "未决状态、过渡安排和例外条件按原状态承载"]:
            self.assertIn(rule, leaf)

    def test_news_message_uses_one_frontmatter_cluster_and_six_body_aliases(self) -> None:
        """News discovery stays compact while six aliases route and factual constraints survive."""
        description = read_frontmatter(CANONICAL / "SKILL.md")["description"]
        self.assertIn("新闻消息", description)
        for alias in ["活动新闻稿", "新闻通稿"]:
            self.assertNotIn(alias, description)
        scenes = read_reference("compatibility-scene-routing.md")
        row = next(line for line in scenes.splitlines() if "`references/genre-playbook-news-message.md`" in line)
        for alias in ["新闻稿", "新闻消息", "快讯", "活动报道", "活动新闻稿", "新闻通稿"]:
            self.assertIn(alias, row)
        self.assertIn("不因材料中偶然出现", row)
        leaf = self.assert_route("新闻消息、活动报道", "genre-playbook-news-message.md")
        for rule in ["标题和导语先交代最重要的已给事实", "材料不足以安全达到下限时，优先交付事实完整的短消息",
                     "材料明示且有新闻价值的单个未决状态应保留", "推断不得改变事实对象或范围",
                     "发布视角只调整叙述主语", "活动名称本身已明示功能且不需要新增参与者动作或活动内容时",
                     "合并成一至两个自然段", "普通消息不自行补“这不代表、这不表示、这不构成”"]:
            self.assertIn(rule, leaf)

    def test_news_commentary_uses_clustered_frontmatter_and_precise_body_route(self) -> None:
        """Explicit commentary intent routes consistently; incidental words do not change genre."""
        for root in skill_roots():
            with self.subTest(root=root):
                frontmatter = read_frontmatter(root / "SKILL.md")
                self.assertIn("新闻评论", frontmatter["description"])
                for alias in ["时评", "评论员文章"]:
                    self.assertNotIn(alias, frontmatter["description"])
                scenes = read_reference("compatibility-scene-routing.md", root)
                row = next(line for line in scenes.splitlines()
                           if "`references/genre-playbook-news-commentary.md`" in line)
                for alias in ["新闻评论", "时评", "评论员文章"]:
                    self.assertIn(alias, row)
                self.assertIn("用户明确将体裁指定为", row)
                self.assertIn("普通公文内容中出现这些词语，不改变原定文种", row)
                self.assert_route("新闻评论、时评", "genre-playbook-news-commentary.md", root)

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
            "评论推演逐句核对依据和适用范围",
            "材料事实与评论推演",
            "公共价值、利弊和成立条件",
            "具体政策、数据、具名责任、期限或承诺",
            "正文自然收束",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, leaf)
        self.assertNotIn("示例：", leaf)
        self.assertNotIn("模板", leaf)
        self.assertNotIn("首先", leaf)
        self.assertNotIn("其次", leaf)

    def test_news_genres_are_defined_in_authoritative_routing(self) -> None:
        self.assert_route("新闻消息、活动报道", "genre-playbook-news-message.md")
        self.assert_route("新闻评论、时评", "genre-playbook-news-commentary.md")
        self.assert_rules("genre-routing.md", "依据主要办理或表达目的选文种", "纪要按会议事项组织")
        self.assert_rules("genre-playbook-news-message.md", "新闻消息以报道已发生事实为主",
                          "以评论公共议题为主要用途的稿件读取 `genre-playbook-news-commentary.md`")
        self.assert_rules("genre-playbook-news-commentary.md", "事实保持原有主体、数字、时间和状态，推演保持为观点",
                          "具体政策、数据、具名责任、期限或承诺以材料为准")
        self.assert_rules("genre-playbook-minutes.md", "不写成会议新闻")

    def test_format_reference_clarifies_document_number_brackets(self) -> None:
        text = (ROOT / "chinese-official-writing" / "references" / "format-gbt9704.md").read_text(encoding="utf-8")

        self.assertIn("年份使用六角括号 `〔〕`", text)
        self.assertIn("不要用方括号 `[]` 或圆括号 `()` 替代", text)

    def test_final_drafts_must_not_keep_unfinished_placeholders(self) -> None:
        home = (CANONICAL / "SKILL.md").read_text(encoding="utf-8")
        self.assert_rules("writing-rules.md", "业务日期沿用材料，年份可继承明确语境",
                          "需要落款且未给日期时，用系统或工具确认的当天日期作为草稿日期",
                          "指定留空、待确认或模板空位的按要求保留", "字段、表格及指定空位，清理无用途占位")
        self.assert_rules("format-gbt9704.md", "最终正文不要残留 `〔签发日期〕`、`〔会议时间〕` 等未完成占位",
                          "正式签发日期以用户或材料确认的信息为准", "不得编造文号、密级、紧急程度、签发人、印章、正式签发日期和版记信息")
        for placeholder in ["〔签发日期〕", "〔会议时间〕", "[具体项目名称]", "XXXX万元",
                            "YYYY年MM月DD日", "（签发日期）", "（成文日期待确认）"]:
            self.assertNotIn(placeholder, home)

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

        self.assertIn(f"当前 GitHub 版本为 `{PUBLISHED_VERSION}`", readme)
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
            "QwenWork",
            "通用 Agent Skills",
            "MiniMax Skills",
            "GLM Skills（Z.ai/智谱）",
            "AutoClaw",
            "Kimi Code CLI",
            "ZCode",
            "TRAE",
            "Baidu Comate AI IDE",
        ]:
            self.assertIn(term, readme)
        for path in [
            "packages/qwen-code/",
            "packages/qwenwork/",
            "packages/agent-skills/",
        ]:
            self.assertIn(path, readme)
        self.assertIn("npx skills add https://github.com/gongyu0918-debug/chinese-official-writing-skill --skill chinese-official-writing", readme)
        for mode in ['"qwen"', '"qwenwork"']:
            self.assertIn(mode, sync_script)
        self.assertNotIn('"minimax"', sync_script)
        self.assertNotIn('"glm"', sync_script)
        frontmatter = read_frontmatter(ROOT / "chinese-official-writing" / "SKILL.md")
        self.assertEqual(set(frontmatter), {"name", "description", "metadata"})

    def test_public_package_versions_match_skill_and_sync_script(self) -> None:
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
        self.assertEqual(CURRENT_VERSION, sync_version.group(1))
        self.assertEqual(CURRENT_VERSION, openclaw_skill["metadata"]["version"])
        self.assertEqual(PUBLISHED_VERSION, openclaw_version.group(1))
        self.assertEqual(PUBLISHED_VERSION, readme_version.group(1))
        self.assertNotIn("ROOT_README", sync_script)
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
        self.assertIn("普通 Skill、references、普通检查脚本与兼容包采用 [MIT License](LICENSE)。", readme)
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
            "packages/qwenwork/skills/chinese-official-writing/SKILL.md",
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
        self.assert_rules("writing-rules.md", "以本轮有效材料、最新版底稿和用户模板为准，落实补充、更正及修改范围",
                          "引用旧稿、样文或模型先前补写内容时重新核对依据",
                          "具体经历、数值、期限、程序、责任、决定和成效须有依据",
                          "材料与常识支持的原因、目的、影响、合理下一步、自然延续和结论可展开",
                          "仅排版、逐字保留或不作分析的限制照办", "明确只要稿件或省略说明时省略提示",
                          "路由、工具过程与自评留在内部")
        self.assert_rules("structure-editing.md", "不回退到旧稿", "不把旧主送、旧落款、旧标题带回正文")
        self.assert_rules("anti-ai-patterns.md", "语言调整保持原意、叙述身份、引用、主体、对象、条件、可能性、否定范围、先后和论断强度")
        for owner in ["writing-rules.md", "review-checklist.md"]:
            self.assertNotIn("未新增原文外事实", read_reference(owner))

    def test_staged_review_workflow_remains_intact(self) -> None:
        common = read_reference("writing-rules.md")
        steps = ["## 第一步：材料与分析", "## 第二步：成稿与篇幅", "## 第三步：复核", "## 第四步：交付"]
        positions = [common.index(step) for step in steps]
        self.assertEqual(positions, sorted(positions))
        self.assert_rules("writing-rules.md", "整体查全文，局部查改动与关联内容", "实质修改后核对关联内容并复扫，影响篇幅时另测字数",
                          "交付前修正范围内已确认的问题", "运行受限时完成可做的检查，如实记录未完成项")
        self.assert_rules("review-checklist.md", "按当前主文种和 `writing-rules.md` 复核", "改后稿复核")
        self.assert_rules("prose-lint-usage.md", "正文实质修改后复扫", "最终采用已检查文本")
        for rejected in ["最多局部修订一次", "只执行一次", "复核完成即停止"]:
            self.assertNotIn(rejected, common)

    def test_v140_mode_routing_material_mapping_and_format_bridge_are_documented(self) -> None:
        home = (CANONICAL / "SKILL.md").read_text(encoding="utf-8")
        for mode in ["**起草**", "**改写**", "**压缩或限字**", "**审核、复核、审校或把关**", "**格式交付**"]:
            self.assertIn(mode, home)
        self.assert_rules("writing-rules.md", "以本轮有效材料、最新版底稿和用户模板为准",
                          "主体、对象、数字、金额、业务日期、引语、来源和事实状态照实保留")
        self.assert_rules("review-checklist.md", "分清已确认错误、待核实风险和可选表达建议",
                          "证据冲突或尚待核实时写明不确定性")
        self.assert_rules("genre-playbook-report.md", "不为填满骨架增加责任、流程、成效、期限或结论")
        self.assert_rules("anti-ai-patterns.md", "删除没有实际作用的夸大评价、充分性自证和口号",
                          "只有换词重复、无新信息或不同作用时合并", "归因需能辨认来源",
                          "相邻段落反复同样开头、连续排比或口号结尾", "抽象词说明具体对象与作用",
                          "不按词表和出现次数机械替换")
        self.assert_rules("format-gbt9704.md", "Word/排版交付衔接", "DOCX/document 技能", "不得编造文号", "Markdown `**加粗**`")

    def test_v141_formal_delivery_review_and_tone_rules_are_documented(self) -> None:
        home = (CANONICAL / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("`references/review-checklist.md`", home)
        self.assertNotIn("review-direct-checklist.md", home)
        self.assert_rules("review-checklist.md", "审核默认检查全文；用户限定范围时按其要求",
                          "将问题定位到原句、段落、标题、字段或附件", "说明依据，同一问题合并",
                          "仅要求审核时交付意见", "交付完整改后稿", "用户同时要求意见和改稿时一并给出")
        self.assert_rules("writing-rules.md", "审核给出位置、问题和建议改法", "AI味问题列原句及可用替代表达")
        self.assert_rules("format-gbt9704.md", "按交付用途核对要素", "影响本次交付的缺项按 `writing-rules.md` 列在正文外",
                          "不得用 `[依据/背景]`", "先保留用户模板", "不得编造文号、密级、紧急程度、签发人、印章、正式签发日期和版记信息")
        self.assert_rules("anti-ai-patterns.md", "口语或情绪化表达用同义正式语体表述", "叙述身份", "论断强度",
                          "不按词表和出现次数机械替换")
        for forbidden in ["document_generator.py", "generate_official_doc.py", "install_fonts.py", "format_docx.py"]:
            self.assertNotIn(forbidden, relative_files(CANONICAL))
        self.assertNotRegex(read_reference("review-checklist.md"), r"输出.{0,20}0[-—]100")

    def test_v141_search_boundary_stays_lightweight_and_opt_in(self) -> None:
        """Spec replaces opt-in-only search with bounded research for unfamiliar writing needs."""
        home = (CANONICAL / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("`references/external-research.md`", home)
        self.assertNotIn("默认不外搜", home)
        self.assert_rules("external-research.md", "不熟悉的新文种、新材料类型或特殊事务场景",
                          "用户明确要求搜索或核验公开来源", "最新数据、当前情况、现行政策、近期进展",
                          "常规已知文种沿用已有路线", "单位名称本身不触发搜索单位样文或写作风格",
                          "用户业务事实仍以用户材料为准",
                          "来源名称、发布机关或发布主体、文号或链接、发布日期、访问日期或检索口径",
                          "来源冲突、无法核验或工具不可用时，列入文后提示",
                          "立即结束该项检索", "才围绕该缺口改一次查询", "一次后无论是否补齐，都停止该项检索")
        self.assert_rules("genre-checklist.md", "通用写法、必备要素或格式不熟悉时，按首页的核查规则定向查证")
        for forbidden in ["search_units.py", "unit_style_cache.json", "unit-style-registry.md"]:
            self.assertNotIn(forbidden, relative_files(CANONICAL))

    def test_v144_common_real_writing_risks_and_adoption_gate_are_documented(self) -> None:
        self.assert_rules("writing-rules.md", "影响文种成立、请批、执行或用户明示要求的缺项", "先完成可用正文",
                          "不足时补全材料和合理分析", "仍不足则说明实际差额与所需材料，不报达标")
        self.assert_rules("field-editing.md", "新增字段没有用户提供值时只写字段名并留空", "即使用分号写在一行",
                          "不合并成连续句", "不推断发票、票据、邮箱、截止日期")
        self.assert_rules("compression-details.md", "长稿先分配开头、主体、措施和结尾的篇幅", "默认按非空白字符统计",
                          "长文各部分均衡压缩", "措施和结尾保留具体落点", "将实测差额和所需材料列入文后提示")
        self.assert_rules("anti-ai-patterns.md", "用已有主体、动作、依据及结果说明问题", "具体成效与保证需要相应证据",
                          "只有换词重复、无新信息或不同作用时合并")
        self.assert_rules("external-research.md", "来源名称、发布机关或发布主体、文号或链接")
        self.assert_rules("format-gbt9704.md", "正文定稿状态按用户信息表述", "默认另存新版本")
        agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        match = re.search(r"\[开发细则\]\(([^)]+)\)", agents)
        self.assertIsNotNone(match)
        development = (ROOT / match.group(1)).read_text(encoding="utf-8")
        self.assertIn("历史归档不作为新要求", agents)
        self.assertIn("全量门原则上只在合并或发布前跑一次", development)
        history = (ROOT / "maintenance/docs/evidence/AGENTS-history-through-v1.5.39.md").read_text(encoding="utf-8")
        self.assertIn("禁止直接誊抄代码、脚本、正则、模板库、大段 prompt、固定话术或模板正文", history)

        for owner in ["writing-rules.md", "review-checklist.md", "genre-checklist.md"]:
            text = read_reference(owner)
            self.assertNotIn("prompt/markdown", text)
            self.assertNotIn("社区技能", text)

    def test_candidate_ac_anchors_fact_relations_to_explicit_material(self) -> None:
        self.assert_rules("writing-rules.md", "主体、对象、数字、金额、业务日期、引语、来源和事实状态照实保留",
                          "业务日期沿用材料，年份可继承明确语境", "合计差额可核算，不据此认定其余正常",
                          "主体、范围和强度与依据相称，多种解释保留不确定性")
        self.assert_rules("argument-chains.md", "同一段围绕一个主要事项展开", "判断所依据的事实或条件、两者之间的关系",
                          "推断与已经发生的事实分别表述")

    def test_fact_sufficiency_guidance_is_soft_and_non_blocking(self) -> None:
        self.assert_rules("writing-rules.md", "先完成可用正文，实质缺项集中在文后提示",
                          "拟、建议、可选、进行中、待核和未决定保持原程度",
                          "影响文种成立、请批、执行或用户明示要求的缺项", "上轮未解决事项和已发现未处理错误",
                          "移除已解决、已给定及无关事项", "明确只要稿件或省略说明时省略提示")
        self.assert_rules("review-checklist.md", "需补材料限于影响文种成立、请批事项、执行或用户明示要求的缺项，并说明影响",
                          "已有依据足以支持基本判断时，次级材料作为可选补充")
        self.assertNotIn("暂停确认", read_reference("writing-rules.md"))

    def test_v147_minimal_borrowing_rules_stay_soft_and_prompt_based(self) -> None:
        self.assert_rules("format-gbt9704.md", "2 号小标宋体", "3 号仿宋体", "一般两端对齐", "4 号半角宋体阿拉伯数字",
                          "回行保持词意完整", "用户只要求排版时，保留原文的用词、数字、标点和字符",
                          "允许同步改稿时，先在授权范围内修正内容", "只起草正文时，先完成所需正文",
                          "优先只列用户点名缺项", "其他正式要素按单位模板另行核对",
                          "普通 Word/docx 稿按当前文种、用户模板和实际使用的字段核对内容与版式",
                          "用户要求正式发文、红头、签发或相应正式要素时，再按适用要求核对发文要素")
        self.assert_rules("writing-rules.md", "引用旧稿、样文或模型先前补写内容时重新核对依据",
                          "具体经历、数值、期限、程序、责任、决定和成效须有依据")
        self.assert_rules("anti-ai-patterns.md", "以语境和句群为单位判断", "保留正式语气", "不按词表和出现次数机械替换",
                          "语言调整保持原意、叙述身份、引用、主体、对象、条件、可能性、否定范围、先后和论断强度")
        self.assert_rules("review-checklist.md", "保留材料与常识支持的分析、条件性结论和合理建议",
                          "次级材料作为可选补充", "将问题定位到原句、段落、标题、字段或附件")
        for purpose, owner in [("通知", "genre-playbook-notice.md"), ("请示", "genre-playbook-request.md"),
                               ("报告、情况报告", "genre-playbook-report.md"), ("方案、实施方案", "genre-playbook-plan-construction.md"),
                               ("征求意见函", "genre-playbook-correspondence.md")]:
            self.assert_route(purpose, owner)

    def test_v148_anti_ai_borrowing_stays_soft_and_official(self) -> None:
        self.assert_rules("anti-ai-patterns.md", "以语境和句群为单位判断", "不按词表和出现次数机械替换",
                          "相邻段落反复同样开头、连续排比或口号结尾", "叙述身份", "论断强度",
                          "必要英文、产品名、型号和缩写沿用正式拼写")
        self.assert_rules("writing-rules.md", "整体查全文，局部查改动与关联内容")
        self.assert_rules("review-checklist.md", "分清已确认错误、待核实风险和可选表达建议")
        self.assert_rules("ai-compute-docs.md", "Token、调用次数、用户数、峰值并发",
                          "单位保持一致。以 Token 为主线时承接费用测算", "不与 Token 单价混作同一成本口径")
        self.assert_rules("proofreading-checklist.md", "数字、金额、日期、比例、单位、专名和引用是否与材料一致")

    def test_v1601_j1_writing_endings_use_natural_terms(self) -> None:
        self.assert_rules("genre-playbook-news-commentary.md", "论点已经充分展开时，正文自然收束")
        self.assert_rules("formulaic-language.md", "妥否，请批示", "请予审批",
                          "请示、申请或请求批准的函有明确请批事项时", "内容已完整时可自然结束，不叠加多层尾语")
        self.assert_rules("genre-playbook-speech-address.md", "重点任务、体会或期望 → 与场合相称的收束",
                          "完整短稿仍表达清楚主题、已有内容和自然收束")
        self.assert_rules("writing-rules.md", "完成文种动作即可收束，指定尾语照录")
        self.assert_rules("anti-ai-patterns.md", "删除没有实际作用的夸大评价、充分性自证和口号")

    def test_v1511_anti_ai_frequency_review_is_prompt_driven_and_local(self) -> None:
        self.assert_rules("anti-ai-patterns.md", "以语境和句群为单位判断", "不按词表和出现次数机械替换",
                          "对比、递进和因果与内容关系一致", "必要否定照常保留，外围否定链合并",
                          "保留正式语气、必要否定、真实比较、引语、专业术语和原有状态",
                          "条件、可能性、否定范围、先后和论断强度")
        self.assert_rules("review-checklist.md", "用户限定范围时按其要求", "在本轮范围内直接修正有充分依据的问题")
        self.assert_rules("writing-rules.md", "整体查全文，局部查改动与关联内容")
        self.assert_rules("field-editing.md", "保留字段名、字段顺序和单元边界")

    def test_continuous_negation_is_position_independent_without_word_ban(self) -> None:
        self.assert_rules("anti-ai-patterns.md", "必要否定照常保留，外围否定链合并",
                          "不按词表和出现次数机械替换", "否定范围、先后和论断强度",
                          "供应商未定通常无需再逐项列合同、到货、验收和付款均未发生")
        self.assert_rules("genre-checklist-request.md", "供应商未定可以作为当前核心状态保留",
                          "下游否定链直接建议删除。材料另有独立办理需要时除外")
        self.assertNotIn("连续否定式收口", read_reference("anti-ai-patterns.md"))

    def test_sustained_progress_example_is_removed_only_from_redundant_cliche_list(self) -> None:
        self.assert_rules("anti-ai-patterns.md", "不按词表和出现次数机械替换", "且没有新增信息或不同作用时，改成直接表达",
                          "删除没有实际作用的夸大评价、充分性自证和口号", "用已有主体、动作、依据及结果说明问题")
        self.assert_rules("genre-checklist-request.md", "“持续推进、确保按期完成”没有材料给出的责任主体和期限时",
                          "不建议反向要求用户补齐套话依据", "优先删除，或回到材料已有的当前进展")

    def test_v150_genre_playbooks_keep_minimal_borrowing_boundaries(self) -> None:
        """Genre-specific field, actor and procurement boundaries survive mixed-page retirement."""
        owners = {
            "会议纪要": "genre-playbook-minutes.md", "征求意见函": "genre-playbook-correspondence.md",
            "工作总结": "genre-playbook-work-summary.md", "工作要点": "genre-playbook-work-priorities.md",
            "方案、实施方案": "genre-playbook-plan-construction.md",
            "调研、研究": "genre-playbook-research.md", "可研": "genre-playbook-feasibility.md",
            "采购公告": "genre-playbook-procurement-announcement.md", "独立审查意见、评审意见": "genre-playbook-review-opinion.md",
            "采购需求、规格报价、响应规则或履约条件需要专项核对": "genre-playbook-procurement-review.md",
            "讲话稿、致辞": "genre-playbook-speech-address.md",
        }
        for purpose, leaf in owners.items():
            self.assert_route(purpose, leaf)
        self.assertFalse((CANONICAL / "references/genre-playbooks.md").exists())
        self.assert_rules("genre-playbook-plan-construction.md", "按 `field-editing.md` 保留已有字段形态及本轮修改范围")
        self.assert_rules("field-editing.md", "改字段值只改指定字段", "不合并成连续句",
                          "拆成独立字段行后不要保留行尾分号或造成 `。；`")
        self.assert_route("周报、月报", "genre-playbook-report.md")
        self.assert_rules("genre-playbook-report.md", "字段式周报读取 `field-editing.md`，保持字段、顺序和换行",
                          "不因周期汇报新增服务单位责任或结果承诺")
        self.assert_rules("genre-playbook-procurement-review.md", "字段式采购清单或审查表读取 `field-editing.md`",
                          "保持字段边界、原值和本轮指定的修改范围")
        self.assert_rules("genre-playbook-review-opinion.md", "字段式审查材料读取 `field-editing.md`",
                          "只改点名字段时，其他字段名、顺序和原值保留")
        self.assert_rules("genre-playbook-minutes.md", "未给会议判断",
                          "责任或期限未给时不使用“按审核执行”“后续推进”等泛口径补齐")
        self.assert_rules("genre-playbook-speech-address.md", "称呼和受众沿用材料、用户要求或原稿",
                          "不为增加篇幅补写成效、受众、职责或部署")
        self.assert_rules("genre-playbook-procurement-announcement.md", "AI 算力场景按首页条件叠加 `ai-compute-docs.md`")
        self.assertIn("普通服务器、接口、安全、SLA 或验收内容单独出现时沿用主文种规则",
                      (CANONICAL / "SKILL.md").read_text(encoding="utf-8"))
        self.assertIn("保留字段名、字段顺序和单元边界", read_field_boundary(CANONICAL))
        self.assert_rules("ai-compute-docs.md", "主文种")

    def test_playbook_template_priority_uses_entry_semantics_without_leaf_duplication(self) -> None:
        duplicate = "每节只用于确定材料骨架和风险点。用户已有模板和字段顺序优先，不因 playbook 改掉真实模板、主送、落款、字段或附件关系。"
        leaves = ["genre-checklist-report.md", "genre-playbook-correspondence.md", "genre-playbook-work-summary.md",
                  "genre-playbook-minutes.md", "genre-playbook-plan-construction.md", "genre-playbook-request.md"]
        for root in skill_roots():
            with self.subTest(root=root):
                home = (root / "SKILL.md").read_text(encoding="utf-8")
                self.assertIn("用户已有提纲、模板、标题顺序或字段表时优先保留", home)
                self.assert_rules("writing-rules.md", "保留用户的标题、顺序、模板、字段、表格及指定空位", root=root)
                for leaf in leaves:
                    self.assertNotIn(duplicate, read_reference(leaf, root))

    def test_work_summary_elaboration_stays_in_target_section(self) -> None:
        """Work summaries keep supported next steps without claiming unobserved effects."""
        self.assert_route("工作总结", "genre-playbook-work-summary.md")
        self.assert_route("工作要点", "genre-playbook-work-priorities.md")
        self.assert_rules("genre-playbook-work-summary.md", "总结中的下一步安排承接本期工作",
                          "实际运行、测评或业务反馈支持时，再作运行稳定、效率改善或支撑能力等成效判断",
                          "材料支持的一般推进方向、自然延续或条件性预期可以分析",
                          "展望可以用自然的将来时表达", "材料明确为拟议、尚未决定或待评估时保留该状态",
                          "一般未来概括与保证效果分开", "“综上所述”等承接语按语境使用")
        self.assert_rules("genre-playbook-work-priorities.md", "以明确未来一段时期的工作方向和重点任务为主",
                          "责任、时间节点、协同机制和评价方式按材料或用户模板落位",
                          "实际成效仍需事实支持")
        self.assertFalse((CANONICAL / "references/genre-playbooks.md").exists())

    def test_ordinary_letter_leaf_is_self_contained_without_default_supplemental_reads(self) -> None:
        leaf = self.assert_route("征求意见函", "genre-playbook-correspondence.md")
        for rule in ["不相隶属单位间商洽、询问答复、征求意见、请求批准和答复审批事项",
                     "用平等沟通语气", "需要对方反馈时写清反馈路径", "称谓服从用户模板和已给主体",
                     "商请", "请予支持", "保留尚待批准的状态", "缺少授权或结论依据时不代作批准",
                     "材料已给或办理确有需要时，保留反馈期限、方式、联系人和附件",
                     "材料未给且不影响办理时不把这些内容补成固定要素"]:
            self.assertIn(rule, leaf)
        for unrelated in ["formal-addressing.md", "genre-checklist.md", "genre-playbooks.md"]:
            self.assertNotIn(unrelated, leaf)
        self.assertIn("上级答复下级请示用批复，转 `genre-playbook-reply.md`", leaf)

    def test_weak_model_suggestion_boundaries_stay_soft(self) -> None:
        self.assert_rules("writing-rules.md", "拟、建议、可选、进行中、待核和未决定保持原程度",
                          "主体、范围和强度与依据相称", "整体查全文，局部查改动与关联内容")
        self.assert_rules("genre-playbook-report.md", "评估报告或成本考察保留用户指定名称和事实口径",
                          "不改题为调研、方案或考核说明", "进行中、待核、建议和拟议状态保持原级别",
                          "建议尝试、考虑测试和下一步设想保持可选或拟议状态")
        self.assert_rules("anti-ai-patterns.md", "条件、可能性、否定范围、先后和论断强度")
        self.assert_rules("field-editing.md", "改字段值只改指定字段")

    def test_proofreading_layer_stays_ai_writing_quality_only(self) -> None:
        self.assert_rules("writing-rules.md", "用户要求校对，或引语、成语、专门术语需核准时，读取 `proofreading-checklist.md`")
        self.assert_rules("proofreading-checklist.md", "语言、引用和稿内一致性", "数字、金额、日期、比例、单位、专名和引用是否与材料一致",
                          "主体、对象、责任、时间、地点和状态在全文是否前后一致", "搭配错误",
                          "用户提供的成语按原语境保留", "明确误引、搭配不当或不合语境时，再调整为贴合原意的表达",
                          "按句法核对“的、地、得”", "定语通常用“的”，状语通常用“地”，程度、状态补语前常用“得”",
                          "固定短语和引语结合原文核对", "量词对应被计数的对象，区分文档份数、问题项数和设备台数",
                          "把握不足时保留原文并核查", "仅审核时给出位置、问题和建议")
        self.assert_rules("review-checklist.md", "结合上下文核对病句和搭配")
        self.assert_rules("prose-lint-usage.md", "合理用语及引用经核对可保留")
        self.assert_rules("writing-rules.md", "拟、建议、可选、进行中、待核和未决定保持原程度",
                          "移除已解决、已给定及无关事项", "遗留错误注明位置、未处理原因和下一步")

    def test_formalization_keeps_only_explicit_literal_boundaries_verbatim(self) -> None:
        self.assert_rules("anti-ai-patterns.md", "口语或情绪化表达用同义正式语体表述",
                          "语言调整保持原意、叙述身份、引用、主体、对象、条件、可能性、否定范围、先后和论断强度",
                          "“更稳、更省”分别保留稳定性和成本两层意思")
        self.assert_rules("writing-rules.md", "仅排版、逐字保留或不作分析的限制照办",
                          "材料与常识支持的原因、目的、影响、合理下一步、自然延续和结论可展开")
        self.assert_rules("proofreading-checklist.md", "用户给定的引语、原文及指定逐字保留内容，按原字面和原语境保留",
                          "明确要求改写这些内容时按授权修改", "数字、金额、日期、比例、单位、专名和引用是否与材料一致")
        self.assertNotIn("或只按给定材料时，分析层降为零", read_reference("writing-rules.md"))

    def test_v1510_sentence_fixes_keep_sparse_and_field_tasks_fact_bounded(self) -> None:
        self.assert_rules("genre-playbook-report.md", "材料未给某一环节时，直接在已给事实处收束",
                          "不为填满骨架增加责任、流程、成效、期限或结论")
        self.assert_rules("formulaic-language.md", "依据、会议、研究动作必须真实存在")
        self.assert_rules("field-editing.md", "保留字段名、字段顺序和单元边界")
        self.assert_rules("anti-ai-patterns.md", "保留用户已有字段与表格", "材料只是素材或用户要求改为叙述时再用自然段")
        self.assertNotIn("只有在用户要表格/字段时保留", read_reference("anti-ai-patterns.md"))

    def test_review_command_includes_interpreter_and_draft_path(self) -> None:
        """Validate the current command and exercise real stdin JSON delivery modes."""
        with self.subTest(contract="current prose-lint usage"):
            home = (CANONICAL / "SKILL.md").read_text(encoding="utf-8")
            common = read_reference("writing-rules.md")
            usage = read_reference("prose-lint-usage.md")
            self.assertIn("references/writing-rules.md", home)
            self.assertIn("prose-lint-usage.md", common)
            command = re.search(r'^python "[^\n]+"$', usage, re.M)
            self.assertIsNotNone(command)
            args = shlex.split(command.group(0))
            self.assertEqual(args[0], "python")
            self.assertTrue(args[1].replace("\\", "/").endswith("/scripts/prose_lint.py"))
            self.assertRegex(command.group(0), r'\s"[^"]+"$')
            self.assertIn("绝对路径", usage)
            self.assertCountEqual(args[2:-1], ["--delivery-mode", "draft-body", "--structure", "--format"])
            for term in ("标准输入", "`-`", "复扫", "已检查文本", "未完成"):
                self.assertIn(term, usage)
            for mode in ("draft-body", "gap-note-allowed", "review-only"):
                self.assertIn(f"`{mode}`", usage)
        draft = "通知\n\n请业务科于9月18日前提交材料。\n\n文后提示\n请补充联系人。"
        for mode, text, expect_note_risk in [
            ("draft-body", draft, True),
            ("gap-note-allowed", draft, False),
            ("review-only", "第2段日期与材料不符，建议按原日期修改。", False),
        ]:
            with self.subTest(delivery_mode=mode):
                run = subprocess.run(
                    [sys.executable, "-B", str(CANONICAL / "scripts/prose_lint.py"),
                     "--delivery-mode", mode, "--structure", "--format", "--json", "-"],
                    input=text, encoding="utf-8", capture_output=True, timeout=30,
                )
                self.assertEqual(run.returncode, 0, run.stderr)
                findings = json.loads(run.stdout)
                self.assertIsInstance(findings, list)
                self.assertEqual(
                    any(item["label"] == "unexpected-external-note" for item in findings),
                    expect_note_risk,
                )

    def test_ai_dedupe_prompt_fix_guidance_is_documented(self) -> None:
        for root in [CANONICAL, skill_roots()[-1]]:
            with self.subTest(root=root):
                self.assert_rules("writing-rules.md", "需要落款且未给日期时，用系统或工具确认的当天日期作为草稿日期",
                                  "指定留空、待确认或模板空位的按要求保留", "业务日期沿用材料",
                                  "仅排版、逐字保留或不作分析的限制照办",
                                  "具体经历、数值、期限、程序、责任、决定和成效须有依据",
                                  "影响文种成立、请批、执行或用户明示要求的缺项", "清理无用途占位",
                                  "正文编号、落款和附件在提示前结束", root=root)
                self.assert_rules("anti-ai-patterns.md", "只有换词重复、无新信息或不同作用时合并",
                                  "条件、可能性、否定范围、先后和论断强度", root=root)
                self.assert_rules("field-editing.md", "新增字段没有用户提供值时只写字段名并留空", root=root)

    def test_openclaw_agent_rules_include_v140_routing_and_format_bridge(self) -> None:
        root = skill_roots()[-1]
        home = (root / "SKILL.md").read_text(encoding="utf-8")
        canonical = (CANONICAL / "SKILL.md").read_text(encoding="utf-8")
        self.assertEqual(home.split("---", 2)[2].strip(), canonical.split("---", 2)[2].strip())
        for route in ["writing-rules.md", "format-gbt9704.md", "review-checklist.md"]:
            self.assertIn(f"`references/{route}`", home)
            self.assertEqual(read_reference(route, root), read_reference(route))
        self.assert_rules("writing-rules.md", "读取 `prose-lint-usage.md`", "`anti-ai-patterns.md`", "`proofreading-checklist.md`", root=root)
        for route in ["prose-lint-usage.md", "anti-ai-patterns.md", "proofreading-checklist.md"]:
            self.assertEqual(read_reference(route, root), read_reference(route))
        self.assertNotIn("workflow.md", home)
        self.assert_rules("writing-rules.md", "主体、对象、数字、金额、业务日期、引语、来源和事实状态照实保留",
                          "明确只要稿件或省略说明时省略提示", root=root)
        self.assert_rules("format-gbt9704.md", "不得把 Markdown `**加粗**`", root=root)

    def test_openclaw_skill_card_source_is_tracked_but_not_packaged_directly(self) -> None:
        source = (
            ROOT / "maintenance" / "docs" / "platform-snapshots" / "clawhub-v1.6.0" / "skill-card.md"
        ).read_text(encoding="utf-8")
        packaged_path = ROOT / "packages" / "openclaw" / "skills" / "chinese_official_writing" / "skill-card.md"

        self.assertIn("Known Risks and Mitigations", source)
        self.assertFalse(packaged_path.exists())

    def test_openclaw_skill_card_uses_absolute_links_and_key_genres(self) -> None:
        skill = read_routing_surfaces(CANONICAL / "SKILL.md")
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
            "1.6.26 短意见、投诉反映与语义减载",
            "1.6.25 意见建议、建议反馈与标题版式",
            "1.6.24 短稿语义路由与 Hook 说明顺序",
            "1.6.28 Hook修复与新闻事实日期",
            "1.6.27 整改方案、命令路径与投诉页精简",
            "明川市政务服务中心服务事项信息变更管理办法（试行）",
            "release-1.6.27.md",
            "release-1.6.27-rc.md",
            "remediation-plan-r1/candidate-r2-result.md",
            "recent-leaf-cleanup-r1/result.md",
            "reference-route-audit-r1/result.md",
            "新闻与评论写作",
            "maintenance/tests/evidence",
            "maintenance/docs/evidence/README.md",
            "普通 Skill、references、普通检查脚本与兼容包采用 [MIT License](LICENSE)。",
        ]:
            self.assertIn(term, text)
        recent_table = text.split("## 模型消融与真实写稿", 1)[1].split("### 制度正文示例", 1)[0]
        self.assertEqual(8, sum(1 for line in recent_table.splitlines() if line.startswith("|")))
        self.assertNotIn("50k+", recent_table)
        self.assertNotIn("SkillHub downloads", recent_table)
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
            "材料暂缺时完成有依据的正文",
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
