# 中文公文写作 Skill

[![Version](https://img.shields.io/badge/version-2.0.25-blue)](https://github.com/gongyu0918-debug/chinese-official-writing-skill/releases/tag/2.0.25)
[![ClawHub downloads: 9,048](https://img.shields.io/badge/ClawHub%20downloads-9%2C048-2f80ed)](https://clawhub.ai/gongyu0918-debug/skills/chinese-official-writing)
[![SkillHub downloads: 227,083](https://img.shields.io/badge/SkillHub%20downloads-227%2C083-2f855a)](https://skillhub.cn/skills/user_f3d82da7/chinese-official-writing)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

下载量更新于 2026-10-06。

用于中文公文、事务性材料、工作材料、新闻消息和新闻评论的起草、改写、压缩、润色、审核及 Word 正文整理。

> 本 Skill 的稿件由 AI 生成或辅助修改，可能存在错误或遗漏。正式使用前请核实事实、数据、引用、政策依据及责任和承诺。

## 适用场景

- 公文：申请、请示、报告、通知、函、批复、意见、决定、公告、通告、纪要等。
- 事务与工作材料：采购、整改、反馈、说明、公示、方案、制度、总结、调研、讲话和述职等。
- 新闻与技术材料：新闻消息、编者按、新闻评论、可研、审查、技术需求及算力专项材料。
- 修改与复核：压缩、扩写、润色、去口语化、降 AI 味、文种与格式检查、审核后改稿。
- Word 整理：结合宿主文档工具处理正文和版式。

## 安装

从 [SkillHub](https://skillhub.cn/skills/user_f3d82da7/chinese-official-writing) 获取 2.0.25。也可下载 [GitHub 2.0.25 源码](https://github.com/gongyu0918-debug/chinese-official-writing-skill/releases/tag/2.0.25)，将 `chinese-official-writing` 文件夹放入所用应用的 Skill 目录。

也可从 [ClawHub](https://clawhub.ai/gongyu0918-debug/skills/chinese-official-writing) 获取。篇幅与文稿检查需要 Python 3；Word 文件生成需要宿主提供文档工具。

## 使用

直接提供现有材料、稿件用途和要求。已有旧稿时，说明采用哪一版，以及哪些内容可以修改、哪些必须保留。

- 起草：“这是下周培训的安排，帮我写个通知，把报名事项说清楚。”
- 抄告单：“从这份纪要中摘出需要抄告财务处的两项决定，按现有抄告单成稿，保留责任和期限。”也可整理领导批示、事项告知或审批结果公示；请提供对应原件和用途。
- 改稿：“这是今年的工作记录，帮我更新去年的总结，分清已完成和正在推进的事项。”
- 局部修改：“仅把回执接收人王老师改为李老师，其余文字、标点和空行原样保留。”
- 压缩：“将这份汇报压缩到400字以内，保留关键数字、日期和未了事项。”
- 审校：“先指出位置、问题和建议；涉及待核实的信息不要改成确定事实。”
- 去口语化：“帮我把这份整改方案写得平实些，保留具体事项。”
- Word：“申请内容已定，请按单位模板整理成 Word。”

篇幅、语气、收件人和交付形式可一并说明。只需要稿件时，可以说：“只输出正文，不附文后提示或过程说明。”

## 写作说明

稿件应围绕本次行文目的安排主次：申请、请示讲清请求批准的事项、理由、主要内容和资源；报告讲清需要了解的进展、问题及判断依据；评论围绕中心判断展开论证。关键内容依据材料写具体，背景、例子、反面观点和边界说明为其提供支撑。用户要求的必列事实、模板和必要的不同观点完整保留。详略以本次用途和材料为依据，长稿同样需要充分说明核心内容。

可以直接指出重点和详略，例如：“这份立项申请重点写为何增加写作能力、具体建设什么、申请什么资源；推广数据只支撑已有基础，技术运行细节集中到附件。保留原章节和有效数字，不新增建设范围。”

有正文和附件时，正文说明本次事项、关键动作与作用，附件集中说明完整过程和细目；审批或理解所需的摘要、关键数字可以两处对应。用途分析与已发生的用户行为、调查测算分别表达，已提供的记录和判断按原状态保留。

审校意见应区分有依据的错误、待核信息和可选表达建议。不同职责、主要标的与整包金额、旧值与新值分别核对；未核实的字段不直接补成确定值，数值差额也不能单独决定应修改哪一项。

实际成稿仍可能出现平均铺陈、沿次要内容展开或重复解释边界。反馈时提供原始要求和完整稿件，指出应重点说明的事项及抢占篇幅的段落，可据此调整段落作用和详略。

## 版本与许可

当前版本为 **2.0.25**。1.x 最后版本 **1.6.36** 保留在 [legacy/1.x](https://github.com/gongyu0918-debug/chinese-official-writing-skill/tree/legacy/1.x) 分支。

本项目采用 [MIT License](LICENSE)，允许修改、分发和商业使用，请保留版权及许可声明。

反馈问题请提交 [GitHub Issue](https://github.com/gongyu0918-debug/chinese-official-writing-skill/issues)，仅附可公开的材料、稿件及预期结果。
