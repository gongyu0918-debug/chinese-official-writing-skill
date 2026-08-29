# `UL-005-R10` 扩写指令 R1 结果

## 结论

`REJECTED_R1_REPAIR_R2`。基线与候选各15份真实写稿，共30份均技术有效。候选证明“允许材料事实与通常功能直接支持的一层原因、作用、归纳和低强度预期”能够解决部分过度回退，但同时出现未决状态改写、后续安排新增和稀疏材料强行补足，不能直接准入。

## 目标收益

- 扫描仪申请：候选3/5进入220—280字，另两份分别为217字和281字；五份都能由260份、单机和排队事实形成必要性及预期作用，没有把合理推断本身当成失败。
- 活动新闻：候选4/5按机械正文计数进入220—280字；Alibaba 1 的正文实际约239字，但附字数自评，交付不合格。相比基线中 OpenCode 逐字回退、Alibaba 1/2 和 MiniMax 输出长篇“材料不足”解释，候选更容易形成完整新闻正文。
- 稀疏控制：Ollama 候选逐字返回 D0，说明新口径仍可安全回退；但该行为只在1/5成立，不足以放行。

## 候选独有硬回退

1. MiniMax 扫描仪候选把“预算、型号、供应商和采购方式尚未确定”改成“将另行研究确定”，把当前未决状态扩成后续动作。
2. MiniMax 新闻候选把参加培训但未完成模拟申报的2人写成“暂未参加”，并新增“持续改进培训安排”；真实归纳越过了人员状态和后续工作边界。
3. 稀疏控制中，MiniMax 新增日常文件印制用途、管理要求和办理程序；OpenCode 新增文件打印用途、审批条件、实施和后续报告。两份均为具体事实/程序外扩，不是允许的一层原因或作用。
4. Alibaba 1/2 稀疏候选虽未编具体事实，但在 D0 前附“材料不足”判断和字数推算；Alibaba 1 新闻候选另附字数自评，违反“只输出完整终稿”。

## R2 最小修复

R2 不撤回一层合理推断，只增加两条直接约束：

- D0 中“尚未、正在、未完成、拟、待定”等状态必须守住，不得改成“将另行研究、持续改进、作为后续依据”等新动作或承诺；归纳不得新增活动顺序、人员属性、参与状态或办理过程，预测只落到当前事项的直接作用。
- 事实不足时，返回 D0 必须从首字到末字完全相同，不加判断原因、字数、自评、引导语或横线。

R2 复用本轮15份固定基线，只重跑五路候选臂；若仍有候选独有具体事实、状态或程序硬回退，则恢复 v1.6.20 产品字节并终止该方向。

## 实际命令

```powershell
python maintenance/tests/evidence/short-inference-r1/run_underlength_ab.py --prepare --candidate-commit 9bf09ba264aba92bdc7f0543ebf3059f3eda20c9
python maintenance/tests/evidence/short-inference-r1/run_underlength_ab.py --provider alibaba2
python maintenance/tests/evidence/short-inference-r1/run_underlength_ab.py --provider alibaba1
python maintenance/tests/evidence/short-inference-r1/run_underlength_ab.py --provider ollama
python maintenance/tests/evidence/short-inference-r1/run_underlength_ab.py --provider opencode
python maintenance/tests/evidence/short-inference-r1/run_underlength_ab.py --provider minimax
python maintenance/tests/evidence/short-inference-r1/run_underlength_ab.py --summarize
```

原始末条消息、JSONL轨迹和 token/耗时记录保存在忽略目录 `output/short-inference-r1/underlength-r10/`。
