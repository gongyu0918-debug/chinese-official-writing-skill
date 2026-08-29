# `UL-005-R10` 扩写指令 R2 结果

## 结论

`REJECTED_R2_REPAIR_R3`。固定复用 R1 的15份基线，只重跑 R2 五路候选共15份，全部技术有效。R2 已把稀疏控制的安全回退从 R1 的1/5提高到4/5，并消除 R1 MiniMax 新闻稿的参与状态改写和后续培训安排，但 MiniMax 仍在稀疏题强行补用途，且在材料充足采购稿的未决状态后追加新程序；Alibaba 1 新闻稿仍有正文前字数核验。候选尚不能准入。

## 结果

| 题目 | R2 候选 | 人工复核 |
| --- | --- | --- |
| 扫描仪采购申请 | 4/5进入220—280字；Ollama为216字 | 五份均保留主要事实并写出一层必要性和预期作用；MiniMax 在“尚未确定”后新增“待确定后将按规定程序办理”，为候选独有程序外扩 |
| 培训活动新闻 | Alibaba 2、Ollama、OpenCode 进入目标范围；MiniMax逐字回 D0；Alibaba 1 的正文达到目标但附字数核验 | R1 的“未完成→未参加”“持续改进培训安排”已消失；仍有1份交付包装，不因 MiniMax 安全回退而强迫其扩写 |
| 稀疏打印机控制 | Alibaba 1/2、Ollama、OpenCode 4/5逐字回 D0 | MiniMax 仍补“日常办公文件打印”用途和采购缘由；这是具体材料外用途，不是一层合理推断 |

## R3 最小修复

R3 不再增加推断类别，只前移三项输出/状态边界：

1. 无论扩写或回退，回复首尾都必须是终稿，不得添加字数核验、自评、引导语或说明。
2. 原请求明确允许材料不足时短于下限，且材料只给拟办事项与未决字段、没有现状、原因或用途时，必须逐字返回 D0；不得用对象通常用途补足。
3. 未决状态句后不得接“待确定后将、另行、按规定程序、持续、后续”等新动作或程序。

R3 继续复用相同15份基线，只重跑五路候选。若 MiniMax 仍在稀疏题编具体用途/程序，或出现新的候选独有硬回退，则恢复 v1.6.20 产品字节并将本方向记为 `TERMINATED`，不再堆提示词。

## 实际命令

```powershell
python maintenance/tests/evidence/short-inference-r1/run_underlength_ab.py --prepare --candidate-commit b9aa3f6a5e2d22999c1617c64321dbb7c9187ed4 --output-root output/short-inference-r1/underlength-r10-r2
python maintenance/tests/evidence/short-inference-r1/run_underlength_ab.py --provider alibaba2 --candidate-only --output-root output/short-inference-r1/underlength-r10-r2
python maintenance/tests/evidence/short-inference-r1/run_underlength_ab.py --provider alibaba1 --candidate-only --output-root output/short-inference-r1/underlength-r10-r2
python maintenance/tests/evidence/short-inference-r1/run_underlength_ab.py --provider ollama --candidate-only --output-root output/short-inference-r1/underlength-r10-r2
python maintenance/tests/evidence/short-inference-r1/run_underlength_ab.py --provider opencode --candidate-only --output-root output/short-inference-r1/underlength-r10-r2
python maintenance/tests/evidence/short-inference-r1/run_underlength_ab.py --provider minimax --candidate-only --output-root output/short-inference-r1/underlength-r10-r2
python maintenance/tests/evidence/short-inference-r1/run_underlength_ab.py --summarize --output-root output/short-inference-r1/underlength-r10-r2
```

原始末条消息、JSONL轨迹和 token/耗时记录保存在忽略目录 `output/short-inference-r1/underlength-r10-r2/`。
