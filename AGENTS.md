# 项目协作

本文件是活动规则入口。产品规则只放 `chinese-official-writing/SKILL.md` 及 `references/`；按需查[规格](maintenance/specs/README.md)、[发布证据](maintenance/docs/evidence/README.md)，历史归档不作为新要求。

## 工作方式

- 修改代码/规则、设计验证、合并或发布前，按[开发细则](maintenance/docs/development-workflow.md)核对基线、授权、工作树和验证范围。代码/文档均提交；功能、大改、研究、基线和发布用独立 worktree。复杂任务交子代理，主代理复核。
- 写作/Hook 先做最小原型并验证真实稿件/生命周期，以准确、自然、完整、可直接使用决定保留；失败先修产品，成功再补工程，不用更多量表或门禁替代质量。
- Markdown 按需选读，已读未变不重复整篇加载；长日志/历史先检索，回传结论与路径。无新改动、失败或未决问题不重复验证；全量门原则上合并/发布前只跑一次。

## 边界

- 当次未明确授权，不合 main、推送、移动 tag、创建 Release、上传/删除平台版本；外部写入不超授权。禁止破坏性 reset、force push、无边界清理；删除须核准路径、工作树干净、成果可恢复。禁止提交密钥、登录态、私有地址和未脱敏数据。
- canonical 的 `hooks/core/` 为唯一核心，`hooks/adapters/` 为静态适配；`packages/` 放公开包，`maintenance/` 放维护证据，`output/` 默认不提交。
- main 不含付费提纲 Hook、胶水、测试和详细规格；付费分支保持 main 加付费增量，按[同步规则](maintenance/specs/public-paid-sync.md)接收公开变更，提纲不得反流；付费发布另行授权。

## 本机真实使用

仅保留完整 Pro 安装，内含 MIT main HEAD 的普通写稿能力及 Pro 增强。开工核对安装指纹；MIT main 或 Pro 已提交版本推进后，按[本机同步](maintenance/docs/local-codex-skill.md)更新并核验，未变则跳过。此本地更新已获授权，无需重复询问，不含推送/发布；旧安装先备份到扫描目录外再移除。

## 交付

简报含摘要、branch、commit、实际测试命令/结果、量化变化、未完成和风险。未运行不写通过；安装、启用、信任、真实执行分别举证，保留失败、回退及 verifier 分歧。写作平实，UI 简洁。
