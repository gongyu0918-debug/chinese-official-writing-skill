# 弱模型低思考真实写作测试记录（2026-07-07）

## 背景

本轮测试在 `be46036 fix: tighten official writing playbook boundaries` 之后进行，目标是复查弱模型低思考下是否仍会出现：

- 把“考察、建议、拟测试、下一步设想”写成已定实施方案或执行命令；
- 把正文外待确认、风险提醒或核验提示写成正文章节；
- 文种过拟合，例如“使用报告”被写成“调研报告”，“成本考察”被写成“考核说明”；
- 改稿时为了正式化新增原文没有的事实；
- 只审不改或正式正文残留 Markdown `**`、代码块、`###` 等格式噪点；
- 长篇限字稿头重脚轻或草草收尾。

本轮只使用 prompt/reference 层判断，不新增脚本清洗，不把单个样本做成硬规则。只有累计三次以上共性问题才进入最小修复。

## 已跑样本

| 样本 | 模型与思考强度 | 场景 | verifier 结论 | 主要问题 |
| --- | --- | --- | --- | --- |
| A | `gpt-5.3-codex-spark` / low | 版慎通成本考察 | WARN | 标题从“成本考察”漂移为“考核说明”；有 Markdown 加粗；防滥用表述偏硬。 |
| B | `gpt-5.4-mini` / low | 版慎通成本考察 | PASS | 标题贴题，要点完整，建议边界保持较好。 |
| 1 | `gpt-5.3-codex-spark` / low | 成本考察短稿 | WARN | “建议尝试、待测试项”收束成偏明确治理口径。 |
| 2 | `gpt-5.4-mini` / low | 版慎通使用报告 | PASS | 未写成调研报告；负面问题和可用价值较平衡；正文外补充未编号成章节。 |
| 3 | `gpt-5.3-codex-spark` / low | 结构锁定改稿 | FAIL | 新增“重复计入或遗漏计入”“影响负荷研判”等原文未给推演。 |
| 4 | `gpt-5.4-mini` / low | 只审不改 | FAIL | 输出用了 Markdown 加粗标签；对日期作了额外推断。 |
| 5 | `gpt-5.3-codex-spark` / low | 900 字以内内部汇报 | WARN | 把治理设想写成“按以上方案执行、一周内反馈”等执行要求；有 Markdown 加粗。 |

## 共性统计

按用户要求，本轮采用累计口径，不做一例一修：

- 达到三次：建议/待测试项被弱模型写成偏既定方案或执行要求。样本 A、1、5 命中。
- 达到三次：Markdown 加粗或格式包装影响正式交付。样本 A、4、5 命中。
- 未达到三次：事实边界越界、把推演写成事实。样本 3、4 命中，继续观察。
- 未达到三次：标题/文种漂移。样本 A 明显命中，样本 1 控制较好，继续观察。
- 未复现：正文外待确认或风险提醒被编号成“第七章”等最后正文章节。
- 未复现：长篇限字稿头重脚轻或草草收尾；样本 5 结构完整，但建议边界偏强。

## 本轮采纳

采纳两项软性最小修复：

1. 对“考察、评估、建议、拟测试、考虑尝试、下一步设想”增加建议/待评估口径提示；没有正式决定、责任单位和期限时，不写成已定实施方案、执行命令、具体反馈时限。
2. 对“只审不改”和用户指定“位置 + 风险层级 + 修改建议”的场景，要求用普通文本标签承接，不用 Markdown `**` 加粗包装标签。

不采纳事实外扩新增规则。本轮事实外扩只有两次，且现有 `SKILL.md`、`workflow.md`、`review-checklist.md` 已有“只压实原文事实、不新增未给判断”的规则，先继续观察，不再叠加一例一修。

## 修复后复测

修复后追加 3 个真实写作/审稿样本：

- `gpt-5.3-codex-spark` / low：版慎通成本考察短稿。输出标题贴近“成本考察”，未使用 Markdown 加粗，末尾写明“尚属优化方向建议，未进入定稿执行阶段”，未再写成执行命令。
- `gpt-5.4-mini` / low：只审不改通知。输出保持“位置、风险层级、修改建议”，未重写全文，也未使用 Markdown `**` 加粗包装标签。
- `gpt-5.5` / medium：强模型内部汇报稿对照。输出完整成稿，使用“拟、评估、逐步形成”等建议口径，未变成过度保守的待确认清单，也未编造已节省金额或已上线成果。

结论：本轮软性收紧对弱模型两类共性问题有改善；强模型未出现明显过拟合或功能性回退。事实外扩仍列为观察项，不在本轮新增规则。

## 验证命令

- `python -m unittest tests.test_real_prompt_ablation tests.test_skill_boundary`：42 tests passed。
- `python -m unittest discover -s tests`：106 tests passed。
- `python .\tools\run_real_prompt_ablation.py --baseline-root output\release-baselines\github-1.5.2 --baseline-label baseline-1.5.2 --current-root . --out output\real-prompt-vs-1.5.2-weak-model-boundaries`：baseline `85/90`，current `90/90`；baseline 只在 P086-P090 新增/后续用例失败。
- `npm run eval:official-writing:smoke`：PowerShell 执行策略拦截 `npm.ps1`。
- `npm.cmd run eval:official-writing:smoke`：启动成功，但脚本内部 `python` 不在 PATH。
- 等价 smoke：`python evals\official-writing\run_eval.py --suite smoke --judge-batch-size 2` 使用 bundled Python 并提权访问 npm registry 后通过，20/20，skill win rate 1.0，judge consistency 1.0。
- `git diff --check`：通过，仅有 Windows LF/CRLF 警告。

## 后续观察项

- 如果“事实推演写成事实”再出现一次，应优先复查现有规则是否太分散，而不是继续追加长句。
- 如果强模型在成本治理类文稿中变得过度保守、只输出待确认事项、不成稿，说明本轮建议边界收得过紧，应回滚或改软。
- 下次发布前，真实写稿实测仍需同时覆盖弱模型低思考和强模型普通写作，防止弱模型优化导致强模型过拟合。
