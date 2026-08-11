# Review-gate document invariant extraction preregistration

Date: 2026-07-25

## Fixed baseline

- Baseline: local stable `main` at `cb2b51e53412a5aa212e084edacde77a32d6427b`.
- Candidate branch: `codex/refactor-review-gate-invariants-v1524`.
- The canonical target is `chinese-official-writing/scripts/review_gate.py`.

## Reproduced god-function evidence

`evaluate_candidate` spans 325 lines and combines repair protocol validation, authorization, text-application planning, hard-anchor verification, document-shape and length invariants, and D0/D1 selection. Existing tests directly call it in 59 locations. The stateful transaction functions and `gate_stop_hook.handle_stop` remain out of scope.

## Single extraction

Extract only the current document-shape and length checks into the same-file private pure helper:

`_candidate_document_invariant_reason(request, draft, candidate, repair_mode) -> str | None`

Preserve this exact reason priority:

1. `heading_or_title_changed`
2. `body_or_section_emptied`
3. `body_content_collapsed`
4. `candidate_length_expansion_exceeded`
5. `prompt_length_compliance_worsened`

`evaluate_candidate` calls the helper after the existing hard-anchor checks and returns D0 with the returned reason. It retains its signature, detection recomputation, repair authorization, hard-anchor logic and final D1 reasons.

Do not change any CLI, exit code, stdout, JSON schema, state transition, hash, retry budget, D0/D1 fallback, reason string, script file list or OpenClaw package contents. Do not split `detect_transaction`, `prose_lint.scan` or `gate_stop_hook.handle_stop` in this candidate.

## Tests

Add direct helper tests for all five reasons, a no-error `None` case and a multiple-violation priority case. Existing public `evaluate_candidate` and CLI tests remain unchanged.

Run:

- `tests.test_review_gate`;
- `tests.test_gate_stop_hook`;
- `tests.test_review_regressions`;
- `tests.test_real_prompt_ablation`;
- full unittest;
- Promptfoo smoke;
- deterministic ablation against `cb2b51e`;
- Skill Creator quick validation;
- canonical/mirror byte equality;
- `git diff --check`.

The baseline and Candidate must produce identical public `CandidateResult`, reason strings, emitted text, state behavior and test results. Any byte-level public output, JSON/state, hash, CLI or exit-code difference is `FAIL`.

This is a mechanical post-draft verifier refactor. It does not generate new writing samples; existing deterministic repair and transaction tests are the real-path validation surface.
