# OC-003 新事实只审盲样

你在当前 checkout 中执行一次真实中文公文审稿。只允许读取以下文件：

- `chinese-official-writing/SKILL.md`
- `chinese-official-writing/references/information-selection.md`
- `chinese-official-writing/references/genre-checklist-feasibility-review.md`
- `chinese-official-writing/references/ai-compute-docs.md`

不要读取用户级同名 Skill、memory、其他分支或其他文件；不要联网，不启用 Hook，不修改文件。

用户只要求审稿，不要求代改。请按“位置—风险—修改建议”检查下列可研摘要片段，只输出审稿意见，不重写全文。

核对材料：2026年6月，5个部门使用现有测试环境处理2800项票据识别与分类任务，64项排队超过8分钟，峰值并发19；4次请求失败均于当日重提完成，原因和影响范围尚无结论。160项抽样实测的单项平均用量为12500 Token；按每月3500项、12个月测算，年度约5.25亿 Token，其中每月3500项只是测算假设。是否把试用范围由5个部门扩大到7个部门尚未决定。项目仅处于可研阶段；一家服务商提供一年46万元非约束性初步报价，尚未比价、未批预算、未定供应商、未形成采购决定。

待审片段：

“中心已形成每年5.25亿 Token的确定需求，现有算力瓶颈已经查明。项目预算46万元已经落实，服务商已经选定。租用服务后可降低综合成本25%，彻底消除排队和请求失败，现已具备直接采购条件。按该测算口径配置资源，预计可缓解高峰排队，实际效果仍需运行验证。”
