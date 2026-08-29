# `SHORT-NATURAL-REFERENCE-R1` 普通 reference 终态

## 结论

普通 reference 原子为 `TERMINATED_TARGET_NOT_IMPROVED / PRODUCT_RESTORED`。当前分支提交 `c8ca980b` 已把 canonical 产品恢复为 `main@c60e3ffaa12af012bf2a3910081ae70244a87a21` 字节；本轮没有可合并的 Skill/reference 产品变化。

这个结论不是因为门槛过严：已给事实和常识直接支持的一层原因、必要性、直接作用、阶段归纳、低强度预期和条件判断均按可接受内容处理。阻断项只包括候选独有的已给状态遗漏、新具体程序/动作/部件/责任/承诺/事件、把预期写成既成效果、用户范围破坏或非正文交付。

## 四臂真实结果

| 臂 | 产品范围 | 真实输出 | 目标结果 | 终态 |
| --- | --- | ---: | --- | --- |
| baseline | `main@c60e3ffa` | 50 | 采购/维修15稿均超过100；活动新闻最低150；说明、事故、通知、纪要存在真实 D0 | 固定比较基线 |
| R1 | SKILL + 信息选择六文种枚举 + 说明/通知/事故卡 | 50 | 事故与通知变长；事故的后续通报收束已重判为正常，整体仍因通知前置动作、培训流程、采购程序和维修部件等候选独有回退被拒绝 | `REJECTED` |
| R2 | 删除六文种枚举，保留三张轻量卡 | 50 | 说明仍3/5低于120，通知2/5低于100，纪要2/5低于120；三家漏“本次材料未附” | `REJECTED` |
| R3 | 只改信息选择页一个篇幅段 | 50 | 说明3/5低于120，通知3/5低于100，事故2/5低于100；未形成至少两家目标改善 | `TERMINATED` |

三轮显式不超过80字控制共15份均为43—56个非空白字符，保留给定时间、渠道和值班字段；没有被普通篇幅目标反向扩写。100—120字压缩控制的技术有效稿均在范围内，技术失效不计胜负。

## 文种裁决保持

- 采购/维修稿的扩写功能只看材料能够支持的原因或必要性和事项；效果句、条件性结论与请批尾语不作为篇幅达标项。请批尾语另按用户指定文种和行文关系判断。
- 事故通报按材料所处阶段承载事件、人员状态、已给影响、现场处置和调查/排查状态；原因未查明时不擅自判定原因或责任，但不禁止已给事实和常识直接支持的影响、处置表达及无具体新安排的续报收束。
- 通知看对象、动作、时间、内容和渠道；活动新闻允许活动动作直接支持的一层即时作用；说明看阶段与未决状态；纪要看决定、建议和未决强度。
- 新数字、用途、程序、责任、期限、承诺、新事件和既成成效仍是硬事实边界；“稿件变长”本身既不是胜也不是败。

## 后续

这是 R1—R3 当时的普通 reference 终态，已被后续 `UL-006-R1` 真实写后原型和 `SHORT-NATURAL-REFERENCE-R4/R5` 重开，不再用100/120等整数作统一通过线。当前后续只在能可靠分离事实材料、D0接近换词转写且文种功能不足时动态触发；显式字数上限、压缩、极短、逐字/精确回复、只审、纯格式和 Hook-off 必须旁路。

## 实际命令

```powershell
python maintenance/tests/evidence/short-natural-reference-r1/run_eval.py --arm candidate_r3 --prepare
python maintenance/tests/evidence/short-natural-reference-r1/run_eval.py --arm candidate_r3 --provider alibaba2
python maintenance/tests/evidence/short-natural-reference-r1/run_eval.py --arm candidate_r3 --provider alibaba1
python maintenance/tests/evidence/short-natural-reference-r1/run_eval.py --arm candidate_r3 --provider ollama
python maintenance/tests/evidence/short-natural-reference-r1/run_eval.py --arm candidate_r3 --provider opencode
python maintenance/tests/evidence/short-natural-reference-r1/run_eval.py --arm candidate_r3 --provider minimax
python maintenance/tests/evidence/short-natural-reference-r1/run_eval.py --summarize
git diff --stat c60e3ffaa12af012bf2a3910081ae70244a87a21..c8ca980b -- chinese-official-writing
```

另逐份读取 `output/short-natural-reference-r1/raw/*/*-candidate_r3.final.txt`，并复核 R1/R2 已记录的候选独有差异。原始输出和 trace 只保留在忽略目录，不进入发行包。
