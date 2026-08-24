# WR-001-DATE-R1 结果

日期：2026-08-24。

## 结论

`TARGET_HIT_NOT_ADMITTED`。日期原子在三条有效 Candidate 中均把“8月20日”恢复为“2026年8月20日”；Alibaba 与 Ollama 的有效 Baseline 继续复现年份遗漏，满足目标增量。两条 Candidate 首次运行因未读取隔离 Skill 记技术无效，随后各补一次同题单臂，原记录未覆盖。

但 Ollama 有效 Candidate 补写“继续面向青少年开展阅读推广活动、助力全民阅读氛围营造”，并把题面仅给名称的导读、讨论和练习具体化为梳理重点、交流体会和应用方法；同次 Baseline 也补写“进一步完善后续阅读活动安排”。这是跨臂存在的既有未来安排/具体化风险，不是日期句的确定因果，但 Candidate 未满足预登记的绝对成稿门，因此本轮不准入、不合并。

## 三路结果

| 路线 | Baseline | Candidate | 判定 |
| --- | --- | --- | --- |
| Alibaba Token Plan 2 | 有效；213字；省略年份 | 有效；195字；完整日期；48/45/3/46、单人原话与汇总状态完整 | 目标通过；“培养阅读兴趣”属于偏宽的一层目的表述，记自然度/范围 WARN |
| Ollama | 有效；223字；省略年份；Markdown标题并补后续安排 | 首次未读 Skill，技术无效；补跑有效，289字，完整日期，但补具体活动过程和后续活动安排 | 目标通过，成稿门失败 |
| MiniMax | 有效；190字；完整日期，未重现 R1 的材料外活动细节 | 首次未读 Skill，技术无效；补跑有效，225字，完整日期，未补讲解人、年龄分组、指定篇目、书面答题或后续安排 | 反序控制与候选均通过；上一轮扩写未稳定复现 |

## 下一最小修改

不增加新的活动细节禁令。只把新增日期句并入原有“正文展开时间、地点……”条目，并压成“完整年月日照录，不缩为月日；材料仅有月日时不补年份”，减少一个独立 bullet 和重复词。R2 只复测 Ollama 与 Alibaba Candidate；沿用本轮对应 Baseline，不重跑三路整包。若 Ollama 仍补材料外过程或后续安排，日期候选停止，不以换 provider 覆盖。

## 实际运行

- `python maintenance/tests/evidence/wr001-date-r1/run_eval.py --prepare`
- `python .../run_eval.py --provider <ollama|alibaba2|minimax>`
- Ollama、MiniMax Candidate 各执行一次同配置单臂技术补跑；补跑输出保存在 `output/wr001-date-r1/retries/`。

固定 Candidate：`05a982269ee34e4fac230df6d925f221545c31db`。本轮未修改 main、版本、tag 或平台内容。
