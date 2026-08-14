# v1.6.5 本地发行候选

状态：`READY_LOCAL_CANDIDATE`。本候选只完成本地 GitHub/SkillHub 组包；未合并 `main`，未推送、未打 tag、未创建 GitHub Release、未上传 SkillHub，也未生成或上传 ClawHub 发布物。

## 固定对象与范围

- 上一正式 tag：`v1.6.4^{commit}=a737791c8ed6fbae82e4a72fb3931e901faafc07`。
- 本地产品候选：`062d7f82b60e3904454ac3a6ef2de3799027c30e`。
- 候选分支：`codex/v165-release-candidate`。
- 公开版本元数据和三宿主 adapter manifest 已准备为 `1.6.5`；普通 Skill、未启用 Hook 和用户临时关闭 Hook 的运行方式不变。
- GitHub 仓库中的 `packages/openclaw/` 仍是随仓库维护的无 Hook 兼容源码，不等于 ClawHub 发布物。本轮没有 ClawHub staging、publish、sync、delete 或版本覆盖操作。

## 主要变化

- 增加三个静态互斥、默认不启用的可选能力：篇幅不足安全扩写、交付洁净度、重复句与高相似零增量复述清理。
- 保持一份 coordinator；每次只选择一个 capability，不并行修改同一终稿。
- 修复 Codex 同一轮并行读取 Skill 与材料时，两个 `PostToolUse` 记录可能互相覆盖 `skill_seen=true` 的生命周期竞态。实现只增加单调 Skill-read 标记，不改变篇幅语义门、数字保护或 D0/D1 选择条件。

## 剩余风险复核

合并后 R3 曾出现模型已读取安装版 Skill，但状态记录为 `skill_seen=false`。复现显示 Skill 与 D0 两条命令在同一轮并行执行，后写入的材料记录可能覆盖先写入的 Skill 状态。修复提交为 `94fe302a11a19f650fde6f9f95375d9e40296ff2`。

修复后只重跑一条同型 Alibaba DeepSeek V4 Flash 0731 max 样本：

- 1 次真实调用、0 retry、1200 秒模型上限；实际耗时 331.906 秒。
- 外层工具在 184 秒先超时，但原 Python/Codex 子进程继续存活并完成，未重启或补样。
- 最终 `skill_seen=true`、`external_material_read=true`，篇幅事务正常创建。
- D0 为 268 字；候选为 376 字，但新增透明计数“28台”，既有数字保护门选择 D0，`delivery_verified=true`。该结果只验证生命周期竞态消失，不用于收紧或放宽篇幅门。
- manifest SHA-256：`304764e048dd362f3465000adfb5bdb66c9075107091daef3f9c5750adbef509`；receipt SHA-256：`fb2d1ba631ae96ebcba8670f2585e797b506ba4f667ddf2898637650ae746d1d`；插件记录 SHA-256：`965985505e4f7028a3b5ae193cfaa22ca760e041039b2b36616edca031385247`。

本机未发现 CodeBuddy/WorkBuddy CLI 或可用登录入口，因此没有冒充当前在线成功。当前只完成：

- CodeBuddy `under_length` 静态 companion 49 文件，`enabled=false`、`installed=false`、`network_used=false`。
- companion fingerprint：`5510e6f69923b1d97fcc2b58790c85f8fe81b0897e02e1eb321951b801e13dde`。
- companion 内核心与 canonical 核心 SHA-256 均为 `ee9d01cd51493cb3feec66a21d6c40baabefbd874e2b01fa208d79ecdd9088d8`。
- WorkBuddy/CodeBuddy 当前 adapter、原生 Skill 事件、晚注册恢复和 Stop 反馈定向测试连同 Hook 层共 10/10 通过。当前在线生命周期仍需以后有可用客户端时补一条，不阻塞本地候选组包。

第一次核心哈希核对误用了不存在的 `hooks/core/` 组装路径并报错；按实际扁平路径 `hooks/gate_stop_hook.py` 重算后字节一致。该初次命令不计通过。

## 本地候选包

唯一可用目录：`output/release-candidates/v1.6.5-local-rc-r2/`。较早的 `v1.6.5-local-rc/` 在 README 最终化前生成，已标记 superseded，不得发布。

### GitHub 源码归档

- 文件：`github-source-v1.6.5.zip`。
- SHA-256：`bbf8a172ad51a6c246e353d7e570bcfef25328ececae536322b09b38c47a580a`。
- 大小：3,201,460 bytes。
- 归档绑定产品候选 `062d7f82b60e3904454ac3a6ef2de3799027c30e`。

### SkillHub 清洁包

- 目录：`skillhub-package/`，共 56 文件。
- `_meta.json` 与专用 `SKILL.md` 均为 `chinese-official-writing@1.6.5`。
- 逐文件 `SHA-256 + 相对路径` 清单文本 SHA-256：`456b378f678b0eebdc9eda4f3f68ce41a322a0871d200e1e8302379d20c4e36e`。
- 排除 `agents/openai.yaml` 和无扩展名 `LICENSE`；以 `LICENSE.md` 携带根 MIT；无缓存、日志、环境文件、仓库 maintenance、生成插件目录或 ClawHub 发布资产。

待正式发布时可使用的 SkillHub 更新说明：

> 新增篇幅不足、交付洁净度、重复句与高相似复述三项可选 Hook，修复并行读取时的生命周期状态覆盖。

## 最小验证

- `test_gate_stop_hook + test_under_length_capability`：31/31 PASS。
- 版本、OpenClaw GitHub 兼容包与 SkillHub builder：7/7 PASS。
- README/版本聚焦：4/4 PASS。
- CodeBuddy adapter 与 Hook 层：10/10 PASS。
- canonical `quick_validate.py`：PASS。
- `sync_adapters.py` 连续运行无漂移；`git diff --check`：PASS。

未运行全量测试；本轮遵循真实生命周期优先和必要 smoke 口径。递归清理旧本地候选的两次命令被执行策略拒绝，未删除任何文件，因此改用全新 `-r2` 目录完成最终构建。
