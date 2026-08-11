# Hook host companions v1.6.2 result

## Fixed boundary

- Base: `180fbd9c75c6300678b712c9d5c3765ee576f634`.
- Changed only package manifests, a host mapping adapter, plugin discovery glue, capability/activation documentation, mirror/build contracts, tests, and MIT package wording.
- Unchanged: canonical `SKILL.md` body, `references/delivery-review-gate.md`, shared `hooks/gate_stop_hook.py`, `scripts/review_gate.py`, findings, state transitions, output selection, four-stop bound, and OpenClaw.
- No model request, publication, real user host configuration write, plugin trust bypass, or live lifecycle claim was made.

## Official contracts used

- Codex plugin and Hook contracts: <https://developers.openai.com/plugins/build/plugins> and <https://learn.chatgpt.com/docs/hooks>.
- WorkBuddy/CodeBuddy plugin and Hook contracts: <https://www.codebuddy.ai/docs/cli/plugins-reference> and <https://www.codebuddy.ai/docs/cli/hooks>.
- Local host evidence: Tencent-signed WorkBuddy 5.3.8 bundles `@tencent-ai/codebuddy-code` 2.115.0; the shipped Stop builder conditionally includes `last_assistant_message`.

## Implementation

- The flattened canonical/SkillHub directory is now the plugin root for both `.codex-plugin/plugin.json` and `.codebuddy-plugin/plugin.json`.
- `hooks/hooks.json` and `hooks/host_gate_adapter.py` are shared by Codex and WorkBuddy/CodeBuddy. The adapter maps documented fields, allocates only WorkBuddy's missing turn id, translates only the host continuation envelope, and delegates all gate decisions to the unchanged shared bridge/core.
- `skills/chinese-official-writing/SKILL.md` contains only discovery metadata and a pointer to `../../SKILL.md`; its description is test-locked to the canonical description.
- Claude Code keeps its existing packaged adapter. Pure `.agents`, `.qwen`, and `hermes` mirrors exclude every Hook/companion file. OpenClaw remains frozen.
- The clean SkillHub package changed from 40 to 45 files. `LICENSE.md` remains byte-identical to the root MIT license; both new manifests declare `MIT`.

## Validation receipts

| Check | Result |
| --- | --- |
| OpenAI `validate_plugin.py` on canonical and clean package | PASS on both |
| WorkBuddy-bundled CodeBuddy 2.115.0 `plugin validate` | First run correctly found `skills: Field "skills" must be an array`; the CLI also returned exit 0 and emitted a trailing HTTP 500, so that run was not counted as pass. After changing only the manifest field to an array, canonical and clean-package reruns both printed `Validation passed`, `valid: true`, exit 0. |
| Combined validator command | The first combined command was rejected before execution because it contained dynamic recursive cleanup. It was replaced with fixed workspace `output/` isolation; no permission bypass or real-home fallback was used. |
| Isolated Codex registration | PASS. With a fresh temporary `CODEX_HOME`, local marketplace add and `codex plugin add chinese-official-writing@cow-host-smoke` returned installed/enabled version 1.6.0. The installed cache retained all 45 clean-package files. |
| Cached required assets | PASS: both manifests, top-level Skill, plugin Skill shim, shared host adapter, shared bridge, `review_gate.py`, and `LICENSE.md` were present. |
| Focused unit tests | PASS, 113/113 |
| Full unit tests | PASS, 513/513 |
| Promptfoo deterministic stub smoke | PASS, 20/20; 0 failed, 0 errors; judge consistency 1.0 |
| Fixed-base deterministic ablation | PASS: `180fbd9c` 111/111; current 111/111 |
| Skill Creator quick validate | PASS, `Skill is valid!` |
| Compile | PASS for the host adapter, shared/Claude bridges, review core, sync tool, and clean-package builder |
| Mirror sync | PASS; second pass preserved diff hash `072a174eb4f2b364833bad042c94fef1d3bf9bf4` |
| OpenClaw frozen fingerprint | PASS |
| `git diff --check` | PASS |

## Evidence boundary and remaining risk

- Codex manifest validation and isolated registration prove package ingestion and cache completeness, not real `UserPromptSubmit`/`PostToolUse`/`Stop` delivery.
- WorkBuddy/CodeBuddy validation plus local binary inspection prove the current installed contract shape, not a live Hook transaction. Older runtimes may omit `last_assistant_message`; the adapter then fails open.
- Hook activation remains explicit. Codex still requires plugin enablement and Hook trust; WorkBuddy/CodeBuddy requires explicit plugin loading. Ordinary Skill installation alone does not activate a Hook.
- The shared command uses documented Claude-compatible plugin-root aliases and `python3`. A host without a usable Python 3 command cannot run the optional companion even though the semantic Skill remains usable.
- No real-host D1 repair was attempted, and no claim is made beyond the existing Claude Code lifecycle evidence.
