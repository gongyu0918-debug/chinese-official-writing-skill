# 1.5.4 交付 Review 复核与最小修复记录

日期：2026-07-09

输入报告：`C:\Users\2\Desktop\中文公文写作skill-1.5.4-交付Review报告.md`

本轮目标是复核报告中的膨胀风险，选择性接受或拒绝，并用当前 1.5.4 基线做确定性消融和真实写稿 A/B。未做版本号变更，未发布远端。

## 复核结论

报告的总体判断成立：1.5.4 没有明确功能性回退，但 prompt/reference 已接近膨胀天花板，不能继续靠枚举式补丁扩写入口规则。

## 接受并修复

1. `task-route-cards.md` 缺少“何时必须转读长 reference”的明确条件。
   - 复现：卡片原文只写“仍复杂时再转读”，对完整文种骨架、长文、多材料合稿、专项论证和正式 Word 交付没有显式触发条件。
   - 修复：在卡片顶部增加一行短规则，明确完整文种骨架、800 字以上长文、多材料合稿、会议纪要/可研/采购/AI 算力专项论证、GB/T 9704 或 Word 正式交付等必须转读长 reference。

2. `genre-playbooks.md` 中通报小节重复事实映射式二次修改细则，存在 single source of truth 风险。
   - 复现：事实映射细则同时分散在 `SKILL.md`、`workflow.md` 和 `genre-playbooks.md`。
   - 修复：不删除既有测试锚点，只把通报 playbook 中对应句改为“按 `workflow.md` 的事实映射式二次修改”，让细则以 `workflow.md` 为主源。

## 拒绝或延期

1. 暂不压缩 `SKILL.md` 的硬边界入口。
   - 理由：仓库历史证据 `attention-compression-ab-20260709.md`、`split-drafting-rules-ab-20260709.md`、`prompt-density-community-review-20260709.md` 显示，入口压缩或拆行在弱模型真实写作 A/B 中出现事实关系错误、Markdown 残留或既有锚点丢失。当前没有新的证据支持再次压缩。

2. 暂不拆分 `workflow.md` 的事实充分性长段。
   - 理由：`reference-density-ab-rollback-20260709.md` 已记录“更短、更分块”没有改善弱模型，反而引入事实外扩和格式噪声。本轮只做指针化，不重排该段。

3. 暂不新增 lint、脚本清洗或 final-draft inspection 硬流程。
   - 理由：本轮 review 的主要结论是停止继续堆规则；新增硬机制会扩大范围，也不符合本技能“软性 prompt 优先、真实写作验证优先”的边界。

## 确定性消融

基线：`output\release-baselines\local-1.5.4-48f3190`，提交 `48f3190b704e0486f09e5b44f4c6a1e3efc91bcd`。

命令：

```text
C:\Users\2\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe .\tools\run_real_prompt_ablation.py --baseline-root output\release-baselines\local-1.5.4-48f3190 --baseline-label baseline-1.5.4 --current-root . --out output\real-prompt-vs-1.5.4-review-fix
```

结果：`baseline-1.5.4 95/95`，`current 95/95`。未发现确定性规则覆盖回退。

## 真实写稿 A/B

按用户要求使用 subagent。writer 只读各自 Skill，不修改仓库；verifier 只看 prompt 和两组输出，不读仓库或历史结论。

- Baseline writer：`019f44de-05a4-7661-a39b-6ee51015ae86`，`gpt-5.4-mini low`，读取 `output\release-baselines\local-1.5.4-48f3190\chinese-official-writing\SKILL.md`。
- Current writer：`019f44de-4f23-7ea0-90af-389fdadd3afd`，`gpt-5.4-mini low`，读取当前 `chinese-official-writing\SKILL.md`。
- Verifier：`019f44df-77c1-7f31-886c-ed97e5c7fb58`，`gpt-5.5 low`。

覆盖任务：

1. 900 字以内版慎通成本治理建议，要求保持建议口径，不写成已定实施方案或执行命令。
2. 通报二次修改，要求删掉未给事实，不新增会议内容、问题清单、闭环督办、联系人或完成时限。

verifier 结论：

- 任务 A：baseline PASS，current PASS。current 保留关键要点，使用“建议、可、宜、先行试行”等建议性表述，未升级为强制实施命令。
- 任务 B：baseline PASS，current PASS。current 正文只保留 12 个系统、3 类问题、2 次协调会和待补责任人、更新周期；未新增会议内容、处理边界、问题清单、闭环机制、督办安排、联系人或完成时限。
- current 是否回退：NO。
- WARN/FAIL：无发布阻断。

## 测试锚点

新增边界测试：

- `test_task_route_cards_keep_sparse_tasks_lightweight` 增加“必须转读长 reference”的触发条件锚点。
- `test_weak_model_suggestion_boundaries_stay_soft` 增加 `genre-playbooks.md` 指向 `workflow.md` 的事实映射锚点，并确认 `workflow.md` 保留主源细则。

定向测试：

```text
C:\Users\2\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m unittest tests.test_skill_boundary tests.test_real_prompt_ablation
```

结果：43 tests OK。

发布前最小验证：

```text
C:\Users\2\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m unittest discover -s tests
C:\Users\2\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe evals\official-writing\run_eval.py --suite smoke --judge-batch-size 2
C:\Users\2\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe .\tools\run_real_article_eval.py --out output\real-article-review-fix-1.5.4-delivery
C:\Users\2\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe C:\Users\2\.codex\skills\.system\skill-creator\scripts\quick_validate.py chinese-official-writing
git -C . diff --check
```

结果：

- 全量 unittest：107 tests OK。
- smoke eval：20/20 passed，skill_win_rate `1.0`，judge_consistency_rate `1.0`。首次运行因 `promptfoo` 依赖访问 npm registry 被系统网络权限拦截失败，提升权限重跑后通过。
- 真实样文回归：`output\real-article-review-fix-1.5.4-delivery\summary.md` 已生成；skill 模式 10 样本关键要素覆盖 61/61，格式风险 0，重复事项 0，反 AI 风险 0；仍有匿名标签式占位词风险样本，属该回归工具既有提示，需人工或 LLM judge 复核。
- quick_validate：`Skill is valid!`
- diff check：通过，仅有 Windows CRLF 提示。

## 剩余风险

- `SKILL.md` 入口和 `workflow.md` 事实充分性段仍偏重，但历史真实 A/B 不支持本轮继续压缩。
- 弱模型首稿仍可能出现格式噪点，当前验收口径仍应重点看事实边界、禁止项和二次修改可交付性。
