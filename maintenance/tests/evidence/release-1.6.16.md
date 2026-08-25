# v1.6.16 发布记录

日期：2026-08-25

## 发布范围与提交

- 发布产品提交：`f6293aaaa4095530b386b50e3a56c07e35206af5`。
- 上一正式产品 tag：`v1.6.15^{commit}=762b84d49c35cb956ce464fa8aab5dd08f1ad113`。
- 本轮按用户明确授权发布 GitHub、SkillHub.cn 与 ClawHub `1.6.16`；小红书 Red SkillHub 及其他平台未操作。
- 三个平台均使用公开非付费版；付费提纲、阶段 Hook 和红头 DOCX 能力未进入公开 tag 或平台包。
- ClawHub 使用33文件无 Hook 普通包；GitHub canonical 与 SkillHub.cn 清洁包保留默认关闭的可选 Hook。

## 主要变化

- 发布已在 main 清洁验证的 `OC-003`：算力可研审稿允许核算已给数据、说明缺项影响并提出一层条件性研究或风险控制建议，同时保留未决状态和程序边界。
- 点名完整性审稿收敛在入口与可研细查叶，覆盖成本比较、技术指标、验收主体和依据四项，不新增程序模板、固定段长、自动测算门、数值阈值门或新 Hook。
- `WR-014-R5`、短稿与长稿后续研究只回填状态，不冒充本版产品增量；付费分支不反向进入公开版。

## 发布前验证

- 聚焦边界、包构建、状态台账、仓库可达性和 `OC-003` 分层测试97/97通过；全量 unittest 693/693通过。
- 固定 v1.6.15/current 的确定性真实用户 prompt 消融分别111/111、111/111，无起草或改稿路由回退。
- Promptfoo 本地 stub smoke 20/20通过，Skill 10胜、baseline 0胜、平票0、无效0、judge consistency 1.0；该项只作发布烟测，不冒充真实模型写稿。
- canonical、Agent Skills、Qwen Code、Hermes 四套 quick validation 均通过；135个 tracked Python 文件内存编译、141个 tracked JSON 文件解析通过。
- 镜像同步复跑 diff hash 不变；发布后 main 定向测试97/97和 canonical quick validation通过。

## 候选包

- SkillHub.cn 正式上传包71文件，本地文件树指纹 `debc7c4b04bbe7bd8470558786f78f75d9f109be9e775335832a2e928557ce40`；排除无扩展名 `LICENSE` 与 `agents/openai.yaml`，保留默认关闭的可选 Hook。
- ClawHub 正式上传目录33文件，本地文件树指纹 `05b70f740cd57261c69d9d0ee3abeb4a5230008fa00695e52833c1de029d628e`；Hook、`agents/openai.yaml`、付费提纲和红头实现路径命中均为0。
- 本地指纹算法按相对 POSIX 路径排序，对每个文件依次写入 `path + NUL + bytes + NUL` 后计算 SHA-256。Windows 检出换行会改变字节指纹，平台正式回执指纹另列，不混用。

## GitHub 回执

- 远端 `main`：`f6293aaaa4095530b386b50e3a56c07e35206af5`。
- annotated tag object：`915fbe6ad84d6aa77acfdbe25845c1fb8d1b87d3`；`v1.6.16^{commit}`：`f6293aaaa4095530b386b50e3a56c07e35206af5`。
- GitHub Release：[`v1.6.16`](https://github.com/gongyu0918-debug/chinese-official-writing-skill/releases/tag/v1.6.16)，`databaseId=376165800`、`id=RE_kwDOSXovUM4Wa9Wo`、`draft=false`、`prerelease=false`、`published_at=2026-08-25T05:33:36Z`。
- `main` 与 annotated tag 已原子推送；GitHub Release 创建一次成功。

## SkillHub.cn 回执与传播状态

- 正式提交一次：`ok=true`、`skillId=70149`、`versionId=268275`、`fileCount=71`、平台 fingerprint `39610babbe772d926010cb3a26467deedeb240c8e820c5639fdddadddb3d1c74`。
- slug 为 `chinese-official-writing`，公开坐标为 `@user_f3d82da7/chinese-official-writing`，展示名为“中文公文写作”。
- 上传回执中 `latest`、`ai-compute`、`chinese`、`content-creation`、`gongwen`、`office-efficiency`、`official-document`、`writing` tags 均指向 `1.6.16`；`reviewStatus`、`securityScanStatus`、`contentAuditStatus` 为 `pending`。
- 首次只读搜索仍显示公开 version `1.6.15`；后续同一公开坐标已传播为 `1.6.16`，slug、展示名和 description 保持正确。期间未重复上传；上传回执中的三项审核状态仍按 `pending` 记录。

## ClawHub 回执与传播状态

- owner `gongyu0918-debug`、slug `chinese-official-writing`、展示名“中文公文写作”、分类 `productivity,knowledge`、话题 `chinese-writing,official-writing,office-productivity,content-creation` 保持不变。
- 最终 dry-run 绑定产品提交并返回 `would-publish`、33文件；正式提交一次返回 `status=published`、`versionId=k975dt3tbjff63946s65sdr3798d5cmw`、`fileCount=33`、平台 fingerprint `2ddfe14f6508820187dc3720a475bafabe8d9c632691c73ed99fdfadbbd745f5`。
- 正式回执中的 `latestVersion` 仍是提交前的1.6.15；首次只读 history 也尚未出现1.6.16，精确版本路由返回 `No matching routes found`。后续 latest、tags.latest、version history 和精确版本均已传播为1.6.16，期间未重复提交。
- 精确版本回读为33文件，与正式上传目录比较缺失0、额外0、哈希不一致0、Hook路径0；aggregate security 为 `clean`，LLM scanner 为 `benign/high`，安全包 SHA-256 为 `ccb8d90dbf0cecab8fba92f4aefc1a569954d4ddb7a892df40b5d8303b094c89`。VT 子扫描仍显示 `stale/pending`，不把 aggregate clean 外推为所有子扫描均已完成。

## 剩余边界

- GitHub、SkillHub.cn 公开 latest、ClawHub latest/精确版本和33文件边界已闭环；SkillHub.cn 上传回执中的审核、安全扫描与内容审核仍为 `pending`，ClawHub VT 子扫描仍为 `stale/pending`。
- Hook 默认关闭并按单能力窄启用；ClawHub 包继续完全不含 Hook。
- 付费提纲和红头 DOCX 能力继续只在独立分支管理，不发布、不反向合入公开 `main`。
