"""Bounded R20 migration of historical method responsibilities to current owners."""
from pathlib import Path
import ast
import hashlib
import json
import textwrap

ROOT = Path(__file__).resolve().parents[4]
EVIDENCE = Path(__file__).resolve().parent
TARGET = ROOT / "maintenance/tests/test_skill_boundary.py"
BASELINE = EVIDENCE / "baseline-test_skill_boundary.py"
CHANGES = {}


def change(name, group, note, body):
    CHANGES[name] = {"group": group, "migration": note, "body": textwrap.dedent(body.replace("\r\n", "\n")).strip()}


change("test_canonical_skill_declares_positive_trigger_boundary", "G07", "入口不再重复事实和检查章节；保持触发范围及 README 责任说明，显式验证入口到共性页。", '''
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
''')

change("test_ai_compute_detail_is_loaded_from_specialty_reference", "G02/G08", "保留算力条件、主叶/叠加页角色及四个正式术语；内部缩写核查迁到当前反 AI 页。", '''
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
''')

change("test_adapter_skill_copies_keep_boundaries", "G07", "五个 adapter 分别验证入口及自己的事实/签发责任页，不再要求首页重列细项。", '''
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
''')

change("test_delivery_scope_rule_is_naturalized_across_current_skill_copies", "G07", "六根逐一保护正文清理、业务声明、表格附件及消息提示；正文同一性仍比较所有入口。", '''
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
''')

change("test_drafting_rules_are_split_for_prompt_following", "G08", "取消独立短材料模式，保留需求先于文种、任务动作及完整的统一共性流程。", '''
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
''')

change("test_long_form_headings_warn_against_markdown_bold", "G03", "纯文本标题/Markdown 例外归入口，Word 标记清理归格式页；整稿代码围栏和横线责任另以3个真实CLI正反例保留。", '''
    home = (CANONICAL / "SKILL.md").read_text(encoding="utf-8")
    self.assertIn("纯文本主标题独立成行", home)
    self.assertIn("用户明确要求 Markdown 时使用对应格式", home)
    self.assert_rules("format-gbt9704.md", "不得把 Markdown `**加粗**`、代码块或 `###` 标题标记原样带入正式 Word",
                      "段首题、编号正文句或用户模板明确接排时仍按正文标点处理")
    self.assert_rules("proofreading-checklist.md", "Markdown 残留是否符合交付形态")
    # The retired short-draft page also protected whole-body wrappers.
    # Exercise the surviving detector instead of losing that responsibility.
    for draft, expected in [
        ("```text\\n关于提交材料的通知\\n请提交材料。\\n```", {"markdown-code-fence"}),
        ("关于提交材料的通知\\n\\n请提交材料。\\n---\\n补充说明。", {"markdown-horizontal-rule"}),
        ("关于提交材料的通知\\n\\n请提交材料。", set()),
    ]:
        with self.subTest(wrappers=expected):
            run = subprocess.run(
                [sys.executable, "-B", str(CANONICAL / "scripts/prose_lint.py"),
                 "--delivery-mode", "draft-body", "--format", "--json", "-"],
                input=draft, encoding="utf-8", capture_output=True, timeout=30,
            )
            self.assertEqual(run.returncode, 0, run.stderr)
            wrappers = {item["label"] for item in json.loads(run.stdout)
                        if item["label"] in {"markdown-code-fence", "markdown-horizontal-rule"}}
            self.assertEqual(wrappers, expected)
''')

change("test_plain_text_title_boundary_contract_is_explicit", "G03", "保留四个独立责任：主标题独行无句号、标题后空行、层级标题与正文分开、编号完整句保留标点。", '''
    home = (CANONICAL / "SKILL.md").read_text(encoding="utf-8")
    for rule in ["纯文本主标题独立成行，行末省略句号，标题后空一行",
                 "层级标题省略行末句号，与其统领的正文分段",
                 "编号内容本身是完整正文句时，保留正常句末标点",
                 "用户模板优先；用户明确要求 Markdown 时使用对应格式",
                 "Word 小标题是否独立成段按模板和实际统领关系判断"]:
        with self.subTest(responsibility=rule):
            self.assertIn(rule, home)
''')

