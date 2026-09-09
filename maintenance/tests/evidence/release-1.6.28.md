# v1.6.28 发布记录

日期：2026-09-06（Asia/Taipei）。状态：`GITHUB_RELEASE_CLOSED / SKILLHUB_SUBMISSION_ACCEPTED_SIGNATURE_PENDING_AUDITS_PENDING / CLAWHUB_SUBMISSION_ACCEPTED_PUBLIC_INDEX_PENDING`。

## 产品与验证

- 按用户“暂时先以当前main”授权发布，基线为 `01ade37fb798eb087e976bb20407a0f0261fc783`，独立分支 `codex/release-v1.6.28`；版本提交及产品tag为 `1d705aeadbcbdc5a818dd7f990e1905249c5f1e8`。上一tag `v1.6.27` 为祖先。main已快进并与新tag一次atomic push；后续证据提交不移动tag。
- 纳入已准入的日期来源绑定、终态重放/晚到事件、默认回显失败、显式关闭与取消清理修复，DSH当前回合取消、OpenCode插件失败分类，以及新闻完整事实日期规则。当前main的产品逐字等于已验证的 `a2a817d1`；发行层只更新14处文件的版本坐标/对应测试断言。[独立范围与敏感扫描](release-v1628/scope-review.json)
- 未合入Hook机会审计分支 `60133253`，未恢复已拒绝的reference/workflow候选，未操作付费Pro、示例或本机安装。
- 最终全量 **806/806通过，145.071秒**；五套quick validate通过。初次默认Python指向Hermes环境，quick validate缺PyYAML，全量尝试被中止；改用既有Python313后通过，不把环境失败计为产品回退。没有新增写稿模型调用；复用[已合入修复的真实证据](remaining-hook-quality-merge-r1/result.md)和[四项修复](hook-four-fixes-merge-r1/result.md)，未重跑原生宿主。
- SkillHub冻结包86文件、ClawHub无Hook包37文件，两平台dry-run通过，禁入路径检查通过。SkillHub ZIP的86个成员逐字匹配冻结目录，ZIP SHA-256 `0e3680fccf4b952e6dae741590d3d81cd46ca8a890dbf5a054c6d12116c07f20`，CLI content hash `9fc48c67ba5eb8caa855fe5a3b6e25a35ed5b3606df4afb856e198a8da062b72`。[逐文件manifest](https://github.com/gongyu0918-debug/chinese-official-writing-skill/blob/0721297298b72be7a37b93c6598172791b58e421/maintenance/tests/evidence/release-v1628/package-manifest.json) [ZIP核对](https://github.com/gongyu0918-debug/chinese-official-writing-skill/blob/0721297298b72be7a37b93c6598172791b58e421/maintenance/tests/evidence/release-v1628/zip-check.json)

实际命令（python使用 `C:/Users/admin/AppData/Local/Programs/Python/Python313/python.exe`）：

```text
python -B -X utf8 -m unittest discover -s maintenance/tests -p "test_*.py"
python -B -X utf8 C:/Users/admin/.codex/skills/.system/skill-creator/scripts/quick_validate.py <canonical及四套普通Skill目录>
python -B -X utf8 maintenance/tools/build_skillhub_package.py --output output/release-v1.6.28/skillhub/chinese-official-writing --version 1.6.28
git diff --check
git push --atomic origin HEAD:main refs/tags/v1.6.28
```

版本同步调用既有 `sync_adapters.main()`，事前核准五个删除重建目标均在独立发行树packages内，且没有未跟踪文件或符号链接。通用validator不用于OpenClaw扩展字段，由全量仓库契约覆盖。日志与实际平台参数见[回执目录](https://github.com/gongyu0918-debug/chinese-official-writing-skill/blob/0721297298b72be7a37b93c6598172791b58e421/maintenance/tests/evidence/release-v1628/publication-evidence.json)。

## 平台结果

- [GitHub Release](https://github.com/gongyu0918-debug/chinese-official-writing-skill/releases/tag/v1.6.28)已公开，`isDraft=false`、`isPrerelease=false`、`publishedAt=2026-09-05T22:26:33Z`。
- SkillHub.cn `@user_f3d82da7/chinese-official-writing`：唯一正式提交 `ok=true`，`versionId=291966`、86文件、fingerprint `4f95005ab6dca12799bbb4ae519acc923bb0d30d8a83cf47b7aff3928022e1d3`；八个既有tags均指向1.6.28。review/security/content三项审核pending。三次只读签名查询（含显式namespace复核）仍返回找不到1.6.28，因此只证明提交已接受，不证明公开签名传播完成。
- ClawHub `gongyu0918-debug/chinese-official-writing`：唯一正式提交 `status=published`，`versionId=k97dh3rey9y8sjd39f94a7exk58dvsav`、37文件、fingerprint `bd9b19d6faaffc48b26be43c9b2189fefec19e47b5933c31aca1f82767ae34a5`与dry-run一致。source commit/ref绑定产品tag。两次精确版本只读查询仍为 `Version not found`，公开索引pending；不因传播延迟重提，也不把旧版审核结果当新版证明。

## 保留边界

DSH取消仅有SDK验证，OpenCode是插件侧停止/失败分类；CodeBuddy/Kimi独立硬停、已显示正文、持续I/O故障与没有后续清理事件的留存边界仍在。批量成稿和多版质量未闭环，806项工程通过不能换算成普遍无错率。下一轮Hook参与、正文清壳、自然上限与原稿事实核验仍是未发布的待验证方向。

平台原始回执、精确提交参数、冻结包hash和失败记录见[证据索引](https://github.com/gongyu0918-debug/chinese-official-writing-skill/blob/0721297298b72be7a37b93c6598172791b58e421/maintenance/tests/evidence/release-v1628/publication-evidence.json)。发布后文档/状态检查另记 `release-v1628/post-release-validation.json`；不回写旧实验或移动产品tag。
