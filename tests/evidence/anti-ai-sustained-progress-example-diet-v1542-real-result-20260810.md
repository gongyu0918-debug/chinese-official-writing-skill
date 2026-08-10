# ANTI-AI “持续推进”重复例子微减载真实结果

日期：2026-08-10

结论：`REAL NON-INFERIOR MICRO-RELIEF / ELIGIBLE FOR MERGE REVIEW`

## 候选与有效性

- Baseline：`9968038b0bc68c942eac78cffe7b4968d674f801`
- Candidate：`75eb98fa5147a2fff2bc806b12e6955daf42154c`
- 产品仅删除空泛套话列表的 ``持续推进`` 一行；适用资格、处理句、其他八例和同叶三处承载保持。
- 完整 Skill prompt 从26,171降至26,162字符，净减9字符。
- Alibaba、Ollama DeepSeek V4 Flash 0731 均为 `max`，各4对ABBA，共8对、16调用；零重试。
- 16/16 final、8/8配对有效；标题、SHA和stdout一致性通过。
- 匿名包 SHA-256：`e65c252020b71b3b3c97daea8a42021ab6b95ebf2306711322810a0fd9bc9ce3`，45,683字节。
- mapping SHA-256：`cb25d89e0f13dfccf178026284d24497a3382ca49c5d5e339828c32cf40f0cd2`。
- harness 未执行 `prose_lint`，结果只评价 Prompt 叶本身。

独立轨迹审计确认：16/16返回码为0、`max`、零重试；两个实际捕获 context 只差删除该行；detached roots clean；final SHA、标题和 prompt SHA 全部匹配。

## 解盲

| 配对 | Provider | A | B | 换算裁决 |
| --- | --- | --- | --- | --- |
| P1 | Alibaba | Baseline | Candidate | Baseline优 |
| P2 | Alibaba | Baseline | Candidate | Candidate优 |
| P3 | Alibaba | Baseline | Candidate | Baseline优 |
| P4 | Alibaba | Candidate | Baseline | Candidate优 |
| P5 | Ollama | Candidate | Baseline | 难分 |
| P6 | Ollama | Baseline | Candidate | Candidate优 |
| P7 | Ollama | Candidate | Baseline | Baseline优 |
| P8 | Ollama | Baseline | Candidate | Candidate优 |

总计 Candidate 4胜、Baseline 3胜、难分1。Alibaba 2:2；Ollama Candidate 2胜、Baseline 1胜、1难分。名义胜负不是本轮收益依据，只用于确认没有稳定反向质量信号。

## DIFF 归因

1. R1两臂16/16都能删除无支撑的 `持续推进` 和 `提供有力支撑`，说明同叶通用机制足以承接该例子的主要召回职责。
2. C1两臂16/16保留材料内有主体、事项、期限、反馈和汇总机制的 `持续推进`，没有把持续性语义缩成普通“推进”。
3. 上一轮整节删除暴露的两类风险没有在本候选形成 Candidate独有硬回退：R2待确认状态保持，R3建设功能没有 Candidate确认性失守。
4. 唯一硬FAIL在P8-A，而A为Baseline；Candidate没有独有FAIL，不需要启动定向复放。
5. 两臂仍有建设功能和空泛表达WARN，但随配对交叉出现，未形成与9字符DIFF对应的稳定方向。
6. 两家 provider 均满足至少3个有效配对，任何一家都没有 Candidate净负2对，也没有控制项确认回退。

因此本候选满足预注册的 `REAL NON-INFERIOR MICRO-RELIEF`：只证明删除重复例子不劣并节省9字符，不宣称写作质量提升。

候选具备合入评估资格，但本分支不自行合入 `main`、推送或发布。原始匿名裁决见 `tests/evidence/anti-ai-sustained-progress-example-diet-v1542-blind-judge-20260810.md`。
