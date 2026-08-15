# v1.6.5 发布记录

日期：2026-08-15

## 发布范围与提交

- 发布产品提交：`81061bd78c0dbf5604fb2927ba275169fc93f5ed`。
- 上一正式产品 tag：`v1.6.4^{commit}=a737791c8ed6fbae82e4a72fb3931e901faafc07`。
- 本版发布 GitHub `main`、annotated tag `v1.6.5`、GitHub Release 和 SkillHub.cn `1.6.5`。
- ClawHub、Red SkillHub 及其他平台未上传；本轮未执行 ClawHub 上传、更新或删除命令。

## 主要变化

- 新增篇幅不足、交付洁净度、重复句与高相似复述三项可选 Hook。
- 修复 Skill 与材料并行读取时激活状态可能被覆盖的问题，使已启用能力能继续进入对应生命周期。
- 继续采用静态兼容、显式启用和单能力互斥；普通 Skill 与关闭 Hook 路径保持独立闭环。

## 真实写稿与发布前验证

- 三条指定 DeepSeek V4 Flash 路线已先完成真实写稿验证；相关同稿修订、SOL max 复核与在线生命周期结果见本版候选记录及其链接证据。
- 修复并行读取竞态后的 Codex 真实调用中，`skill_seen=true` 且篇幅事务正常创建；候选新增材料外数量后由既有数字门安全选择 D0，没有据此收紧语义门。
- 发布级全量回归：`python -B -m unittest discover -s maintenance/tests -p "test_*.py" -q`，602/602 PASS。
- SkillHub 清洁包重新构建为56文件，禁入项0；`git diff --check` 与候选工作树清洁检查通过。

## GitHub 回执

- 远端 `main`：`81061bd78c0dbf5604fb2927ba275169fc93f5ed`。
- annotated tag object：`cdbd5820419186c27be10b60e2a036d1bdeb9984`；`v1.6.5^{commit}`：`81061bd78c0dbf5604fb2927ba275169fc93f5ed`。
- GitHub Release：[`v1.6.5`](https://github.com/gongyu0918-debug/chinese-official-writing-skill/releases/tag/v1.6.5)，`id=370940432`、`draft=false`、`prerelease=false`、`published_at=2026-08-15T02:58:48Z`。

## SkillHub.cn 回执与传播状态

- 最终清洁包路径：`output/release-candidates/v1.6.5-release-final/skillhub-package/`；共56文件，排除 `agents/openai.yaml` 和无扩展名 `LICENSE`，另带根 MIT 全文的 `LICENSE.md`。
- 本地逐文件清单 SHA-256：`456b378f678b0eebdc9eda4f3f68ce41a322a0871d200e1e8302379d20c4e36e`。
- dry-run 返回 `dryRun=true`、slug `chinese-official-writing`、version `1.6.5`。
- 正式提交一次：`ok=true`、`skillId=70149`、`versionId=237846`、`fileCount=56`、平台 fingerprint `e35d395ebc07e3a4a447d14d06d76bbf8a969881d993b6326ee38d28f262bebc`。
- `latest`、`ai-compute`、`chinese`、`content-creation`、`gongwen`、`office-efficiency`、`official-document`、`writing` tags 均已指向 `1.6.5`。
- 上传回执的 `reviewStatus`、`securityScanStatus`、`contentAuditStatus` 均为 `pending`。上传后即时只读查询时，公开 `latestVersion` 仍为 `1.6.4`，1.6.5 签名端点返回404；这是平台异步传播状态，没有重复上传。

## 剩余事项

- 等待 SkillHub 公开 `latestVersion`、精确版本签名及审核、安全、内容状态异步更新；只读复核，不重复提交。
- CodeBuddy/WorkBuddy 仍缺本机可用客户端或登录入口；本版仅报告静态兼容验证，不把它写成在线生命周期成功。

