# OC-003-AI-FEASIBILITY 基线真实写稿结果

日期：2026-08-24。

## 结论

`REPRODUCED_NARROW_GAP / BUILD_ONE-SENTENCE_CANDIDATE`。

当前产品能够区分实测、测算、假设、初步报价和未决状态，也允许在排队、并发与拟议服务的直接关系上写一层“预计缓解高峰排队、提高处理稳定性”的合理预期；这一部分不需要收紧。实际缺口是：`ai-compute-docs.md` 的完整可研/采购骨架会诱发模型把材料没有给出的比价、预算审批、采购程序、合同谈判、启动、试运行或后续评估补成已经启动、将要推进或必须履行的动作。

起草题4条严格有效路线均复现了该缺口，第5条路线因越过限定读取范围不进入严格计数，但其正文也有同类表现。只审不改题5条路线均识别了题面硬错误并保留合理预期句；同时，5条路线的修改建议仍不同程度补入材料外程序。达到预登记的跨模型复现条件，只建立一个最接近 `ai-compute-docs.md` 常见结构的单句候选，不改入口、信息选择、论证链、审查叶、Hook或字数门。

## 起草题

| 路线 | Codex session | 技术/指令状态 | 目标结果 | 观察到的材料外增量 |
| --- | --- | --- | --- | --- |
| Ollama Cloud / DeepSeek V4 Flash 0731 max | `01a0326a-a110-78b2-a0c0-75052c544c6b` | `VALID`，读取固定5文件 | `TARGET_FAIL` | 末段新增“按程序推进需求范围确认、同口径费用测算、供应商比选和采购方式研究”“经审定后另行确定”；材料没有给这些后续动作。 |
| Alibaba Token Plan 2 / DeepSeek V4 Flash 0731 max | `01a0326b-deaa-7de1-8696-9926ff2560b3` | `VALID`，读取固定5文件；交付模式另有硬失败 | `TARGET_FAIL` | 新增“后续应重点推进比价、超时原因分析、需求假设复核和经费安排论证”；并输出过程旁白、Markdown横线、加粗标题、字数和“要点说明”，不是只交正文。 |
| MiniMax CN / MiniMax-M3 max | `01a0326b-db22-7022-b859-ec307c2cbc7c` | `VALID`，读取固定5文件 | `TARGET_FAIL` | 新增“立项审批、采购程序和合同谈判环节”“预算审批程序尚未启动”“正式投运后另行评估”；还把“尚无原因结论”扩成技术组继续梳理/正在分析。 |
| GPT-5.6 Luna max | `01a0326d-738d-7143-8d05-c949432bfd20` | `VALID`；首次批量读取被沙箱拒绝后，逐文件读取固定5文件 | `TARGET_FAIL` | 新增“采购决定及相关程序也未启动”；材料只说未形成采购决定，没有给程序是否启动。其余事实、测算、报价和一层合理预期完整。 |
| OpenCode Go / DeepSeek V4 Flash max | `01a0326d-7035-7670-bd62-b50fede90617` | `INSTRUCTION_INVALID`：执行了限定范围外的目录枚举，不进入严格矩阵 | `OBSERVED_SAME_GAP` | 正文新增“技术组仍在核查”“经费来源未落实”“上述事项均需在形成采购决定前进一步明确”等材料外状态或动作。 |

五稿均没有把8.64亿 Token写成实耗、没有把78万元写成已批预算或合同金额，且均能写出低强度预期。候选只处理共同的程序补写，不因稿件偏短、模型包装或单稿文采差异扩大规则。

## 只审不改题

| 路线 | Codex session | 技术状态 | 正确识别与保留 | 材料外建议增量 |
| --- | --- | --- | --- | --- |
| Ollama Cloud / DeepSeek V4 Flash 0731 max | `01a03270-9569-76c2-ae61-e42f1dc21d75` | `VALID` | 识别全部7类风险，明确合理预期句可保留 | 建议写“采购后通过运行验证”“预算审批程序”等题面未给程序。 |
| Alibaba Token Plan 2 / DeepSeek V4 Flash 0731 max | `01a03270-9515-7f30-8bb0-01a42b0dbdca` | `VALID` | 识别全部风险并保留合理预期句 | 建议“完成比价和预算审批前暂不具备采购条件”。 |
| MiniMax CN / MiniMax-M3 max | `01a03272-233a-7ed3-8483-18290c6616ad` | `VALID` | 识别实际/测算/假设、报价、供应商和效果强度错误，明确合理预期句可保留 | 建议补足预算审批、供应商比选、服务方案、合同条款和试运行验证。 |
| GPT-5.6 Luna max | `01a03272-2109-7e13-950f-7dccd413f733` | `VALID` | 识别全部目标风险 | 对正确句提出额外资源对应关系要求，并建议采购判断等待比价、预算审批、供应商确定和技术验证。 |
| OpenCode Go / DeepSeek V4 Flash max | `01a03275-4b89-70a2-b2dc-e6dedc9af338` | `VALID`，仅读取固定4文件 | 识别全部目标风险，判合理预期句为低风险、可保留 | 建议“需开展比价选型”，并在清单外追加待确认事项、验证方案和运行说明。 |

审稿能力本身有价值，不需要新增独立审稿叶。需要校正的是建议边界：修改建议应以现有句子的删除、核算、降级或限缩为主，不能因为可研通常包含某道程序就把该程序写进本题。

## 实际执行方式

五条路线均通过 Codex CLI 调用本机 OpenCodex 兼容端点执行，未使用自建写稿 harness；关闭用户配置、用户规则和 Hook，工作区只读，模型推理强度为 `max`。命令形态如下，模型名和 prompt 文件按路线替换：

```powershell
$env:OPENAI_API_KEY='opencodex-loopback'
$env:RUST_LOG='error'
$promptText = Get-Content -Raw -LiteralPath '<prompt-file>'
codex exec --ignore-user-config --ignore-rules --sandbox read-only --ephemeral --color never `
  -m '<model>' `
  -c 'openai_base_url="http://127.0.0.1:10100/v1"' `
  -c 'model_catalog_json="C:\Users\admin\.codex\opencodex-catalog.json"' `
  -c 'model_reasoning_effort="max"' `
  -C 'F:\Workspaces\chinese-official-writing-skill\output\research-worktrees\post-v1615-backlog-recovery-r1' -- $promptText
```

OpenCode Go 起草题的越界目录枚举如实保留为无效样本，不用正文质量覆盖指令失败。WebSocket 端点返回426后 CLI 自动回退 HTTP；各列明 session 均最终 `exit 0`，未因质量原因重抽。

## 下一步固定原子

只在 `chinese-official-writing/references/ai-compute-docs.md` 的“常见结构”附近增加一句：完整结构按材料取舍，材料未给的比价、预算审批、采购程序、合同谈判、启动或后续评估不得补成已启动、将推进或必须履行的动作。保留现有“低强度合理预期”规则，不把程序克制扩成禁止一般原因、目的、即时作用或合理影响推断。
