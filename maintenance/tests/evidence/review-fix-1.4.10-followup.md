# 1.4.10 Hermes/GLM Follow-up Review Fix Evidence

Date: 2026-06-28

Scope: follow-up review reports:

- `C:\Users\admin\Desktop\chinese-official-writing-Review-1.4.10.md`
- `C:\Users\admin\Desktop\chinese-official-writing-Review-1.4.10-扩大范围.md`

Baseline: GitHub/main `d8d7ee0a96a0c0b822446bd70d1d417eef2a729e` (`chinese-official-writing@1.4.10`).

## Findings

Accepted and minimally fixed:

- `N-1`: `可以说` matched `不可以说`. Fixed by narrowing the regex to `(?<!不)可以说[，,]`.
- `N-2`: `综上所述` matched section-reference text such as `本文综上所述部分如下`. Fixed by requiring punctuation: `综上所述[，,]`.
- `B3`: `经现场检查，未发现重大隐患` was flagged even though an explicit check basis is present. Fixed by skipping `unsupported-conclusion` only when the same line immediately contains `经...检查/核查/评估/审查` before the conclusion.
- `N-3`: long-form方案 output could retain Markdown bold headings. Fixed at prompt level by adding a common-error reminder that long-form official drafts use Chinese heading markers or ordinary headings, not `**加粗**`, `###`, or code fences.

Deferred:

- `B1`: `高度重视` can be a valid official phrase, but current severity is `low` and the lint advice is only a quality reminder. No change.
- `B2`: `有关方面认为` can appear in research context, but it is still vague attribution and should usually ask for clearer source. No change.

## Direct Reproduction

Direct lint repro after the fix:

- `不可以说这个方案没有问题。` -> no finding.
- `本文综上所述部分如下。` -> no finding.
- `经现场检查，未发现重大隐患。` -> no `unsupported-conclusion`.
- `未发现重大隐患。` -> `medium/unsupported-conclusion`.
- `可以说，项目建设很有必要。` -> `medium/side-commentary`.
- `综上所述，本项工作意义重大。` -> `medium/side-commentary`.
- `**一、活动安排**` -> `low/markdown-bold`.
- Code fence with halfwidth punctuation, emoji, and bold still emits `markdown-code-fence`, `halfwidth-punctuation`, `emoji-marker`, and `markdown-bold`.

## Subagent Cross-check

Read-only verifier subagent `019f0ed1-b2be-7f02-a31b-b531462c713c` independently reviewed both reports and current source. Result:

- Accept: `N-1`, `N-2`, `B3`, `N-3`.
- Defer: `B1`, `B2`.
- No recommended expansion beyond the minimal regex/prompt fixes above.

## Real Subagent Skill Test

Writer subagents used the local `.agents/skills/chinese-official-writing/SKILL.md` package.

Coverage:

- Long activity方案 based on public节能宣传周/低碳日 material: no Markdown bold or `###`; missing dates, funding, and contact were listed as待确认.
- Maintenance-service请示: missing budget, procurement method, supplier, contract dates, and contact were not fabricated.
- Field-form rewrite: preserved field names/order/empty values; only the requested field was improved.
- Review-only: produced positions, risk levels, and suggestions; did not rewrite full text or score 0-100.
- Lint boundary judgment: matched direct lint behavior for `不可以说`, `综上所述` section reference, explicit check basis, unsupported conclusion, and vague attribution.

Independent verifier subagent `019f0edb-fed1-7b01-8f11-778eb9961d4a` result:

- `overall_verdict=PASS`
- `publish_blocking=false`
- All tested cases PASS.

Verifier noted that A1 used `市发展改革委`; the original prompt explicitly requested a draft for `市发展改革委`, so this was not an unprovided-fact issue.

## Deterministic Validation

Commands run:

- `python .\tools\sync_adapters.py`: OK after rerun with file-write permissions.
- `python -m unittest tests.test_review_regressions tests.test_skill_boundary -v`: 58 tests OK. A sandbox-only `tempfile` permission error was reproduced before rerun; elevated rerun passed.
- `python -m unittest discover -s tests -v`: 92 tests OK.
- `$env:PROMPTFOO_PYTHON='C:\Users\admin\AppData\Local\Programs\Python\Python313\python.exe'; npm run eval:official-writing:smoke`: 20/20 passed, skill win rate 1.0, judge consistency rate 1.0.
- `python .\tools\run_real_prompt_ablation.py --baseline-root .\output\release-baselines\github-1.4.10-review-fix --baseline-label baseline-1.4.10 --current-root . --out .\output\real-prompt-vs-1.4.10-review-fix`: baseline 54/54, current 54/54.
- `git diff --check`: OK.
- `python C:\Users\admin\.codex\skills\.system\skill-creator\scripts\quick_validate.py .\chinese-official-writing`: `Skill is valid!`

Conclusion: the follow-up review fixes are minimal, verified against the 1.4.10 baseline, and did not regress the prior 1.4.10 repairs for high-frequency phrase detection, fenced format linting, or split drafting rules.
