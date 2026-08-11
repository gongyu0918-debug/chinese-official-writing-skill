# 请示与报告复核叶精确去重结果

日期：2026-08-09

固定基线：`main=954cf5ec3ee418e3a2412496aa5fa269075b50d8`

预注册：`5c5416a3`

D1：`22d50d75`

D2：`d554c81b`

## 结论

- D1 申请顺序复述：`MIXED / KEEP ISOLATED`。工程通过，固定读取复放没有稳定漏召，但匿名盲审由 Baseline 小胜，未形成净收益，不进入 `main`。
- D2 报告审批边界复述：`PASS / ELIGIBLE FOR CLEAN INTEGRATION`。最终实现只删除“使用事实性汇报语言，不在报告中请求上级批准”中的重复后半句，保留“使用事实性汇报语言”；两道固定读取真实复核均无回退，Candidate 分别小胜和更克制。

## 工程结果

D2 初稿曾删除整行，导致既有“使用事实性汇报语言”原子叶断言失败，首轮全量为 456/457。该实现不成立；修复为只删重复后半句后重新验证：

| 检查 | 结果 |
| --- | --- |
| 聚焦与镜像测试 | 5/5 通过 |
| 全量 unittest | 457/457 通过 |
| stub smoke | 20/20 通过，0 error |
| 固定 `main` 与 Candidate 确定性消融 | 111/111，111/111 |
| Skill quick validate | 通过 |
| `git diff --check` | 通过 |

初次 456/457 不记为通过。

## D1 真实复放

首组申请复核中，两臂都实际读取 `genre-checklist-request.md`，但 Baseline 额外读取 `handling-elements.md`，不计严格胜负。Candidate 抓到请批语位于落款之后，Baseline 漏召。

固定 manifest 后，第一组 Candidate 错把“落款后、日期前”判断为符合“落款和日期之前”，Baseline 没有作出该错误判断；第二组同题复放中两臂均正确召回顺序问题。Candidate 的客观误判没有复现，按采样波动处理，但匿名盲审对有效第二组判两稿均 WARN、Baseline 小胜，主要因为 Candidate 把承诺事项表述得更像通用必备项。

D1 没有形成稳定硬回退，也没有形成质量收益。按预注册只保留研究，不因“少一行”直接合入。

## D2 真实复放

两组均固定只读各自 `SKILL.md`、`review-checklist.md` 和 `genre-checklist-report.md`。

1. 报告夹带“请批准采购6台设备”：两臂均正确判报告不得写审批请求、采购数量缺依据并保留原因未决状态。匿名 SOL 盲审判两稿 PASS，Candidate 小胜；Candidate 对已有正文结构的评价更准确，少一条不必要的分段重排建议。
2. 正常接口异常情况报告：Candidate 直接判“未发现需修改项”；Baseline 追加主送、报告单位、日期和报告语建议，虽带条件限定但提高直接使用成本。Candidate 未误报报告为请示，也未删改真实状态。

D2 的收益是同次加载叶内减少重复审批边界后，报告功能召回保持，正常短报告的过审倾向下降。没有改变起草叶、轻量卡、文种路由、信息选择或输出模式。

## 整合边界

只允许从固定 `main` 重建 D2 半句删除及其测试、结果证据。不得带入 D1、P0 检测、lint 前移、Hook、FSM 或其他 reference 清理。清洁整合分支需重新跑全量 unittest、stub smoke、固定消融、quick validate、镜像和差异检查后，才可快进 `main`。
