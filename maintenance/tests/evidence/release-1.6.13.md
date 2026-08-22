# v1.6.13 发布记录

日期：2026-08-22

## 发布范围与提交

- 发布产品提交：`c4ea80a6146a2c672fdec8aeb8de13ed547f33f9`。
- 上一正式产品 tag：`v1.6.12^{commit}=ae4a25b497fab1ccdd621ffbf21e43501701f8b9`。
- 本轮按用户明确授权发布 GitHub、SkillHub.cn 与 ClawHub `1.6.13`；小红书 Red SkillHub 及其他平台未操作。
- 三个平台均使用公开非付费版；`codex/paid-outline-review` 的提纲能力、胶水、测试和详细规格未进入产品 tag、SkillHub 包或 ClawHub 包。
- ClawHub 使用33文件无 Hook 包；可选 Hook 只进入 GitHub canonical 与 SkillHub.cn 清洁包。

## 主要变化

- `WR-013`：允许材料和常识支持的一层合理原因、即时作用和发布者角色表达，不把预期影响冒充已取得成效。
- `WR-011`：区分来源名称/载体、来源身份、原始出处、来源冲突和限定来源结论。
- `UL-005`：篇幅扩写的 verifier 使用单稿事实台账和同一事实 span 角色绑定，拒绝无关 span、跨 span 拼接和新增谓语。
- 联网来源用途：国家规范、本地执行和外省比较不混用；补搜围绕已识别缺口，并把元数据与 URL 绑定实际打开页。

## 发布前验证

- 版本边界、SkillHub 包构建和 UL-005 直接相关定向测试首次104/105；唯一失败是 README 最近证据列表漏掉上一正式发布记录。只调整该列表后复跑105/105通过。
- 全量 unittest 655/655通过；canonical、Agent Skills、Qwen Code、Hermes 四套 quick validation 均通过。
- 固定 v1.6.12/current 的确定性消融分别110/111、111/111；当前候选0失败。
- `sync_adapters.py` 二次执行未改变候选 diff；Markdown 链接检查和 `git diff --check`通过。
- SkillHub.cn 清洁包61文件，本地规范化文件树指纹 `4de24c3e635ff05df2cb9b1572970a51dd51e19fee1014aa10647da8fde42097`。
- ClawHub 无 Hook 包33文件，本地规范化文件树指纹 `02b1900e9e6c5357d8e5cee3b7af6514dd7a6e7a6e02ea547ff4ea258990fd71`；Hook、交付门禁、`agents/openai.yaml` 和付费提纲文件命中数均为0。

## GitHub 回执

- 首次发布推送后远端 `main`：`c4ea80a6146a2c672fdec8aeb8de13ed547f33f9`。
- annotated tag object：`38f9baa4f6d854e62d6f176fefc4421b0ba404c1`；`v1.6.13^{commit}`：`c4ea80a6146a2c672fdec8aeb8de13ed547f33f9`。
- GitHub Release：[`v1.6.13`](https://github.com/gongyu0918-debug/chinese-official-writing-skill/releases/tag/v1.6.13)，`id=374853158`、`node_id=RE_kwDOSXovUM4WV84m`、`draft=false`、`prerelease=false`、`published_at=2026-08-22T06:40:58Z`。
- 本发布证据在 tag 之后单独推进 `main`，不移动已发布 tag。

## SkillHub.cn 回执与传播状态

- 正式提交一次：`ok=true`、`skillId=70149`、`versionId=261633`、`fileCount=61`、平台 fingerprint `e04621819e2d0fd5d5b603f304c2cce3a98cc47b1728d669fd758dd9d9bb14ce`。
- slug 为 `chinese-official-writing`，公开坐标为 `@user_f3d82da7/chinese-official-writing`，展示名为“中文公文写作”。
- `latest`、`ai-compute`、`chinese`、`content-creation`、`gongwen`、`office-efficiency`、`official-document`、`writing` tags 均已指向 `1.6.13`。
- 上传回执的 `reviewStatus`、`securityScanStatus`、`contentAuditStatus` 均为 `pending`。提交后的首次只读复核中，公开 tags 已更新，`latestVersion` 与版本列表仍停在1.6.12；未重复上传。
- 后续只读复核中，公开搜索、详情 `latestVersion` 与 `tags.latest` 均已切换为1.6.13；精确1.6.13签名已生成，绑定 `versionId=261633`，签名内容 hash 为 `8f3ab1642fcb3ffc936692e3674902fe45c3c45a78fd3ea06ba10a8b3552ca87`。公开报告接口仍为空，不据此把提交回执中的三项 `pending` 改写为已审核通过。

## ClawHub 回执与传播状态

- 正式提交一次：`ok=true`、`status=published`、`versionId=k977jefykss9wtgyg4xxndr0558cyrv5`、`fileCount=33`、fingerprint `f39454f4577efb5d11980573569de4e77b2b670f1fcd850489ce8e5b747bd662`。
- slug 为 `chinese-official-writing`，展示名为“中文公文写作”；分类保持 `productivity,knowledge`，话题保持 `chinese-writing,official-writing,office-productivity,content-creation`。
- 正式回执与最终 dry-run 的33文件 fingerprint 完全一致；上传目录为发行 worktree 中的无 Hook OpenClaw 包。
- 提交后的首次只读复核仍返回 `latestVersion=1.6.12`，精确1.6.13返回 `Version not found`；未重复上传。随后公开 `latestVersion`、`tags.latest` 和版本列表均已切换为1.6.13，精确版本 moderation 为 `clean`。
- 首次公开文件复核时，远端33个源文件逐项与正式上传所用发行 worktree 比较：缺失0、哈希不一致0、多余0。后续平台生成 `skill-card.md` 后，公开文件面为34项；排除该平台生成卡片，33个源文件再次逐项比较仍为缺失0、哈希不一致0、多余0。上传源文件及当前公开文件中的 Hook、交付门禁、`agents/openai.yaml` 和付费提纲文件命中数均为0。

## 剩余边界

- SkillHub.cn 的公开 latest 与精确版本签名已闭环，提交回执中的审核、安全扫描和内容审核仍保持 `pending`；不因内部状态未公开而重复发布。ClawHub 的 latest、精确版本、文件清单和 moderation 已闭环。
- 付费提纲仍不发布；`OT-002` 提纲修正和结构化组合 Stop 生命周期继续在 `codex/paid-outline-review` 原子化验证。
