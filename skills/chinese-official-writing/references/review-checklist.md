# Review Checklist

Use this checklist at three levels: paragraph, section, and full document.

## Paragraph Review

- Viewpoint: the paragraph speaks from the correct sponsor/reporting unit.
- Main point: the first sentence or first half of the paragraph carries the judgment.
- Evidence: data, fact, policy, business need, or practical condition supports the point.
- Landing: the paragraph returns to the project, work arrangement, or decision.
- Argument chain: the paragraph fits the selected chain from `argument-chains.md` and does not mix unrelated claims.
- Style: no teaching voice, side-commentary, or casual wording.
- AI flavor: no obvious paired-summary frames or mechanical transitions.

## Section Review

- The section has one clear task in the article.
- Heading fit: if the heading was user-specified, keep it and revise the body to match; if generated, polish headings that drift, duplicate, or overpromise.
- The first paragraph gives the section conclusion.
- Paragraph order moves from conclusion to support to arrangement.
- Data units stay consistent inside the section.
- Repeated points are merged.
- Adjacent paragraphs do not repeat the same matter unless the later paragraph adds data, reason, responsibility, risk, deadline, or acceptance.
- Missing data is left blank, marked for follow-up, or described as estimated only when the user permits estimation.
- The section follows its genre's formal expectations. Load `genre-checklist.md` for notices, requests, reports, explanations, plans, applications, letters, replies, approvals, public notices, circulars, and minutes.
- The section follows the selected handling logic. Load `genre-routing.md` when the genre is ambiguous, and `handling-elements.md` when required items may be missing.

## Full-Document Review

- The title, viewpoint, and conclusion match the user's latest instruction.
- The main title is not changed unless the user asked for it.
- Generated headings receive a second-pass polish; fixed headings receive a body-fit check.
- The document's function matches its genre. Requests for approval are not hidden in reports, and reports do not end like requests for approval.
- Required handling elements are present or explicitly left for user confirmation.
- The main argument follows one suitable chain: request, report, notice/coordination, plan/construction, feasibility/review, or AI compute/technical service.
- The structure answers the reader's decision question.
- All critical user comments are addressed.
- Tables are used only where needed; prose carries the main argument.
- Tables are not used to avoid writing a difficult argument.
- Figures and highlighted data are consistent across sections.
- "建设背景", "必要性", "成本测算", "收益", "建设方案", "建设成效", and "安全保障" do not repeat the same claims.
- Terms are unified across the file.
- Final Word formatting preserves the source template unless the user requests a new format.
- Public-document plausibility is checked: dates, deadlines, attachments, contact channels, responsible units, approval basis, process language, and implementation responsibilities are present where the genre normally requires them.
- Repeated template phrases are reduced. Watch for frequent starts such as `总体看`, `重点任务包括`, `保障措施包括`, and `形成一批`.
- Thought leakage is removed: no AI identity, hidden reasoning, prompt references, recording instructions, or user-editing process in the final document.
- Format noise is checked: Chinese punctuation, number spacing, number grouping, first-line indentation, list-marker frequency, table overuse, and Emoji/decorative bullets.
- AI compute technical documents are checked with `ai-compute-docs.md`: business demand, Token/resource conversion, cost comparison, server scale, SLA, concurrency, operations, security, service period, acceptance, and actual/estimated data separation are all clear.
- Community style references are used only as auxiliary writing and review methods. Official genre functions and user templates take precedence.

## Optional Independent Review

Use an independent reviewer only when the user asks or the document is high-stakes. Ask the reviewer for concrete findings on:

- wrong viewpoint,
-口语化 wording,
- AI-flavor sentence frames,
- unsupported or conflicting data,
- repeated paragraphs,
- logic gaps between claim and evidence.
- repeated matters between adjacent paragraphs or sections,
- title/body drift and heading overreach,
- format noise such as half-width punctuation in Chinese prose, number spacing, list-marker overuse, table overuse, and Emoji.

Pass compact excerpts or the final draft, not internal reasoning.