change("test_style_references_keep_precise_routes_without_common_error_catchall", "G04", "正式语体并入反 AI 页；保留所有成稿/改稿/审核的显式入口→共性→反 AI 链。", '''
    home = (CANONICAL / "SKILL.md").read_text(encoding="utf-8")
    self.assertIn("`references/writing-rules.md`", home)
    self.assert_rules("writing-rules.md", "所有成稿、改后稿和审核任务读取 `anti-ai-patterns.md` 检查语言")
    self.assert_rules("anti-ai-patterns.md", "口语或情绪化表达用同义正式语体表述", "保留正式语气")
    self.assertFalse((CANONICAL / "references/official-style.md").exists())
    self.assertNotIn("其他口语化、标题漂移、重复事项、格式噪点", home)
    self.assertNotIn("## 常见错误反例", home)
''')

change("test_second_revision_fact_mapping_has_one_complete_entry_rule", "G06", "不复刻内部映射表/特定纠错口令；保护本轮更正、旧来源复核、不回退、先交正文及保留未解事项。", '''
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
''')

change("test_reference_loading_table_keeps_progressive_disclosure", "G08", "保留单主叶与条件资料，取消短稿卡片终点，全部任务承接统一共性流程。", '''
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
''')

change("test_lightened_indices_resolve_from_each_skill_root_and_keep_quality_bridges", "G07", "六根保留显式两跳、索引目标存在和正文一致；检查桥改成当前共性页的三条实际链接。", '''
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
''')

change("test_task_route_cards_keep_sparse_tasks_lightweight", "G08", "取消卡片/短材料分流；保留局部范围、默认完整短稿下限和稀疏材料的纪要/通知语义。", '''
    self.assertFalse((CANONICAL / "references/task-route-cards.md").exists())
    self.assert_rules("writing-rules.md", "普通完整短稿至少80字", "局部替换、字段处理或明确要求更短时按实际范围处理",
                      "整体查全文，局部查改动与关联内容", "先完成可用正文")
    self.assert_rules("field-editing.md", "改字段值只改指定字段")
    self.assert_rules("structure-editing.md", "用户要求“补一句”时只补一句或短句")
    self.assert_route("会议纪要", "genre-playbook-minutes.md")
    self.assert_route("通知", "genre-playbook-notice.md")
    self.assert_rules("genre-playbook-minutes.md", "建议、待议和未形成决定的内容保持相应状态", "不补写“会议认为”“会议强调”")
    self.assert_rules("genre-playbook-notice.md", "不为了形成通知格式补整改、会议、责任或期限", "不能为了显得完整新增办理承诺")
''')

change("test_missing_metric_visibility_does_not_become_plan_state", "G06", "缺信息与业务未定、暂无结果与是否启动仍分开；外围缺项用当前交付范围约束。", '''
    self.assert_rules("writing-rules.md", "分清信息未给与业务未定、暂无结果与是否启动",
                      "拟、建议、可选、进行中、待核和未决定保持原程度",
                      "影响文种成立、请批、执行或用户明示要求的缺项", "移除已解决、已给定及无关事项")
''')

change("test_light_route_is_terminal_until_an_explicit_escalation_condition", "G08", "旧终点与升级门取消；当前为不依长度选主叶、共性复核、局部范围和审核/改稿分交付。", '''
    home = (CANONICAL / "SKILL.md").read_text(encoding="utf-8")
    self.assertIn("以用户模板、最新版底稿、明确标题和用途选路", home)
    self.assertIn("选定主文种后，读取 `references/writing-rules.md`", home)
    self.assert_rules("writing-rules.md", "整体查全文，局部查改动与关联内容",
                      "实质修改后核对关联内容并复扫，影响篇幅时另测字数")
    self.assert_rules("review-checklist.md", "仅要求审核时交付意见", "要求审核后修改、复核后修改或优化稿件时",
                      "在本轮范围内直接修正有充分依据的问题", "交付完整改后稿")
    self.assertFalse((CANONICAL / "references/task-route-cards.md").exists())
''')

