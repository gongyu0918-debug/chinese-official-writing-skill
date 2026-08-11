# 1.4.9 发布前真实写稿检查

日期：2026-06-28

本轮用于复核 `619519a` 后的最小 prompt 修复和 1.4.9 版本同步是否可发布。writer subagent 只读 `.agents/skills/chinese-official-writing/SKILL.md` 生成样稿，不修改仓库；独立 verifier 只看“原 prompt + 成稿”，按事实边界、文种格式、只审不改、缺项提示和 AI 味残留判断。

## Agent 分工

| Agent | 任务 | 结果 |
| --- | --- | --- |
| Mencius | 生成 6 条真实场景样稿 | 完成 |
| Nash | 独立 verifier 复核 6 条样稿 | `WARN`，无发布阻断 |

## 覆盖场景

| ID | 场景 | 检查点 | Verifier 结论 |
| --- | --- | --- | --- |
| W149-01 | 数据脱敏工具请示，资金来源、采购方式、供应商、验收指标缺失 | 缺项不阻断、正文后短列待确认、不编造 | PASS |
| W149-02 | 调研报告只给 3 项问题，禁止新增原因、影响范围和整改举措 | 去 AI 味不补事实 | WARN，未突破事实边界；末句略像审稿口径提示 |
| W149-03 | 只审不改，检查空话套话 | 不重写全文，按位置、风险层级、建议输出 | PASS |
| W149-04 | 字段式申请，只润色“申请事由”字段 | 字段边界、顺序和空值保留 | WARN，内容边界通过；原分号单行被改成分行字段 |
| W149-05 | 商请函 | 不写成通知或下行命令 | PASS |
| W149-06 | 180 字内压缩 | 限字、关键事实保留、无解释 | PASS，输出 117 字 |

## Verifier 总结

整体结论：`WARN`，`publish_blocking=false`。

非阻断观察项：

- `W149-02`：末句带审稿/口径提示色彩，作为调研报告正文略不自然。
- `W149-04`：用户要求按原格式时，输出将分号式单行改成分行字段；因字段名、顺序、边界和空值均保留，判定为非阻断格式偏移。

发布判断：可发布。上述两项留作后续观察，不在发布前临时扩大 prompt 修复，避免引入新的事实外扩或格式漂移风险。

## 发布前工程验证

已运行：

- `python -m unittest tests.test_skill_boundary -q`
  - 结果：29 tests OK。
- `python -m unittest tests.test_real_prompt_ablation tests.test_review_regressions tests.test_revision_instruction_eval tests.test_promptfoo_eval -q`
  - 结果：57 tests OK。
- `python C:\Users\admin\.codex\skills\.system\skill-creator\scripts\quick_validate.py .\chinese-official-writing`
  - 结果：Skill is valid。
- `python -m unittest discover -s tests -q`
  - 结果：86 tests OK。
- `$env:PROMPTFOO_PYTHON = 'C:\Users\admin\AppData\Local\Programs\Python\Python313\python.exe'; npm run eval:official-writing:smoke`
  - 结果：20/20 passed；skill win rate 1.0；judge consistency rate 1.0。
  - 说明：首次未设置 `PROMPTFOO_PYTHON` 时，promptfoo 因找不到 Python 退出；显式设置本机 Python 后通过。
- `python .\tools\run_real_prompt_ablation.py --baseline-root .\output\release-baselines\619519a --baseline-label baseline-619519a --current-root . --out .\output\real-prompt-vs-619519a-release-1.4.9`
  - 结果：baseline-619519a 54/54 通过，current 54/54 通过。
- `git diff --check`
  - 结果：通过。

## 结论

1.4.9 只做版本同步和发布前证据补充；行为基线仍是 `619519a` 的最小 prompt 修复。真实 subagent 测试未发现发布阻断，确定性消融未出现回归，允许发布 GitHub main 和 ClawHub 1.4.9。
