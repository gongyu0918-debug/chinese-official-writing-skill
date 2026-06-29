# Release 1.4.12 Evidence

Date: 2026-06-29

Release target: `chinese-official-writing@1.4.12`

Baseline: `v1.4.11` / `origin/main` commit `89948800d9616cb207f7d263948db7f51bc2441c`

Pre-release remote state:

- `git fetch origin`: completed.
- `git rev-list --left-right --count origin/main...HEAD`: `0 3`.
- Latest local tag before release: `v1.4.11`.
- `clawhub inspect chinese-official-writing --json`: `latestVersion.version=1.4.11`, moderation `clean`.

## Release Scope

This release publishes the three local commits after 1.4.11:

- `cddf211`: record 1.4.11 follow-up review gaps.
- `db5607b`: review Hermes community borrowing candidate.
- `57ffdc0`: minimal community borrowing implementation.

Behavior changes relative to 1.4.11:

- Adds soft high-risk-first review layering.
- Prevents oral source phrases such as `老板关心`, `钱花得值`, and `马上要搞` from being upgraded into unsupported strong conclusions.
- Adds light genre reference order hints that do not override user templates, field-style materials, web-copied drafts, or existing heading order.
- Keeps lint as a warning layer and weakens over-strong oral-source suggestions.

Not included:

- No `format_docx.py`.
- No paragraph-isomorphism lint.
- No hard gate or auto-cleaning script.
- No change to OpenClaw name compatibility rule.

## Version Sync

- `chinese-official-writing/SKILL.md`: `1.4.12`.
- `tools/sync_adapters.py`: `VERSION = "1.4.12"`.
- Synced adapters: `skills/`, `.agents/`, `.qwen/`, `hermes/`, `openclaw/`, `.claude-plugin/plugin.json`, root README, OpenClaw README, marketplace README, and skill card.

## Verification

- `python .\tools\sync_adapters.py`
  - Passed.
- `python -m unittest discover -s tests -v`
  - 93 tests OK.
- `python .\tools\run_real_prompt_ablation.py --baseline-root .\output\release-baselines\v1.4.11-release-1.4.12 --baseline-label baseline-v1.4.11 --current-root . --out .\output\real-prompt-vs-1.4.11-release-1.4.12`
  - `baseline-v1.4.11`: 55 cases, 54 passed, 1 failed.
  - `current`: 55 cases, 55 passed, 0 failed.
  - The only baseline failure is new P055; current has no regression.
- `python C:\Users\admin\.codex\skills\.system\skill-creator\scripts\quick_validate.py .\chinese-official-writing`
  - Skill is valid.
- `git diff --check`
  - Passed.
- `$env:PROMPTFOO_PYTHON='C:\Users\admin\AppData\Local\Programs\Python\Python313\python.exe'; npm run eval:official-writing:smoke`
  - 20/20 passed.
  - `skill_win_rate=1.0`.
  - `judge_consistency_rate=1.0`.

## Real Subagent Test

Writer subagent: `019f1303-13ab-7d11-898d-7e3c4706c5b0`

Verifier subagent: `019f1305-167f-7bb1-9379-371ca0c02720`

Coverage:

- T1: oral-source formalization without unsupported strong conclusions.
- T2: fixed two-paragraph notice template with missing date/contact.
- T3:商请函 with missing amount, feedback deadline, contact, and attachment list.
- T4: review-only AI taste and format risk check.

Verifier result:

- T1 PASS.
- T2 PASS.
- T3 PASS.
- T4 PASS.
- `overall=PASS`.
- `publish_blocking=false`.

## Release Notes Draft

chinese-official-writing 1.4.12 更新说明

- 增加定稿前高风险先查清单，帮助优先发现文种、缺项、模板、格式和过程泄露风险。
- 收紧口语来源事实边界，避免把“老板关心”“钱花得值”“马上要搞”等表达升级为未给出的强结论。
- 为通知、请示、报告、方案、申请、函补充轻量写作顺序参照，并明确不覆盖用户模板和字段式材料。
- 调整 lint 的口语提示文案，继续提示风险但不诱导固定强替换。

## Remaining Risk

- This release still relies on prompt/reference guidance for real model behavior. Future review loops should continue watching for over-strong fiscal conclusions when users provide only oral-source material.
- The promptfoo warning about a newer promptfoo version is not release-blocking; the smoke suite completed successfully on the pinned local version.
