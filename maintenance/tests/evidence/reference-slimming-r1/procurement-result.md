# PROCUREMENT-ANNOUNCEMENT-LEAF-R1/R2 真实 A/B 结果

日期：2026-08-29。终态：`REJECTED_INSUFFICIENT_ATTRIBUTABLE_LOAD_BENEFIT_AFTER_MINIMAL_REPAIR`。

## 结论

只拆采购公告叶的写稿质量总体安全，但没有形成跨provider稳定减载，最小R2修复后仍低于预登记门，因此不进入产品。R1五条低成本路线完成4题双臂40份真实正文，40份技术有效；目标路由2/5通过，字段式审查材料有1条Candidate误读公告叶。R2只收紧显式文种路由并把通用页补读改为条件式，再以原始公开产品为Baseline重跑公告与审查控制，共20份真实输出；19份技术有效，MiniMax公告Candidate无终稿且无精确Skill读取证据，按预登记记`INVALID`、零重试。

R2消除了公告叶控制污染，5/5有效字段审查Candidate均未读公告叶；但目标仍仅2/5通过。Alibaba Token Plan 2与Ollama各少读4166字节；Alibaba Token Plan的Baseline本来只读入口，OpenCode Candidate没有进入新叶，MiniMax Candidate技术无效。R2没有达到至少3/5可归因减载对，继续堆入口提示将偏离“减载”目标。

## 真实稿复核

- R1十份公告和R2九份技术有效公告均实际生成，采购主体、项目、31.5万元预算、LTO-9磁带600盘、条码标签600套、资格、2026年9月25日9时30分、提交地点、宋宁及电话总体保持；没有Candidate独有的采购方式、资格年限、项目数量、评审办法、合同、付款、验收结论或发布日期。
- R2四份技术有效Candidate公告均为可直接使用正文。Ollama两臂都有“公开采购”，属于Baseline既有表述，不作为R2回退；Alibaba Token Plan 2 Candidate的“根据采购工作安排”是孤立衔接语，没有形成材料外程序或承诺，也未跨provider复现。
- R2十份字段审查输出均保持五个字段及“已补充、依据尚未提供、结论未提供”状态。自动检查把`《设计说明》第2版`、`设计说明书（第2版）`等词形计为缺失；逐稿核对确认版本关系仍在。MiniMax Candidate另把“用户提供”改为“用户提交”，但该臂只读入口、未读公告叶，且本原子只改文种路由，不作为公告拆叶的可归因失败。
- R1的申请、审查材料和通知控制未见公告文种写法的跨provider质量污染；R2进一步确认控制路由可以修复，但单独修好控制串扰不足以证明拆页值得保留。

## 终态

- R1 Candidate：`0acda8e7f30e38a3acfbc25e9daf66c035eb44e7`；目标路由2/5，控制污染1。
- R2 Candidate：`20979c77e019e071846bf6adb3b338f915d47b49`；目标路由2/5，控制污染0，技术无效1臂。
- 最小修复已经完成并真实重测，不留`HOLD`；终止沿同一入口提示继续堆字。若未来真实宿主普遍读取综合采购小节，再以新反例重新立项。
- 产品恢复原始固定Baseline；不新增采购公告叶，不同步镜像，不改Hook、包体、description、版本或发布坐标，不合入main。

## 命令与证据

```powershell
py -3 maintenance/tests/evidence/reference-slimming-r1/run_eval.py --experiment procurement --prepare 03a72fb5 0acda8e7f30e38a3acfbc25e9daf66c035eb44e7
py -3 maintenance/tests/evidence/reference-slimming-r1/run_eval.py --experiment procurement --provider <alibaba2|alibaba1|ollama|opencode|minimax>
py -3 maintenance/tests/evidence/reference-slimming-r1/run_eval.py --experiment procurement --summarize
py -3 maintenance/tests/evidence/reference-slimming-r1/run_eval.py --experiment procurement-r2 --prepare 03a72fb5 20979c77e019e071846bf6adb3b338f915d47b49
py -3 maintenance/tests/evidence/reference-slimming-r1/run_eval.py --experiment procurement-r2 --provider <alibaba2|alibaba1|ollama|opencode|minimax>
py -3 maintenance/tests/evidence/reference-slimming-r1/run_eval.py --experiment procurement-r2 --summarize
```

- R1 `fixture.json` SHA-256：`C2F1F3280422D5B319291DE20ADCA87E1AEDA8726241E6115C7AA9C23E82345F`
- R1 `summary.json` SHA-256：`BF3F0CA275385C12EC0EEE949973966C6BF6087C4467566D9CFC05E5DBF032E9`
- R2 `fixture.json` SHA-256：`5CF5E2E4D7DFD0CDCF35EBE4136C9E4E5772C263BBAA768F6649872DC4C5E068`
- R2 `summary.json` SHA-256：`40CF454AEDBA62910D72A48D0C4919C555EAF2BF8BCD65A08D6DD87DE0C2A129`
- 原始final、trace和stderr位于对应忽略目录；提交证据只保留预登记、runner和终态摘要。
