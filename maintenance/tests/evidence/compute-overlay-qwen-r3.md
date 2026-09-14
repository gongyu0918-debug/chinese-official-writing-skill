# R3 算力报告组合 A/B 证据摘要（2026-09-12）

- 模型：`alibaba-token-plan-2/qwen3.8-flash`
- 参数：客户端 `0.22.0`，`max`，同题同提示，baseline=`main@1ce71123`，candidate=`codex/reference-rewrite-20260912`
- baseline：8 次读取；读取 `SKILL.md`、`reference-index.md`、`task-route-cards.md`、`information-selection.md`、`genre-checklist-report.md`、`ai-compute-docs.md`、`anti-ai-patterns.md`、`argument-chains.md`。
- candidate：6 次读取；读取 `SKILL.md`、`reference-index.md`、`task-route-cards.md`、`information-selection.md`、`genre-checklist-report.md`、`ai-compute-docs.md`。
- 两臂均完成并输出正文；候选未读取反旁白和论证附页，未出现候选独有事实或状态硬回退。
- 候选正文保持“试用”及“拟核对”状态，结构更紧凑；未把试用写成已实施或已验收。
- 该摘要只保存后续组合验证所需证据；本轮不据此宣布功能迁移或合并。
