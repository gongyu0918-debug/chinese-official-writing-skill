# AH-002 同稿精确修订结果

日期：2026-08-29。

## 结论

五家便宜 provider 对三份自然漏年 D0 和一份完整日期控制稿共完成20次 Hook 式续写。三份目标稿均为5/5只把唯一的月日恢复为材料中的完整年月日，控制稿为5/5逐字不动；20份终稿全部逐字等于机械期望值，没有日期外改写、正文外说明或事实扩张。该结果达到产品原型启动条件。

| provider | 目标与控制精确命中 | 显式 Skill trace | 总耗时（秒） |
| --- | ---: | ---: | ---: |
| Alibaba Token Plan 2 | 4/4 | 0/4 | 79.14 |
| Alibaba Token Plan | 4/4 | 1/4 | 88.22 |
| Ollama Cloud | 4/4 | 0/4 | 72.84 |
| OpenCode Go | 4/4 | 1/4 | 246.52 |
| MiniMax CN | 4/4 | 0/4 | 101.96 |

## trace 口径修正

上游真实写稿 runner 把“没有显式读取 Skill”统一记为技术失败，因此旧汇总只得到2份技术有效稿。阶段二实际测试的是 Hook 已发出的有界续写指令，目标是宿主模型能否逐字执行该指令；续写不需要重新读取 Skill。故本轮同时保留两个口径：

- `skill_attributed`：仅2/20，可用于证明模型在该回合重新读取了 Skill；
- `continuation_valid`：20/20，要求命令成功、终稿非空且没有其他技术失败，用于判断 Hook 续写能否成立。

这不是放宽正文标准。所有20份正文仍须逐字等于唯一机械期望值；任何日期外变化都会失败。缺失 Skill trace 只是不把结果归因于普通 Skill 触发，不影响对 Hook 续写能力的判断。

## 产品边界

本结果只支持下一步的确定性 source-bound 原型：请求中已有唯一完整日期，D0 只出现一次对应月日，且没有歧义时，才可做一次机械替换。它不支持自由改写，不允许从当前日期或常识补年份，也不处理多个同月日、冲突日期、来源只给月日、用户要求省略年份或正文已出现完整日期的情况。

实际命令：

```text
py -3 maintenance/tests/evidence/ah002-news-date-completeness-r1/run_repair.py --prepare
py -3 maintenance/tests/evidence/ah002-news-date-completeness-r1/run_repair.py --provider alibaba2
py -3 maintenance/tests/evidence/ah002-news-date-completeness-r1/run_repair.py --provider alibaba1
py -3 maintenance/tests/evidence/ah002-news-date-completeness-r1/run_repair.py --provider ollama
py -3 maintenance/tests/evidence/ah002-news-date-completeness-r1/run_repair.py --provider opencode
py -3 maintenance/tests/evidence/ah002-news-date-completeness-r1/run_repair.py --provider minimax
py -3 maintenance/tests/evidence/ah002-news-date-completeness-r1/run_repair.py --summarize
```

原始 final、trace、stderr、fixture 和 summary 位于忽略目录 `output/ah002-news-date-completeness-r1/repair/`。
