# v1.6.23 发布记录

日期：2026-09-01。

状态：`GITHUB_RELEASE_CLOSED / SKILLHUB_PUBLIC_LATEST_CLOSED_SECURITY_REPORTS_QUEUED / CLAWHUB_PUBLIC_INDEX_CLOSED_SECURITY_CLEAN`。

## 发布范围与提交

- 发布产品提交为 `6a6ededa2ec287f68457ec1d5762aabae8e79bac`；上一正式产品 tag 为 `v1.6.22^{commit}=4b135c506b4b4d61f49115298bc78564b5ec8f50`。
- 本轮按用户明确授权发布 GitHub、SkillHub.cn 与 ClawHub `1.6.23`。产品增量为 `UL-006-CONTRACT-R1 / HK-009-STOP-BUDGET-R1` 的事故入口契约、单次 Stop 共享预算、可信恢复和有限失败脱敏，以及 `MT-004b-REVIEW-DIRECT-LEAF-R1/R2` 的点名只审轻页。
- `WR-025` 建议反馈专叶与 `WR-008b` 小标题文本规则不在产品 tag 的祖先或上传包中；它们继续作为发布后的下一版本候选。付费提纲、Pro Hook、红头 DOCX 与 Red SkillHub 未操作。

## 发布门与候选包

- 冻结发行 worktree 为 `codex/release-v1.6.23@88eec00e0f0e18d2a9fe5334811bf3521462565a`。发布前远端 `main@d32c3fec3637a4d81b6c02bcfbfd432726fe1ace` 和固定上一 tag 均为冻结候选祖先；产品 tag 固定在版本坐标提交，候选记录和回执文档不进入产品 tag。
- 冻结坐标上一次全量回归为756/756；确定性真实题面消融为固定 v1.6.22 与候选各111/111，Promptfoo stub smoke为20/20，五套 Skill Creator quick validate、tracked Python/JSON检查和镜像幂等性均通过。正式发布前又复跑发布边界、包构建、Hook契约、状态台账和仓库可达性108/108，并通过 `git diff --check`。
- SkillHub.cn 正式包83文件，本地规范化文件树 fingerprint 为 `3c40dad50434d9f297c7b844357de72f5f439e0b1b932ce7903be926404ccf9a`；包内 slug `chinese-official-writing`、展示名“中文公文写作”、版本`1.6.23`，含`LICENSE.md`，排除根`LICENSE`与`agents/openai.yaml`。
- ClawHub 正式目录34文件，本地规范化文件树 fingerprint 为 `f0f69ba6322889643fa53654734e7c2293128f3e42738fddcce8f933d57edda8`；Hook路径、`agents/openai.yaml`、付费提纲、Pro Hook和红头实现命中均为0。dry-run返回`would-publish`、34文件和平台 fingerprint `6dda63353fdbcb760e235b7bca2388cfbac8171ce9f831abcf78c3428278f770`。

## GitHub 回执

- `main` 与 annotated tag 通过一次 atomic push 成功，无 force push 或 tag 移动。远端 `main` 推进到 `88eec00e0f0e18d2a9fe5334811bf3521462565a`；tag对象为`736c5569d5772274a1b8f603d02b8171bb449910`，`v1.6.23^{commit}=6a6ededa2ec287f68457ec1d5762aabae8e79bac`。
- GitHub Release：<https://github.com/gongyu0918-debug/chinese-official-writing-skill/releases/tag/v1.6.23>，`databaseId=380131617`、`draft=false`、`prerelease=false`、`publishedAt=2026-09-01T00:09:34Z`。
- 公开更新说明只陈述复杂终审一致性、失败恢复和点名审稿轻量路径，没有混入内部排除项。

## SkillHub.cn 回执

- slug `chinese-official-writing`、`skillId=70149`、公开坐标 `@user_f3d82da7/chinese-official-writing`、展示名“中文公文写作”保持不变。
- dry-run先返回`dryRun=true`、slug和版本正确；正式提交只执行一次并成功：`ok=true`、`versionId=279383`、`fileCount=83`、平台 fingerprint `37c8f1cfa23381017390c983ed6b7f5bb98ac127c95ba9cabd07b4539b1dab75`，八个既有 tags 含`latest`均在提交回执中指向1.6.23。
- 提交回执中的`reviewStatus`、`securityScanStatus`、`contentAuditStatus`均为`pending`。首次只读公开接口中 tags 已切换为1.6.23，`latestVersion`仍为1.6.22；随后只读复核确认`latestVersion`与八个既有tags均已切换为1.6.23，slug、展示名、公开坐标和更新说明正确。Keen、Sanbu 报告仍为`queued`，不从公开latest反推提交回执中的三项内部状态，也不重复提交。

## ClawHub 回执

- owner `gongyu0918-debug`、slug `chinese-official-writing`、展示名“中文公文写作”、分类`productivity,knowledge`、话题`chinese-writing,official-writing,office-productivity,content-creation`保持不变。
- 正式提交只执行一次并成功：`status=published`、`versionId=k97da1z02hxs6cd58a9txyahb98dkv4w`、`fileCount=34`、平台 fingerprint `6dda63353fdbcb760e235b7bca2388cfbac8171ce9f831abcf78c3428278f770`。
- 提交回执中的`latestVersion`仍为1.6.22；首次精确1.6.23只读检查返回`Version not found`，公开 latest 也仍为1.6.22。随后只读复核确认公开latest、`tags.latest`和精确版本均为1.6.23；精确版本为34文件，Hook路径和`agents/openai.yaml`均为0，moderation与版本级security均为`clean`，许可证显示平台既有`MIT-0`。期间未重复上传。

## 剩余边界

- GitHub产品提交、annotated tag和Release已闭环；SkillHub.cn公开latest已闭环，外部安全报告仍排队；ClawHub公开latest、精确版本文件和clean状态已闭环。三个平台均未重复提交。
- 产品 tag 与两类已提交包均不含 `WR-025 / WR-008b`。这两个已验证原子随后仅合入本地下一版本`main`，未推送、未移动v1.6.23 tag、未修改已提交包，也未把下一版本本地预检包冒充本次发行物。
