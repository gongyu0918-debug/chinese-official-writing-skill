# v1.6.1 发布记录

## 发布范围

- v1.6.1 先发布 GitHub `main`、annotated tag `v1.6.1` 和 GitHub Release；仓库整理完成后，再按单独授权补充发布 SkillHub.cn 1.6.1。
- GitHub 仓库中的 OpenClaw 兼容包随维护提交更新到 1.6.1；ClawHub 远端没有执行发布或同步。
- 小红书 Red SkillHub 未触碰。
- 偏短篇幅 Hook v2 研究分支及其产品提交未进入 v1.6.1。

## 主要变化

- 精简运行入口 frontmatter，只保留发现所需字段和标签；新闻稿件能力在 description 中前置呈现。
- 将运行规则中的“顺稿”“收束”等维护用语替换为普通表达，并把“先……再……”仅作为全文通读的软线索，不按词表或次数自动判错。
- SkillHub/Codex 完整包提供默认关闭的 Codex、Claude Code、WorkBuddy/CodeBuddy Hook 伴随物；启用、信任和真实执行分别确认。Hook 的真实矩阵没有形成 D1，不宣称质量提升或全面兜底，并保留额外 Stop 延迟风险。
- 仓库及仓内当前包统一采用 MIT；ClawHub 远端页面的许可证由平台规则决定，本轮未改动该远端发行面。
- README 同题示例更新为 `gpt-5.6-sol` `ultra` 使用已发布 v1.6.0 Skill 的首个有效输出；两名完整题面匿名裁判均判 Skill 稿胜出。
- README 展示 SkillHub `37k+` 累计下载量下限；因动态 Shields 曾返回 `inaccessible`，使用稳定静态下限而不写成实时精确值。

## 发布前验证

- 全量 unittest：522/522 PASS。
- Promptfoo stub smoke：20/20 PASS，run `eval-2nh-2026-08-11T19:57:20`。
- 固定 v1.6.0 确定性消融：v1.6.0 为 109/111，v1.6.1 为 111/111。
- canonical quick validate、Codex plugin validator、Claude plugin validator、WorkBuddy/CodeBuddy validator：PASS。
- Claude 无模型 preflight：PASS。
- SkillHub 清洁包本地构建：46 文件，version `1.6.1`，MIT `LICENSE.md`；发布前平台 dry-run 返回 `dryRun=true`、slug `chinese-official-writing`、version `1.6.1`。
- 首次在主工作区重跑包边界时，`core.autocrlf=true` 造成工作树中的 LICENSE 和 `agents/openai.yaml` 换行投影不一致，79 项定向测试中 6 项失败；Git blob 与同一 HEAD 的隔离 worktree 内容没有漂移。正式包改由 HEAD `cfd33023749215a79a1798cbb4e7459e9996d43e` 的干净 worktree 重建，随后 79/79 通过，未修改产品或重试上传。
- Codex 通用 quick validator 会拒绝 SkillHub 专用的 `slug`、`version`、`displayName`、`summary` 和 `tags` 字段，该次 schema 不匹配不作为平台包通过证据；最终采用仓库 builder 契约测试和 SkillHub CLI 自身 dry-run。
- 镜像同步两次内容幂等；Windows 行尾造成的 index 伪脏经 Git 过滤后 blob 与 HEAD 相同，刷新索引后工作树恢复干净。
- OpenClaw tree 与 v1.6.0 相同；tracked 高置信凭据扫描、`git diff --check`：PASS。

## 外部回执

- GitHub 产品发布提交：`239eb72edc9cee513a4f76c13b9ed38f223fe32b`。
- annotated tag object：`1366d46e0e99d43a2b78a27cca97879fd04f6e99`。
- `v1.6.1^{commit}`：`239eb72edc9cee513a4f76c13b9ed38f223fe32b`，与产品发布提交一致。
- GitHub `main` 在发布时已推进到产品发布提交并完成远端回读。
- GitHub Release：[`v1.6.1`](https://github.com/gongyu0918-debug/chinese-official-writing-skill/releases/tag/v1.6.1)。
- Release 状态：`draft=false`、`prerelease=false`，发布时间 `2026-08-11T20:04:48Z`。
- GitHub 返回的 `targetCommitish` 为 `main`；产品事实以 annotated tag 解引用提交为准。
- SkillHub.cn 补充发布来源为仓库维护提交 `cfd33023749215a79a1798cbb4e7459e9996d43e`；canonical 产品内容相对该次 GitHub 追加维护前的 `ff04d9eec4bd0dd84a2680647b074ae58541ca37` 零差异，`v1.6.1` tag 未移动。
- 正式上传只执行一次，回执为 `ok=true`、skillId `70149`、versionId `230797`、46 文件、fingerprint `c35c0399b5a2fb36e3856c0221a76ccb7a4de66b9f73a88a646a761e0fb26911`，`tags.latest=1.6.1`；review、security scan 与 content audit 均为 `pending`。
- 本地清洁包按 SkillHub 内容指纹算法计算的 `content+meta` 哈希与正式回执 fingerprint 完全一致；MIT `LICENSE.md` SHA-256 为 `ead35e40076582d7053fb0908588adb878ff5108601a76647b9f5626b3a0d5f8`。
- 本地复核 zip SHA-256 为 `dfa82b7bc8c2b87fb0ebc1ecde5b2a6568f31af34d2bea6ac4a69c5b3febab27`；该 zip 仅用于发布后验签准备，正式上传走 CLI 的目录 multipart 流程。
- 发布后公开详情已显示 `tags.latest=1.6.1`、版本数由 63 增至 64，并更新为当前 description；`latestVersion.version`、公开搜索和版本签名端点暂时仍为 1.6.0 或未传播。按发行纪律记为索引、审核与签名传播 pending，不重复上传。
- ClawHub 与小红书 Red SkillHub 未执行正式上传。

本节作为发布后证据提交推进 `main`，不移动 `v1.6.1` tag。
