# 1.4.11 Follow-up Review Evidence

Date: 2026-06-29

Report: `C:\Users\admin\Desktop\chinese-official-writing-Review-1.4.11.md`

Baseline at start: GitHub/main and local `HEAD` both at `89948800d9616cb207f7d263948db7f51bc2441c` (`chinese-official-writing@1.4.11`). This follow-up intentionally does not bump or publish `1.4.12`.

## Review Decisions

Accepted and fixed:

- `B1`: `综上所述。` / `综上所述：` / `综上所述；` were real lint misses in clean `1.4.11`. The prior 1.4.10 follow-up narrowed the rule to comma punctuation to avoid false positives, but the regression matrix only covered the comma form and `本文综上所述部分如下。`.
- `O1`: `（成文日期待确认）` was already caught by lint, but not explicit enough in the prompt. Real writer testing also exposed an adjacent date-boundary failure: when the user explicitly says the成文日期 is missing, the writer could still place today's date in the落款. This was fixed as the same minimal prompt boundary.

Rejected or deferred:

- `X-1`: rejected. OpenClaw frontmatter uses `name: chinese_official_writing` by documented compatibility choice; no loading break was reproduced.
- `B2`: deferred. `经调查/检测/审计/评测/论证/了解` was not blanket-added as a safe basis for `未发现重大隐患`; broad expansion would weaken unsupported safety-conclusion warnings. Current behavior keeps `经现场检查，未发现重大隐患。` clean and still warns on `调查了解后，未发现重大隐患。`.
- `A-2/R-2/D-1` and older observations: deferred because no clear current failure was reproduced.

## Why Earlier Rounds Missed This

The earlier 1.4.10/1.4.11 work did catch and fix the scoped findings it tested, but the coverage boundary was too narrow:

- The deterministic lint tests covered `综上所述，` and the false-positive control `本文综上所述部分如下。`, not the period, colon, or semicolon variants.
- `O1` was a generation-behavior issue, not a pure lint issue. The existing lint regex already caught the literal `（成文日期待确认）`, but real writer acceptance did not force the case where the user explicitly says成文日期 is missing and forbids today's date in the落款.
- `tools/run_real_prompt_ablation.py` is deterministic and does not call an LLM; it proves skill packaging, references, routing, lint, and evaluation hooks, but cannot by itself expose live writer behavior.
- Previous real-writing rounds had missing dates and contacts, but did not isolate the exact "成文日期明确缺失, do not use current date" failure mode. This round added that real environment check.

## Minimal Changes

- `prose_lint.py`: broadened only the `综上所述` terminal punctuation pattern from comma-only to `，,。：:；;`; it still does not match the section-reference control.
- `SKILL.md` and references: explicitly forbid `（成文日期待确认）` in final正文/落款, and distinguish two cases:
  - if the user wants a complete draft but does not say the成文日期 is missing, current date may still be used as a draft date;
  - if the user explicitly says成文日期 is missing, pending, or must be confirmed, do not use current date in the落款; list it outside正文.
- `tools/sync_adapters.py`: updated the generated OpenClaw compact body so future adapter syncs keep the same date-boundary rule.
- Tests: added regression coverage for the punctuation variants and for the explicit date-boundary prompt text across mirrors/OpenClaw.

## Direct Reproduction

Final direct lint result:

```text
[(1, 'side-commentary', 'medium', '综上所述，'),
 (2, 'side-commentary', 'medium', '综上所述。'),
 (3, 'side-commentary', 'medium', '综上所述：'),
 (4, 'side-commentary', 'medium', '综上所述；'),
 (6, 'unfinished-placeholder', 'medium', '（成文日期待确认）'),
 (8, 'unsupported-conclusion', 'medium', '未发现重大隐患')]
```

Controls:

- `本文综上所述部分如下。` stayed clean for the summary-transition lint.
- `经现场检查，未发现重大隐患。` stayed clean for unsupported-conclusion.
- `调查了解后，未发现重大隐患。` still warned, preserving the fact-boundary protection.

## Subagent Verification

Read-only reviewer `019f0f46-08ca-7770-a049-d88e20a773d3` independently confirmed:

- `B1` is valid against clean `8994880` and fixed in the worktree.
- `O1` is a prompt/generation gap, while lint already detects the literal placeholder.
- `B2` should not be blanket-expanded without stronger corpus evidence.
- `X-1` remains an intentional OpenClaw compatibility adapter choice.

Real writer/verifier chain:

- Initial writer A produced a请示 with today's date in the落款 although the prompt said成文日期 was missing. Independent verifier marked this `FAIL`, so the first prompt-only fix was not enough.
- After the narrower date-boundary prompt fix, writer `019f0f4e-b7f7-7223-a621-ea7247e1f46e` re-ran the same missing-date请示 scenario. The draft kept only `市政务服务中心` in the落款 and listed `成文日期` under正文外待确认事项.
- Independent verifier `019f0f4f-d79b-7aa2-baef-3413a05c389f` returned `overall=PASS`, with no warnings, and stated this supports a local commit without a `1.4.12` release.

## Ablation and Regression

Baseline worktree comparison:

- `baseline-1.4.11`: 54/54 deterministic real-prompt cases passed.
- `current`: 54/54 deterministic real-prompt cases passed.
- Output: `output/real-prompt-vs-1.4.11-review-followup-after-date-fix/summary.md`.

Commands already run:

- `python .\tools\sync_adapters.py`: OK.
- `python -m unittest tests.test_review_regressions tests.test_skill_boundary -v`: 59 tests OK.
- `python -m unittest discover -s tests -v`: 93 tests OK.
- `python C:\Users\admin\.codex\skills\.system\skill-creator\scripts\quick_validate.py .\chinese-official-writing`: `Skill is valid!`
- `npm run eval:official-writing:smoke`: final elevated rerun passed 20/20, skill win rate 1.0, judge consistency rate 1.0. A prior sandboxed attempt failed because promptfoo could not spawn the configured Python executable and remove old logs; it was an environment/permission failure, not a product failure.
- `git diff --check`: passed. The command printed only Windows line-ending warnings, not whitespace errors.

Conclusion: the report was partially correct. The accepted fixes are small, prompt/lint scoped, and covered by deterministic, smoke, and real subagent verification. No `1.4.12` bump or ClawHub/GitHub publish is needed in this round.
