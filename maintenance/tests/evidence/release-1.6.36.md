# v1.6.36 发布记录

## 授权与版本范围

2026年9月14日，用户明确授权将最新 v1.6.36 发布到 GitHub、SkillHub 和 ClawHub。发布沿用已验证的 1.0 主线同步候选；v1.6.35 及其 Release 说明不作修改，也不联系 2.0 构筑线。

相较 v1.6.35，本版将通知与公开发布、决策部署、讲话致辞、调研可研、采购审查分流到更聚焦的写作路径，补充多人出席讲话开场的称谓顺序处理，并加强说明式开场识别。公开更新说明统一使用 [`release-v1636/release-notes.md`](release-v1636/release-notes.md) 的自然语言正向表述。

仓库、canonical Skill、各兼容 Skill、SkillHub clean package 和 OpenClaw/ClawHub 包继续采用 MIT 许可证；授权随 1.0 版本后续更新延续。

## 产品与平台边界

- GitHub 发布完整 1.0 仓库；SkillHub 使用含公开 Hook 的 clean package。
- ClawHub 使用 `packages/openclaw/skills/chinese_official_writing` 的无 Hook 兼容包。
- GitHub、SkillHub、ClawHub 各正式提交一次；成功回执、公开索引与审核状态分别记录，不因传播延迟重复提交。

## 发布前验证

- 候选产品提交：`2a629d361bbfab8c1d884bdf802544a7c2c0790a`；候选证据提交：`6ab57e0a7ce5b770fcbd602bc07d4644eea7a3db`。
- 候选全量 unittest：851/851 通过；版本、包边界、许可、可达性聚焦回归：110/110 通过；五套普通 Skill quick validation：5/5 通过。
- 发布日最终树再次运行全量 unittest：851/851 通过，耗时 148.014 秒；五套普通 Skill quick validation 仍为 5/5 通过。
- `sync_adapters.py` 幂等，`git diff --check` 通过；七份仓内 Skill 许可证 SHA-256 均为 `ead35e40076582d7053fb0908588adb878ff5108601a76647b9f5626b3a0d5f8`。
- SkillHub clean package 为 104 文件；ClawHub 无 Hook 包为 53 文件。两端 v1.6.36 dry-run 均通过。
- 发布日再次核对远端 `origin/main` 和 `v1.6.35^{commit}` 均为 `c0abfeeb3d2a21cfd6ec722de7d8ae534ad68f61`；远端 v1.6.36 tag、GitHub Release、SkillHub v1.6.36 和 ClawHub v1.6.36 均不存在。

## 发布回执

### GitHub

- 发布提交与 `v1.6.36^{commit}`：`92af987bf8a1b96e95a6e22bb0d33165cabd13d7`。
- annotated tag object：`33183605b724a1889a39f5263afad82eb06401f6`。
- `main` 与 tag 已原子推送；GitHub Release ID：`388079381`。
- Release：<https://github.com/gongyu0918-debug/chinese-official-writing-skill/releases/tag/v1.6.36>；`draft=false`、`prerelease=false`。
- 公开更新说明文件 SHA-256：`98518bef366241d00b22f9aa7f1e6ca96b885342672037cf556cc7b66e4363d4`。

### SkillHub

- 正式提交成功：`ok=true`、`version=1.6.36`、`versionId=310553`、`fileCount=104`。
- 上传 ZIP SHA-256：`46faf818759ee63386e05b1059ac4afcf34d7cdaf5b0ca157c5960118884c0a2`；平台 fingerprint：`b1d75e382eaefc73f8d57af1e1cf84bb4db753b101fc1726f91e8ff2a23b9034`。
- 回执中 `tags.latest=1.6.36`；`reviewStatus=pending`、`securityScanStatus=pending`、`contentAuditStatus=pending`。提交成功不等于审核完成，不重复提交。

### ClawHub

- 正式提交成功：`status=published`、`version=1.6.36`、`versionId=k97738x9bs05cqvb3tzxnxbhkn8ecmzx`、`fileCount=53`。
- 无 Hook 包快照 ZIP SHA-256：`3f393aee484131d7a020b2e550ecc9e8aedc79aaa64c6b20414c2195c06e1207`；正式回执 fingerprint：`cdedd672ccaaa481bb63c5c7f727209f720098be01286e2a0b4c0f049d677550`。
- 正式回执的 `latestVersion` 仍为 `1.6.35`，按传播状态记录；取得成功回执后不轮询、不重复提交。

### 收口状态

GitHub、SkillHub 与 ClawHub 均已完成各自唯一一次正式提交。后续证据提交只更新 GitHub `main`，不移动 `v1.6.36` tag，不改 Release 正文，也不再次提交两个平台。
