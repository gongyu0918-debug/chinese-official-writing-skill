# Ablation Summary

Date: 2026-05-08

This summary describes anonymized ablation results. Raw test prompts and raw generated documents are intentionally excluded.

## General Official-Document Ablation

Setup:

- Same common official-writing tasks were given to two isolated agents.
- One agent received only minimal task prompts and no skill.
- One agent used `official-writing`.
- The outputs were reviewed with the lint helper and by an independent blind reviewer.

Result:

- The skill output had no lint findings.
- The no-skill output triggered paired-summary/template warnings.
- The blind reviewer preferred the skill output for genre format, document-body viewpoint, completeness of formal elements, and realism as a usable first draft.

Observed difference:

- No-skill output was usually readable but more generic.
- Skill output more consistently preserved document genre, added formal elements such as deadlines, attachments, responsible units, minutes metadata, and application/report headings, and reduced template flavor.

## AI-Compute Technical Official-Document Ablation

Setup:

- Same AI-compute tasks were given to two isolated agents.
- One agent received only minimal task prompts and no skill.
- One agent used `official-writing` with the AI-compute reference.
- A blind reviewer compared both outputs.

Result:

- The skill output was preferred overall.
- It was stronger on lease rationale, Token/resource demand, cost comparison, SLA/concurrency, operations, acceptance, and data-security responsibility.

Observed difference:

- No-skill output often described the topic correctly but stayed closer to an explanatory overview.
- Skill output more often used procurement/feasibility language: equivalent resources, performance basis, resource isolation, logs, monitoring, monthly utilization analysis, acceptance testing, fault recovery, replacement resources, and contract-managed service responsibilities.

## AI-Compute Rule Ablation

Setup:

- A generic official-writing baseline was compared with an AI-compute-calibrated draft.

Result:

- The generic baseline contained vague claims such as advanced computing power, powerful platform, or future development needs.
- The calibrated draft replaced those claims with measurable service scope, Token demand, scheduling, monitoring, SLA, acceptance, operations, and security content.

## Caution

These tests are smoke and regression tests, not a complete benchmark. Real official documents still require subject-matter, legal, policy, procurement, and financial review before use.
