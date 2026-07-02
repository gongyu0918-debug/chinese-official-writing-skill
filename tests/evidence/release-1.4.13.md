# Release 1.4.13 Evidence

Release target: `chinese-official-writing@1.4.13`

This release packages the GLM5.2/OpenCode review follow-up at `cb7c8d3` plus a metadata bump to `1.4.13`. It does not add new hard gates, lint rules, search behavior, or writing workflow stages.

## Baseline

- GitHub `origin/main` before this release: `b2fc5ba983e6544f5a791b3f3df82c821016e698`.
- GitHub tag `v1.4.12`: `d7524bde5cb4fe69d2fb4b9572d10a8253afe2f5`.
- ClawHub latest before this release: `1.4.12`, moderation clean.
- Local behavior fix commit before metadata bump: `cb7c8d3 fix: tighten review-reported prompt and lint boundaries`.

## What Changed

- Bumped canonical and adapter metadata from `1.4.12` to `1.4.13`.
- Fixed `tools/sync_adapters.py` so future version bumps also update existing `version: "x.y.z"` fields in canonical `SKILL.md` and copied adapter frontmatter.
- Synchronized Codex/Claude, `.agents`, `.qwen`, Hermes, OpenClaw, README, plugin manifest, marketplace readme, and skill card versions.

## 1.4.12 Baseline Ablation

Command:

`py -3.14 .\tools\run_real_prompt_ablation.py --baseline-root output\release-baselines\github-1.4.12-publish-1.4.13 --baseline-label baseline-1.4.12 --current-root . --out output\real-prompt-vs-1.4.12-release-1.4.13`

Result:

- `baseline-1.4.12`: 55 cases, 55 passed, 0 failed.
- `current`: 55 cases, 55 passed, 0 failed.

Conclusion: no deterministic regression against the 1.4.12 release baseline.

## Real Writing Sanity

Writer subagent produced three short samples with the current `1.4.13` candidate:

- W1: 220-character hard disk purchase application with applicant, date, SSD, 2T, quantity 1, price 2000 yuan, and approval closing.
- W2: revision that only moved contact and phone to the end of the second paragraph without adding headings or paragraphs.
- W3: format/tone review of a short notice, requested not to rewrite the full text.

Independent verifier result:

- W1: PASS.
- W2: PASS.
- W3: WARN. The output did not rewrite the full text and gave position/risk/suggestion, but format review coverage was light because it did not mention notice signature/date or line-break issues.

Release decision: this is a residual quality risk for review-mode completeness, not a release-blocking regression. It is not caused by the metadata bump and does not show task blocking, format destruction, or fact fabrication.

## Release Checks

- `py -3.14 -m unittest discover -s tests -v`: 95 tests passed.
- `npm run eval:official-writing:smoke`: 20/20 passed; skill wins 10, baseline wins 0, tie 0; judge consistency 1.0.
- `py -3.14 .\tools\run_real_article_eval.py --out output\real-article-release-1.4.13`: completed.
- `py -3.14 .\tools\sync_adapters.py`: completed.
- `py -3.14 C:\Users\2\.codex\skills\.system\skill-creator\scripts\quick_validate.py chinese-official-writing`: `Skill is valid!`.
- `git diff --check`: passed; only Windows line-ending warnings were printed.

## Remaining Risk

- `run_real_article_eval.py` still reports placeholder-risk labels for anonymized sample terms such as `主送单位` and `发文字号`; this is an existing evaluation-audit limitation, not a new 1.4.13 regression.
- Review-mode output may under-cover format details when the prompt asks for both format and tone in a very short sample. Record as a follow-up quality observation; do not patch in this release without a broader real-writing pattern.
