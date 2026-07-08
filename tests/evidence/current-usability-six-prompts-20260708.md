# Current Usability Test - Six Real Prompts

Date: 2026-07-08

Scope: test current workspace candidate with the six user-requested real writing prompts. This is a usability check, not a release decision.

## Method

- Writer A: `gpt-5.4-mini`, low reasoning, loaded `chinese-official-writing` skill.
- Writer B: `gpt-5.5`, low reasoning, loaded `chinese-official-writing` skill.
- Verifier: independent `gpt-5.5`, low reasoning, only saw prompts, webpage facts, and both writer outputs.
- Web facts checked by main context:
  - Eastmoney repost of MIIT risk notice: Claude Code affected versions are `2.1.91` through `2.1.196`.
  - Xinhua/China Weather article: Central Meteorological Observatory continued orange rainstorm warning at 2026-07-08 06:00, with heavy rain risks in Guangxi, Guangdong, Hainan, Hunan, Heilongjiang, Jilin, Liaoning, Shandong and Yunnan, plus short-time heavy rain and thunderstorm/gale risks.

## Prompts

1. Computer purchase situation explanation for RTX 5090 / 35B model / Banshentong / harness / desensitized internal AI processing / OCR / text-to-image.
2. Weibo situation explanation with daily 200 posts, 1 million daily reads, 5 million followers, 5% monthly growth, 21:00-23:00 peak, weak local news traffic.
3. Convert Eastmoney Claude Code risk article to internal notice, require deletion of affected versions or report none, DingTalk report by 2026-07-10 15:00 to technical application department.
4. Convert Xinhua weather article to commuting safety notice, sender is 二十一世纪出版社集团办公室.
5. Notice to 红星出版社 departments and subsidiaries during 2026-06-11 to 2026-07-19 World Cup: no betting, strengthen attendance, but wish happy viewing.
6. Report to 江西出版集团 from 红星出版社: OpenClaw and any "小龙虾" variants not found after check.

## Verifier Result

Overall:

- Strong model: `WARN`, usable but tends to expand brief user facts into institutional procedures, follow-up actions or management requirements.
- Weak model: `WARN`, can produce usable short drafts but URL-based rewriting is not stable enough for direct delivery.

Weak model details:

- P1 `PASS`: all user-supplied purchase reasons entered the draft.
- P2 `PASS`: all supplied Weibo metrics and next-step local-news point entered the draft.
- P3 `WARN`: did not extract the concrete affected Claude Code versions `2.1.91` to `2.1.196`; used the generic phrase `相关版本`.
- P4 `WARN`: did not preserve the orange warning time, named regions or concrete weather-risk facts; generalized to `天气变化较快`.
- P5 `PASS`: covered no betting, attendance, audience and good-wishes tone.
- P6 `WARN`: covered conclusion but added mild unsupported scope/source phrases such as `根据要求` and `所属终端设备`.

Strong model details:

- P1 `WARN`: high quality but added extra technical details and ended with `建议按程序推进采购工作`, shifting a situation explanation toward a proposal.
- P2 `WARN`: covered metrics but added unsupported analysis dimensions such as title appeal and interaction metrics.
- P3 `PASS`: extracted `Claude Code 2.1.91 至 2.1.196`, risk notice, deletion/uninstall, deadline, DingTalk and department.
- P4 `PASS`: extracted orange warning, time, regions and strong-convection risks; sender correct.
- P5 `WARN`: covered required points but added stricter discipline items such as serious handling and workplace discussion limits.
- P6 `WARN`: covered report relation and conclusion but added unsupported terminal scope and follow-up software-management actions.

## Common Risks

1. URL material is still weak-model sensitive. Weak models may use generic phrases instead of extracting version numbers, dates, named regions and concrete risk ranges.
2. Strong models still tend to over-expand sparse materials into procedure chains, follow-up actions, responsibility scope or management requirements.
3. Report and situation-explanation drafts can drift into `下一步`, `持续做好`, `按程序推进` style endings when the user only supplied current facts or a brief explanation.
4. No sampled output showed Markdown residue, AI process text or task blocking.

## Current Judgment

The current candidate is usable for assisted drafting, especially with stronger models. It is not yet safe to call fully stable for weak-model URL rewriting or sparse-fact formal reports. Keep using real writer/verifier tests before any release decision.
