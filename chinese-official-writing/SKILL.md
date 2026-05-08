---
name: chinese-official-writing
description: Use when drafting or revising Chinese official-style documents and formal enterprise/government materials, including notices, requests for instructions, reports, explanatory notes, plans, applications, letters, replies/approvals, opinions, decisions, announcements/public notices, bulletins, meeting minutes, work points, work summaries, research reports, feasibility studies, implementation plans, construction plans, review materials, AI computing power service feasibility reports, computing resource procurement or leasing plans, GPU/server rental procurement materials, and technical service requirement documents that require structured argumentation, Chinese official prose, formatting discipline, and low-AI-flavor wording. Not intended for English prose writing.
license: MIT-0
metadata:
  openclaw:
    version: "1.0.0"
    emoji: "📝"
    tags:
      - chinese
      - official-document
      - writing
      - gongwen
      - ai-compute
---

# Chinese Official Writing

Use this skill to produce Chinese official-style writing that reads like a document body, not like instructions about how to write a document.

## Core Workflow

1. Identify the document type, audience, sponsor viewpoint, core conclusion, required data, latest source file, and user comments. If these are mostly available, proceed without asking.
2. Build a manuscript blueprint before writing: outline -> paragraph map -> small paragraph points.
3. Draft by section or paragraph. Each paragraph serves one argument and normally follows: conclusion first, fact support, judgment, project/work landing point.
4. Review each small paragraph before merging. Then review each section. Then review the full document.
5. When editing DOCX, preserve the user's latest version and existing styles; create a new version unless the user asks to overwrite. Use the document/DOCX skill for Word operations and render checks.

## Required Discipline

- Write from the sponsor's viewpoint, such as the group company, government office, project unit, or reporting unit. Avoid a detached teaching or commentary voice.
- Keep data and claims traceable. Do not invent actual data; label estimates as estimates or calculations.
- Prefer plain official prose over technical display. Use specialized terms only when they help the argument.
- Avoid side-commentary, teaching voice, casual phrasing, and high-AI-flavor paired summary frames. Load `references/anti-ai-patterns.md` for Chinese examples and repair methods.

## References

Load only the reference needed for the current task:

- `references/workflow.md`: staged blueprint writing process and review gates.
- `references/official-style.md`: official-document sentence patterns, viewpoint control, and argument structure.
- `references/format-gbt9704.md`: common GB/T 9704-2012-style Word formatting defaults.
- `references/anti-ai-patterns.md`: AI-flavor, teaching-view, and casual-phrasing patterns to avoid.
- `references/genre-checklist.md`: genre-specific elements for notices, requests, reports, explanations, plans, applications, letters, replies, approvals, public notices, circulars, and minutes.
- `references/ai-compute-docs.md`: AI computing power, GPU/server rental, model service, procurement, leasing, feasibility, cost-comparison, SLA, and security writing patterns.
- `references/review-checklist.md`: paragraph, section, and full-document audit checklist.

## Script

Use `scripts/prose_lint.py` on `.txt`, `.md`, or `.docx` drafts when checking for banned patterns. It reports risks only; it does not rewrite text.
