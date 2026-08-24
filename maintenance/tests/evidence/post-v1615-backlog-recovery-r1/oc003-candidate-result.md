# OC-003 算力可研状态与审稿建议候选结果

日期：2026-08-24。

## 结论

`ACCEPTED_RESEARCH_CANDIDATE / NO_MAIN_MERGE_OR_RELEASE`。

固定基线为 `main=origin/main@8aab5e61e65c0411b4bd6580173c2a107986fdcb`。基线起草题4条严格有效路线均新增材料外程序；候选在不删除测算、报价、未决状态和一层合理预期的前提下，使严格有效的 Luna、Ollama 起草稿不再生成具体核查、采购、上线或评估安排。Alibaba 原题仍有程序链回退，不能写成全模型通过；该回退在基线已经存在，不是候选独有回退。

只审不改侧，抽象禁令不足以稳定改变模型行为，经过“状态原样恢复—固定错误只删除或降级”的原子化修改后，Luna、Ollama 在原题收敛；Alibaba 原题的逐条意见仍与其总评冲突，但在全新事实盲样中收敛为恢复状态、不补比价审批程序。用户明确要求完整性核对的反向控制仍能检出成本同口径比较、技术指标、验收主体和验收依据，未出现过度保护。

因此保留本轮4处窄改动，进入包镜像与确定性验证；不因单模型残留继续堆规则，也不以多数票抹掉残留风险。

## 候选改动

1. `ai-compute-docs.md`：算力可研结构按材料取舍，篇幅不足不授权补核查、比价、采购、上线或后续安排。
2. `argument-chains.md`：可研的条件、整改、补充材料或后续程序只在材料已给或用户明确要求时写；仅有未决状态时止于当前状态与可行性判断。
3. `workflow.md`：实施、建设、进度、验收和后续管理章节改为“材料已给时”使用。
4. `genre-checklist-feasibility-review.md`：只审不改时把失实结论恢复为已给状态或删除；不把“尚无结论、未比价、未批预算、未形成采购决定”改写成正在核查或待办程序。用户明示完整性核对时仍按点名范围检查。

没有修改入口 description、通用信息选择、Hook、adapter、付费提纲分支或 main。

## 起草结果

基线结果及命令见 `oc003-baseline-result.md`。最终起草候选读取 `SKILL.md`、`information-selection.md`、`argument-chains.md`、`workflow.md`、`ai-compute-docs.md`，结果如下：

| 路线 | Codex session | 技术状态 | 目标结果 | 说明 |
| --- | --- | --- | --- | --- |
| GPT-5.6 Luna max | `01a03293-3425-7562-89af-3388b1ac0e7c` | `VALID` | `PASS` | 完整正文保留实测、抽样、年度测算、报价和全部未决状态；写一层“有望缓解高峰排队、提高处理稳定性”，未新增后续动作，未退化为极短稿。 |
| Ollama Cloud / DeepSeek V4 Flash 0731 max | `01a0328f-b08e-7b93-88fc-13a2d9c66f13` | `VALID` | `PASS_WITH_WARN` | 未新增具体程序，仅有“上述事项需在后续研究中进一步明确”的泛化状态句；不含责任主体、期限或具体动作。 |
| Alibaba Token Plan 2 / DeepSeek V4 Flash 0731 max | `01a03291-e6d7-76a2-a77c-7bf70bb9abff` | `VALID` | `TARGET_FAIL` | 仍把“尚无结论”写成技术组排查，把全部未决项写成后续逐项明确，并新增服务落地后运行验证。 |
| MiniMax CN / MiniMax-M3 max | `01a0328c-c12e-7e31-9359-690c692cd5ae` | `INSTRUCTION_INVALID` | `OBSERVED_TARGET_FAIL` | 越过限定读取范围；正文另有明显程序扩写，只作质量观察。 |
| OpenCode Go / DeepSeek V4 Flash max | `01a03294-fcc8-7052-a8bc-828ede7e9687` | `INSTRUCTION_INVALID` | `OBSERVED_TARGET_FAIL` | 额外检查目录和行数；正文新增重新核定、后续明确、服务落地验证，只作质量观察。 |

起草侧相对基线由“4/4严格有效路线目标失败”改善为“2条严格有效路线通过或带轻微泛化提示、1条严格路线残留失败”；不能写成5家全过。

