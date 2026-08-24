# OC-003 明示完整性核对控制题

你在当前 checkout 中执行一次真实中文公文审稿。只允许读取以下文件：

- `chinese-official-writing/SKILL.md`
- `chinese-official-writing/references/information-selection.md`
- `chinese-official-writing/references/genre-checklist-feasibility-review.md`
- `chinese-official-writing/references/ai-compute-docs.md`

不要读取用户级同名 Skill、memory、其他分支或其他文件；不要联网，不启用 Hook，不修改文件。

用户只要求审稿，不要求代改。除核对事实和状态外，用户明确要求检查该可研摘要能否支撑后续采购决策，并指出材料在成本同口径比较、服务技术指标、验收主体与验收依据方面的实质缺项。请按“位置—风险—修改建议”输出审稿意见，不重写全文。

核对材料：2026年6月，5个部门在测试环境处理2800项票据识别与分类任务；160项抽样实测的单项平均用量为12500 Token；按每月3500项、12个月测算，年度约5.25亿 Token。项目拟研究一年期推理资源、统一排队、用量统计和故障告警服务；一家服务商提供一年46万元非约束性初步报价。材料没有同口径成本比较，没有并发、响应时延、可用性或故障响应指标，没有验收主体与验收依据；尚未形成采购决定。

待审片段：

“根据测试和抽样测算，中心拟研究租用一年期票据识别与分类算力服务，年度用量按每月3500项假设测算约5.25亿 Token。一家服务商提供一年46万元非约束性初步报价。项目尚处于可研阶段，尚未形成采购决定。”
