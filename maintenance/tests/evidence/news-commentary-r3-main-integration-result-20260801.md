# 新闻评论 R3 当前 main 组合验证结果

日期：2026-08-01

## 结论

`ENGINEERING PASS + 3/3 ANONYMOUS BENEFIT`。产品提交 `ba59011f` 只在新闻评论叶的既有一次局部复核句末追加一条证据强度检查，六份产品 blob 与既有 R3 终态 `dda6f156` 完全一致。工程门全部通过；既有三对匿名 A/B 均由 Candidate 胜出，支持交由主任务决定是否合并。

本分支不合并 main、不改版本号、不发布。

## 提交与产品边界

- 固定本地 main：`6bd6c676`。
- 预注册：`1b6b94bd`。
- 产品：`ba59011f`。
- 证据校正：`27e27bfb`。
- 唯一产品语义：在 `references/genre-playbook-news-commentary.md` 的“一次局部复核”句末增加“评论推演逐句核对事实依据和适用范围，只修改判断强度超过材料支持的句子”。
- 入口、新闻评论路由、读集、篇幅规则、其他文种、脚本、修改次数、回退和发布链均未改变。

canonical 与五份发行镜像的目标文件 Git blob 均为 `662104ea0ba040911d0815a8db5c02e2c3247e1f`，与 `dda6f156` 对应文件逐一相等；工作区 SHA-256 均为 `D824671A50AD19FCE536B92295F770897A0179D7FFBE0FE64870683C8F9D270A`。

## 父节点差异校正

R3 产品父节点 `6ee7732c` 仍保留过一条 R2 的枚举式表述，不能当作当前 main 的逐字副本。本次没有移植该父节点，也没有 cherry-pick R1/R2 历史。

真实比较的两臂保持为：

- Baseline：固定 main `6bd6c676`；
- Candidate：终态新闻评论叶 `dda6f156`，即本组合产品 `ba59011f` 的同一 blob。

`6ee7732c..6bd6c676` 在 `SKILL.md`、`tools/agent_writer.py`、`tools/run_real_prompt_ablation.py` 及对应路由断言范围内无加载条件差异。父节点残留已从组合产品与证据归因中排除。

## 工程验证

| 验证 | 结果 |
| --- | --- |
| `python -m unittest discover -s tests` | 405/405，PASS |
| `npm run eval:official-writing:smoke` | 20/20，PASS；Promptfoo 版本更新提示不影响本次结果 |
| 固定 main 确定性消融 | Baseline 110/110，Candidate 110/110 |
| `python C:\Users\admin\.codex\skills\.system\skill-creator\scripts\quick_validate.py chinese-official-writing` | `Skill is valid!` |
| 两项镜像一致性单测 | 2/2，PASS |
| 六份新闻评论叶哈希 | 全部一致 |
| `git diff --check` | PASS |

确定性消融输出：`output/news-commentary-r3-main-integration-ablation-20260801/summary.md`。该测试不调用 LLM，只证明包、路由和评估入口无回退。

## 既有真实 A/B 复核

编排层指定 `gpt-5.6-terra/high`，但落盘 writer 回执没有独立暴露精确模型和档位：Candidate 只记录“GPT-5（运行环境公开标识）/档位 unavailable”，Baseline 记录 model/tier unavailable。因此模型精度属于二级证据，不能把本轮写成“仅凭仓库产物即可独立复现精确模型档位”的实验；遵照预注册不重跑、不补抽。

以下字段可由原始产物独立核验：三题输入 SHA-256、四文件读取顺序、每臂各生成一次、修订 0、补抽 0、六份成稿输出哈希和匿名 A/B 映射。哈希复核结果：

- NC01：A=Candidate，B=Baseline；
- NC03：A=Baseline，B=Candidate；
- NCC05：A=Candidate，B=Baseline。

匿名盲审结果：

| 任务 | Candidate / Baseline 目标风险 | Candidate / Baseline 去空白字符 | 结论 |
| --- | ---: | ---: | --- |
| NC01 社区托管 | 1 / 3 | 855 / 976 | Candidate 中等胜 |
| NC03 共享实验室 | 3 / 4 | 973 / 1086 | Candidate 小胜 |
| NCC05 技改咨询 | 0 / 1 | 1026 / 1141 | Candidate 中等胜 |

Candidate 目标风险合计 4 处，Baseline 合计 8 处；双方 P0 保护性外扩均为 0。三题日期、数字、主体、材料状态、新闻评论文种和输出范围均保真。该收益与唯一 diff 的作用位置一致，且不是由 R2 枚举式起草规则产生。

## 剩余风险

1. 精确模型和 thinking 没有在 writer 原始回执中独立落盘；本轮只能把编排层指定值作为二级证据。
2. NC03 的 Candidate 仍有 3 处推演强度偏高，规则降低了频次，没有消除全部风险。
3. NC03、NCC05 仍高于“约 800 字”的常用容差；该问题不由本原子新增，也不在本分支继续调词。
4. 本结论只覆盖新闻评论叶相对当前固定 main 的单变量组合；与工作总结拆分、篇幅余量原子等其他候选的联合作用尚未验证。

综合判定：保留 `ba59011f`，交由主任务做最终组合回归；不在本分支追加规则。
