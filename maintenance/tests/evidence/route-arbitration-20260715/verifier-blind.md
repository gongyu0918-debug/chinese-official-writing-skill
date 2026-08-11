# 路由仲裁匿名写稿盲审

## 复核口径

- 只依据 prompts.md、writer-c.md、writer-d.md 中的原始任务和匿名输出判定，不推断 A/B 对应版本。
- 内容先按指令遵循、关键事实、无新增事实、文种功能、正式文本格式和输出模式判定 PASS/WARN/FAIL。
- ROUTE 为证据元数据，不计入正文。路由单独核对；多读只记 route over-read，不自动影响内容判定。
- 逻辑路径按相对文件归一：R1、R3、R4 应为 SKILL.md + references/task-route-cards.md；R2 应为 SKILL.md + references/genre-playbooks.md。

## 逐份判定

| Writer | 样本 | 指令遵循 | 关键事实 | 无新增事实 | 文种、格式与输出模式 | 内容总判 | 路由判定 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| C | R1-A | PASS：仅输出简短纪要正文 | PASS：主题、时间、地点、参会单位、汇报、再观察一周、7月22日再次评估及未决状态完整 | PASS：未补决定、责任、期限、采购、考核或 KPI | PASS：会议纪要功能成立，无禁用会议判断和写作说明 | PASS | OVER-READ：除 SKILL 和 task-route-cards 外，多读 genre-playbooks |
| C | R1-B | PASS：仅输出简短纪要正文 | PASS：全部已给事实及未形成决定、责任分工和期限的状态完整 | PASS：无新增事实 | PASS：会议纪要格式清楚，无禁用表达和附加说明 | PASS | PASS：仅 SKILL + task-route-cards |
| C | R2-A | PASS：仅输出简短、完整的正式纪要 | PASS：上线日期、两项任务、责任单位及各自期限绑定准确 | PASS：未新增决定、责任、期限或会议判断 | PASS：纪要功能和正式格式成立 | PASS | PASS：仅 SKILL + genre-playbooks |
| C | R2-B | PASS：仅输出简短、完整的正式纪要 | PASS：三项已给事项完整，责任和期限对应准确 | PASS：无新增事实 | PASS：编号结构清楚，纪要功能和输出模式正确 | PASS | PASS：仅 SKILL + genre-playbooks |
| C | R3-A | PASS：200字以内，仅输出正文 | PASS：10:20延迟、影响3个页面、10:45恢复完整准确 | PASS：未补原因、责任、损失、整改、下一步、主送或落款 | PASS：情况说明简洁正式，无附加说明 | PASS | PASS：仅 SKILL + task-route-cards |
| C | R3-B | PASS：200字以内，仅输出正文 | PASS：全部三项事实准确 | PASS：无禁止新增内容 | PASS：情况说明格式和输出模式正确 | PASS | PASS：仅 SKILL + task-route-cards |
| C | R4-A | PASS：保留标题并仅输出改后稿 | PASS：7月14日、5台、2台未及时更新及当日下午已更新完整 | PASS：未补责任、原因、影响、督办或下一步 | PASS：报告语体可用，无待确认或改动说明 | PASS | PASS：仅 SKILL + task-route-cards |
| C | R4-B | PASS：保留标题并仅输出改后稿 | PASS：日期、数量和处理状态完整准确 | PASS：无新增事实 | PASS：正式报告表达清楚，无附加内容 | PASS | PASS：仅 SKILL + task-route-cards |
| D | R1-A | PASS：仅输出简短纪要正文 | PASS：全部会议要素、建议、再次评估日期和未决状态完整 | PASS：未补决定、责任、期限或其他禁止内容 | PASS：会议纪要功能成立；“会议听取”准确承接已给汇报事实，不构成新增判断 | PASS | PASS：仅 SKILL + task-route-cards |
| D | R1-B | PASS：仅输出简短纪要正文 | PASS：全部关键事实和状态准确 | PASS：无新增事实 | PASS：格式、文种和输出模式正确 | PASS | OVER-READ：除 SKILL 和 task-route-cards 外，多读 genre-playbooks |
| D | R2-A | PASS：仅输出简短、完整的正式纪要 | PASS：上线日期、配置与验收责任、两项期限逐项对应 | PASS：未新增决定、责任、期限或会议判断 | PASS：编号结构和纪要功能正确 | PASS | PASS：仅 SKILL + genre-playbooks |
| D | R2-B | PASS：仅输出简短、完整的正式纪要 | PASS：全部已给事实及对应关系完整准确 | PASS：无新增事实 | PASS：正式纪要格式和输出模式正确 | PASS | PASS：仅 SKILL + genre-playbooks |
| D | R3-A | PASS：200字以内，仅输出正文 | PASS：时间、延迟、3个页面和恢复时间准确 | PASS：未补任何禁止内容 | PASS：情况说明简洁正式，无附加说明 | PASS | PASS：仅 SKILL + task-route-cards |
| D | R3-B | PASS：200字以内，仅输出正文 | PASS：全部三项事实准确 | PASS：无新增事实 | PASS：文种、格式和输出模式正确 | PASS | PASS：仅 SKILL + task-route-cards |
| D | R4-A | PASS：保留标题并仅输出改后稿 | PASS：日期、5台、2台及当日下午完成更新均准确 | PASS：未补责任、原因、影响、督办或下一步 | PASS：正式报告表达清楚，无附加内容 | PASS | PASS：仅 SKILL + task-route-cards |
| D | R4-B | PASS：保留标题并仅输出改后稿 | PASS：全部数字、日期和处理状态完整 | PASS：无新增事实 | PASS：报告功能、正式格式和输出模式正确 | PASS | PASS：仅 SKILL + task-route-cards |

## 同一 Writer 的 A/B 对照

| Writer | 任务 | A/B 差异 | 独有内容问题 |
| --- | --- | --- | --- |
| C | R1 | A 使用“会议时间/会议地点”，B 使用“时间/地点”；B 将主题补入“数据接口联调测试结果”。两稿事实范围一致。A 的 route 多读 playbook，B 路由适配。 | 无事实、文种、格式或输出模式问题 |
| C | R2 | A 用连续段落，B 用编号列示；两稿均准确绑定任务、责任和期限。 | 无 |
| C | R3 | 正文一致。 | 无 |
| C | R4 | A 保留“我们检查”的主体表达，B 改为无主句；两种写法均未改变事实且可用于正式报告。 | 无 |
| D | R1 | 正文一致；B 的 route 多读 playbook，A 路由适配。 | 无事实、文种、格式或输出模式问题 |
| D | R2 | 正文一致。 | 无 |
| D | R3 | 正文一致。 | 无 |
| D | R4 | 正文一致。 | 无 |

## 总判定

- 内容：16/16 PASS，0 WARN，0 FAIL。
- 路由：14/16 适配；2/16 为 route over-read，分别是 Writer C 的 R1-A、Writer D 的 R1-B，均在未决纪要轻卡之外多读 genre-playbooks。
- A/B 对照：没有发现任何一侧独有的事实、文种、正式格式或输出模式问题。
- 本报告不推断 A/B 对应版本，也不把 ROUTE 多读计为内容失败。
