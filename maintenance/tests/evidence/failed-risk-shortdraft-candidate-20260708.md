# 2026-07-08 风险提示/排查短稿候选回退记录

## 背景

在 `3a6eba3` 之后尝试过一个最小候选：不继续堆通用 prompt 限制，而是把三次以上共性外扩归纳为“风险提示、排查、核查类短稿”场景。

候选修改曾覆盖：

- `SKILL.md`：把 `风险提示/排查/核查类短稿` 加入 `workflow.md` 加载条件，并提示不扩展执行链条、排查范围或处置流程。
- `references/workflow.md`：补一段风险提示、排查、核查类短稿补充。
- `tools/run_real_prompt_ablation.py` 和边界测试：新增确定性 P096。
- 已同步到 `skills/`、`.agents/`、`.qwen/`、`hermes/`、`openclaw/` 镜像。

## 确定性验证

候选的确定性验证通过：

- `python -m unittest tests.test_real_prompt_ablation tests.test_skill_boundary`：43 tests OK。
- `python -m unittest discover -s tests`：107 tests OK。
- `git diff --check`：通过。
- `run_real_prompt_ablation.py` 对比 `3a6eba3`：baseline `95/96`，current `96/96`，baseline 只在新增 P096 失败。

## 真实复测

随后用真实写作复测验证是否值得保留：

- writer：
  - weak：`gpt-5.3-codex-spark`，`reasoning_effort=low`
  - strong：`gpt-5.5`，`reasoning_effort=low`
- verifier：`gpt-5.5`，`reasoning_effort=low`
- 覆盖：
  - Claude Code 风险提示网页改本单位通知。
  - 新华网暴雨预警改上下班路上注意防范。
  - 世界杯期间禁止赌球、强化考勤但祝观赛愉快的通知。
  - OpenClaw 已排查安装情况报告。

独立 verifier 结论：

- W1 Claude Code weak：`WARN`，核心要点覆盖，但 Markdown 加粗残留、缺落款单位。
- S1 Claude Code strong：`PASS`，但不能抵消 weak 风险。
- W2 暴雨通勤 weak：`FAIL`，大量保留气象报道地区细节，并补校园、社区、路段排查、室外巡检等未授权管理链条。
- W3 世界杯通知 weak：`WARN`，补每日考勤核查、请销假真实性核验、异常考勤跟进、长期监督等执行链条，且有 Markdown 加粗。
- W4 OpenClaw 报告 weak：`FAIL`，补办公终端、应用商店安装项、软件清单、服务器、安装目录、常驻进程、运维记录、复核等未给排查范围和方法。

## 决定

候选已回退，不保留进入下一步。

原因：虽然确定性消融通过，但真实弱模型复测仍出现三次以上共性风险，且 W2、W4 为 FAIL。这个候选没有把风险提示/排查短稿边界稳定转化为弱模型首稿能力，继续保留只会增加规则体积。

后续不要重复追加同类“把场景名称写进 SKILL.md + workflow.md”的短稿边界。若继续推进，优先探索不增加默认阻断的二次修订链路或外部 final-draft inspection，而不是继续往入口加场景禁令。
