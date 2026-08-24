# OC-003 只审不改题

你在当前 checkout 中执行一次真实中文公文审稿。只允许读取以下文件：

- `chinese-official-writing/SKILL.md`
- `chinese-official-writing/references/information-selection.md`
- `chinese-official-writing/references/genre-checklist-feasibility-review.md`
- `chinese-official-writing/references/ai-compute-docs.md`

不要读取用户级同名 Skill、memory、其他分支或其他文件；不要联网，不启用 Hook，不修改文件。

用户只要求审稿，不要求代改。请按“位置—风险—修改建议”检查下列可研摘要片段，只输出审稿意见，不重写全文。

核对材料：2026年5月，4个部门使用现有测试环境处理3200项长文本审校任务，71项排队超过10分钟，峰值并发22；3次请求超时均于当日重提完成，原因和影响范围尚无结论。200项抽样实测的单项平均用量为18000 Token；按每月4000项、12个月测算，年度约8.64亿 Token，其中每月4000项只是测算假设。项目仅处于可研阶段；一家服务商提供一年78万元非约束性初步报价，尚未比价、未批预算、未定供应商、未形成采购决定。

待审片段：

“现已形成每年8.64亿 Token的刚性需求，现有算力严重不足。项目预算78万元已经批准，服务商已经确定。租用算力后可节约综合成本30%，彻底消除任务排队和请求超时，项目已具备立即采购条件。若后续按该测算口径配置资源，预计可缓解高峰排队，具体效果需运行验证。”
