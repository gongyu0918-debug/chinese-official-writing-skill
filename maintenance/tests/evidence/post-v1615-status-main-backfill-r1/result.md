# v1.6.15 后状态回填 main 结果

日期：2026-08-24。

## 结论

`PASS_MAINTENANCE_ONLY_MAIN_CANDIDATE / NO_PRODUCT_OR_PAID_SOURCE`。

固定基线为 `main=origin/main@8aab5e61e65c0411b4bd6580173c2a107986fdcb`。本候选把 WR-020b1/b2、v1.6.15 发布、OC-003 登记、国产 CLI adapter、description 两字原子、HK-008b、WR-014-R4、WR-019c/019d 和本地付费候选的真实状态回填到轻量规格、待办和证据索引。

旧 HOLD 不再作为无人处理的中间状态：具体失败候选记 `REJECTED`，多轮失败实现方向记 `TERMINATED`，当前基线已覆盖且只等待新真实失败的目标记 `WAIT_NEW_COUNTEREXAMPLE`。`HOLD` 只保留给仍有明确下一原子的活动候选。

## 关键校准

- `WR-020b1` 任务卡候选为 REJECTED；`WR-020b2a/b2b/b2c` 已由当前产品完成搬移、删除和只审定位，状态为 `B1_REJECTED / B2_DONE / WAIT_NEW_COUNTEREXAMPLE`。Ollama b2b 删除正确但正文包装失败，风险没有被抹去。
- `OC-003` 已登记到 requirements、coverage、roadmap、待办和 evidence。重新裁定确认候选减少了真实状态升级，但上一轮又把条件性可研建议判得过严，当前为 `ACCEPTED_RESEARCH_CANDIDATE / MINIMAL_SCOPE_REPAIR_REQUIRED`，不写成 REJECTED 或可直接合并。
- `HK-004`、`MT-005b6b`、`HK-008b`、`WR-014-R4`、`WR-019c/019d` 均回填为已随 v1.6.15 发布。
- `codex/paid-outline-review@8f1d31fe6feb839f02611f21192a45563865a8c3` 仍以当前 main 为祖先且 clean，已收敛 OT-001、OT-001-composite、OT-002 与 RF-001；公开规格只记录边界和状态，不带实现源码。

## 精确范围

相对固定 main 的38个差异路径全部位于 `maintenance/`。明确排除 OC-003 的4个 canonical reference 候选及其四套普通镜像，共20个产品路径；公开 Skill、description、Hook、adapter、版本和付费源码差异为0。

带入的证据目录为：

- `wr020b1-speech-task-card/`；
- `post-v1615-backlog-recovery-r1/`；
- `v1615-like-signal-short-writing-r1/`；
- `wr001-date-r1/`。

## 验证

- 非维护路径检查：`TOTAL=38`，`NON_MAINT=0`。
- `git diff --check HEAD`：通过。
- `python -m unittest maintenance.tests.test_status_ledger_consistency maintenance.tests.test_repository_reachability maintenance.tests.test_skill_boundary`：91/91通过。
- `python -B C:\Users\admin\.codex\skills\.system\skill-creator\scripts\quick_validate.py chinese-official-writing`：通过，输出 `Skill is valid!`。
- 付费分支祖先检查：`git merge-base --is-ancestor 8aab5e61 8f1d31fe` 退出0；付费 worktree clean。

本候选不修改、推送或发布平台版本；是否进入本地 main 与后续真实写稿、OC-003 最小修复分开处理。
