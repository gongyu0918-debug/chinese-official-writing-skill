# Hook host command R2 preregistration

## Reproduction

- Fixed candidate: `827d296b9cb854cd431ef214721c908133f27c18`.
- The package-root default `hooks/hooks.json` uses `${CLAUDE_PLUGIN_ROOT}` for both Codex and WorkBuddy/CodeBuddy, while the adapter identifies the invoking host from `PLUGIN_ROOT` or `CODEBUDDY_PLUGIN_ROOT`.
- Structural validators accepted this compatibility alias, but no test expanded the configured command and launched the packaged script with each host's native environment contract.

## Atomic fix

1. Keep `hooks/hooks.json` as the Codex default and use only `${PLUGIN_ROOT}` there.
2. Add `hooks/workbuddy/hooks.json`, point `.codebuddy-plugin/plugin.json` to it, and use only `${CODEBUDDY_PLUGIN_ROOT}` there.
3. Do not change the shared adapter mapping, bridge, review core, protocol, findings, output selection, or continuation bound.
4. Increase the clean package count from 45 to 46 and keep the full package under the same MIT boundary.

## Required evidence

- A focused smoke must read each real manifest/config, expand only that host's native root variable, and execute the resulting real `python3` subprocess for `UserPromptSubmit`, `PostToolUse:Read`, and `Stop`.
- Both commands must use the expanded package root and must not contain the other host's root variable or the generic Claude compatibility alias.
- OpenAI validation, WorkBuddy/CodeBuddy validation, clean-package build, isolated Codex install/cache verification, focused/full unit tests, deterministic stub, fixed-base ablation, quick validate, mirror sync, OpenClaw fingerprint, compile, and diff checks must pass.
