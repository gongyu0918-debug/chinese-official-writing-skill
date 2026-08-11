# T27-T30 文种补缺独立 Verifier

## 输入与方法

本轮只读取 `genre-gap-writer-c.md` 和 `genre-gap-writer-d.md`。第一阶段忽略每题 `ROUTE` 行，只根据完整原始 prompt 与成稿判定内容；内容判分锁定后，第二阶段才统计 `ROUTE` 自报。

核对范围包括事实、数字、主体、对象、日期、期限、责任和文种关系，用户禁止事项，Markdown、过程说明和保护性自证。`PASS` 表示未发现影响指令遵循、事实边界或文种功能的问题；`WARN` 表示存在非阻断瑕疵；`FAIL` 表示存在明确违背。

## 第一阶段：内容判定

| 题目 | Writer C | 简短证据 | Writer D | 简短证据 |
| --- | --- | --- | --- | --- |
| T27 决定 | PASS | 保持“决定”文种，以市人民政府名义写明2026年7月10日会议审议、8月1日起停止执行及3项措施，发布日期准确；未改成通知或命令，未补文号、依据、原因或后续措施。 | PASS | 明确使用“市人民政府决定”，会议日期、施行日期和3项措施完整，未增加依据、原因、文号或后续安排。 |
| T28 复函 | PASS | 标题、主送和“来函收悉—现函复”保持来函/答复关系；2名技术人员、7月18日9时30分、302会议室、7月17日前名单及联系人电话全部准确，无禁增内容。 | PASS | 来函日期、同意协助、2名人员、对接时间地点、名单期限、联系人和复函日期完整；未补服务范围、费用、姓名、政策或其他安排。 |
| T29 批复 | PASS | 以上级市数据局答复市政务服务中心请示，明确“同意”；8月1日、17时调至18时、试行至9月30日及7月25日前公布的强度和期限均保持，无新增依据、会议、要求或联系人。 | PASS | 请示与批复关系清楚，两项批复内容完整，所有日期、时点和“应”要求准确；无禁增内容。 |
| T30 致辞 | PASS | 欢迎38支团队和评委，介绍12个方向、2天赛程，感谢评委和承办人员并祝赛事顺利；篇幅明显低于500字，语气克制，无政策、成绩、单位、姓名、奖项、承诺或口号。 | PASS | 欢迎38支团队、评委和承办人员，覆盖12个方向、2天、两类感谢和祝愿；500字内，无禁止新增内容。 |

### 统计

| Writer | PASS | WARN | FAIL |
| --- | ---: | ---: | ---: |
| C | 4 | 0 | 0 |
| D | 4 | 0 | 0 |
| 合计 | 8 | 0 | 0 |

8份成稿均未残留 Markdown 标记、写作过程说明或与稿件无关的保护性自证。未发现跨 writer 或跨文种重复出现的同类成稿问题。

## 第二阶段：ROUTE 自报统计

按每名 writer 的4道题统计；同一道题多次自报同一文件时只计1次。

| Writer | SKILL.md | task-route-cards | genre-playbooks | genre-checklist | argument-chains | handling-elements | formal-addressing | official-style | anti-ai | final-review | proofreading | ai-compute |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| C | 4 | 4 | 3 | 4 | 2 | 3 | 0 | 1 | 1 | 4 | 4 | 0 |
| D | 4 | 4 | 3 | 4 | 2 | 3 | 2 | 1 | 1 | 4 | 4 | 0 |

两名 writer 的 `WEB` 均为4/4 `no`，合计8/8 `no`；没有题目自报进入 `ai-compute-docs`。两名 writer 的共同自报模式为：每题均命中 `SKILL.md`、`task-route-cards`、`genre-checklist`、`final-review-layers` 和 `proofreading-checklist`；T27、T28、T30命中 `genre-playbooks`；T28、T30命中 `argument-chains`；T27-T29命中 `handling-elements`；T30命中 `official-style` 和 `anti-ai-patterns`。Writer D 另在T28、T29自报 `formal-addressing`。

## 证据限制

本轮未读取冷审总报告、Skill 源码、其他 evidence、tests 或网络资料。以上 `ROUTE` 统计只能证明两个输入 packet 写明了哪些自报项，不能证明系统实际访问、加载或未加载了哪些文件，也不能作为访问审计。本报告仅判定这8份原 prompt 与成稿，不外推到其他 writer、文种、模型或整体版本质量，也不据此提出修改建议。
