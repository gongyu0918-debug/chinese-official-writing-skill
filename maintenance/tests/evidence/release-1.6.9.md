# v1.6.9 发布记录

日期：2026-08-18

## 发布范围与提交

- 发布产品提交：`5047c224456183d97dd46cb5be09506bfdcfd0b8`。
- 上一正式产品 tag：`v1.6.8^{commit}=6b1dc2c507d2a7f240506a036c6859620dd0f43a`。
- 本轮按用户明确授权发布 GitHub、SkillHub.cn 与 ClawHub `1.6.9`；Red SkillHub 及其他平台未操作。
- ClawHub 使用33文件无 Hook 包；可选 Hook 只进入 GitHub canonical 与 SkillHub 清洁包。

## 主要变化

- 修复可选超长收束 Hook 对“约、左右、上下”等软性字数表达的误触发。
- 加强长引语、无标点编号正文、否定责任短语和同动词多拟办对象的保护。
- 完善自然审稿识别；常用审稿表达保持只审不改，审后改写和材料引语仍按成稿任务处理。
- SkillHub `50k+` 徽章和维护记录不属于产品更新说明，未写入三端更新日志。

## 发布前验证

- 全量单元测试617/617通过；发行边界聚焦测试120/120、三宿主与 Hook 聚焦测试41/41、最终 smoke 5/5通过。
- canonical 与四个普通镜像通过 quick validation；同步幂等、相关 Python 编译检查和 diff check 通过。
- SkillHub 清洁包60文件，本地逐文件集合哈希为 `da3b0ced66e815df87c5eb22945bb38ded0047e5d0c805fe71afbb740b3dbbb3`。
- ClawHub 无 Hook 包33文件，本地逐文件集合哈希为 `046aac1a88f1d962b424dd9a106b1a18d60ecf0df79e202898e7650f75adcfc0`。
- 两包许可证 SHA-256 均为 `ead35e40076582d7053fb0908588adb878ff5108601a76647b9f5626b3a0d5f8`，与根 MIT `LICENSE` 一致。

## GitHub 回执

- 发行时远端 `main`：`5047c224456183d97dd46cb5be09506bfdcfd0b8`。
- annotated tag object：`ffa42f308fafd722f5effbb0110b2ffe9345975f`；`v1.6.9^{commit}`：`5047c224456183d97dd46cb5be09506bfdcfd0b8`。
- GitHub Release：[`v1.6.9`](https://github.com/gongyu0918-debug/chinese-official-writing-skill/releases/tag/v1.6.9)，`id=RE_kwDOSXovUM4WLHwR`、`draft=false`、`prerelease=false`、`published_at=2026-08-18T00:01:44Z`。
- 本发布证据在 tag 之后单独推进 `main`，不移动已发布 tag。

## SkillHub.cn 回执与传播状态

- 正式提交一次：`ok=true`、`skillId=70149`、`versionId=242935`、`fileCount=60`、平台 fingerprint `f73f3d3f1839ef4071e72e6d148df667ddac649472bbc89b928c5bf35eb2872e`。
- `latest`、`ai-compute`、`chinese`、`content-creation`、`gongwen`、`office-efficiency`、`official-document`、`writing` tags 均已指向 `1.6.9`；公开版本计数为72。
- 上传回执的 `reviewStatus`、`securityScanStatus`、`contentAuditStatus` 均为 `pending`。提交后只读复核时 `latestVersion` 仍为1.6.8，1.6.9精确版本签名返回404；属于平台异步传播，不重复上传。

## ClawHub 回执与传播状态

- 正式提交返回 `ok=true`、`status=published`、`versionId=k97ebbfvew6pp8383m7rhpd46h8cpv5c`、`fileCount=33`、fingerprint `a24b1934008a09a00376551594645f6c45918fd2221adcc321a619a8b482a2d0`。
- 展示名为“中文公文写作”；公开 `latestVersion`、`tags.latest` 和精确版本均为1.6.9。
- 远端33个文件逐项与本地发布包比较：缺失0、哈希不一致0、多余0。
- 公开 moderation verdict 为 `clean`；VirusTotal 状态仍为 pending/stale，Skillspector 保留两项中等级提示，平台 LLM 扫描为 clean。ClawHub 页面按平台统一规则显示 MIT-0，GitHub 仓库和仓内包仍采用根 MIT 许可证。
- 第一次正式命令在写入版本前因无效分类 slug `writing` 被拒绝；移除该参数并按用户指定展示名重跑后一次成功，没有产生重复版本。
- ClawHub 分类和话题本轮不调整，按用户最后指令留到下一版本单独处理。

## 剩余边界

- 本轮没有新增三宿主在线生命周期样本；超长收束沿用 v1.6.8 的 Claude Code 在线 D1，并已按本轮机械门重放通过。Codex、CodeBuddy 的静态 companion 不冒充当次在线成功。
- `AH-001` 共享硬锚抽取及 ClawHub 分类/话题整理继续作为后续研究项。
