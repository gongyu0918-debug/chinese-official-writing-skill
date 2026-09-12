# 五通道组合真实写稿 A/B 复测证据（2026-09-12）

## 固定条件

- 基线：`main`；候选：当前重构分支 `HEAD`。
- 五条客户端实际通道均使用 `max`，同一任务提示分别运行基线与候选；第二轮复测复用第一轮每一臂的提示 SHA-256。
- 只允许读取冻结输入和任务给定文件；不联网、不启用 Hook 或插件、不覆盖输入。
- 第一轮和第二轮均 5 个文种场景、10 个臂次，全部 `exit_code=0` 且有非空最终稿。

## 通道与结果

| 场景 | 通道 | 第一轮基线/候选耗时 | 第二轮基线/候选耗时 | 归因结论 |
|---|---|---:|---:|---|
| notice | `minimax-cn/MiniMax-M3` | 114.0s / 239.34s | 113.03s / 166.3s | 首轮出现的旁白、补句或状态省略在同提示复测中未稳定复现；未见候选独有硬回退。 |
  - 输出 SHA-256 前12位（首轮基线/候选；复测基线/候选）：`dc1eeee7db46/52b420d861e2; 03d1432a9f71/b1791bbf68fe`
| speech | `alibaba-token-plan/qwen3.8-flash` | 123.11s / 100.2s | 151.2s / 49.31s | 首轮出现的旁白、补句或状态省略在同提示复测中未稳定复现；未见候选独有硬回退。 |
  - 输出 SHA-256 前12位（首轮基线/候选；复测基线/候选）：`0affe7e79f93/3ddabc896384; 579936b98147/b1c6401e6eb6`
| research | `alibaba-token-plan-2/qwen3.8-flash` | 103.88s / 71.81s | 95.48s / 87.08s | 首轮出现的旁白、补句或状态省略在同提示复测中未稳定复现；未见候选独有硬回退。 |
  - 输出 SHA-256 前12位（首轮基线/候选；复测基线/候选）：`dc65cba1d125/589b4faedddf; 723c2c790086/e38d9a1d119a`
| procurement | `command-code/deepseek-deepseek-v4.1-flash` | 60.58s / 34.42s | 60.03s / 38.06s | 首轮出现的旁白、补句或状态省略在同提示复测中未稳定复现；未见候选独有硬回退。 |
  - 输出 SHA-256 前12位（首轮基线/候选；复测基线/候选）：`0c0d8136d4ca/b39499d3addc; cb779617ecfb/dd8e94c7d4ad`
| correspondence | `ollama-cloud/glm-5.3-flash` | 70.97s / 49.28s | 44.59s / 41.0s | 首轮出现的旁白、补句或状态省略在同提示复测中未稳定复现；未见候选独有硬回退。 |
  - 输出 SHA-256 前12位（首轮基线/候选；复测基线/候选）：`50e50f11b756/5d33765ae027; 4307367ac911/2ed956c74bc8`

## 质量判定

- `notice`：首轮候选带过程说明，复测直接交付通知正文；没有增加期限、会议或责任安排。
- `speech`：首轮候选多出“汇总结果出来前不作判断”，复测消失；数字、反馈汇总和未结论状态均保留。
- `research`：候选压缩为短报告，访问数、问卷数、3 家反馈、原因未核实和建议未决定均保留。
- `procurement`：两轮候选均保留 15 件、3000 元、2 项规格缺失、供应商未提供和结论未形成。
- `correspondence`：首轮候选一度省略“分歧已记录”，复测完整保留；同提示下该差异未持续，因此归为模型波动，不能作为候选独有回退。
- 首轮候选的过程旁白与复测候选的正文直出交叉出现，且基线同样多次出现过程旁白，说明它们是模型采样/共同交付波动，不是当前路由改动稳定造成的回退。

## 门禁与限制

- 静态组合测试：`python -B -m unittest maintenance.tests.test_reference_rewrite_contract maintenance.tests.test_promptfoo_eval maintenance.tests.test_repository_reachability maintenance.tests.test_report_generic_block_relief maintenance.tests.test_core_lint_pointer_relocation maintenance.tests.test_ab_provenance maintenance.tests.test_hook_layer_contract maintenance.tests.test_description_news_trigger maintenance.tests.test_review_gate_request_fact_safety maintenance.tests.test_review_gate maintenance.tests.test_safe_request_entry_integration maintenance.tests.test_short_draft_naturalness -q` → **239 tests, OK**。
- 本证据支持当前组合候选继续进入架构验收；尚不授权合并、推送或发布。
- 全量历史测试仍有未迁移的旧结构断言，不能以全量旧套件宣称全部通过；本轮以已迁移的架构、路由、镜像、Hook 边界和真实写稿门禁为准。
