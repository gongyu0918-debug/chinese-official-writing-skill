# 文种族群路由组合验证（2026-09-12）

候选基于当前 main `8b8aa1c6b8c65414b0444615c39cfa537619957a`，仅将原混合文种页的五组文种骨架改为按任务进入独立叶子，并保留函页和讲话开场人物排序提示。候选提交为 `aa735a71`。变更文件为五个新文种叶和 `references/genre-playbooks.md`；未改写文种规则事实和质量边界。

真实写稿使用当前客户端五条通道、默认 max、同题两臂独立上下文：

- `minimax-cn/MiniMax-M3`：通知/通报；基线 max 首轮技术超时，唯一 high 回退有效，候选 max 有效，不能作 max/max 质量胜负。
- `alibaba-token-plan/qwen3.8-flash`：讲话；基线 max 超时后 high 有效，候选 max 有效，不能作 max/max 质量胜负。
- `alibaba-token-plan-2/qwen3.8-flash`：调研报告；基线与候选 max 均有效，数字、原因未核实和建议未决定状态保持。
- `command-code/deepseek-deepseek-v4.1-flash`：采购审查；基线与候选 max 均有效，品名、数量、预算、规格缺口、供应商缺失和结论未形成保持。
- `ollama-cloud/glm-5.3-flash`：函；基线与候选 max 均有效，请求、日期、邮箱和未决定状态保持。

首轮通知与讲话的 max/high 不同档位结果只作技术覆盖。针对讲话和函的候选过程旁白疑点，使用同一 `command-code/deepseek-deepseek-v4.1-flash`、同一 max 和同一提示补跑各一对：四份终稿均有效，均无候选独有旁白或事实/结构硬错误。首轮与定向结果的措辞、空行和是否出现简短执行说明属于模型采样差异，不归因于新路由。没有发现门禁过严导致的候选假阴性。

工程验证：`quick_validate.py chinese-official-writing` 通过；`test_skill_boundary`、`test_real_prompt_ablation`、`test_repository_reachability` 合计 102/102 通过；五套普通镜像已由 `sync_adapters.py` 同步，`git diff --check` 和 Python 语法检查通过。旧的确定性断言已改为验证新叶路径和完整行为组，不以保留旧混合页文本作为通过条件。

当前证据支持该文种族群路由在五类真实任务中不劣于当前 main，且减少无关文种阅读；不宣称所有模型、所有文种组合的统计稳定性提升。可进入下一步候选评审，是否合并或发布另行决定。
