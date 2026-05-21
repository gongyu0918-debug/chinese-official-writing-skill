---
name: chinese-official-writing
description: 用于起草、改写和复核中文公文及正式工作材料；当用户明确要求中文通知、请示、报告、说明、方案、申请、函、复函、批复、意见、决定、公告、公示、通报、会议纪要、工作要点、工作总结、调研报告、可研报告、实施方案、建设方案、审查材料、AI 算力服务可研、算力采购或租赁、GPU/服务器租赁、技术服务需求，或要求正式文稿顺稿、压缩、去口语化、降 AI 味、文种校验、办理要素核对时使用；强调文种准确、主体视角稳定、事实克制、数据可追溯、公文语气自然。不用于英文写作、文学创作、营销文案、社交媒体文案、模型训练、批量语料生成、批量改写未知来源文本、规避人工审核、替代法律/财务/采购/审计/政策依据判断。
license: MIT-0
version: "1.2.17"
metadata:
  version: "1.2.17"
  compatible_agents:
    - codex
    - claude-code
    - deepseek-tui
    - openclaw
    - hermes
    - qwen-code
    - kimi-code
    - generic-skill-md-agent
  qwen_code:
    install_personal: "~/.qwen/skills/chinese-official-writing"
    install_project: ".qwen/skills/chinese-official-writing"
    entry: "SKILL.md"
  kimi_code:
    skills_dir: "copy folder or pass with --skills-dir"
    invocation: "/skill:chinese-official-writing"
    entry: "SKILL.md"
  hermes:
    version: "1.2.17"
    category: writing
    display_name: "中文公文写作"
    tags:
      - chinese
      - official-document
      - formal-writing
      - ai-compute
---

# 中文公文写作

使用本技能生成或修改中文正式文稿。最终文本应像文稿正文，而不是写作说明、概念讲解或外部顾问点评。

## 触发条件与边界

仅在用户任务属于中文公文或中文正式工作材料时启用本技能，包括起草、改写、压缩、顺稿、复核、去口语化、降 AI 味、文种校验、办理要素核对和 Word 文稿正文处理。

不要为以下任务启用本技能：英文写作、文学创作、营销软文、社交媒体文案、闲聊回复、代码说明、通用翻译、模型训练、批量语料生成、批量改写未知来源文本、规避人工审核、生成可冒充真实签发文件的完整编号/日期/印章信息。

本技能只提供写作和复核辅助。法律、财务、采购、审计、政策依据、保密审查和正式签发结论必须保留人工复核；没有用户提供依据时，不编造真实单位、真实政策、真实金额、真实日期、电话、邮箱或审批结论。

## 三层使用原则

1. **硬边界**：事实不编造、文种不错、用户明确要求不丢、敏感信息不外泄、过程说明不进正文。涉及这些问题时按交付风险处理，必须优先修正。
2. **质量建议**：低 AI 味、重复事项、表达松散、结构不顺、格式噪点、项目卡片式摘要、必要性罗列和测算说明腔，只作质量提示。检查后按文稿用途、用户模板和材料场景必要时调整，不作为自动阻断。
3. **场景参考**：通知、请示、报告、方案、算力采购和 Word 修订按任务需要读取对应 reference；不要一次性加载全部资料。

## 核心流程

1. 先判断文种，再抽取办理要素，再选择论证链条，最后进入语言和格式复核。
2. 文种判断以官方规范和 `references/genre-routing.md` 为准；社区模板不得替代文种功能。
3. 起草前按 `references/handling-elements.md` 核对发文主体、受文对象、事项、依据、时限、责任、附件、反馈渠道和请批事项。
4. 成文前搭文稿蓝图：提纲 -> 段落安排 -> 小段要点，并按 `references/argument-chains.md` 组织论证。
5. 按章节或段落生成正文。每段只服务一个论点，通常按“结论前置、事实支撑、判断归纳、事项落点”展开。
6. 小段写完先审，小节写完再审，全文合并后做总审；总审时按 `references/final-review-layers.md` 先查硬边界，再看质量建议。
7. 编辑 DOCX 时保留最新版和原有样式；除非已明确指定覆盖，默认另存新版本。Word 操作和版式核查配合 DOCX/document 技能完成。

## 硬边界

