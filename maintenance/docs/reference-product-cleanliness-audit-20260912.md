# Skill 产品面清洁审计（2026-09-12）

审计范围是 canonical `chinese-official-writing/SKILL.md` 与 `references/*.md`；构建、同步、测试和发布命令留在 `maintenance/`，不进入用户可读 Skill。

自动审计命令：`python maintenance/tools/audit_product_surface.py`。

当前规则：

- 首页 description 只承担能力触发，不写交付模式、文种读取顺序或路由实现。
- 用户面没有 `git commit`、`git push`、pytest、unittest、worktree、maintenance 路径、构建命令、开发命令、宿主适配或运行时实现约束。
- `prose-lint-usage.md` 中的脚本参数属于用户明确选择的草稿检查能力；`delivery-review-gate.md` 中的 `review_gate.py` 命令属于用户选择 Hook 增强能力，二者不是 Skill 构建或维护命令。
- 维护、测试、镜像同步和发布规范只存在于 `maintenance/`、AGENTS.md 或发布工具，不由正文写作路由加载。
