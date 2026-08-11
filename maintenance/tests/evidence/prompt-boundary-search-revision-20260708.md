# Prompt Boundary Search/Revision Test - 2026-07-08

## Scope

This evidence records a minimal prompt/reference update after real writing tests found two weak-model risks:

- When asked to search for similar articles or supplement arguments, weak models may use academic/vendor sources first or fabricate source context when no web access exists.
- In activity-period internal notices, weak models may expand a simple reminder into management actions such as duty shifts, patrols, records, reporting, discipline handling, or hard execution language.

The update stays prompt/reference-only. It does not add lint rules, scripts, hard gates, default web search, or blocking confirmation steps.

## Changes Tested

- Search argument priority:
  - Prefer same-genre/same-scenario official public documents from government organs, public institutions, state-owned enterprises, and similar formal bodies.
  - Then use domestic mainstream or industry media.
  - Use academic papers, vendor technical documents, or foreign sources only when the task needs technical judgment such as model routing, cost models, AI compute, or architecture.
  - Borrow only argument angle, structure, risk dimension, and wording scale; do not turn other organizations' practices into this user's facts.

- No-web boundary:
  - If the agent has no web/search capability, it must not fabricate search process, source names, links, dates, or "verified" status.
  - If the user asks to "appropriately supplement arguments" but no source can be checked, the draft may include only general reasoning that does not introduce new facts.
  - Concrete management actions, responsibility, process, handling, feedback, reporting, deadlines, records, patrols, duty shifts, or discipline measures should stay out of the body unless supplied by the user. If useful, list them outside the body as candidate supplements and mark them as unverified writing supplements.

- Reminder-notice boundary:
  - For activity, sports event, holiday, or special-period internal reminder notices, stay close to the user's supplied prohibitions, attendance reminders, civilized-conduct language, reporting requirements, or greeting text.
  - Attendance reminders should not expand into leave-request workflows, duty coverage, or work-continuity arrangements unless supplied.
  - Civilized-conduct reminders should not expand into publicity organization or public-opinion prevention unless supplied.
  - If the user asks for a softer tone, do not upgrade the wording to "strict", "resolute", "serious handling", or similar command language.

## Real Writing Checks

### No-web weak-model notice, before tighter reminder rule

Prompt: no web/search tools; user asks to search similar public unit notices and draft a short World Cup-period notice for Red Star Publishing House.

Result: FAIL/WARN. The output did not fabricate source links and disclosed no web access, but still added unprovided actions:

- duty/position arrangements,
- internal publicity,
- discipline handling,
- reporting to the office,
- patrol/record-like management logic.

This showed that the first abstract "no concrete management actions" boundary was not enough for weak models.

### Cost-optimization strong-model no-web supplement

Prompt: no web/search tools; user allows adding arguments for a Banshentong model-cost recommendation.

Result: PASS. The output kept the body on the supplied facts and marked "sampling, review, fallback rules" and "phased cost evaluation" as writing supplements outside the body, with a note that no public sources were searched.

### No-web weak-model notice, after reminder-notice tightening

Prompt: same no-web World Cup notice, with the updated skill loaded.

Result: improved WARN/PASS. The output no longer fabricated source names, links, dates, or verified status. It did not add duty shifts, patrol records, reporting, feedback, responsible-person duties, or serious handling. It placed the no-web note outside the body.

Residual risk: weak model still generalized "betting" into "涉赌、私彩、赌球相关讨论" and added mild abstractions such as "网络交流秩序" and "工作节奏有序". These are wording expansions rather than concrete management actions. Do not one-off patch unless this appears repeatedly.

## Deterministic Checks

- `python -m unittest tests.test_skill_boundary`: passed after sync.
- `git diff --check`: passed, with only Windows line-ending warnings.