change("test_sparse_notice_does_not_treat_delivery_channel_as_issuer", "G01", "不要求旧邮箱例句；同时保护通知对象/落款已有信息及审核发文/动作角色，具体渠道输入仍需实稿证据。", '''
    self.assert_route("通知", "genre-playbook-notice.md")
    self.assert_rules("genre-playbook-notice.md", "通知对象由材料或用户给出时保留原称谓",
                      "落款主体和文号采用已有信息",
                      "参加、报送、组织人员、反馈和办理等动作只在材料或用户明确给出时写入")
    self.assert_rules("writing-rules.md", "主体、对象、数字、金额、业务日期、引语、来源和事实状态照实保留")
    self.assert_rules("review-checklist.md", "发文主体和动作主体分别按材料核对", "保持各自角色与原有状态")
''')

change("test_workflow_sparse_line_relief_keeps_carriers_and_route_graph", "G08", "保留报告事实载体与缺环节收束，不再断言已撤的 workflow/短稿卡。", '''
    self.assertFalse((CANONICAL / "references/workflow.md").exists())
    self.assert_route("报告、情况报告", "genre-playbook-report.md")
    self.assert_rules("genre-playbook-report.md", "材料未给某一环节时，直接在已给事实处收束",
                      "不为填满骨架增加责任、流程、成效、期限或结论",
                      "字段式、表单式和清单式材料保留字段名、顺序、数字和换行")
    self.assert_rules("writing-rules.md", "围绕事项组织自然段", "完成文种动作即可收束")
    self.assert_rules("anti-ai-patterns.md", "同一事项只有换词重复、无新信息或不同作用时合并")
''')

change("test_multi_round_revision_rules_keep_structure_and_genre_format", "G06", "结构页原有细粒度全留，最终校核改接统一共性页并增加删除事项复现检查。", '''
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
''')

change("test_legal_genres_have_checklist_and_handling_elements", "G08", "取消额外通用办理表，保留各法定文种功能并按主叶核必要办理字段；兜底仅用于未覆盖用途。", '''
    for purpose, leaf, function in [("公告、公示、通告", "genre-playbook-publication.md", "应知、应遵或应办理"),
                                    ("决议", "genre-playbook-resolution.md", "通过"),
                                    ("意见", "genre-playbook-opinion.md", "指导")]:
        self.assertIn(function, self.assert_route(purpose, leaf))
    self.assert_rules("reference-index.md", "用途已明确且没有适用专页时，读取 `genre-checklist.md`")
    self.assert_rules("genre-checklist.md", "结合主体、接收对象和用途核对行文关系", "保留用户限定的标题和字段")
    self.assert_rules("genre-playbook-publication.md", "公示对象、期限、异议或反馈渠道及联系人", "材料未给期限或渠道时保留缺项，不编造")
    self.assert_rules("writing-rules.md", "按主文种写全要素、缘由、用途和合理衔接",
                      "影响文种成立、请批、执行或用户明示要求的缺项")
''')

change("test_genre_authority_uses_the_defined_routing_source", "G08", "决策表改为冲突判定页；保留用途、行文关系、批准权限和官方来源责任。", '''
    home = (CANONICAL / "SKILL.md").read_text(encoding="utf-8")
    self.assertIn("标题、模板、正文用途或行文关系有冲突时，先读 `references/genre-routing.md` 判定，再选主叶", home)
    self.assert_rules("genre-routing.md", "依据主要办理或表达目的选文种", "结合收文方权限和行文关系确定文种",
                      "不相隶属单位间商洽、询答、请求批准或在权限范围内答复审批事项，按函或复函处理",
                      "上级答复下级请示按批复处理")
    self.assert_rules("external-research.md", "优先查看官方规范和公开正式文本", "用户业务事实仍以用户材料为准")
''')

change("test_report_checklist_is_routed_as_an_atomic_leaf", "G08", "按当前索引的报告功能/状态存疑条件检查细查页，保留接口原词、原因责任、汇报/请批区分。", '''
    draft = self.assert_route("报告、情况报告", "genre-playbook-report.md")
    self.assert_route("报告功能或状态表达拿不准时", "genre-checklist-report.md")
    self.assert_rules("genre-checklist-report.md", "文种核对", "没有夹带审批请求", "保留用户指定名称",
                      "接口、系统、页面、数字、日期、单位和进行中/待核/建议状态是否保持原词和原强度")
    self.assertNotIn("成稿骨架", read_reference("genre-checklist-report.md"))
    for rule in ["成稿骨架", "报告事项与范围", "使用事实性汇报语言", "结论先行或按时间顺序均可",
                 "不改题为调研、方案或考核说明", "原因、责任、损失或整改结论以材料为准"]:
        self.assertIn(rule, draft)
    self.assertFalse((CANONICAL / "references/genre-playbooks.md").exists())
''')

