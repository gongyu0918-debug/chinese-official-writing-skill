# 1.5.0 文种 Playbook 架构候选验证记录

日期：2026-07-04

本轮只做本地候选提交，不发布、不打 tag、不 bump 1.5.0。基线固定为 GitHub/ClawHub 1.4.15 对应的 `origin/main` commit `9c218ea849449a9aced6ad101e2a05fc21b233e0`。

## 修改范围

- 新增 `references/genre-playbooks.md`，按文种和专项提供轻量骨架、误区和补充读取路径。
- `SKILL.md` 增加按文种/专项选读入口；`agent_writer.py` 增加 playbook 路由，未知泛文种不默认加载。
- 将分散在通用文档里的 AI 算力细节收束为指向 `ai-compute-docs.md`；普通采购明确不进入 AI 算力语境。
- 针对真实 A/B 暴露的问题，补强字段式材料规则：即使用分号串写为一行，只要是“字段名：字段值”序列，也按字段单元处理，改写时优先逐字段独立成行。
- 同步 `skills/`、`.agents/`、`.qwen/`、`hermes/`、`openclaw/` 镜像。

未做事项：

- 未引入脚本硬门禁、默认联网、API、Word/PDF 重排版引擎或检测器。
- 未复制社区技能模板正文、脚本、正则、固定话术或大段 prompt。
- 未发布 1.5.0。

## Subagent 复核

只读 diff 审核：

- Ohm：PASS with WARNs。未发现硬门禁、默认网络/API、模板抄袭或普通材料 AI 算力偏置；提醒新 `genre-playbooks.md` 必须纳入 commit，版本仍是 1.4.15，适合本地候选但不能直接当 1.5.0 发布。

真实 A/B 写稿：

- Erdos 使用 1.4.15 baseline skill 生成 W01-W08。
- Planck 使用当前候选 skill 生成同组 W01-W08。
- Kierkegaard 盲评 A/B，发现当前候选在 W07 字段式审查材料中把多个字段合并成一行，判定为 material regression；W02、W04 有轻微事实/字段风险。

修复后复测：

- Pascal 复测 R02/R04/R07，R07 仍把分号串字段合并成一行，因此继续上移规则到 `SKILL.md`、`workflow.md`、`review-checklist.md`。
- Ampere 重新只测 R07，输出保持逐字段独立行，仅替换 `审查意见` 字段，回归解除。

## 验证结果

已运行：

- `python .\tools\sync_adapters.py`：通过。
- `python -m unittest tests.test_skill_boundary tests.test_real_prompt_ablation tests.test_promptfoo_eval -v`：54 tests OK。
- `python .\tools\run_real_prompt_ablation.py --baseline-root .\output\release-baselines\github-1.4.15 --baseline-label baseline-1.4.15 --current-root . --out .\output\real-prompt-vs-1.4.15-playbook-architecture-fieldfix`：退出码 0。
  - baseline-1.4.15：79 用例，71 通过，8 失败。
  - current：79 用例，79 通过，0 失败。
  - baseline 失败集中在新增 P072-P079；P001-P071 未观察到确定性回退。
- `python -m unittest discover -s tests -v`：99 tests OK。
- `python .\tools\run_real_article_eval.py --out output\real-article-playbook-architecture-fieldfix`：退出码 0。
  - skill：10 样本，平均差异率 0.00%，关键词命中率 100.00%，格式风险 0，重复事项 0，反 AI 风险 0。
  - 该工具仍提示匿名占位词风险样本 9，属于真实样文回归工具的复核提示，不等同质量通过证明。
- `& 'C:\Users\admin\AppData\Local\Programs\Python\Python313\python.exe' evals/official-writing/run_eval.py --suite smoke --judge-batch-size 2`：通过。
  - promptfoo smoke：20/20 passed。
  - pairwise：skill 10，baseline 0，tie 0，needs_manual_review 0，judge_consistency_rate 1.0。
- `git diff --check`：通过；只有 Windows LF/CRLF 提示，无 whitespace error。

说明：

- 直接运行 `npm run eval:official-writing:smoke` 在沙箱内失败，原因是外层 `python` 解析到已失效的 Hermes venv，且 promptfoo 清理 `.promptfoo/logs` 受限。已用同一 `run_eval.py` 入口指定真实 Python 3.13 并在沙箱外复跑通过。

## 结论

当前候选可以作为本地 1.5.0 架构候选提交，但不应直接发布。下一轮如准备正式 1.5.0，需要重新 bump 版本、完整跑发布验证、真实安装/inspect，并在 GitHub/ClawHub 发布后确认 live 版本和 moderation 状态。

剩余风险：

- Playbook 属于 prompt/reference 层优化，真实模型输出仍需继续用 subagent 和真实材料复核。
- 本轮未做外部发布链路验证。
- 真实样文回归工具的匿名占位词风险仍需在正式发布前结合人工或 LLM judge 解释。
