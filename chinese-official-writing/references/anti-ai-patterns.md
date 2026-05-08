# Anti-AI Patterns

Use this reference before polishing, after user criticism about "AI味", or before final delivery of important official writing.

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
- 结论后置：先铺概念、背景、趋势，最后才写项目判断。
- 论据空转：有观点无数据，有数据不换算，有金额不说明对应需求。
- 技术堆叠：列一串模型、GPU、并发、SLA 名词，但不说明业务使用场景。
- 成本比较失衡：只比较单项 API 价格，不比较云资源、运维、安全、服务保障和扩容风险。
- 责任缺位：方案写了目标和任务，但没有实施主体、时间安排、验收方式和后续管理。