change("test_minutes_playbook_is_routed_as_an_atomic_leaf", "G08", "撤卡片条件；纪要专页的建议归属、待议及责任期限缺失均继续显式验证。", '''
    leaf = self.assert_route("会议纪要", "genre-playbook-minutes.md")
    for rule in ["重点是议定事项、责任、期限和后续动作", "不补写“会议认为”“会议强调”",
                 "建议、待议和未形成决定的内容保持相应状态", "不编造“会议决定”",
                 "发言人的建议、判断和条件逐项对照记录，归属保持一致",
                 "责任或期限未给时不使用“按审核执行”“后续推进”等泛口径补齐"]:
        self.assertIn(rule, leaf)
    self.assertFalse((CANONICAL / "references/genre-playbooks.md").exists())
''')

change("test_request_playbook_is_routed_as_an_atomic_leaf", "G08", "保留完整申请理由、短稿非强制、请假理由和后续未定状态；缺项转当前 writing-rules 而非撤页。", '''
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
''')

change("test_institution_rules_have_a_dedicated_routed_leaf", "G08", "首页直链改索引行；增加制度权限及通知壳/附件独立核对责任，保留 Word 条件。", '''
    self.assertIn("制度", read_frontmatter(CANONICAL / "SKILL.md")["description"])
    leaf = self.assert_route("制度、规定、办法", "genre-playbook-institution-rules.md")
    for rule in ["管理办法", "实施细则", "内容较短、事项单一时连续列条", "通知壳只写发布对象、执行要求和附件关系",
                 "围绕实际操作顺序写清主体、触发条件、步骤、时限、结果和记录", "仅在材料明确时写入",
                 "同时读取 `format-gbt9704.md`", "不把建议或协助升级为审批权、处罚权或最终责任",
                 "制度正文作为附件独立成文、独立复核", "未决状态、过渡安排和例外条件按原状态承载"]:
        self.assertIn(rule, leaf)
''')

change("test_news_genres_are_defined_in_authoritative_routing", "G08", "撤旧决策表但不撤消息/纪要/评论用途分工；在各实际主叶保护事实/观点边界。", '''
    self.assert_route("新闻消息、活动报道", "genre-playbook-news-message.md")
    self.assert_route("新闻评论、时评", "genre-playbook-news-commentary.md")
    self.assert_rules("genre-routing.md", "依据主要办理或表达目的选文种", "纪要按会议事项组织")
    self.assert_rules("genre-playbook-news-message.md", "新闻消息以报道已发生事实为主",
                      "以评论公共议题为主要用途的稿件读取 `genre-playbook-news-commentary.md`")
    self.assert_rules("genre-playbook-news-commentary.md", "事实保持原有主体、数字、时间和状态，推演保持为观点",
                      "具体政策、数据、具名责任、期限或承诺以材料为准")
    self.assert_rules("genre-playbook-minutes.md", "不写成会议新闻")
''')

change("test_final_drafts_must_not_keep_unfinished_placeholders", "G06", "旧缺日期默认省略契约被当前已确认当天草稿日期取代；保留业务日期、指定留空及正式签发边界。", '''
    home = (CANONICAL / "SKILL.md").read_text(encoding="utf-8")
    self.assert_rules("writing-rules.md", "业务日期沿用材料，年份可继承明确语境",
                      "需要落款且未给日期时，用系统或工具确认的当天日期作为草稿日期",
                      "指定留空、待确认或模板空位的按要求保留", "字段、表格及指定空位，清理无用途占位")
    self.assert_rules("format-gbt9704.md", "最终正文不要残留 `〔签发日期〕`、`〔会议时间〕` 等未完成占位",
                      "正式签发日期以用户或材料确认的信息为准", "不得编造文号、密级、紧急程度、签发人、印章、正式签发日期和版记信息")
    for placeholder in ["〔签发日期〕", "〔会议时间〕", "[具体项目名称]", "XXXX万元",
                        "YYYY年MM月DD日", "（签发日期）", "（成文日期待确认）"]:
        self.assertNotIn(placeholder, home)
''')

