# 算力附加页组合 A/B 试跑记录（2026-09-12）

## 结论

本次是技术有效、质量不通过的试跑，不支持合并结论。候选和当前 `main` 均完成同题写稿，候选读取 9 次、基线读取 10 次；但两臂都输出了路由/参考页说明和正文外提示。该洁净度问题不能归因于候选独有规则，先归为共有模型或交付契约执行问题，继续修正入口契约后重跑。

## 固定条件

- 题面、输出要求、输入快照和客户端版本相同；
- writer：`alibaba-token-plan/qwen3.8-flash`，配置 `max`，0 retry；
- 隔离只读快照，不执行脚本，不启用 Hook；
- baseline：`main@1ce7112303172478faa2392667a2de1098eb912c`；
- candidate：`04bb55d505367a2046c6e201cfa0d1a4b9678ae6`；
- 两次 receipt 均为 `COMPLETE`，读取均在快照内。

## 读取与输出

基线读取：`SKILL.md`、`reference-index.md`、`information-selection.md`、`task-route-cards.md`、`ai-compute-docs.md`、报告叶、`argument-chains.md`、`anti-ai-patterns.md`、`proofreading-checklist.md`、`formulaic-language.md`。

候选读取：`SKILL.md`、`information-selection.md`、`reference-index.md`、报告叶、`ai-compute-docs.md`、`argument-chains.md`、`formulaic-language.md`、`anti-ai-patterns.md`、`final-review-layers.md`。

基线正文 SHA-256：`071e7d46f7dcbd6a14a3f2fc574301cba6997baffbe5f40c2c096b9f477d1cc2`。

候选正文 SHA-256：`66f49bc15d06e792e8b2842ec2c712ec784ecd9c2f6320b8aa265972ec7c7cee`。

两臂都保留了给定的“拟开展”和“拟核对”状态，没有观察到候选独有的事实升级；但两臂均违反了只输出正文的交付形态，因此本对照只证明读取集合和技术可用性，不证明质量通过。
