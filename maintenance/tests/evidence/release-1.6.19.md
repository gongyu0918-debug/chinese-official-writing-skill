# v1.6.19 发布记录

日期：2026-08-28。

## 发布范围与提交

- 发布产品提交：`eef65336d5dfd5a09434f7ca6bed6e01975b37fb`；上一正式产品 tag：`v1.6.18^{commit}=67a68257f8a79220a38e961ced932bcb022cf86b`。
- 本轮按用户明确授权发布 GitHub、SkillHub.cn 与 ClawHub `1.6.19`；小红书 Red SkillHub、付费分支及其他平台未操作。
- GitHub 与 SkillHub.cn 新增已验证的 Hermes Agent 0.20.5—0.20.6 新建且不可恢复单题 adapter、DeepSeek Harness 0.1.1-rc.2 Windows headless 原生 Profile Bundle、共享 core、组装/测试及工程记录；公开写作规则、description 和 references 相对 v1.6.18 不变。
- ClawHub 只同步版本坐标，继续使用33文件无 Hook 普通包；正文规则与v1.6.18逐字相同。

## 发布门与候选包

- 全量 unittest 723/723通过；发布定向回归最终122/122通过，交付前最终状态/边界/链接检查94/94通过；固定 v1.6.18/current 确定性消融分别110/111、111/111，当前 create/revise failure 为0。上一版唯一失败是当前工程用例要求新增 adapter 组装，不解释为旧版写作质量失败。
- Promptfoo 本地 stub smoke 20/20通过；canonical、Agent Skills、Qwen Code、Hermes 四套 quick validation 均通过；143个 tracked Python 文件内存编译、143个 tracked JSON 文件解析通过；镜像同步复跑 diff hash 不变。
- SkillHub.cn 正式上传包81文件，本地文件树指纹 `1d36f23e7b4f2bc2a2b0a61b665926899c41b94293f93164d9bdd70b5f934ed9`；含 `LICENSE.md`，不含 `agents/openai.yaml` 或付费实现路径。留存 zip SHA-256 为 `d2129a9bbf38c0d10733a8d1bf61c25b0651e98c1b0cdec8ec086cc512dbd05f`。
- ClawHub 正式上传目录33文件，本地文件树指纹 `829d4b06f1cf59f131bdd0cafe34724443aeecbfa6a4060c174da7a80b374a47`；Hook路径、Hook内容、`agents/openai.yaml`、付费提纲和红头实现路径命中均为0。结构与 source-bound dry-run 均返回平台 fingerprint `5fd17d00ab30a0fe214833be64b93470eabd68a48df4dd506eae8f06707888dc`。

## GitHub 回执

- 远端 `main` 与 `v1.6.19^{commit}` 在产品发布时均为 `eef65336d5dfd5a09434f7ca6bed6e01975b37fb`；annotated tag object 为 `9577852bb9c13c2ae9834ed2f708df3116f4f47a`。
- GitHub Release：<https://github.com/gongyu0918-debug/chinese-official-writing-skill/releases/tag/v1.6.19>，`databaseId=378257496`、`draft=false`、`prerelease=false`、`publishedAt=2026-08-28T04:17:50Z`。
- `main` 与 annotated tag 原子推送；GitHub Release 创建一次成功。

## SkillHub.cn 回执

- slug `chinese-official-writing`、公开坐标 `@user_f3d82da7/chinese-official-writing`、展示名“中文公文写作”保持不变。
- 正式提交一次：`ok=true`、`skillId=70149`、`versionId=274063`、`fileCount=81`、平台 fingerprint `345977b16acfbf785ea5bb769a6f86adcb1a7099cc0e144a9991ed3f477af80e`；八个既有 tags 含 `latest` 均在提交回执中指向1.6.19。
- 两次初始只读搜索仍显示1.6.18，精确1.6.19签名入口返回“找不到该版本”；期间未重复提交。后续公开搜索已显示精确坐标、中文展示名和1.6.19；留存正式 zip 对平台签名验证 `content_hash_match=true`，content hash 为 `52bbeee8772238ebeda1ba378cea8ee64dc13b59145a65dcbc0f590b55d47a77`。上传回执中的 `reviewStatus`、`securityScanStatus`、`contentAuditStatus` 均为 `pending`，不改写为审核完成。

## ClawHub 回执

- owner `gongyu0918-debug`、slug `chinese-official-writing`、展示名“中文公文写作”、分类 `productivity,knowledge`、话题 `chinese-writing,official-writing,office-productivity,content-creation` 保持不变。
- ClawHub CLI 0.23.1 正式提交一次：`status=published`、`versionId=k978k7j6050bhb6ynrgxw8z9jx8dak9v`、`fileCount=33`、平台提交 fingerprint `7bc40baf599f27969ec122f6686365064650c04fe1e05293dd177961814c4d13`。首次回执的 `latestVersion` 仍为1.6.18，期间未重复提交。
- 后续 `latestVersion`、`tags.latest` 与精确版本均为1.6.19。精确远端33文件与本地比较：缺失0、额外0、SHA-256不一致0、Hook路径0；总体安全状态为 `clean`。版本级 `hasWarnings=true` 与 VirusTotal stale/pending 同时出现，不把总体clean外推为所有异步扫描已完成。

## 剩余边界

- GitHub、SkillHub.cn 与 ClawHub 公开版本均已到1.6.19；SkillHub 精确签名匹配，ClawHub 精确33文件、哈希和总体安全状态已闭环。
- SkillHub.cn 上传回执中的三项审核/扫描仍为pending，不重复上传；平台后续状态不能由本回执预判。
- Hermes adapter 只支持新建且不可恢复的单题；DeepSeek Harness adapter 只支持已验证的 Windows headless `delivery_review`。ClawHub 包完全不含 Hook。
- 付费提纲和红头 DOCX 能力继续只在独立分支管理，未发布、未反向合入公开 `main`。
