# v1.6.25 发布记录

日期：2026-09-03。

状态：`GITHUB_RELEASE_CLOSED / SKILLHUB_PUBLIC_LATEST_SIGNATURE_CLOSED_AUDITS_PENDING / CLAWHUB_PUBLIC_INDEX_CLOSED_SECURITY_CLEAN`。

## 发布范围与提交

- 发布产品提交为 `cf8e181591ea01ba81138352c12b5b93a8acf098`；上一正式产品 tag 为 `v1.6.24^{commit}=105fc3b134ef2c17fb8a541a6e41ec1859c12bb3`。
- 产品增量为 `WR-025 / WR-008b` 建议反馈专叶与标题版式规则，以及 `WR-025c` 第一方证据顺序、外部做法辅助边界和建议型分项标题。`WR-025d` 只形成当前基线充分证据，没有产品改动。
- 产品 tag 之后的候选记录和发布回执不改变产品字节；ClawHub 继续使用 35 文件无 Hook 清洁包。

## 发布门与候选包

- 冻结发行分支的产品 tag 为 `v1.6.25^{commit}=cf8e181591ea01ba81138352c12b5b93a8acf098`，tag object 为 `b41a173d302bb577da4cdcb3ab62205295d51980`；发布前远端 `main@09855cacb32fa5a1655a5ea0ccce372fe997407d` 与固定上一 tag 均为发行分支祖先。
- 聚焦回归 104/104、全量回归 765/765、canonical 与四套公开镜像共五套 `quick_validate.py`、镜像幂等性、185 个 Python 文件语法解析、190 个 JSON 文件解析及 `git diff --check` 均通过；完整冻结记录见 [`release-1.6.25-rc.md`](release-1.6.25-rc.md)。
- 发布回执、公开版本指针与状态台账回填后，`python -m unittest maintenance.tests.test_skill_boundary maintenance.tests.test_status_ledger_consistency maintenance.tests.test_repository_reachability` 为 102/102 通过，`git diff --check` 通过；这些提交位于产品 tag 之后。
- SkillHub.cn 正式包 84 文件，本地规范化文件树 fingerprint 为 `ac419578fd3da59b763fa68c9e5d8a57a94ea37cbb5eb7b593482953bf9e7955`；包内 slug `chinese-official-writing`、展示名“中文公文写作”、版本 `1.6.25`，含 `LICENSE.md`，排除根 `LICENSE` 与 `agents/openai.yaml`。
- ClawHub 正式目录 35 文件，本地规范化文件树 fingerprint 为 `09ad6064bf1cb9aee91019eef889a5eb36a3b3af7945572c2409b05233a90c4a`；Hook 路径、`agents/openai.yaml`、付费提纲和红头实现命中均为 0。dry-run 与正式成功回执的平台 fingerprint 一致，为 `a1298d045f7ee6aadc5b5304da26530e12fb478c0bb038796ef0444d6f4f6c9e`。

## GitHub 回执

- 冻结发行分支与 annotated tag 通过一次 atomic push 成功，无 force push 或 tag 移动；远端 `main` 首次推进到候选记录提交 `ead595b7aeda655104297e56600885e3117c9694`，产品 tag 仍精确指向 `cf8e181591ea01ba81138352c12b5b93a8acf098`。
- GitHub Release：<https://github.com/gongyu0918-debug/chinese-official-writing-skill/releases/tag/v1.6.25>，`databaseId=381769572`、`draft=false`、`prerelease=false`、`publishedAt=2026-09-03T05:53:20Z`。
- 公开更新说明只陈述建议反馈写作、建议对象权限、共性问题归并和标题版式，没有混入内部排除项。

## SkillHub.cn 回执

- slug `chinese-official-writing`、`skillId=70149`、公开坐标 `@user_f3d82da7/chinese-official-writing`、展示名“中文公文写作”保持不变。
- dry-run 先返回 `dryRun=true`、slug 和版本正确；正式提交只执行一次并成功：`ok=true`、`versionId=284959`、`fileCount=84`、平台 fingerprint `3020a30ed01ec615702156a6ddf9b2df22f12e7e97d3408e6009d5548d06fea1`，八个既有 tags 含 `latest` 均在提交回执中指向 1.6.25。
- 提交回执中的 `reviewStatus`、`securityScanStatus`、`contentAuditStatus` 均为 `pending`。公开搜索随后确认精确坐标、中文展示名和 latest 1.6.25；期间没有重复提交。
- 官方 `verify` 对本地 84 文件包的签名核验返回 `ok=true`、`content_hash_match=true`，平台与本地 content hash 均为 `29022f45a1acd90e2b84c6c6927689b066cad79293aca28968b5ef0069160aca`。

## ClawHub 回执

- owner `gongyu0918-debug`、slug `chinese-official-writing`、展示名“中文公文写作”和四个既有 topics 保持不变。
- 首次正式调用携带了平台当前不再接受的旧分类值，在服务端参数校验阶段以 `Unknown skill category slug` 失败；只读精确版本查询确认没有形成 1.6.25。移除无效分类覆盖后执行唯一成功提交：`status=published`、`versionId=k97db83x0f1agxnqa0qy5wkjrd8dp9v5`、`fileCount=35`、平台 fingerprint `a1298d045f7ee6aadc5b5304da26530e12fb478c0bb038796ef0444d6f4f6c9e`，source commit 精确绑定产品提交 `cf8e181591ea01ba81138352c12b5b93a8acf098`。
- 正式成功回执中的 `latestVersion` 仍为 1.6.24；随后只读复核确认公开 latest、`tags.latest` 和精确版本均为 1.6.25。精确版本为 35 文件，禁入路径命中为 0，moderation 与版本级 security 均为 `clean`；期间没有重复成功提交。

## 剩余边界

- GitHub 产品提交、annotated tag 与 Release 已闭环；SkillHub.cn 公开 latest、八个 tags 和本地包签名已闭环，提交回执的三项审核状态仍为 pending；ClawHub 公开 latest、精确 35 文件和 clean 状态已闭环。
- 后续只允许继续做只读审核状态核验；不得因 SkillHub.cn 的异步 pending 再次提交同一版本。
