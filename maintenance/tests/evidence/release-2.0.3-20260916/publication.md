# 2.0.3 发布回执

2026-09-16，按用户授权将最新 main 发布至 GitHub、ClawHub、SkillHub。三个发布任务均取得成功回执。

- 产品提交：`ef5335edcffd2c16b7d826c80afcd2e743c69935`，注释标签 `2.0.3` 固定于该提交。后续仅追加维护证据，不移动标签。
- GitHub：main 与标签原子推送成功，正式 [2.0.3 Release](https://github.com/gongyu0918-debug/chinese-official-writing-skill/releases/tag/2.0.3) 创建成功，设置为 latest。本轮没有上传下载附件。
- ClawHub：唯一调用返回 `OK. Published chinese-official-writing@2.0.3 (k976qv0r1936b2qhk9mmzq1mdn8ef3a7)`，退出码 0，按实际发布成功处理。
- SkillHub：唯一正式提交成功，`skillId=70149`、`versionId=316920`，73 文件，回执中的内容审核、审核及安全扫描均为 `pending`。按项目规范，成功提交即完成该平台任务。
- SkillHub 回执 fingerprint：`9d6edd1fa33acc3de05e708ecb800fc5b3ade501a84ea79dd7cf1027117ed28c`。

没有执行市场提交后的版本查询、页面核验、传播轮询或再次提交；回执成功不等同于审核通过。

## 验证及内容来源

发布准备未修改写作规则或脚本。相对 main@c70f15c2，仅更新两份 README 版本信息和维护记录；相对 2.0.2，意见、说明两页沿用已经完成的原生写稿和独立审阅结果。完整来源及界限见 [scope.md](scope.md)、[preflight.json](preflight.json) 和 [上传清单](upload-manifest.json)。

- `audit_product_surface.py`：通过，引用路径可达。
- `quick_validate.py`：通过，标准 Skill 格式有效。
- 对比上传目录与产品提交：通过，逐文件核对；按既有规范处理平台元数据、可选宿主元数据和许可文件名，SKILL 正文一致。
- `git diff --exit-code c70f15c2 HEAD -- chinese-official-writing/SKILL.md chinese-official-writing/references chinese-official-writing/scripts`：发布准备阶段通过。
- `git diff --exit-code 2.0.2 HEAD -- chinese-official-writing/scripts`：通过，脚本与已发布 2.0.2 一致。
- SkillHub 本地 dry-run：通过。既有真实写稿证据不因版本号更新重复调用模型，未运行语义关键词断言。

## ClawHub 调用异常记录

本次经 `clawhub.cmd` 发起的调用显式包含 `--dry-run --json`，实际返回的却是上述发布成功文本，已经产生版本回执。立即停止后续 ClawHub 提交并保存原返回，未将它误记为普通 dry-run 通过，也未再执行一次正式发布。原始记录文件名 [clawhub-dry-run.json](clawhub-dry-run.json) 保持原样，实际状态见 [clawhub-result.json](clawhub-result.json)。

本次正式发布本身在用户授权内。Windows 包装器及多行参数传递问题尚未证实为根因；后续发布应直接使用 Node CLI 入口并先核对本地参数传递，避免经 `.cmd` 传入多行更新说明。本轮不为排查原因再次访问平台。

## 冻结范围

未构建或更新桌面 WorkBuddy 包、其他适配包、GitHub 下载附件和本机 Pro 安装包。平台上传目录仅用于本次获授权的提交。此前已核验的本机写作规则继续保留，与本次发布规则相同；版本说明的本机同步随包冻结暂缓。

原始回执：[GitHub](github-result.json)、[SkillHub](skillhub-publish.json)、[ClawHub](clawhub-result.json)。
