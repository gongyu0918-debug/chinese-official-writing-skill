# 当前公开 MIT Skill 审核发现

固定基线 `5fbb2d26c49d0b780ad11fc4cff008854995ad3f`；审核时 main 干净。冷审和离线故障复现不代表真实成稿总体失败率。

## 可复现缺陷

| 发现 | 位置（相对仓库根） | 复现与状态 |
| --- | --- | --- |
| 自动补日期错绑示例 | `chinese-official-writing/hooks/shared/source_bound_dates.py:111`；`hooks/core/gate_stop_hook.py:1374` | 请求活动事实为2026-09-05，另有明确不属于事实的格式示例2020年9月5日；D0仅写9月5日。首个Stop将其改成2020年9月5日并以TERMINAL_D0选择。根代理独立复现；日期歧义旁路原型在codex/hook-date-binding-audit-r1，未准入、未合并。 |
| 错回显预算耗尽放行 | `chinese-official-writing/hooks/core/gate_stop_hook.py:1489` | 选定稿是“测试工作已完成”，连续提供四次“已批准采购”错回显后，返回continue=true、delivery_verified=false，事务已清理。原生adapter无法替换可见正文。根独立复现；未修复。 |
| 终态重放恢复原请求 | `chinese-official-writing/hooks/core/gate_stop_hook.py:1234`及`:1635` | 禁用Hook的任务到Stop清理后，重放同turn的UserPromptSubmit恢复request；后续Stop看到旧脱敏标志直接放行。根独立复现；未修复。 |
| 晚到事件覆盖终态 | `chinese-official-writing/hooks/core/gate_stop_hook.py:1276` | 用确定性线程调度暂停PostToolUse写入，先让正确Stop完成清理，再释放旧写入，request与emitted_output回流，已删除txn不能再清理。根独立复现；这是离线并发故障调度，不冒充在线发生率。 |
| lint命令依赖cwd | `chinese-official-writing/references/final-review-layers.md:74` | 普通包安装在项目.agents/skills下时，在项目cwd执行python scripts/prose_lint.py失败exit2；按SKILL目录解析绝对脚本路径成功并检出同一finding。尚未修改产品文字。 |
| 过期协议前置指向 | `chinese-official-writing/references/delivery-review-gate.md:56` | 指向information-selection.md的写后标记流程已经不存在；普通包排除该协议，不构成普通用户必读负担。尚未修改。 |

## 质量覆盖边界

默认delivery_review的自动定位器主要发现保护性、自证、示弱、材料阅读叙述、无依据负面断言等句式。无finding时直接选择D0；数字、主体与状态硬锚多用于保护D0到D1的修订，不等于已验证D0完全正确。六项能力静态互斥，不能把单项通过等同于综合无错。

已核实固定基线：普通core最多4次Stop续写尝试，每个Stop子进程共享25秒预算，单子进程20秒；存在事务绑定、正常终态脱敏和bootstrap锁。上述正面控制与缺陷同时成立。

## references负担与统计边界

Git UTF-8字节：入口27,147；35份references共196,198；其中Hook协议14,400。五套普通兼容包已排除Hook协议、hooks和review_gate.py，因此不能宣传把协议搬目录就让普通写稿每次节省14KB。

入口5行原型的20份真实A/B已完成并依据原trace重算；候选独有硬问题阻断准入，运行时已恢复基线，见[完整结果](candidate-r1-result.md)。旧probe漏记Windows重复分隔符的统计独立保留，不重跑模型掩盖问题。

## 可缩小的转读范围

- SKILL核心步骤与条件表各自指向通用页，可能让已由专叶覆盖的任务继续读通用路由、办理要素或论证页；R1试验证明不能一次整体放松后仅凭文件变短准入。
- `genre-playbook-minutes.md:16` 的只审不改转读仍指向完整review-checklist，而当前已有定向review-direct页；需要以纪要定向审稿真实对照检验，尚未改动。
- `genre-playbooks.md:30` 把再次修订送到workflow，但精确修订模式入口已在SKILL中；`final-review-layers.md:56` 无条件要求通读anti-ai-patterns，与入口按需条件不一致。两处均登记为具体候选，不直接删除整页。
- `final-review-layers.md`中的正文残留规则实际约束交付，不能因含“校验”“审核”等字样就当维护说明剪掉。Hook协议是功能性运行时资料，但只有明确处理Hook才应读；其过期指向应修，不应宣传目录搬迁等于普通包减载。

## 已运行的审核验证

固定基线执行以下159项全部通过，quick_validate输出Skill is valid；这些结果没有覆盖上表新反例，也不证明稿件无错：

```text
python -m unittest maintenance.tests.test_gate_stop_hook maintenance.tests.test_hook_layer_contract maintenance.tests.test_repository_reachability maintenance.tests.test_status_ledger_consistency maintenance.tests.test_review_prompt_nearfield maintenance.tests.test_skill_boundary
```

新反例由临时审计脚本在独立目录复现，未写入main、未安装或发布插件。后续修复须按同一真实D0或真实写稿验证，再补直接相关工程门。
