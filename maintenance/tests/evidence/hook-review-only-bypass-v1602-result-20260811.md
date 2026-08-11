# Hook 纯审稿绕过原子结果

日期：2026-08-11

结论：`ENGINEERING PASS / PURE REVIEW BYPASS CONFIRMED / NO MODEL-QUALITY CLAIM`

## 固定范围

- 固定集成基线：`6a374542`。
- 产品提交：`5aedda31`；镜像同步提交：`0664ac0f`。
- 最终集成对应提交：`e7d03727`、`3679fd49`。
- 只调整 Hook 对纯审稿请求的触发范围；不修改 `review_gate.py`、`prose_lint.py`、普通 Skill 路由或写稿规则。

## 实际行为

- “只审查、不代改”“仅指出问题”“只给修改建议”等四种纯审稿表达均直接放行，不创建 transaction，不进入 `AWAITING_REPAIR`。
- 起草、改写以及“先复核后改写”继续进入原有有界门禁，未被宽泛绕过。
- Claude Code 适配器复用同一判定，保持相同行为。

## 已运行验证

- 原子 focused：25/25 通过。
- 原子全量单测：500/500 通过。
- Promptfoo stub smoke：20/20 通过，run id `eval-wgG`。
- 固定基线确定性消融：baseline 111/111，candidate 111/111。
- quick validate、`py_compile`、两轮镜像同步和 `git diff --check` 均通过。
- 最终集成复核：`tests.test_host_gate_adapter`、`tests.test_hook_layer_contract`、`tests.test_skillhub_package_builder`、`tests.test_skill_boundary` 共 89/89 通过。

## 结论边界

这些结果证明纯审稿不会被 Hook 误当成待修正文稿，也证明正常起草和改写仍受门禁约束。该原子没有单独调用写稿模型，不据此宣称文稿质量提升；带 Hook 与不带 Hook 的真实写稿非劣结论由独立 A/B 记录给出。

本原子未合并 `main`、未推送、未发布，也未修改冻结的 ClawHub/OpenClaw 包。
