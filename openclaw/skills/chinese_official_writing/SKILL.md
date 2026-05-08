---
name: chinese_official_writing
description: 用于起草、改写和复核中文公文及正式工作材料，覆盖通知、请示、报告、说明、方案、申请、函、复函、批复、意见、决定、公告、公示、通报、会议纪要、工作要点、工作总结、调研报告、可研报告、实施方案、建设方案、审查材料，以及 AI 算力服务可研、算力采购或租赁、GPU/服务器租赁、技术服务需求等材料；强调文种准确、主体视角稳定、论点清楚、数据可追溯、公文语气自然、低 AI 味。不用于英文写作。
license: MIT-0
metadata:
  openclaw:
    version: "1.2.1"
    emoji: "📝"
    tags:
      - chinese
      - official-document
      - writing
      - gongwen
      - ai-compute
---

# 中文公文写作

使用本技能生成或修改中文正式文稿。最终文本应像文稿正文，而不是写作说明、概念讲解或外部顾问点评。

## 核心流程

1. 先确认文种、受文对象、发文或报告主体、核心结论、必要数据、最新底稿和用户批注。信息基本够用时直接推进。
2. 成文前先搭文稿蓝图：提纲 -> 段落安排 -> 小段要点。
3. 按章节或段落生成正文。每段只服务一个论点，通常按“结论前置、事实支撑、判断归纳、事项落点”展开。
4. 小段写完先审，小节写完再审，全文合并后做总审。
5. 编辑 DOCX 时保留用户最新版和原有样式；除非用户要求覆盖，一律另存新版本。Word 操作和版式核查配合 DOCX/document 技能完成。

## 写作纪律

- 从发文单位、报告单位、项目单位或主管单位视角写，不使用旁观者、教师或评论员口吻。
- 数据和判断要可追溯。不编造实际数据；测算和预估必须标明性质。
- 以正式、平实、可执行的公文语言为主。专业词只在支撑论证时使用。
- 避免旁白式、教学式、口语化和高 AI 味的二元包装句。中文反例和修法见 `references/anti-ai-patterns.md`。
- 起草算力、采购、租赁或服务器租赁材料时，论证重点放在需求从哪里来、Token/资源如何换算成费用、节省或锁定了哪些成本，以及 SLA、并发、安全、交付和验收如何落实。

## 常见错误反例

定稿前用以下反例快速自查：

- **旁白式写法**：`本方案重点说明三个问题。` -> 直接写正文判断，如 `项目年度调用需求主要来自审校、内容生产、知识库问答和智能体应用。`
- **教学式写法**：`重点说明 Token 用在哪里。` -> 改写为业务事实，如 `Token 调用主要消耗在长文审校、批量稿件处理、多轮问答和知识库检索环节。`
- **口语化判断**：`租赁方式更稳，也更省。` -> 改写为正式判断，如 `租赁服务方式有利于稳定三年成本、缩短建设周期并明确服务保障责任。`
- **视角错位**：不要像外部顾问讲解“报告应该怎么写”，要从发文或项目主体视角说明本单位拟做什么、为什么做、如何做。
- **文种错位**：请示要有明确请批事项；报告不得夹带审批请求；通知要写清对象、时限、材料和办理要求。
- **成本链条断裂**：不要把 Token、TOPS、服务器数量和金额混在一起。面向决策层论证成本时，先写需求，再换算 Token 或资源，再换算金额。
- **技术空话**：`建设先进算力平台，满足未来发展需要。` -> 补充使用单位、业务系统、Token 增长、并发、SLA、部署边界和验收要求。

## 参考资料

按任务只读取需要的资料：

- `references/workflow.md`: staged blueprint writing process and review gates.
- `references/official-style.md`: official-document sentence patterns, viewpoint control, and argument structure.
- `references/format-gbt9704.md`: common GB/T 9704-2012-style Word formatting defaults.
- `references/anti-ai-patterns.md`: AI-flavor, teaching-view, and casual-phrasing patterns to avoid.
- `references/genre-checklist.md`: genre-specific elements for notices, requests, reports, explanations, plans, applications, letters, replies, approvals, public notices, circulars, and minutes.
- `references/ai-compute-docs.md`: AI computing power, GPU/server rental, model service, procurement, leasing, feasibility, cost-comparison, SLA, and security writing patterns.
- `references/review-checklist.md`: paragraph, section, and full-document audit checklist.

## 脚本

检查 `.txt`、`.md` 或 `.docx` 草稿时使用 `scripts/prose_lint.py`。脚本只提示风险，不自动改写。
