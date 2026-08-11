# Hook canonical package v1.6.2 preregistration

## Fixed base and problem

- Fixed base: `69087b5c` on `codex/v1602-integration`.
- The Claude Code adapter currently lives under repository-root `agent-glue/`, while the SkillHub clean package is built from `chinese-official-writing/`. The adapter is therefore absent from that package, and its repository-relative core path is not portable to a flattened Skill install.

## Atomic change

1. Move only the five runtime or user-facing compatibility assets into the canonical Skill:
   - `hooks/AGENT_GLUE.md`
   - `hooks/host-capabilities.json`
   - `hooks/claude-code/.claude-plugin/plugin.json`
   - `hooks/claude-code/hooks/hooks.json`
   - `hooks/claude-code/scripts/gate_stop_hook.py`
2. Resolve the shared bridge from the containing Skill root and let the existing Codex bridge recognize the co-located Skill root. Do not change `review_gate.py`, state transitions, verdict rules, or the four-stop bound.
3. Keep the five assets in canonical and `skills/` only. Continue excluding all gate assets from `.agents`, `.qwen`, `hermes`, and `openclaw` mirrors.
4. Update the clean-package allowlist contract from 33 to 38 files. Ordinary Skill installation still does not enable hooks; activation remains an explicit host action.

## Evidence boundary

- Existing Claude smoke proves only session-only plugin registration and `UserPromptSubmit`; `PostToolUse`, `Stop`, persisted core state, and D0/D1 remain unverified.
- After relocation, one registration smoke may be run against the new package path. Authentication failure must be preserved and cannot be represented as a Stop lifecycle pass.
- OpenClaw remains metadata-only and WorkBuddy remains unknown. No executable adapter is added for either host.

## Gates and stop conditions

- Focused adapter/core/package tests, full unittest, stub smoke, fixed-base deterministic ablation, quick/plugin validation, py_compile, two-pass mirror sync, package allowlist and `git diff --check` must pass.
- SkillHub package must contain the five assets; ClawHub and generic mirrors must contain none of them.
- Stop if relocation changes Codex gate behavior, allows an unrelated Skill read to arm the gate, mutates host configuration, or requires a host contract that is not documented and locally testable.
