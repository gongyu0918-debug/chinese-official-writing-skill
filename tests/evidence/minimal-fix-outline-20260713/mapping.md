# 真实 A/B 解盲映射与汇总

本文件在两名 verifier 完成盲审后创建。两名 verifier 审阅时只知道 X/Y 为匿名条件，不知道下列映射。

## 条件映射

- Writer 1：`X=baseline-aaba577`，`Y=current-candidate`。
- Writer 2：`X=current-candidate`，`Y=baseline-aaba577`。
- 两个 writer 均记录 `MODEL_ID: unavailable`；未使用 MiniMax，未猜测精确模型 ID。

## 解盲后的 verifier 结果

| verifier | 候选胜 | 基线胜 | 平局 | 双失败 | 候选硬回退 |
| --- | ---: | ---: | ---: | ---: | ---: |
| verifier 1 | 6 | 1 | 5 | 0 | 0 |
| verifier 2 | 8 | 1 | 3 | 0 | 0 |

共同结论：

- T1、T2：候选在两个独立 writer 中均减少跨章近义重复，未遗漏给定事实。
- T3：Writer 1 的候选改善，Writer 2 的基线略优；候选均保留固定四章和层级，没有硬回退，结论为改善不稳定、继续观察。
- T4：候选均保留六章与给定材料；唯一硬失败是 Writer 2 的基线遗漏“10 名师生”这一访谈对象事实。
- T5：充分材料下没有过度压缩或事实补造。
- T6：候选维持只审不改，没有代拟新提纲。

按预先写入修复报告的门槛，候选在至少两个目标 prompt 上跨两次独立 writer 改善，且没有候选侧硬回退，因此保留单句修复。精确模型 ID 未暴露，本轮真实 A/B 只作为 Codex 原生子代理 sanity，不包装为指定精确模型矩阵或统计有效性证明。
