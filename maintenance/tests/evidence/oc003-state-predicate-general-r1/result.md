# OC-003 未决状态谓语泛化结果

日期：2026-08-25。

## 终态

- “尚未形成决定”不是多重否定或禁词。材料明确同一对象的整体决定尚未作出时，可以使用这一未决表述；只给局部节点未定、内容未设置或单次会议未审议时，不能上推为项目整体决定。
- 把 v1.6.16 可研复核叶中的专句改成通用“对象、谓语、时间范围和状态强度”规则，经过四轮最小化和最终因果臂仍出现候选独有硬回退，状态为 `TERMINATED`，产品文件已恢复 `main@65d85cc1` 原文。
- 把资金、审批或技术缺口直接列成“暂不具备相应条件”的产品例示，五路接受度不稳定，且与状态外扩风险同轮出现，状态为 `REJECTED`，不进入产品。
- 本轮只保留研究、真实写稿和状态回填；不改 Hook、adapter、description、版本或公开包，不合并 main，不发布。

## 官方表达校准

- 南阳市生态环境局公开材料出现“因该项目资金暂未下达，暂不具备启动政府采购条件”，说明材料同时给出直接前提缺口时，低强度条件判断可以成立，不能把“不具备/暂不具备”机械当作错误。
- 中国政府采购网使用“政府采购活动尚未完成”“中标、成交供应商尚未确定”，上海市发展改革委使用“尚未确定采购对象或承建主体”。这些实例支持按具体阶段、对象和谓语承载状态，而不是把局部未定统一概括为整体采购决定未形成。
- 来源、用途和链接见 [`research.md`](research.md)。公开稿只用于校准方法，没有复制文字、模板或代码。

## 真实写稿设计与结果

使用 Codex CLI 0.144.6，Hook 关闭、工作区只读、隔离用户级同名 Skill、reasoning effort=`max`。五条便宜路线为：

- `opencode-go/deepseek-v4-flash`
- `ollama-cloud/deepseek-v4-flash:0731`
- `alibaba-token-plan-2/deepseek-v4-flash-0731`
- `minimax-cn/MiniMax-M3`
- `gpt-5.6-luna`

首批10次 stdin 调用在模型生成前报 `No prompt provided via stdin`，全部记技术无效，不读取正文、不计质量。改用 prompt 参数后共36次有效真实复核/改稿：R1 10次、R2 10次、R3 5次、R4 5次、最终候选5次、MiniMax同题基线因果臂1次。

| 阶段 | 原子变化 | 真实结果 | 处理 |
| --- | --- | --- | --- |
| R1 | 删除专句，改为泛化恢复状态 | 状态层级有改善，但 Ollama 出现候选独有回退 | 不准入，继续缩小 |
| R2 | 增加整体/局部范围约束 | 十臂均能区分单次会议与整体决定；十臂又都把官方式资金缺口判断判得过严 | 不准入，校准判断标准 |
| R3 | 允许直接前提缺口形成低强度条件判断 | 采购资金题由0/5改善到3/5；其他三题无硬回退 | 改善不稳定，继续最小化 |
| R4 | 列出资金、审批、技术三类缺口 | 新采购题仅2/5接受；MiniMax把“未安排期限、未指定部门”改成“尚待明确” | 条件例示 `REJECTED` |
| 最终回退候选 | 只保留对象、谓语、时间范围和整体/局部层级，不再写条件例示 | OpenCode、Ollama、Alibaba2、Luna三题均通过；MiniMax再次把“未安排/未指定”写成“尚待研究确定” | 补同题基线因果臂 |
| MiniMax同题基线 | v1.6.16原文 | 正确保留“会议未安排采购期限，未指定承办部门” | 确认候选独有硬回退，泛化方向 `TERMINATED` |

最终候选的五路目标题均正确识别：一次会议未审议不能推出单位已经决定不采购；材料明示“取得环评批复后方可开工”且批复未取得时，“暂不具备开工条件”可以保留。失败只发生在 MiniMax 直接改稿题，但同模型同题 baseline 通过，因此不能归为模型固有噪声后忽略。

## 最终产物指纹

原始 trace、stderr、终稿和隔离 runtime 位于忽略目录 `output/oc003-state-predicate-general-r1/`；以下 SHA-256 绑定最终判定：

| 文件 | SHA-256 |
| --- | --- |
| `opencode-final-candidate.final.txt` | `fccc070bd764b0b622d193098ec4aa930a03874c66877200c3bd26f4b73299f8` |
| `ollama-final-candidate.final.txt` | `e4b2540b1070020da60809489d86b2d85d62b98e4147f3875e842ce1e35d2971` |
| `alibaba2-final-candidate.final.txt` | `5532d823d78c5e94bd62e99edb1a10a99ac625ca4664594618ed9a703f6d7228` |
| `minimax-final-candidate.final.txt` | `b4dcdc43d3778ef75d8166e9a9aa44afce588f7683d1784027984a78b35a9135` |
| `luna-final-candidate.final.txt` | `ebdd5c661eba5dba39333825ef06b9288502c0fd497e1af324c204058378252f` |
| `minimax-final-baseline.final.txt` | `68b5455160ca371efeeb18ccddf19b71fac26d3288d9b22670b2ca28db1860a9` |

六份最终 trace 均有一个 `turn.completed`。对应 session 为 `01a037c6-2ca7-7d72-9d66-4a9b2a065158`、`01a037c6-3aec-7243-a10e-83d7e791463a`、`01a037c6-2ad5-7be2-a402-f3618568348a`、`01a037c6-2e3a-75b3-9e4b-b205dbd8f3c2`、`01a037c4-a45d-76a3-acad-57d0256f21de`、`01a037cd-4e45-7f72-a172-aef208b0b728`。

## 实际命令形态

```powershell
$env:OPENAI_API_KEY='opencodex-loopback'
$prompt = Get-Content -Raw -LiteralPath '<prompt-file>'
codex exec --ignore-user-config --ignore-rules --ephemeral --json --color never `
  --sandbox read-only -m '<model>' `
  -c 'openai_base_url="http://127.0.0.1:10100/v1"' `
  -c 'model_catalog_json="C:/Users/admin/.codex/opencodex-catalog.json"' `
  -c 'model_reasoning_effort="max"' -C '<isolated-runtime>' -- $prompt
```

Luna 最终候选使用同一 Codex CLI 的 ChatGPT 原生模型路由；四条第三方路线及 MiniMax 因果臂使用本机 OpenCodex 兼容端点。四条遗漏代理参数的首次最终确认在服务端模型校验阶段返回400，均被同题有效调用覆盖，未计质量结果。

## 剩余风险

- 当前产品能区分已知样本中的整体决定和局部节点，但模型仍可能把“未设置、未安排、未指定”改成“待明确、待研究确定”；这是已有通用信息选择规则下仍可出现的生成风险，不再靠这一可研叶重复堆句子。
- 单个官方条件句只能证明该写法在有直接前提缺口时可能成立，不能推广为所有资金、审批或技术材料的固定句式。
- 只有新的真实用户稿反例或不同机制能够解决上述外扩时再重开；本方向不保留 `HOLD`。
