# Anti-AI Patterns

用于正式文稿定稿前的语言复核，重点排查模板腔、旁白腔、教学腔和口语化表达。

## High-Risk Sentence Frames

Avoid these frames in final text unless quoting source material:

- `不是……而是……`
- `不仅……还……`
- `不但……而且……`
- `既……又……`
- `一方面……另一方面……`
- `从……来看，从……来看，从……来看` repeated mechanically.
- `这不仅是……更是……`
- `可以说，……`
- `需要指出的是，……`
- `值得注意的是，……`
- `综上所述，……` when it only repeats the prior paragraph.

Repair method:

- State the positive conclusion directly.
- Split stacked claims into separate concrete sentences.
- Keep only the claim that helps the document's decision.
- Keep necessary negative comparison when it is a real decision distinction, legal boundary, or risk reminder; remove only decorative paired framing.

## Side-Commentary and Teaching Voice

Avoid phrases that tell the reader what the document is doing:

- `本方案重点说明三个问题`
- `重点说明 Token 用在哪里`
- `根据有关资料显示`
- `相关情况如下`
- `以下直接列出`
- `本文将从……`
- `本节主要介绍`
- `为了便于理解`
- `简单来说`
- `通俗地说`
- `可以理解为`

Prefer document-body language:

- `项目年度调用需求主要来自……`
- `租赁服务方式可将……纳入统一管理。`
- `相关费用随业务放量和模型升级呈上升趋势。`
- `项目实施后将支撑……`

## Thought Leakage and Drafting Process

Remove model identity, hidden reasoning, and drafting process from final text:

- `作为 AI……`
- `我的思路是……`
- `思考过程如下……`
- `接下来我会……`
- `按你的要求……`
- `领导要求……`
- `录音要求……`
- `这版文章……`

Prefer final-document wording:

- `项目拟……`
- `经测算……`
- `有关事项安排如下……` when the document itself needs a transition.
- `本次修订将……` only when the document is explicitly a revision note.

## Casual or Weak Phrases

Replace:

- `更稳，也更省` -> `成本和服务保障更具确定性`
- `用不完` -> `阶段性资源余量`
- `AI 味` -> `表述偏泛、判断不够具体`
- `搞清楚` -> `厘清`
- `哪里需要 Token` -> `Token 调用需求主要集中于`
- `这个钱花得值` -> `投入产出关系较为清晰`
- `老板/领导关心` -> `决策层重点关注`

## Empty Fillers

Delete or replace:

- `持续推进`, if no specific work follows.
- `不断提升`, if no measurable target follows.
- `充分发挥`, if no mechanism follows.
- `有力支撑`, if the object is vague.
- `全面赋能`, unless the document's style already accepts it.
- `形成一批`, if the target, quantity, or result form is unclear.
- `重点任务包括`, when it introduces a long generic list.
- `保障措施包括`, when it introduces a long generic list.
- `总体看`, when it only adds a filler transition.

## Overused Formal Terms

Use sparingly and only when necessary:

- `口径`
- `边界`
- `底座`
- `闭环`
- `生态`
- `抓手`
- `矩阵`
- `赋能`
- `体系化`

If one of these appears many times, replace some with concrete nouns such as `服务`, `平台`, `系统`, `流程`, `资源`, `费用`, `数据`, or `管理措施`.

## AI Compute Empty Technical Claims

For computing power, GPU/server rental, model service, and AI platform documents, avoid:

- `先进算力`, unless followed by specific GPU/server/model/service indicators.
- `强大平台`, unless followed by scheduling, monitoring, isolation, billing, or operation functions.
- `自主可控`, unless followed by deployment boundary, data location, permission, key, log, and audit measures.
- `成本更低`, unless the comparison period, demand, and cost items are stated.
- `满足未来发展需要`, unless it explains users, Token, concurrency, model upgrades, or agent workflows.

## Common Official-Writing Mistakes

- 文种错位：把请示写成报告，或者在报告中夹带请求审批事项。
- 主体错位：把发文单位写成旁观者、顾问或写作教师。
- 标题漂移：大小标题强调的是一个事项，正文却转向另一个事项。
- 胶水连接：上一段已经说明的事项在下一段换词重复，没有新增事实、判断或安排。
- 结论后置：先铺概念、背景、趋势，最后才写项目判断。
- 论据空转：有观点无数据，有数据不换算，有金额不说明对应需求。
- 技术堆叠：列一串模型、GPU、并发、SLA 名词，但不说明业务使用场景。
- 成本比较失衡：只比较单项 API 价格，不比较云资源、运维、安全、服务保障和扩容风险。
- 责任缺位：方案写了目标和任务，但没有实施主体、时间安排、验收方式和后续管理。

## Format Noise

Check these after content review, especially when generating Word drafts:

- Do not add spaces between Chinese text and numbers unless the user's template already does so.
- Avoid comma grouping in numbers such as `1,000,000` in ordinary Chinese official prose; use the unit expression preferred by the document.
- Use full-width Chinese punctuation in Chinese prose. Keep half-width punctuation for URLs, code, model names, English abbreviations, and formulas.
- Preserve first-line indentation and source Word styles when editing DOCX.
- Do not overuse tables. Use tables only for data comparison, schedules, budgets, or itemized responsibilities.
- Avoid frequent `1. 2. 3.` numbering in prose; prefer Chinese 条款 style or natural paragraphs when the source document uses that style.
- Do not use Emoji or decorative symbols in official prose.
