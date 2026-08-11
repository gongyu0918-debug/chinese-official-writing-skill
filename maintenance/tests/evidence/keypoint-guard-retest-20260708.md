# 2026-07-08 关键要点覆盖短检候选复测

## 背景

上一轮 6 个真实 prompt 可用度复测在 `7c43c23` 上发现：弱模型会漏掉用户点名的关键要求，例如 Claude Code 受影响版本号、世界杯通知中的“禁止赌球”等。与此同时，前序多轮已经证明继续堆叠场景禁令容易造成 prompt 膨胀，且不能稳定解决弱模型首稿问题。

本轮只做一条通用软性最小修复：成稿前做“关键要点覆盖短检”，核对用户点名的数字、版本号、禁止或必须事项、报送时间、渠道、对象和落款没有漏写，也没有被“相关版本”“有关事项”等泛称替代。

本轮未新增硬阻断、脚本清洗、默认联网、场景特例或版本号。

## 修改范围

- `chinese-official-writing/SKILL.md`
- `chinese-official-writing/references/workflow.md`
- `chinese-official-writing/references/review-checklist.md`
- 对应 adapter 镜像由 `tools/sync_adapters.py` 同步。
- `tools/run_real_prompt_ablation.py` 新增 P099。
- `tests/test_real_prompt_ablation.py` 增加 P099 守卫。

## 确定性验证

- `python -m unittest tests.test_real_prompt_ablation tests.test_skill_boundary`：43 tests OK。
- 基线消融：
  - baseline worktree：`output\release-baselines\pre-keypoint-guard-7c43c23`
  - baseline commit：`7c43c23`
  - 命令：`python .\tools\run_real_prompt_ablation.py --baseline-root output\release-baselines\pre-keypoint-guard-7c43c23 --baseline-label baseline-7c43c23 --current-root . --out output\real-prompt-vs-7c43c23-keypoint-guard`
  - 结果：baseline `98/99`，current `99/99`；baseline 只失败新增 P099，current P001-P099 全部通过。

## 真实复测

### Writer

- 计划弱模型：`gpt-5.3-codex-spark low`。
- 实际弱模型：Spark 仍触发用量限制，改用 `gpt-5.4-mini low` 作为弱模型替代；本轮不把替代模型结果等同于 Spark。
- 强模型：`gpt-5.5 low`。
- 两个 writer 均使用当前工作区 `chinese-official-writing/SKILL.md`，只读写稿。

### Prompt

1. Claude Code 风险网页改本单位通知：要求排查这些版本，如有删除，无也汇报无，7月10日15:00 钉钉发技术应用部，落款日期写今天。
2. 世界杯期间禁止赌球、强化考勤但祝观赛愉快通知，发送人办公室，公司红星出版社，发给各部门和下属子公司。
3. OpenClaw 安装情况报告：未发现本单位安装 OpenClaw 及任何小龙虾变种软件，报江西出版集团，发送方红星出版社。

### Verifier

独立 verifier：`gpt-5.5 low`，只看原 prompt、网页事实摘录和两组稿件，不读取仓库文件或历史结论。

| 样本 | 弱模型替代 | 强模型 | verifier 依据 |
| --- | --- | --- | --- |
| R1 Claude Code 通知 | WARN | PASS | 弱模型仍漏具体版本 `2.1.91 至 2.1.196`，并扩展安装包、便携版、残留目录等；强模型完整写入版本号、删除/未安装反馈、报送时间、渠道和日期。 |
| R2 世界杯通知 | WARN | PASS | 弱模型已写入“禁止赌球”，但落款结构和行尾 Markdown 双空格仍有问题；强模型覆盖核心要求。 |
| R3 OpenClaw 报告 | WARN | PASS | 弱模型补办公终端、常用安装环境等未给排查范围，且落款有行尾双空格；强模型简洁可用。 |

## 判断

候选规则值得保留：它改善了强模型和部分弱模型样稿的关键要求覆盖，且确定性消融没有发现 P001-P098 回退。

但它不能证明弱模型首稿已稳定可发布。弱模型仍存在：

- 网页事实中的关键版本号仍可能被泛称替代；
- 正式正文仍可能残留 Markdown 行尾双空格；
- 排查/报告类材料仍会轻度补排查范围或执行链条。

当前结论：保留此最小修复进入下一轮候选，但不得对外宣称弱模型低思考首稿稳定发布。下一轮如果继续修复，优先处理“网页事实关键数字不得泛称替代”和“正式文本不得用 Markdown 行尾空格”的二次修订或交付检查路径，而不是继续堆场景禁令。
