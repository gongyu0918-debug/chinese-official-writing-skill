# Hook request fact safety atom result

## Result

Fixed parent `5cc551c94518452e8b10e5c7be9002a16753e603` reproduced two independent problems when the Hook had no separate source file:

- A request-supplied and explicitly required negative result was still detected as `unsupported-negative-claim`. P001 then attempted a rewrite, returned `replacement_retains_protective_pattern`, selected D0, and spent a Stop cycle without changing the delivered draft.
- A sentence carrying pending procurement, approval, responsibility, or deadline state could be rewritten to a different pending object and reach D1 when unrelated document-length fallback did not mask it.

Candidate `2a4d462a` narrows the shared review gate in three places:

1. A negative result is treated as request/source authority only when the same negative event and object are supplied outside a nearby deletion or prohibition instruction. The P001 wording pair `未发现同类现象` / `未发现同类异常现象` is the only wording normalization added.
2. A pure unsupported negative sentence with no structured hard anchor may use DELETE. Mixed sentences, numbered/date-bearing results, and required facts retain the existing fallback rules.
3. REWRITE preserves the negative-result object. If the request or source carries pending procurement decision, approval, responsibility, or deadline objects also present in the target, the replacement must retain those objects; otherwise mechanical verification selects D0.

The Hook reference now states the same division. The adapter prompt already requires preservation of supplied facts, judgment strength, and pending state, so no competing prompt rule or new Hook state was added. Cause wording such as `原因尚未查明` and `正在核查` does not enter the protected-object check and remains a clean no-finding case.

## Over-strict attempt retained as evidence

The first uncommitted implementation required every semantic-sensitive unresolved rewrite to be text-anchored in request/source. It caused 13 failures and 1 error in the 178-test review-gate/Hook suite and also changed established fallback reasons. That implementation was discarded. The committed mechanism protects only the four observed pending-object classes plus the exact negative-result object, and the original 178 tests return to green.

## Verification

| Check | Result |
| --- | --- |
| `python -B -m unittest tests.test_review_gate_request_fact_safety -v` | 6/6 pass |
| `python -B -m unittest tests.test_review_gate tests.test_gate_stop_hook` | 178/178 pass |
| `python -B -m unittest discover -s tests -p "test_*.py"` | 510/510 pass |
| `OFFICIAL_WRITING_EVAL_STUB=1 python -B evals/official-writing/run_eval.py --suite smoke --judge-batch-size 2` | 20/20 pass; `eval-HBQ-2026-08-11T11:45:48` |
| `python -B tools/run_real_prompt_ablation.py --baseline-root <5cc551c9> --current-root <candidate>` | baseline 111/111; candidate 111/111 |
| Skill Creator `quick_validate.py chinese-official-writing` | `Skill is valid!` |
| `python -B tools/preflight_claude_hooks.py --plugin-dir chinese-official-writing/hooks/claude-code` | no errors; no model invocation; no configuration mutation |
| `py_compile` canonical and full-package mirror | pass |
| `sync_adapters.py` twice, `git diff --exit-code`, `git diff --check` | pass; idempotent |

Canonical and full-package mirror `review_gate.py` SHA-256 are both `1B743298E9413C30A8F81D2B9275317D56529834B4841F404384E708C5CA3A32`.

## Boundary

This atom does not claim that Hook-enabled writing is globally better; the prior real A/B remains HOLD. It removes one demonstrated no-benefit P001 trigger and closes two mechanical rewrite escapes. It adds no independent length gate, model call, retry, second repair, general semantic-similarity threshold, or word-list style ban.
