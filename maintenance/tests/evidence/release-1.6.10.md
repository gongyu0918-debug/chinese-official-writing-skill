# v1.6.10 发布记录

日期：2026-08-19

## 发布范围与提交

- 发布产品提交：`af12b771e376e815c44d53b08d26c635805586b3`。
- 上一正式产品 tag：`v1.6.9^{commit}=5047c224456183d97dd46cb5be09506bfdcfd0b8`。
- 本轮按用户明确授权发布 GitHub、SkillHub.cn 与 ClawHub `1.6.10`；Red SkillHub 及其他平台未操作。
- 三个平台均使用公开非付费版；付费提纲能力 `outline_assist` 未进入源码 tag、SkillHub 包或 ClawHub 包。
- ClawHub 使用33文件无 Hook 包；可选 Hook 只进入 GitHub canonical 与 SkillHub 清洁包。

## 主要变化

- 完善标题与正文边界：主标题去除句末句号并与正文留空行，编号正文仍保留必要句号。
- 收束未决状态引出的材料外程序，减少重复规则和解释性负担。
- 篇幅不足、超长收束 Hook 共享引用、数字、字段和归属关系保护。
- 精简会议纪要、函件和通用文种叶中重复的使用说明。

## 发布前验证

- 直接相关测试最终183/183通过。首次运行有2项旧字符串断言失败，均指向已压缩的 reference 或 AGENTS 历史长句；更新测试契约后复跑通过。
- 全量单元测试首次为630/632，失败原因同为上述旧断言；修正后先复跑3/3，再取得最终632/632通过回执。
- canonical、Agent Skills、Qwen Code、Hermes 通过通用 quick validation。OpenClaw 因平台专用 `category` 字段不符合通用 validator 的字段集合，改用专用包边界、ClawHub dry-run 和远端逐文件哈希验证，不把通用 validator 结果写成通过。
- `sync_adapters.py` 幂等，版本面、`git diff --check` 和最终工作树检查通过。
- SkillHub 清洁包61文件，LF 规范化内容哈希为 `762f4d6aee3381d99a02f70add845b1868a40f11ef61f5cf62877919a9df4224`。
- ClawHub 无 Hook 包33文件，同口径哈希为 `c7daa752bcd0fc43d0f91c15097ae1a86cd68ffefbec38bc8c4510b8a56981f4`；Hook、交付门禁、`agents/openai.yaml` 和付费提纲文件命中数均为0。
- 两包许可证 SHA-256 均为 `ead35e40076582d7053fb0908588adb878ff5108601a76647b9f5626b3a0d5f8`，与根 MIT `LICENSE` 一致。

## GitHub 回执

- 发行时远端 `main`：`af12b771e376e815c44d53b08d26c635805586b3`。
- annotated tag object：`9916497ba2b6368453f97662845ce8f02b798013`；`v1.6.10^{commit}`：`af12b771e376e815c44d53b08d26c635805586b3`。
- GitHub Release：[`v1.6.10`](https://github.com/gongyu0918-debug/chinese-official-writing-skill/releases/tag/v1.6.10)，`id=RE_kwDOSXovUM4WOL-2`、`draft=false`、`prerelease=false`、`published_at=2026-08-19T05:42:37Z`。
- 本发布证据在 tag 之后单独推进 `main`，不移动已发布 tag。

## SkillHub.cn 回执与传播状态

- 正式提交一次：`ok=true`、`skillId=70149`、`versionId=245586`、`fileCount=61`、平台 fingerprint `e3c3a194e2fa8aeb625603b62e55762f1a5372ca35510bf58d436a02680c7a2c`。
- `latest`、`ai-compute`、`chinese`、`content-creation`、`gongwen`、`office-efficiency`、`official-document`、`writing` tags 均已指向 `1.6.10`；公开版本计数为73。
- 上传回执的 `reviewStatus`、`securityScanStatus`、`contentAuditStatus` 均为 `pending`。提交后只读复核时 `latestVersion` 仍为1.6.9，1.6.10精确版本签名返回404；属于平台异步传播，不重复上传。

## ClawHub 回执与传播状态

- 正式提交返回 `ok=true`、`status=published`、`versionId=k970rw8byt4ct7h1455swjhv998csvve`、`fileCount=33`、fingerprint `cc519248b1279a8f49681522a089f2ff19269abb8cdef542f7ed83971ddedd77`。
- 展示名为“中文公文写作”；分类提交为 `productivity,knowledge`，话题为 `chinese-writing,official-writing,office-productivity,content-creation`。
- 公开 `latestVersion`、`tags.latest` 和精确版本均为1.6.10；moderation verdict 为 `clean`，平台 LLM 扫描为 clean。
- 远端33个文件逐项与本地发布包比较：缺失0、哈希不一致0、多余0；远端文件清单不含 Hook。
- 第一次正式命令因 PowerShell 未引用逗号列表，将分类拼接为无效 slug `productivity knowledge`，平台在创建版本前拒绝。确认1.6.10仍不存在后，使用带引号的分类与话题列表重试一次成功，没有产生重复版本。
- ClawHub 页面按平台统一规则显示 MIT-0；GitHub 仓库和上传包内 `LICENSE` 使用根 MIT 许可证。

## 剩余边界

- 本轮没有重新跑 Codex、CodeBuddy/WorkBuddy 在线 Hook 生命周期；共享硬锚的真实修订和静态组装证据已闭环，宿主协议没有变化。
- SkillHub.cn 的公开 latest、精确签名和本版本审核、安全、内容状态仍待异步传播；只读复核，不重复上传。
- 付费提纲能力继续只保存在 `codex/paid-outline-review`，未进入本次三个公开发行面。
