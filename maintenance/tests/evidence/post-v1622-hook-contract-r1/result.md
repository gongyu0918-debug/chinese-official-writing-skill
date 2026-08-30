# v1.6.22 后 Hook 契约与 Stop 预算原子结果

日期：2026-08-31。

## 结论

`UL-006-CONTRACT-R1` 与 `HK-009-STOP-BUDGET-R1` 已在 `codex/post-v1622-hook-contract-r1` 完成目标反例、最小实现、独立冷审和工程回归，状态为 `ENGINEERING_VERIFIED_NEXT_VERSION_CANDIDATE / NOT_MERGED`。固定基线是 `main@62ba9e8206e5b11f08a8f28ebdfe95b08e30ccfe`；本候选未修改版本号，未合入 `main`，未创建或移动 tag，未推送或发布。

这两个原子不新增写稿文种或放宽事实边界。事故通报无显式下限入口已经有五家20稿和联合留出的既有真实写稿证据；本轮只把 README、manifest 与实际运行时统一，并删除已经终止且不可达的情况说明/办理通知旧代码。Stop 原子只改变超时、选择恢复和失败清理，不改变写稿提示、verifier 口径、能力路由或正常 D0/D1 状态机，因此没有用新的大模型稿件替代工程生命周期验证。

## 固定反例与修正

1. 固定基线能复现 under-length README/manifest 只声明显式下限、运行时却已有事故隐式入口的契约漂移；情况说明和办理通知旧正则与指导语不可达。候选统一为仅 `incident_bulletin`，并明确情况说明、办理通知和会议纪要不启用隐式入口。
2. 原实现的 review-gate 子进程可以在同一 Stop 中分别取得20秒，异常路径的静态累计会超过宿主30秒。候选为一次 `handle_stop` 建立25秒共享预算，单调用仍不超过20秒，下一次独立 Stop 重新取得预算。
3. R1 冷审复现 `emit` 失败后的两处候选风险：进程内调用带 stdout 副作用的 emit 会形成“正文+JSON”；已选 D1 无法恢复时可能静默回 D0。候选改为纯选择解析，只有可信 `TERMINAL_D0 / selected=D0 / hash匹配` 才恢复；D1 证据损坏停止自动交付并脱敏。
4. R2 冷审通过真实 `handle_stop` 复现“预算已耗尽、非终态达到最大尝试次数但仍留存 request/txn/inputs”。候选统一记 `failed_bounded`、`delivery_verified=false` 并精确删除当前 turn 原文与事务，宿主保持既有 fail-open 返回形状。

## 改动范围

- 产品：`hooks/capabilities/under_length/README.md`、`runtime.py`、`hooks/host-capabilities.json`、`hooks/core/gate_stop_hook.py`、`scripts/review_gate.py`。
- 直接测试：`test_under_length_capability.py`、`test_gate_stop_hook.py`、`test_host_gate_adapter.py`、`test_hook_layer_contract.py`。
- 规格与证据：requirements、coverage、roadmap、待办、evidence 索引及本目录。
- 不变：版本坐标、公开 README、普通写稿 references、description、宿主30秒 manifest、正常能力选择、ClawHub 无 Hook 包边界和付费分支。

## 实际验证

固定反例先失败、最小修正后通过；中间直接回归依次得到3/3、5/5、332/332、20/20、275/275。独立冷审另跑101/101，并发现后续已修正的“预算耗尽仍留存原始事务”问题。

最终命令与结果：

```text
python -B -m unittest maintenance.tests.test_gate_stop_hook maintenance.tests.test_host_gate_adapter maintenance.tests.test_under_length_capability maintenance.tests.test_hook_layer_contract
Ran 102 tests in 55.078s；OK

python -B -m unittest maintenance.tests.test_status_ledger_consistency
Ran 12 tests in 0.014s；OK

python -B -m unittest discover -s maintenance/tests -p 'test_*.py'
----------------------------------------------------------------------
Ran 756 tests in 123.930s

OK

python -B maintenance/tools/sync_adapters.py
PASS；再次检查无新增镜像差异

python -B -c "import ast,json,pathlib; ..."
PASS；3个变更Python文件可解析，host-capabilities.json可解析

git diff --check
PASS
```

host adapter 测试通过实际 `main()` 的 stdin/stdout 路径执行 emit 失败恢复，完整 stdout 可一次解析为单一 JSON 对象；预算与脱敏测试通过真实 `handle_stop` 入口执行，不以只测 helper 代替生命周期。

## 提交与边界

- `d37068a7`：预登记及固定失败测试。
- `d5faa6ff`：登记 R1 可信恢复修正。
- `18751371`：同步事故隐式入口契约。
- `15eaa7eb`：实现共享 Stop 预算和可信恢复。
- `bfeb56c2`：登记 R2 失败清理修正。
- `d0235670`：实现预算耗尽后的精确脱敏。

剩余风险只有当前候选未在真实在线宿主上人为制造20秒级慢子进程；这种注入会扩大外部运行成本，本轮以真实 adapter 入口、模拟单调时钟和九宿主组装契约覆盖。候选尚未合入 `main`，下一步由用户决定是否作为 v1.6.22 之后的小版本增量合并；无需保留 `HOLD`。
