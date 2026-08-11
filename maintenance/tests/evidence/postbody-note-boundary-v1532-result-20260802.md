# 文后提示边界审计与编号检测结果

## 结论

Prompt 交付链当前可用，检测层补强具备合并资格。

当前 main 的四模式真实 sanity 均通过：只输出正文时无附注；明确允许一项时只附该项；未限制正文外内容且存在办理实质缺口时短列；材料完整时不附注。现有归档没有复现“待确认事项、风险提醒或核验提示被编号成正文最后一章”。

确定性复放发现 `prose_lint.py --delivery-mode draft-body` 原先只能识别无编号或 Markdown 标题，漏掉 `七、待确认事项`、`第七章 待确认事项`、`2. 待确认事项` 和 `（二）待确认事项`。产品提交补齐这四类标题，同时保留合法业务标题反例。

## 固定对象与实现边界

- 固定基线：本地 `main=5ed38350c2ac10ac83ea81b5f6d3ec7c04462012`。
- 产品提交：`5aac7f12`。
- `SKILL.md`、`information-selection.md` 和 `review-checklist.md` 决定何时允许提示、提示内容和提示位置。
- `prose_lint.py` 是可选、只定位、不改稿的复核工具；只有显式使用 `--delivery-mode draft-body` 时，正文外提示残留才作为 high 级 `unexpected-external-note`。
- 宿主 Hook 不是本轮判断前提，也不是所有平台的统一强制出口。

## 当前提示条件

允许文后提示需同时满足：

1. 输出模式允许。正文-only、只输出改后稿或不解释时不附提示；用户只允许某一类提示时只附该类。
2. 内容确实影响文种成立、请批事项或执行落地。外围信息和不影响办理的缺项省略。
3. 少量短列，正文已承载的调查、核查、研究等未定状态不在文后重复。
4. 标题不编号成正文最后一章。

## 现有证据

- 当前 main 的 OS01—OS04 四模式结果均通过，见 `tests/evidence/entry-clarity-integration-result-20260801.md`。
- 历史 `weak-model-low-reasoning-20260707.md` 曾登记“正文外提示编号成第七章”的风险，但后续复测未复现。
- 1.4.4 曾出现泛化截止时间、指定渠道、联系人等缺项进入正文的相邻问题；当前四模式复验未重现，不能把旧问题直接当作 1.5.32 当前故障。

因此本轮没有向写作 Prompt 追加同义禁令，也没有重生成四模式稿件；只修复已经可以用正例和合法反例稳定区分的检测盲区。

## 检测补强

新增命中：

- `七、待确认事项`
- `第七章 待确认事项`
- `2. 待确认事项`
- `（二）待确认事项`

新增 clean 反例：

- `一、待确认事项办理情况`
- `第二章 补充信息管理办法`
- 正文句 `经核查，待确认事项已全部确认。`

上述反例在 `draft-body` 模式下均不产生 `unexpected-external-note`。

## 工程验证

- 定向回归：134/134 通过。
- `python -m unittest discover -s tests`：413/413 通过。
- `npm run eval:official-writing:smoke`：20/20 通过，0 failed，0 errors。
- `python tools/run_real_prompt_ablation.py ...`：固定 main 111/111，Candidate 111/111。
- `python .../skill-creator/scripts/quick_validate.py chinese-official-writing`：通过。
- `python tools/sync_adapters.py`：canonical 已同步至五份发行镜像。
- `git diff --check`：通过。

## 剩余风险

- 该检查不是全平台自动执行；宿主未调用脚本或未选择 `draft-body` 时，编号提示仍主要依赖 Prompt 与语义复核。
- 脚本只能根据标题形态给线索。若用户明确要求把“待确认事项”作为正文业务章节，仍需 Agent 根据用户意图区分；脚本不会自动删除该章节。
- 本轮没有当前版本的正常任务复现“提示误入正文”，因此只把它定性为检测覆盖补强，不写成已修复当前生成共性故障。
