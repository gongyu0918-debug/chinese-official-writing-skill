# URL 与稀疏排查报告最小修复 loop 记录

日期：2026-07-08

基线：`b7798f8 fix:strengthen-final-draft-inspection`

## 修改范围

- `SKILL.md` 与镜像入口：补充 URL 指代任务的版本范围、来源核验和处置动作保真提示；补充稀疏排查/核查材料只给结论时宁可短写、不补范围和后续机制。
- `references/workflow.md` 与镜像：同步 URL 来源核验、删除/卸载/报送“无”动作保真、稀疏排查结论不扩展为终端范围或后续管理。
- `tools/run_real_prompt_ablation.py`：新增 P103/P104，覆盖 URL 来源核验与稀疏排查首稿边界。
- `tests/test_real_prompt_ablation.py`：补 P103/P104 的确定性守卫。

本轮未新增硬 lint、脚本清洗、默认联网、默认阻断或先问流程。

## 工程验证

- `python -m unittest tests.test_real_prompt_ablation tests.test_skill_boundary`：43 tests OK。
- `python -m unittest discover -s tests`：107 tests OK。
- `git diff --check`：通过；仅 Windows 换行提示。
- `tools/run_real_prompt_ablation.py --baseline-root output\release-baselines\b7798f8 --baseline-label baseline-b7798f8 --current-root . --out output\real-prompt-vs-b7798f8-url-sparse-fix-final`：
  - baseline-b7798f8：102/104。
  - current：104/104。
  - baseline 只在新增 P103/P104 失败，current 无失败。

## 真实写作复测结论

测试覆盖：

- URL 改内部通知：Claude Code 风险版本排查通知。
- URL 改天气提醒：气象文章改上下班防范提示。
- 稀疏排查报告：OpenClaw 未安装情况报告。
- 活动期间提醒通知：世界杯期间禁止赌球、强化考勤、祝观赛愉快。

结果：

- 强模型低思考：URL 任务能较稳定保留版本范围、删除/报送无等用户动作；部分轮次能输出来源核验，部分轮次仍漏来源核验。稀疏 OpenClaw 报告经修复后可压到只保留用户给定结论和报告语。
- 弱模型低思考：OpenClaw 稀疏报告由 FAIL 改善为 PASS/WARN，主要不再补下一步管理链条；但 URL 通知仍不稳定，最后一轮仍写成“文中所涉各版本”，没有给出具体版本范围和来源核验，并补了终端范围。
- 对照的世界杯通知未出现大面积回退；能覆盖禁止赌球、强化考勤、祝观赛愉快，个别样稿语气略硬但可二次修改。

独立 verifier 结论：

- URL 场景仍为 WARN，不建议直接作为发布候选通过。
- OpenClaw 稀疏报告 PASS。
- 世界杯通知 PASS。
- 建议保留当前修复方向，但不要继续无限堆首稿 prompt；弱模型 URL 首稿仍需终稿检查或二次修订兜底。

## 发布判断

本轮修复保留，但不作为发布通过结论。当前候选仍不应发布 GitHub、ClawHub 或 SkillHub。

后续建议：

- 不继续扩大 `SKILL.md` 首稿规则。
- 针对 URL 类稿件增加二次审稿/终稿检查样本，要求检查“具体版本范围、来源核验、用户处置动作是否被替换”。
- 如果弱模型首稿仍不能稳定产出来源核验，发布门槛应依赖“写作 + 审稿/二次修订”链路，而不是单次首稿。
