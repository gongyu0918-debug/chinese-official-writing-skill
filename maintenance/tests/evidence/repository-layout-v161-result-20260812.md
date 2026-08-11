# Repository layout cleanup result (2026-08-12)

## Scope and binding

- Fixed base: `ff04d9eec4bd0dd84a2680647b074ae58541ca37`.
- Branch: `codex/repository-layout-cleanup`.
- Preregistration: `61cee2afd9ae6fc30ef0e92a139b00cb5b6cd873`.
- Layout and documentation commit: `58039c150ddbb3d584b0b00243b7c496ff011244`.
- Promptfoo root correction: `97258bd321a2449de6958ec5d619195d3a00ad9f`.
- No tag, push, GitHub Release, ClawHub upload, SkillHub upload, plugin installation, or plugin enablement was performed.

## Result

The tracked repository root now contains only `.gitattributes`, `.gitignore`, `AGENTS.md`, `LICENSE`, `README.md`, the canonical `chinese-official-writing/` Skill, `packages/`, and `maintenance/`.

- Platform adapters and distributable surfaces are grouped under `packages/`.
- Tests, evals, tools, package-manager files, evidence, and historical page snapshots are grouped under `maintenance/`.
- The canonical Skill and all writing references are byte-identical to the fixed base.
- The GitHub OpenClaw compatibility bundle is synchronized to version `1.6.1`, uses the repository MIT license, contains 31 Skill files, and excludes Hook files, plugin manifests, `review_gate.py`, `delivery-review-gate.md`, `agents/openai.yaml`, and package-internal README material.
- The root README presents only MIT, adds news and news-commentary capabilities, shows the real migrated structure, keeps five recent version rows and five recent evidence links, and removes internal platform scheduling text and the requested legacy evaluation wording.
- The previous ClawHub v1.6.0 marketplace copy and skill card remain under `maintenance/docs/platform-snapshots/clawhub-v1.6.0/` as historical evidence, not as a current GitHub package surface.

## Verification

- Focused Hook, package, Promptfoo, and boundary suite: `195/195` PASS.
- Full unittest discovery after path migration: `522/522` PASS; final post-fix discovery with the new repository-root regression: `523/523` PASS.
- Promptfoo stub smoke through the migrated command `npm.cmd --prefix maintenance run eval:official-writing:smoke`: `20/20` PASS, run `eval-81X-2026-08-11T21:26:20`.
- Promptfoo runner-specific regression: `85/85` PASS.
- Canonical and four general adapter quick validations: `5/5` PASS.
- Plugin validation for `packages/agent-plugin`, canonical, and the clean SkillHub package: `3/3` PASS.
- SkillHub clean-package build: 46 files; `LICENSE.md` byte-equal to root `LICENSE`; zero banned files.
- Sync tool run twice with identical diff hash; no second-run change.
- Key Python modules compiled successfully using a temporary `PYTHONPYCACHEPREFIX`.
- README/AGENTS/current-index local link audit: 21 links checked, zero missing.
- High-confidence secret-prefix scan: zero matches after excluding ignored dependency/output directories.
- Deterministic current suite: `111/111`; fixed pre-layout tree: `107/111`. The four baseline failures are path-layout anchors P020/P021/P022/P103, not writing behavior. Exact `git diff --exit-code ff04d9ee -- chinese-official-writing` passed.
- `git diff --check` passed.

## Transparent failed attempts

- The first post-migration focused suite failed on stale paths; after updating only layout contracts it passed `195/195`.
- The first post-migration full suite had three failures: stale AGENTS wording, the obsolete frozen-OpenClaw description assertion, and deterministic paths. After correcting those layout expectations it passed `522/522`.
- The first deterministic command included unsupported `--current-label` and exited before evaluation. The supported invocation completed normally.
- The first local-link audit snippet had a Python f-string syntax error and performed no repository write. The corrected audit checked all intended links.
- The first Promptfoo smoke passed but revealed `REPO_ROOT` had climbed one directory too far and wrote ignored output outside the worktree. Commit `97258bd3` restored the correct worktree root, added a regression assertion, and the repeated smoke passed `20/20` at the correct path.

## Remaining risks

- `npm ci` installed the locked Promptfoo dependency tree successfully but reported 37 dependency advisories (2 low, 17 moderate, 18 high). This task did not change dependency versions or run an automatic audit fix.
- Historical evidence retains its original paths and platform-license wording by design. The current README and current package contracts do not reuse those historical statements.
- Moving hundreds of evidence files creates a large Git rename diff, although their bytes are unchanged. Future references should use `maintenance/tests/evidence/` and `maintenance/docs/evidence/`.
