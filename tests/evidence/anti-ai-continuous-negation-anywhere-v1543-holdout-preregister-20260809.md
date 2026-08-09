# 连续否定全位置减载跨模型留出预注册

日期：2026-08-09

固定 Baseline：`03c13d2dea8924d3eb2e8c487956da45ce6b0692`

固定 Candidate：`fcc1d960a857fa418afa83714fbabdd0b5fed431`

## 目的

首轮5个有效配对支持 Candidate 减载后不劣，但一个 Ollama Baseline 技术无效，且两家均为 DeepSeek V4 Flash 0731。留出测试保持题包、六文件 context、判据、唯一产品 DIFF 和首个 final 冻结方式不变，只更换模型，不重跑或替代失效配对。

## 矩阵

- `gpt-5.6-luna`，`max`，2组 Baseline/Candidate 配对；
- `alibaba-token-plan/qwen3.8-max`，`max`，2组 Baseline/Candidate 配对；
- 共8次调用，无重试；模型内部平衡两臂先后。

## 裁决

1. 每个模型至少2个完整配对；任一臂技术无效则整对作废。任一模型不足2对时，留出只记 `NO EVIDENCE`，Candidate 继续隔离。
2. Candidate 在每个模型的目标分句和连续否定组均不得高于 Baseline；任何 Candidate 独有事实、对象、状态、否定范围、禁令或引语硬回退立即停止。
3. 两臂目标0对0、控制全部通过时，按替换减载目标记“行为不劣”，无需制造 Candidate 语言净胜。
4. 留出两种模型均通过，且与首轮5个有效配对无冲突，Candidate 才可由 `PROVISIONAL` 升为 `REAL NON-INFERIOR RELIEF / MERGE-ELIGIBLE`；仍须组合回归后才能合 main。
5. 固定引语、标点、句长等与目标 DIFF 无直接关系的单次差异单列为模型/采样噪声，不能据总胜数抵销硬回退，也不能冒充规则收益。

本留出不改产品、不推送、不发布。
