# 1.6.0 四原子组合真实回归结果

日期：2026-08-11

## 结论

`COMBINATION GATE FAIL / SPLIT REQUIRED / DO NOT RELEASE THIS COMBINATION`

入口交付范围自然化、通用叶报告块删除、Hook 未决转进行态预放行删除、五叶模板优先重复句删除四项同时存在时，没有满足预注册的发布门槛。后续 1.6.0 发布候选只保留入口自然化和报告块减载；Hook 与模板减载继续隔离，不随本组合发布。

## 冻结对象与有效性

- Baseline：`b91f25cc49cc8ca1379804a81a1d6e5a4eab987c`。
- Candidate 产品冻结：`23a89114`。
- Baseline 运行时 fingerprint：`17c3ce975c53890cc4e19882ad2bdf9bc3a45b345461cd94b92f39631b63c964`。
- Candidate 运行时 fingerprint：`f30b3c9759f4e6889936da8317efc1e12effe7fec580dc48c31392fa30129967`。
- 写手：Alibaba Token Plan `deepseek-v4-flash-0731`、Ollama Cloud `deepseek-v4-flash:0731`，均为 `max`。
- 最终矩阵 10/10 对技术有效；20 份首个 final，零模型重试。两条最初被执行策略拦截的 arm 仅按预注册补充技术执行，原失败记录保留。
- 匿名包：`output/release-1.6.0-combination-real-final/blind-packet.md`。
- 匿名包 SHA-256：`8f1f5bc381611d9129e035ac7b2c0ce1e791c6e42462ae723fd19074692ed0c6`，2966 字符。
- mapping SHA-256：`38c0e6805783892b4df43e78026520989590d2db704cc10ada871002dc0a819d`；解盲前保存在仓库外。
- SOL：`gpt-5.6-sol`，`max`；冻结盲审原文见 `tests/evidence/release-1.6.0-combination-real/sol-blind-review.md`，final SHA-256 为 `11ef881ebdf28011a2128c451eab7a897cd54356e3478b0cf56859491df13b92`。

R1 因多行 prompt 被错误作为单个 CLI 参数传入，20 次均没有收到完整题面，判 `ENV_INVALID`，不进入质量结论。R2 改为 UTF-8 stdin 后重跑；首次 PowerShell 管道调用 SOL 也在模型前报 `No prompt provided via stdin`，随后用 Python stdin 成功。所有失败均保留，没有伪装为有效样本。

## 解盲映射与裁决

| 盲位 | Provider / 任务 | A | B | SOL |
|---|---|---|---|---|
| P01 | Alibaba / W1 | Candidate | Baseline | A优，双方 FAIL |
| P02 | Ollama / W1 | Candidate | Baseline | A优，A PASS / B WARN |
| P03 | Alibaba / W2 | Baseline | Candidate | B优，双方 FAIL |
| P04 | Ollama / W2 | Candidate | Baseline | A优，双方 FAIL |
| P05 | Alibaba / W3 | Baseline | Candidate | B优，A FAIL / B WARN |
| P06 | Ollama / W3 | Baseline | Candidate | B优，A WARN / B PASS |
| P07 | Alibaba / H1 | Candidate | Baseline | A优，A PASS / B FAIL |
| P08 | Ollama / H1 | Baseline | Candidate | B优，双方 FAIL |
| P09 | Alibaba / H2 | Baseline | Candidate | 难分，双方 PASS |
| P10 | Ollama / H2 | Candidate | Baseline | 难分，双方 PASS |

解盲后 Candidate 相对胜 8 组、Baseline 胜 0 组、难分 2 组；匿名原始顺序统计为 A优 4、B优 4、难分 2。总体胜负仍不能覆盖 Candidate 在附件字段和未决状态上的硬失败，发布裁决以硬边界与 DIFF 归因为准。

## DIFF 归因

### 入口自然化与报告块减载

- W1 两家 Candidate 均胜；Alibaba 两臂都补了材料外会议要求，属于共性风险，Candidate 扩写较轻；Ollama Candidate 为 PASS，Baseline 因短通知过度分项为 WARN。
- W3 两家 Candidate 均胜；Alibaba Candidate 为 WARN，Ollama Candidate 为 PASS。未出现跨 provider 的 Candidate 独有栏目、数字或未决强度回退。
- 这两项保留为缩减组合候选，但本轮四原子结果不能替代缩减组合的独立复放。

### 模板优先重复句减载

W2 两家 Candidate 都在同一机制上违反用户既有格式：

- Alibaba Candidate 将“附件”字段置于反馈期限之后；
- Ollama Candidate 只在正文提及附件，没有独立附件字段。

两家 Baseline 的硬错都是日期缺少年份，没有附件字段回退。Candidate 2/2 的附件字段/顺序问题与被删除的模板、字段优先近场句直接相关，达到预注册的 DIFF 相关停止条件。该原子退出 1.6.0 发布候选，继续隔离。

### Hook 预放行删除

- Alibaba H1 Candidate 完整保留“尚未查明”，Baseline 错改为“正在核查中”，是明确正向信号。
- Ollama H1 Baseline 将状态改为“正在核查中”，Candidate 则完全删除“尚未查明”。两臂均 FAIL；Candidate 虽相对修改成本较低，仍直接违反“必须保持未决强度”的预注册硬边界。
- H2 两家两臂均准确保留材料明确的“正在核查”。

因此该原子不是被证明无效，而是本次组合中未跨两家 provider 闭合 H1 契约。它退出 1.6.0 发布候选，后续需单独修复或扩大验证；不能用总体胜票覆盖状态遗漏。

## 后续发布口径

1. 从固定 `main=b91f25cc` 新建干净发布候选。
2. 只合入入口自然化与通用叶报告块减载及其必要确定性锚。
3. 对 W1、W2、W3 重新运行两家 DeepSeek V4 Flash 0731 `max` 的真实复放；W2 用于确认移除模板原子后附件字段与顺序恢复。
4. 缩减组合通过真实回归及完整工程门后，才进入 v1.6.0 版本面与三平台发布。
