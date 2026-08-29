# References 减载 R2 当前基线结果

## 结论

固定 `v1.6.20` 后 `main@6e4e8914431c5674a3fda87ab42d35ed8a531e8c` 共运行30次真实起草、改稿和可研任务，28次技术有效。`FINAL-BODY-LEAF-R1` 与 `WORKFLOW-REVISION-LEAF-R1` 都没有复现稳定大页读取，按预登记直接进入 `REJECTED_BASELINE_ROUTE_NOT_REPRODUCED`，不做产品原型。`AI-COMPUTE-BASIC-LEAF-R1` 在简单算力申请出现3/5 trace读取信号，其中2路完成有效终稿、OpenCode在已经读取专项页后因 provider 502 中断；完整算力可研为4/5读取专项页，因此只继续这个原子的窄叶 A/B。

本结果不把合理原因、即时作用、低强度预期、条件判断或必要论证判作事实外扩。自动 required/forbidden 只作为定位线索；“申请采购”对应“拟采购”、“待确定”对应“未定”等语义等价写法经人工复核后不计失败。

## 真实读取

| 原子与题目 | 技术有效 | 目标大页读取 | 裁决 |
| --- | ---: | ---: | --- |
| `FINAL-BODY-LEAF-R1` 稀疏采购申请 | 5/5 | `final-review-layers.md` 1/5 | 未达门 |
| `FINAL-BODY-LEAF-R1` 完整日期活动新闻 | 5/5 | 0/5 | 未达门 |
| `FINAL-BODY-LEAF-R1` 普通长报告 | 5/5 | 1/5 | 未达门 |
| `WORKFLOW-REVISION-LEAF-R1` 普通长报告 | 5/5 | `workflow.md` 0/5 | 未达门 |
| `WORKFLOW-REVISION-LEAF-R1` 多材料改稿 | 4/5 trace有效 | 1/4 | 未达门；MiniMax正文有效但只发生失败的 MCP 读取，不计路由证据 |
| `AI-COMPUTE-BASIC-LEAF-R1` 简单算力申请 | 4/5终稿有效 | `ai-compute-docs.md` 3/5 trace；有效终稿2路，OpenCode读取后502 | 达到继续做最小候选的信号，不直接记通过 |
| 完整算力可研控制 | 5/5 | `ai-compute-docs.md` 4/5 | 可作为完整页控制 |

## 稿件复核

### 短采购与活动新闻

- 五篇活动新闻均保留完整日期、48人、45人已提交、3人未提交、反馈未分类和单人原话范围；“提供阅读交流机会”等一层即时作用成立，不算外扩。
- 稀疏打印机采购五篇均形成申请正文，OpenCode、Alibaba 1 和 MiniMax 的主体关系与未决状态可用；Alibaba 1 的“现申请采购”与“拟采购”语义等价，MiniMax 的“待确定”与“未定”语义等价，自动缺词不计失败。
- Alibaba 2 在正文前输出“已读取技能规则”，并补“待确定后另行报告”；Ollama补“待确定后另行报批”。这是当前基线的正文包装或材料外后续承诺风险，但两项待研究拆分并未形成产品 diff，不能拿这些随机基线问题冒充拆分回退。

### 长报告与多材料改稿

- 五篇普通长报告均保留主要数字、局部试用、补测和扩大范围未决状态，非空白字符为1378—2023；合理的原因分析、有限效果判断和条件性建议保留，不因材料未逐字写出因果句判失败。
- 部分稿件仍有与事实链无关的替代原因枚举、反馈采集安排、正文内边界自证或“完整调用数据”等偏强表述；这些是当前长稿质量观察，不属于本轮尚未实现的拆叶 DIFF。
- 多材料改稿中4篇完整保留最新日期，Alibaba 1遗漏 `2026年7月22日18时`；五篇均没有回流36项、30项、6项或网络抖动旧判断。该题只有1路读取工作流，不能靠拆 `workflow.md` 修复日期遗漏。

### 算力申请与完整可研

- 简单算力申请的4篇有效稿中，Ollama总体保留事实但补“验证后再研究后续安排”；MiniMax在读取完整专项页后新增“外部资源”“不对现有架构作重大调整”“验收付款”和后续研究；Alibaba 1漏写全部未决字段；Alibaba 2未读专项页并新增“承担全市政务数据汇聚”等具体事实与后续比选程序。合理的排队原因、分流作用和低强度预期均保留为可接受关系。
- 上述分布说明窄叶只可能改善“已经主动读取完整专项页”的模型，不能修复只读入口却自行外扩的 provider，也不能把所有基线问题归因于 `ai-compute-docs.md`。
- 五篇完整可研均形成成本、响应、数据控制和运维比较；多篇做出材料可直接计算的24个月租赁总额758.4万元和差额556.8万元，这类简单算术不判外扩。MiniMax另有正文前过程说明及较多材料外办理建议；完整页候选控制必须确保不扩大这类风险。

## 技术失败

- OpenCode `AI-BASIC-PURCHASE`：已实际读取 `SKILL.md`、`ai-compute-docs.md`、申请叶和信息选择页，随后 provider `opencode.ai` 解析失败并连续返回502，无终稿；记技术失败，不记产品失败。
- MiniMax多材料改稿：通过不可用的 `skills` MCP 尝试读取本地 `SKILL.md` 后直接成稿，正文可复核，但没有成功的精确文件读取证据；只从路由统计剔除，不把正文判为失败。

## 命令与冻结输出

```powershell
python maintenance/tests/evidence/reference-slimming-r2/run_probe.py --prepare
python maintenance/tests/evidence/reference-slimming-r2/run_probe.py --provider alibaba2
python maintenance/tests/evidence/reference-slimming-r2/run_probe.py --provider alibaba1
python maintenance/tests/evidence/reference-slimming-r2/run_probe.py --provider ollama
python maintenance/tests/evidence/reference-slimming-r2/run_probe.py --provider opencode
python maintenance/tests/evidence/reference-slimming-r2/run_probe.py --provider minimax
python maintenance/tests/evidence/reference-slimming-r2/run_probe.py --summarize
```

冻结输出位于忽略目录 `output/reference-slimming-r2/baseline-probe/`：82文件 tree fingerprint 为 `09df261aa3bfaa7b3a57f1d3a0359fb625956a0090a4589aee888a228bb72640`，包含30份终稿、JSONL trace、stderr、provider记录和 `summary.json`。原始输出不进入产品包。
