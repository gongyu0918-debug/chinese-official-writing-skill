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

GitHub、SkillHub 与 ClawHub 的实际提交回执在发布完成后补记。
