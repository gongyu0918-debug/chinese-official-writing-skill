# WR-020b2a 已有讲话稿任务段精确搬移结果

日期：2026-08-24。

## 结论

`CURRENT_PRODUCT_DONE_NO_NEW_RULE`。

当前 v1.6.15 产品已经能按用户明确结构动作，把一个既有未决状态自然段从第一项任务精确移到第三项任务，正文其余内容不改。3条具有可见限定文件读取回执的路线全部通过；OpenCode Go 正文也完成同样的精确搬移，但本轮截取未保留完整读取 trace，只作质量观察。没有建立候选，不修改讲话 playbook、task card、Hook、段长或节奏规则。

## 实际结果

| 路线 | Codex session | 技术状态 | 结果 |
| --- | --- | --- | --- |
| GPT-5.6 Luna max | `01a032b0-4833-7a13-9944-bd5f844e009b` | `VALID`，读取限定4文件 | `PASS`；目标段只出现一次，移至第三项第一段之后，其余正文未见改动 |
| Ollama Cloud / DeepSeek V4 Flash 0731 max | `01a032b0-46d6-7502-bd95-0fbc3d025b14` | `VALID`，读取限定4文件 | `PASS`；只交完整正文并精确搬移 |
| Alibaba Token Plan 2 / DeepSeek V4 Flash 0731 max | `01a032b0-474b-7613-9e40-c8d6746aac59` | `VALID`，读取限定4文件 | `PASS`；只交完整正文并精确搬移 |
| OpenCode Go / DeepSeek V4 Flash max | `01a032b0-4b51-7112-b256-2dbaf18f48aa` | `TRACE_INCOMPLETE`，当前截取未保留完整读取回执 | `OBSERVED_PASS`；正文精确搬移，无可见额外改动 |

四份正文均保留标题、称呼、三个任务标题、486=421+52+13、38分钟已恢复/原因联合复核、两轮测试、3个字段、3名联络人和两种保障方式未决；没有新增职责、程序、期限、成效、采购决定、解释或 Markdown 包装。

## 边界

本结果只证明“用户点名一个完整自然段及目标位置”的局部搬移。它不推翻 `WR-020b1` 首次起草任务卡的拒绝结论，也不证明模型可以自行判断复杂长稿中所有段落归属。删除、只审不改和多段组合分别保留为独立原子。

## 实际执行

所有路线均通过 Codex CLI 0.144.6 调用本机 OpenCodex 兼容端点，`read-only`、`ephemeral`、禁用用户规则与 Hook，推理强度为 `max`。WebSocket 426 后自动回退 HTTP；四条 session 均 `exit 0`。
