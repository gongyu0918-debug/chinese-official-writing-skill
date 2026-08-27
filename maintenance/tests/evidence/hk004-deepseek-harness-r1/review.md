# HK-004 DeepSeek Harness R1 基线复核

复核范围为固定基线 `3c363257fee2e823f96253682331ef4ec5128fb7..91786e5ecdd8f375d1e01155a41a8a144a240681`，在第五次候选提交前完成。

- ancestry：固定基线是候选祖先。
- baseline diff：20个文件，新增896行、删除11行；范围只含 DeepSeek Harness adapter/Bundle、共享 Hook 说明与能力台账、组装器、测试和证据。
- 轻量消融：`chinese-official-writing/SKILL.md`、全部 `references/` 和 `packages/` 相对基线零差异，故普通写稿语义、description 和无 Hook 市场包不受本候选影响。
- Qoder：候选路径和实现/测试 diff 中没有 Qoder 代码或配置；仅维护状态说明保留 `DEFERRED_BY_USER`。先前旧预登记已由 DSH-only 预登记取代。
- Git：候选 worktree clean；本地 `main` 仍为 `3c363257`、工作树 clean，`origin/main` 为 `c784e372`，本轮未合并、推送、打 tag 或发布。
- 回归：全量 unittest 723/723、Skill Creator quick validate、真实最终 DSH Profile Bundle 安装与 W3 三 Stop 闭环均在该产品提交之后完成；未发现候选独有的普通写稿或其他宿主回退。

首轮 PowerShell 命令把 `$base..HEAD` 写成未加边界的变量表达式，`git diff` 只打印 usage；该次不计复核。随后使用 `$range="${base}..HEAD"` 重跑，得到上述实际结果。
