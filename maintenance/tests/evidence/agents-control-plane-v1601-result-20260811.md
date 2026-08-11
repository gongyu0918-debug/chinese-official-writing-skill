# AGENTS.md 工程控制面匿名审查结果

## 固定输入

- 固定基线：`9abc48794ebf82b8e918c593ebdada8cc080fe61`。
- 候选提交：`0e1da2baa4c2b9c0ac63e4eb9c1d6ad369779b3c`。
- 匿名包：`tests/evidence/agents-control-plane-v1601/packet.md`，SHA-256 `AB34C6C4C17536E6F68AFD076367AC009E1CB43DE0B665ECA77820C7206255CB`。
- 映射在三份有效首个最终答复冻结后揭示：A=Candidate，B=Baseline。

## 裁判

三份有效审查均通过本机 Codex harness、`reasoning_effort=max`、只读临时目录运行：

- `kimi/k3`：A=PASS，B=WARN，偏好 A。
- `xai/grok-4.5`：A=PASS，B=WARN，偏好 A。
- `alibaba-token-plan/qwen3.8-max` 清洁复放：A=PASS，B=WARN，偏好 A。

第一次 Qwen 运行虽形成最终答复，但它在共享目录读取了 Kimi 与 Grok 的答复，违反独立审查条件，固定为 `INVALID_CONTEXT_CONTAMINATION`；原文保存在 `qwen-review-invalid-contaminated.md`，不计票、不覆盖。

## 共同结论

三名有效裁判一致认为：

1. 候选去除容易过时的当前版本号，发布事实只由 evidence 索引承载，方向正确。
2. 候选明确 SkillHub 可选 Hook、专属 `hooks/` 目录、ClawHub 排除和五层验证事实，补足了发行控制边界。
3. `至少三份真实样本` 应只约束写作行为类规则，不应阻断单次即可确定复现的工程、安全或发行缺陷。
4. 基线中更明确的冲突证据处理、来源缺失记法和实际测试命令报告值得保留。

## 后续修正

提交 `9bd971c3` 仅按上述共同意见调整控制面：保留写作行为类三样本门；为确定性工程、安全和发行缺陷增加可重复证据通道；恢复 `不得择优汇报`、必要时复现原样本、来源缺失记 `unavailable`、交付报告实际测试命令。修正后 focused 2/2、`tests.test_skill_boundary` 71/71、`git diff --check` 均通过。

本轮没有修改产品 Skill、安装插件、推送、合并或发布。
