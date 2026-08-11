# 29 个公文与正式材料入口真实写作证据盘点

## 口径

- `A`：保存了原始用户式 prompt、LLM writer 成稿和独立 verifier 判定，可复核完整链路。
- `B1`：有单文种真实 writer/verifier 结论或成稿摘要，但缺少原始 prompt、完整成稿、逐稿 verifier 中的一项或多项。
- `B2`：只在多文种混合真实 A/B 报告中声明覆盖，没有留下该文种的独立原始三件套。
- 确定性用例、Promptfoo stub、规则文档和办理要素表不计为真实写作证据。

本次只做历史证据盘点，不根据文种名称或规则存在推定已经完成真实测试闭环。

## 结果

| 入口 | 级别 | 可核对证据 |
| --- | --- | --- |
| 申请 | A | `release-1.5.12-writing/prompts.md`、`current-writers.md`、`verifier.md` 的 P3 |
| 请示 | A | `cold-audit-1.5.7-codex-ab-packet-20260712.md` 的 T02 原 prompt、两组输出和盲审 |
| 报告 | A | `release-1.5.12-writing/` 的 P1；另有本轮长文连续改稿原始包 |
| 通知 | A | `release-1.5.8-routing/` 的 B 组 prompt、两名 writer 和 verifier |
| 通告 | B1 | `real-writing-1.4.15-description-routes.md` 仅保存单文种结果摘要 |
| 意见 | B1 | `real-writing-1.4.15-description-routes.md` 仅保存单文种结果摘要 |
| 决定 | B2 | `deep-review-1.5.4-workflow-split.md` 只记录 30 类混合 prompt A/B |
| 决议 | B1 | `real-writing-1.4.15-description-routes.md` 仅保存单文种结果摘要 |
| 议案 | B1 | `real-writing-1.4.15-description-routes.md` 仅保存单文种结果摘要 |
| 公报 | B1 | `real-writing-1.4.15-description-routes.md` 仅保存单文种结果摘要 |
| 命令 | B1 | `real-writing-1.4.15-description-routes.md` 仅保存单文种结果摘要 |
| 函 | B1 | `real-writing-1.4.9-release.md` 有 writer/verifier 结论，未保存完整原始稿 |
| 复函 | B2 | `deep-review-1.5.4-workflow-split.md` 只有混合覆盖记录；`real-article-eval-summary.md` 属工具回归 |
| 批复 | B2 | `deep-review-1.5.4-workflow-split.md` 只有混合覆盖记录；`real-article-eval-summary.md` 属工具回归 |
| 说明 | A | `release-1.5.12-writing/` 的 P4 prompt、两名 writer 和 verifier |
| 方案 | B1 | `real-writing-1.4.9-public-source-5round.md` 只保存任务和稿件摘要 |
| 纪要 | A | `codex-expanded-ab-packet-20260712.md` 的 T07 原 prompt、输出；判定见 `codex-expanded-ab-20260712.md` |
| 公告 | B2 | `deep-review-1.5.4-workflow-split.md` 只有混合覆盖记录 |
| 公示 | B2 | `deep-review-1.5.4-workflow-split.md` 只有混合覆盖记录 |
| 通报 | A | `codex-expanded-ab-packet-20260712.md` 的 T01 原 prompt、输出；判定见 `codex-expanded-ab-20260712.md` |
| 征求意见函 | B1 | `release-1.5.0.md` 有 writer/verifier 摘要，缺完整原始三件套 |
| 工作要点 | B1 | `playbook-architecture-1.5.0-current-sample-outputs.md` 与 follow-up 报告，缺原始 prompt |
| 总结 | B1 | `anti-ai-red-blue-5round-2026-06-30.md` 保存任务和 judge 摘要，未保存完整稿件包 |
| 调研 | B1 | `longform-3000-real-regression-20260706.md` 保存 writer/verifier 结论，未保存完整长稿 |
| 讲话 | B1 | `playbook-architecture-1.5.0-current-sample-outputs.md` 与 follow-up 报告，任务仅为摘要 |
| 致辞 | B2 | `deep-review-1.5.4-workflow-split.md` 只有混合覆盖记录 |
| 采购公告 | B1 | `release-1.5.0.md` 有覆盖和 verifier 摘要，缺完整原始三件套 |
| 可研 | B1 | `longform-3000-real-regression-20260706.md` 保存 writer/verifier 结论，未保存完整长稿 |
| 审查材料 | B1 | `playbook-architecture-1.5.0-current-sample-outputs.md` 与 follow-up 报告，缺原始 prompt |

统计：`A=7`、`B1=16`、`B2=6`，合计 29。没有任何入口完全没有被历史真实 A/B 报告覆盖，但只有 7 个入口保留了可独立复核的完整证据链。

## 研判

仓库可以说“29 个入口均曾进入历史真实 A/B”，不能说“29 个入口均已有完整、可审计的真实写作闭环”。下一轮补证据时先覆盖 `B2` 的决定、复函、批复、公告、公示、致辞，再按实际使用量从 `B1` 中补齐函、方案、可研、采购公告、讲话等原始三件套。补测只完善证据，不预设需要修改产品 Prompt；出现共性失败后再决定是否修复。
