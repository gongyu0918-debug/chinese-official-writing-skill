# A/B 映射与揭盲结果

本文件在 `verifier-blind.md` 和 `verifier-hard-boundary.md` 均完成后创建。两名 verifier 审核时未获知以下映射。

固定基线：`v1.5.13` / `cd2d46c58a5f56b9009c5da08626a88640f2e5b3`

候选提交：`f4d79ceeed4f2ae78f8a2522f22f709d63b6056c`

| Writer | A | B |
|---|---|---|
| Writer E | 固定 `v1.5.13` 基线 | current |
| Writer F | current | 固定 `v1.5.13` 基线 |

## 内容揭盲

综合盲审：

| 版本 | PASS | WARN | FAIL | 合计 |
|---|---:|---:|---:|---:|
| 固定 `v1.5.13` 基线 | 29 | 1 | 0 | 30 |
| current | 29 | 1 | 0 | 30 |

两项 WARN 分别是 Writer E 的 F01-A 和 F01-B：均未明示“未形成决定、结论、责任分工和完成期限”，但保留了建议、观察和再次评估的未决状态，没有写出相反决定。该现象在同一 writer 的基线侧和 current 侧对称出现，不是版本独有。

硬边界盲审：

| 版本 | PASS | WARN | FAIL | 合计 |
|---|---:|---:|---:|---:|
| 固定 `v1.5.13` 基线 | 30 | 0 | 0 | 30 |
| current | 30 | 0 | 0 | 30 |

揭盲后未发现 current 独有的事实、文种、格式或输出模式 FAIL，也没有 current 独有的 WARN。

## 路由揭盲

两名 writer 自报的 60 条路由均被综合 verifier 判为任务相关。按本轮新增仲裁边界进一步核对：

- F01 简短且全部未决：current 两次均自报未决事项轻量卡；基线一次自报轻量卡、一次自报会议纪要 playbook。
- F02 完整正式且已形成决定：current 和基线均自报会议纪要 playbook。
- F14 完整正式但全部未决：current 和基线均自报会议纪要 playbook，证明“完整正式”请求可独立触发升级，同时保持未决状态。
- F15 简短但已形成决定：current 和基线均自报会议纪要 playbook，证明“已形成决定、责任和期限”可独立触发升级。

`ROUTE` 为 writer 自报，不是操作系统级文件访问日志。确定性 provider 的精确提示核对另见主报告。
