# 1.5.4 深度 review 与真实写稿 A/B 记录

日期：2026-07-09

本轮目标：使用隔离 subagent 重新做一次深度 review，不复用既往 review 结论；对 finding 先复现再选择接受或拒绝；禁止脚本硬清洗、一例一修和默认阻断；达到三次以上共性问题才尝试修改；每次实质 reference 修改必须与 1.5.4 基线做确定性消融和真实写稿 A/B。

## 基线

- 当前工作树起点：`42e7b08`
- 1.5.4 基线：`output\release-baselines\local-1.5.4-48f3190`
- 基线提交：`48f3190b704e0486f09e5b44f4c6a1e3efc91bcd`

## 隔离 subagent

- 冷审 reviewer：`019f44f2-c729-7ec2-9962-3343180d5f9d`
- 首轮 baseline writer：`019f44f3-5ed3-7591-903c-405227879a94`
- 首轮 current writer：`019f44f3-d46a-7ad1-b47e-1703ec9acd0b`
- 首轮 verifier：`019f44f6-bbcc-7670-8925-ab958dcbd84a`
- post-fix baseline writer：`019f44fb-083f-7db0-b8e9-b09df951a945`
- post-fix current writer：`019f44fb-8c5c-77b1-a759-e6bed3dc75c2`
- post-fix verifier：`019f4500-f7ae-7462-a43d-ad38f4c4ac34`

## 冷审结论

冷审未发现高严重度问题。接受 1 项最小修复，拒绝或暂缓 3 项：

- 接受：`references/workflow.md` 的“事实充分性软处理”段落单行过长，包含事实不足、待确认、字段式材料、稀疏材料、二次修改、会议纪要/讲话等多组规则，存在弱模型检索和注意力风险。最小修复方式是只拆成短 bullet，不新增语义规则。
- 暂缓：P065-P071 低频法定文种 deterministic 测试偏触发词检查。源码 reference 支撑存在，且本轮真实 A/B 已覆盖通告、意见、决定、决议、议案、公报、命令；没有出现三次以上同类失败，本轮不改测试结构。
- 拒绝立即修改：description 中 `AI 算力` 有潜在误触发面，但 SKILL 和 reference 已限定为正式材料任务，未复现误触发，不扩写 description。
- 拒绝立即修改：`prose_lint --strict` 默认 `fail-on low` 可能被误用，但当前文档说明和测试自洽，不构成本轮缺陷。

## 首轮真实 A/B

首轮 30 类文种/正式材料真实 prompt 覆盖 description 中声明的主要任务类型：申请、请示、报告、通知、通告、意见、决定、决议、议案、公报、命令、函、复函、批复、说明、方案、纪要、公告、公示、通报、征求意见函、工作要点、总结、调研、讲话、致辞、采购公告、可研、审查材料、只审不改。

首轮 verifier 判定 current 相对 baseline 达到三次以上共性问题：

- 材料不足时补入未给事实、判断或工作安排：10 例。
- 把“拟、待补、未给、待确认”写成更确定的执行口径：5 例。
- 低频或正式文种套普通执行要求导致文种边界变硬：3 例。

据此允许尝试最小修复，但禁止逐项补丁。

## 最小修复

仅修改 `chinese-official-writing/references/workflow.md`：把既有“事实充分性软处理”超长段落拆成短 bullet，保持原语义，不新增硬阻断、不新增脚本清洗、不新增 lint 规则、不改变默认联网和工作流阶段。

同步镜像：

- `skills/chinese-official-writing/references/workflow.md`
- `.agents/skills/chinese-official-writing/references/workflow.md`
- `.qwen/skills/chinese-official-writing/references/workflow.md`
- `hermes/skills/chinese-official-writing/references/workflow.md`
- `openclaw/skills/chinese_official_writing/references/workflow.md`

## post-fix 真实 A/B

post-fix 继续使用 30 类相同 prompt；baseline writer 只读 1.5.4 基线，current writer 只读当前候选，verifier 只看 prompt 与两组输出，不读仓库和历史结论。

verifier 总体结论：`WARN`。

current 独有或更重的回退点：

- G08：补入“符合当前工作实际和年度目标要求”等会议评价判断。
- G12：补入“逾期未反馈视为无意见”。
- G13：写成“已根据当前系统情况开展对接”，偏已发生事实。
- G16：增加后续复核、确认、跟踪等轻微处置链条。
- G29：扩展为“可进入下一步核查流程”“报价真实性、口径一致性”等办理判断。

共同风险：

- G18、G27：两边都没有真正写清提交方式和联系人，而是用了占位式表达。
- G19：两边都没有具体异议渠道和联系电话。
- G21：材料未给反馈期限、邮箱和联系人时，两边都未能“写清”，只能占位或提示补齐。
- 部分样稿存在说明性文字混入正文的共同风格风险。

verifier 判断：未发现 current 独有且达到三次以上的同类功能性回退；不建议继续修改，不需要回滚；建议保留 workflow 拆分。

## 确定性消融

命令：

```cmd
C:\Users\2\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe .\tools\run_real_prompt_ablation.py --baseline-root output\release-baselines\local-1.5.4-48f3190 --baseline-label baseline-1.5.4 --current-root . --out output\real-prompt-vs-1.5.4-deep-review-workflow-split
```

结果：

- baseline-1.5.4：95/95 通过
- current：95/95 通过

## 发布前最小验证

已运行：

```cmd
C:\Users\2\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m unittest tests.test_skill_boundary tests.test_real_prompt_ablation
C:\Users\2\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m unittest discover -s tests
C:\Users\2\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe evals\official-writing\run_eval.py --suite smoke --judge-batch-size 2
C:\Users\2\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe .\tools\run_real_article_eval.py --out output\real-article-deep-review-1.5.4-workflow-split
C:\Users\2\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe C:\Users\2\.codex\skills\.system\skill-creator\scripts\quick_validate.py chinese-official-writing
git diff --check
```

结果：

- 定向 unittest：43/43 通过。
- 全量 unittest：107/107 通过。
- promptfoo smoke：20/20 通过；skill_win_rate 1.0，judge_consistency_rate 1.0。
- 真实样文回归：skill 平均差异率 0.00%，关键词命中率 100.00%；存在占位词风险样本，作为人工复核观察项。
- quick_validate：`Skill is valid!`
- `git diff --check`：通过，仅有 Windows 换行提示。

## 结论

本轮只接受并落地 1 项最小 reference 结构修复：拆分 workflow 事实充分性长段。真实写稿 A/B 没有发现 current 相对 1.5.4 的三次以上同类功能性回退，因此保留修改，不继续补丁式追加规则。剩余问题均记录为观察项，不作为本轮继续修改依据。
