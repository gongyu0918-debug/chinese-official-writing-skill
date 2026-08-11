# GLM5.2 + OpenCode Review 复现与最小修复记录

日期：2026-07-02

## 基线核验

- GitHub `origin/main`：`b2fc5ba983e6544f5a791b3f3df82c821016e698`。
- GitHub tag `v1.4.12`：`d7524bde5cb4fe69d2fb4b9572d10a8253afe2f5`。
- ClawHub CLI：`chinese-official-writing` latest 为 `1.4.12`，moderation `CLEAN`。
- 本地 `HEAD` 在修复前为 `b3234ce`，比 GitHub main 多两个本地 docs/evidence 提交；这些提交只改 `AGENTS.md` 和测试证据，不改 skill 包行为文件。

结论：GitHub main 与 ClawHub 发行基线一致；本轮以 GitHub/ClawHub 发行基线 `b2fc5ba` 作为消融基线。

## Review Finding 处理

| Finding | 结论 | 处理 |
| --- | --- | --- |
| ClawHub/OpenClaw 市场版 SKILL.md 弱于 canonical | 接受 | 只在 `tools/sync_adapters.py` 生成的 Agent 使用规则中补一句：遇到事实、文种、行文关系、用户模板或结构锁定问题时回看 canonical `SKILL.md` 硬边界和 `references/final-review-layers.md`、`references/review-checklist.md`；不把 canonical 全量塞进市场版。 |
| `prose_lint` 误扫正文外待确认区 | 接受 | 在 `prose_lint.py` 增加正文区边界识别，遇到 `待确认事项`、`补充以下信息后` 等正文外缺项提示后停止扫描正文风险；补回归测试。 |
| `prose_lint` 不覆盖文种要素完整性 | 接受 | 在 `SKILL.md` 和 README 声明脚本只提示语言、格式和重复风险，不替代文种、行文关系和办理要素复核。 |
| `run_real_article_eval.point_covered` 标点脆性 | 部分接受 | `normalize()` 改为去除中文标点和符号，使 `《请示》收悉` 可覆盖 `请示收悉`；OR 同义词结构和标签型 term 重构暂缓，避免一次改变评估语义过大。 |
| 限字计数口径 | 接受 | `workflow.md` 和 `review-checklist.md` 补充按用户明示口径计数；用户说含标题、主送、落款时全稿计数，未说明时按正文计数。 |
| 推断性具体化 | 接受 | `workflow.md` 和 `review-checklist.md` 补充类别性软提醒：耗材、交通、日志字段、整改数量、资金节约额等仅由语境推断的信息不当作已知事实。 |
| “补一句”变新增节 | 接受 | `workflow.md` 和 `review-checklist.md` 补充句/段/节粒度规则。 |
| R1 改写补造具体数据 | 暂缓 | 归入推断性具体化风险，不做一例一修。 |
| `.pyc` 缓存 | 拒绝 | 已被 `.gitignore` 忽略，非产品问题。 |
| ClawHub CLI Windows uv 断言日志 | 拒绝 | 外部 CLI/Node Windows 退出噪声，命令本身成功返回版本信息。 |

## 真实 Prompt 写稿测试

4 个 writer subagent 使用当前 skill 生成样稿，独立 verifier 只看 prompt 和输出判定：

| 样本 | 覆盖风险 | Verifier |
| --- | --- | --- |
| W1 通知压缩，180 字含标题主送落款 | 限字口径、要点保留 | PASS |
| W2 只在第二段末尾补一句联系人 | 句段节粒度、结构锁定 | PASS |
| W3 申请说明不补造具体用途 | 推断性具体化、缺项正文后一句 | PASS |
| W4 商请函不列具体日志字段 | 平行文、事实边界、正文后缺项 | PASS |

Verifier 结论：未发现 3 次以上共性问题；整体遵循用户明确指令，事实边界和结构边界控制较好。

## 验证命令

- `python -m unittest tests.test_review_regressions`：30 tests OK。
- `python -m unittest discover -s tests`：95 tests OK。
- `npm run eval:official-writing:smoke`：20/20 passed，skill win rate 100%，judge consistency 100%。
- `python .\tools\run_real_article_eval.py --out output\real-article-glm-opencode-review`：生成 `output/real-article-glm-opencode-review/summary.md`。
- `python .\tools\run_real_prompt_ablation.py --baseline-root output\release-baselines\github-1.4.12 --baseline-label baseline-1.4.12 --current-root . --out output\real-prompt-vs-1.4.12-glm-opencode-review`：baseline 55/55，通过；current 55/55，通过。
- `python .\tools\sync_adapters.py`：同步完成。

## 剩余边界

- 真实文章 eval 的标签型 term（如“通报对象”“主送单位”“征求对象”）仍可能导致占位词风险或绝对分解释偏差。本轮只修标点归一化，OR 同义词和夹具 term 重构暂缓。
- 本轮未 bump 版本号，未发布 GitHub 或 ClawHub；只是针对 review finding 做本地最小修复与验证。
