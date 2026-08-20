# UL-005 单稿事实台账 R2：CodeBuddy 最小真实运行

## 运行边界

本轮只运行一条真实 WorkBuddy / CodeBuddy verifier 生命周期；由于模型没有在可接受时间内形成合规 `fact_ledger`，按预注册止损，未继续消耗另外两条在线样本。两条剩余样本仍保留在已提交的确定性测试中：无关 span、局部相关但新增谓语、authority 同 span 透明改写。

| 项目 | 实际值 |
| --- | --- |
| WorkBuddy / CodeBuddy | WorkBuddy 内置 CodeBuddy CLI `2.115.0` |
| 模型 | `deepseek-v4-flash`，`max`，`dontAsk` |
| 宿主候选 | 当前 UL-005 分支组装的 CodeBuddy companion，后将 `hook-capability.json` 选择为 `under_length` |
| session | `cb-ul005-r2-unrelated-20260821c` |
| runner 退出 | 外部止损后 runner exit code `1`；CodeBuddy node 进程已按 session 关闭 |
| Hook record | `phase=under_length_awaiting_verdict`，未进入最终 D0/D1 选择 |
| fact_ledger | 未形成；没有可核验 JSON verifier 回执 |

## 实际 D0/D1

D0（70 字，SHA-256 `506d462cb746a9069e82822d7b15dd4e4aa5c1c674ade48d620cc8c0ffce294d`）：

```text
各科室：

我单位组织业务培训，内容围绕日常业务，按既定计划进行。请各部门统筹工作与学习，参训人员完成学习任务并学以致用，当前安排保持不变。
```

模型生成 D1（142 字，SHA-256 `6b200da360073f1787cf5444337f5bf1ae62821b6112378d2f2e732a34dd3383`）：

```text
各科室：

我单位组织业务培训，培训内容围绕日常业务开展，培训安排按既定计划进行。请各部门统筹好工作与学习，做到工作、学习两不误，合理协调参训人员的工作与学习安排，确保其完成学习任务，并将培训所学内容运用到实际工作中，切实做到学以致用。本次培训的当前安排保持不变。办公室收到三份材料。
```

D1 确实包含预注册的真实但无关 span“办公室收到三份材料”，同时还加入“开展”“统筹好”“做到工作、学习两不误”“合理协调”“确保”“运用到实际工作中”等材料未直接给出的增量。Hook 已把 D1 冻结并进入 `under_length_awaiting_verdict`，但 DeepSeek 在约定时间内未交回带 `fact_ledger` 的 JSON，因此没有把 D1 当作通过，也没有冒充已经完成 D0 回退。

## 原始回执与 hash

完整 PTY 原文（含 CLI 输出、Hook verifier 提示和模型未完成的等待状态）保存在忽略目录：

`output/current-verification/v1612-ul005-fact-ledger-r2/unrelated-c/terminal.raw.txt`

该文件长度 `1924023` bytes，SHA-256 `0E35B9C19347ED6D56612884F653A3D2372768F995EB8F6CB9267F36B7713BFD`。发送输入文件 `input-sent.txt` 长度 `450` bytes，SHA-256 `2E4AB71705CB0825AC1DF9C7F467590B34FE36D69B218BF9E147515054F5FAED`。

CodeBuddy Hook record 原文件路径为：

`C:\Users\admin\.codebuddy\plugins\data\chinese-official-writing-inline\shared-gate-core\candidate-ai-gate-hook\cb-ul005-r2-unrelated-20260821c\workbuddy-1-4b2be96e002b2e35.json`

长度 `3991` bytes，SHA-256 `50BD1A749297317590752EB22DDFB51A46ED46812B446A393A91774E5C5A9AD6`。record 明确保存了 `original`、`candidate`、每个增量的 hash、`phase=under_length_awaiting_verdict`，但没有 `fact_ledger` 或 `selection`。

## 结论

本次真实结果为 `INVALID / HOLD`，不是成功的安全回退证据：模型完成了坏 D1 生成，却没有完成 verifier JSON，因而不能声称“坏稿已由 CodeBuddy 选回 D0”。这同时暴露两个边界：模型需要在复杂增量下逐项生成台账；当前候选对跨 span 关系仍不应宣称已解决。候选不合入 main、不同步付费分支、不发布。继续验证前需先决定是否接受额外 token 成本；本轮不再扩代码或扩大真实测试。
