# v1.6.24 发布记录

日期：2026-09-02。

状态：`GITHUB_RELEASE_CLOSED / SKILLHUB_PUBLIC_LATEST_SIGNATURE_CLOSED_REPORTS_QUEUED / CLAWHUB_PUBLIC_INDEX_CLOSED_SECURITY_CLEAN`。

## 发布范围与提交

- 发布产品提交为 `105fc3b134ef2c17fb8a541a6e41ec1859c12bb3`；上一正式产品 tag 为 `v1.6.23^{commit}=6a6ededa2ec287f68457ec1d5762aabae8e79bac`。
- 本轮按用户明确授权发布 GitHub、SkillHub.cn 与 ClawHub `1.6.24`。产品增量为 `WR-005b` 短稿任务的语义化识别，以及可选 Hook README 中使用说明与暂停/关闭说明的顺序调整。
- 产品 tag 之后的候选记录和发布回执不改变产品字节；ClawHub 继续使用 34 文件无 Hook 包。

## 发布门与候选包

- 冻结发行分支的产品 tag 为 `v1.6.24^{commit}=105fc3b134ef2c17fb8a541a6e41ec1859c12bb3`。发布前远端 `main@0336084f64013e8e93b2b61eacd4d445fb23e7a1` 与固定上一 tag 均为发行分支祖先。
- 聚焦回归 101/101、全量回归 756/756、canonical 与四套公开镜像共五套 `quick_validate.py`、镜像幂等性和 `git diff --check` 均通过；完整冻结记录见 [`release-1.6.24-rc.md`](release-1.6.24-rc.md)。
- 发布回执、公开版本指针与状态台账回填后，`python -m unittest maintenance.tests.test_skill_boundary maintenance.tests.test_status_ledger_consistency` 为 93/93 通过，`git diff --check` 通过；这些提交位于产品 tag 之后。
- SkillHub.cn 正式包 83 文件，本地规范化文件树 fingerprint 为 `c7c154b748b4ab974b893da564a9282e20cdc2751b1469f1f8e43c8eb01fe59f`；包内 slug `chinese-official-writing`、展示名“中文公文写作”、版本 `1.6.24`，含 `LICENSE.md`，排除根 `LICENSE` 与 `agents/openai.yaml`。
- ClawHub 正式目录 34 文件，本地规范化文件树 fingerprint 为 `58db6cfcafb14b886619faaa677981e56bdae20e80c82099b013424e49dc09f2`；Hook 路径、`agents/openai.yaml`、付费提纲、Pro Hook 和红头实现命中均为 0。dry-run 与正式回执的平台 fingerprint 一致，为 `ac29da4032bf9b9bedf0c788286caf6f9bf27519efd10d52e18eca7164fcd7db`。

## GitHub 回执

- `main` 与 annotated tag 通过一次 atomic push 成功，无 force push 或 tag 移动。首次远端 `main` 推进到候选记录提交 `f915307b3314aa33f14ee10666aad2a377c84487`；tag 对象为 `9220d5a1f58448666290b334f2194ee58f9a5bf0`，`v1.6.24^{commit}=105fc3b134ef2c17fb8a541a6e41ec1859c12bb3`。
- GitHub Release：<https://github.com/gongyu0918-debug/chinese-official-writing-skill/releases/tag/v1.6.24>，`databaseId=380901628`、`draft=false`、`prerelease=false`、`publishedAt=2026-09-02T00:17:48Z`。
- 公开更新说明只陈述短稿语义识别与可选 Hook 说明顺序，没有混入内部排除项。

## SkillHub.cn 回执

- slug `chinese-official-writing`、`skillId=70149`、公开坐标 `@user_f3d82da7/chinese-official-writing`、展示名“中文公文写作”保持不变。
- dry-run 先返回 `dryRun=true`、slug 和版本正确；正式提交只执行一次并成功：`ok=true`、`versionId=281889`、`fileCount=83`、平台 fingerprint `f1e53d8c7716f997bc37449cc55584323e4062cc871f9c267c399fa48eda9c5a`，八个既有 tags 含 `latest` 均在提交回执中指向 1.6.24。
- 提交回执中的 `reviewStatus`、`securityScanStatus`、`contentAuditStatus` 均为 `pending`。首次只读搜索仍显示公开 latest 为 1.6.23；随后公开接口确认 `latestVersion` 与八个既有 tags 均已切换为 1.6.24，slug、展示名、公开坐标和更新说明正确。
- 官方 `verify` 对本地 83 文件包的签名核验返回 `ok=true`、`content_hash_match=true`，平台与本地 content hash 均为 `3bd49798d7e4d28359aca678289ddc3ffd6d56d25e2a331829a8e83733e55664`。Keen 与 Sanbu 报告仍为 `queued`；期间未重复提交。

## ClawHub 回执

- owner `gongyu0918-debug`、slug `chinese-official-writing`、展示名“中文公文写作”、分类 `productivity,knowledge`、话题 `chinese-writing,official-writing,office-productivity,content-creation` 保持不变。
- 正式提交只执行一次并成功：`status=published`、`versionId=k972sdvqbb8gvxpvzngcqpgj9h8dnnbb`、`fileCount=34`、平台 fingerprint `ac29da4032bf9b9bedf0c788286caf6f9bf27519efd10d52e18eca7164fcd7db`，source commit 精确绑定产品提交 `105fc3b134ef2c17fb8a541a6e41ec1859c12bb3`。
- 提交回执中的 `latestVersion` 仍为 1.6.23；首次精确 1.6.24 只读检查返回 `Version not found`，公开 latest 也仍为 1.6.23。随后只读复核确认公开 latest、`tags.latest` 和精确版本均为 1.6.24；精确版本为 34 文件，禁入路径命中为 0，moderation 与版本级 security 均为 `clean`。期间未重复上传。

## 剩余边界

- GitHub 产品提交、annotated tag 与 Release 已闭环；SkillHub.cn 公开 latest、八个 tags 和本地包签名已闭环，外部安全报告仍排队；ClawHub 公开 latest、精确 34 文件和 clean 状态已闭环。
- 只允许继续做只读传播核验；不得因公开索引暂未更新而再次提交同一版本。
