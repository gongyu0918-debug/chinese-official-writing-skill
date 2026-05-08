# official-writing

`official-writing` is a Codex skill for Chinese official-document writing. It helps draft and revise formal Chinese materials such as notices, requests for instructions, reports, explanatory notes, plans, applications, letters, replies, approvals, public notices, circulars, meeting minutes, work summaries, research reports, feasibility studies, implementation plans, and construction plans.

The skill is designed for public-sector, state-owned-enterprise, and formal enterprise writing where the document must read like a real working draft rather than a generic AI answer.

## What It Improves

- Builds a manuscript blueprint before writing: outline, paragraph map, small paragraph points, paragraph review, section review, and full-document review.
- Keeps the sponsor viewpoint stable, such as a government office, group company, project unit, or reporting unit.
- Reduces teaching voice and side-commentary such as "this document explains..." or "the following lists...".
- Flags common AI-flavor sentence frames and template phrases.
- Provides genre-specific checks for common Chinese official-document types.
- Includes a special reference for AI computing-power documents, including feasibility reports, computing resource procurement, GPU/server rental, cloud-cost comparison, SLA, operations, acceptance, and data security.

## Repository Layout

```text
official-writing-skill/
├── official-writing/
│   ├── SKILL.md
│   ├── agents/
│   │   └── openai.yaml
│   ├── references/
│   │   ├── ai-compute-docs.md
│   │   ├── anti-ai-patterns.md
│   │   ├── format-gbt9704.md
│   │   ├── genre-checklist.md
│   │   ├── official-style.md
│   │   ├── review-checklist.md
│   │   └── workflow.md
│   └── scripts/
│       └── prose_lint.py
└── tests/
    └── evidence/
        ├── ablation-summary.md
        └── validation-summary.md
```

## Install

Copy the `official-writing` folder into your Codex skills directory:

```powershell
Copy-Item -Recurse .\official-writing "$env:USERPROFILE\.codex\skills\official-writing"
```

Then invoke it in prompts with:

```text
Use $official-writing to draft a Chinese official-style implementation plan.
```

## Lint Helper

The bundled lint helper reports risky prose patterns. It does not rewrite text.

```powershell
python .\official-writing\scripts\prose_lint.py .\draft.md
python .\official-writing\scripts\prose_lint.py .\draft.docx
```

It currently checks for high-risk paired summary frames, side-commentary, casual expressions, repeated template phrases, and vague AI-compute claims.

## Validation Evidence

This repository includes only anonymized validation summaries. Raw prompts and raw generated document drafts are not included.

Summary of local validation:

- General official-writing true ablation: same tasks, one output without the skill and one output using the skill. The skill output had no lint findings, while the no-skill output triggered paired-summary/template warnings. A blind independent review preferred the skill output for genre format, document-body viewpoint, and public-document realism.
- AI-compute true ablation: same AI-compute writing tasks, one output without the skill and one output using the skill. A blind independent review preferred the skill output for clearer lease rationale, Token/resource demand, cost comparison, SLA/concurrency, operations, acceptance, and data-security responsibility.
- AI-compute rule ablation: a generic baseline was compared with an AI-compute-calibrated draft. The calibrated draft replaced vague claims with measurable service, operations, acceptance, and security content.

Validation is intentionally summarized to avoid publishing private project facts, raw internal examples, or identifiable document content.

## Notes

- The skill does not guarantee political, legal, procurement, or accounting correctness. Human review is required before official use.
- When the source document has a unit-specific Word template, the template should take priority over default GB/T 9704-style settings.
- Estimates should be clearly separated from actual data.
- Specific names, dates, amounts, and policy references generated during drafting must be checked before use.
