# v1.6.4 发布记录

日期：2026-08-14

## 发布范围与提交

- 发布产品提交：`a737791c8ed6fbae82e4a72fb3931e901faafc07`。
- 上一正式产品 tag：`v1.6.3^{commit}=f23d5697d973043d03ef3ea05b5741d5abcec42f`。
- 本版发布 GitHub `main`、annotated tag `v1.6.4`、GitHub Release 和 SkillHub.cn `1.6.4`。
- 用户先明确要求 GitHub 与 ClawHub；ClawHub CLI 在随后“只上传 SkillHub”纠正到达前返回过正回执。纠正后停止写入；应用户指出页面没有内容，只做一次精确版本只读核验，结果为 `Version not found`，因此本版不计为 ClawHub 已发布。
- 小红书 Red SkillHub 及其他平台未上传。

## 主要变化

- 普通写作收束材料外免责说明、下游未发生事项、无来源具体化和同义状态复述，短稿优先保留已给事实与当前状态。
- 新闻稿件明确事实、合理推断、责任主体和状态强度的边界。
- GitHub 可选 Hook 增加保护性外扩精确删除能力，默认关闭，只删除冻结目标片段，异常时保留原稿。
- Hook 永久移除使用 `hooks/README.md` 语义接引、用户二次确认和宿主原生文件编辑能力。
- 篇幅不足 Hook 没有进入本版能力声明；其生命周期证据与未完成的 D1 质量门继续保留在待办。

## 真实写稿与发布前验证

- 三家 DeepSeek V4 Flash 完成六份真实写稿；事实边界均通过，四份稀薄材料稿仍未达到用户篇幅下限。结果见 [`v164-real-writing-final/result.md`](v164-real-writing-final/result.md)。
- 同一初稿的保护性外扩功能包经独立 SOL max 校准，29/29 通过。
- 全量维护单测首次运行时，572项通过、1项因信息选择规则已收紧而仍锁定旧文案；只更新该测试断言后，最终573/573通过。
- Promptfoo stub smoke：20/20 PASS，run `eval-Bnv-2026-08-14T02:14:54`。
- 版本与包边界聚焦测试：89/89 PASS；canonical quick validate：PASS；`sync_adapters.py` 复跑无漂移；`git diff --check`：PASS。

## GitHub 回执

- 远端 `main`：`a737791c8ed6fbae82e4a72fb3931e901faafc07`。
- annotated tag object：`dd7d33963fc03982a7c2662c55806c9bf576f97a`；`v1.6.4^{commit}`：`a737791c8ed6fbae82e4a72fb3931e901faafc07`。
- GitHub Release：[`v1.6.4`](https://github.com/gongyu0918-debug/chinese-official-writing-skill/releases/tag/v1.6.4)，`id=370311306`、`draft=false`、`prerelease=false`、`published_at=2026-08-14T02:20:26Z`。

## SkillHub.cn 回执与传播状态

- 清洁包51文件，排除 `agents/openai.yaml` 和无扩展名 `LICENSE`，另带根 MIT 全文的 `LICENSE.md`。
- 本地逐文件清单 SHA-256：`0ab689dc4f822ba15fe8707c3bfc0c913ca93897a4ba5b7c762e1cb2d291417e`。
- 正式提交一次：`ok=true`、`skillId=70149`、`versionId=235645`、`fileCount=51`、平台 fingerprint `785260e85ac792cc56d5dcc41f9138602ad19b6dab0935da3ea71137f9540bea`。
- `latest`、`ai-compute`、`chinese`、`content-creation`、`gongwen`、`office-efficiency`、`official-document`、`writing` tags 均指向 `1.6.4`。
- 上传回执的 `reviewStatus`、`securityScanStatus`、`contentAuditStatus` 均为 `pending`。上传后即时只读查询时，公开 `latestVersion` 仍为 `1.6.3`，1.6.4签名端点返回404；没有重复上传。最终复查时公开 `latestVersion` 与 tags.latest 均为 `1.6.4`，1.6.4签名端点返回 HTTP 200，公开传播和版本签名已闭环；审核状态仍按原回执记为 pending。

## ClawHub 异常回执与未发布状态

- 在用户纠正发布范围前，ClawHub CLI 返回 `status=published`、`versionId=k971eyat4kc83hejvc2ztxqw1h8cep5t`、31文件、fingerprint `ea580c6af1ab089c40552d22ec9ac01850bb5a4e517c735ed10dbe9ef3d52d65`。
- 该包为 `packages/openclaw/skills/chinese_official_writing` 的无 Hook 兼容包；本地逐文件清单 SHA-256 为 `c07ddb35c887791b2cf5ce01547e67148c766a4e9a389e897002c2d1042e047a`。
- 用户随后明确“ClawHub不上传，只上传SkillHub”；收到纠正后未再执行 ClawHub 写入。
- 用户报告页面没有任何1.6.4内容后，唯一一次只读命令 `clawhub inspect chinese-official-writing --version 1.6.4 --json` 返回 `Version not found`。正回执没有形成可读取版本，故不把它记为已上传或已发布，也不重试。
- 用户随后明确授权使用 `delete` 撤回误提交版本；精确命令 `clawhub delete chinese-official-writing --version 1.6.4 --yes` 返回 `This skill version is already unavailable and cannot be deleted.`。命令没有删除整个 Skill，也没有改动既有1.6.0；1.6.4保持不可用，不再重试。

## 下一轮必须继续

- 先对3—5份真实短初稿直接验证篇幅修订提示，至少取得一份安全、自然、达到用户下限且可直接交付的 D1。
- 有合格 D1 后，仅由独立 SOL max 审同一 D0/D1 增量；随后再接回单一 coordinator，做 Codex、Claude Code 少量真实在线 Hook 生命周期和 CodeBuddy 迁移核验。
- 继续复测 Hook 显式关闭、纯审稿、起草和改写路由，关闭时不得创建事务、阻断或替换终稿。
