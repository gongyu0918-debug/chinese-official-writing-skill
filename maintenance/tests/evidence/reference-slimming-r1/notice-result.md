# NOTICE-LEAF-CURRENT-R1 真实 A/B 结果

日期：2026-08-28。终态：`REJECTED_ROUTE_BENEFIT_INSUFFICIENT_AND_CONTROL_REGRESSION`。

## 结论

把综合文种页的通知组小节搬到通知专叶，没有形成稳定真实减载，且产生了候选相关的正文与控制题回退。五条低成本路线完成5题双臂50份真实正文；48份技术有效，MiniMax内部通知Baseline未形成隔离Skill精确读取证据、Alibaba Token Plan 2讲话Candidate读取用户级同名Skill，均按预登记记`INVALID`。15个技术有效通知目标配对只有2个满足预登记路由门，且仅覆盖内部通知；多数Baseline本来不读综合`genre-playbooks.md`，新专叶反而增加读取。

静态拆叶没有自动等于真实省读。Alibaba Token Plan 2与Ollama的内部通知分别少读5089、7529字节，但其余目标多为Baseline未读综合页、Candidate未读新叶或Candidate加载不降。采购公告控制另有1个明确污染：Candidate错误读取通知叶。

## 真实稿复核

- Alibaba Token Plan 2内部通知Candidate读取新通知叶后，把对象由材料中的“窗口人员”扩大为“各部门、科室（窗口）”，补入材料外的规范、提升目的，增加星期，把培训日期写成文末成文日期，并在正文后附过程说明；Baseline未出现这些问题。
- 同一路线采购公告控制Candidate错误读取通知叶，补入“自服务提供之日起”的合同关系，并把运行日`2026年8月28日`写成材料明确未提供的发布日期；Baseline保持日期缺失。
- 公开通告中，Ollama与MiniMax Candidate均新增“请办事群众合理安排办理时间”等材料外建议，Baseline未新增。MiniMax该题只读改过路由的`SKILL.md`，仍属于候选信息架构带来的可归因回退。
- 其余通知、通报和讲话控制未形成可归因的跨provider硬回退。首版字符串检查中的“2人”等词形遗漏只作观察，不用于否定候选；本终态由真实稿污染、控制串扰和路由收益不足共同决定。

## 终态

- Candidate提交：`f82285bee62632309fb982853e0e7937b98060bf`。
- 目标路由：2/15通过，仅1类目标、2个provider；低于至少3对、至少2类目标的预登记门。
- 控制污染：1个有效配对；另有2臂技术无效。
- 产品恢复固定Baseline，不同步镜像，不改Hook、包体、description、版本或发布坐标，不合入main。

## 命令与证据

```powershell
py -3 maintenance/tests/evidence/reference-slimming-r1/run_eval.py --experiment notice --prepare 03a72fb5 f82285bee62632309fb982853e0e7937b98060bf
py -3 maintenance/tests/evidence/reference-slimming-r1/run_eval.py --experiment notice --provider <alibaba2|alibaba1|ollama|opencode|minimax>
py -3 maintenance/tests/evidence/reference-slimming-r1/run_eval.py --experiment notice --summarize
```

- `output/reference-slimming-r1/notice/fixture.json` SHA-256：`6DB015EADD00AD74A21EB5D109CF44435C4A621A6F76E58F8CFDAD242694C988`
- `output/reference-slimming-r1/notice/summary.json` SHA-256：`B573940AA36DD82CD6D3DBD322CE484468998DECBB3C8ECFFCD4201848565992`
- 原始final、trace和stderr位于同一忽略目录；提交证据只保留预登记、runner和终态摘要。
