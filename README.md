# 中文公文写作 Skill

[![Version](https://img.shields.io/badge/version-2.0.14-blue)](https://github.com/gongyu0918-debug/chinese-official-writing-skill/releases/tag/2.0.14)
[![ClawHub downloads: 8,294](https://img.shields.io/badge/ClawHub%20downloads-8%2C294-2f80ed)](https://clawhub.ai/gongyu0918-debug/skills/chinese-official-writing)
[![SkillHub downloads: 176,470](https://img.shields.io/badge/SkillHub%20downloads-176%2C470-2f855a)](https://skillhub.cn/skills/user_f3d82da7/chinese-official-writing)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

下载量更新于 2026-09-24。

用于中文公文、事务性材料、工作材料、新闻消息和新闻评论的起草、改写、压缩、润色、审核及 Word 正文整理。

> 本 Skill 的稿件由 AI 生成或辅助修改，可能存在错误或遗漏。正式使用前请核实事实、数据、引用、政策依据及责任和承诺。

## 适用场景

- 公文：申请、请示、报告、通知、函、批复、意见、决定、公告、通告、纪要等。
- 事务与工作材料：采购、整改、反馈、说明、公示、方案、制度、总结、调研、讲话和述职等。
- 新闻与技术材料：新闻消息、编者按、新闻评论、可研、审查、技术需求及算力专项材料。
- 修改与复核：压缩、扩写、润色、去口语化、降 AI 味、文种与格式检查、审核后改稿。
- Word 整理：结合宿主文档工具处理正文和版式。

## 安装

下载 [2.0.14 源码](https://github.com/gongyu0918-debug/chinese-official-writing-skill/releases/tag/2.0.14)，将 `chinese-official-writing` 文件夹放入所用应用的 Skill 目录。

也可从 [ClawHub](https://clawhub.ai/gongyu0918-debug/skills/chinese-official-writing) 获取。篇幅与文稿检查需要 Python 3；Word 文件生成需要宿主提供文档工具。

## 使用

直接提供现有材料、稿件用途和要求。已有旧稿时，说明采用哪一版，以及哪些内容可以修改、哪些必须保留。

- 起草：“这是下周培训的安排，帮我写个通知，把报名事项说清楚。”
- 改稿：“这是今年的工作记录，帮我更新去年的总结，分清已完成和正在推进的事项。”
- 局部修改：“仅把回执接收人王老师改为李老师，其余文字、标点和空行原样保留。”
- 压缩：“将这份汇报压缩到400字以内，保留关键数字、日期和未了事项。”
- 审校：“先指出位置、问题和建议；涉及待核实的信息不要改成确定事实。”
- 去口语化：“帮我把这份整改方案写得平实些，保留具体事项。”
- Word：“申请内容已定，请按单位模板整理成 Word。”

篇幅、语气、收件人和交付形式可一并说明。只需要稿件时，可以说：“只输出正文，不附文后提示或过程说明。”

## 版本与许可

当前版本为 **2.0.14**。1.x 最后版本 **1.6.36** 保留在 [legacy/1.x](https://github.com/gongyu0918-debug/chinese-official-writing-skill/tree/legacy/1.x) 分支。

本项目采用 [MIT License](LICENSE)，允许修改、分发和商业使用，请保留版权及许可声明。

反馈问题请提交 [GitHub Issue](https://github.com/gongyu0918-debug/chinese-official-writing-skill/issues)，仅附可公开的材料、稿件及预期结果。
