# Community Borrowing Minimal Follow-up

Date: 2026-06-29

Baseline: `db5607b` (`docs: review Hermes community borrowing candidate`)

Current scope: local Codex workspace only. Hermes work repo `C:\Users\admin\chinese-official-writing-review\repo` was not modified.

## Decision

Accepted as minimal borrowing:

- Add a short risk-first review layer in `review-checklist.md`.
- Add a soft oral-source boundary in `official-style.md` and align the existing `anti-ai-patterns.md` examples.
- Add light genre "可参考顺序" hints for common genres in `genre-checklist.md`, explicitly not as visible labels and not overriding user templates, field-style material, web-copied drafts, or existing heading order.
- Adjust existing `prose_lint.py` casual hints for `这个钱花得值` and `老板关心` so they still warn but no longer suggest over-strong fixed replacements.

Rejected in this round:

- No `format_docx.py`.
- No paragraph-isomorphism lint.
- No new hard gate, no auto-cleaning script, no forced confirmation workflow.
- No version bump and no GitHub/ClawHub release.

## Implementation

- `chinese-official-writing/references/review-checklist.md`
  - Added `定稿前高风险先查`.
  - It says to continue with paragraph/section/full-text review after locating risk, and not to turn this into a blocking workflow.
- `chinese-official-writing/references/official-style.md`
  - Added `口语来源不等于事实授权`.
  - Specifically guards `老板关心`, `钱花得值`, `马上要搞` from becoming unsupported `领导高度关注`, `投入产出清晰`, `推进较为紧迫`, or `按程序推进`.
- `chinese-official-writing/references/anti-ai-patterns.md`
  - Replaced fixed strong examples with lower-strength fact-bound examples.
- `chinese-official-writing/scripts/prose_lint.py`
  - Keeps `casual` findings for the same oral phrases but changes the suggested wording to preserve evidence boundaries.
- `chinese-official-writing/references/genre-checklist.md`
  - Added light sequence hints for `通知`, `请示`, `报告`, `方案`, `申请`, and `函`.
  - Confirmed `## 函` remains intact and no `## 函数` is introduced.
- Ran `python .\tools\sync_adapters.py` to sync `.agents`, `.qwen`, `skills`, `hermes`, and `openclaw` mirrors.

## Deterministic Evidence

- `python .\tools\sync_adapters.py`
  - Passed after elevated rerun. The first sandboxed run failed on `.agents` permission denial.
- `python -m unittest tests.test_skill_boundary tests.test_real_prompt_ablation -v`
  - 39 tests OK.
- `python -m unittest tests.test_review_regressions tests.test_skill_boundary -v`
  - 59 tests OK.
- `python -m unittest discover -s tests -v`
  - 93 tests OK.
- `$env:PROMPTFOO_PYTHON='C:\Users\admin\AppData\Local\Programs\Python\Python313\python.exe'; npm run eval:official-writing:smoke`
  - 20/20 passed.
  - `skill_win_rate=1.0`.
  - `judge_consistency_rate=1.0`.
  - Earlier unqualified `npm run eval:official-writing:smoke` failed because promptfoo tried to use missing Hermes venv Python and could not remove old `.promptfoo` logs in sandbox.
- `python C:\Users\admin\.codex\skills\.system\skill-creator\scripts\quick_validate.py .\chinese-official-writing`
  - Skill is valid.
- `git diff --check`
  - Passed.
- `rg --files chinese-official-writing .agents skills .qwen hermes openclaw | rg "(^|/)format_docx\.py$|(^|/)document_generator\.py$|(^|/)generate_official_doc\.py$|(^|/)install_fonts\.py$"`
  - No matches.
- Direct lint reproduction:
  - Input: `老板关心这个钱花得值不值，要求马上要搞一个试点。`
  - `这个钱花得值` still reports `medium/casual`, message: `改为资金使用必要性和预期效果，并保留依据边界。`
  - `老板关心` still reports `medium/casual`, message: `改为相关负责人关注该事项，不无依据升级为领导高度关注。`

## Baseline Ablation

Command:

`python .\tools\run_real_prompt_ablation.py --baseline-root .\output\release-baselines\db5607b-before-community-borrowing --baseline-label baseline-db5607b --current-root . --out .\output\real-prompt-vs-db5607b-community-borrowing`

Result:

- `baseline-db5607b`: 55 cases, 54 passed, 1 failed.
- `current`: 55 cases, 55 passed, 0 failed.
- The only baseline failure is new P055, which checks the new minimal borrowing support.
- Current has no regression against the existing 54 cases.

Summary file:

- `output/real-prompt-vs-db5607b-community-borrowing/summary.md`

## Real Subagent Test

Writer subagent: `019f1289-e637-7821-9994-d0bc63280cf1`

Verifier subagent: `019f128b-9977-7351-ba33-508958022f91`

Scenarios:

- T1: oral-source formalization for `老板关心 / 钱花得值 / 马上要搞`.
- T2: field-style application rewrite.
- T3: review-only AI taste and format risk.
- T4:商请函 with missing amount, feedback deadline, contact, and attachment list.
- T5: user template first, fixed two-paragraph notice.

Verifier result:

- T1 PASS: no banned strong expressions; budget, approval process, and completion deadline remained unset.
- T2 PASS: field names, order, and blank fields preserved; no invented invoice, email, or date.
- T3 PASS: review-only behavior; no full rewrite and no 0-100 score.
- T4 PASS: missing items stayed in short out-of-body confirmation list.
- T5 PASS: user two-paragraph template preserved; no custom visible structure labels.
- `overall=PASS`.
- `publish_blocking=false`.

## Remaining Risk

- Real writer used `资金使用必要性和预期效果`, which verifier accepted as a low-strength expression corresponding to `钱花得值不值`. Continue watching for over-strong fiscal conclusions in future real tests.
- This is a prompt/reference-layer minimal borrowing commit, not a release. No 1.4.12 bump, tag, push, or ClawHub publish was performed.
