# SkillHub MIT / pure-Skill MIT-0 license split v1.6.2 preregistration

## Fixed baseline and user decision

- Baseline: `1ae9d73f2f05eb33a9801f1146118403c195194d`.
- User decision: beginning with the next version, the SkillHub/Codex full package that includes Hook and shared gate code uses MIT rather than MIT-0. The ClawHub/OpenClaw pure writing package remains distinct and continues to use MIT-0.
- Red SkillHub, historical release evidence, tags, remote packages, and published v1.6.0 metadata are out of scope.

## Atomic product scope

1. Keep root `LICENSE` as MIT and root `LICENSE-SKILL` as MIT-0.
2. The canonical SkillHub package and byte-identical `skills/` Codex surface use `license: MIT`, include a package-local MIT `LICENSE`, and set the root Codex/Claude manifests plus the packaged Claude adapter manifest to `MIT`.
3. `.agents`, `.qwen`, Hermes, and OpenClaw/ClawHub keep `license: MIT-0` and receive a package-local MIT-0 `LICENSE`; they continue to exclude all gate assets.
4. Split the synchronizer's single license constant into explicit full-package and pure-Skill licenses. Do not infer license from whether a file happens to exist.
5. Update only the current README license table and deterministic boundary tests. Do not rewrite historical evidence.

## Non-behavioral boundary

This atom changes distribution metadata and package license files only. It does not change writing instructions, references, Hook execution, gate logic, routing, model prompts, or external host configuration. Real writing A/B is therefore not used as evidence for the license decision; deterministic prompt ablation must remain unchanged.

## Acceptance checks

- Canonical/`skills` frontmatter and all full-package manifests say `MIT`; their `LICENSE` bytes equal root `LICENSE`.
- Four pure-Skill mirrors say `MIT-0`; their `LICENSE` bytes equal root `LICENSE-SKILL`.
- SkillHub clean allowlist increases by exactly one file and contains MIT `LICENSE` plus all Hook assets.
- ClawHub/OpenClaw contains MIT-0 `LICENSE` and no gate assets.
- Sync is idempotent; canonical and `skills` stay byte-identical; focused/full tests, stub smoke, deterministic ablation, validators, JSON parsing, and `git diff --check` pass.
- Any mixed package whose frontmatter and bundled `LICENSE` disagree is a stop condition.