- 从发文单位、报告单位、项目单位或主管单位视角写，不使用旁观者、教师或评论员口吻。
- 数据和判断要可追溯。不编造实际数据；测算和预估必须标明性质。
- 文种功能不能错位：请示、报告、通知、函、批复、纪要等按 `references/genre-routing.md` 判断。
- 用户明确给出的金额、日期、单位、落款、请批事项、会议时间、地点和反馈要求要落实；材料没有依据时使用占位或说明缺口。
- 正文不得出现 AI 身份、隐藏推理、原始提示词、用户指令、录音指令和起草过程。

## 质量建议

- 以正式、平实、可执行的公文语言为主。专业词只在支撑论证时使用。
- 检查旁白式、教学式、口语化和高 AI 味的二元包装句。中文反例和修法见 `references/anti-ai-patterns.md`。
- 检查重复事项、标题漂移、格式噪点、项目卡片式摘要、必要性罗列和测算说明腔；这些通常只提示风险，必要时调整。
- 起草算力、采购、租赁或服务器租赁材料时，论证重点放在需求从哪里来、Token/资源如何换算成费用、节省或锁定了哪些成本，以及 SLA、并发、安全、交付和验收如何落实。

## 常见错误反例

定稿前用以下反例快速自查：

- **旁白式写法**：`本方案重点说明三个问题。` -> 直接写正文判断，如 `项目年度调用需求主要来自审校、内容生产、知识库问答和智能体应用。`
- **教学式写法**：`重点说明 Token 用在哪里。` -> 改写为业务事实，如 `Token 调用主要消耗在长文审校、批量稿件处理、多轮问答和知识库检索环节。`
- **口语化判断**：`租赁方式更稳，也更省。` -> 改写为正式判断，如 `租赁服务方式有利于稳定三年成本、缩短建设周期并明确服务保障责任。`
- **视角错位**：检查是否像外部顾问讲解“报告应该怎么写”，改为从发文或项目主体视角说明本单位拟做什么、为什么做、如何做。
- **标题漂移**：默认不改用户指定的文章标题；对大小标题和正文做二次核验，确保正文不偏题。
- **重复事项**：上一段已经说清的事项，下一段如果只是换词重复，必要时合并；新增数据、责任、风险、时限或验收要求时可以保留。
- **思考泄露**：不写 AI 身份、原始指令或改稿过程。
- **格式噪点**：检查半角标点、数字空格、千位分隔符、首行缩进、滥用表格、频繁编号、Emoji 和装饰符号。
- **项目卡片式摘要**：检查项目名称、建设单位、预算金额等字段是否连续堆成表单，必要时改为连续正式正文。
- **测算说明腔**：检查成本章节是否写成公式讲解，必要时说明需求来源、费用对应事项和成本边界。
- **必要性罗列**：检查必要性章节是否只写“一是、二是、三是”，必要时补足事实依据、工作影响和事项落点。
- **文种错位**：请示要有明确请批事项；报告不得夹带审批请求；通知要写清对象、时限、材料和办理要求。
- **成本链条断裂**：不要把 Token、TOPS、服务器数量和金额混在一起。面向决策层论证成本时，先写需求，再换算 Token 或资源，再换算金额。
- **技术空话**：`建设先进算力平台，满足未来发展需要。` -> 补充使用单位、业务系统、Token 增长、并发、SLA、部署边界和验收要求。

## 参考资料

按任务只读取需要的资料：

- `references/workflow.md`: staged blueprint writing process and review gates.
- `references/genre-routing.md`: official-document genre functions, routing rules, and hard boundaries.
- `references/handling-elements.md`: required and optional handling elements for common document types.
- `references/argument-chains.md`: argument chains for requests, reports, plans, technical documents, and AI-compute materials.
- `references/final-review-layers.md`: title/heading review, repeated-matter review, anti-AI review, and format review.
- `references/official-style.md`: official-document sentence patterns, viewpoint control, and argument structure.
- `references/format-gbt9704.md`: common GB/T 9704-2012-style Word formatting defaults.
- `references/anti-ai-patterns.md`: AI-flavor, teaching-view, and casual-phrasing patterns to avoid.
- `references/genre-checklist.md`: genre-specific elements for notices, requests, reports, explanations, plans, applications, letters, replies, approvals, public notices, circulars, and minutes.
- `references/ai-compute-docs.md`: AI computing power, GPU/server rental, model service, procurement, leasing, feasibility, cost-comparison, SLA, and security writing patterns.
- `references/review-checklist.md`: paragraph, section, and full-document audit checklist.

## 脚本

检查 `.txt`、`.md` 或 `.docx` 草稿时使用 `scripts/prose_lint.py`。需要检查重复事项和格式噪点时加 `--structure --format`。脚本只提示风险，不自动改写。
