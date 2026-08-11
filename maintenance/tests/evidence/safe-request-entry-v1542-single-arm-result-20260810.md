# 短事务采购入口候选单臂真实质量验证结果

## 结论

结果为 `TECHNICAL_FAILURE`，本轮没有取得任何可审计的模型首 final，不能据此判断候选成稿质量、硬要素或紧凑/展开形态。候选不因本轮获得真实写作通过结论。

- 候选产品提交：`a8a5c4e70bda422833bdee08fb9a068cbfba7583`。
- 预注册提交：`82b7a0f2f2446f18750fcac456037a7b6022604a`。
- 运行目录：`C:\Users\admin\Documents\Codex\runtime-evidence\safe-request-entry-v1542-20260810`。
- 固定参数：Alibaba Token Plan `alibaba-token-plan/deepseek-v4-flash-0731`、Ollama Cloud `ollama-cloud/deepseek-v4-flash:0731`，均请求 `reasoning=max`；每 provider 每场景仅一次，`retries=0`。

## 真实运行记录

运行器在每次模型调用前由 `agent_writer._single_prompt("skill", ...)` 自动取得 selected paths，并把完整 prompt 通过标准输入交给独立外部运行时。12 次调用均在启动器阶段失败：`powershell.exe -File C:\Users\admin\AppData\Roaming\npm\codex.ps1 exec ...` 立即以 return code `1` 退出，stderr 为 PowerShell 对无效 `name` 参数的拒绝。单次耗时约 0.22 秒，无模型输出、无 final 文件；因此可确认失败发生在首 final 之前，但不能将其标为任何模型或产品失败。

| provider | R1 | R2 | R3 | R4 | R5 | R6 | 首 final |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Alibaba Token Plan | TECHNICAL_FAILURE | TECHNICAL_FAILURE | TECHNICAL_FAILURE | TECHNICAL_FAILURE | TECHNICAL_FAILURE | TECHNICAL_FAILURE | 0/6 |
| Ollama Cloud | TECHNICAL_FAILURE | TECHNICAL_FAILURE | TECHNICAL_FAILURE | TECHNICAL_FAILURE | TECHNICAL_FAILURE | TECHNICAL_FAILURE | 0/6 |

按预注册“首 final、零重试、技术失败不补抽”的约定，未改变命令、未改用其他模型、未重跑任何场景。原始 `run-status.json`、逐调用 trace 和运行元数据保留在上述外部目录；`run-status.json` 记录 12 项技术失败、0 个 final，记录完整性检查为 `PASS`。

## 自动路由核验

模型未启动不影响对候选 `agent_writer._reference_paths_for_genres` 的实际调用验证。R1、R3、R4、R6 均选择：

`SKILL.md` → `information-selection.md` → `genre-playbook-request.md` → `workflow.md` → `handling-elements.md` → `argument-chains.md`。

R2、R5 均选择：

`SKILL.md` → `information-selection.md` → `genre-playbook-request.md`。

12 条运行记录均未加载 `references/task-route-cards.md` 或 `references/genre-playbooks.md`。因此，固定矩阵中的复杂/轻路由分流和请求叶子选择已通过静态调用链核验；这不是模型成稿质量的替代证据。

## 未执行的审计与剩余风险

因没有首 final，数字、状态、字段保留、输出范围以及 R2/R5 紧凑与 R1/R3/R4/R6 展开形态均为 `NOT_RUN_NO_FINAL`。如恢复验证，必须另行预注册新的 run，明确记录修正后的启动命令和新的首 final 规则；不得将本轮 12 个技术失败当作可重试样本。
