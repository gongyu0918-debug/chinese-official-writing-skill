# SkillHub MIT / pure-Skill MIT-0 license split v1.6.2 result

## Verdict

`ENGINEERING PASS / LICENSE SURFACES CONSISTENT / ELIGIBLE FOR LOCAL INTEGRATION`.

The next-version full SkillHub/Codex distribution uses MIT and carries the complete MIT text. The ordinary `.agents`, Qwen, and Hermes pure-Skill mirrors retain their MIT-0 package license. ClawHub/OpenClaw is frozen at its published v1.6.0 package, whose frontmatter and user-facing copy identify MIT-0 without a package-local license file. No writing instruction, reference, Hook implementation, gate state machine, route, or external configuration changed.

## Bound commits

- Fixed baseline: `1ae9d73f2f05eb33a9801f1146118403c195194d`.
- Preregistration: `eb7bdb9b`.
- Product and contract tests: `f3453e2a`.

## Package surfaces

| Surface | Frontmatter/manifest | Bundled license | Files |
| --- | --- | --- | ---: |
| canonical full package | MIT | root MIT bytes | 40 |
| SkillHub clean package | MIT | `LICENSE.md` equals root MIT bytes | 40 after excluding `agents/openai.yaml` and extensionless `LICENSE` |
| `skills/` Codex package | MIT | root MIT bytes | 40 |
| `.agents`, Qwen, Hermes pure Skill | MIT-0 | root `LICENSE-SKILL` bytes | per mirrored package |
| OpenClaw/ClawHub | MIT-0 | frozen v1.6.0 metadata; no package-local license | 32 |

- MIT SHA-256: `EAD35E40076582D7053FB0908588ADB878FF5108601A76647B9F5626B3A0D5F8`.
- MIT-0 SHA-256: `F2E66A0AFB821915DA09B79C1BF63DAF4F4EED3356F2D6B7AFF9A6FB763B7A7A`.
- Canonical, `skills/`, both root plugin manifests, and the packaged Claude adapter manifest declare MIT.
- The current pure-Skill mirrors retain MIT-0 package files; frozen OpenClaw frontmatter and user-facing copy remain MIT-0.
- Red SkillHub and historical evidence were not changed.

## Verification

| Check | Actual result |
| --- | --- |
| License/package focused tests | 5/5 passed |
| Full unittest discovery | 488/488 passed |
| Promptfoo stub smoke | 20/20 passed; `eval-554-2026-08-11T08:34:57` |
| Fixed `1ae9d73f` deterministic ablation | baseline 111/111; candidate 111/111 |
| Skill Creator quick validation | `Skill is valid!` |
| Codex plugin validation | passed |
| Claude packaged plugin validation | passed |
| Claude no-model preflight | Claude 2.1.195, zero errors, no model invocation |
| Python compilation | 4/4 passed in a system temporary directory |
| Manifest JSON parsing | passed for Codex, root Claude, and packaged Claude manifests |
| Synchronizer | two consecutive runs preserved the same tracked patch |
| `git diff --check` | passed |

The first full discovery run had one expected contract failure: `test_skill_context_is_complete_and_within_eval_budget` still required the pure `.agents` frontmatter to be byte-identical to canonical. The product intentionally splits only the license frontmatter while retaining an identical executable body. The test was narrowed to require the selected package text in the evaluation context and byte-equivalent executable bodies; the complete rerun then passed 488/488. The initial failure is retained here rather than hidden.

Promptfoo reported that local version 0.121.11 is behind 0.122.0; the frozen stub suite still completed without failure or error. No dependency upgrade was performed.

## Remaining boundary

- This is a package metadata and bundled-license change, not a writing-quality claim. No real-writing A/B was run for this atom.
- Public SkillHub/ClawHub packages remain at v1.6.0 until an authorized release; this candidate does not change remote state, tag, or published license metadata.
- Release checks must use the new expected count: SkillHub clean 40. ClawHub/OpenClaw is frozen at the published v1.6.0 tree and no longer participates in this release line.
