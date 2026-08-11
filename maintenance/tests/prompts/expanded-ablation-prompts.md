# Expanded Ablation Prompts

This file contains anonymized, synthetic prompts for testing. It must not include real project names, internal file paths, personal information, or raw user documents.

## Test Method

For each genre below, run two variants:

- Baseline: give only the task prompt and no style/workflow constraints.
- Skill: explicitly use `chinese-official-writing` and follow its workflow.

Each genre has a short-form and long-form task. Outputs should be reviewed for genre fit, sponsor viewpoint, argument clarity, data handling, AI-flavor patterns, oral wording, and actionable next steps.

## Genres

1. 通知：组织各单位报送年度数字化建设项目储备情况。
2. 请示：申请启动内部管理系统升级项目。
3. 报告：报告季度重点项目推进情况。
4. 说明：说明专项资金执行进度偏慢的原因及后续安排。
5. 方案：制定年度数据治理专项工作方案。
6. 申请：申请增补项目测试环境资源。
7. 函：向外部合作单位商请提供接口联调支持。
8. 复函：回复合作单位关于延期联调的来函。
9. 批复：批复下属单位实施办公网络改造项目。
10. 意见：提出加强内部数据安全管理的意见。
11. 决定：作出成立专项工作专班的决定。
12. 公告：发布服务平台停机维护公告。
13. 公示：公示拟入选技术服务供应商名单。
14. 通报：通报内部审查发现的问题及整改要求。
15. 会议纪要：形成项目协调会会议纪要。
16. 工作要点：制定年度信息化工作要点。
17. 工作总结：总结年度技术服务工作。
18. 调研报告：调研基层单位数字化应用现状。
19. 可研报告：论证建设统一模型服务平台的可行性。
20. 实施方案：制定统一身份认证系统实施方案。
21. 建设方案：制定数据资产管理平台建设方案。
22. 审查材料：形成项目初步设计审查意见材料。

## AI Compute Calibration Tasks

1. 算力服务可研报告：说明需求来源、Token 年需求、云端费用、租赁费用、收益和安全保障。
2. 算力资源采购方案：说明资源规模、采购方式、服务边界、费用构成、验收指标和风险控制。
3. GPU/服务器租赁技术需求：说明服务器配置、模型部署、并发能力、SLA、运维响应和数据安全。
4. 云端部署成本对比说明：以 Token 增长为主线，比较继续云端部署和租赁服务的三年成本。
5. 技术服务审查材料：审查租赁服务方案是否具备需求依据、成本依据、交付依据和安全依据。
