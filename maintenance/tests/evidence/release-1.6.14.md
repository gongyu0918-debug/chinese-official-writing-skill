# v1.6.14 发布记录

日期：2026-08-23

## 发布范围与提交

- 发布产品提交：`b0e5d5c43849b082dd023ba72101689b3eacd0b3`。
- 上一正式产品 tag：`v1.6.13^{commit}=c4ea80a6146a2c672fdec8aeb8de13ed547f33f9`。
- 本轮按用户明确授权发布 GitHub、SkillHub.cn 与 ClawHub `1.6.14`；小红书 Red SkillHub 及其他平台未操作。
- 三个平台均使用公开非付费版；付费提纲能力、胶水、测试和详细规格未进入产品 tag、SkillHub 包或 ClawHub 包。
- ClawHub 使用33文件无 Hook 包；可选 Hook 只进入 GitHub canonical 与 SkillHub.cn 清洁包。

## 主要变化

- `OV-001`：超长收束只在事实、状态、主体、关系、文种功能或直接可用性存在具体风险时失败；一般措辞偏好、变短和单句成段本身不判失败，重复删除目标与保留目标限定为 sentence。
- `HK-008`：Hook 正常终态移除原请求、D0、观察包、候选稿和事务文件，只保留 hash、计数、阶段、选择与交付状态。
- `WR-014-R3`：能力或选项“可安排、可开展”保持“可”，明确“拟、计划、将”保持原强度。
- `UL-005`：清除已完成事项遗留的 `known_hold`，不改变 under-length 运行语义。
- `MT-005c` description 减载因真实稿新增安排和状态升级被拒绝，发布 description 与1.6.13一致。

## 发布前验证

- 定向门首次127/128，唯一失败是 README 最近证据列表遗漏上一正式发布记录；只修证据列表后复跑128/128通过。
- 全量 unittest 660/660通过；canonical、Agent Skills、Qwen Code、Hermes 四套 quick validation 均通过。
- 固定 v1.6.13/current 的确定性消融均为111/111；Promptfoo 本地 stub 20/20通过、Skill 10胜、judge consistency 1.0。
- repository reachability 7/7，Python compileall、四个 JSON 解析、同步幂等和 `git diff --check`通过。
- 独立只读冷审无运行时、包体、坐标、付费实现或 Red SkillHub blocker；冷审发现的产品文件计数措辞已在 tag 前修正。
- Promptfoo 首次从仓库根运行因缺少 `package.json` 未进入评测；改用 `npm.cmd --prefix maintenance` 后通过。一次 ClawHub dry-run 手工展开了错误完整 SHA，最终预检安全停止且没有外部写入；改用 `git rev-parse HEAD` 绑定正确提交后重跑通过。

## 候选包

- SkillHub.cn 清洁包61文件，本地规范化文件树指纹 `89f320da84f6f6f72ed9883e4122935a4e2d53dc410b82d801b252ecd820bec2`。
- ClawHub 无 Hook 包33文件，本地规范化文件树指纹 `87f0f849bd9c5fd8ab63be84c083e839d83eed31a098d83d861b77b56b4030be`；Hook、交付门禁、`agents/openai.yaml` 和付费提纲路径与文本命中数均为0。
- 两包许可证与根 MIT `LICENSE` 的 SHA-256 均为 `ead35e40076582d7053fb0908588adb878ff5108601a76647b9f5626b3a0d5f8`。

## GitHub 回执

- 远端 `main`：`b0e5d5c43849b082dd023ba72101689b3eacd0b3`。
- annotated tag object：`a5564636e5f857a7478060c389e6a40ed303ff96`；`v1.6.14^{commit}`：`b0e5d5c43849b082dd023ba72101689b3eacd0b3`。
- GitHub Release：[`v1.6.14`](https://github.com/gongyu0918-debug/chinese-official-writing-skill/releases/tag/v1.6.14)，`databaseId=375086248`、`id=RE_kwDOSXovUM4WW1yo`、`draft=false`、`prerelease=false`、`published_at=2026-08-23T01:34:41Z`。
- `main` 与 tag 已原子推送。首次 Release 创建因 notes 参数解析失败且未产生 Release；确认不存在后以纯文本说明重试一次成功，没有重复推送 main 或 tag。

## SkillHub.cn 回执与传播状态

- 正式提交一次：`ok=true`、`skillId=70149`、`versionId=262769`、`fileCount=61`、平台 fingerprint `c4fe7dba0b156ea37ad6898f3bdbe4cc49a8e7ff6d603de814ee6e122aa5a04f`。
- slug 为 `chinese-official-writing`，公开坐标为 `@user_f3d82da7/chinese-official-writing`，展示名为“中文公文写作”。
- `latest`、`ai-compute`、`chinese`、`content-creation`、`gongwen`、`office-efficiency`、`official-document`、`writing` tags 均已指向 `1.6.14`。
- 上传回执的 `reviewStatus`、`securityScanStatus`、`contentAuditStatus` 均为 `pending`。首次只读复核中，公开 `tags.latest` 已为1.6.14，`latestVersion` 与版本列表仍停在1.6.13；未重复上传。

## ClawHub 回执与传播状态

- 正式提交一次：`ok=true`、`status=published`、`versionId=k97aavwrmkx3k4d0xrs44jxgpx8d1m0j`、`fileCount=33`、fingerprint `3256085ef4c746b4f99abd05c24c82098b139375563df4bf4f661b468c0fdaa7`。
- slug 为 `chinese-official-writing`，展示名为“中文公文写作”；分类保持 `productivity,knowledge`，话题保持 `chinese-writing,official-writing,office-productivity,content-creation`。
- 正式回执与最终 dry-run 的33文件 fingerprint 完全一致；上传目录为发行 worktree 中的无 Hook OpenClaw 包，source commit 绑定正确产品提交。
- 提交后的首次只读复核仍返回 `latestVersion=1.6.13`、`tags.latest=1.6.13`，精确1.6.14返回 `Version not found`；未重复上传。

## 剩余边界

- SkillHub.cn 与 ClawHub 的正式提交均已受理；公开 latest、精确版本、签名、文件清单和审核/扫描状态按异步传播分别记录，不以旧公开索引否定成功回执，也不重复发布。
- Hook 继续默认关闭并按单能力窄启用；单次真实压缩仍可能需要约4分钟，终态前异常退出与宿主日志不在 HK-008 已证明范围内。
- 付费提纲仍不发布；其结构化组合和真实 Stop 生命周期继续只在付费分支管理。
