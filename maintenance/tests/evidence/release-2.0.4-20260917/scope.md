# 2.0.4 发布范围

2026-09-17，用户明确授权将当前main作为新版本发布至GitHub、SkillHub、ClawHub。发布起点main@20d89158；GitHub及两个市场上次成功提交为2.0.3，本次采用2.0.4。独立分支codex/release-2.0.4-20260917。

相对2.0.3，产品只改变prose_lint.py、draft_length.py和prose-lint-usage.md。沿用script-fixes-merge-20260916中的8次原生写稿、142项脚本行为检查及合入记录。抗AI近义复述、规则范围收窄候选和新增专项页设想均未合main，不随本次发布。

发布准备只更新两份README版本号、发布说明和维护证据；SKILL.md、references及scripts与获授权的main逐文件绑定。保留既有使用示例、下载量徽章和其标注日期。

GitHub更新main、固定注释标签2.0.4并创建正式Release。SkillHub与ClawHub使用各自的清洁上传目录，每个平台正式提交一次；成功回执即完成，不再读取发布后的市场页面、索引或传播状态。内容审核及安全扫描按回执原状态登记。

复用标准上传目录构建方式，不更新桌面WorkBuddy或其他独立适配包。ClawHub直接调用已安装Node CLI入口，以结构化参数传递多行说明，避免之前.cmd包装器参数丢失问题。发布前检查产品路径、Skill格式、来源和上传目录一致性，并对上传目录的脚本做机械输入输出smoke；未修改的规则不重复跑写稿模型或历史语义关键词断言。
