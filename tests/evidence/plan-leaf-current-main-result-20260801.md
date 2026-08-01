# 方案起草叶 current-main 验证结果（2026-08-01）

## 裁决

`PASS / 可进入本地合并回归`。

方案、实施方案和建设方案从聚合 playbook 物理迁入专叶后，实际命中上下文由 13909 字符降至 11358 字符，减少 2551 字符（18.34%）。当前主线确定性能力未回退；新增自然起草题中，Candidate 明显优于 current main；局部改稿控制题中，Candidate 锁定内容和事实状态均保留。没有发现可归因于拆叶的事实、数字、主体、状态、文种、格式、输出模式或直接修改成本回退。

本结论只支持方案叶单变量进入本地合并回归，不改变版本号，不代表已经发布。

## 固定对象与提交

- 固定 Baseline：`origin/main=cdb74bf92471d8f4979c85d7fafe67eec5c7f6e4`。
- 研究分支：`codex/plan-leaf-current-main-v1532`。
- 预注册：`44df1c4f`。
- 产品提交：`4a481bb0768d04b7b2a324a8c7e1fe981cb5a3f6`。
- A/B 任务冻结：`69f1a66ee98accedba313807e5a68b508b433757`。
- 旧方案叶产品来源：`35f55689bff76d581046c3e443f5fb9247095392`；本轮从 current main 重建，没有直接合入旧分支的证据提交或其他候选。

产品差异严格限定为：新增方案专叶、入口增加直达路由、聚合 playbook 移出建设方案条目、五套镜像同步，以及对应 evaluator、消融和路由测试。没有修改信息选择、事实边界、篇幅规则、复核顺序、脚本、版本号或发布链。

## 工程验证

| 验证 | 结果 |
| --- | --- |
| `python -m unittest discover -s tests` | PASS，410/410 |
| `npm run eval:official-writing:smoke` | PASS，20/20 |
| Skill Creator `quick_validate.py chinese-official-writing` | PASS，`Skill is valid!` |
| current-main 固定确定性消融 | Candidate 111/111；Baseline 110/111，Baseline 只失败于本轮新增 P112 专叶存在性断言 |
| canonical 与五套发行镜像 | PASS，专叶及被迁移聚合页一致 |
| 预注册产品 allowlist | PASS，23/23，无范围外产品文件 |
| `git diff --check` | PASS |

确定性消融只证明路由、文件和检查入口未回退，不代替真实成稿判断。

## 真实 A/B

两题均使用逐字一致原始任务，各臂只取首个完整输出，不补抽、不重写。调度时 writer 均指定 `gpt-5.6-terra/high`；运行 trace 未提供可独立读取的模型与 thinking 回执，因此报告中将精确运行自证记为 `unavailable`，不把调度参数写成模型端自证。

### PL01：常规方案起草

- 输入 SHA-256：`564b4497c50acae13c7306b5f9b3828bec913ea9d0e15770d4f60ad9a4ed0fa9`。
- Candidate 实际读取方案专叶，未读取聚合 playbook；Baseline 实际读取聚合 playbook。
- Candidate SHA-256：`604c3faad82dd2e4b5f02076562b67de066f6e821f9103210b189bb5b91cafd8`；非空白字符 998，六节齐全，lint 为 0。
- Baseline SHA-256：`60f3d34ba7fd7a8bf2b8ab5c97b6a0795b87638e654a370f1c97a2817aeed4fa`；非空白字符 781，六节齐全，lint 为 0，但明显低于“约1000—1200字”。
- 匿名盲审：Candidate 明显胜出。Candidate 的任务链条、记录—处理—复查—汇总衔接和验收闭合更完整，直接修改成本更低；Baseline 因篇幅和展开不足触发硬项失败。
- 观察项：Candidate 的“每个窗口巡检设备包括……”可被理解为把三类设备总数进一步解释成窗口配置关系。盲审认定为轻微信息强化而非数量冲突；单稿单处不作 Prompt 特例修复，保留为后续自然样本观察项。

### PL02：既有方案局部改稿

- 输入 SHA-256：`ae693a11a3913bc212092afe0e3c5e190b0fbcde90d89f0c6a60df72e8ff2138`。
- Candidate SHA-256：`e5bb701e2d62b0426850d4ceaf8d60bfec9df62df0564db119a8147d313f01c0`；Baseline SHA-256：`b60f9f2fc155ff829db45a7c0aa2a1ac2364c43ef9ca99dc7fa299b68827e6b2`。
- 两稿标题及第一、二、五节 4/4 项均与原稿逐字一致；只有第三、四节发生变化；日期、数字、范围、责任主体和状态均保留；两稿 lint 均为 0。
- 匿名盲审：Candidate 小胜，主要来自步骤与职责对应更紧、分句可读性更好；两稿均可直接使用。
- 因果限制：该局部改稿实际没有读取方案专叶，属于非目标控制样本；Baseline 还额外读取了本机已安装的 1.5.20 入口。因此本题只用于确认 Candidate 自身没有非目标硬回退，语言小胜不计入方案叶的严格因果收益。

## 匿名映射与裁决

- PL01：A=Baseline，B=Candidate；盲审 B 明显胜。
- PL02：A=Candidate，B=Baseline；盲审 A 小胜。

按产品因果口径，PL01 提供一项明确正向；PL02 提供一项非目标无回退控制。结合既有旧方案叶工程证据和当前主线重建结果，满足预注册 `PASS` 门。

## 外部 scene-lint 包隔离状态

桌面外部合并包未遗漏，也未混入本候选。独立只读审计结论为 `NEEDS-REPAIR / NO MERGE`：可保留的只有两条 `scene-filler` 检测思路；包内 Git 提交不可核验、Baseline 不完整，且全局规则缺少报告、方案、可研只审的定向回归。该方向继续作为独立后续候选，不影响方案叶结论。

## 剩余风险

1. 严格可归因的最新真实 A/B 只有一题实际命中方案专叶；发布前若方案叶与其他候选组合，应再做一组组合回归，不用本题替代组合证据。
2. 方案专叶逐字继承原聚合页的共享骨架，仍含“事实、数据、样本”等研究型词序；本轮为保持单变量没有改写。
3. PL01 的单处设备分布解释留作观察，不构成三次共性风险，不追加同义禁令或文种特例。
4. 本轮没有真正 No-Skill 对照；结论只相对 current main，不外推为全面优于 No-Skill。
