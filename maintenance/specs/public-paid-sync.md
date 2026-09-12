# 普通 Skill 与 Pro 同步

## 产品与许可边界

- 普通主线 `main` 保留写稿入口、references、篇幅检查、文稿复核等普通脚本及兼容包。本轮候选通过验收合并后，全部 Hook、交付门禁、宿主适配及对应活动构建链退出 MIT 主线。
- Hook 资产保存在 `codex/pro-hooks-preserved-20260912`；来源、验证范围与后续接续事项见 [Hook 去向便条](../docs/pro-hooks-next.md)。原 `codex/paid-outline-review` 是既有付费候选，后续 Pro 不再限于提纲增量。
- Pro 专属范围包括 Hook 核心、宿主适配、交付门禁、提纲审核、已授权的红头 DOCX 能力，以及对应说明、构建工具、测试和证据。它们不进入公开 GitHub 主线或普通 SkillHub、ClawHub、OpenClaw 包。
- 普通写稿规则、references、普通脚本和公开兼容修复仍以 MIT 主线为来源，避免维护两套普通规则。
- 既往已发布的 MIT 副本保留原许可。Hook 的 MIT 发布截止到上一已发布版本 v1.6.34；后续 Hook 更新作为 Pro 专属内容，采用版权所有协议（All rights reserved），并保留所复用旧代码和第三方代码适用的原版权与许可声明。

## 接续顺序

1. 普通候选完成真实写稿与相关脚本验证，按授权合入 `main`。
2. 获得 Pro 接续授权后，在独立 Pro worktree 对照 MIT 来源提交、Hook 保存提交和 Pro 自身改动，列出同步路径。
3. 同步普通规则和脚本，保留 Pro Hook 及其构建链；逐项审查 MIT 移除 Hook 的删除记录，避免直接合并时覆盖 Pro 资产。可以采用有审查的合并或路径级同步，记录来源提交与差异。
4. 检查普通写稿与 MIT 来源的一致性，核对批准的 Pro 差异；测试同稿开关效果、终稿核对和受影响宿主的真实生命周期。
5. Pro 激活、版本、包名、平台、许可文件和发布按当次授权执行。本轮仅保留便条，不发送到 Pro 任务、不激活、不发布。

## 最小检查

- 普通产品与兼容包均不含 `hooks/`、`scripts/review_gate.py`、`references/delivery-review-gate.md` 或付费红头路由。
- 普通篇幅检查与 `prose_lint.py` 均保留，按写作阶段调用；移除 Hook 不构成删除普通脚本的理由。
- Pro 相对所记录 MIT 来源的普通能力差异可解释，Hook 资产、适配器和已验证特性完整。
- 每次接续记录准确来源与最小测试，不以 Git ancestry 单独替代内容一致性检查。
- 提交后核对 worktree 状态；未经授权不推送、移动 tag 或发布。
