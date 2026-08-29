# v1.6.20 发布记录

日期：2026-08-29。

## 发布范围与提交

- 发布产品提交：`2fc9d1d4baf8b5b74009d6ac28cf92135881a5c8`；上一正式产品 tag：`v1.6.19^{commit}=eef65336d5dfd5a09434f7ca6bed6e01975b37fb`。
- 本轮按用户明确授权发布 GitHub、SkillHub.cn 与 ClawHub `1.6.20`；小红书 Red SkillHub、付费分支及其他平台未操作。
- GitHub 与 SkillHub.cn 新增 `AH-002` 来源绑定的新闻完整日期写后修复，并将 Hook README 的安装、使用和适配说明前移、彻底删除说明后移。canonical `SKILL.md`、description 与全部公开 references 相对 v1.6.19 不变。
- 四个 references 减载原子的五路190次真实任务及终态一并归档，但被拒绝的产品候选均已恢复，不以研究字节冒充产品收益。
- ClawHub 只同步版本坐标，继续使用33文件无 Hook 普通包；正文规则与v1.6.19逐字相同。

## 发布门与候选包

- 全量 unittest 734/734通过；发布定向回归最终150/150通过，交付前最终状态/边界/链接检查15/15通过；固定 v1.6.19/current 确定性消融均为111/111，双方 create/revise failure 为0。
- Promptfoo 0.122.2 本地 stub smoke 20/20通过；canonical、Agent Skills、Qwen Code、Hermes 四套 quick validation 均通过；149个 tracked Python 文件内存编译、147个 tracked JSON 文件解析通过；镜像同步复跑 diff hash 不变。
- `AH-002` 的真实依据为三 provider 九次 Claude Code 生命周期：3次精确修复、3次目标稿自然正确、3次控制逐字不变；Alibaba Token Plan 2 与 OpenCode Go 达到预登记门。完整结果见 [`ah002-news-date-completeness-r1/live-result.md`](ah002-news-date-completeness-r1/live-result.md)。
- SkillHub.cn 正式上传包82文件，本地文件树指纹 `77424ba02234474f8d57fc2b9f5062851f779de5967a1f64d149f8c674365b8d`；含 `LICENSE.md`，不含 `agents/openai.yaml` 或付费实现路径。留存 zip SHA-256 为 `7dc66a44fe2697d1378ca3911e8c58b4ac026cf9128e40a7d4451f18903a2add`。
- ClawHub 正式上传目录33文件，本地文件树指纹 `39d2e7b093bcc8001c58444965332bab6e06fccdf41feac9c9b85cb2b3d8f392`；Hook路径、Hook内容、`agents/openai.yaml`、付费提纲和红头实现路径命中均为0。结构与绑定最终产品提交的 source-bound dry-run 均返回平台 fingerprint `1386bf0fb02bf836d7f00f5eaed48e351d152442992a0876f41195b4d84d8d24`。

## GitHub 回执

- 远端 `main` 与 `v1.6.20^{commit}` 在产品发布时均为 `2fc9d1d4baf8b5b74009d6ac28cf92135881a5c8`；annotated tag object 为 `cd9faa12034e23275b2d007468ff0fa129451837`。
- GitHub Release：<https://github.com/gongyu0918-debug/chinese-official-writing-skill/releases/tag/v1.6.20>，`databaseId=378908920`、`draft=false`、`prerelease=false`、`publishedAt=2026-08-29T07:27:51Z`。
- `main` 与 annotated tag 原子推送；GitHub Release 创建一次成功。

## SkillHub.cn 回执

- slug `chinese-official-writing`、公开坐标 `@user_f3d82da7/chinese-official-writing`、展示名“中文公文写作”保持不变。
- 正式提交一次：`ok=true`、`skillId=70149`、`versionId=275458`、`fileCount=82`、平台 fingerprint `1467c4b2abf79fe4f5a571fb8ed51697b3b614ac36e46cfdb25a464370cd94f8`；八个既有 tags 含 `latest` 均在提交回执中指向1.6.20。
- 提交回执中的 `reviewStatus`、`securityScanStatus`、`contentAuditStatus` 均为 `pending`。两次初始只读搜索仍显示1.6.19，精确1.6.20签名入口返回“找不到该版本”；期间未重复提交。后续公开搜索已显示精确坐标、中文展示名和1.6.20；留存正式 zip 对平台签名验证 `content_hash_match=true`，content hash 为 `6672323c52810cdd56fe7701ad1adc11fb22147c9c8bfd831bc5f21f39fe5ffd`。公开传播与签名匹配不改写上传回执中的三项pending。

## ClawHub 回执

- owner `gongyu0918-debug`、slug `chinese-official-writing`、展示名“中文公文写作”、分类 `productivity,knowledge`、话题 `chinese-writing,official-writing,office-productivity,content-creation` 保持不变。
- 首次正式调用因 PowerShell 未给逗号列表加引号，被服务端在写入前拒绝为未知分类 `productivity knowledge`；未创建版本。修正为显式引号后只成功提交一次，回执为 `status=published`、`versionId=k97df79ant8tkx5yp85fcjj2ad8ddnwf`、`fileCount=33`、平台 fingerprint `1386bf0fb02bf836d7f00f5eaed48e351d152442992a0876f41195b4d84d8d24`。
- 后续 `latestVersion`、`tags.latest` 与精确版本均为1.6.20；版本列表前五项为1.6.20—1.6.16。精确远端33文件与本地比较：缺失0、额外0、SHA-256不一致0。首次精确回读为 `status=clean`、`hasWarnings=false`；后续异步子扫描更新后总体仍为 `clean`，但 `hasWarnings=true`：VirusTotal 为 `stale/pending`，Skillspector 为 `suspicious`、`MEDIUM`、score 29、issueCount 1，LLM 扫描为 `clean/benign/high`。平台未返回该 Skillspector issue 的具体明细，不把总体clean外推为所有子扫描完成或无警告。

## 剩余边界

- GitHub、SkillHub.cn 与 ClawHub 已公开到1.6.20；SkillHub 精确签名匹配，ClawHub 精确33文件、逐文件哈希和总体 `clean` 状态均已闭环。
- ClawHub 的异步子扫描仍有 `hasWarnings=true`：VirusTotal stale/pending，Skillspector 给出未附明细的 MEDIUM/Caution 单项警告；LLM 扫描为 benign。该警告不触发重复上传，后续只能只读观察或取得平台明细后再判断。
- SkillHub.cn 上传回执中的三项审核/扫描仍为pending，不重复上传；平台后续状态不能由本回执预判。
- `AH-002` 只覆盖默认 `delivery_review` 中唯一完整来源日期与唯一目标新闻文种；多日期、非新闻、歧义材料、其他 capability 和所有宿主不外推。ClawHub 包完全不含 Hook。
- 付费提纲和红头 DOCX 能力继续只在独立分支管理，未发布、未反向合入公开 `main`。
