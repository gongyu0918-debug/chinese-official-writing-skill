# v1.6.26 发布记录

日期：2026-09-04。

状态：`GITHUB_RELEASE_CLOSED / SKILLHUB_PUBLIC_LATEST_SIGNATURE_CLOSED_AUDITS_PENDING / CLAWHUB_PUBLIC_INDEX_CLOSED_SECURITY_CLEAN_WITH_WARNINGS`。

## 发布范围与提交

- 发布产品 tag 为 `v1.6.26`：annotated tag object `636f9ceff2da545c506c8eda0e8c9fc5a8a16f19`，解引用产品提交 `41a477b852062ad9fb66c80a791633cb29ab71f6`；上一产品 `v1.6.25^{commit}=cf8e181591ea01ba81138352c12b5b93a8acf098` 是其祖先。
- 相对 v1.6.25 的公开产品增量包括：`WR-026-R4` 短意见正文组合，`WR-027-R2` 投诉与情况反映专叶，以及 `MT-006` 对建议反馈、投诉、报告、方案和轻量校对运行时说明的语义减载。产品 tag 之后的候选和回执记录不改变发行字节。
- 公开产品不含付费提纲与红头实现；ClawHub 使用 36 文件无 Hook 包。

## 发布门与候选包

- 版本坐标与状态聚焦回归先后为 106/106、103/103 通过；一次全量回归最终为 773/773 通过。首跑发现 P085 仍绑定已删除的维护否定句，改为核对正向事实与联网边界后，目标项和全量均通过。
- canonical、Agent Skills、Qwen Code、QwenWork、Hermes 五套通用 `quick_validate.py` 通过；OpenClaw 的既有 `category` 扩展字段由仓库专项契约覆盖。镜像同步幂等、191 个 Python 文件语法解析、194 个 JSON 文件解析及 `git diff --check` 均通过。完整冻结记录见 [`release-1.6.26-rc.md`](release-1.6.26-rc.md)。
- SkillHub.cn 正式包 85 文件，本地规范化 fingerprint 为 `9869642fcb3c5c9ae6c54e1308025691f46f04d8f60994793e49f9b988004e31`；ClawHub 正式目录 36 文件，本地规范化 fingerprint 为 `442b3a386c9e0950d9940bb5cab972ef6f7c992cb7f2549c7d1f8d0f3248b5d3`，Hook、付费、提纲、红头和 `agents/openai.yaml` 禁入路径命中为 0。

## GitHub 回执

- `main` 与 annotated tag 通过一次 atomic push 成功：远端 `main` 首次推进到 tag 后候选记录提交 `caab10d95e62f3fb9e65432e9a91e2ce6488f860`，tag 仍精确指向 `41a477b852062ad9fb66c80a791633cb29ab71f6`。
- GitHub Release：<https://github.com/gongyu0918-debug/chinese-official-writing-skill/releases/tag/v1.6.26>，`databaseId=382488355`、`draft=false`、`prerelease=false`、`publishedAt=2026-09-04T05:04:33Z`。
- 公开更新说明只陈述本版写作能力、运行时精简和兼容包同步，没有混入内部排除项。

## SkillHub.cn 回执

- slug `chinese-official-writing`、`skillId=70149`、公开坐标 `@user_f3d82da7/chinese-official-writing`、展示名“中文公文写作”保持不变。
- dry-run 返回 `dryRun=true`、slug 和版本正确；正式提交只执行一次并成功：`ok=true`、`versionId=286925`、`fileCount=85`、平台 fingerprint `b760358dc31125e316db65f56d8f1c068fac290a362f051ad0eba56550b8ba5e`，八个既有 tags 含 `latest` 均在提交回执中指向 1.6.26。
- 提交回执中的 `reviewStatus`、`securityScanStatus`、`contentAuditStatus` 均为 `pending`。随后公开搜索已确认精确坐标、中文展示名和 latest 1.6.26；本地 85 文件 ZIP 的平台签名核验返回 `ok=true`、`content_hash_match=true`，平台与本地 content hash 均为 `987711e88d84da45c30dc6843839096193ddea32cbe5a94d27b0ca31955e9090`。期间没有重复提交。

## ClawHub 回执

- owner `gongyu0918-debug`、slug `chinese-official-writing`、展示名“中文公文写作”和四个既有 topics 保持不变。
- dry-run 返回 `would-publish`、36 文件与正确坐标；正式提交只执行一次并成功：`status=published`、`versionId=k970ftnpyf3e1cy84b9mxa87798dsz4x`、`fileCount=36`、平台 fingerprint `a77359597bc67092dc6dca532a774c8959e5144522fe34bfdcbfccf29443cfbb`，source commit 绑定产品提交 `41a477b852062ad9fb66c80a791633cb29ab71f6`。
- 成功回执中的 `latestVersion` 仍为 1.6.25；随后只读核验确认公开 latest 和精确版本均为 1.6.26、精确文件数为 36，moderation、VirusTotal 与 LLM 扫描为 `clean`。Skillspector 单项仍给出 medium/caution 警告，因此只表述总体 clean 并保留分项警告；期间没有重复提交。四个分类 topics 保持不变，`latest` 指向 1.6.26；历史主题 dist-tags 未随本次只更新 `latest` 的发布调用移动。

## 剩余边界

- GitHub 产品提交、annotated tag 与 Release、SkillHub.cn 公开 latest 和签名、ClawHub 公开 latest 与精确 36 文件均已闭环。SkillHub.cn 三项审核仍为 pending；ClawHub 总体 clean，但 Skillspector 分项警告和历史主题 dist-tags 状态如上保留。
- 后续只允许做只读审核状态核验；不得因 pending 再次提交同一版本。
