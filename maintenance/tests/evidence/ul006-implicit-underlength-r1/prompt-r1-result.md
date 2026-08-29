# `UL-006-R1` 动态短稿写后提示结果

## 结论

本轮是写后提示原型，不是 Hook 生命周期通过证明。五家低成本 provider 共返回20份可读取终稿，命令级失败0；18份比 D0 正文更长，20份均长于可分离事实材料。旧100/120观察值只有14份达到，但不再参与胜负。

提示语义对情况说明、事故通报和办理通知取得跨 provider 的安全实质增量；会议纪要只有一家取得安全实质增量，不进入该文种实现。普通起草和 Hook 后续均不得把100字设成统一通过线。

## 逐题裁决

| 题目 | D0 | D1 范围 | 安全实质增量 | 裁决 |
| --- | ---: | ---: | ---: | --- |
| U1 未决情况说明 | 102 | 124—162 | 3/5 | Alibaba 1/2、OpenCode 完整保留三组状态并通过标题、归组和承接形成正文；Ollama 把“安全演练＋设备采购”缩成“安全采购”，MiniMax 标题只覆盖联调，不计目标成功 |
| U2 事故通报 | 98 | 105—138 | 5/5 | 五家均保留事件、人员、已给影响、处置和原因待查状态；“现场医疗处理”是对已给“现场处理”的自然表达，“安全区域”和现场安全提醒按已给坠塌、人员撤离和道路通行关系下的一层合理处置表达接受，均未新增原因、数字或既成成效 |
| U3 办理通知 | 74 | 96—100 | 5/5 | 五家均只增加由报送动作直接支持的低强度目的和“特此通知”，无新增执行链；四家未到旧100观察值仍属于有效改进 |
| U4 未决会议纪要 | 118 | 118—211 | 1/5 | OpenCode 增加状态分类承接且保留全部强度；Alibaba 1/2 没有增长，Ollama 重复全部事实凑出汇总段，MiniMax 用“会议议定事项”框住未决建议，不计成功 |

## 事故文种边界

“本题不判断事故原因”只来自 U2 的原因仍在调查状态，不是事故通报通则。官方阶段通报会同时承载已核伤亡或影响、处置、初步判断及原因待查；调查结案稿会承载已查明原因、损失、责任和防范措施。本题必须保留2人撤离、1人擦伤并已处理、道路通行和原因待查，不得新增其他原因或影响。

核对来源：

- <https://yjj.taizhou.gov.cn/xwzx/yjdt/art/2026/art_82eebe41a1724f9b88a11bb457b7868c.html>
- <https://www.mem.gov.cn/xw/zhsgxx/202604/t20260408_599563.shtml>
- <https://yjt.hunan.gov.cn/yjt/xxgk/gzdt/ajyw/202205/t20220501_24113615.html>

## 技术边界

20份记录均带 `missing_exact_skill_trace`：本轮直接给出自包含的 Hook 修订提示，没有重新触发普通 Skill 路由。原始 D0 来自此前固定产品且已确认 Skill trace 的真实起草，但本结果只能证明提示语义，不证明 adapter、Stop、D0/D1选择、fact ledger 或 verifier 生命周期。后续实际 Hook 候选必须另跑真实 Stop 生命周期。

## 下一步

1. 普通 reference 重新按“安全实质增长”而非固定整数下限裁决；只改一段，先保护全部已给事实与状态。
2. Hook 动态触发只在能可靠分离事实材料、D0 接近材料转写且命中已验证文种时工作；显式压缩、上限、极短、精确回复、只审、纯格式和 Hook-off 旁路。
3. 事故提示按材料阶段处理原因与影响；采购提示只要求必要性/原因和采购事项，不强制作用、效果或结论。

## 实际命令

```powershell
python maintenance/tests/evidence/ul006-implicit-underlength-r1/run_eval.py --prepare
python maintenance/tests/evidence/ul006-implicit-underlength-r1/run_eval.py --provider alibaba2
python maintenance/tests/evidence/ul006-implicit-underlength-r1/run_eval.py --provider alibaba1
python maintenance/tests/evidence/ul006-implicit-underlength-r1/run_eval.py --provider ollama
python maintenance/tests/evidence/ul006-implicit-underlength-r1/run_eval.py --provider opencode
python maintenance/tests/evidence/ul006-implicit-underlength-r1/run_eval.py --provider minimax
python maintenance/tests/evidence/ul006-implicit-underlength-r1/run_eval.py --summarize
```

另逐份读取 `output/ul006-implicit-underlength-r1/raw/*/*.final.txt`，只把候选新增且与本提示相关的事实、状态、文种或交付回退计为失败。
