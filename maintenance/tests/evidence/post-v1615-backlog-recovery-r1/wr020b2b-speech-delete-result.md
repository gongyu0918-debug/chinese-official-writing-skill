# WR-020b2b 已有讲话稿任务句精确删除结果

日期：2026-08-24。

## 结论

`CURRENT_PRODUCT_DONE_NO_NEW_RULE / OLLAMA_DELIVERY_FAIL_RETAINED`。

Alibaba 与 Luna 两条具有4文件读取回执的有效路线只删除目标材料外任务句，完整保留其余讲话正文；当前产品已经覆盖明确点名删除。Ollama 有效重跑也完成了删除，但在正文前新增读取自证和 Markdown 横线，直接交付失败。SKILL 与轻量卡已经明确“只交正文”和清理 Markdown 包装，本轮不再往讲话叶重复堆同义规则，不用两条通过覆盖 Ollama 失败。

## 结果

| 路线 | Codex session | 技术状态 | 目标结果 |
| --- | --- | --- | --- |
| Alibaba Token Plan 2 / DeepSeek V4 Flash 0731 max | `01a032b3-208a-7251-abc1-2e73a5a8961b` | `VALID`，读取限定4文件 | `PASS`；目标句删除，无近义任务、提示或其他改动 |
| GPT-5.6 Luna max | `01a032b4-aba5-7ba0-be8c-86c82aa7d157` | `VALID`，读取限定4文件 | `PASS`；目标句删除，只交完整正文 |
| Ollama Cloud / DeepSeek V4 Flash 0731 max | `01a032b4-af0d-75f2-b284-b8239b228fb1` | `VALID`，读取限定4文件 | `DELIVERY_FAIL`；删除动作正确，但新增“文件均已读取/样本有效”自证、引导句和 `---` 横线 |
| GPT-5.6 Luna max 首跑 | `01a032b3-2569-7bf2-80ab-bfe576cba57f` | `NO_SKILL_READ_INVALID` | 正文质量观察为精确删除，不计产品证据 |
| Ollama 首跑 | `01a032b3-2210-7713-ac01-956d6b3365bf` | `NO_SKILL_READ_INVALID` | 正文质量观察为精确删除，不计产品证据 |

初次 prompt 只写“只允许读取”，Luna/Ollama直接完成机械删除，没有 Skill 读取回执。测试约束随后只增加“必须实际读取4文件”，产品与题面正文均未变；无读取样本没有被冒充有效通过。

## 边界

本结果只证明用户点名一条完整句子的删除。它不证明模型可以自行判定哪条任务材料外，也不覆盖多句删除、改写、搬移组合或只审不改。Ollama 的正文包装是实际风险；除非后续新题跨 provider 复现且现有交付规则无效，否则不为单路遵循失败叠加规则。

## 实际执行

Codex CLI 0.144.6 经本机 OpenCodex 兼容端点执行，`read-only`、`ephemeral`、禁用用户规则与 Hook，推理强度为 `max`。列明 session 均 `exit 0`；WebSocket 426 后自动回退 HTTP。
