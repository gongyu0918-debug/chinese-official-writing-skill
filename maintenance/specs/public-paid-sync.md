# 公开主线与付费提纲候选同步

## 边界

- 公开主线：`main`。不包含提纲审核 Hook、宿主胶水、测试、结果包和详细实现规格。
- 付费候选：`codex/paid-outline-review`。它必须以当前 `main` 为祖先，只在其上增加提纲审核能力。
- 红头 DOCX 只允许在独立付费实验通过后进入付费候选，不反向进入公开 `main`。
- 普通 Skill 语义、references、共享 Hook、宿主兼容修复和安全修复默认先进入 `main`，再同步到付费候选。
- 提纲增量不得反向合入 `main`，也不得进入公开 GitHub、SkillHub、ClawHub 或 OpenClaw 包。

## 更新顺序

1. 先在 `main` 完成真实写稿优先的公开改动和最小验证。
2. 在付费 worktree 合并最新 `main`；冲突时，普通语义和共享能力以 `main` 为准，提纲专属路径保留付费实现。
3. 核对 `main` 是付费分支祖先；付费分支相对 `main` 的产品差异只能落在批准的提纲能力、付费说明和对应测试/evidence。
4. 先跑提纲能力的少量真实写稿与真实生命周期，确认公开改动没有破坏提纲冻结和终稿核对；通过后才补必要胶水回归。
5. 付费分支不自动发布。版本、包名、平台和许可证按当次授权另行确定。

## 差异 allowlist

付费候选当前允许新增：

- `chinese-official-writing/hooks/capabilities/outline_assist/`
- `chinese-official-writing/paid/redhead_docx/`
- `chinese-official-writing/SKILL.md` 中仅用于显式红头/套红请求的付费窄路由
- 提纲 companion 所需的 `hooks/README.md`、`hooks/host-capabilities.json` 和组装器窄增量
- 对应的定向测试、真实 evidence 和付费候选规格，包括红头结构审计、逐页渲染和公开投影剔除

除此之外的产品差异应优先回到 `main`，避免公开版与付费版形成两套普通写作规则。

## 最小检查

- `main` 必须是付费分支祖先。
- 公开 `main` 的 tracked tree 中 `outline_assist` 文件数必须为0。
- 公开 `main` 的 tracked tree 中 `paid/redhead_docx` 文件数必须为0，且不含付费红头路由。
- 付费候选必须保留提纲能力文件、三宿主组装和已验证生命周期。
- 两个 worktree 均须 clean；未取得授权不得 push、tag 或发布。
