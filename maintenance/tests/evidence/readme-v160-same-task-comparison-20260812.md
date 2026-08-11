# README v1.6.0 same-task comparison

## Scope

- This evidence refreshes only the README same-task display. It does not change package version fields, writing rules, references, Hook behavior, the fixed no-Skill baseline, or any release surface.
- The original prompt displayed in README is unchanged. Its UTF-8/LF/no-final-newline display-block SHA-256 is `f90fb8a6fd1538ae0f67683253786ae0949f7c65d906d30fc9bc234c1797684a`.
- The no-Skill output is reused byte-for-byte from the existing comparison. Its UTF-8/LF/no-final-newline SHA-256 is `25d6cd5eb9a6fc90a93e8ff3f1657ac45694d7b33b2a90f27d9f998c4500b31b`, with 926 non-whitespace characters.

## v1.6.0 Skill-arm binding

- Writer: `gpt-5.6-sol`, reasoning effort `ultra`, zero retry.
- Fixed published Skill commit: `0f6ec603993d5595e784fa7079837e299d1b0da3` (`v1.6.0`).
- The isolated writer successfully read the fixed canonical `SKILL.md` and these routed references: `information-selection.md`, `task-route-cards.md`, `genre-checklist-report.md`, `argument-chains.md`, `final-review-layers.md`, and `proofreading-checklist.md`.
- The writer received the same original prompt as the no-Skill arm. No Hook result was injected into the writing output.
- Skill output UTF-8/LF/no-final-newline SHA-256: `8b2b54e6ae29af7f5166df6bf10e688c08b959c48f3a6c6dd61aed7e2e2dd8a7`.
- Skill output length: 761 non-whitespace characters.

## Anonymous mapping

- Terra packet: `A` was the v1.6.0 Skill arm; `B` was the fixed existing no-Skill baseline.
- SOL R2 packet: `A` was the fixed existing no-Skill baseline; `B` was the v1.6.0 Skill arm.
- Neither mapping was disclosed to its judge before the verdict.

## Valid independent verdict: Terra max

The judge received the complete original task and both anonymous outputs. Raw verdict:

```json
{"A":{"fact_state":"PASS","length":"PASS","genre":"PASS","direct_use_cost":1,"issues":[]},"B":{"fact_state":"FAIL","length":"WARN","genre":"FAIL","direct_use_cost":5,"issues":["缺少要求的正式标题。","新增“未出现超期情况”，原材料未提供办理时限或超期状态依据。","新增“有效分流工作日办事压力”等未经材料证明的成效判断。","将“加强对老年群众的现场帮办”、持续优化、密切关注、阶段评估分析内容等写成既成措施或后续行动承诺，超出材料明确范围。"]},"winner":"A","reason":"A标题、数据、时间、主体和既定安排均与材料一致，篇幅接近800字，报告结构完整，可直接采用；B缺题名且多处新增材料外状态、成效和行动承诺，需较大幅度删改。"}
```

## Valid independent verdict: SOL R2

R2 received the complete original task. Raw verdict:

```json
{"A":{"fact_state":"FAIL","length":"PASS","genre":"FAIL","direct_use_cost":4,"issues":["缺少指定标题《明川市政务服务中心周六延时服务试运行情况报告》","新增“未出现超期情况”“有效分流了工作日办事压力”等材料未明确给出的结论","将“加强对老年群众的现场帮办”写成已经实施的措施，原材料仅明确制作大字版操作指引","新增汇总事项类别、持续优化帮办服务、密切关注重点需求、及时完善现场组织等行动承诺","擅自扩展8月底评估的具体分析维度"]},"B":{"fact_state":"PASS","length":"PASS","genre":"PASS","direct_use_cost":1,"issues":[]},"winner":"B","reason":"B标题完整，数字、时间、主体、办理状态、调整措施和后续安排均与材料一致，推导比例计算准确，篇幅和报告结构适当，可直接采用。A虽主体结构完整，但漏写指定标题，并新增多项材料外结论、已实施措施和后续行动承诺，触及硬边界，需较大修改。"}
```

## Invalid judge attempt

The first SOL judge packet omitted three source phrases: `现场发放并收回`, `自助填报`, and `停车区域`. Its warnings therefore did not test the fixed original task. That attempt is `INVALID`, is not counted, and is not used in README.

## Current conclusion

Both valid blind verdicts prefer the v1.6.0 Skill output. This single comparison is suitable as a reproducible README example, not as a universal model or genre claim.
