# v1.6.21 发布记录

日期：2026-08-30。

## 发布范围与提交

- 发布产品提交：`8086ff255f04df8b080ef1a0488236295bf2cb8d`；上一正式产品 tag：`v1.6.20^{commit}=2fc9d1d4baf8b5b74009d6ac28cf92135881a5c8`。
- 本轮按用户明确授权发布 GitHub、SkillHub.cn 与 ClawHub `1.6.21`；小红书 Red SkillHub、付费分支、Pro Hook、红头 DOCX、`UL-006` 动态字数下限及其他研究候选未操作。
- 相对 v1.6.20 的公开产品增量为 `UL-005-R10` 篇幅不足修订口径与 QwenWork 34文件无 Hook 静态 Skill 包。canonical `SKILL.md` 和公开 references 相对 v1.6.20 没有本轮新增修改；QwenWork 不声明未被官方生命周期证明的 Hook。
- `UL-006` 候选 `389b43f4` 及当日后续 `short-natural-reference-r1`、`ul006-*`、`wr018-*`、付费同步分支均不是发布提交祖先。ClawHub 继续只发布33文件无 Hook 普通包。

## 发布门与候选包

- 发行 worktree `codex/release-v1.6.21` 在发布前固定并保持干净，`main@c60e3ffaa12af012bf2a3910081ae70244a87a21` 与远端发布前 `main@6e4e8914431c5674a3fda87ab42d35ed8a531e8c` 均为发布提交祖先。
- 发布定向回归本次复跑为123/123通过；发布前全量 unittest 为737/737通过，耗时95.531秒，回执状态文档更新后又复跑状态/边界/链接95/95与全量737/737，后者耗时94.873秒。候选冻结记录分别为122/122和736/736；本次多出的既有契约测试均通过，失败数仍为0，不回写历史计数。
- Promptfoo 0.121.11 本地 stub smoke 20/20通过，Skill 10胜、baseline 0胜、平票0、无效0、judge consistency 1.0；固定 v1.6.20/current 确定性消融均为111/111，双方 create/revise failure 均为0。两项均不调用真实写稿模型。
- canonical、Agent Skills、QwenWork、Qwen Code、Hermes 五套 quick validation 均通过；161个 tracked Python 文件完成内存编译，158个 tracked JSON 文件解析通过。首次把 Windows `NUL` 作为 `.pyc` 目标的补充命令因目标不是普通文件而失效，随后改用内存 `compile()` 原样重跑通过，不把失效命令记为产品失败或通过。
- `sync_adapters.py` 复跑前后 tracked diff 均为空对象；活动 Markdown 链接7/7、`git diff --check`、工作树状态与版本边界均通过。
- SkillHub.cn 正式包82文件，本地规范化文件树指纹 `39816269d78bed354d16a52f64b789ae7e9e4c80c33cfc53a0f2ebe7caf6668e`；留存 zip SHA-256 为 `c34acff6661672e23f66f6c376b27f72d81cf84199835621a2b8e28d56f1edbb`。包内 slug `chinese-official-writing`、展示名“中文公文写作”、版本 `1.6.21`，含 `LICENSE.md`，不含 `LICENSE`、`agents/openai.yaml`、付费实现或私密路径。
- ClawHub 正式目录33文件，本地规范化文件树指纹 `69e312eb9f0f3f5b71b3a2923cb658be37905b89c0c3b35f2c7db2dd9d0b1285`；Hook路径、Hook内容、`agents/openai.yaml`、付费提纲和红头实现路径命中均为0。绑定 source commit 的 dry-run 返回 `would-publish`、33文件和平台 fingerprint `559d5d2727bbbd74dd3c91ad7f7d5e96031da92b99c05e2cb4c70e63c4a6a5d6`。

## GitHub 回执

- 远端 `main` 与 `v1.6.21^{commit}` 在产品发布时均为 `8086ff255f04df8b080ef1a0488236295bf2cb8d`；annotated tag object 为 `211fbe7429d15e7fbbe73e178b86d8ca37c5193a`。
- 首次 `git push --atomic` 在 TLS 握手阶段失败；随后用 GitHub API 只读确认远端 `main` 仍为 `6e4e8914` 且 `v1.6.21` 不存在，再以同一原子 ref 集合、OpenSSL backend 重试成功。没有非原子更新、force push 或 tag 移动。
- GitHub Release：<https://github.com/gongyu0918-debug/chinese-official-writing-skill/releases/tag/v1.6.21>，`databaseId=379147885`、`draft=false`、`prerelease=false`、`publishedAt=2026-08-30T01:13:12Z`。

## SkillHub.cn 回执

- slug `chinese-official-writing`、`skillId=70149`、公开坐标 `@user_f3d82da7/chinese-official-writing`、展示名“中文公文写作”保持不变。
- 正式提交一次成功：`ok=true`、`versionId=276070`、`fileCount=82`、平台 fingerprint `9841d5082d11af04c6c9dd0abe679b63b4ed5ed91ac79cf841e41556a373a9df`；八个既有 tags 含 `latest` 均在提交回执中指向1.6.21。
- 提交回执中的 `reviewStatus`、`securityScanStatus`、`contentAuditStatus` 均为 `pending`。首次只读公开搜索仍显示1.6.20，精确1.6.21签名入口返回“找不到该版本”；期间未重复提交，当前记为 `ACCEPTED / PUBLIC_PROPAGATION_PENDING`。

## ClawHub 回执

- owner `gongyu0918-debug`、slug `chinese-official-writing`、展示名“中文公文写作”、分类 `productivity,knowledge`、话题 `chinese-writing,official-writing,office-productivity,content-creation` 保持不变；分类与话题逗号列表均以单一带引号参数传递。
- 正式提交一次成功：`status=published`、`versionId=k97asahr8jx0qbvqeny6jrp3m18dftt1`、`fileCount=33`、平台 fingerprint `559d5d2727bbbd74dd3c91ad7f7d5e96031da92b99c05e2cb4c70e63c4a6a5d6`。
- 提交回执中的 `latestVersion` 仍为1.6.20；首次精确1.6.21只读检查返回 `Version not found`，当时记为 `PUBLISHED_RECEIPT / PUBLIC_INDEX_PENDING`。后续只读复核确认公开 `latestVersion=1.6.21`，精确版本33文件与本地包逐项 SHA-256 一致，Hook仍为0，moderation 与版本级 security 均为 `clean`；VirusTotal 子扫描仍为pending，Skillspector与LLM子扫描为clean。期间未重复上传。

## 剩余边界

- GitHub 产品提交、annotated tag 和 Release 已闭环；后续发布证据提交只推进 `main`，不得移动产品 tag。
- SkillHub.cn 与 ClawHub 已各成功提交一次。ClawHub 公开latest、精确33文件哈希和总体clean已闭环；SkillHub.cn公开搜索、精确签名与三项审核仍在异步传播。成功回执不等于审核通过，不重复上传。
- `UL-005-R10` 的真实稿使用五条低成本 Codex CLI 路线，宿主协议未变化且未在本候选重跑所有在线生命周期；不外推为每个模型都必须扩写成功。
- QwenWork 只证明官方布局、静态无 Hook 包和包路径真实写稿，不代表在线触发或 Hook 生命周期已验证。ClawHub 包完全不含 Hook。
- 付费提纲、Pro Hook、红头 DOCX 与 `UL-006` 动态字数研究继续留在授权外的独立分支或研究状态，未反向进入本版。
