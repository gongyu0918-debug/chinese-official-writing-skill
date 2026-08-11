# Weak-model second-round repair test, 2026-07-08

Purpose: continue the release-prep loop after six real weak-model prompts showed that first drafts remain usable but not publish-ready. This round tested whether natural-language second-round corrections can repair Markdown residue, unsupported fact expansion, hard tone, and date carry-over without adding a heavy default writing stage.

Base state: `f20c8b8` before this round. Writer model: `gpt-5.3-codex-spark`, low reasoning, isolated subagents, each loading `chinese-official-writing/SKILL.md`. Verifier model: `gpt-5.5`, low reasoning, isolated subagents.

## Initial 6-prompt availability test

The six real prompts covered:

- RTX 5090 computer purchase situation explanation for Banshentong/model testing.
- Weibo operations situation explanation.
- Claude Code affected-version security notice from a public article.
- Weather warning rewritten as commute-safety notice.
- World Cup anti-gambling and attendance reminder notice.
- OpenClaw installation-status report.

Independent verifier result: all six completed and preserved most genre/key points, but all were `WARN`; conclusion was `usable but not publish-ready`.

Three repeated risks:

- Markdown/template residue in formal drafts (`**`, `---`, line-break formatting, template notes).
- Unsupported management/execution details, especially in sparse-material notices or reports.
- Tone or factual口径 drift, such as situation explanation becoming approval/request language or `比上月增长` becoming `同比上月增长`.

## Natural-language second-round repair test

Three problematic drafts were revised with normal user-style feedback:

- Computer purchase: remove request/approval tone, Markdown, measurement/audit/permission-control expansions.
- Weather notice: soften tone, remove region list, duty/reporting/strict execution and unsafe "walk if possible" wording.
- OpenClaw report: delete invented background, scope, written record, standing inspection and risk conclusion.

Verifier result:

- Computer purchase: `PASS`.
- Weather notice: `WARN`; major over-expansion removed, but date and some harder wording remained.
- OpenClaw report: `WARN`; major unsupported facts removed, but "related information terminal" and Markdown line-break traces remained.

Conclusion: second-round repair clearly helps, but it is not enough by itself as a release mitigation.

## Minimal prompt/reference changes

Accepted narrowly:

- When the user asks to keep only provided facts in second-round revision, do not expand broad actions such as `已排查`, `已核查`, or `已检查` into unprovided scope, carrier, process, or result judgments.
- Formal drafts should not use Markdown line-break formatting via trailing double spaces.
- When the user asks in second-round revision to remove or not add a date, remove the previous draft date too; if formal completeness is affected, only note it outside the body.

Rejected for this round:

- More default first-draft prompt stacking. Six earlier candidates failed or added noise.
- A new blocking stage or mandatory pre-output confirmation.
- Claims that the current version is publish-ready.

## Focused retest after the minimal changes

Focused retest results:

- Explicit Markdown/line-break cleanup: `PASS`; output had no `**`, `---`, code fence, or trailing double-space line breaks and did not expand facts.
- OpenClaw fact-only second revision: verifier judged the "已排查" expansion rule worth keeping; output no longer expanded into a detailed scope/process chain, though one line still had Markdown-like trailing spaces.
- Weather notice date removal: initial focused retest still kept the previous date; after the narrow date carry-over rule, verifier judged the date retest `PASS`.

Remaining risks:

- The fixes improve explicit second-round repair, not weak-model first drafts.
- Weak models may still add small general reminders or wording such as "提醒身边同事" in sparse notices.
- Full release still requires another broad weak/strong real-writing A/B plus deterministic ablation against the previous baseline.
