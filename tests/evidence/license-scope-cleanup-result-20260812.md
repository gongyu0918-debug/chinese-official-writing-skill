# License scope cleanup result

## Outcome

The cleanup makes MIT the explicit license for the GitHub repository and every non-ClawHub package and repository surface. MIT-0 is limited to the frozen `openclaw/` tree and the ClawHub package derived from it. No writing rule, reference, Hook behavior, package version field, tag, remote, release, or marketplace state changed.

Fixed baseline: `2e0e6b30fb76ed7b53c32d0d879e92ccbfac34b9`.

Branch: `codex/license-scope-cleanup`.

Implementation commits before this result record:

- `bf721058`: switch non-OpenClaw package licenses and synchronizer behavior to MIT.
- `234aa21e`: move the preserved MIT-0 exception text under `licenses/` so root `LICENSE` remains the sole root license text.

## Final license boundary

| Surface | License and proof |
| --- | --- |
| GitHub repository | Root `LICENSE`, MIT, SHA-256 `EAD35E40076582D7053FB0908588ADB878FF5108601A76647B9F5626B3A0D5F8` |
| canonical and `skills/` | package-local `LICENSE` byte-identical to root MIT |
| `.agents`, Qwen Code, Hermes | package-local `LICENSE` changed from MIT-0 to root MIT bytes |
| SkillHub clean package | generated `LICENSE.md` byte-identical to root MIT; 46 files at version coordinate 1.6.1 |
| Codex, Claude Code, WorkBuddy and packaged Hook companions | plugin manifests remain `license: MIT`; Hook code remains inside the MIT package scope |
| Red SkillHub source | its existing platform-specific frontmatter now declares `license: MIT`; no upload was attempted |
| tools, tests, evals, evidence, build records and docs | MIT under root `LICENSE`, stated explicitly in `LICENSE-SCOPE.md` and README |
| frozen `openclaw/` and derived ClawHub package | MIT-0 only; full text at `licenses/LICENSE-CLAWHUB` |
| third-party material | retains the license declared by its respective rightsholder |

The MIT-0 text was not edited while moving from the obsolete generic `LICENSE-SKILL` name. Both old and new content resolve to Git blob `80f996ba922ea77a9173eba687f9664dc55a01f0`.

## Verification actually run

- Focused license-boundary plus SkillHub builder suite: 79/79 PASS before the final documentation refresh; the final focused boundary/builder recheck was 5/5 PASS.
- Full unittest discovery after the README v1.6.0 output was inserted: 521/521 PASS in 21.681 seconds.
- `tools/sync_adapters.py` ran twice; both runs preserved candidate diff hash `1b8d7eeab98ea952b60877b1e01bed95f3f81e74` and introduced no additional change.
- `tools/build_skillhub_package.py --version 1.6.1`: PASS, 46 files; generated `LICENSE.md` SHA-256 equals root MIT SHA-256 above.
- Skill Creator `quick_validate.py`: canonical, `skills`, `.agents`, `.qwen`, and Hermes all PASS.
- The generic Skill Creator validator was also tried on the historical Red SkillHub package and rejected its platform-specific `slug`, `displayName`, `homepage`, `summary`, `tags`, and `version` fields. This is a validator/schema mismatch, not a license failure; the repository boundary test parsed that frontmatter and confirmed `license: MIT`.
- `claude plugin validate .`: PASS with the pre-existing advisory that the root Claude manifest has no author field.
- The installed Codex CLI exposes no `plugin validate` subcommand, and CodeBuddy CLI is unavailable. Five relevant JSON manifests were parsed directly and all declared MIT; repository host/package tests cover their structure.
- Local Markdown link check: PASS.
- `git diff --check`: PASS.
- `openclaw/` relative to `0f6ec603993d5595e784fa7079837e299d1b0da3`: zero diff.
- canonical `SKILL.md`, references, and `prose_lint.py` relative to the fixed baseline: zero diff.
- root and packaged plugin/version manifest surfaces relative to the fixed baseline: zero diff.
- README prompt block and no-Skill block stayed byte-stable; the v1.6.0 Skill output and two valid blind verdicts are recorded separately in `readme-v160-same-task-comparison-20260812.md`.

## Distribution and legal limits

- This branch was not merged, pushed, tagged, released, or uploaded. Existing public packages retain the license under which they were published until a separately authorized update occurs.
- Repositories with copyright contributions from other rightsholders may require their consent before imposing MIT's attribution condition on previously MIT-0 material. This engineering cleanup is not legal advice; confirm contributor authority before publication if ownership is not already centralized.
- The frozen ClawHub package still has no new package-local license file because changing it would violate the fixed v1.6.0 zero-diff boundary. Its MIT-0 identifier remains in the frozen package, and the full current exception text is available at `licenses/LICENSE-CLAWHUB` for any future separately authorized ClawHub build.
