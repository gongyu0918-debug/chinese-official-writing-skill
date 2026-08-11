# Hook host companions v1.6.2 preregistration

## Fixed base and scope

- Fixed base: `180fbd9c75c6300678b712c9d5c3765ee576f634` on `codex/v1602-final-integration`.
- This atom changes packaging, host manifests, host event mapping, capability metadata, tests, and clean-package counts only.
- Do not change `SKILL.md`, `references/delivery-review-gate.md`, `scripts/review_gate.py`, shared gate findings, state transitions, output selection, or the four-stop bound.
- Do not rebase onto later request-fact-safety work. OpenClaw remains byte-frozen.

## Official-source findings

- OpenAI Codex documents plugin-bundled hooks, default `hooks/hooks.json` discovery, command-hook JSON on stdin, `PLUGIN_ROOT` / `PLUGIN_DATA`, explicit hook trust, and `turn_id` plus `last_assistant_message` on Stop: <https://developers.openai.com/plugins/build/plugins> and <https://learn.chatgpt.com/docs/hooks>.
- Tencent CodeBuddy documents plugin hooks, `.codebuddy-plugin/` plus `.workbuddy-plugin/` compatibility, `CODEBUDDY_PLUGIN_ROOT` / `CODEBUDDY_PLUGIN_DATA`, `UserPromptSubmit`, `PostToolUse`, `Stop`, and `continue: false` Stop continuation: <https://www.codebuddy.ai/docs/cli/plugins-reference> and <https://www.codebuddy.ai/docs/cli/hooks>.
- The locally installed Tencent-signed WorkBuddy 5.3.8 bundles `@tencent-ai/codebuddy-code` 2.115.0. Its shipped Stop event builder includes `last_assistant_message` when available. This local binary check is version-bounded evidence, not a claim about every WorkBuddy release.
- Claude Code already has a packaged, tested adapter. Keep that adapter and its verified/unverified boundary unchanged.

## Atomic design

1. Make the flattened SkillHub package root a self-contained Codex and WorkBuddy/CodeBuddy companion plugin by adding both host manifests.
2. Add one shared host adapter and one default `hooks/hooks.json`. Detect the invoking host from documented plugin environment variables, map only documented event fields, and translate the existing core block result to each host's documented output shape.
3. Add a minimal nested plugin Skill shim that routes to the canonical top-level `SKILL.md`; keep its description byte-aligned with canonical metadata. This avoids duplicating product instructions while ensuring cached plugin installs read the same packaged Skill root that arms the existing bridge.
4. Keep all adapter/core state below documented plugin data directories. Missing root/data/event fields, unsupported versions, or missing Stop draft text must fail open without host configuration writes.
5. Keep the ordinary Skill install non-activating. Codex still requires explicit plugin install/enable and hook trust; WorkBuddy/CodeBuddy requires explicit plugin loading. Package presence is not activation.
6. Continue mirroring the full package only to `skills/chinese-official-writing`; exclude all gate and companion assets from `.agents`, `.qwen`, `hermes`, and frozen `openclaw`.

## Gates and stop conditions

- Focused adapter/package/layer/boundary tests and full unittest must pass.
- OpenAI plugin validator must pass against the canonical package root.
- A clean SkillHub build must register from an isolated temporary `CODEX_HOME` through a local marketplace without a model call; the installed cache must contain the shared bridge and review core.
- The installed WorkBuddy/CodeBuddy CLI must pass `plugin validate` against the canonical package root under an isolated home, without a model call.
- Promptfoo stub, deterministic fixed-base ablation, quick validation, compile, two-pass mirror sync, package assertions, OpenClaw fingerprint, and `git diff --check` must pass.
- Stop rather than claim compatibility if either host copies only an incomplete subtree, rejects the manifests/hooks, mutates real user configuration, or requires reading data outside the packaged MIT boundary.
