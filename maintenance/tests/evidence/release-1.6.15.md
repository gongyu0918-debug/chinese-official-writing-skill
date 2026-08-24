# v1.6.15 发布记录

日期：2026-08-24

## 发布范围与提交

- 发布产品提交：`762b84d49c35cb956ce464fa8aab5dd08f1ad113`。
- 上一正式产品 tag：`v1.6.14^{commit}=b0e5d5c43849b082dd023ba72101689b3eacd0b3`。
- 本轮按用户明确授权发布 GitHub、SkillHub.cn 与 ClawHub `1.6.15`；小红书 Red SkillHub 及其他平台未操作。
- 三个平台均使用公开非付费版；付费提纲能力、胶水、测试和详细规格未进入产品 tag、SkillHub 包或 ClawHub 包。
- ClawHub 使用33文件无 Hook 包；可选 Hook 进入 GitHub canonical 与 SkillHub.cn 清洁包。

## 主要变化

- 新增 ZCode、Qwen Code、Kimi Code CLI 独立 Hook adapter；Qwen 覆盖多 Stop，Kimi 如实保留宿主单 Stop 边界，ZCode 使用社区 wrapper runtime 接入 D0/hash 生命周期。
- description 只把“实施细则”原子合并为“细则”，204字降至202字；两轮五 provider 共50次正式发文意图路由均为5/5触发、0/5误触发。
- 纳入已在 main 清洁验证的 `HK-008b`、`WR-014-R4`、`WR-019c/019d`；`WR-020b1` 与付费提纲未进入公开版。
- 发布证据中的本机绝对路径已脱敏，证据 runner 改用 `Path.home()` 获取用户目录。

## 发布前验证

- 合并后定向测试96/96、版本与包体定向测试99/99、全量 unittest 684/684通过。
- canonical、Agent Skills、Qwen Code、Hermes 四套 quick validation 均通过。
- 固定 v1.6.14/current 的确定性消融分别110/111、111/111；旧 tag 唯一失败是没有本轮新增的 adapter assembly contract，当前候选0失败。
- Promptfoo 本地 stub smoke 20/20通过，Skill 10胜、baseline 0胜、judge consistency 1.0。
- 同步幂等、128个 tracked Python 文件内存编译、137个 tracked JSON 文件解析、61个脱敏 runtime JSON 复解析、路径扫描和 `git diff --check`通过。
- 发布后直接相关定向测试99/99、canonical quick validation、两包禁入内容扫描通过。

## 候选包

- SkillHub.cn 清洁包71文件，本地规范化文件树指纹 `ef7635f955422aadfeaf28bef06cf770e6a82df207b87c1e1c2e07ab5452899b`；包含默认关闭的可选 Hook，不含 `agents/openai.yaml`、付费提纲或本机绝对路径。
- ClawHub 无 Hook 包33文件，本地规范化文件树指纹 `b2fc77dcba8421337bbde7f13104cc864ba61bef5556dac17b84e4daba2dd87c`；Hook、`agents/openai.yaml` 和付费提纲禁入路径均为0。
- ClawHub 最终 dry-run 返回33文件、平台 fingerprint `f20de481091a81905190c84c992e694bd5f875033b6fde2a643df0e62a0f4f1f`，并绑定产品提交 `762b84d49c35cb956ce464fa8aab5dd08f1ad113`。

## GitHub 回执

- 远端 `main`：`762b84d49c35cb956ce464fa8aab5dd08f1ad113`。
- annotated tag object：`bbdf09d70045898051baa376eae31ebd57722b54`；`v1.6.15^{commit}`：`762b84d49c35cb956ce464fa8aab5dd08f1ad113`。
- GitHub Release：[`v1.6.15`](https://github.com/gongyu0918-debug/chinese-official-writing-skill/releases/tag/v1.6.15)，`databaseId=375402850`、`id=RE_kwDOSXovUM4WYDFi`、`draft=false`、`prerelease=false`、`published_at=2026-08-24T02:31:04Z`。
- `main` 与 annotated tag 已原子推送；GitHub Release 创建一次成功。

## SkillHub.cn 回执与传播状态

- 正式提交一次：`ok=true`、`skillId=70149`、`versionId=265765`、`fileCount=71`、平台 fingerprint `538e45d2cb66a06acf72175a9b1d66fee83f5b3caf2de1075e6a9f5e8187e3f6`。
- slug 为 `chinese-official-writing`，公开坐标为 `@user_f3d82da7/chinese-official-writing`，展示名为“中文公文写作”。
- 上传回执中 `latest`、`ai-compute`、`chinese`、`content-creation`、`gongwen`、`office-efficiency`、`official-document`、`writing` tags 均指向 `1.6.15`；`reviewStatus`、`securityScanStatus`、`contentAuditStatus` 仍为 `pending`。
- 精确1.6.15签名已生成：`key_id=skillhub-platform-v1`，签名内容 hash `ae8e9a789e2c71aa9440666a0cd1afc57eb694421786a7f1083237778d3f2495`；正式上传所用71文件目录完成本地验签与内容匹配。
- 首次只读搜索复核中，description 已更新但搜索结果的 version 字段仍为1.6.14；未重复上传。后续搜索结果已切换为1.6.15，并保留“管理办法、细则、操作规程”的原子描述。由 `main` 工作树重新构建的包受 Windows 检出换行影响，内容 hash 与正式上传原包不同；发布指纹以正式上传原包及签名为准。

## ClawHub 回执与传播状态

- owner `gongyu0918-debug`、slug `chinese-official-writing`、展示名“中文公文写作”、分类 `productivity,knowledge`、话题 `chinese-writing,official-writing,office-productivity,content-creation` 保持不变。
- 第一次正式命令因 PowerShell 将未加引号的分类逗号解析为空格而在上传前拒绝。修正引号后的正式请求无即时标准输出，后续同版本请求明确返回“Version 1.6.15 already exists”；没有再提交新版本。
- 精确版本回读确认 `latestVersion=1.6.15`、`tags.latest=1.6.15`、version history 首项为1.6.15，moderation 与 security 均为 `clean`。
- 公开精确版本为33文件；与正式上传目录逐项比较，缺失0、额外0、哈希不一致0、Hook 路径0。平台安全包 SHA-256 为 `80eb888960cb41f367b181db3883cfde6d153d201825be4be6f654c3c87d0cfa`。

## 剩余边界

- GitHub、SkillHub.cn 与 ClawHub 的公开 latest 和精确版本均已闭环；SkillHub.cn 上传回执中的审核、安全扫描和内容审核仍保持 `pending`。
- Hook 默认关闭并按单能力窄启用。Kimi Code CLI 当前只证明宿主允许的一次 Stop；Qwen 和 ZCode 的宿主协议变化仍需后续真实生命周期回归。
- 付费提纲继续只在独立分支管理，不发布、不反向合入公开 `main`。