## 原题审稿迭代

| 阶段 | 路线与 session | 结果 |
| --- | --- | --- |
| 状态原样恢复规则 | Luna `01a0329f-ca9c-7c73-a518-fa508c15dc28` | `PASS`；只删除、降级或恢复状态，不新增程序。 |
| 状态原样恢复规则 | Ollama `01a0329f-c5ed-7943-b2d3-bad61d412829` | `TARGET_FAIL`；仍写“待比价并履行审批程序”。 |
| 状态原样恢复规则 | Alibaba `01a0329f-c763-7fb3-b186-5773a5410104` | `TARGET_FAIL`；仍写待核查、待比价测算、待审批。 |
| 三处固定转换正向动作 | Ollama `01a032a1-f858-7cd1-bae5-524daea30cc4` | `PASS`；恢复运行事实和未决状态，删除无依据比例与采购条件，不新增程序。 |
| 三处固定转换正向动作 | Alibaba `01a032a1-f573-7501-af2b-02ab6a590ab2` | `TARGET_FAIL_WITH_SELF-CONTRADICTION`；总评要求不补待办，逐条意见仍写“尚在核实”和采购前置程序。 |

MiniMax 在此前两轮出现目录枚举、Markdown包装和程序补写，作为 `INSTRUCTION_INVALID / OBSERVED_TARGET_FAIL` 保留，不用重抽覆盖。

## 新事实盲样与反向控制

新事实盲样没有沿用3200项、8.64亿 Token、78万元等原题数字，改为票据识别与分类场景；反向控制明确要求核对采购决策完整性。

| 题目 | 路线与 session | 结果 |
| --- | --- | --- |
| 新事实只审盲样 | Ollama `01a032a4-82bb-7402-bf5a-bc937d07d1e8` | `PASS`；逐项恢复测算、初步报价和可研状态，无待办程序。 |
| 新事实只审盲样 | Alibaba `01a032a4-8435-7543-b12f-c20bc24de93c` | `PASS_WITH_WARN`；不新增比价审批程序；另提示7部门变化时测算口径需调整，属基于已给未决范围的敏感性提醒。 |
| 明示完整性核对控制 | Luna `01a032a4-8706-7b20-8b94-3c3bfd094aba` | `PASS`；检出同口径成本比较、并发/时延/SLA、验收主体和验收依据，且保留“可研阶段、未形成采购决定”。 |

## 消融与五提交 review

- 仅在 `ai-compute-docs.md` 增加结构取舍句时，Luna、Ollama、OpenCode Go 质量观察改善，MiniMax仍补“采购完成、服务上线并稳定运行后验证”。
- 增加字数优先级仍不能稳定压住程序链；把可研论证链与 workflow 中的实施、验收章节改为材料条件项后，Luna、Ollama 起草稿收敛，说明缺口不只来自篇幅压力。
- 审稿侧抽象“不要新增程序”不足；固定状态转换才在 Ollama 原题和 Alibaba新盲样生效。
- 第5和第10个提交后均检查固定基线、完整 diff、五提交增量和改动边界。第10提交 review 发现 `oc003-baseline-result.md` 尾部多余空行，已由 `c2019b0e` 单独修复。
- `python C:\Users\admin\.codex\skills\.system\skill-creator\scripts\quick_validate.py chinese-official-writing`：`Skill is valid!`。

## 实际执行方式

所有稿件均经 Codex CLI 调用本机 OpenCodex 兼容端点，关闭用户配置、用户规则和 Hook，工作区只读，推理强度为 `max`。命令形态与基线证据相同，仅替换模型和 prompt 文件。WebSocket 426 后 CLI 自动回退 HTTP；列明 session 均最终 `exit 0`。限定读取失败的样本单列为无效，不以正文质量覆盖指令失败。

## 剩余风险与边界

- Alibaba 在原题仍出现“逐条意见补程序、总评禁止补程序”的内部矛盾；新事实盲样已收敛，但不能据此宣称该 provider 稳定通过。
- MiniMax 和 OpenCode Go 在严格限定读取题上存在工具遵循问题，当前只提供质量观察。
- 本轮没有验证 Hook D0、description 触发、付费提纲生命周期或长讲话稿；这些属于后续独立原子。
- 当前仅为研究分支候选；包镜像、确定性回归、main 合并和发布分别需要后续验证与授权。
