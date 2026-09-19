# 2.0.6 发布记录

2026-09-19按用户授权发布最新main。产品提交`82b26779abd4ddaff346a953877192871a374382`，注释标签`2.0.6`指向该提交；后续维护回执提交不移动产品标签。发布分支为`codex/release-2.0.6-20260919`。

| 平台 | 结果 | 回执 |
| --- | --- | --- |
| GitHub | Release已创建 | [中文公文写作2.0.6](https://github.com/gongyu0918-debug/chinese-official-writing-skill/releases/tag/2.0.6) |
| SkillHub | 提交成功，审核pending | skillId 70149 / versionId 327468，76文件 |
| ClawHub | published | versionId k97bcyv87fb89gffqbb140bkyh8ep2ss，75文件 |

每个平台正式提交一次。SkillHub、ClawHub成功回执即完成，没有提交后的公开页面、索引、传播或审核查询，也没有重复上传；pending不表述为审核通过。ClawHub回执中的latestVersion仍为提交前值，不据此重复提交。

## 用户可感知的改进

完善复杂材料报送的主体、统计口径、材料与期限对应；明确代表建议和委员提案答复的函路由；完善采购更正公告中原公告、后续履约、更正理由和处理结论的关系。相对2.0.5只有4个规则文件变化，SKILL.md及两个脚本没有改动；发布准备只更新两份README版本号，保留现有示例与下载量徽章日期。

采纳依据见[场景原子验证](../scenario-atoms-20260918/results.md)：单轮34对共68稿含各次试验，最终精确候选7对未确认语义回退；另有1.x与2.0的12次连续多轮验证。上述结果不等于所有文种或所有模型全面领先，合理推断、简称和宽泛表达按实际语义判断。本轮发布未新增真实写稿调用。

## 发布核对

- `python -B maintenance/tests/evidence/release-2.0.6-20260919/prepare.py`：8项路径、Skill结构、脚本smoke及SkillHub本地预检通过；原生规则和脚本逐字节对应授权main@b707e086。
- ClawHub dry-run为would-publish，正式回执fingerprint与dry-run一致；SkillHub本地预检不返回指纹，正式指纹原样保存，不作不存在的比较。
- canonical 76文件，SkillHub 76文件、ClawHub 75文件；两个清洁目录都只包含普通写稿规则、参考、脚本、README及许可/平台元数据，没有Hook、维护代码、缓存、付费实现或适配归档。逐文件哈希见upload-manifest.json。
- 独立原生Codex CLI审阅使用alibaba-token-plan/deepseek-v4.1-flash max，207.52秒完成，未发现发布阻断。此前协作面加密消息不兼容和旧CLI路径失效均记录为未完成的启动尝试；没有把它们算通过，后续明文CLI核查完成。
- `git diff --check`通过，标签继承2.0.5历史。main与新tag原子推送成功；新标签只指向产品提交，后续只推送发布记录。
- 普通脚本沿用相同字节的既有行为验证，并对上传包执行smoke；未运行中文规则关键词或整句断言。

本轮未改桌面WorkBuddy、其他适配归档、本机Pro插件、Hook或激活状态，也未调用旧完整Pro同步工具。最新用户对本机Hook清理的反馈优先于旧自动同步惯例。
