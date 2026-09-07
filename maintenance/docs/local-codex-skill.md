# 本机 Pro 同步

本页只在本机安装核对、MIT main/Pro 版本推进或恢复旧安装时读取。开发和真实写稿共用一个完整 Pro 入口：普通写稿规则来自本地 MIT `main`，Pro 提供叠加增强；不再并装普通 Skill 或旧普通 companion。此为本机自用授权，不授权平台发布。

## 同步要求

- 首次开工核对安装；MIT main 或已提交 Pro 构建输入推进后同步。比较 canonical 内容指纹和 Pro 构建输入，不因仅有维护文档变化反复打包。无变化也须核对实际安装文件，不能只信历史回执。
- 复用 Pro 工程的本机同步工具。它使用专用投影及构建工作树，不修改正在开发的工作树，不将未提交改动混入已提交 HEAD；来源未就绪时如实报告待同步，不称已更新。
- 组装、签名校验、安装文件比对成功后再替换旧入口；另外核对 Codex 的 Skill 发现、插件启用、Hook 信任/启用和本地执行结果。已安装不等于真实宿主写稿已验证。
- 签名包同版本内容不可覆盖；本地开发安装保留独立版本目录和上一份可恢复安装，不移动公开 tag 或上传平台。
- 付费构建、投影和安装胶水保留在 Pro 工程。MIT 项目仅记录同步要求，不接收付费实现。

## 普通版与 Pro 的 A/B 入口

同一个安装中，`SKILL.md` 只负责选路：普通写稿规则入口是 `mit/ENTRY.md`，Pro 入口是 `PRO.md`。普通入口、说明及 `mit/references/` 保持 MIT main 对应原字节；Pro 路径加载其叠加规则。二者按需读取，不重新并装普通 Skill。基线目录提供写稿规则；测试普通版原生脚本或 Hook 时使用绑定提交的 canonical，不以 Pro 工具代替。

A/B 两组使用相同输入和各自新的隔离上下文。普通 A 组显式读取 `mit/ENTRY.md` 及其需要的 MIT 叶子；B 组读取 `PRO.md` 并按测试范围启用增强。具体隔离方法以安装包 `AB.md` 中经宿主实测的步骤为准，不改变日常宿主的全局开关。

普通组启动前核实 Pro Skill、MCP 和 Hook 均未参与，不能仅以命令接受禁用参数为证据。提示中写“普通版”也不会自动隔离 Hook；已读过 Pro 规则的上下文不能称为纯普通组。未验证隔离不得宣称对照有效；隔离宿主仍可按绝对路径读取包内普通规则，无需并装另一份 Skill。

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
