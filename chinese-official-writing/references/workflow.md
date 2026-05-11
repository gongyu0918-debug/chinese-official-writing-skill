# Workflow

Use the "manuscript blueprint" method for formal Chinese plans, reports, research materials, feasibility studies, and official enterprise documents. Do not jump straight from scattered notes into a full article.

## 1. Prepare the brief

Confirm or infer these items:

- Document type: plan, report, feasibility study, research report, implementation plan, summary, briefing, request, or meeting material.
- Viewpoint: who is speaking and whose interest the document serves.
- Reader: leader, board, supervising authority, procurement reviewer, implementation unit, or internal department.
- Core conclusion: what decision or judgment the document should support.
- Source hierarchy: latest user-edited version first, then formal attachments, then notes, recordings, and online reference style.
- Data status: actual data, estimated data, missing data, and figures that must be highlighted.

If the user provides a latest file or version number, treat it as the main branch.

When the document type is unclear, load `genre-routing.md` before drafting. When the document type is clear but the content is thin, load `handling-elements.md` and identify missing required elements before writing.

## 2. Build the outline

Create a title-level outline before writing body text. The outline should show the document logic, not a generic template.

Choose a chain from `argument-chains.md` before drafting the outline. Keep the chain internal; do not print chain labels in the final text.

For construction plans and project materials, a common order is:

1. Background and conclusion.
2. Demand or necessity.
3. Cost calculation and comparison.
4. Implementation plan.
5. Benefits and expected results.
6. Security, compliance, and safeguards.
7. Implementation schedule or guarantee mechanism.

Adjust the order to the user's document and comments.

## 3. Create a paragraph map

For each section, list paragraphs before drafting. Each paragraph map item should include:

- Main point.
- Evidence or data.
- Judgment.
- Landing point for the project, policy, or work arrangement.
- Data source or calculation basis if numbers are used.

One paragraph should support one point. Merge or delete paragraphs that repeat the same point.

## 4. Draft small paragraphs

Write paragraphs in batches. For each paragraph:

- Put the main judgment near the beginning.
- Use concrete subjects such as the project, group, platform, system, business unit, or data.
- Replace teaching language with project language.
- Avoid explaining the writing method inside the document.
- Use estimates carefully and mark them as measurement or calculation results, not actual occurrence.

## 5. Review each paragraph

Before merging a paragraph into the section, check:

- Viewpoint: does it speak as the sponsor/reporting unit?
- Argument: does it make a document claim rather than explain a concept?
- Data: are units and calculations consistent?
- Wording: are there AI-flavor summary frames or口语化 phrases?
- Necessity: can any sentence be removed without weakening the point?

## 6. Review each section

After completing a section, check whether its first paragraph gives the section conclusion, whether all later paragraphs serve that conclusion, and whether it repeats other sections. If a section repeats another section, keep the version closer to the reader's decision need.

## 7. Merge and final-review

After all sections pass local review:

- Merge sections into one document.
- Unify numbering, terms, figures, and punctuation.
- Move repeated details to the strongest section and remove duplicate wording elsewhere.
- Check comments and user-specific instructions one by one.
- Run `scripts/prose_lint.py` when available.
- For DOCX, render to PDF or page images before delivery when layout matters.
