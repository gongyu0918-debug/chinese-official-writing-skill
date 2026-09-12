# 算力附加页组合 A/B R2（2026-09-12）

## 技术条件

- baseline：`main@1ce71123`；candidate：`db0762e5`；
- 同一题面、只读隔离快照、0 retry、无 Hook、无脚本；
- writer 通道分别为 `alibaba-token-plan/qwen3.8-flash` 与 `alibaba-token-plan-2/qwen3.8-flash`，均配置 `max`；
- 四次 receipt 均为 `COMPLETE`，读取边界通过。

## 结果

第一条通道：基线 8 次读取，候选 8 次读取；两臂均输出干净正文，无过程旁白。候选没有候选独有事实升级，但出现了“核对结果另行报告”等材料未明确的后续安排，暂记为需收紧规则的软性风险。

第二条通道：基线 6 次读取，候选 8 次读取；候选多读 `ai-compute-examples.md`、`final-review-layers.md` 和 `anti-ai-patterns.md`，并出现“具体指标和阈值在试用中掌握”“核对结果另行报告”等扩展。该组暴露了候选起草路由的过读和过扩展，不能判为通过。

正文哈希：

| 通道 | 基线 | 候选 |
| --- | --- | --- |
| Alibaba Token Plan | `c43fa7e648528422b002389fdc7e5efd479547e03bd8c4a50b25a3f160e263a5` | `30580a621bada53cea40746e1ff58831213c9fe8ac83507f3fbf7fed382e6ff8` |
| Alibaba Token Plan 2 | `daa0490959effdf5f2f67715553f840e9d318fbd42d9d2658e3a09fe06f36155` | `24229db84fea12b4e993d47887d5f11da71e5cc92105937c63ece7d9d312e719` |

## 处理结论

第一条通道可视为正文洁净和基本事实状态保持的有效样本；第二条通道说明候选路由仍不稳定。已进一步收紧：起草在主文种和明确叠加页完成后停止；算力术语、示例和审查资料只有用户明确要求时读取。该修正后需要重跑两条通道，当前不支持合并。
