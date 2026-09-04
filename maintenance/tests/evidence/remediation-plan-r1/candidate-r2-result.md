# WR-028 R2 状态落位结果

## 运行范围

- 基线：`5869234bcfee5aeb7f70762035a8ee593569fbc3`
- R2 产品候选：`028a11746472d0e8ed062e3744ac462fa4b13591`
- 相对 R1 只强化整改专叶中的状态落位句；五家低成本 provider 以 `max` 各运行短整改和中等审计整改两题，共 10 份候选。
- 候选 8/10 轨迹有效。Alibaba2 短整改和 MiniMax 中等审计读取到用户 Skill 路径，按隔离污染剔除；与原基线组成 7 个双臂技术有效对。

## 人工复核

| 原子 | 有效稿 | 状态与功能 | 判定 |
| --- | ---: | --- | --- |
| 中等审计整改 | 4/5 | 4 份有效稿均明确写出“上述问题均尚未启动整改”或同义状态，R1 的 Alibaba2 候选独有遗漏已消除；四类问题、给定责任、统一期限和实际措施均保留 | 通过 |
| 短整改方案 | 4/5 | 4 份有效稿均同时保留办事指南“尚未形成统一版本”和整改“尚未开始/尚未启动”，并形成原因、直接影响和可执行措施，没有退化成问题复述 | 通过 |

自动检查把 Ollama、MiniMax 的“整改工作尚未启动”标成缺少“整改工作尚未开始”，人工按等义状态校正为保留。所有有效稿均允许并实际使用了一层合理归因、直接影响或职责范围内未来措施；这些不作外扩失败。

## 非阻断观察

- Alibaba1、Ollama 短稿各出现一句正文前过程说明。R1 同模型同题没有该现象，R2 唯一规则又只涉及正文内状态落位，不能把这类采样波动归因于状态句；但它已满足 `CL-001-NOHK-R2` 的跨 provider 新反例条件，单独重开正文交付原子，不在 WR-028 内叠加修复。
- MiniMax 短稿同时读取普通方案叶、论证链、办理要素等 9 份文件，形成 1,390 字且出现编号跳项；其他有效 provider 未复现同类过读，暂记单 provider 路由观察，不据此改变整改专叶。
- 部分稿件仍会自行选择培训、台账、定期核对等未来载体。只要未伪装成材料已经批准的事实、未新增精确人员预算日期且与问题直接对应，就按用户授权的方案设计处理；不把正常整改措施误判为失败。

## 结论

R2 消除了 R1 唯一候选独有硬状态回退，达到预登记的真实写稿通过线。直达路由和专叶可进入直接工程门：同步普通兼容镜像，补路由、状态和镜像断言，再运行 quick validate 与合并前一次全量门。当前结论只代表候选具备工程验证资格，不代表已经合入 `main`、推送或发布。

## 实际命令

```powershell
python maintenance/tests/evidence/remediation-plan-r1/run_r2.py --prepare
python maintenance/tests/evidence/remediation-plan-r1/run_r2.py --provider alibaba2
python maintenance/tests/evidence/remediation-plan-r1/run_r2.py --provider alibaba1
python maintenance/tests/evidence/remediation-plan-r1/run_r2.py --provider ollama
python maintenance/tests/evidence/remediation-plan-r1/run_r2.py --provider opencode
python maintenance/tests/evidence/remediation-plan-r1/run_r2.py --provider minimax
python maintenance/tests/evidence/remediation-plan-r1/run_r2.py --summarize
```
