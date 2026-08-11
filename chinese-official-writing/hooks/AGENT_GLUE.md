# AGENT_GLUE

`chinese-official-writing/scripts/review_gate.py` is the only shared gate core. Host adapters may map documented lifecycle JSON into the existing bridge, but must not alter core state transitions, verdict rules, or the four-stop continuation bound.

## Three layers

1. The semantic Skill drafts or revises from the user's request and materials. It may run `scripts/prose_lint.py` as a separate, read-only aid before settling a complete D0, but lint is optional and never edits the draft automatically.
2. After D0 exists, an explicitly enabled host lifecycle Hook may snapshot the raw request and D0, then call `scripts/review_gate.py`. The ordinary Skill does not call, install, or enable that Hook.
3. `review_gate.py` applies the bounded transaction documented in `references/delivery-review-gate.md` and selects D0 or a mechanically and semantically verified D1. That reference is the Hook protocol specification, not an ordinary Skill reference route, and must not be added to normal `SKILL.md` loading.

The Hook receives the raw request and D0. It does not run `prose_lint.py` and must not treat prose-lint findings or reports as Hook input. If semantic review, optional lint guidance, Hook state, or gate verification disagree, the immutable D0 is the fallback; no layer may use the disagreement to trigger another drafting loop.

## Activation

The ordinary Skill and its mirrors do not enable hooks. Hook activation is a separate, explicit host action and this repository never writes user, project, or global host configuration.

The repository-root Codex adapter is a verified companion surface at `hooks/hooks.json`; it is not inside an ordinary SkillHub package. A SkillHub installation therefore needs separately user-authorized host glue before Codex lifecycle events can reach the packaged bridge. Package presence alone never proves activation.

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

## Capability status

See `host-capabilities.json` in this directory for the authoritative support matrix. The Codex adapter is verified only as a repository companion; the ordinary SkillHub package has no Codex adapter. The Claude Code adapter is present in the package. An isolated Claude Code 2.1.195 run through an Anthropic-compatible third-party gateway verified session-only plugin registration, `UserPromptSubmit`, `PostToolUse:Read`, `Stop`, persisted core state, and bounded D0 emission without a Claude account login. `PostToolUse:Bash` and a D1 repair remain unverified. OpenClaw remains frozen at its released package with no adapter change. WorkBuddy remains `unknown`; do not infer a hook API or ship an executable adapter.

## No-model preflight

Run the following before an authorized live smoke test:

```powershell
python tools/preflight_claude_hooks.py
```

It reads `claude --version` and validates only local manifest/layout data. It does not send a model request or change host configuration. A live invocation that loads the plugin is intentionally deferred until separately authorized.
