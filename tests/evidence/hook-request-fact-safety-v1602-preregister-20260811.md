# Hook request fact safety atom preregistration

## Fixed candidate and observed failure

- Fixed parent: `5cc551c94518452e8b10e5c7be9002a16753e603`.
- The real Hook A/B P001 request supplied 48 checked records, required retention of the negative result, and had no separate source file. Detection still labelled the drafted result `unsupported-negative-claim`; the repair retained the required result and mechanical verification returned D0 with `replacement_retains_protective_pattern`.
- This atom changes only request/source authority handling for review-gate findings and repairs. It does not add a length gate, change Hook lifecycle states, increase repair budgets, call a model, or alter ordinary drafting rules.

## Frozen controls

1. A negative result supplied as material and explicitly required by the request is not a review finding, including the narrow wording pair `未发现同类现象` / `未发现同类异常现象`.
2. Quoting a sentence in an instruction to delete it does not make that sentence protected request authority; a pure unsupported negative sentence remains deletable.
3. A pure negative result absent from request and source remains a review finding and DELETE remains available without enabling arbitrary mixed-sentence deletion.
4. `原因尚未查明` and `正在核查` may coexist or substitute when the request supplies that cause status. This atom must not turn that normal status into a finding or a settled conclusion.
5. With no separate source, REWRITE cannot replace a supplied pending procurement decision, approval, responsibility, or deadline with another pending object. Failure selects D0. DELETE remains limited to proven pure expansion.

## Acceptance

- New focused controls pass and pre-change behavior is recorded before implementation.
- Existing review-gate and Hook tests pass.
- Full unittest, stub smoke, deterministic baseline/current gate, quick validation, adapter sync idempotence, and `git diff --check` pass before handoff.
- Any broader lexical ban, general semantic similarity threshold, or model-assisted decision is out of scope.
