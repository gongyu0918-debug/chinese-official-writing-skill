# Hook host command R2 result

## Fix

- Parent: `827d296b9cb854cd431ef214721c908133f27c18`.
- Codex default `hooks/hooks.json` now resolves only `${PLUGIN_ROOT}`.
- WorkBuddy/CodeBuddy `.codebuddy-plugin/plugin.json` now points to `hooks/workbuddy/hooks.json`, which resolves only `${CODEBUDDY_PLUGIN_ROOT}`.
- Both host configs still execute the same package-local `hooks/host_gate_adapter.py`; the adapter, shared bridge, review core, protocol, findings, state transitions, output selection, and four-stop bound are unchanged.
- The clean SkillHub package now contains 46 files. The new host config remains inside the existing MIT package boundary.

## Semantic command smoke

The focused test reads the real host config selected by each manifest, expands only that host's native root placeholder, tokenizes the resulting command, and starts the real configured `python3` subprocess three times:

1. `UserPromptSubmit` records the request.
2. `PostToolUse:Read` records the package-local top-level Skill read.
3. `Stop` drives the unchanged shared gate.

Codex returned its documented `decision: block` continuation envelope. WorkBuddy/CodeBuddy returned its documented `continue: false` envelope. Both subprocess sequences exited 0 and used the expected package-local adapter path. The test also rejects the other host's root variable and the generic Claude compatibility alias on each surface.

## Validation

| Check | Result |
| --- | --- |
| Focused tests | PASS, 114/114 |
| Full unittest | PASS, 514/514 |
| OpenAI plugin validator | PASS on canonical and clean package |
| WorkBuddy-bundled CodeBuddy 2.115.0 `plugin validate` | PASS on canonical and clean package; `valid: true` |
| Isolated Codex marketplace install | PASS; installed and enabled in a fresh `CODEX_HOME` |
| Clean package / installed cache | 46/46 files; both host Hook configs, shared adapter, and review core present |
| Promptfoo deterministic stub | PASS, 20/20; 0 failures, 0 errors; judge consistency 1.0 |
| Fixed-base deterministic ablation | PASS: `180fbd9c` 111/111; current 111/111 |
| Skill Creator quick validate | PASS |
| Compile | PASS |
| Two-pass mirror sync | PASS; identical diff hash `80493748375c9444aea6d9aab1fe8c0e11477faa` |
| OpenClaw frozen fingerprint | PASS |
| `git diff --check` | PASS |

## Boundary

- No model was called and no live host configuration was modified.
- Registration and subprocess Hook simulation do not claim a real interactive host lifecycle run.
- The optional companions still fail open on incomplete event payloads; the semantic Skill remains usable if a companion cannot execute.
