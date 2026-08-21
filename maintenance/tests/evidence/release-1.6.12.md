# v1.6.12 发布记录

日期：2026-08-21

## 发布范围与提交

- 发布产品提交：`ae4a25b497fab1ccdd621ffbf21e43501701f8b9`。
- 上一正式产品 tag：`v1.6.11^{commit}=15af538adfb5ec6a711770d67ec265498ec7127d`。
- 本轮按用户明确授权发布 GitHub、SkillHub.cn 与 ClawHub `1.6.12`；Red SkillHub 及其他平台未操作。
- 三个平台均使用公开非付费版；`codex/paid-outline-review` 的提纲能力、胶水、测试和详细规格未进入产品 tag、SkillHub 包或 ClawHub 包。
- ClawHub 使用33文件无 Hook 包；可选 Hook 只进入 GitHub canonical 与 SkillHub 清洁包。

## 主要变化

- 原子化精简 Skill description，删除已由上位类别或正文边界覆盖的重复负向句、新闻细项和文种别名，减少每次发现阶段的上下文开销。
- 每个减载原子先做正向触发、相邻非触发和真实成稿 A/B；制度、函件、讲话致辞和受众合并等出现候选独有硬回退的较大方案均未进入本版。
- 固定消融契约改为同时检查上位类别入口和叶子路由，不再要求 description 保留已验证可删的逐字枚举。

## 发布前验证

- 版本面与包体定向测试87/87通过。
- 全量测试首次639/640，唯一失败是旧断言仍要求 description 逐字包含“采购公告”；更新为“公告”上位入口并继续检查“采购公告”叶子路由后，单项1/1、最终全量640/640通过。
- 固定 v1.6.11 与当前候选的确定性消融均为111/111。
- canonical、Agent Skills、Qwen Code、Hermes 通过 quick validation；`sync_adapters.py` 二次执行无差异，`git diff --check`通过。
- SkillHub 清洁包61文件，CRLF→LF 规范化文件树指纹为 `62764bf3bff9e2f5e0c7829252997462efd101678f4873ab1d9c5752de89479a`。
- ClawHub 无 Hook 包33文件，同口径指纹为 `620ccd494314d240d2e2a4e76bf031b6c35c9679f885834f1b0275eed52b870d`；Hook、交付门禁、`agents/openai.yaml` 和付费提纲文件命中数均为0。
- 正式上传所用根 checkout 与发行 worktree 有4个文本文件仅 CRLF/LF 物理换行不同，规范化后33文件完全一致；因此 dry-run 与正式回执 fingerprint 分别保留，不互相冒充。

## GitHub 回执

- 首次发布推送后远端 `main`：`ae4a25b497fab1ccdd621ffbf21e43501701f8b9`。
- annotated tag object：`32d7d6f2b33395208672473ff41c2523ab36b76a`；`v1.6.12^{commit}`：`ae4a25b497fab1ccdd621ffbf21e43501701f8b9`。
- GitHub Release：[`v1.6.12`](https://github.com/gongyu0918-debug/chinese-official-writing-skill/releases/tag/v1.6.12)，`id=374191251`、`node_id=RE_kwDOSXovUM4WTbST`、`draft=false`、`prerelease=false`、`published_at=2026-08-21T05:44:08Z`。
- 本发布证据在 tag 之后单独推进 `main`，不移动已发布 tag。

## SkillHub.cn 回执与传播状态

- 正式提交一次：`ok=true`、`skillId=70149`、`versionId=255236`、`fileCount=61`、平台 fingerprint `248d26d053a60e7e85102839441047a94799cfc399aeade8f8d71a001b4fd1bd`。
- slug 为 `chinese-official-writing`，公开坐标为 `@user_f3d82da7/chinese-official-writing`，展示名为“中文公文写作”。
- `latest`、`ai-compute`、`chinese`、`content-creation`、`gongwen`、`office-efficiency`、`official-document`、`writing` tags 均已指向 `1.6.12`。
- 上传回执的 `reviewStatus`、`securityScanStatus`、`contentAuditStatus` 均为 `pending`。提交后的首次只读复核中，公开 tags 已更新，`latestVersion` 与版本列表仍停在1.6.11；未重复上传。

## ClawHub 回执与传播状态

- 第一次正式命令因 PowerShell 将未加引号的分类参数合并成无效 slug，在包提交前退出；随后精确查询确认1.6.12不存在，再以加引号的原分类参数执行一次有效正式提交。
- 有效正式提交：`ok=true`、`status=published`、`versionId=k9768g59e2hwbwjf33acgxjzrd8cxe03`、`fileCount=33`、fingerprint `f5835b689e42d5cbda04d31c16393d9a95ee23e169fde86249304b9b26d1ea57`。
- slug 为 `chinese-official-writing`，展示名为“中文公文写作”；分类提交为 `productivity,knowledge`，话题为 `chinese-writing,official-writing,office-productivity,content-creation`。
- 发布前发行 worktree dry-run 的33文件平台 fingerprint 为 `c118b2be2518c68115399d4569db9eac9538bddbee2cb65c4ae4f0b413b9981d`；正式回执使用根 checkout 的物理换行口径，按上一节记录为不同事实。
- 提交后的首次只读复核曾返回 `Version not found`；未重复上传。随后公开 `latestVersion` 与精确版本均为1.6.12，moderation 为 `clean`。远端33个文件逐项与正式上传所用根 checkout 比较：缺失0、哈希不一致0、多余0；Hook、交付门禁、`agents/openai.yaml` 和付费提纲文件命中数为0。
- ClawHub 页面按平台统一规则显示 MIT-0；GitHub 仓库和上传包内 `LICENSE` 使用根 MIT 许可证。

## 剩余边界

- SkillHub.cn 的公开 latest、版本列表和审核/扫描仍待平台异步传播；正式回执和 tags 已存在，不因索引滞后重复发布。
- `UL-005`、`OT-001` Stop 收紧、`OT-002`、`WR-010` sidecar、`WR-011`、`WR-012` 与付费提纲组合继续 HOLD，未进入本版本。
