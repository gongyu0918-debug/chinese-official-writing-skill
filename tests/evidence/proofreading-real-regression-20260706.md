# AI 写稿校对层真实回归测试

日期：2026-07-06

本轮基于 `01cb9eee1599a957b357f5db23aed5a20125bb58` 继续测试 AI 写稿轻量校对层。测试目标是确认传统写稿链路、新增 proofreading workflow、长程写作、多轮写作、精准回滚和 compact 后继续修改没有功能性回退。

## 基线和消融

- Baseline worktree：`output/release-baselines/proofreading-parent-01cb9ee`，对应 `01cb9ee^` / `ee1127e docs: record 1.5.1 publish status`。
- 首轮消融：`python .\tools\run_real_prompt_ablation.py --baseline-root .\output\release-baselines\proofreading-parent-01cb9ee --baseline-label baseline-before-proofreading --current-root . --out .\output\real-prompt-vs-before-proofreading-20260706`
  - `baseline-before-proofreading`：85 用例，84 通过，1 失败。
  - `current`：85 用例，85 通过，0 失败。
  - 旧基线只在新增 P085 proofreading reference 边界用例失败。
- 修复后消融：`python .\tools\run_real_prompt_ablation.py --baseline-root .\output\release-baselines\proofreading-parent-01cb9ee --baseline-label baseline-before-proofreading --current-root . --out .\output\real-prompt-vs-before-proofreading-fixed-20260706`
  - `baseline-before-proofreading`：85 用例，84 通过，1 失败。
  - `current`：85 用例，85 通过，0 失败。

## 真实 subagent 测试

### 传统基线链路

Writer：`019f36b8-95a7-75c0-8804-0c536d38456c`

覆盖：

- `T1` 请示起草，缺成文日期和联系人。
- `T2` 通知起草，含时限、OA 渠道和联系人。
- `T3` 函起草，平行商请车辆临停支持。
- `T4` 字段式申请改写，只改“用途”字段。
- `T5` 只审不改，不重写全文、不打分。

结果：5/5 可用。未见 proofreading 层把传统写稿链路变成校对报告、追问流程或事实核验流程。

### 新增 proofreading workflow 链路

Writer：`019f36b8-e572-7863-bfe8-e1a374e71733`

覆盖：

- `P1` 半角标点、错别字/语法顺稿，只输出正文。
- `P2` 领导原句和古诗词引用保留。
- `P3` 金额、日期口径冲突，不联网、不自选口径。
- `P4` 成语逐项处理。
- `P5` 政策原文保护，缺实施时间和责任科室。

结果：3 个核心边界稳定；发现 2 个同类 proofreading 保真观察：

- `P2` 末尾提示写成 `请核实引用出处。`，未使用固定短句。
- `P4` 成语处理偏保守，未保留可能可用的 `久久为功`。

### 长程、多轮、回滚和 compact 链路

Writer：`019f36ba-7fcf-7dc1-acbd-76b3eefe734b`

覆盖：

- `L1` 900-1100 字校园消防安全专项整治工作方案。
- `L2` 多轮新增自然段后撤回，回到第一版结构。
- `L3` 收文单位误改后恢复，其他润色保留。
- `L4` compact 交接摘要后，只压缩必要性部分，不重写全文。
- `L5` 用户明确“回滚此次修改，恢复原样”后，继续只改语气。

结果：5/5 可用。`L5` 精准撤销了第二轮 `7月15日` 和 `逾期未报将纳入月度通报`，保留原 `7月12日` 和联系人，并完成第四轮语气修改。

## 独立 verifier 结论

Verifier A：`019f36bb-fde8-79b2-9d64-651914695881`

- 14 PASS，1 WARN。
- WARN：`P4` 成语保留偏保守，属于单例观察。
- 共性问题：无三次以上共性问题。
- 建议：不做大范围 prompt 修复。

Verifier B：`019f36bc-4001-7c80-a078-51a28c824338`

- 传统写稿退化：0/5。
- proofreading 默认联网、事实核验、长报告化：0/5。
- 长程、多轮、compact、精准回滚失败：0。
- 引用/成语保真偏差：2/5，建议只做 proofreading 边界最小修复。

## 最小修复

接受最小修复项：引用核实提示句不稳定。

修复范围：

- `chinese-official-writing/SKILL.md`
- `chinese-official-writing/references/proofreading-checklist.md`
- 各适配器镜像
- `tests/test_skill_boundary.py`

修复内容：

- 最终稿保留用户给定引用时，末尾使用固定短句：`引用表述、出处和发布日期建议由用户按原始材料核实。`
- 除非用户另给提示语，不改写成 `请核实出处`、`请自行核实` 等泛泛提醒。

未修复项：

- 成语保留偏保守未单独修复。定向复测显示 Q3/Q4 已能逐项替换误用成语并保留 `久久为功`，未形成稳定共性失败。

## 修复后真实复测

Writer：`019f36c0-0807-76c0-9815-b24598272c6e`

覆盖：

- `Q1` 讲话稿引用保真。
- `Q2` 政策原文保护。
- `Q3` 成语逐项处理。
- `Q4` 成语合适保留。

结果：

- `Q1` / `Q2` 均使用固定短句：`引用表述、出处和发布日期建议由用户按原始材料核实。`
- `Q3` 保留 `久久为功`，替换不合语境表达。
- `Q4` 保留 `久久为功`、`一蹴而就`、`举一反三`、`立行立改`。

## 命令验证

- `python .\tools\sync_adapters.py`：普通沙箱因 `.agents` 权限失败；提升权限后通过。
- `python -m unittest tests.test_skill_boundary tests.test_review_regressions tests.test_real_prompt_ablation -v`：78 tests OK。
- `python -m unittest discover -s tests -v`：105 tests OK。
- `npm run eval:official-writing:smoke`：20/20 passed。普通沙箱会因 Node spawn Python `EPERM` 失败；提升权限并将 Python 3.13 放到 PATH 前后通过。
- `git diff --check`：通过。

## 结论

传统基线写稿、字段式改写、只审不改、新 proofreading workflow、长程写作、多轮修改、精确回滚和 compact 后继续修改均未见功能性回退。已对重复出现的引用提示句不稳定做 prompt 层最小修复，不新增脚本清洗、硬门禁、默认联网、模型或 API。

## 剩余风险

- compact 测试是基于压缩交接摘要模拟，不是一次真实上下文耗尽后的系统级 compaction 事件。
- 长程写作只覆盖 1 个约千字方案样本，尚未覆盖 3000 字以上调研报告、可研报告或多附件合稿。
- 本轮未做 Word/docx 真实排版链路；校对层不应影响 Word，但正式发布前仍建议另跑 docx 场景。
- 成语处理目前只有一次初始 WARN，后续定向复测通过；继续观察不同文体下“低语境符合”判断是否过度保守。
