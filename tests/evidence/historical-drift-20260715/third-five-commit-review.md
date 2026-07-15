# 第三次五提交检查点

检查范围：`a7bc0b9..633a89e`。本检查点在首个产品候选修改前完成，只核对严格同模型 A/B 证据、盲审映射、留出任务和工程回归。

## 范围与时序

- 五个提交的修改均位于 `tests/evidence/`，没有修改 Skill、README、版本号、运行时或发布面。
- Git 时序为：先在 `86b0f9e` 固定自然触发的 1.5.14 成稿和匿名盲包，再在 `e74d4d3` 固定四份 verifier 报告，最后在 `009336c` 揭示映射并汇总结论。
- 独立 review 程序比对 8 个任务，盲包中的 prompt、A 稿和 B 稿与固定 prompt、对应原稿 24/24 逐字一致。
- 汇总中的 4/8 Skill 共识、1/8 无 Skill 共识、3/8 分歧，以及“没有一题获得两名 judge 共同判定全面领先”的结论，与原始判词和映射一致。

## 发现与处置

独立 review 发现 H09 原 prompt 写“保留两个日期”，材料实际包含 7 月 18 日、7 月 21 日、7 月 25 日三个办理节点，verifier rubric 也要求三个节点。若不修正，H09 的三模型结果均应按预设规则作废。

该矛盾在产品修改前修正为明确保留三个办理节点，rubric 无需改动。修正后重新检查：

- prompt 编号 H01—H12 共 12 个，编号唯一；
- rubric 行 H01—H12 共 12 行，编号唯一；
- prompt 与 rubric 的任务集合一致；
- H09 prompt 与 rubric 均明确 7 月 18 日、7 月 21 日、7 月 25 日三个办理节点；
- `git diff --check` 无错误。

留出集有 10/12 个任务带精确篇幅要求，且多个任务显式给出事实和未决边界。它适合检验本轮过度压缩、事实保真和文种功能，不单独代表所有普通写作场景。后续 80%—90% 质量结论须同时报告任务构成，不把本压力集外推为全场景胜率。

## 工程回归

- `python -m unittest discover -s tests -v`：174/174 通过。
- `python .\tools\run_real_prompt_ablation.py --baseline-root .\output\release-baselines\github-1.5.13-cold-audit --baseline-label baseline-1.5.13 --current-root . --out .\output\checkpoint3-vs-1.5.13-20260715`：baseline-1.5.13 108/108，current 108/108。
- `C:\Users\admin\AppData\Local\Programs\Python\Python313\python.exe .\evals\official-writing\run_eval.py --suite smoke --judge-batch-size 2`：20/20 通过，0 failed，0 errors；Promptfoo 提示本机 0.121.11 低于 0.121.19，但未影响本轮结果。
- `git diff --check a7bc0b9..633a89e`：无错误。

## 检查点结论

H09 矛盾修正并重新冻结后，没有发现阻断候选 A 的证据问题。下一步可只解除“宁可短写”的过高优先级，保留事实不外扩、显式事实完整覆盖和文种功能，不改变任务路由、reference 加载条件、复核轮次或输出模式。
