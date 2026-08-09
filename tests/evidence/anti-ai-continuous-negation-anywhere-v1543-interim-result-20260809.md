# 连续否定全位置减载原子首轮真实结果

日期：2026-08-09

Baseline：`03c13d2dea8924d3eb2e8c487956da45ce6b0692`

Candidate 产品：`fcc1d960a857fa418afa83714fbabdd0b5fed431`

## 结论

`ENGINEERING PASS / FIVE VALID PAIRS NON-INFERIOR / ONE PAIR ENV_INVALID / PROVISIONAL HOLD`。

Candidate 将“连续否定式收口”的句尾例子簇替换为位置无关的“连续否定”短规则，canonical reference 规范化减少175字符。首轮两家 DeepSeek 共12次调用均返回码0；其中 `ollama-r3-baseline` 只输出三项，未通过六标题完整性检查，对应整对剔除且未重试。剩余5个完整配对中，两名独立裁判一致确认：两臂 T1—T3 全部为0个材料外否定分句、0组连续否定；C1必要否定和C2禁令全部保留；Candidate 没有独有硬回退。

该结果证明减载后在五个有效配对中不劣，不能证明新增质量收益。固定引语和标点造成的匿名胜负不在本 DIFF 的直接管辖范围，按噪声保留。由于预注册未提前规定单臂无效后的处理，本轮按执行补充降为 `PROVISIONAL`，不合 main；另做跨模型留出后再裁决。

## 有效性与哈希

- Alibaba DeepSeek：3/3完整配对有效；Ollama DeepSeek：2/3完整配对有效。
- 失效配对：`ollama-r3`；Baseline final 缺 T3、C2、C3，Candidate 单臂同时作废。
- Baseline prompt SHA-256：`2bd380f1e5c9476451bc87b140cf3bce62189a210d85352c7236a75c48ff1d77`。
- Candidate prompt SHA-256：`fd0ea00b71ca4dc2c3105ae4e746ad22345346abb4618eb3c5a3bb928a585551`。
- catalog SHA-256：`2594067318d7ec5ebfcac833cc1494fe9da5d70fa053bd6b1b97acc30bc9b60e`。
- 有效配对匿名包 SHA-256：`85ecd87bad44cf467f1d01b35d54f5d67d17da49a2fdac793d4eae8f47c943b5`。
- mapping SHA-256：`b3adeadba96bdce3e7dd7edca50c83c6ad2c22aae24c4f3f1534ed41ba14f579`。
- Root 裁决 SHA-256：`f4f5df4e5f5feb2f5a6a2c212c91dffa3761708da255f1da611c9dd06f372f6e`。
- 独立裁决 SHA-256：`9c98063fb31d315d9f476872ac2a6cbe356d17cf55900cacef723fe89e241b35`。
- 最终首轮 manifest SHA-256：`528f09e0617eabe0f23169e132ed13af525597c3c9d6400af6e8a6058782c5b7`。

原始 prompt、12份 final、stdout、stderr、首次无效记录、manifest、匿名包、mapping 和两份解盲前裁决位于 `output/anti-ai-continuous-negation-anywhere-v1543-real/`。

## 双盲与解盲

两名裁判对 P1、P2、P3、P5 均判 B优；P4 分别判难分和A优。解盲如下：

| 配对 | Provider | A | B | Candidate 结果 |
| --- | --- | --- | --- | --- |
| P1 | Alibaba R1 | Baseline | Candidate | B优；C3多一个句号，仅格式 WARN。 |
| P2 | Alibaba R2 | Baseline | Candidate | B优；Baseline C3 串入 C2。 |
| P3 | Alibaba R3 | Baseline | Candidate | B优；Baseline 增加未给主体。 |
| P4 | Ollama R1 | Candidate | Baseline | Root难分、独立裁判A优。 |
| P5 | Ollama R2 | Baseline | Candidate | B优。 |

所有目标题均0对0，因此匿名质量偏好只支持不劣，不能宣称规则提高质量。P1—P3 的引语差异也没有跨 provider 形成 Candidate 机制，不计本原子收益。

## 工程验证

- 聚焦边界与镜像：4/4 PASS；
- 全量 unittest：458/458 PASS；
- Promptfoo stub smoke：20/20 PASS；
- 固定确定性消融：main 110/111，Candidate 111/111；唯一差项是 main 没有新“连续否定”锚点；
- Skill Creator quick validate：PASS；
- 六份 reference 镜像一致，`git diff --check` PASS。

本结果不合 main、不推送、不发布。
