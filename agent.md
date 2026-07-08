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

## 修改思路和提交路径

本轮不是一次直接升级，而是按“测试 -> 最小修复 -> 复测 -> 消融 -> 失败则回退”的 loop 推进。核心判断口径是：确定性用例只能说明规则和文件存在，真实写稿 A/B 与独立 verifier 结论优先。

提交路径和处理逻辑如下：

1. `df83674` 起：尝试收紧 URL 改通知、稀疏报告和事实边界。
   - 思路：针对真实 prompt 中出现的“URL 来源事实漏用”“稀疏材料自动补管理链条”做软性 prompt/reference 修复。
   - 结果：工程测试可通过，但弱模型真实写稿仍会补范围、流程、责任或后续机制。

2. `22c0ac8`、`03eadbb`、`4f8f4ed`、`feb794a`：连续记录弱模型首稿和二次修改失败样本。
   - 思路：先不继续改规则，扩大真实场景测试，验证问题是不是单例。
   - 结果：问题集中在弱模型对“未给事实”和“二次修干净”的执行不稳定；单纯把规则写进入口无法稳定改善。

3. `ead7182`：记录并回退“事实授权短检”候选。
   - 思路：在成稿前增加短检，提醒模型不要补未授权事实。
   - 结果：弱模型仍 FAIL，且入口规则密度增加，存在让强模型过度保守的风险；不保留。

4. `4d83b57`、`fd4066a`：只记录外部删减型清稿链路的测试证据。
   - 思路：不把清稿做成默认 workflow，而是验证“用户明确要求修干净/删掉没说的内容/能发时”的二次删减是否更可靠。
   - 结果：能明显删掉 Markdown 和未授权管理链条，但仍有正文外提示隔离、来源事实保留、反馈字段补入等残留风险；只作为下一轮候选，不并入当前 skill。

5. `2081ded`：回退到 `v1.5.2` 行为。
   - 思路：既然真实 A/B 判定当前候选相对 `1.5.2` 没有净改进，就优先恢复稳定发行基线。
   - 范围：恢复会影响 skill 行为、镜像入口、lint、sync、README 和确定性测试门槛的文件；保留 `tests/evidence/` 和本文件作为审计记录。

关键证据文件：

- `tests/evidence/weak-model-prompt-loop-20260708.md`：弱模型 prompt 堆叠无效的早期证据。
- `tests/evidence/second-revision-chain-failed-20260708.md`：二次修改链路失败记录。
- `tests/evidence/external-deletion-cleaner-6prompts-20260708.md`：外部删减型清稿 6 prompt 初测。
- `tests/evidence/external-deletion-cleaner-source-focused-20260708.md`：外部清稿 focused 风险复测。
- `tests/evidence/current-vs-1.5.2-real-writing-rollback-20260708.md`：最终回退判定。

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

## 下一次继续前的执行步骤

1. 先确认当前产品文件仍与 `v1.5.2` 行为一致，再决定是否从“外部删减型清稿/用户明确二次修订”做最小候选。
2. 如要修改，只优先动 `references/review-checklist.md` 或相关复核 reference，不把新规则继续塞进 `SKILL.md` 入口。
3. 新规则必须写成软性、用户触发、非默认阻断：只在用户明确要求“修干净”“删掉没说的内容”“去掉格式痕迹”“能发”时使用；不得变成首稿默认阶段。
4. 修改后先跑确定性消融，再跑真实写稿 A/B；真实写稿至少覆盖 Claude Code URL 改通知、OpenClaw 排查报告、世界杯期间通知和一个普通情况说明，且要有独立 verifier。
5. 如果真实 A/B 仍显示 current 相对 `1.5.2` 无净改进，立即回退候选，不发布、不 bump 版本号。
