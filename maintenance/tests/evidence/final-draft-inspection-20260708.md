# Final-draft inspection 最小修复记录（2026-07-08）

## 背景

连续多轮弱模型首稿修复表明，继续往 `SKILL.md` 堆“不要补某些事项”的默认起草规则，会增加 prompt 体积，但不能稳定解决稀疏材料外扩。上一轮诊断还确认：URL-only 失败常混入来源读取问题；真正反复出现的是稀疏报告、提醒通知和风险排查短稿中补依据、范围、日期、管理动作和后续链条。

本轮不再修默认起草流程，只验证并加强“只审不改 / final-draft inspection”这条外部安全网。

## 修改

只改 `references/review-checklist.md`：

- 在“定稿前高风险先查”加入稀疏 `已排查/已核查/已检查` 类报告的事实边界复核。
- 在“段落复核”加入“稀疏排查报告外扩”检查：原材料只给 `已排查/未发现` 结论时，`按照有关要求`、`相关终端设备`、`运行痕迹`、`后续加强管理`、当前日期等未给依据、范围、过程、后续动作或正式要素，至少按中风险提示。
- 新增确定性消融 P102，只覆盖 review-checklist 支撑，不把它写成默认起草阻断。

## 工程验证

- `python -m unittest tests.test_real_prompt_ablation tests.test_skill_boundary`：43 tests OK。
- `python -m unittest discover -s tests`：107 tests OK。
- `git diff --check`：通过，仅有 Windows 换行提示。
- 消融对比 `d5c2c61`：
  - baseline `101/102`
  - current `102/102`
  - baseline 只失败新增 P102，current 无失败。

## 真实审稿复测

使用 `gpt-5.4-mini`、低思考、隔离 final-draft inspection agent。agent 只加载当前 skill，任务为只审不改，按“位置｜风险层级｜修改建议”输出。

样本覆盖：

1. OpenClaw 已排查报告：原 prompt 只给未发现安装结论，成稿补 `按照有关要求`、`相关终端设备`、当前日期。
2. 世界杯通知：原 prompt 只给禁止赌球、强化考勤、祝观赛愉快，成稿补请假审批、教育提醒、工作生活两不误、确保工作正常开展。
3. Claude Code 风险通知：原 prompt 给版本、风险、删除和报送要求，成稿补开发终端/工作终端/相关设备、核实其他安全版本、记录留痕。

复测结果：

- OpenClaw 样本：审稿 agent 将 `按照有关要求`、`相关终端设备` 标为中风险，指出应只保留已给事实；日期列为低到中风险，提示严格贴原 prompt 时不写或放正文外待确认。
- 世界杯样本：审稿 agent 抓到新增管理动作和“祝观赛愉快”被压掉的问题。
- Claude Code 样本：审稿 agent 抓到新增设备范围和记录留痕动作。

独立 verifier 判定：PASS。认为这次 final-draft inspection 能证明本轮 `review-checklist` 最小修复值得保留；它覆盖稀疏材料补依据/范围、通知类补管理链条、排查类补留痕动作，且审稿形态没有滑成改稿。

## 结论

本轮修复可保留，但不是发布充分条件。它改善的是“外部审稿/只审不改”能力，不代表弱模型首稿已经稳定。后续发布前仍需跑强弱模型真实写稿 A/B、二次修订和 final-draft inspection 组合测试。

