# HK-009 R2 预算耗尽清理修正

日期：2026-08-31。

固定基线与原子边界继续以 [`preregister.md`](preregister.md) 为准；stdout 与选择恢复修正见 [`r1-amendment.md`](r1-amendment.md)。本修正来自 R1 实现后的独立只读复审，不修改 25 秒 Stop 总预算、20 秒单子进程上限、能力路由或写稿语义。

## 新发现的候选风险

当事务仍处于 `AWAITING_REPAIR` 或未知非终态、`stop_attempts` 已达到上限，而共享 Stop 预算已经耗尽时，`_abort()` 不再启动子进程并返回 `None`。候选当前直接 `_allow()`，未把记录标为 `failed_bounded`，也未清理当前 request、txn 和输入快照。

## 最小修正与验收

1. 先通过真实 `handle_stop` 入口构造“已过期 deadline + `AWAITING_REPAIR` + 最大尝试次数”，确认当前候选仍保留原始 request/txn。
2. abort 无法形成可信终态时，统一记录有限失败、将 `delivery_verified` 置为 false，并立即清理精确当前 turn 的 request、txn 和输入快照；保留既有 fail-open 返回形状。
3. 同一清理 helper 覆盖未知状态的最大尝试分支；已有 terminal D0/D1 选择、emit 恢复和正常 Stop 状态机保持不变。
4. 修正后复跑预算、选择恢复、脱敏、adapter stdout 与九宿主直接相关回归；若清理不完整或影响正常 D0/D1 交付，则终止本候选。
