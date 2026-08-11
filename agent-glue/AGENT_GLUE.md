# AGENT_GLUE

`chinese-official-writing/scripts/review_gate.py` is the only shared gate core. Host adapters may map documented lifecycle JSON into the existing bridge, but must not alter core state transitions, verdict rules, or the four-stop continuation bound.

## Activation

The ordinary Skill and its mirrors do not enable hooks. Hook activation is a separate, explicit host action and this repository never writes user, project, or global host configuration.

For the local Claude Code adapter, run it from this checked-out repository only:

```powershell
claude --plugin-dir .\agent-glue\claude-code
```

This loads a hook-enabled plugin for that invocation. It is not an installation command, does not modify Claude configuration, and requires the ordinary writing Skill to be available separately. Do not present it as automatic after a Skill installation.

## Claude Code adapter contract

- The adapter accepts only `UserPromptSubmit`, `PostToolUse` for `Bash|Read`, and `Stop`.
- It maps documented `prompt`, `tool_input`, `tool_response`, `stop_hook_active`, and `last_assistant_message` fields to the existing gate bridge. `Read.file_path` is normalized to bridge command text so the existing skill-read guard remains intact.
- Claude Code 2.1.195 has no `prompt_id`; the adapter allocates a bounded per-session turn identifier in `CLAUDE_PLUGIN_DATA`. All adapter and core state stays below that host-provided plugin data directory.
- The adapter reads `CLAUDE_PLUGIN_ROOT` and `CLAUDE_PLUGIN_DATA`, verifies its own plugin root, then sets only process-local bridge environment values. It does not bypass workspace trust or permissions.
- The existing core bridge limits continuation to four attempts. Claude Code also enforces its own documented Stop-block ceiling.

## Capability status

See `host-capabilities.json` for the authoritative support matrix. OpenClaw remains metadata-only pending a separately validated typed `before_agent_finalize` adapter. WorkBuddy remains `unknown`; do not infer a hook API or ship an executable adapter.

## No-model preflight

Run the following before an authorized live smoke test:

```powershell
python tools/preflight_claude_hooks.py
```

It reads `claude --version` and validates only local manifest/layout data. It does not send a model request or change host configuration. A live invocation that loads the plugin is intentionally deferred until separately authorized.
