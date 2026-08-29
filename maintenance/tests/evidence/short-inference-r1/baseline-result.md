# `WR-013d/WR-018-R2` 当前基线结果

## 结论

`WAIT_NEW_COUNTEREXAMPLE`。固定 v1.6.20 主线共运行15份真实稿，14份具有精确 Skill 读取轨迹；Alibaba Token Plan 2 的活动新闻因未能读取 Skill 且输出过程说明，记为技术无效。当前有效样本没有复现跨 provider 的“事务稿因不敢作一层合理推断而功能性过薄”，因此不改普通写稿规则，也不设置统一字数下限。

## 篇幅与功能

| 题目 | 有效稿正文非空白字符 | 一层原因/目的 | 一层作用、归纳或预期 | 结论 |
| --- | ---: | ---: | ---: | --- |
| 扫描仪采购申请 | 260—467 | 5/5 | 5/5 | 均说明现有能力与集中排队的矛盾，并把增配设备写成缓解排队、提升扫描能力的预期，不把字数不足当作必须补具体程序的理由 |
| 投影设备维修申请 | 142—262 | 5/5 | 5/5 | 最短稿仍保留三次中断、时长、更换连接线、故障仍偶发、检测维修事项及三项未决状态，能成立为完整申请 |
| 培训活动新闻 | 167—230（4份有效稿） | 不适用 | 3/4明确写出“帮助熟悉流程/掌握要点”的一层活动作用；余下1份事实完整但附带正文外自评 | 没有两家共同因谨慎而删去新闻成立所需事项；不据此追加统一影响句 |

正文短于包含材料、允许项、禁止项和交付要求的完整提示词，不等于稿件过短。本轮三题的有效正文均长于事实材料；更重要的是，申请稿均具备“现状—原因—拟办事项—预期作用—未决状态—请示落点”，新闻稿具备“时间—主体—活动—人数—环节—完成/未完成状态—补测—意见汇总”。

## 允许的一层推断

有效稿稳定采用了以下关系，均属于材料事实、通常功能与事项关系直接支持的一层表达，不记为外扩：

- 由每日260份、单机和15至25分钟排队，归纳现有设备在集中时段处理能力不足；
- 由增配高速扫描仪，低强度预计缓解排队、提高扫描归档效率；
- 由连续三次中断且换线后仍偶发，说明有必要检测维修，并以保障后续培训正常开展为目的；
- 由流程讲解、现场操作和模拟申报，概括为帮助参训人员熟悉流程、掌握操作要点，但不把34人完成扩大为36人全体成效。

## 仍需保留的风险

- 三家有效新闻稿把完整日期缩成“8月28日”；这是已有完整年份风险，不是“合理推断过严”造成的目标回退，也不应靠统一扩写规则处理。
- Ollama 新闻稿附正文外自评，OpenCode 采购稿附过程引导语，仍属于 `CL-001-NOHK` 的包装风险。
- 个别申请稿补当前成文日期、泛化用途或“按程序办理/另行报告”等安排；这说明风险更接近材料外具体流程和承诺，而不是规则过于谨慎。
- 自动汇总中的部分“缺少数字”来自阿拉伯数字与中文数字、量词或同义表达差异；本结论按原稿逐份复核，不把该机械观察冒充质量失败。

## 收口

- `WR-013d/WR-018-R2` 转为 `WAIT_NEW_COUNTEREXAMPLE`：只有新题再次出现至少两家有效 provider 共同漏写文种必要的原因、作用或事项落点，才重开普通写稿规则。
- `UL-005-R10` 继续：现有篇幅不足 Hook 的扩写指令与核验口径确有文字冲突，应在固定 D0 上单独做同稿 A/B。
- `WR-009b` 继续：只验证“原因确实无法推断且允许正文外提示”的窄情形，不把提示扩成普遍追问。

## 实际命令与输出边界

```powershell
python maintenance/tests/evidence/short-inference-r1/run_eval.py --arm baseline --prepare
python maintenance/tests/evidence/short-inference-r1/run_eval.py --arm baseline --provider alibaba2
python maintenance/tests/evidence/short-inference-r1/run_eval.py --arm baseline --provider alibaba1
python maintenance/tests/evidence/short-inference-r1/run_eval.py --arm baseline --provider ollama
python maintenance/tests/evidence/short-inference-r1/run_eval.py --arm baseline --provider opencode
python maintenance/tests/evidence/short-inference-r1/run_eval.py --arm baseline --provider minimax
python maintenance/tests/evidence/short-inference-r1/run_eval.py --summarize
```

原始轨迹、末条消息与运行日志保存在忽略目录 `output/short-inference-r1/`，未提交模型输出或可能含本机路径的原始日志。