change("test_revision_workflow_forbids_new_unprovided_facts", "G06", "最新版/本轮更正、具体事实需依据、合理分析授权及只交正文并存；不再把来源限定等同零分析。", '''
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
''')

change("test_staged_review_workflow_remains_intact", "G06/G08", "旧首页五阶段改当前共性四步，保留整体/局部、关联校核、复扫及字数重测而非旧微阶段。", '''
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
''')

change("test_v140_mode_routing_material_mapping_and_format_bridge_are_documented", "G04/G06/G08", "模式、事实保真、审核强度、反 AI 风险族和 Word 衔接继续分具体责任检查。", '''
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
''')

change("test_v141_formal_delivery_review_and_tone_rules_are_documented", "G04/G08", "审核意见/改后稿、全文默认、局部范围、具体定位和文外格式提示保留；正式语体以强度及角色保真代替例句。", '''
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
''')

change("test_candidate_ac_anchors_fact_relations_to_explicit_material", "G06", "年份禁补改成只继承明确语境；合计差额不推出其余正常，以及因果/条件关系继续保护。", '''
    self.assert_rules("writing-rules.md", "主体、对象、数字、金额、业务日期、引语、来源和事实状态照实保留",
                      "业务日期沿用材料，年份可继承明确语境", "合计差额可核算，不据此认定其余正常",
                      "主体、范围和强度与依据相称，多种解释保留不确定性")
    self.assert_rules("argument-chains.md", "同一段围绕一个主要事项展开", "判断所依据的事实或条件、两者之间的关系",
                      "推断与已经发生的事实分别表述")
''')

change("test_fact_sufficiency_guidance_is_soft_and_non_blocking", "G06", "先交可用正文、限定实质缺项、次级可选、清理无关提示及遗留问题接续继续明确保护。", '''
    self.assert_rules("writing-rules.md", "先完成可用正文，实质缺项集中在文后提示",
                      "拟、建议、可选、进行中、待核和未决定保持原程度",
                      "影响文种成立、请批、执行或用户明示要求的缺项", "上轮未解决事项和已发现未处理错误",
                      "移除已解决、已给定及无关事项", "明确只要稿件或省略说明时省略提示")
    self.assert_rules("review-checklist.md", "需补材料限于影响文种成立、请批事项、执行或用户明示要求的缺项，并说明影响",
                      "已有依据足以支持基本判断时，次级材料作为可选补充")
    self.assertNotIn("暂停确认", read_reference("writing-rules.md"))
''')

change("test_v147_minimal_borrowing_rules_stay_soft_and_prompt_based", "G04/G06/G08", "保留 Word 排版/允许改稿区别、模板格式、素材来源和合理推断；旧口语例句改保真语义，不声称逐例已验证。", '''
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
''')

change("test_v148_anti_ai_borrowing_stays_soft_and_official", "G02/G04", "保留语境判断、重复修复和身份强度；Token 与调用次数分别列项及计费单位在算力页，专项实稿仍未覆盖。", '''
    self.assert_rules("anti-ai-patterns.md", "以语境和句群为单位判断", "不按词表和出现次数机械替换",
                      "相邻段落反复同样开头、连续排比或口号结尾", "叙述身份", "论断强度",
                      "必要英文、产品名、型号和缩写沿用正式拼写")
    self.assert_rules("writing-rules.md", "整体查全文，局部查改动与关联内容")
    self.assert_rules("review-checklist.md", "分清已确认错误、待核实风险和可选表达建议")
    self.assert_rules("ai-compute-docs.md", "Token、调用次数、用户数、峰值并发",
                      "单位保持一致。以 Token 为主线时承接费用测算", "不与 Token 单价混作同一成本口径")
    self.assert_rules("proofreading-checklist.md", "数字、金额、日期、比例、单位、专名和引用是否与材料一致")
''')

