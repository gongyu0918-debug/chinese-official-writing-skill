# v1.6.22 后 Hook 契约与 Stop 预算原子预登记

日期：2026-08-31。

固定基线：`main@62ba9e8206e5b11f08a8f28ebdfe95b08e30ccfe`。工作分支：`codex/post-v1622-hook-contract-r1`。本分支是下一版本候选，不反向改写 v1.6.22 本地基线，不修改版本号，不创建 tag，不推送或发布。

## 已确认问题

### UL-006-CONTRACT-R1

- `under_length/README.md` 与 `host-capabilities.json` 仍只声明显式下限入口，但运行时已经真实验证并接入阶段性事故通报的无显式下限入口。
- 运行时模块注释仍称“三种文种”；情况说明和办理通知的两个识别正则及两段隐式指导语已不可达，容易让后续维护误恢复已终止路径。
- 事故通报修订指令中的“可可靠分离”是语病，可能削弱模型对材料分离边界的理解。

允许的最小改动：同步 README 与 host capability；明确隐式入口仅限事故通报，情况说明、办理通知和纪要不启用；删除不可达正则与指导语；修正一句提示语。不得恢复其他隐式文种，不得改变动态阈值、机械门、verifier 或正常 D0/D1 选择。

验收：事故通报正向、情况说明/通知/纪要反控、明确上限/极短/只审旁路均保持；生成的事故修订指令保留事实、状态、合理推断和不能安全增长时逐字 D0 的现有边界；README、JSON 与运行时只声明一个隐式文种。

### HK-009-STOP-BUDGET-R1

- shared core 的 `detect`、`prepare/finalize/emit` 与 `abort` 子进程各自最多 20 秒；Claude-compatible、Codex、CodeBuddy、Qwen、Kimi 的 Stop 上限为 30 秒。
- 异常终态存在同一 Stop 内 `prepare/finalize -> abort -> emit` 或 `abort -> emit` 的路径，静态最坏值可超过宿主预算。当前没有共享剩余时限测试。

允许的最小改动：为单次 `handle_stop` 建立上下文隔离的 25 秒 review-gate 子进程总预算，保留单次调用 20 秒上限；`detect`、`_run_gate` 和 `_abort` 都只取得剩余预算，耗尽后不再启动新子进程。不得粗暴把所有单次调用统一降到 10 秒，不修改宿主 manifest 的 30 秒上限，不改变正常状态机、尝试次数或能力路由。

验收：模拟慢子进程时，同一 Stop 传入 `subprocess.run` 的 timeout 总和不超过 25 秒；预算耗尽后第三个子进程不启动；下一次独立 Stop 获得新预算；任一步失败仍沿既有 fail-open/D0 与终态脱敏路径，不泄露正文或状态包。

## 验证顺序

1. 先添加能在固定基线上暴露契约漂移和累加超时的定向测试，确认失败原因只属于本原子。
2. 再做最小产品修改，运行 under-length 与 gate Stop 定向回归和一条本地真实脚本生命周期；只有目标问题消失且既有正反控不回退才保留。
3. 通过后补 requirements、coverage、roadmap、待办和 evidence 索引，运行 Hook/adapter 直接回归、组装和 `git diff --check`。本候选不跑大规模付费模型，也不因无关写稿偏好扩大规则。
