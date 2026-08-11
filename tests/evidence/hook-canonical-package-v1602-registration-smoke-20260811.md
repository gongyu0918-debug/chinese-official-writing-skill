# Hook canonical package registration smoke v1.6.2

## Bound candidate and command boundary

- Product commit: `7b2e0ee4`.
- Plugin path: `chinese-official-writing/hooks/claude-code` inside the canonical Skill.
- Invocation used session-only `--plugin-dir`, empty settings sources, `--no-session-persistence`, the `Read` tool only, `--include-hook-events`, `--print --verbose --output-format stream-json`, and a public fixed probe.
- No plugin installation, user/project/global settings write, permission bypass, credential read, or retry occurred.

## Observed events

The single invocation exited `1` after 460 ms with zero API duration and zero tokens. The raw local stream contains, in order:

1. `hook_started` for `UserPromptSubmit`;
2. `hook_response` with `exit_code: 0` and `{"continue":true}`;
3. `init` listing `chinese-official-writing-gate@inline` from the canonical package path;
4. `authentication_failed` / `Not logged in · Please run /login`;
5. terminal result with no model turn.

Raw local artifacts are kept only under ignored `output/hook-canonical-package-smoke-20260811/` because the init event includes a user-local Claude memory path.

- Raw stream bytes: 3615
- Raw stream SHA-256: `C40B9C9F49E9B607B875F530969C61B83D9D7E5B47B435E6036B94E613921CAC`
- Empty stderr SHA-256: `E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855`

## Verdict

`REGISTRATION PASS / AUTHENTICATION INVALID FOR MODEL LIFECYCLE`.

The relocated package path and real `UserPromptSubmit` command delivery are verified. There was no model `Read`, `PostToolUse`, `Stop`, persisted core transaction, D0, D1, or final gate state. Those capabilities remain unverified and must not be inferred from this smoke.
