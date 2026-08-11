# AGENT_GLUE

`chinese-official-writing/scripts/review_gate.py` is the only shared gate core. Host adapters may map documented lifecycle JSON into the existing bridge, but must not alter core state transitions, verdict rules, or the four-stop continuation bound.

## Three layers

1. The semantic Skill drafts or revises from the user's request and materials. It may run `scripts/prose_lint.py` as a separate, read-only aid before settling a complete D0, but lint is optional and never edits the draft automatically.
2. After D0 exists, an explicitly enabled host lifecycle Hook may snapshot the raw request and D0, then call `scripts/review_gate.py`. The ordinary Skill does not call, install, or enable that Hook.
3. `review_gate.py` applies the bounded transaction documented in `references/delivery-review-gate.md` and selects D0 or a mechanically and semantically verified D1. That reference is the Hook protocol specification, not an ordinary Skill reference route, and must not be added to normal `SKILL.md` loading.

The Hook receives the raw request and D0. It does not run `prose_lint.py` and must not treat prose-lint findings or reports as Hook input. If semantic review, optional lint guidance, Hook state, or gate verification disagree, the immutable D0 is the fallback; no layer may use the disagreement to trigger another drafting loop.

## Activation

The ordinary Skill and its mirrors do not enable hooks. Hook activation is a separate, explicit host action and this repository never writes user, project, or global host configuration.

The flattened SkillHub directory is also a self-contained Codex and WorkBuddy/CodeBuddy companion plugin. Its `.codex-plugin/plugin.json` and `.codebuddy-plugin/plugin.json` share `hooks/hooks.json`, `hooks/host_gate_adapter.py`, the top-level Skill, and the existing gate core. The nested `skills/chinese-official-writing/SKILL.md` is discovery glue only: it routes to the same top-level `SKILL.md` and contains no product rules of its own.

For Codex, register the entire installed Skill directory as a plugin through a user-authorized local marketplace, enable it, then review and trust its Hook. Registering only `hooks/` is invalid because plugin caches must retain the top-level Skill, bridge, protocol, and review core together. Installation, enablement, and Hook trust are separate actions; this repository performs none of them automatically.

For WorkBuddy/CodeBuddy, load the entire installed Skill directory explicitly for the current invocation:

```powershell
codebuddy --plugin-dir .
```

The adapter uses the host-provided persistent plugin-data directory. Current compatibility is bounded to the documented CodeBuddy plugin/Hook contract and the locally inspected WorkBuddy 5.3.8 bundle with CodeBuddy Code 2.115.0. Missing `last_assistant_message`, plugin data, or another required event field fails open. Do not infer equivalent support for an older WorkBuddy runtime.

For the packaged Claude Code adapter, run it from the installed Skill directory:

```powershell
claude --plugin-dir .\hooks\claude-code
```

This loads a hook-enabled plugin for that invocation. It is not an installation command, does not modify Claude configuration, and requires the ordinary writing Skill to be available separately. Do not present it as automatic after a Skill installation.

## Claude Code adapter contract

- The adapter accepts only `UserPromptSubmit`, `PostToolUse` for `Bash|Read`, and `Stop`.
- It maps documented `prompt`, `tool_input`, `tool_response`, `stop_hook_active`, and `last_assistant_message` fields to the existing gate bridge. `Read.file_path` is normalized to bridge command text so the existing skill-read guard remains intact.
- Claude Code 2.1.195 has no `prompt_id`; the adapter allocates a bounded per-session turn identifier in `CLAUDE_PLUGIN_DATA`. All adapter and core state stays below that host-provided plugin data directory.
- The adapter reads `CLAUDE_PLUGIN_ROOT` and `CLAUDE_PLUGIN_DATA`, verifies its own plugin root, then sets only process-local bridge environment values. It does not bypass workspace trust or permissions.
- The existing core bridge limits continuation to four attempts. Claude Code also enforces its own documented Stop-block ceiling.

## Codex and WorkBuddy/CodeBuddy adapter contract

- Both hosts use the package-root manifests and the same `hooks/hooks.json`; the adapter selects a mapping only from documented host plugin environment variables.
- Codex `turn_id`, `prompt`, `tool_input`, `tool_response`, `stop_hook_active`, and `last_assistant_message` map directly to the shared bridge. WorkBuddy/CodeBuddy receives a bounded per-session turn identifier in its persistent plugin-data directory because its documented Hook payload has no `turn_id`.
- `Bash.command` and `Read.file_path` normalize to the bridge command text so the existing skill-read guard remains unchanged. Unsupported tools, incomplete events, missing persistent data, and root mismatches fail open.
- The adapter converts only the shared core's continuation response: Codex retains `decision: block`; WorkBuddy/CodeBuddy receives its documented `continue: false` plus `reason`. It does not change findings, repairs, verdicts, state transitions, or the four-stop bound.
- A plugin cache must contain the complete MIT package. No adapter may traverse outside the registered package root or write host settings.

## Capability status

See `host-capabilities.json` in this directory for the authoritative support matrix. The SkillHub package contains Codex and WorkBuddy/CodeBuddy companion manifests, shared Hook glue, and the previously packaged Claude Code adapter. Codex package validation and isolated registration do not prove a real lifecycle run. WorkBuddy/CodeBuddy manifest validation and local binary inspection do not prove a real lifecycle run. An isolated Claude Code 2.1.195 run through an Anthropic-compatible third-party gateway verified session-only plugin registration, `UserPromptSubmit`, `PostToolUse:Read`, `Stop`, persisted core state, and bounded D0 emission without a Claude account login. `PostToolUse:Bash` and a D1 repair remain unverified. OpenClaw remains frozen at its released package with no adapter change.

## No-model preflight

Run the following before an authorized live smoke test:

```powershell
python tools/preflight_claude_hooks.py
```

It reads `claude --version` and validates only local manifest/layout data. Codex and WorkBuddy/CodeBuddy companion manifests must additionally pass their official validators or local registration commands against an isolated temporary home. These checks do not send a model request or change the real host configuration. A live invocation that exercises lifecycle events is intentionally deferred until separately authorized.
