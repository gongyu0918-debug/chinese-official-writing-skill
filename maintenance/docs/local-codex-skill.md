# 本机 Pro 同步

本页只在本机安装核对、MIT main/Pro 版本推进或恢复旧安装时读取。开发和真实写稿共用一个完整 Pro 入口：普通写稿规则来自本地 MIT `main`，Pro 提供叠加增强；不再并装普通 Skill 或旧普通 companion。此为本机自用授权，不授权平台发布。

## 同步要求

- 首次开工核对安装；MIT main 或已提交 Pro 构建输入推进后同步。比较 canonical 内容指纹和 Pro 构建输入，不因仅有维护文档变化反复打包。无变化也须核对实际安装文件，不能只信历史回执。
- 复用 Pro 工程的本机同步工具。它使用专用投影及构建工作树，不修改正在开发的工作树，不将未提交改动混入已提交 HEAD；来源未就绪时如实报告待同步，不称已更新。
- 组装、签名校验、安装文件比对成功后再替换旧入口；另外核对 Codex 的 Skill 发现、插件启用、Hook 信任/启用和本地执行结果。已安装不等于真实宿主写稿已验证。
- 签名包同版本内容不可覆盖；本地开发安装保留独立版本目录和上一份可恢复安装，不移动公开 tag 或上传平台。
- 付费构建、投影和安装胶水保留在 Pro 工程。MIT 项目仅记录同步要求，不接收付费实现。

## 本机命令

本机配置由 Pro 同步工具创建，保存在用户数据目录，不提交到 MIT 仓库。配置不存在时报告未配置，不替其他机器默认安装。

```powershell
$proSyncConfig = Join-Path $env:LOCALAPPDATA 'OfficialWritingPaid\local-main-follow\config.json'
$proSync = Get-Content -LiteralPath $proSyncConfig -Raw | ConvertFrom-Json
& $proSync.python_executable (Join-Path $proSync.runtime_repo 'scripts\sync_local_pro.py') --config $proSyncConfig
```

这条命令执行本地核对/更新，不启动写稿模型。以返回结果和安装核验为准；来源脏、构建失败、安装或信任未完成时保留旧可用安装并报告差异，不把跳过记作更新成功。

## 清理与恢复

重复 Skill 必须移出 `.agents/skills`、`.codex/skills` 等扫描目录；只在目录里改名仍可能被扫描。先记录文件哈希并保存扫描范围外的备份，再通过插件卸载入口或已核准路径移除。不得按“写作”关键词删除不同用途的 Skill。

恢复时先关闭当前重复入口，再从备份恢复选定的单个版本；重新核验安装和 Hook 状态。宿主当前回合已有的上下文不会被清理追溯改写，更新后以重新扫描结果和后续任务为准。
