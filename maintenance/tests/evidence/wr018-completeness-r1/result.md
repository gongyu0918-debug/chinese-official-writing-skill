# `WR-018-COMPLETENESS-R1—R3` 真实写稿终态

日期：2026-08-30。

终态：`TERMINATED_REFERENCE_NOT_STABLE / PRODUCT_RESTORED / NOT_MAIN / NOT_V1.6.21`。

## 目标与判定修正

同一事项同时给出“结果已经形成”和“本次材料未附”时，正文应同时保留两种状态，不把“未附”省略或改成以后提供、报送、说明的承诺。只统计候选相对基线且与该规则有关的变化；`本次未随附`、`未随本说明附送`、`未随附`均按等义保留，不因没有逐字出现“本次材料未附”判失败。标题、分段、自然归纳和合理前置说明不属于本原子失败。

正文前后解释 Skill、路由、规则执行或“以下是正文”属于直接交付回退。该回退只有在候选新增时才归因于本原子；基线已有的包装不重复归罪。

## 真实结果

固定 `main@c60e3ffaa12af012bf2a3910081ae70244a87a21`，五家低成本 provider 使用同一内部情况说明。R1 完成五家 baseline/candidate 共10稿；R2、R3各完成五家 candidate，另分别复跑 MiniMax 与 Alibaba2一次，总计22稿，全部技术有效并实际按隔离 Skill 路由；R2/R3复测均核对了目标 reference 的真实读取。

| 轮次 | 完整性收益 | 与改动有关的回退 | 结论 |
| --- | --- | --- | --- |
| R1 示例式规则 | Alibaba2、Alibaba1、OpenCode 相对各自基线补回“未附”；Ollama、MiniMax原基线已保留 | MiniMax候选把轻量卡、事实单元和禁补项解释抄到正文前 | 拒绝示例式写法 |
| R2 抽象规则 | Alibaba2、Alibaba1、OpenCode继续保留；MiniMax首次写“本次未随附”，复跑写“本次材料未附” | MiniMax两次候选均新增正文前包装，首次为规则说明，复跑为“下面是可直接使用的正文” | 目标收益存在，但直接交付不稳定 |
| R3 记录/附件具体化 | 五家均保留等义随附状态；Alibaba1的“本次材料未随附”和OpenCode的“未随本说明附送”均人工改判为通过 | Alibaba2首次和同题复跑均新增材料稀疏、轻量路由或状态保持说明 | 包装回退跨轮转移到另一 provider |

R2 的原自动检查把等义“未随附”误记为缺失，R3 后已修正；修正评判后仍不改变终态。三个措辞原子都能改善部分模型的事实完整性，但没有一个在五家中同时保持正文直接交付，继续堆 reference 文字的边际收益不足。

## 决定与剩余风险

- canonical `task-route-cards.md` 已恢复到 `main@c60e3ffa` 产品字节；三个产品提交只保留在历史中，不同步镜像、不合并公开主线。
- 本项不再显示为 `HOLD`。若以后出现不依赖新增 reference 文字的同类缺失，可作为新的 Hook 完整性观察或共享事实选择机制另立原子；没有新机制或新反例时不重跑 R1—R3。
- 当前产品仍可能在单稿中遗漏“已形成但未附”的后半状态；这是已知残余风险，不以本轮不稳定候选修复。
- 所有模型原始 trace、终稿、fixture 与 provider JSON 保存在各自 worktree 的忽略目录 `output/wr018-completeness-*`，未提交模型正文或运行时凭据。

## 实际命令

- `python maintenance/tests/evidence/wr018-completeness-r1/run_eval.py --prepare|--provider <id>`
- `python maintenance/tests/evidence/wr018-completeness-r1/run_eval_r2.py --prepare|--provider <id>`
- `python maintenance/tests/evidence/wr018-completeness-r1/run_eval_r3.py --prepare|--provider <id>`
- `python maintenance/tests/evidence/wr018-completeness-r1/run_eval_r3_repeat.py --prepare|--provider alibaba2`
- `python maintenance/tests/evidence/wr018-completeness-r1/run_eval_r2_repeat.py --prepare|--provider minimax`
- `git diff --check c60e3ffaa12af012bf2a3910081ae70244a87a21..HEAD`
