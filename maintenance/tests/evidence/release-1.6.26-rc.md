# v1.6.26 本地候选记录

日期：2026-09-04。

状态：`PUBLISHED / SEE release-1.6.26.md`。本记录位于产品 tag 之后，不改变 v1.6.26 产品字节；正式平台回执见 [`release-1.6.26.md`](release-1.6.26.md)。

## 候选边界

- `v1.6.26` 是 annotated tag：tag object 为 `636f9ceff2da545c506c8eda0e8c9fc5a8a16f19`，解引用产品提交为 `41a477b852062ad9fb66c80a791633cb29ab71f6`。
- `v1.6.25^{commit}=cf8e181591ea01ba81138352c12b5b93a8acf098` 是本候选祖先；相对上一 tag 共 90 个变更路径，付费、提纲和红头禁入路径命中为 0。
- 本版产品增量包括 `WR-026-R4` 短意见正文组合、`WR-027-R2` 投诉与情况反映专叶，以及 `MT-006-SEMANTIC-REFERENCE-DIET-R1` 对建议反馈、投诉、报告、方案和轻量校对运行时说明的语义减载；canonical 运行时文件在 MT-006 中净减 2,926 bytes。

## 真实写稿与工程门

- 写稿语义 R2/R3 已完成五家 provider 真实 A/B：R2 共 50 份输出、49 份有效，R3 共 10 份有效；所选候选 5/5 直接交正文，未出现与本次差异相关的事实、状态、文种或交付形态硬回退。纯维护声明删除按用户校准只做结构、镜像和最小校验。
- 版本坐标与状态聚焦回归先后为 106/106、103/103 通过；一次全量回归最终为 773/773 通过，耗时 112.344 秒。全量首跑暴露 P085 仍要求已删除的维护否定句，改为核对正向事实与联网边界后，目标两项与最终全量均通过。
- canonical、Agent Skills、Qwen Code、QwenWork、Hermes 五套通用 `quick_validate.py` 均通过；OpenClaw 使用其既有 `category` 扩展字段，由仓库专项契约覆盖，不冒充通用 Codex validator 通过。
- `python maintenance/tools/sync_adapters.py` 复跑无产品差异；191 个受控 Python 文件通过语法解析，194 个受控 JSON 文件通过解析；`git diff --check` 通过。冻结记录落盘前另跑状态/可达性 23/23 通过。

## 本地包预检

- SkillHub.cn 包位于 `output/release-v1.6.26-41a477b8/skillhub/chinese-official-writing`，共 85 文件，规范化文件树 fingerprint 为 `9869642fcb3c5c9ae6c54e1308025691f46f04d8f60994793e49f9b988004e31`。slug 为 `chinese-official-writing`、展示名为“中文公文写作”、版本为 `1.6.26`，含 canonical Hook，排除根 `LICENSE` 与 `agents/openai.yaml`，使用 `LICENSE.md`；官方 CLI dry-run 返回 `dryRun=true`。
- ClawHub 无 Hook 包位于 `packages/openclaw/skills/chinese_official_writing`，共 36 文件，规范化文件树 fingerprint 为 `442b3a386c9e0950d9940bb5cab972ef6f7c992cb7f2549c7d1f8d0f3248b5d3`；平台 dry-run fingerprint 为 `2abc22cb96c3c3ab090c83a3acbce0c7a445d3a16b60192c0f2041944ed9a9f4`。dry-run 返回 `would-publish`，slug、展示名、owner、版本和文件数正确；Hook、付费、提纲、红头及 `agents/openai.yaml` 命中为 0。
- 发布前只读查询确认：SkillHub.cn 登录账号为 `user_f3d82da7`，ClawHub owner 为 `gongyu0918-debug` 且公开 latest 为 1.6.25；GitHub 远端不存在 v1.6.26 tag 或 Release。上述均不是正式发布回执。

## 发布边界

- GitHub、SkillHub.cn、ClawHub 均复用本 tag 与上述冻结包面完成正式发布；三个平台的精确回执和异步传播状态见正式发布记录。每个平台成功提交一次后只做只读传播核验，不因审核或索引延迟重复提交。
