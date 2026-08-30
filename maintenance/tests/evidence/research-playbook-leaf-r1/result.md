# RESEARCH-PLAYBOOK-LEAF-R1 当前基线结果

日期：2026-08-31。固定产品基线：`main@5cb26b75395f598838267a88dd7825cad4fcac12`。研究分支：`codex/research-playbook-leaf-r1`。

## 结论

状态为 `REJECTED_BASELINE_ROUTE_NOT_REPRODUCED / WAIT_NEW_COUNTEREXAMPLE`。

两家低成本 provider 的8次真实写稿均技术有效，4份研究目标题均形成1715—1973个非空白字符的完整长稿；但 `genre-playbooks.md` 只在 OpenCode 的一份仪器共享研究报告中被读取。政务服务调研报告为0/2读取，仪器共享研究报告为1/2读取，合计1/4。其余目标题稳定使用 `genre-checklist-report.md`、`argument-chains.md` 和 `information-selection.md`，没有形成“两家在两类全新长稿共同伴读组合页”的候选前提。

因此不创建 `genre-playbook-research.md`，不调整 `SKILL.md`，不扩大到其余三家 provider，不补 deterministic provider、镜像或工程门。canonical Skill、references、Hook、packages、description、版本和冻结 v1.6.22 均为0字节变化。这是已按停止条件收口的拒绝，不是 `HOLD`。

## 实际结果

| provider | 调研报告字符 | 读取组合页 | 研究报告字符 | 读取组合页 | 通知字符 | 采购申请字符 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Alibaba Token Plan 2 / DeepSeek V4 Flash 0731 | 1897 | 否 | 1715 | 否 | 204 | 157 |
| OpenCode Go / DeepSeek V4 Flash | 1861 | 否 | 1973 | 是 | 161 | 145 |

- 8/8记录正常返回、读取精确隔离 Skill，无用户目录 Skill 污染。
- 4/4研究目标题处于1600—2200字题面范围内，均不短于提示词；自动事实/状态硬检查为0项。
- 4份长稿均保留样本、数据、时间范围和未决条件，问题、原因、建议与条件风险有完整后半篇；透明比例和余数计算属于已给数据的直接算术，不作外扩失败。
- 调研稿中的一般时段习惯、流程衔接和条件性建议属于材料与常识支持的一层分析。本轮没有用过严的“逐字复述”标准否决长稿。
- 两份通知的自动失败分别来自“6个/六个”和“各2名/各选派2名”的等义字面差异，人工复核均保留对象与人数，不计真实失败。
- 两份采购申请均保留采购原因、事项、数量、单价、合计、经费来源、申请主体和缺失日期边界，但未把供应商、采购方式和完成日期的未决状态写入正文。这是当前基线的相邻短稿观察，不由不存在的候选 diff 造成，也不能反向证明研究 playbook 应拆分；本轮不另开规则原子。

当前 Windows 工作树中，`genre-playbooks.md` 为5691字节，现有研究小节为877个 UTF-8 字节。即使把该小节迁入自包含新叶，理论收益也只会出现在实际读取组合页的记录中；本次目标题只有1/4命中，静态约4 KB差额不足以证明稳定用户收益。

## 原始证据与用量

- 预登记、题面和 runner 位于本目录；终稿、JSONL trace、stderr、usage 与逐条读取位于忽略目录 `output/research-playbook-leaf-r1/baseline/`。
- baseline summary SHA-256：`CFF0CEF5A71EB7CAB2FF09AB9B5A975C1D1F751C9FC3D7B7F6F35671F855FAF1`。
- 8次调用累计 input 1,122,074、cached input 959,488、output 64,583、reasoning output 15,799 token。用量只证明真实模型执行，不作为质量票。
- 首阶段终稿 SHA-256：
  - Alibaba2 调研：`3cd844d74f4484ef8f09cb3c1a3d070f46d41e84eca6f6b76f24bbc46d374d96`
  - Alibaba2 研究：`0e966f3a49c8cd708cfff652718e2350991be3810cf75ea256416d365a995106`
  - OpenCode 调研：`e7d37c5c314fb499729de76fbd7f0fce6bef562a0dd3a5c9821e5bb85af861e6`
  - OpenCode 研究：`9aa0219b2a66947b5c8be6f7aa18f38be21c6823236ae5cc873a3e612d97191f`

实际执行：

```text
python -m json.tool maintenance/tests/evidence/research-playbook-leaf-r1/cases.json
python -m py_compile maintenance/tests/evidence/research-playbook-leaf-r1/run_probe.py
python maintenance/tests/evidence/research-playbook-leaf-r1/run_probe.py --prepare
python maintenance/tests/evidence/research-playbook-leaf-r1/run_probe.py --provider alibaba2
python maintenance/tests/evidence/research-playbook-leaf-r1/run_probe.py --provider opencode
python maintenance/tests/evidence/research-playbook-leaf-r1/run_probe.py --summarize
git diff --check
```

其余 Alibaba Token Plan、Ollama Cloud 与 MiniMax 三家未运行，原因是预登记的首阶段加载门已经失败；继续消耗不会使未出现的跨 provider 共同路由成立。冻结 `codex/release-v1.6.22@62ba9e8206e5b11f08a8f28ebdfe95b08e30ccfe` 未修改、未重建、未移动，本轮不合并、不推送、不发布。
