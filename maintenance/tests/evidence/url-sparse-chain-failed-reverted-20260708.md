# URL and Sparse-Report Prompt Patch Reverted

Date: 2026-07-08

This records a failed local prompt patch after commit `d0b47ab`. The patch was not retained.

## Attempted Change

The local patch tried two soft prompt refinements:

1. URL rewriting should extract concrete facts such as version ranges, dates, locations or affected objects, risks and required actions.
2. Situation explanations and completed-check reports should stop at the supplied conclusion when the user did not provide follow-up management actions.

The patch was synchronized to mirrors and guarded with deterministic P102/P103 cases. Deterministic ablation against `d0b47ab` passed as expected:

- baseline `d0b47ab`: `101/103`, failing only new P102/P103.
- current local patch: `103/103`.

Engineering tests also passed:

- `python -m unittest tests.test_real_prompt_ablation tests.test_skill_boundary`
- `python -m unittest discover -s tests`
- `git diff --check`

## Real Writing Retest

Two rounds of real writer/verifier tests were run with `gpt-5.4-mini` low reasoning and `gpt-5.5` low reasoning.

Round 1 result: `WARN`.

- Weak model improved on the Claude Code URL prompt and wrote `2.1.91 至 2.1.196`.
- Weak model still generalized the weather URL prompt and did not retain the full warning time and region scope.
- Weak model still added follow-up management actions to the OpenClaw completed-check report.
- Strong model mostly passed but sometimes became over-conservative when source access was uncertain.

Round 2 targeted retest result: `FAIL`.

- Weak model P3 retained `Claude Code 2.1.91 至 2.1.196`, but added unsupported reporting fields such as checked terminal count, issue count and disposition count.
- Weak model P4 regressed to generic weather wording and omitted the warning time, forecast period and complete affected-region scope.
- Weak model P6 still added unsupported follow-up actions including terminal software management, daily inspection and risk prevention.
- Strong model P4/P6 were usable, but P3 still added unsupported residual configuration/plugin/call-record checks and an unprovided sender.

Independent verifier recommendation: revert the uncommitted prompt patch. Continuing to pile constraints into the prompt would likely increase rule noise and might make stronger models over-conservative without reliably fixing weak-model behavior.

## Decision

The uncommitted prompt/test/mirror changes were reverted with `git restore`. The repository remains at commit `d0b47ab` behavior plus this evidence record.

Next iteration should not continue by adding more adjacent prompt clauses. Prefer a different approach, such as a lightweight post-generation check for URL facts and sparse-report unsupported follow-up actions, validated first with weak-model real prompts.
