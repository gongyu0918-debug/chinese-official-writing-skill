# 1.4.10 Hermes/GLM Review 复现、修复与发布前测试

日期：2026-06-28

本轮依据 `C:\Users\admin\Desktop\chinese-official-writing-Review-报告.md` 做发布前复现和最小修复。报告不能直接采信；每项 finding 先复现，再决定接受、拒绝或延期。候选 commit `9385784` 已在本工作区可见，本轮按源码、diff、测试和独立 subagent 复核重新验证。

## Git 基线

- 复现基线：`76c212a`，即已发布的 1.4.9。
- 当前修复：`9385784`，后续将作为 1.4.10 行为基础。
- `git fetch origin` 后 `origin/main...HEAD` 为 `0 2`，远端无本地缺失提交。
- 未纳入提交项：`.clawhub/` 本地目录。

## 接受并修复

| Finding | 复现证据 | 修复证据 | 结论 |
| --- | --- | --- | --- |
| R-1 / S-3 / A-1 高频风险句式 lint 漏检 | 1.4.9 基线 13 条高频句式命中 `0/13` | 当前 HEAD 命中 `13/13`；新增 `test_anti_ai_reference_high_frequency_phrases_are_linted` | 接受并修复 |
| S-1 / S-2 `--format` 代码围栏内格式漏扫和 `core_compiled` 冗余 | 1.4.9 基线围栏第 2 行命中标签为空，源码存在 `core_compiled` | 当前 HEAD 围栏第 2 行命中 `emoji-marker`、`halfwidth-punctuation`、`markdown-bold`，源码不再含 `core_compiled` | 接受并修复 |
| P-1 起草规则 730 字单 bullet 过密 | 1.4.9 基线起草规则最长 730 字，0 个子 bullet | 当前 HEAD 起草规则最长 181 字，6 个子 bullet；新增边界测试约束 | 接受并修复 |

直接复现脚本结果：

```text
=== baseline-1.4.9
phrase_matched=0/13 lines=[]
fence_line2_labels=[]
drafting_max_len=730 child_bullets=0
has_core_compiled=True
=== current
phrase_matched=13/13 lines=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
fence_line2_labels=['emoji-marker', 'halfwidth-punctuation', 'markdown-bold']
drafting_max_len=181 child_bullets=6
has_core_compiled=False
```

## 拒绝或延期

| Finding | 处理 | 理由 |
| --- | --- | --- |
| X-1 OpenClaw `name` 下划线 vs 连字符 | 拒绝 | `openclaw/README.md` 和根 README 明确说明 OpenClaw 适配副本使用 `name: chinese_official_writing` 是当前匹配规则，ClawHub slug 仍为 `chinese-official-writing`；未复现实际加载断裂。 |
| D-1 / D-2 / R-2 / R-3 / S-4 / S-5 / A-2 / P-2 / P-3 / X-2 | 延期 | 仅为设计或低风险观察，未复现明确失败。P-2 已被 P-1 部分缓解；其余不进入本轮最小修复。 |

## 独立只读复核

独立 explorer subagent 读取 review 报告、`76c212a..HEAD` diff、源码和测试后结论：

- `publish_blocking=false`。
- `R-1/S-3/A-1`、`S-1/S-2`、`P-1` 均为 `minimal_fixed`。
- `X-1` 为 `reject_finding`。
- 其余 finding 均 `defer`，无明确失败证据。

## 真实 subagent 写稿/审稿测试

writer subagents 只读 `.agents/skills/chinese-official-writing/SKILL.md`，不修改仓库。verifier subagent 只看 prompt 和输出。

覆盖场景：

- `R1410-A1`：请示，缺金额、采购方式、供应商、合同日期、联系人。
- `R1410-A2`：通知，缺报送截止日期、邮箱、联系人。
- `R1410-A3`：函，缺项目附件、回函日期、联系人。
- `R1410-B1`：字段式材料只润色申请事由。
- `R1410-B2`：只审不改，不重写、不评分。
- `R1410-C1`：去 AI 味 / format lint，只提示风险，不自动清洗。

独立 verifier 结论：`PASS_WITH_WARNINGS`，`publish_blocking=false`。

- 请示、通知、函均未编造缺失金额、日期、联系人、供应商或附件。
- 字段式材料保持字段名、顺序和空字段，只润色指定字段。
- 只审不改输出位置、风险层级和建议，未重写全文，未打 0-100 分。
- lint 场景明确只提示风险，不自动清洗；命中新增 AI 味和围栏内 format 标签。
- 轻微观察项：通知里新增“暂未发生目录更新也请说明”等执行要求，虽合理但不是用户明确事实，后续继续观察。

## 测试命令

已运行：

- `python .\tools\sync_adapters.py`
  - 结果：同步完成，无新增 diff。
- `python -m unittest tests.test_review_regressions tests.test_skill_boundary -v`
  - 结果：55 tests OK。
- `python -m unittest discover -s tests -v`
  - 结果：89 tests OK。
- `$env:PROMPTFOO_PYTHON = 'C:\Users\admin\AppData\Local\Programs\Python\Python313\python.exe'; npm run eval:official-writing:smoke`
  - 结果：20/20 passed，skill win rate 1.0，judge consistency rate 1.0。
- `git diff --check`
  - 结果：通过。
- `python .\tools\run_real_prompt_ablation.py --baseline-root .\output\release-baselines\github-1.4.9-review --baseline-label baseline-1.4.9 --current-root . --out .\output\real-prompt-vs-1.4.9-release-1.4.10`
  - 结果：baseline-1.4.9 54/54 通过，current 54/54 通过。

## 结论

本轮只保留 review 已复现的最小修复：补齐 prose_lint 高频风险句式、修复代码围栏内 `--format` 漏扫、拆分过密起草规则。未复现明确失败的 finding 不扩修。当前修复通过确定性测试、基线消融和真实 subagent 测试，可进入 1.4.10 版本同步和发布。
