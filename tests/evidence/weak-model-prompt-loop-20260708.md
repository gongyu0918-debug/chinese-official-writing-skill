# Weak-model prompt loop evidence, 2026-07-08

Baseline: `446c08c`

Purpose: test whether small prompt-only changes can stabilize weak-model low-reasoning writing quality for the six real prompts used in the current release-prep loop.

Models:

- Writer: `gpt-5.3-codex-spark`, low reasoning, isolated context, loaded `chinese-official-writing/SKILL.md`.
- Verifier: `gpt-5.5`, low reasoning, isolated context, judged only prompt plus output.

Prompts covered:

1. RTX 5090 computer purchase situation explanation for Banshentong small-model testing.
2. Weibo operations situation explanation.
3. Claude Code affected-version security notification.
4. Weather warning commute/safety reminder from public source material.
5. World Cup anti-gambling and attendance reminder notice.
6. OpenClaw installation-status report.

Tried and reverted candidates:

1. `workflow.md` sparse-material short-draft wording.
2. `SKILL.md` front-loaded "three delivery habits" wording.
3. `SKILL.md` long-rule split into shorter bullets without changing semantics.
4. `SKILL.md` one-pass silent cleanup wording before delivery.

Common verified failures:

- Markdown residue repeatedly remained in formal drafts: `**...**`, `###`, or bolded inline labels.
- Sparse or public-source material still expanded into unprovided execution chains, such as duty watch, patrol, reporting, contact person, response linkage, filing/备案, verification scope, or feedback deadlines.
- Situation explanations still drifted into approval language such as "建议批准" or "请予同意".
- Weak-model outputs often preserved the document genre skeleton, but the fact boundary was not stable enough for release.

Useful finding:

- Explicit second-round user correction works better than silent prompt rules. When the weak model was given the bad draft plus specific correction points, it often removed Markdown and most unsupported execution chains. This did not transfer reliably when written as an automatic "silent cleanup once" rule in the skill.

Decision:

- Do not keep any of the four candidates above.
- Do not continue adding similar `SKILL.md` prompt restrictions; they increased noise or failed to change weak-model behavior.
- Next viable path should be a separate, explicitly-invoked repair/check workflow or tool-assisted final-draft inspection, with real A/B testing before any release claim.

Validation run during the loop:

- `python -m unittest tests.test_skill_boundary`: passed for attempted candidates before real-writing rejection.
- `git diff --check`: passed for attempted candidates before real-writing rejection.
- `tools/run_real_prompt_ablation.py` against `output/release-baselines/pre-loop-446c08c`: no new deterministic regression; both baseline and current remained `92/95`, with the same known P031-P033 anchor failures.

