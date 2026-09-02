# WR-025d 反馈词路由与同总数重组结果

日期：2026-09-02。

状态：`BASELINE_SUFFICIENT / CANDIDATE_NOT_STARTED / NO_PRODUCT_CHANGE`。

## 固定范围

- 基线产品：`f03081dbaf6dd946b1fb2c4d9edc7ca37e017327`。
- 五条低成本路线各运行4题，共20次真实写稿；19次形成带精确 Skill trace 的技术有效记录。MiniMax 的同总数重组题缺失精确 Skill trace，记技术无效，不补跑。
- 因基线没有达到“至少两家正向题漏读专叶”的预登记条件，未制作、未运行路由候选，不修改 `SKILL.md`、建议专叶、镜像、Hook、description 或版本。

## 路由结果

| 题目 | 技术有效 | 建议反馈专叶读取 | 结论 |
| --- | ---: | ---: | --- |
| 对外“反馈意见” | 5/5 | 4/5 | Alibaba2、Alibaba1、Ollama、OpenCode 均读专叶并形成合作性正式稿；MiniMax 只读主入口。单家漏读不满足候选门。 |
| 对外“意见反馈” | 5/5 | 5/5 | 五家均读专叶，稿件保持平台运营方与审核部门权限、尚未决定状态。 |
| 收到反馈意见/反馈办理结果控制 | 5/5 | 0/5 | 四家转读情况说明任务卡与信息选择页，MiniMax只读主入口；5/5没有改写为向平台提建议。 |

脚本把个别等义保留标为 `missing_any`：例如稿件以两条已答复事项和一条未决事项承载“2项/1项”，未逐字复述数字；人工核对事实和状态均在，不按自动标记判失败。

## 同总数重组结果

- 4份带精确 Skill trace 的有效稿中，Alibaba1、Ollama、OpenCode 3家实际读取建议反馈专叶；三稿均把底稿第1、2项合并为审核材料组合认定与勾稽问题，再把原第3项按审核部门、平台运营方权限拆成两项建议，最终合理保留3项。
- 该结果说明专叶“同类项不能只换标题后原样保留”的文字没有迫使有效读叶模型机械减少总数；冷审推测的同总数误伤未复现，不凭静态担忧修改规则。
- Alibaba2 未读专叶并只交付过程说明，属于单家路由/交付失败；MiniMax 缺精确 trace。两者不作为该句的可归因反例，也不通过重跑堆票。

## 稿件质量与剩余风险

- 两道对外正向题的有效稿总体能从实际办理事实切入，区分审核与平台权限，并用建议状态表达未决事项；篇幅均不短于题面。
- Ollama 在“反馈意见”稿补入系统当前日期，MiniMax 又补入当前日期和占位落款；这两项不在材料中，属于既有成文日期/占位边界的残余反例，不由本轮不存在的候选 diff 造成。后续如重开，应归 `WR-001` 的独立自然题，不在本原子顺手加禁令。
- Alibaba2、OpenCode 个别稿增加“后续组织、继续收集”等正文承诺；未形成五家共同问题，也与路由词是否显式列出无可归因关系，保留为无 Hook 直写观察。

## 实际命令

```powershell
python maintenance/tests/evidence/wr025d-feedback-route-r1/run_probe.py --prepare
python maintenance/tests/evidence/wr025d-feedback-route-r1/run_probe.py --provider alibaba2
python maintenance/tests/evidence/wr025d-feedback-route-r1/run_probe.py --provider alibaba1
python maintenance/tests/evidence/wr025d-feedback-route-r1/run_probe.py --provider ollama
python maintenance/tests/evidence/wr025d-feedback-route-r1/run_probe.py --provider opencode
python maintenance/tests/evidence/wr025d-feedback-route-r1/run_probe.py --provider minimax
python maintenance/tests/evidence/wr025d-feedback-route-r1/run_probe.py --summarize
```

原始终稿、trace、provider JSON 和汇总位于未跟踪的 `output/wr025d-feedback-route-r1/baseline/`；冻结题面、配置、runner 与本结果进入仓库。未运行候选命令，不把它写成通过。
