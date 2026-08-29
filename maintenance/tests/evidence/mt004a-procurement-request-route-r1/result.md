# MT-004a-PROCUREMENT-REQUEST-ROUTE-R1 结果

## 结论

状态：`CURRENT_BASELINE_SUFFICIENT / WAIT_NEW_COUNTEREXAMPLE`

没有形成产品候选。首份 QwenWork 包路径 Alibaba Token Plan 2 样本读取入口和6个 references，但全新 Alibaba Token Plan 1 当前基线没有复现：它只读取 `SKILL.md`、`information-selection.md`、`task-route-cards.md` 与 `genre-playbook-request.md`，没有读取本原子关注的 `argument-chains.md`、`formal-addressing.md`、`proofreading-checklist.md` 或 `final-review-layers.md`。

预注册要求第二家也读取请示/申请叶及至少三份上述通用页后才能实现候选。复现门未成立，因此没有修改 reference、SKILL、description、Hook、脚本或镜像，也没有继续五路 A/B 或工程门。

## 两份当前基线观察

| 观察 | 模型 | 实际读取 | 稿件结果 |
| --- | --- | --- | --- |
| QwenWork 包路径 | `alibaba-token-plan-2/deepseek-v4-flash-0731`，max | 入口、信息选择、申请叶、论证链、称谓、轻量校对、总审 | 89字材料→143字正文，事实、状态、合理原因和直接作用通过 |
| 本原子全新题 | `alibaba-token-plan/deepseek-v4-flash-0731`，max | 入口、信息选择、轻量卡、申请叶 | 132字材料→219字正文，技术失败0、硬失败0 |

第二稿完整保留综合处、2台、2018年、近一个月、卡纸、扫描中断、两次清洁、650页、1台A3黑白多功能一体机、3.6万元、4万元和办公设备购置经费。稿中“现有设备已难以满足日常工作需要”“保障日常打印、扫描工作正常开展”由反复故障、处理量和排队事实直接支持，属于允许的一层合理归因与目的，不是外扩；没有新增采购程序、供应商状态、责任、日期或完成承诺。

稿件219个非空白字符短于含测试约束的291字提示词，但长于132字材料，且文种功能完整。提示词总长度不作为短稿失败门。

## 用量与边界

- 客户端：`codex-cli 0.144.6`；只读、ephemeral、无 Hook，用户级同名 Skill 污染0，精确项目 Skill trace 为true。
- Alibaba Token Plan 1 用量：input 76407、cached input 56320、output 4109、reasoning output 3292 tokens。
- 两次模型结果不同，不能仅凭 Token Plan 2 单 trace 认定稳定过载，也不能把 QwenWork 静态包差异认定为原因；QwenWork 包写作字节来自同一 canonical 无 Hook 镜像。

## 重开条件

只有新的简单采购申请在另一家低成本 provider 中再次出现“已读取申请叶，仍继续读取至少三份无任务需要的通用页”，或真实稿出现可归因的功能/质量回退，才重开单一停止条件。重开时仍保护合理原因、直接作用和稿件完整性，并使用复杂采购请示与普通报告反控；不沿本轮样本堆入口提示。

## 实际命令

```powershell
python -m py_compile maintenance/tests/evidence/mt004a-procurement-request-route-r1/run_eval.py maintenance/tests/evidence/mt004a-procurement-request-route-r1/run_baseline_probe.py
python -m json.tool maintenance/tests/evidence/mt004a-procurement-request-route-r1/cases.json
python maintenance/tests/evidence/mt004a-procurement-request-route-r1/run_baseline_probe.py --prepare
python maintenance/tests/evidence/mt004a-procurement-request-route-r1/run_baseline_probe.py --run
python -m unittest maintenance.tests.test_status_ledger_consistency maintenance.tests.test_repository_reachability
git diff --check
```

没有合并、推送或发布。
