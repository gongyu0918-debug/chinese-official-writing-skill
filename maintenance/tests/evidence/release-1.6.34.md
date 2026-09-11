# v1.6.34 发布说明

相较上一版，本版将常用的压缩、字段编辑和语言检查指引按任务集中呈现，减少无关阅读，首页入口更聚焦；压缩限字、字段增删改、格式与语言检查的操作边界更清楚，便于在短稿、报告、函件和字段式材料之间稳定切换。

本版继续保留事实、数字、日期、主体、责任和未决状态的保护要求，并保持旧文种与新文种的质量衔接。真实写稿复核覆盖限字报告、字段材料、函件压缩和 Word 正文排版；候选未发现相对基线的独有硬回退。工程校验包括 canonical Skill 校验、102 项边界回归、Python 语法检查和 `git diff --check`。

本次发布说明只描述用户可见的改进，不展开内部实现过程。开场称谓排序能力不属于本版。

## 发布回执

- GitHub：annotated tag `v1.6.34` 已推送，Release 已公开：<https://github.com/gongyu0918-debug/chinese-official-writing-skill/releases/tag/v1.6.34>。
- SkillHub：向既有 `skillId=70149` 正式提交一次，返回 `ok=true`、`versionId=307027`、98 个文件、fingerprint `d5e17fb02a4e7ef9e79d94c2c74b451aa97da1acf9c0e8fde38c415efceeed7a`、`tags.latest=1.6.34`；`reviewStatus`、`securityScanStatus`、`contentAuditStatus` 均为 `pending`。
- ClawHub：向 `chinese-official-writing` 正式提交一次，返回 `status=published`、`versionId=k977mjpdawjpb5semd23e7sdas8e64j2`、47 个文件、fingerprint `95c09b0433636f66e2288d29408c59e81f64e30000583a8083e830f35ead12c6`。提交回执中的 `latestVersion=1.6.33` 是当时平台返回值；按项目规范以本次成功回执为完成依据，不重复提交或做传播轮询。
