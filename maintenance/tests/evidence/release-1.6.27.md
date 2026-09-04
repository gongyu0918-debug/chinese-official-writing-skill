# v1.6.27 发布记录

日期：2026-09-05（Asia/Taipei）。状态：`GITHUB_RELEASE_CLOSED / SKILLHUB_PUBLIC_LATEST_SIGNATURE_CLOSED_AUDITS_PENDING / CLAWHUB_SUBMISSION_ACCEPTED_PUBLIC_INDEX_PENDING`。

## 产品、验证与边界

- 产品为 `v1.6.27^{commit}=0a83ecbf3be21815e72a80593f612eb858613be5`，annotated tag object为 `8a45b6af8c835f7ad70caf1df532873717f6f84f`；上一产品 `v1.6.26^{commit}=41a477b852062ad9fb66c80a791633cb29ab71f6` 是其祖先。发行树为 `codex/release-v1.6.27`，基于当时main `5fbb2d26`及本轮获选改动，验证后快进main；后续文档提交不移动tag。
- 本版包含整改方案专叶与直达路由、已验证的校对绝对路径说明，以及投诉/情况反映页68-byte重复例词删除。AGENTS减少607 UTF-8/LF bytes（15.12%）只计开发纪律，不冒充普通写稿减载。用户撤销示例替换，原示例未改；未操作付费Pro、安装状态或同名Skill副本。
- 投诉与定向审稿两路共8次真实调用全部技术有效，只选择投诉删除；定向审稿36-byte删除因候选独有过程说明恢复。投诉共同联系方向歧义和审稿共同误报保留。整改方案与命令路径复用各自已通过的真实结果，详见[候选记录](release-1.6.27-rc.md)及[本轮逐稿结果](recent-leaf-cleanup-r1/result.md)。
- 发布前最终全量774/774通过（102.473秒）；首轮774项中的两处旧措辞断言失败、对应修正及2项目标复验均保留。五套通用quick validate、镜像幂等、直接结构/禁入路径与包hash检查通过；OpenClaw由仓库专项契约检查。

## GitHub

- [GitHub Release](https://github.com/gongyu0918-debug/chinese-official-writing-skill/releases/tag/v1.6.27) 已公开：`databaseId=383060958`、`isDraft=false`、`isPrerelease=false`、`publishedAt=2026-09-04T23:20:01Z`。
- 一次atomic push将远端main由 `5869234b` 推进到产品tag之后的候选记录提交 `ae9187c9a74935490b92742fed7a55509824d95c`，同时推送annotated tag；tag仍精确绑定上述产品。Release正文只描述本版写作能力、命令路径和精简结果。

## SkillHub.cn

- 坐标 `@user_f3d82da7/chinese-official-writing`、`skillId=70149`、展示名“中文公文写作”保持不变。含Hook包共86文件，使用LICENSE.md；逐文件hash与本地fingerprint见[manifest](release-v1627/package-manifest.json)。
- 正式提交仅一次：`ok=true`、`version=1.6.27`、`versionId=288487`、`fileCount=86`，平台fingerprint `4bc403222d77dc99bf883ee43ba4f04a4c66b3cf8cf578b7dcba6b6746860b98`。回执中的八个既有tags均指向1.6.27；`reviewStatus`、`securityScanStatus`、`contentAuditStatus`均为pending，尚未取得后续审核完成证明。
- 首次公开搜索仍是1.6.26，签名查询返回找不到1.6.27；没有重提。随后只读复核已确认精确公开坐标latest为1.6.27，官方CLI对冻结ZIP返回 `ok=true / content_hash_match=true`，平台与本地content hash均为 `cea9f4c16594b277d2a9b019a5eaab1f243b3e45244b86dce97001e20a6e17ab`。公开latest与签名闭环不等于三项审核已通过。

## ClawHub

- owner为gongyu0918-debug、slug为chinese-official-writing、展示名“中文公文写作”；四个topics保持，只更新latest。无Hook包37文件；不含agents/openai.yaml、付费提纲或红头实现。
- 正式提交仅一次：`ok=true`、`status=published`、`version=1.6.27`、`versionId=k97165q125wnh9vc1wdd38ys5d8dsd0h`、`fileCount=37`，平台fingerprint `6ed68c7cb787ecca3085349af0b2225bcf7e398b4af17b156358345cc16f30fe`与dry-run一致；source commit精确绑定产品0a83ecbf，source ref为v1.6.27。
- 成功回执的latestVersion仍为1.6.26。随后公开latest查询仍显示1.6.26，三次间隔数分钟的1.6.27精确只读查询均返回 `Version not found`；故当前只记提交成功、公开索引pending。旧1.6.26的总体clean与分项警告不能当作新版审核证明，也没有为传播延迟重复上传。

## 证据与后续

[实际调用参数](release-v1627/publish-commands.json)、正式回执和只读核验均在[回执目录](release-v1627/)保留；[回执索引](release-v1627/publication-evidence.json)记录来源、hash、提交次数与当前边界。

发布后README当前版本/近五版证据、specs状态、待办与对应测试坐标已同步；原制度示例逐字等于上一tag。实际运行 `python -X utf8 -B -m unittest maintenance.tests.test_skill_boundary maintenance.tests.test_status_ledger_consistency maintenance.tests.test_repository_reachability`，最终104/104通过（0.570秒）。首跑104项中WR-028仍被旧断言要求留在IN_PROGRESS，已改为核对DONE与已发布覆盖状态，保留该次失败。31份平台原始证据hash、528个本地链接核对通过；产品tag之后的canonical与五套skills目录差异为0，`git diff --check`通过。

本版未修改Hook核心语义。此前的日期示例错绑、错回显耗尽放行、终态重放及晚到覆盖仍登记待修；批量写稿和同稿七版审计也仍有事实外扩、漏改等问题。不能把774项工程门、8次有效调用或四条相关修改链称作98%或普遍可靠率。后续质量改动仍须先真实写稿/同一D0验证；平台后续仅需只读传播及审核核验。
