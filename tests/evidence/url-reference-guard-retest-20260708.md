# 2026-07-08 URL 指代关键范围候选复测

## 背景

上一轮“关键要点覆盖短检”候选改善了部分关键要求漏写问题，但弱模型在 Claude Code 链接通知中仍把用户所说“这些版本”泛化为“相关版本”，没有写入网页中的具体受影响版本号。

本轮只做一条 URL 指代边界最小修复：用户给 URL 并用“这些版本、上述名单、该事项、这篇文章”等指代网页内容时，应先提取网页中的具体名称、数字、版本范围、日期和主体；打不开网页、无法联网或来源无法核验时，不用泛称装作已经核验，而是在正文外提示需补充原文关键范围。

本轮未新增硬阻断、脚本清洗、默认单位风格搜索、场景特例或版本号。

## 修改范围

- `chinese-official-writing/SKILL.md`
- `chinese-official-writing/references/workflow.md`
- `chinese-official-writing/references/review-checklist.md`
- 对应 adapter 镜像由 `tools/sync_adapters.py` 同步。
- `tools/run_real_prompt_ablation.py` 新增 P100。
- `tests/test_real_prompt_ablation.py` 增加 P100 守卫。

## 确定性验证

- `python -m unittest tests.test_real_prompt_ablation tests.test_skill_boundary`：43 tests OK。
- 基线消融：
  - baseline worktree：`output\release-baselines\pre-url-reference-guard-b2431ce`
  - baseline commit：`b2431ce`
  - 命令：`python .\tools\run_real_prompt_ablation.py --baseline-root output\release-baselines\pre-url-reference-guard-b2431ce --baseline-label baseline-b2431ce --current-root . --out output\real-prompt-vs-b2431ce-url-reference-guard`
  - 结果：baseline `99/100`，current `100/100`；baseline 只失败新增 P100，current P001-P100 全部通过。

## 真实复测

### Prompt

把 `https://finance.eastmoney.com/a/202607083798236519.html` 改为本单位的通知，要求员工全面排查这些版本的 Claude Code，如有请删除，没有也要汇报无，汇报记录于 7月10日15:00 通过钉钉发送至技术应用部，落款日期写今天。

网页事实摘录：受影响版本为 `2.1.91 至 2.1.196`；建议安装受影响版本的开发终端卸载或升级；当前日期为 `2026-07-08`。

### Writer

- 弱模型替代：`gpt-5.4-mini low`。Spark 仍处于用量限制，本轮不把替代模型结果等同于 Spark。
- 强模型：`gpt-5.5 low`。
- 两个 writer 均使用当前工作区 `chinese-official-writing/SKILL.md`，只读写稿。

### Verifier

独立 verifier：`gpt-5.5 low`，只看原 prompt、网页事实摘录和两组稿件，不读取仓库文件或历史结论。

| 样本 | 判定 | 依据 |
| --- | --- | --- |
| 弱模型替代 | WARN | 已写入 `2.1.91 至 2.1.196`、删除、无也反馈、7月10日15:00、钉钉、技术应用部和 2026年7月8日；但仍补了开发终端、测试终端、替代工具切换、后续风险处置、外联权限管控和流量监测等治理链条。 |
| 强模型 | PASS | 已写入版本号、删除、无也反馈、7月10日15:00、钉钉、技术应用部和日期；整体围绕排查、删除、反馈展开，轻微扩写在可接受范围。 |

## 判断

候选规则值得保留：它针对性解决了“网页链接中的具体版本号被弱模型泛称替代”的问题，且确定性消融没有发现 P001-P099 回退。

但它仍不构成发布充分条件。弱模型仍会把安全风险通知扩展为未给出的治理和处置链条，尤其是：

- 开发终端、测试终端、共享设备等排查范围；
- 替代工具切换和后续风险处置；
- 外联权限管控、流量监测等安全治理措施；
- 个别落款仍有 Markdown 换行式排版痕迹。

下一轮若继续修复，应先确认这些“安全治理措施扩写”是否在多场景中达到三次共性；如果只在该 URL 通知中出现，不应继续做场景化补丁。
