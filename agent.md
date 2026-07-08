# 当前 Agent 接手记录

本文件记录本轮 `1.5.2` 之后的测试、修复、复测、消融和回退链路，便于下一个 agent 接手。仓库长期规则仍以 `AGENTS.md` 为准；本文件只记录当前 loop 的实际状态和下一步建议。

## 当前状态

- 远端发布基线仍以 `chinese-official-writing@1.5.2` 为准。
- 当前工作树已将会影响 skill 行为、镜像入口、lint、sync、README 和确定性测试门槛的候选改动恢复到 `v1.5.2` 内容。
- 1.5.3 相关尝试只保留为 `tests/evidence/` 下的测试证据和本文件记录，不作为发布候选。
- 不应发布当前候选；下一轮应从 `v1.5.2` 行为边界重新开始最小修复。

## 本轮为什么回退

用同一批 6 个真实 prompt 对比 `1.5.2` 和当前候选，弱模型低思考独立 verifier 判定：current 相对 `1.5.2` 没有改进，存在轻度功能性回退。

主要回退点：

- Markdown 加粗、横线、占位等格式残留没有改善。
- 稀疏排查、通知、报告场景仍补排查范围、流程、责任、后续机制。
- P3 URL 改通知仍没有落实“如有请删除”，并把定点时间写成截止时间。
- P4、P5、P6 出现落款日期缺失或不规范。
- P1 有从情况说明漂向“请领导审议”的倾向。

因此按“有问题就回退”的 loop 要求，已回退影响行为的候选改动。

## 已跑验证

确定性验证：

- `python -m unittest tests.test_real_prompt_ablation tests.test_skill_boundary`：43 tests OK。
- `python -m unittest discover -s tests`：107 tests OK（回退前候选状态）。
- `git diff --check`：无检查错误。
- `tools/run_real_prompt_ablation.py --baseline-root output\release-baselines\github-1.5.2 --baseline-label baseline-1.5.2 --current-root . --out output\real-prompt-vs-1.5.2-current-fd4066a`：候选状态下 `baseline-1.5.2 84/106`、`current 106/106`。

真实写稿验证：

- 6 个真实 prompt 覆盖电脑采购情况说明、微博情况说明、Claude Code URL 改通知、气象 URL 改通知、世界杯期间通知、OpenClaw 排查报告。
- 弱模型低思考 A/B：`1.5.2` 与 current 都有明显问题，但 current 在格式完整性和事实外扩上被判轻度回退。
- 结论：确定性消融变好不代表真实写稿变好；真实 writer/verifier 结论优先。

## 本轮尝试过但不保留的方向

1. 在 `SKILL.md` 入口增加“成稿前事实授权短检”。
   - 结果：弱模型仍 FAIL，P3/P6 未改善，入口规则密度增加。
   - 处理：已回退。

2. 外部删减型清稿链路。
   - 结果：能把弱模型失败稿基本拉回 `PASS with WARN`，尤其能删除 Markdown 和未授权管理链条。
   - 残留：正文外提示隔离和来源事实保留需要继续测试；focused 测试后仍发现 cleaner 会补反馈字段。
   - 处理：只作为下一轮候选方向，不写入默认 skill workflow。

## 下一轮建议

- 不要继续往 `SKILL.md` 堆入口规则；弱模型已经表现出选择性忽略。
- 不要一例一修。只有同类问题在真实写稿或独立 verifier 中出现 3 次以上，才进入 prompt/reference 最小修复；单个样本问题先记录证据，不直接改规则。
- 如果继续推进，应优先验证“外部删减型清稿/二次修订”方向，但只能作为可选交付链路，不能默认阻断成稿。
- 下一轮 cleaner 约束只窄收紧一点：不得新增原 prompt 未给出的反馈字段、统计口径、报送表项和责任要求；确需提示时放正文外。
- 每累计 5 次 commit，或任何影响 skill 行为的修改，都必须重新做 `1.5.2` 或最新发布基线的确定性消融和真实写稿 A/B。
- 真实写稿测试必须包含弱模型低思考；只看强模型会掩盖边界漂移。
