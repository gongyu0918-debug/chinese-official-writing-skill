# 1.6.31 有据分析拆分候选

从已发布 `v1.6.30`（`d2f97ba0`）及其发布记录 `73d20160` 建立独立分支 `codex/release-v1.6.31-candidate`。本次只取已合本地 main 的 R25 全局有据分析原子：入口摘要与既有 information-selection 页“事实与分析”小节，原文来自 `a440f97e`，canonical 净增1354字节，同步五套普通镜像。版本元数据更新为1.6.31；现有路由、专叶、脚本、Hook 与 README 使用入口保留。

| 增量 | 本次取舍 |
| --- | --- |
| R25 事实与常识支撑的分析 | 纳入；允许展开有据论证，具体事实及状态仍受材料约束 |
| R26 增项申请专页及其路由 | 留在本地 main，后续单独取舍 |
| R9 发言身份、R10 讲话改稿信息选择段 | 留在本地 main，未混入当前两处文件 |
| HK-002b 来源状态纠正候选 | 按本轮授权另行集成本地 main，不进入1.6.31；原生 Stop 结果单独登记 |

R25 既有真实写稿是12次调用、11份最终回复、10次完整且符合目录范围，四组成对有效。它支持“分析能够展开”的有限结论，不证明整体成功率提高，原有具体事实、分工、包装和超时问题保留。没有为拆版本追加写稿调用。原始结果及失败见[历史结果](../global-grounded-analysis-r25/result.md)、[合并记录](../global-grounded-analysis-r25/integration.md)；120份历史文件从 `f69534f0` 原字节迁移，校验清单见[历史文件清单](https://github.com/gongyu0918-debug/chinese-official-writing-skill/blob/0721297298b72be7a37b93c6598172791b58e421/maintenance/tests/evidence/release-v1631-candidate/historical-evidence-manifest.json)。

候选已冻结。用户随后明确要求1.6.31暂不发布，早上再接续；当前未推送、建tag、创建Release或上传平台，未设置自动发布。根README继续标识已发布1.6.30。早上须从本分支冻结内容接续，不能从届时main整包发布。

验证记录：

- `py -3.13 -B -X utf8 -m unittest discover -s maintenance/tests -p test_*.py`：本候选最终817/817通过，145.011秒，见[最终全量](https://github.com/gongyu0918-debug/chinese-official-writing-skill/blob/0721297298b72be7a37b93c6598172791b58e421/maintenance/tests/evidence/release-v1631-candidate/full-tests-final.json)。另有107项相关检查与五处Skill校验通过；检查命令和完整输出均在本目录。
- [精确范围](https://github.com/gongyu0918-debug/chinese-official-writing-skill/blob/0721297298b72be7a37b93c6598172791b58e421/maintenance/tests/evidence/release-v1631-candidate/scope-check.json)：12份写作文件、7份版本manifest；没有新增或删除产品资产。120份迁移历史文件SHA256全部匹配。[独立冷审](cold-review.md)复核了暂存字节和最终包。
- SkillHub最终包为 `output/release-v1631-candidate/skillhub-final`，88文件；ClawHub包为 `packages/openclaw/skills/chinese_official_writing`，38文件。逐文件清单和清单SHA256见[包汇总](package-summary.json)、[SkillHub](https://github.com/gongyu0918-debug/chinese-official-writing-skill/blob/0721297298b72be7a37b93c6598172791b58e421/maintenance/tests/evidence/release-v1631-candidate/skillhub-manifest.json)、[ClawHub](https://github.com/gongyu0918-debug/chinese-official-writing-skill/blob/0721297298b72be7a37b93c6598172791b58e421/maintenance/tests/evidence/release-v1631-candidate/clawhub-manifest.json)。最终包均完成发布命令的dry-run，本轮正式提交次数为0。

首次全量的两处失败来自Windows checkout：root LICENSE为CRLF，而产品文件已恢复Git原字节LF。恢复root LICENSE为原提交LF后，107项相关检查和上述817项全量均通过；许可内容未改。首次scope脚本误把历史冻结的red-skillhub当作当前同步镜像，修正为明确的六个根目录后通过，未改该历史包。首次失败与旧包清单、旧dry-run均保留；最终SkillHub验收使用[最终组包](https://github.com/gongyu0918-debug/chinese-official-writing-skill/blob/0721297298b72be7a37b93c6598172791b58e421/maintenance/tests/evidence/release-v1631-candidate/skillhub-build-final.json)和[最终dry-run](https://github.com/gongyu0918-debug/chinese-official-writing-skill/blob/0721297298b72be7a37b93c6598172791b58e421/maintenance/tests/evidence/release-v1631-candidate/skillhub-dry-run-final.json)，不混用旧目录记录。

Hook本地集成的845项及其原生Stop检查属于另一产品快照，不计入本版写作质量或工程结果。本次拆分没有新增模型调用。
