# License scope cleanup preregistration

## Fixed baseline and authorization

- Baseline: local `main` commit `2e0e6b30fb76ed7b53c32d0d879e92ccbfac34b9`.
- Worktree: `output/research-worktrees/license-scope-cleanup`.
- Branch: `codex/license-scope-cleanup`.
- This task may clarify repository and package license scope only. It must not change writing rules, references, Hook behavior, package version numbers, tags, remotes, releases, or marketplace state.
- The tracked `openclaw/` tree is frozen and must remain byte-identical to release commit `0f6ec603993d5595e784fa7079837e299d1b0da3`.

## Reproduced baseline conflict

1. Root `LICENSE`, canonical/`skills` package licenses, SkillHub builder output, and Codex/Claude/WorkBuddy manifests already use MIT.
2. `tools/sync_adapters.py` still overwrites `.agents`, `.qwen`, and Hermes package licenses with root `LICENSE-SKILL` (MIT-0).
3. README and `tests/test_skill_boundary.py` describe and enforce that obsolete pure-Skill split.
4. `redskill/skills/chinese-official-writing/SKILL.md` still declares `license: MIT-0`, although Red SkillHub is not the frozen ClawHub/OpenClaw release surface.
5. The generic name `LICENSE-SKILL` obscures that MIT-0 is now intended only for the ClawHub/OpenClaw exception.

## Candidate atom

1. Keep root `LICENSE` as the repository-wide MIT text.
2. Rename the MIT-0 text to an exception-specific root filename and document that it applies only to `openclaw/` and the ClawHub package derived from it.
3. Make canonical, `skills`, `.agents`, `.qwen`, Hermes, Red SkillHub source, Hook assets, plugin manifests, tools, tests, evals, evidence, and docs unambiguously MIT without adding license metadata to runtime Skill frontmatter.
4. Update the adapter synchronizer and boundary tests so every non-OpenClaw package receives root MIT bytes.
5. Preserve historical evidence as history; statements describing prior releases are not current license declarations.

## Gates

- `git diff --exit-code 0f6ec603993d5595e784fa7079837e299d1b0da3 -- openclaw`
- focused license-boundary and SkillHub package-builder tests
- synchronizer run twice with the second run producing no diff
- clean SkillHub package build with `LICENSE.md` byte-identical to root MIT
- full unittest suite, `quick_validate`, plugin manifest validation where available, and `git diff --check`
- no version-number diff and no product-writing-rule/reference diff

## Stop conditions

- Stop if the frozen `openclaw/` tree changes.
- Stop if the cleanup requires a version bump, release, upload, push, or writing-rule change.
- Do not claim legal advice or retroactively relicense third-party material; referenced third-party works retain their own licenses.
