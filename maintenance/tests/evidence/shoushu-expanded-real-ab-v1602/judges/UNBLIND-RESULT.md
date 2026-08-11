# J1 收束自然化 R2 解盲结果

## 证据资格

- Kimi：`CLEAN`，唯一正式裁判。
- Qwen、Grok：读取了 `MEMORY.md`，均为 `CONTAMINATED`，只作旁证，不计票。
- SOL：无文件读取调用，输入也未包含 17 对全文，完整盲包是否实际可见不可证，记 `INPUT_UNPROVEN`，不计票。
- 四份 final 与访问 trace 已在 commit `f130105afb50a181058b4f22913155000f9322a0` 冻结后才读取 mapping。

表中 `C` 为 Candidate，`B` 为 Baseline，`T` 为难分；星号和匕首列不进入正式结论。

| Blind | Pair | Task/provider | Map | Kimi | Qwen* | Grok* | SOL† |
|---|---|---|---|---:|---:|---:|---:|
| B001 | P013 | L1/alibaba | A=Candidate, B=Baseline | C | B | C | C |
| B002 | P014 | L1/alibaba | A=Baseline, B=Candidate | C | C | C | C |
| B003 | P015 | L1/ollama | A=Candidate, B=Baseline | B | B | B | B |
| B004 | P016 | L1/ollama | A=Baseline, B=Candidate | B | B | B | B |
| B005 | P018 | L1/minimax | A=Candidate, B=Baseline | C | C | T | B |
| B006 | P019 | L2/alibaba | A=Baseline, B=Candidate | B | B | B | B |
| B007 | P020 | L2/alibaba | A=Candidate, B=Baseline | B | C | B | B |
| B008 | P021 | L2/ollama | A=Candidate, B=Baseline | B | B | B | B |
| B009 | P022 | L2/ollama | A=Baseline, B=Candidate | C | C | C | C |
| B010 | P023 | L2/minimax | A=Candidate, B=Baseline | B | B | B | B |
| B011 | P024 | L2/minimax | A=Baseline, B=Candidate | B | B | T | C |
| B012 | P025 | C1/alibaba | A=Candidate, B=Baseline | C | C | C | C |
| B013 | P026 | C1/alibaba | A=Baseline, B=Candidate | C | B | B | B |
| B014 | P027 | C1/ollama | A=Baseline, B=Candidate | B | B | B | B |
| B015 | P028 | C1/ollama | A=Baseline, B=Candidate | C | C | C | C |
| B016 | P029 | C1/minimax | A=Baseline, B=Candidate | T | C | C | C |
| B017 | P030 | C1/minimax | A=Candidate, B=Baseline | C | C | C | T |

正式票解盲后为 Candidate 8 胜、Baseline 8 胜、难分 1。Kimi 的等级分布为：Candidate `PASS 1 / WARN 10 / FAIL 6`，Baseline `PASS 5 / WARN 5 / FAIL 7`。Candidate 没有形成整体质量胜势；它的重失败少 1 例，但高质量直接可用稿也少。

## 机械硬边界复核

manifest 记录 3 个 Candidate-only 硬失败：

1. `P013 / B001`：机械门要求逐字出现“已登记复核”，Candidate 未逐字命中；Kimi 通读后认为登记和复核状态已保留。该项是精确字符串与语义等价表达的冲突，不认定为事实丢失。
2. `P024 / B011`：Candidate 在否定式缺口说明中出现“满意度、财政投入、人员补贴、政策依据”等词，机械门按裸词判禁补；Kimi 没有认定这些信息被写成事实。该项是词表对否定语境的假阳性。
3. `P027 / B014`：Candidate 389 字，Baseline 622 字；机械门判 Candidate `length_under`，Kimi 同样判 Candidate FAIL、Baseline PASS。这是唯一得到机械门和干净裁判共同支持的 Candidate 独有硬回退。

`P027` 只有一例，未达到预注册“同一 Candidate 独有硬机制至少 2 对”的停止条件。未发现可复现的 Candidate 独有硬回退。

## 共性波动与长度信号

两侧共同存在的主要风险是材料外流程/结果补写、把未决状态写成确定结论、擅加下一步或责任分工、口号式结尾和篇幅失控。这些问题跨 A/B 出现，不能归因给本原子。

按题面正式字数区间复算 17 个技术有效 pair：

- Candidate 9/17 超出区间，Baseline 7/17；Candidate 平均比同对 Baseline 短 46.6 字，17 对中 12 对更短。
- 该差异高度依赖 provider：Alibaba 平均差 `-0.3` 字，MiniMax `+66.8` 字，Ollama `-187.5` 字且 6/6 Candidate 更短。
- 同一 Ollama/C1 路线上，`P027` 的 Candidate 过短并落败；`P028` 的 Candidate 又因避免 Baseline 超长而获胜。方向不稳定。

因此“Candidate 更短”值得下一轮观察，但当前更像 provider/采样波动与轻度提示效应叠加，不能认定为跨 provider 的稳定回归。

## 与 `734a34f0` 的直接关系

Candidate 只改 4 个运行时文件中的 6 行措辞：把“每段收束”“口号式收束”“以……收束”“自然收束”“收束到责任或目标”等维护性术语改为“每段结尾”“口号式结尾”“以……作结”“自然结束”“结尾落在责任或目标上”。事实边界、流程、字数范围和文种结构均未改。

- 34 篇有效正文中，两侧均未出现字面“收束”；没有观察到旧术语或新规则话语稳定泄漏进正文。
- 正式裁判 8:8:1，未证明质量提升，也未证明整体质量回退。
- 唯一真实 Candidate 独有硬回退是 `P027` 的篇幅不足；没有跨题目、跨 provider 复现。
- Candidate 的短稿倾向主要集中在 Ollama，未在 Alibaba、MiniMax 同向复现。

## 合入结论

`734a34f0` **可以合入**，但只能按“术语自然化、运行时规则等价改写”记账，不能宣传为写稿质量提升。理由是改动小、语义等价、正式盲审不分胜负，且没有达到预注册停止线的重复 Candidate 独有硬回退。

剩余风险登记：`P027` 单例篇幅回退、Ollama Candidate 偏短现象、机械词表对否定语境的假阳性。下一轮如继续研究，应针对这些机制单独预注册，不能把本轮中性结果写成收益。
