# 弱模型注意力压缩 A/B 测试记录（2026-07-09）

## 目标

验证一个假设：弱模型写作问题可能不是“看不到规则”，而是入口规则过密、术语化、重复，导致注意力崩溃。测试方向是压缩 `SKILL.md` 的“任务模式路由与交付模式”入口段，保留高价值事实边界，把细节交给 references 渐进读取。

## 实验改动

临时候选只改 `chinese-official-writing/SKILL.md` 及同步镜像，未改 reference、脚本或 lint。入口段从 2013 字符压到 1463 字符，减少 550 字符；行数从 16 行变为 20 行，用更短的扫描项替代高密度长句。

该候选未保留，测试后已撤回，当前产品文件恢复到 1.5.2 入口写法。

## 确定性验证

- `python -m unittest tests.test_real_prompt_ablation tests.test_skill_boundary`
  - 压缩候选最终可通过 41 tests。
- `python .\tools\run_real_prompt_ablation.py --baseline-root output\release-baselines\github-1.5.2 --baseline-label baseline-1.5.2 --current-root . --out output\real-prompt-vs-1.5.2-compressed-entry`
  - baseline-1.5.2：85/85。
  - current 压缩候选：85/85。

确定性测试只能证明规则锚点还在，不能证明真实写稿改善。

## 真实写稿 A/B

使用 5 个真实用户式 prompt，覆盖：

1. TestAgent 版本排查通知：版本、删除动作、无安装反馈、精确时间点、钉钉报送技术应用部。
2. OpenClaw 安装排查报告：只允许写“未发现安装”，用户明确不要日期、过程、范围、责任人、后续整改。
3. 世界杯期间禁止赌球和考勤提醒通知：语气柔和、祝观赛愉快。
4. 5090 电脑采购情况说明：版慎通、35B 小模型、模型校准、harness、脱敏处理、安全和成本。
5. 通知压缩到 260 字以内：只输出正文，不要 Markdown，不要解释。

Writer 组合：

- 1.5.2 基线弱模型：`gpt-5.3-codex-spark`，low。
- 当前压缩入口弱模型：`gpt-5.3-codex-spark`，low。
- 当前压缩入口强模型：`gpt-5.5`，low。

独立 verifier 只看 prompt 与成稿，结论如下：

| Prompt | 1.5.2 弱模型基线 | 压缩入口弱模型 | 压缩入口强模型 |
| --- | --- | --- | --- |
| TestAgent 通知 | WARN | FAIL | PASS |
| OpenClaw 报告 | PASS | WARN | PASS |
| 世界杯通知 | PASS | WARN | PASS |
| 电脑采购说明 | PASS | WARN | PASS |
| 260 字压缩 | PASS | PASS | PASS |

## 结论

压缩入口没有达成弱模型改善，反而在 TestAgent 通知中出现实质性指令错误：

- 把“通过钉钉发给技术应用部”写成“通过钉钉下发至技术应用部”。
- 把排查主体错误转给技术应用部。
- 当前压缩入口弱模型 C1-C4 仍连续残留 Markdown 加粗。

强模型未出现明显退化，但这只能说明压缩对强模型基本安全，不能证明对弱模型有效。

## 处理决定

不保留本次压缩候选，不作为发布候选，不推送。当前工作区产品文件已恢复到 1.5.2 入口写法。

## 后续建议

后续如果继续做注意力优化，应避免一次性压缩大段入口。更稳妥的路径是：

- 先做只读信息熵审查，标出重复句、术语化句和不清晰片段。
- 每次只动一个高重复小块，并保留同一组弱/强模型 A/B。
- 把“时间点不得改成截止时间”“报送至/下发至/由谁执行的动作关系”“正式正文不使用 Markdown 加粗”作为真实写作对比样本，不要只靠确定性用例。
- 若压缩后弱模型真实写稿不优于 1.5.2，立即回滚，不继续在失败候选上叠补丁。
