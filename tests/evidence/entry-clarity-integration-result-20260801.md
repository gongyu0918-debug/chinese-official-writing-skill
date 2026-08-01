# 入口清晰度原子组合回归结果

## 结论

PASS，可合入当前本地 main。组合候选只整合七个已分别通过的入口原子，canonical `SKILL.md` 由 10,678 个规范化字符降至 10,145 个，净减 533 个，约 4.99%。工程门全部通过；组合真实 A/B 解盲后为 Candidate 1 胜、1 难分，没有事实、数字、日期、对象、事项、格式、占位、引用、输出模式或正文外说明回退。

该结果证明“减载且不劣于固定 1.5.32”的发布前资格，不把两道短测包装成整体写作质量胜率。

## 固定对象

- 固定基线：`07dd93d79488cd3a07da6ef12afc1e86ead796dd`
- 组合产品提交：`007d1c08`
- 真实测试固定 HEAD：`6975c52a0e5e3327e999f75f495401dfa8f7fcea`，只比产品提交多两道已冻结任务。
- 组合范围：审稿条件正式化、文种权威句去空泛尾巴、评分约束留在复核叶、占位与 Markdown 重复反例删除、引用／数据规则留在复核叶、样式 catchall 由精确路由替代，以及删除组合后为空的“常见错误反例”标题。
- 明确未改：文后提示链、任务路由、reference 加载条件、复核顺序、脚本、版本号和发布链。

## 原子证据汇总

| 原子 | 产品提交 | 定向真实结果 | 判定 |
| --- | --- | --- | --- |
| 引用与数据长规则下沉 | `f29c5e92` | 2 难分、1 Baseline 小胜；负项是无因果的细节量差异 | PASS |
| 社区模板尾句删除 | `3b5c29e7` | 1 难分、1 Baseline 小胜；文种和行文关系均正确，标题差异无因果 | PASS |
| 0—100 评分约束留在复核叶 | `55dbd574` | Candidate 2 胜；不主张 17 字删除带来稳定质量因果 | PASS |
| “审一下”入口正式化 | `7b6e6011` | 2 难分；口语审稿与“审后直接改写”均正确路由 | PASS |
| 未完成占位重复反例删除 | `9a433b4f` | 2 难分；占位和日期状态 2/2 通过 | PASS |
| Markdown 重复反例删除 | `7b0cc606` | 两题两侧字节一致 | PASS |
| 样式 catchall 删除 | `d89a2fc5` | 解盲后 Candidate 1 胜、1 难分 | PASS |

“审一下”来自 Agent 构造的兼容性测试 prompt，不是经核验的真实用户语料。本轮只证明正式条件式没有丢失这类口语理解，不估计真实用户使用频率。

## 组合真实 A/B

### 运行条件

- Candidate 与 Baseline 逐字读取相同 IR01、IR02 原始任务，每题只保留首个技术有效输出，没有补抽。
- 两侧精确模型部署名与 thinking 档位均未暴露，记为 `unavailable`。
- Candidate 两稿生成后，一次递归文件名检查显示了 Baseline 下三个文件名，但没有打开或读取内容；该事后元数据暴露不可能影响已完成首稿，仍如实记录。

### 结果

- IR01 只审不改：两稿均只输出位置、风险层级和建议，不评分、不重写；均识别 Markdown 标题与联系人占位，保留引号原话。匿名映射 A=Baseline、B=Candidate，judge 判 B 胜，Candidate 额外识别主送对象应单列的问题。
- IR02 正式改稿：两稿均保留对象、事项、8月12日17时前、邮箱、王宁和电话，清除 Markdown、口语和正文外说明。匿名映射 A=Candidate、B=Baseline，judge 判难分。
- 总体：PASS，Candidate 1 胜、1 难分，无硬回退。

### 稿件哈希

- Candidate IR01：`BC47FAC59A2A6373AF56CD523E4DCC33670B717FC1F668ED58149EAE08BC24A5`
- Candidate IR02：`9E8DD393125C5C7C3BEB45089725F574D991EACF18117D7BF27A6FF1361764A6`
- Baseline IR01：`75067DEE566150E8D2590CEB0592FA804D64828934F78EB5269B1319AE629470`
- Baseline IR02：`7358C1DB0ACCFC80013E97E122090AB7B78E928E5CE96D62455985D59DCFB4FC`

原始稿与 trace 保存在忽略目录 `output/entry-clarity-integration-real-ab-20260801/`。

## 文后提示链复核

固定基线另做四模式首稿 sanity：

1. 只输出正文：无文后提示、无占位；
2. 明确允许一条待确认：只附反馈邮箱和联系人；
3. 无显式输出限制且存在办理实质缺口：正文后短列一条；
4. 材料完整：无缘故附注。

四题均通过。因此“按用户允许的输出范围说明”与下一条正文-only规则虽然静态上相邻、读感较密，但没有复现左右冲突。本轮保留这条历史承重链，不采纳旧 `1633306a` 的广义“必须显式允许才可提示”改法。

## 工程验证

- `python -m unittest discover -s tests`：412/412 通过。
- `npm run eval:official-writing:smoke`：20/20 通过，0 failed，0 errors。
- `python tools/run_real_prompt_ablation.py ...`：固定 1.5.32 111/111，Candidate 111/111。
- `python .../skill-creator/scripts/quick_validate.py chinese-official-writing`：通过。
- `python tools/sync_adapters.py`：canonical 已同步至五份发行镜像。
- `git diff --check`：通过。

## 外部审计处理

- 修正版 scene-lint RAR 仍为 `NEEDS-REPAIR / NO MERGE`：外部 3/5 正例召回、3/8 误报；本仓库窄规则原型 5/5、0/8，但缺真实归档正例，继续保留研究线，不混入本轮。
- 外部入口精确审计中的 H1 不是方向冲突：入口“压到限制内”是硬上限，reference 的 5%—10% 余量是上限内安全子集。H2/H4 属高熵静态观察，尚无 P0 运行证据；字段与日期重复中包含轻量路由承重项，不能按逐字重复直接删除。
- 外部报告声称存在 `tests/evidence/skill-entry-precise-audit-20260801.md`，但当前 main、全 Git 历史和已检 worktree 均未找到该原始证据，相关 P0 结论不直接采信。

## 剩余风险

- 审稿模式主句仍较长，但历史整体拆行曾出现 mixed／回退；下一轮如继续，只拆独立子条件并沿用因果口径。
- 本轮真实 A/B 的精确模型与 thinking 不可核验，因此不能声称严格同模型语言胜率；硬能力、字节一致样本、工程门和匿名比较均可复核。
- 样式 catchall Candidate 的一次优势可能包含 reference 实际读取差异，按无回退净减载保留，不夸大为稳定质量增益。
