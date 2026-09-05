# Four Hook fixes R1

- Fixed baseline: `3532afd6619ac6256558e9552b92d03da5ae9c0f` (public main, product v1.6.27).
- Worktree: `codex/hook-four-fixes-r1`. User authorized attempting the four recorded fixes. No examples, installed Skill, Pro or platform changes.
- Requirements: `AH-002b`, `HK-005b`, with the existing `HK-008` raw-data boundary.

## Minimal evidence before integration

1. Date: reuse the original, hash-verified natural D0/request pairs from `ah002-news-date-completeness-r1` as positive controls. Separately replay the same real D0 against explicitly registered source-role request variants (ISO fact plus nonfactual Chinese format example). These variants are constructed lifecycle inputs, not original natural-generation pairs. Preserve the old synthetic counterexample separately.
2. Fresh writing: two isolated existing Claude CLI sessions, exact routes `alibaba-token-plan-2/deepseek-v4-flash-0731` and `minimax-cn/MiniMax-M3`, effort max, frozen main Skill/news leaf and the original `date-source-real-r1/case.json` request. No tools, plugins, MCP, automatic retry or model fallback. Retain full prompts, D0, streams and model-binding receipts. A naturally complete date is a control, not a reproduced missing-year benefit.
3. Delivery: baseline and minimal candidate receive the same real D0/request. Obtain a real exact-output response on the candidate. For the mismatch branch, inject a clearly labeled wrong response at the host event boundary, exhaust the existing finite budget and replay Stop. Require a persistent failure response, never `delivery_verified=true`; do not claim that a Stop hook retracts already displayed text.
4. Retention: replay the original request after a verified terminal Stop; schedule a late PostToolUse write across terminal cleanup. Use a real D0 without altering its content. Both raw request and selected body must stay absent, with no effect on the next distinct turn. Scheduled concurrency and replay are fault injection, not incidence measurements.

Only after the targeted prototype result and real-writing controls pass, integrate the needed core/adapter changes and run focused tests, validation and assembly checks. Native host behavior must be evidenced separately from core subprocess replay; changed adapters do not inherit old online success as current proof.

## Research used

- [Codex official Hook protocol](https://learn.chatgpt.com/docs/hooks.md): Stop `decision:block` requests continuation; `continue:false` takes precedence over Stop continuation.
- [Claude Code official Hook protocol](https://code.claude.com/docs/en/hooks): `continue:false` stops processing; a Stop block requests another model turn. Neither response promises to retract already emitted assistant text.
- [Codex issue 37937](https://github.com/openai/codex/issues/37937): a reported repeatedly blocking Stop loop supports keeping a finite budget; it is community evidence, not a verified host contract.

Acceptance reports separate improved fault handling, unchanged real-draft controls, native-host behavior and unresolved coverage. This small sample cannot establish a population error rate or 98%/100% drafting reliability.