change("test_v1601_j1_writing_endings_use_natural_terms", "G08", "取消收束词禁词和短稿页；请批函当前合法范围、自然结尾、指定尾语和无证据口号分别保留。", '''
    self.assert_rules("genre-playbook-news-commentary.md", "论点已经充分展开时，正文自然收束")
    self.assert_rules("formulaic-language.md", "妥否，请批示", "请予审批",
                      "请示、申请或请求批准的函有明确请批事项时", "内容已完整时可自然结束，不叠加多层尾语")
    self.assert_rules("genre-playbook-speech-address.md", "重点任务、体会或期望 → 与场合相称的收束",
                      "完整短稿仍表达清楚主题、已有内容和自然收束")
    self.assert_rules("writing-rules.md", "完成文种动作即可收束，指定尾语照录")
    self.assert_rules("anti-ai-patterns.md", "删除没有实际作用的夸大评价、充分性自证和口号")
''')

change("test_v1511_anti_ai_frequency_review_is_prompt_driven_and_local", "G04", "不按次数禁词，保留关系真实、必要否定/引用术语、局部范围与字段原貌。", '''
    self.assert_rules("anti-ai-patterns.md", "以语境和句群为单位判断", "不按词表和出现次数机械替换",
                      "对比、递进和因果与内容关系一致", "必要否定照常保留，外围否定链合并",
                      "保留正式语气、必要否定、真实比较、引语、专业术语和原有状态",
                      "条件、可能性、否定范围、先后和论断强度")
    self.assert_rules("review-checklist.md", "用户限定范围时按其要求", "在本轮范围内直接修正有充分依据的问题")
    self.assert_rules("writing-rules.md", "整体查全文，局部查改动与关联内容")
    self.assert_rules("field-editing.md", "保留字段名、字段顺序和单元边界")
''')

change("test_continuous_negation_is_position_independent_without_word_ban", "G04", "否定作用与原范围继续检查，保留供应商未定/下游否定链的具体反例和独立办理例外。", '''
    self.assert_rules("anti-ai-patterns.md", "必要否定照常保留，外围否定链合并",
                      "不按词表和出现次数机械替换", "否定范围、先后和论断强度",
                      "供应商未定通常无需再逐项列合同、到货、验收和付款均未发生")
    self.assert_rules("genre-checklist-request.md", "供应商未定可以作为当前核心状态保留",
                      "下游否定链直接建议删除。材料另有独立办理需要时除外")
    self.assertNotIn("连续否定式收口", read_reference("anti-ai-patterns.md"))
''')

change("test_sustained_progress_example_is_removed_only_from_redundant_cliche_list", "G04/G08", "不强留旧套话名单位置；持续推进的具体无主体期限责任由申请细查页承接，不反向补造依据。", '''
    self.assert_rules("anti-ai-patterns.md", "不按词表和出现次数机械替换", "且没有新增信息或不同作用时，改成直接表达",
                      "删除没有实际作用的夸大评价、充分性自证和口号", "用已有主体、动作、依据及结果说明问题")
    self.assert_rules("genre-checklist-request.md", "“持续推进、确保按期完成”没有材料给出的责任主体和期限时",
                      "不建议反向要求用户补齐套话依据", "优先删除，或回到材料已有的当前进展")
''')

change("test_playbook_template_priority_uses_entry_semantics_without_leaf_duplication", "G06/G07", "模板优先与固定字段改接现共性页，保留六根及原六叶无重复历史段的检查。", '''
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
''')

change("test_ordinary_letter_leaf_is_self_contained_without_default_supplemental_reads", "G08", "保留函件平等关系/权限及有条件反馈，不再强留已删例句、结尾清单或默认补读链；新增请批/审批答复有效功能。", '''
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
''')

change("test_weak_model_suggestion_boundaries_stay_soft", "G06", "共性状态、报告中的评估/拟测试/可选及反 AI 条件强度共同承接，不再要求首页列全旧状态词。", '''
    self.assert_rules("writing-rules.md", "拟、建议、可选、进行中、待核和未决定保持原程度",
                      "主体、范围和强度与依据相称", "整体查全文，局部查改动与关联内容")
    self.assert_rules("genre-playbook-report.md", "评估报告或成本考察保留用户指定名称和事实口径",
                      "不改题为调研、方案或考核说明", "进行中、待核、建议和拟议状态保持原级别",
                      "建议尝试、考虑测试和下一步设想保持可选或拟议状态")
    self.assert_rules("anti-ai-patterns.md", "条件、可能性、否定范围、先后和论断强度")
    self.assert_rules("field-editing.md", "改字段值只改指定字段")
''')

