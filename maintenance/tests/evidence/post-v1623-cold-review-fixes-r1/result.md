# v1.6.23 后双模型冷审最小修复结果

## 结论

固定基线为本地 `main@4ec30a11c810e2455bf913862746b1a271215c8e`。Qwen 3.8 Max 与 Grok 4.6 均指出 `SKILL.md` 第26行的短稿语义判断与第96行参考资料表旧“前置直达”表述不一致；两者均未发现 P0/P1 或新增 Hook 缺陷。

本轮没有把冷审文字结论直接写进产品，而是连续拆成三次单句原型并运行27份低成本模型真实稿。三轮均未达到预登记的可归因收益门，所有产品原型已经恢复，最终相对固定基线的 `chinese-official-writing/` 产品差异为零。

终态：

- `CR-001-R1 = SUPERSEDED_BY_R2`
- `CR-001-R2 = REJECTED`
- `CR-001-R3 = TERMINATED_NO_REAL_GAIN`
- `CR-002 = BASELINE_RETAINED / WAIT_NEW_COUNTEREXAMPLE`
- 无活动 `HOLD`；未改 Hook、description、reference、镜像、版本或发行面。

## 真实写稿

三轮均使用 Codex CLI 隔离运行当前项目 Skill，思考强度 `max`：

- `alibaba-token-plan-2/deepseek-v4-flash-0731`
- `opencode-go/deepseek-v4-flash`
- `minimax-cn/MiniMax-M3`

三家全部有效，未启用备用的 Alibaba Token Plan 1 或 Ollama Cloud。总计27份终稿、技术失败0。

| 轮次 | 真实稿 | 目标读取与稿件结果 | 终态 |
| --- | ---: | --- | --- |
| R1 | 12 | 讲话短稿页读取基线1/3、候选1/3；未形成目标收益。Alibaba2候选把`2026年上半年`弱化为`今年上半年` | `SUPERSEDED_BY_R2` |
| R2 | 9 | 讲话候选读取2/3；报告基线/候选均为2/3。报告候选字符数相对同家基线为`353→315`、`309→312`、`507→324`；Alibaba2另泄露Skill读取说明，MiniMax新增下次会议和节点安排 | `REJECTED` |
| R3 | 6 | 报告候选读取降至1/3，只形成一个provider-case改善；讲话候选反升为2/3。MiniMax仍弱化明确年份，整体稿长没有共性改善 | `TERMINATED_NO_REAL_GAIN` |

R1 同时用当前基线完成两份路由观察：

- 合作性建议信3/3均区分审核部门与平台运营方处置权，以“建议研究”保持未决关系，语气克制；不要求逐字复述“尚未决定”。MiniMax有一次正文外引导和代码块包装，是单家交付噪声，不构成专叶共性失败。
- 征求意见复函3/3均保留主送、来文、具体修改建议、其他条款无意见、落款和日期；Alibaba2同时读取建议反馈页和函类页，OpenCode仅凭入口仍形成完整复函，MiniMax读取函类页。没有两家共同结构缺失，故不增加路由规则。

## 判定校准

- 合理的一层原因、直接作用、总结和条件性后续不计事实外扩。
- 建议信已使用“建议、研究、供参考”时，不因没有机械重复“尚未决定”判失败；只有把建议写成已经认可、已经上线或建议方直接部署才算状态升级。
- 明确年份被改成相对年份、正文外过程说明、材料外责任分工、会议节点和既成决定仍是硬风险。
- 字数只用于同题观察，不以“越长越好”裁决；本轮拒绝的核心是目标读取没有稳定改善且出现候选独有回退。

## 五提交复核与工程边界

第五次提交后暂停复核：相对基线的产品差仅为 canonical `SKILL.md` 一句，Hook、description、版本和镜像均无变化；R1/R2共21份输出技术失败0。`quick_validate.py chinese-official-writing` 通过。镜像尚未同步时，`test_skill_boundary` 准确报出4套普通镜像与 canonical 不一致，不把该预期失败写成通过；候选终止后产品恢复基线，因此不再同步镜像。

冷审还确认两处纯维护状态矛盾，本轮一并修正：

- `requirements.md` 不再声称当前 `SKILL.md` 仍含300/200字阈值，改为指向 `WR-005b` 已完成的历史固定阈值删除。
- `advisory-feedback-tone-r1/result.md` 底部不再与同文件“已合入main”结论冲突。

## 本地输出与哈希

原始终稿、trace、provider JSON 和 summary 留在忽略目录 `output/post-v1623-cold-review-fixes-r1`、`-r2`、`-r3`；未把模型长输出提交到产品包。

- R1 `summary.json` SHA-256：`3fb6c8cea5c16d9998aa4b8c8fabbfb984b7e287050e172e4f380e31ab867619`
- R2 `summary.json` SHA-256：`19c6ac2b56d45b831b3fbb33a221395cc9d6b2319935bc5ddc54832e07af1f7f`
- R3 `summary.json` SHA-256：`e99caf4454a51864fe8bfdc6662f703966c77378d3f8a8955a5116aa2119ca05`

## 实际命令

```text
python maintenance/tests/evidence/post-v1623-cold-review-fixes-r1/run_eval.py --prepare ...
python maintenance/tests/evidence/post-v1623-cold-review-fixes-r1/run_eval.py --provider <alibaba2|opencode|minimax>
python maintenance/tests/evidence/post-v1623-cold-review-fixes-r1/run_eval.py --summarize
python maintenance/tests/evidence/post-v1623-cold-review-fixes-r1/run_r2.py --prepare/--provider/--summarize ...
python maintenance/tests/evidence/post-v1623-cold-review-fixes-r1/run_r3.py --prepare/--provider/--summarize ...
python -m unittest maintenance.tests.test_short_draft_naturalness maintenance.tests.test_skill_boundary
python C:\Users\admin\.codex\skills\.system\skill-creator\scripts\quick_validate.py chinese-official-writing
git diff --check
```

产品修复方向只有在出现新的真实反例、并能用不同机制稳定改善时再开；不继续围绕同一表项堆字。
