# `SHORT-NATURAL-REFERENCE-R1` R2 真实写稿结果

## 固定候选

- 产品候选：`95ffb71d2e4ea0f465e94031c83823a55b52f1e6`。
- 五家低成本 provider、同一十题、`max`，共 50 次输出；49 次确认固定 Skill trace，MiniMax 的100—120字压缩控制为技术失效。40 次普通起草均技术有效。
- R2 相对 R1 删除通用六文种功能枚举，增加“文种功能已经完整时停止扩写”，并只保留说明/通知/事故轻量卡的窄指导。

## 量化结果

| 题组 | R2 有效正文字符 | 低于校准值 | 人工结论 |
| --- | --- | ---: | --- |
| 采购算力 | 143—227 | 0/5 | 基线已足够；R2没有篇幅目标收益，仍可见模型既有的调研、任务增量或用途外扩 |
| 办公采购 | 118—286 | 0/5 | 基线已足够；一份仍新增“另行报批”，MiniMax 继续外扩办文和采购流程 |
| 维修申请 | 131—177 | 0/5 | 基线已足够；OpenCode 候选独有新增检测后另行报告，其他报告/判断风险与基线部分共有 |
| 活动新闻 | 166—260 | 0/5 | 篇幅不短，但两家由基线保留2026年变为只写8月28日；多家仍出现材料外培训过程或后续安排 |
| 未决情况说明 | 104—224 | 3/5 | Alibaba 1/2、MiniMax 三家候选独有漏掉“本次材料未附”，目标未改善且出现跨 provider 硬回退 |
| 突发事故通报 | 101—230 | 0/5 | 内容5/5没有擅自判断事故原因；是否使用正常的后续通报收束不再作为质量门。Alibaba 2、OpenCode 同时输出过程说明，直接交付形态回退 |
| 办理通知 | 94—230 | 2/5 | 两份干净正文仍为94/96字；OpenCode输出过程/自评，MiniMax仍新增“梳理”前置动作 |
| 未决会议纪要 | 116—308 | 2/5 | 目标未改善；MiniMax新增主持、业务办理、下次研究、另行通知及意见汇总等多项材料外内容 |
| 100—120字压缩 | 四份113字 | 不适用 | 四份有效稿遵守范围；一份技术失效 |
| 不超过80字 | 五份44—47字 | 不适用 | 5/5旁路普通篇幅要求，事实和字段完整 |

## 决定与 R3

R2 为 `REJECTED_TARGET_NOT_IMPROVED_AND_CANDIDATE_OMISSION`。最明确的阻断不是合理推断，而是三家共同漏掉材料明确存在但未附的联调记录状态；通知和纪要也未取得跨 provider 的篇幅目标改善。

R3 继续拆成一个产品字节原子：

- `SKILL.md` 与 `task-route-cards.md` 完全恢复当前 main；
- 只修改普通起草必读的 `information-selection.md` 篇幅段，删除“宁可短于下限”的默认偏置，保留“不换词缩写、不短于可分离事实材料”；
- 不点名任何文种、功能、作用、结论、原因或示例，不新增 Hook、adapter 或工程门。

R3 若仍没有跨 provider 目标改善，普通 reference 原子终止，不继续堆措辞；100字写后兜底转由独立 `UL-006` Hook 同稿原子验证。

## 实际命令

```powershell
python maintenance/tests/evidence/short-natural-reference-r1/run_eval.py --arm candidate_r2 --prepare
python maintenance/tests/evidence/short-natural-reference-r1/run_eval.py --arm candidate_r2 --provider alibaba2
python maintenance/tests/evidence/short-natural-reference-r1/run_eval.py --arm candidate_r2 --provider alibaba1
python maintenance/tests/evidence/short-natural-reference-r1/run_eval.py --arm candidate_r2 --provider ollama
python maintenance/tests/evidence/short-natural-reference-r1/run_eval.py --arm candidate_r2 --provider opencode
python maintenance/tests/evidence/short-natural-reference-r1/run_eval.py --arm candidate_r2 --provider minimax
python maintenance/tests/evidence/short-natural-reference-r1/run_eval.py --summarize
```

逐份人工复核只把候选独有的新具体事实、状态遗漏、程序、责任、承诺、文种或交付形态回退计为候选失败；合理原因、直接作用、阶段归纳和条件性判断没有被当作失败。
