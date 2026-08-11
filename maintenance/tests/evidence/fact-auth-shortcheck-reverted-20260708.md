# 事实授权短检候选回退记录

日期：2026-07-08

基线：`feb794a test: record current six-prompt availability`

## 候选修改

曾尝试在 `chinese-official-writing/SKILL.md` 入口新增一个短小的“成稿前事实授权短检”，目标是在不继续堆长规则的前提下提醒模型：

- 材料越少，正文越要短而准。
- 排查、核查、处置、报送类材料不补排查范围、核查方式、登记、责任人、联系人、例检、后续管理等链条。
- 活动提醒类通知不补值班、巡查、宣贯、记录、上报、严肃处理等执行链。
- URL 指代无法提取或核验时，不以“相关版本”“安全风险提示”等泛称代替。
- 定点时间不改成截止时间。

该修改已在真实写作复测后回退，未保留在当前工作区。

## 工程验证

候选修改期间已完成以下确定性验证：

- `python -m unittest tests.test_real_prompt_ablation tests.test_skill_boundary`：43 tests OK。
- `python -m unittest discover -s tests`：107 tests OK。
- `git diff --check`：无检查错误，仅换行提示。
- `tools/run_real_prompt_ablation.py --baseline-root output\release-baselines\pre-factauth-feb794a --baseline-label baseline-feb794a --current-root . --out output\real-prompt-vs-feb794a-factauth`：`baseline-feb794a 106/106`，`current 106/106`。

确定性测试没有发现工程回归，但它不能证明真实写作质量改善。

## 真实写作复测

复测方式：

- writer A：`gpt-5.3-codex-spark`，低思考，加载当前候选 skill，写同一批 6 个真实 prompt。
- writer B：`gpt-5.5`，低思考，加载当前候选 skill，写同一批 6 个真实 prompt。
- verifier：`gpt-5.5`，低思考，对比候选相对 `feb794a` 的真实写作表现。

Verifier 结论：

- 弱模型本轮 `FAIL`，较 baseline 未改善，且部分场景退化。
- 强模型本轮 `WARN`，较 baseline 不明显改善。
- 建议回退这次 `SKILL.md` 修改。

主要问题：

1. 弱模型仍稳定出现 Markdown 加粗标题。
2. P3 仍丢失“如有请删除”的核心动作，并把 `7月10日15:00` 改成 `15:00 前`。
3. P5 仍补请假、加班审批、逐日报送等未给管理动作。
4. P6 仍把“已排查、未发现安装”扩写为排查范围、端口、目录、进程、月度巡检、告警、审批记录等未给事实。
5. 强模型虽能意识到 URL 来源无法核验，但仍补排查范围、设备范围、反馈字段和后续管理。

## 处理决定

本候选不保留。原因是新增入口短检没有解决弱模型核心失败模式，也没有让强模型形成明确净改善；继续保留只会增加入口规则密度，可能加重后续 prompt 冲突和弱模型选择性忽略。

下一轮不应继续往 `SKILL.md` 堆同类规则。更值得验证的方向是外部 `final-draft inspection` 或删减型二次修订链路：

- 生成后只标出未由用户材料授权的范围、流程、责任、记录、联系人、设备、后续管理、日期变形和 Markdown 残留。
- 对弱模型输出先做删减型二次修订，只删除未授权内容和格式残留，不补写新内容。
- 重点测试 P3、P6 这类“稀疏材料 + 正式文种 + 排查/处置”场景，证明能否稳定把 FAIL 拉回 WARN/PASS，再考虑是否纳入发布流程。
