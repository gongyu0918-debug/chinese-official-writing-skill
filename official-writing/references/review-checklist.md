# Review Checklist

Use this checklist at three levels: paragraph, section, and full document.

## Paragraph Review

- Viewpoint: the paragraph speaks from the correct sponsor/reporting unit.
- Main point: the first sentence or first half of the paragraph carries the judgment.
- Evidence: data, fact, policy, business need, or practical condition supports the point.
- Landing: the paragraph returns to the project, work arrangement, or decision.
- Style: no teaching voice, side-commentary, or casual wording.
- AI flavor: no obvious paired-summary frames or mechanical transitions.

## Section Review

- The section has one clear task in the article.
- The first paragraph gives the section conclusion.
- Paragraph order moves from conclusion to support to arrangement.
- Data units stay consistent inside the section.
- Repeated points are merged.
- Missing data is left blank, marked for follow-up, or described as estimated only when the user permits estimation.
- The section follows its genre's formal expectations. Load `genre-checklist.md` for notices, requests, reports, explanations, plans, applications, letters, replies, approvals, public notices, circulars, and minutes.

## Full-Document Review

- The title, viewpoint, and conclusion match the user's latest instruction.
- The structure answers the reader's decision question.
- All critical user comments are addressed.
- Tables are used only where needed; prose carries the main argument.
- Figures and highlighted data are consistent across sections.
- "建设背景", "必要性", "成本测算", "收益", "建设方案", "建设成效", and "安全保障" do not repeat the same claims.
- Terms are unified across the file.
- Final Word formatting preserves the source template unless the user requests a new format.
- Public-document plausibility is checked: dates, deadlines, attachments, contact channels, responsible units, approval basis, process language, and implementation responsibilities are present where the genre normally requires them.
- Repeated template phrases are reduced. Watch for frequent starts such as `总体看`, `重点任务包括`, `保障措施包括`, and `形成一批`.
- AI compute technical documents are checked with `ai-compute-docs.md`: business demand, Token/resource conversion, cost comparison, server scale, SLA, concurrency, operations, security, service period, acceptance, and actual/estimated data separation are all clear.

## Optional Independent Review

Use an independent reviewer only when the user asks or the document is high-stakes. Ask the reviewer for concrete findings on:

- wrong viewpoint,
-口语化 wording,
- AI-flavor sentence frames,
- unsupported or conflicting data,
- repeated paragraphs,
- logic gaps between claim and evidence.

Pass compact excerpts or the final draft, not internal reasoning.
