# References 四原子减载真实验证汇总

日期：2026-08-29。固定产品起点：`main@31dacd0805035521ad848bdc10e70c0a366d554c`（已发布v1.6.19回执后的主线）。

## 总结

四个候选均已完成真实任务、trace读取和逐稿复核，没有留下`HOLD`，也没有产品规则、Hook、包体、description、版本或发布变化。会议纪要检查搬移、通知拆叶和复核四层拆分直接拒绝；采购公告拆叶是唯一写稿质量安全且有局部减载信号的候选，已继续做最小R2，控制污染消失但真实减载仍只有2/5 provider，因此也恢复原产品。

| 原子 | 真实输出 | 可归因路由 | 稿件结论 | 终态 |
| --- | ---: | ---: | --- | --- |
| `MINUTES-CHECKLIST-LEAF-R1` | 40，技术有效39 | 0/15目标对 | 纪要事实、未决状态、责任期限总体安全；Baseline目标本来不读通用检查页 | `REJECTED_INSUFFICIENT_ATTRIBUTABLE_LOAD_BENEFIT` |
| `NOTICE-LEAF-CURRENT-R1` | 50，技术有效48 | 2/15目标对 | 出现对象扩大、材料外目的/星期/成文日期/合同关系、过程说明和控制串叶 | `REJECTED_ROUTE_BENEFIT_INSUFFICIENT_AND_CONTROL_REGRESSION` |
| `PROCUREMENT-ANNOUNCEMENT-LEAF-R1/R2` | 60，技术有效59 | R1 2/5；R2 2/5 | 公告质量安全；R2把控制污染从1降至0，但仍未达到3/5减载门 | `REJECTED_INSUFFICIENT_ATTRIBUTABLE_LOAD_BENEFIT_AFTER_MINIMAL_REPAIR` |
| `REVIEW-LAYER-SPLIT-R1` | 40，技术有效40 | 0/10局部目标对 | 局部Baseline本来不读大页，全文能力0/5闭合；两家Candidate给改后正文添加Skill过程旁白 | `REJECTED_ROUTE_NOT_REPRODUCED_AND_BODY_PACKAGING_REGRESSION` |

## 真实模型与用量

五条路线均在Codex CLI隔离环境内加载本候选的`.agents/skills/chinese-official-writing`，Hook关闭、只读、ephemeral、零重试，reasoning effort为`max`：

- `alibaba-token-plan-2/deepseek-v4-flash-0731`
- `alibaba-token-plan/deepseek-v4-flash-0731`
- `ollama-cloud/deepseek-v4-flash:0731`
- `opencode-go/deepseek-v4-flash`
- `minimax-cn/MiniMax-M3`

累计190次真实任务输出，其中180次为起草或改写、10次为纯格式复核形状控制；186次技术有效、4次按预登记作废。客户端usage回执累计：input 25,039,049 token、cached input 18,493,051、output 670,654、reasoning output 310,740。用量证明这些是实际模型调用，不是静态规则表或stub；数量本身不作为质量票。

## 证据

- [总预登记](preregister.md)
- [会议纪要结果](minutes-result.md)
- [通知结果](notice-result.md)
- [采购公告R2预登记](procurement-r2-preregister.md)
- [采购公告R1/R2结果](procurement-result.md)
- [复核分层结果](review-result.md)

原始final、trace、stderr、fixture和summary保留在各实验worktree的忽略目录；每份终态记录给出fixture与summary SHA-256。所有实验产品均已恢复固定Baseline，不应选择性合入候选产品字节。

