# T31-T33 最终补充文种独立 Verifier

## 输入与方法

本轮只读取 `genre-final-writer-c.md` 与 `genre-final-writer-d.md`。第一阶段忽略每题 `ROUTE` 行，仅根据完整原始 prompt 与成稿判定内容；内容判分锁定后，第二阶段才统计 `ROUTE` 自报。

核对范围包括文种功能与行文关系，全部数字、主体、日期、期限、原因、责任和后续事项，用户禁止内容，以及 Markdown、过程说明和保护性自证。`PASS` 表示未发现影响指令遵循、事实边界或文种功能的问题；`WARN` 表示存在非阻断瑕疵；`FAIL` 表示存在明确违背。

## 第一阶段：内容判定

| 题目 | Writer C | 简短证据 | Writer D | 简短证据 |
| --- | --- | --- | --- | --- |
| T31 报告 | PASS | 以市数据局向市人民政府报告，46个系统、12项问题、已整改9项、剩余3项、设备未到货、8月31日前、每月跟踪及完成后复核全部准确；无请批语、审批请求或禁增结论。 | PASS | 保持报告和上下行关系，全部数字、状态、原因、期限及两项后续安排完整；正文外仅提示未提供的成文日期，没有补造日期、审批请求或禁止结论。 |
| T32 说明 | PASS | 保持“情况说明”文种；8件、6件线路故障、2件转办不及时、故障起止、16时20分恢复、次日答复及三项后续措施完整，无评价、追责、影响范围或无影响结论。 | PASS | 以“超时情况—后续措施”组织说明，全部数量、原因、时间和三项措施准确；未改成报告或通报，未补禁增内容。 |
| T33 通报 | PASS | 保持通报文种和局机关各处室对象；10个应报、7个按时、三个处室及2/3/5天、7月22日前整改计划、下一季度既定时限完整，无原因、处罚、排名、表扬或影响结论。 | PASS | 通报事实和要求分层清楚，全部主体、数字、逾期天数、整改计划期限和下一季度要求准确，未补禁止内容。 |

### 统计

| Writer | PASS | WARN | FAIL |
| --- | ---: | ---: | ---: |
| C | 3 | 0 | 0 |
| D | 3 | 0 | 0 |
| 合计 | 6 | 0 | 0 |

6份成稿均未残留 Markdown 标记、写作过程说明或与稿件无关的保护性自证。未发现跨 writer 或跨文种重复出现的同类成稿问题。

## 第二阶段：ROUTE 自报统计

按每名 writer 的3道题统计；同一道题重复自报同一文件时只计1次。

| Writer | SKILL.md | task-route-cards | genre-playbooks | genre-checklist | argument-chains | handling-elements | formal-addressing | official-style | anti-ai | final-review | proofreading | ai-compute |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| C | 3 | 3 | 3 | 3 | 2 | 2 | 0 | 0 | 0 | 3 | 3 | 0 |
| D | 3 | 3 | 3 | 3 | 1 | 3 | 0 | 0 | 0 | 3 | 3 | 0 |

两名 writer 的 `WEB` 均为3/3 `no`，合计6/6 `no`；没有题目自报进入 `ai-compute-docs`。两名 writer 每题均自报 `SKILL.md`、`task-route-cards`、`genre-playbooks`、`genre-checklist`、`final-review-layers` 和 `proofreading-checklist`。Writer C 在T31、T32自报 `argument-chains`，在T31、T33自报 `handling-elements`；Writer D 在T31自报 `argument-chains`，三题均自报 `handling-elements`。

## 证据限制

本轮未读取冷审总报告、Skill 源码、其他 evidence、tests 或网络资料。以上 `ROUTE` 统计只能证明两个输入 packet 写明了哪些自报项，不能证明系统实际访问、加载或未加载了哪些文件，也不能作为访问审计。本报告只判定这6份原 prompt 与成稿，不外推到其他 writer、文种、模型或整体版本质量，也不据此提出修改建议。
