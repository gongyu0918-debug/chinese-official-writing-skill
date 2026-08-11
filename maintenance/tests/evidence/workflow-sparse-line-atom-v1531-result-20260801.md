# workflow 稀疏句原子减载结果（2026-08-01）

## 结论

**PASS，可进入主线合并候选。**

产品提交 `ee02d9ab1cbe3b29285e4a7a7a2058461a09d41d` 只删除 `workflow.md` 中一条已由入口、信息选择规则和报告叶共同覆盖的稀疏材料说明。每个运行包净减 43 个字符、123 个 UTF-8/LF 字节；六个运行包合计净减 258 个字符、738 字节。文种路由、reference 图和事实边界均未改变。

## 工程证据

- 全量 unittest：405/405 通过；
- Promptfoo smoke：20/20 通过；
- 固定 `21084f3` 确定性消融：Baseline 110/110，Candidate 110/110；
- quick validate：通过；
- canonical 与五份运行镜像：一致；
- `git diff --check`：通过；
- 独立静态 diff review：除预注册目标句和对应断言外，无越界产品改动。

## 真实写稿

固定条件为 `gpt-5.6-terra/high`、逐字同输入、相同 reference 集、各臂一次首稿。WS01 因 Candidate 自然读取了预注册禁止的轻量卡且未完成终审链，整对标记 `INVALID`，不计产品正负，也未补抽。

随后使用三组技术有效稿件：

| 任务 | 场景 | Candidate / Baseline 字数 | 硬核验 | 匿名结果 |
| --- | --- | ---: | --- | --- |
| WS02 | 材料充分报告控制题 | 1207 / 1367 | VALID / PASS | Baseline 小胜 |
| WS03 | 稀疏试运行报告目标题 | 885 / 892 | VALID / PASS | Candidate 小胜 |
| WS04 | 材料充分报告控制题 | 906 / 1055 | VALID / PASS | Candidate 小胜 |

匿名映射为：WS02 `P=Candidate、Q=Baseline`；WS03 `P=Baseline、Q=Candidate`；WS04 `P=Candidate、Q=Baseline`。总计 Candidate 2 胜 1 负。

三题均保留事实、数字、日期、主体、责任、期限、状态、文种、格式和输出范围，没有 Candidate 独有且可归因于删句的 P0、材料外具体承诺或硬回退。WS02 的负点是零增量解释较多，但该题材料充分，被删句只约束稀疏材料；同类表达在两臂和三题均有出现，不能归因于本 diff。直接命中删句适用场景的 WS03 为 Candidate 小胜。

## 决策

该原子满足“真实写作不劣于发布基线、负点须与改动相关”的口径：三题 2 胜 1 负，目标题胜出，唯一负题没有因果联系。保留产品提交，允许在主线组合回归前合并；不追加 Prompt，不扩大测试矩阵。

原始报告：

- `output/workflow-sparse-line-real-ab-20260801/hard-verifier.md`
- `output/workflow-sparse-line-real-ab-20260801/blind-judge.md`
- `output/workflow-sparse-line-extension-ab-20260801/hard-verifier.md`
- `output/workflow-sparse-line-extension-ab-20260801/blind-judge.md`
