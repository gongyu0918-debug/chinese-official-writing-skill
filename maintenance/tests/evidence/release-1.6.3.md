# v1.6.3 发布记录

日期：2026-08-13

## 发布范围

- 本版发布 GitHub `main`、annotated tag `v1.6.3`、GitHub Release 和 skillhub.cn `1.6.3`。
- ClawHub、小红书 Red SkillHub 及其他平台不在本次授权范围内，未执行其上传或发布。
- 发布产品提交：`f23d5697d973043d03ef3ea05b5741d5abcec42f`；上一正式 tag 解引用提交为 `v1.6.2^{commit}=7d794b10f7acd320c90c2d311af9466fca732cfe`。

## 主要变化

- 已启用的可选 Hook 识别“只审不改”“仅审不改”“只检查不修改正文”等纯审稿短语，并直接旁路，不创建 transaction；审后改写、起草和材料引用反例仍走原门禁。
- SkillHub 清洁包的专用 summary/tags 补充 `office-efficiency`、`content-creation`；canonical 与其他平台包不新增平台专用字段。
- Codex、Claude Code、WorkBuddy/CodeBuddy companion 与纯 Skill 镜像同步为 1.6.3；GitHub 内 OpenClaw 兼容包同步，但不代表 ClawHub 已发布。

## 发布前验证

- 全量 unittest：551/551 PASS。
- Promptfoo stub smoke：20/20 PASS，run `eval-MA6-2026-08-13T08:34:44`。
- 固定 v1.6.2 确定性消融：v1.6.2 为 111/111，v1.6.3 为 111/111。
- canonical `quick_validate.py`：PASS；`sync_adapters.py` 复跑无差异；`git diff --check`：PASS。
- SkillHub 清洁包：48 文件，许可证为 `LICENSE.md`；不含 `agents/openai.yaml` 与无扩展名 `LICENSE`。本地逐文件清单 SHA-256 为 `02277e6ae6aca7a8b19891a8a7c4f459b7c2fb18807eb0f302f4d9d8f608a99a`。

## 已排除内容

- 新闻普通语义候选真实 A/B 为 HOLD：17 个有效对中候选 8 胜、基线 9 胜，并有候选独有硬失败。
- 保护性/编辑性 Hook、篇幅 Hook 与其他未闭环适用性研究未进入本版；不以工程可运行或单项能力验证替代其准入门。

## GitHub 回执

- 远端 `main` 回读为 `f23d5697d973043d03ef3ea05b5741d5abcec42f`。
- annotated tag object：`cebd80454736f24ce2ad89069177e31ebdc25bc7`；`v1.6.3^{commit}` 解引用为 `f23d5697d973043d03ef3ea05b5741d5abcec42f`。tag 为未签名 annotated tag，GitHub API `verification.reason=unsigned`。
- GitHub Release：[`v1.6.3`](https://github.com/gongyu0918-debug/chinese-official-writing-skill/releases/tag/v1.6.3)，`id=369772074`、`draft=false`、`prerelease=false`、`published_at=2026-08-13T08:37:12Z`，目标提交为发布产品提交。

## SkillHub.cn 回执与公开状态

- 正式提交只执行一次：`ok=true`、`skillId=70149`、`versionId=234415`、`fileCount=48`、平台 fingerprint `399c0c13c1aa1794cc0f7c0e448a88634a25134592081a48c468060e93af7e26`。
- `latest` 与 `ai-compute`、`chinese`、`content-creation`、`gongwen`、`office-efficiency`、`official-document`、`writing` tags 均指向 `1.6.3`。
- 提交回执的 `reviewStatus`、`securityScanStatus` 与 `contentAuditStatus` 均为 `pending`。发布后立即只读查询时，公开 `latestVersion` 仍为 `1.6.2`，属于索引传播滞后；不重复提交。公开详情当前 category 为 `office-efficiency`、subCategory 为 `office-doc`，不能据此把 `content-creation` tag 表述为平台分类已生效。
- 平台 fingerprint 与本地逐文件清单 SHA-256 使用不同计算口径，分别记录，不互相替代。

## 过程异常与边界

- GitHub Release 首次经 CLI GraphQL 创建时遇到网络连接失败，命令返回 `release not found`，没有创建 Release；清理当前进程代理变量后通过 GitHub REST API 创建一次并回读。
- tag push 期间的一次 `fetch --tags` 出现短暂网络失败；tag push 随后成功，远端 tag object 与解引用 commit 均已回读确认。
- 本版未宣称 Hook 改善整体写稿质量，也未宣称 SkillHub 审核、安全扫描、内容审核或公开索引已经完成。