change("test_proofreading_layer_stays_ai_writing_quality_only", "G04", "校对触发从共性页显式到达；成语原语境、误用例外、的地得句法、量词对象及低把握核查逐项保留。", '''
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
''')

change("test_formalization_keeps_only_explicit_literal_boundaries_verbatim", "G04", "普通口语正式化与给定引语/逐字原文分开；不以同义改写覆盖明确逐字边界。", '''
    self.assert_rules("anti-ai-patterns.md", "口语或情绪化表达用同义正式语体表述",
                      "语言调整保持原意、叙述身份、引用、主体、对象、条件、可能性、否定范围、先后和论断强度",
                      "“更稳、更省”分别保留稳定性和成本两层意思")
    self.assert_rules("writing-rules.md", "仅排版、逐字保留或不作分析的限制照办",
                      "材料与常识支持的原因、目的、影响、合理下一步、自然延续和结论可展开")
    self.assert_rules("proofreading-checklist.md", "用户给定的引语、原文及指定逐字保留内容，按原字面和原语境保留",
                      "明确要求改写这些内容时按授权修改", "数字、金额、日期、比例、单位、专名和引用是否与材料一致")
    self.assertNotIn("或只按给定材料时，分析层降为零", read_reference("writing-rules.md"))
''')

change("test_v1510_sentence_fixes_keep_sparse_and_field_tasks_fact_bounded", "G04/G08", "报告稀疏边界和依据真实性不变；既有字段/素材转叙述的条件迁到当前反 AI 表达。", '''
    self.assert_rules("genre-playbook-report.md", "材料未给某一环节时，直接在已给事实处收束",
                      "不为填满骨架增加责任、流程、成效、期限或结论")
    self.assert_rules("formulaic-language.md", "依据、会议、研究动作必须真实存在")
    self.assert_rules("field-editing.md", "保留字段名、字段顺序和单元边界")
    self.assert_rules("anti-ai-patterns.md", "保留用户已有字段与表格", "材料只是素材或用户要求改为叙述时再用自然段")
    self.assertNotIn("只有在用户要表格/字段时保留", read_reference("anti-ai-patterns.md"))
''')

change("test_ai_dedupe_prompt_fix_guidance_is_documented", "G04/G06/G07", "两包保护去重不失条件/强度，日期按现契约，缺项限域并清理占位，提示始终在正文外。", '''
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
''')

change("test_openclaw_agent_rules_include_v140_routing_and_format_bridge", "G07", "OpenClaw 保留首页和当前共性/格式/审核/扫描正文同一性，实际检查链允许经共性页到达。", '''
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
''')


