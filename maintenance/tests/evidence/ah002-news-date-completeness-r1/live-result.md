# AH-002 新闻完整日期来源绑定 Hook 真实生命周期结果

## 结论

`PASS_CANDIDATE_NOT_MERGED`。

重复增加日期提示的旧方向仍保持 `TERMINATED`。本候选改用不同机制：默认 `delivery_review` 在完整 D0 形成后的 Stop 先做一次有界检查；只有原请求明确要求新闻成稿、只含一个唯一完整日期，且 D0 只出现一次对应月日时，才把该月日机械替换为完整日期。多日期、来源角色不清、用户要求只保留月日、新闻转成其他文种、D0 已有完整日期或模块异常时均逐字保留 D0。

## 固定范围

- 候选产品树：`ecacc543ba310ac2da1200303a0e5053b5af6ea7`
- 宿主：Claude Code CLI 2.1.195，隔离配置目录，使用未安装的本地 companion
- 能力：默认 `delivery_review`
- 初始 provider：
  - `ollama-cloud/deepseek-v4-flash:0731`
  - `alibaba-token-plan-2/deepseek-v4-flash-0731`
- 固定 fallback：初始合格 provider 少于两家时，只补 `opencode-go/deepseek-v4-flash`
- 每家三题：两则全新活动新闻目标题、一则明确要求照录完整日期的控制题
- 合格门：同一家至少一题自然省略年份后被精确修复，且控制题逐字不变；至少两家合格

## 真实生命周期结果

| provider | 目标 A | 目标 B | 完整日期控制 | provider 结论 |
| --- | --- | --- | --- | --- |
| Ollama Cloud DeepSeek V4 Flash 0731 | D0 已有完整日期，未启动修复 | D0 已有完整日期，未启动修复 | 逐字不变 | 不构成可修复样本 |
| Alibaba Token Plan 2 DeepSeek V4 Flash 0731 | `9月15日` 精确替换为 `2026年9月15日` | `9月22日` 精确替换为 `2026年9月22日` | 逐字不变 | 合格 |
| OpenCode Go DeepSeek V4 Flash | `9月15日` 精确替换为 `2026年9月15日` | D0 已有完整日期，未启动修复 | 逐字不变 | 合格 |

九次执行均完成 Skill 读取、目标新闻叶读取、`UserPromptSubmit`、`PostToolUse`、Stop 和终态脱敏回执；按当前留存契约计算的 `analysis.technical_valid` 为 9/9。三份被修稿件的 D1 与 D0 只差一次预登记的月日到完整日期替换，主体、52/46/6/50、41/37/4/39及相应未汇总状态均保留。三份目标稿自行写全日期时 Hook 没有重复改写，三份控制稿也全部逐字不变。

旧基线 harness 的 `meta.technical_valid` 仍要求终态保留 `state.json`，因此九次均把 `gate_transaction_persisted=false` 显示为技术无效；这与当前 HK-008 终态删除原文事务、只留脱敏回执的产品契约冲突。本结果没有沿用该旧字段，而是要求终态成功、Skill 读取、三事件齐全、无越界读取、模型绑定和脱敏回执同时成立。没有为满足旧 harness 恢复原文事务留存。

## 人工复核

- 三份修订稿均为单一日期替换，没有重写标题、段落、影响谓语或未决状态。
- Alibaba 目标稿和 OpenCode 目标稿存在各模型自身的表达差异，但这些内容在 D0 已经形成，D1 未新增；按本原子只评价与日期 Hook 直接相关的增量，没有把合理即时作用误判为 Hook 回退。
- Ollama 与 OpenCode 目标 B 自行写全日期，记为 `TARGET_NOT_REPRODUCED`，不冒充修复成功，也不记为质量失败。

## 实际命令

```powershell
py -3 maintenance/tests/evidence/ah002-news-date-completeness-r1/run_live.py --prepare
py -3 maintenance/tests/evidence/ah002-news-date-completeness-r1/run_live.py --provider ollama
py -3 maintenance/tests/evidence/ah002-news-date-completeness-r1/run_live.py --provider alibaba2
py -3 maintenance/tests/evidence/ah002-news-date-completeness-r1/run_live.py --summarize
py -3 maintenance/tests/evidence/ah002-news-date-completeness-r1/run_live.py --provider opencode
py -3 maintenance/tests/evidence/ah002-news-date-completeness-r1/run_live.py --summarize
py -3 -m unittest maintenance.tests.test_source_bound_dates maintenance.tests.test_gate_stop_hook maintenance.tests.test_hook_layer_contract maintenance.tests.test_status_ledger_consistency maintenance.tests.test_repository_reachability
py -3 C:\Users\admin\.codex\skills\.system\skill-creator\scripts\quick_validate.py chinese-official-writing
git diff --check
```

直接相关回归为 68/68 `OK`；Skill Creator 校验为 `Skill is valid!`；`git diff --check` 通过。

## 边界与剩余风险

- 当前只证明单一明确日期、目标文种为新闻、默认 `delivery_review` 和 Claude Code companion 的真实在线闭环。
- 不外推到多日期、跨来源日期、日期区间、通知/报告等非新闻目标，也不宣称其他 capability 或所有宿主已经在线重跑。
- companion 只在隔离目录组装，未安装、未启用；候选未合并、未推送、未发布。
