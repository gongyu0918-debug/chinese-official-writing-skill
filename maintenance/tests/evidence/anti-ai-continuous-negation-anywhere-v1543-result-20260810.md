# 连续否定全位置减载原子最终结果

日期：2026-08-10

Baseline：`03c13d2dea8924d3eb2e8c487956da45ce6b0692`

Candidate 产品：`fcc1d960a857fa418afa83714fbabdd0b5fed431`

## 结论

`ENGINEERING PASS / REAL NON-INFERIOR RELIEF / MERGE-ELIGIBLE IN ISOLATION / NOT MERGED`。

Candidate 不再使用“连续否定式收口”，也不强制改成正向表达；它用位置无关的“连续否定”结构规则覆盖句中和相邻句，并保留必要否定。canonical `anti-ai-patterns.md` 规范化减少175字符。

经有效性修正后，首轮保留 Alibaba 与 Ollama DeepSeek 各2个完整配对；Luna 与 Qwen 留出各2个完整配对。合计8个有效配对、16份有效 final。两名裁判在全部配对中均确认：Baseline 和 Candidate 的 T1—T3 都是0个材料外否定分句、0组连续否定；C1必要否定、C2禁令和C3固定引语均由 Candidate 保留；没有 Candidate 独有硬回退。

因此本原子证明的是“删除句尾例子簇并减载175字符后，跨四种模型行为不劣”，不是新增质量改善。它具备独立并入资格，但尚未与“固定二段式”原子做组合 A/B，本分支不自行合 main、不推送、不发布。

## 有效性修正

首轮12次调用中有两个整对作废：

- `alibaba-r1-candidate` 六标题齐全但顺序为 T1、T2、C1、C2、C3、T3；首版 harness 漏检标题次序。第5提交 review 发现后，该整对作废；
- `ollama-r3-baseline` 缺 T3、C2、C3，对应整对作废。

没有重跑、补稿或覆盖旧文件。harness 随后改为同时要求标题各出现一次且位置严格递增；旧五对匿名包和中期结果标为 `SUPERSEDED`。最终首轮只使用重新随机化的4对有序有效包。

## 首轮修正后双盲

| 配对 | Provider | Candidate 身份 | Root | 独立裁判 | 目标计数 |
| --- | --- | --- | --- | --- | --- |
| P1 | Alibaba R2 | A | Candidate 胜 | Candidate 胜 | 0:0 |
| P2 | Alibaba R3 | A | Candidate 胜 | Candidate 胜 | 0:0 |
| P3 | Ollama R1 | B | Candidate 胜 | Candidate 胜 | 0:0 |
| P4 | Ollama R2 | B | Candidate 胜 | 难分 | 0:0 |

修正后匿名包 SHA-256：`b2f8744c48267863d519f66dcd1291e671a86ec3d7077e0ec83b2162f260664d`；mapping：`5ed81b9d89e2cb28b3eca569c6fed5459625c4d3f22abcf6c300422aa2a7fecd`；Root 裁决：`aa1396c448eae695f8c69065c2f6e1d14f581e6b42032d1c625a4412a2c4b13f`；独立裁决：`552a89aa084900e04b5f391fef303bfd5e4779ec07ccec2b02ae6045f0764e5b`；最终首轮 manifest：`ddb9f4964462859a47b24b0cc24e9c7d104a0ce295848dd816795c853363daef`。

## 跨模型留出双盲

留出8/8调用技术有效，使用修正后的标题顺序门槛。

| 配对 | 模型 | Candidate 身份 | Root | 独立裁判 | 目标计数 |
| --- | --- | --- | --- | --- | --- |
| P1 | Luna R1 | B | 难分 | 难分 | 0:0 |
| P2 | Luna R2 | B | 难分 | Candidate 胜 | 0:0 |
| P3 | Qwen R1 | B | Baseline 胜 | Baseline 胜 | 0:0 |
| P4 | Qwen R2 | A | Baseline 胜 | Baseline 胜 | 0:0 |

Qwen 两对 Baseline 的语言质量偏好来自 Candidate 增加通知式引导语、使用“投入试用”和一句不自然停顿；这些变化没有改变事实或目标计数，也不属于连续否定规则的直接管辖。按预注册保留为模型/provider 软负信号，不用 DeepSeek/Luna 的偏好抵销，也不把它升级为 DIFF 硬回退。

留出匿名包 SHA-256：`0f8e262a4d17f516d7398a93d6507ad4222bfee26df1eefa3007864baf6fa3f1`；mapping：`b2c61cee42a176fa7b226773eda397bbaea38b6a04846181ace45fd2e912309e`；Root 裁决：`331011bd5df5a862814486e60c126805d57dbe98549ffb88a260bfbacf0d43c3`；独立裁决：`b8ce613a1b7f51bc790e5680f0c3b04a8b907f069cad130cc7f3b170ef745196`；manifest：`d0c7e070940256d9b65eb30b5896e93ac90ac490fa3c02bc1fe894cb3cc0c150`。

## 工程验证

- 聚焦边界与镜像：4/4 PASS；
- 全量 unittest：458/458 PASS；
- Promptfoo stub smoke：20/20 PASS；
- 固定确定性消融：main 110/111，Candidate 111/111；唯一差项是 main 没有新“连续否定”锚点；
- Skill Creator quick validate：PASS；
- 六份产品 reference SHA 一致；`git diff --check` PASS；
- 第5提交轻量 review 的标题顺序阻断已修复并以新匿名包重裁。

原始证据分别位于：

- `output/anti-ai-continuous-negation-anywhere-v1543-real/`；
- `output/anti-ai-continuous-negation-anywhere-v1543-holdout-real/`。