def migrate():
    raw = BASELINE.read_bytes()
    if (EVIDENCE / "module-run.json").exists():
        raise RuntimeError("R20 validation is frozen; do not overwrite the reviewed test module")
    source = raw.decode("utf-8")
    tree = ast.parse(source)
    lines = source.splitlines(keepends=True)
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "SkillBoundaryTests")
    methods = {n.name: n for n in cls.body if isinstance(n, ast.FunctionDef)}
    # Small unchanged-contract wording/path migrations remain explicit and auditable.
    replacements = {
        "test_sparse_length_rule_keeps_fact_boundary_without_short_first_priority": [
            ('r"仍不足[^。]*实际差额[^。]*不报达标"', 'r"仍不足[^。]*实际差额[^。]*不报达标"')],
        "test_reported_genre_coverage_gaps_have_minimum_support": [
            ('"征求意见函必须给反馈路径"', '"需要对方反馈时写清反馈路径"'),
            ('"响应期限、提交方式、联系人"', '"响应期限和提交方式", "联系方式、公告期限、附件",\n                          "只提示影响当前发布目的的缺项"')],
        "test_request_review_checklist_is_routed_as_an_atomic_leaf": [
            ('self.assert_route("文种专项复核",', 'self.assert_route("请批事项或必要要素拿不准时",')],
        "test_news_commentary_leaf_is_bounded_and_non_templated": [
            ('"直接判断、事实解释和自然衔接",', '"评论推演逐句核对依据和适用范围",')],
        "test_v141_search_boundary_stays_lightweight_and_opt_in": [
            ('self.assert_rules("handling-elements.md", "尚不熟悉通用写法或必备要素时读取 `external-research.md`")',
             'self.assert_rules("genre-checklist.md", "通用写法、必备要素或格式不熟悉时，按首页的核查规则定向查证")')],
    }
    notes = {
        "test_reported_genre_coverage_gaps_have_minimum_support": ("G08", "反馈路径保持按办理目的触发，采购公告渠道仍具体核对。"),
        "test_request_review_checklist_is_routed_as_an_atomic_leaf": ("G08", "只替换索引细查条件；请批语/两行标题/模板/缺项及位置全部原断言保留。"),
        "test_news_commentary_leaf_is_bounded_and_non_templated": ("G08", "当前语义为推演逐句核对依据/适用范围；完整时间锚、约数篇幅、每段论点等全部保留。"),
        "test_v141_search_boundary_stays_lightweight_and_opt_in": ("G08", "撤办理要素页桥，兜底改按首页核查规则；两类触发、来源、一次补搜及停止责任不改。"),
    }
    for name, pairs in replacements.items():
        node = methods[name]
        body = "".join(lines[node.lineno:node.end_lineno])
        changed = body
        for before, after in pairs:
            if before not in changed:
                raise AssertionError((name, before))
            changed = changed.replace(before, after)
        if changed != body:
            group, note = notes[name]
            change(name, group, note, changed)
    # This method also retains maintenance-history assertions outside product rules.
    name = "test_v144_common_real_writing_risks_and_adoption_gate_are_documented"
    node = methods[name]
    old = "".join(lines[node.lineno:node.end_lineno])
    maintenance_tail = old[old.index('        agents = '):old.index('        for owner in ')]
    new = '''
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
    '''
    new = textwrap.dedent(new).strip() + "\n" + textwrap.dedent(maintenance_tail).strip() + '''

for owner in ["writing-rules.md", "review-checklist.md", "genre-checklist.md"]:
    text = read_reference(owner)
    self.assertNotIn("prompt/markdown", text)
    self.assertNotIn("社区技能", text)
'''
    change(name, "G04/G06/G08", "缺项/篇幅/去重/Word 保真迁当前页，原维护细则和历史证据责任原样保留。", new)
    for name, change_ in sorted(CHANGES.items(), key=lambda item: methods[item[0]].lineno, reverse=True):
        node = methods[name]
        replacement = "    def " + name + "(self) -> None:\n" + textwrap.indent(change_["body"], "        ") + "\n"
        lines[node.lineno - 1:node.end_lineno] = [replacement]
    updated = "".join(lines)
    ast.parse(updated)
    test_names = lambda s: {n.name for n in ast.walk(ast.parse(s)) if isinstance(n, ast.FunctionDef) and n.name.startswith("test_")}
    assert test_names(source) == test_names(updated) and len(test_names(updated)) == 81
    assert 'CURRENT_VERSION = "1.6.30"' in updated and 'PUBLISHED_VERSION = "1.6.30"' in updated
    assert not any(isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr in {"skip", "skipTest", "expectedFailure"} for n in ast.walk(ast.parse(updated)))
    TARGET.write_bytes(updated.replace("\r\n", "\n").replace("\n", "\r\n").encode("utf-8"))
    catalog = [{"method": name, "group": c["group"], "migration": c["migration"]} for name, c in CHANGES.items()]
    (EVIDENCE / "migration-catalog.json").write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", "utf-8")
    print(json.dumps({"changed_methods": len(CHANGES), "method_count": 81, "baseline_sha256": hashlib.sha256(raw).hexdigest(),
                      "candidate_sha256": hashlib.sha256(TARGET.read_bytes()).hexdigest()}, ensure_ascii=False))


if __name__ == "__main__":
    migrate()
