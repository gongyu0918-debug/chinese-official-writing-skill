# REVIEW-LAYER-SPLIT-R1 真实 A/B 结果

日期：2026-08-28。终态：`REJECTED_ROUTE_NOT_REPRODUCED_AND_BODY_PACKAGING_REGRESSION`。

## 结论

把`review-checklist.md`机械拆为共用、段落、小节和全文四层，没有证明局部审稿的真实减载。五条低成本路线完成4题双臂40份真实改稿或审稿输出，40份技术有效；10个单句/小节目标配对为0/10通过。Baseline在这些局部任务中读取旧`review-checklist.md`为0/10，Candidate也没有稳定进入新局部层，因此候选主要增加了入口路由文字，未削减真实已发生的读取。

全文能力控制同样未闭合：五条Candidate均未同时读取共用层、段落层、小节层和全文层，完整能力路由为0/5。纯格式题仅作输出形状控制；Alibaba Token Plan 2、Ollama和OpenCode满足格式页/通用复核页形状，Alibaba Token Plan与MiniMax只停在入口，不能证明分层后仍保留完整格式复核路径。

## 真实稿复核

- 单句改写Candidate五家均给出同一条35字符直接可用正文，17项、3项和“正在核验”均保持；拆层没有带来质量收益，也没有单句事实回退。
- 全文情况报告Candidate总体保持异常时间、恢复时间、影响范围和原因未决状态，未形成可归因硬回退。
- 局部小节改写中，OpenCode Candidate在正文前增加“已使用 chinese-official-writing 技能完成……”过程旁白，MiniMax Candidate增加“已调用中文公文写作 Skill……”过程旁白；Baseline没有。两臂均为直接交付任务，且这两条Candidate只读取改过的`SKILL.md`，属于本次入口分层路由可归因的交付形状回退。
- 格式核验两臂普遍较长；自动字符串把否定句中的“已生成Word”和编号“0分”计为告警，只作观察，不据此判失败。终态由真实路由不成立、全文能力未闭合和两家Candidate正文包装回退决定。

## 终态

- Candidate提交：`93399f7b0a35e64f81ee8525f128fd5c2cb23e39`。
- 局部目标路由：0/10通过；Baseline旧复核页实际读取0/10。
- 全文能力路由：0/5通过；格式形状控制3/5通过。
- 产品恢复固定Baseline，不同步镜像，不改Hook、包体、description、版本或发布坐标，不合入main。
- 不沿“物理拆成四层并扩大入口路由”这一机制继续R2。若以后出现局部复核确实读取大页的新反例，可另立只调整直达路由、不拆页的新原子。

## 命令与证据

```powershell
py -3 maintenance/tests/evidence/reference-slimming-r1/run_eval.py --experiment review --prepare 03a72fb5 93399f7b0a35e64f81ee8525f128fd5c2cb23e39
py -3 maintenance/tests/evidence/reference-slimming-r1/run_eval.py --experiment review --provider <alibaba2|alibaba1|ollama|opencode|minimax>
py -3 maintenance/tests/evidence/reference-slimming-r1/run_eval.py --experiment review --summarize
```

- `output/reference-slimming-r1/review/fixture.json` SHA-256：`05775EDF80C1DFEF242453101530F8C94475F7A0DD7A828958C49502E370A4E3`
- `output/reference-slimming-r1/review/summary.json` SHA-256：`0BC89C109DEE20A4C3D4BF79FA8B20DEC089274133FDD6682D136D6B643C6D78`
- 原始final、trace和stderr位于同一忽略目录；提交证据只保留预登记、runner和终态摘要。
