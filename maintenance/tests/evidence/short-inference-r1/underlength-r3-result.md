# `UL-005-R10` 扩写指令 R3 结果

## 结论

`REJECTED_R3_REPAIR_R4`。五路候选共15份全部技术有效。R3 已实现稀疏控制5/5逐字回 D0、正文外包装0/15，并保留材料充足稿的一层原因与作用；但 Alibaba Token Plan 1 的扫描仪稿把未确定型号的“高速扫描仪”展开为“自动进纸、连续扫描”具体功能，属于与“通常功能”许可直接相关的候选风险，不能直接准入。

## 结果

| 题目 | R3 候选 | 人工复核 |
| --- | --- | --- |
| 扫描仪采购申请 | 4/5进入220—280字；Alibaba 1为213字但文种功能完整 | 五份均保留260份、1台、15至25分钟、错峰尝试、2台及四项未决状态；均自然写出必要性和预期作用。Alibaba 1 另断言设备具备自动进纸、连续扫描，具体规格未由材料支持 |
| 培训活动新闻 | 4/5进入220—280字；Ollama为217字 | 五份均保留完整日期、36/34/2范围、账号状态、补测和意见正在汇总。MiniMax 的“以确保全部完成”是补测目的，不是既成成效，记强度观察而不按过严口径判失败 |
| 稀疏打印机控制 | 5/5逐字返回 D0，SHA-256 均为 `3a9f111bd4d8ae13a613076c40336aae169c9b64287446cdff364e8f6aaebafd` | R1/R2 的用途、程序、后续报告和解释包装均消失 |

## R4 最小修复

R4 只补一条“通常功能”的抽象层级：对象名称已明示的上位功能可以用于一层作用推断，例如高速设备可以概括为提高处理能力；不得补材料未给的组件、技术特性、性能对比、参数或新增用途。原因、作用、归纳、状态、精确 D0 回退和正文交付口径均不再改。

R4 继续复用相同15份基线并重跑五路候选。若仍出现与该句直接相关的具体设备规格/用途外扩，或已通过的稀疏回退、状态、交付发生硬回退，则恢复 v1.6.20 产品字节并终止该方向。

## 实际命令

```powershell
python maintenance/tests/evidence/short-inference-r1/run_underlength_ab.py --prepare --candidate-commit 12b2dfd952ecc2ed4e0ac1308716c2bfd746b419 --output-root output/short-inference-r1/underlength-r10-r3
python maintenance/tests/evidence/short-inference-r1/run_underlength_ab.py --provider alibaba2 --candidate-only --output-root output/short-inference-r1/underlength-r10-r3
python maintenance/tests/evidence/short-inference-r1/run_underlength_ab.py --provider alibaba1 --candidate-only --output-root output/short-inference-r1/underlength-r10-r3
python maintenance/tests/evidence/short-inference-r1/run_underlength_ab.py --provider ollama --candidate-only --output-root output/short-inference-r1/underlength-r10-r3
python maintenance/tests/evidence/short-inference-r1/run_underlength_ab.py --provider opencode --candidate-only --output-root output/short-inference-r1/underlength-r10-r3
python maintenance/tests/evidence/short-inference-r1/run_underlength_ab.py --provider minimax --candidate-only --output-root output/short-inference-r1/underlength-r10-r3
python maintenance/tests/evidence/short-inference-r1/run_underlength_ab.py --summarize --output-root output/short-inference-r1/underlength-r10-r3
```

原始末条消息、JSONL轨迹和 token/耗时记录保存在忽略目录 `output/short-inference-r1/underlength-r10-r3/`。
