# Claude Code third-party gateway Hook smoke v1.6.2 result

## Verdict

`LIFECYCLE PASS / NO CLAUDE LOGIN / D0 VERIFIED / D1 UNVERIFIED`.

Claude Code 2.1.195 completed one isolated request through the local Anthropic-compatible gateway with `ollama-cloud/deepseek-v4-flash:0731` and `--effort max`. The run exercised `UserPromptSubmit -> Read -> PostToolUse:Read -> Stop`, persisted the adapter turn and core transaction below the temporary plugin-data root, performed one bounded Stop block/emit cycle, and then completed with exit code 0. No retry occurred.

The prompt explicitly required the displayed AI/internal-review line, so the core correctly recorded `findings: []` and selected D0. This run proves the D0 lifecycle and transport binding; it does not prove a D1 repair or the `PostToolUse:Bash` path.

## Isolation and model binding

- Product/preregistration commit: `cf5f779b3a74f849f6644b2eee3879aad5cd1fe5`.
- Plugin: `chinese-official-writing/hooks/claude-code` loaded with session-only `--plugin-dir`.
- Gateway: process-local `ANTHROPIC_BASE_URL=http://127.0.0.1:10100`; a non-secret probe token was used only in that child process.
- Model: all assistant records and `modelUsage` bind to `ollama-cloud/deepseek-v4-flash:0731`.
- Claude flags: empty setting sources, no session persistence, `Read` only, explicit Skill directory, hook events, stream JSON, and `--effort max`.
- `CLAUDE_CONFIG_DIR` and `CLAUDE_CODE_TMPDIR` were isolated under ignored run output. No plugin install, settings mutation, permission bypass, user credential read, or first-party login occurred.
- The same isolated config reports `loggedIn: false`, `authMethod: none`; this diagnostic exits 1 as expected for a non-login session.

## Observed event chain

1. `UserPromptSubmit` hook started and returned `{"continue":true}`.
2. The bound model invoked `Read` on the candidate canonical `SKILL.md`.
3. `PostToolUse:Read` started and returned `{"continue":true}`.
4. The first `Stop` hook returned a successful `decision:block` response containing the selected D0.
5. Claude Code supplied the Stop feedback to the same session; the second `Stop` returned `{"continue":true}`.
6. The terminal result was `success`, `num_turns: 3`, with the same D0 hash recorded by the gate.

Claude Code also emitted a `stop-hook-error` notification after the intentional block even though that hook response records `exit_code: 0`, `outcome: success`, the bounded continuation completed, and the process exited 0. This UI-level notification is retained as a compatibility warning rather than hidden.

## Core state

- Session: `df92aec9-3ef0-4c46-97d8-e4afeb1a9b86`.
- Adapter turn: `claude-1-43af263484e49129`, counter 1.
- Gate state: `TERMINAL_D0`; reason `no_review_candidate`; detect 1, repair 0, verify 0.
- Request SHA-256: `7BF726D29059CB1F2C9A4DAEFF2E8C02A2E543DF970D22DE72C83B9F1E42F6E1`.
- Source SHA-256: `E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855`.
- D0/final SHA-256: `0C1BB0AB11EE54F391B21A933D69DBB2433102F44C4A449582FB8E192673C04B`.
- Adapter turn file SHA-256: `8BBBD383D1713F311B796E20EE57E491B3AE90FDE8EF0CA9699DC68FD2F73369`.
- State SHA-256: `EAECDCFE9078168AE90EA2E92F5626D4F2AC82B3EA48441FA0A582F174D75298`.
- Report SHA-256: `B255A0EAD3198275C72F8142246E0FCCFDD2922C2DC8B815BFF574C11345C438`.
- Detection SHA-256: `087781A35AB0D350AC9821657BA24E80D6C4BC90316B05E76D5F66643E0D3B4A`.

## Raw local evidence

Raw output remains under ignored `output/hook-third-party-gateway-v1602-run-20260811/`; it is not copied into the product package.

- `stream.jsonl`: 61,196 bytes; SHA-256 `7AEFF73AAE904023157363CF691E13E99FB71E955B08D023E1D9374B480046EF`.
- `stderr.txt`: 0 bytes; SHA-256 `E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855`.
- `prompt.txt`: 313 bytes; SHA-256 `3C77EACEC981879216570459143A0A9F3B943EE6835C99AEBD66601F4F8CE029`.
- Start: `2026-08-11T08:10:12.8880381Z`; finish: `2026-08-11T08:10:21.2086092Z`.

## Remaining boundary

This smoke does not claim that ordinary Skill installation enables hooks. Activation remains an explicit, session-only host action. It also does not claim OpenClaw or WorkBuddy compatibility, and it does not upgrade the untested Claude `Bash` event or D1 repair path.
