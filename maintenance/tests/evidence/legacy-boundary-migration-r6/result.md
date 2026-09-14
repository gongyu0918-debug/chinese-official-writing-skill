# R6 旧边界断言迁移

本项仅修改 `maintenance/tests/test_skill_boundary.py`，唯一新报告为本文件。没有修改产品、镜像、其他测试、runner 或既有证据，没有启动模型，没有提交。

- 工作树：`F:/Workspaces/chinese-official-writing-skill/output/route-worktrees/reference-rewrite-20260912`
- 分支：`codex/reference-rewrite-20260912`
- HEAD：`d06d51f8c766739a3f0e49dc5205e1672aad53e4`
- 固定旧语义基线：`1ce7112303172478faa2392667a2de1098eb912c`
- 改动：94 行新增、45 行删除；81 个测试方法全部保留，没有删除、skip 或 expectedFailure。

最终运行 81 个方法，75 个方法通过，6 个方法仍有 12 个子断言失败，退出码 1。相较根任务旧日志的 23 个失败方法、41 个失败子断言，29 个失败子断言已有迁移证据并解决；剩余 12 个继续暴露，不能报告全绿。

## 判断依据

先逐项读取旧失败方法，再对照当前明确责任页；必要时读取固定 Git 对象中相应旧规则的实际原文。没有把任意文件拼接成全集搜索来满足断言，也没有把一般的“引用保真”“用户模板”措辞视为所有细分功能都已证明。

主要静态依据：

- `maintenance/tests/evidence/rewrite-cold-r5/legacy-common-parity-r5.md`：G1 明确区分材料来源限制与禁止分析；G2 确认现有字段默认保留；逐页表确认引用保护、字段、格式、材料和复核规则的实际去向。
- `maintenance/tests/evidence/rewrite-cold-r5/legacy-genre-parity-r5.md`：确认工作总结/工作要点、审查意见/采购专项、方案/可研等按功能拆分；G2、G3 分别指出可研建议和消息内合理分析不应被新限制排除。
- 旧 Git 对象中的 `proofreading-checklist.md:11,17–28`、`anti-ai-patterns.md:164`、`final-review-layers.md:50`、`task-route-cards.md:29–30`：直接核对了原有语法/引用、Token 单位、声明版本例外及渠道不推主体要求，未据旧测试名称猜测意图。

定向查看的已完成 native 材料：`maintenance/tests/evidence/rewrite-cold-r5/semantic-parity-native-r5/binding.json`、同目录 `read-analysis.json`，以及 `output/semantic-parity-native-r5/m2-material_based_analysis-candidate.final.txt`、`m4-material_based_analysis-candidate.final.txt`、`m2-existing_field_form-candidate.final.txt`、`m4-existing_field_form-candidate.final.txt`、`m2-news_supported_analysis-candidate.final.txt`。它们可分别观察“只按材料”仍组织有据必要性、既有字段保持字段形态和消息中保留直接作用。这些是旧 R5 绑定，未冒充当前 R6 的新 native 验证；终稿中仍有过程旁白等独立问题，本报告没有将这些稿件宣称为交付质量通过。

另读取了 `maintenance/tests/evidence/rewrite-cold-r5/legacy-functions-native-r5-qwen/binding.json` 用于确认旧事务功能测试的实际任务范围，没有把只读绑定当成成稿结果。

## 逐方法处理

“字面/职责迁移”表示旧检查目的仍在明确责任页成立；“语义纠正/授权替代”表示旧断言本身包含本轮明确修正的限制，或已被统一交付要求取代；“未决”表示没有足够功能证据，继续保留失败。下表计数为根任务旧日志中已经暴露的失败子断言数，受前置断言阻断而未运行到的同方法检查也已逐条核对。

| 测试方法（均保留 `test_` 方法） | 旧失败数 | 处理及实际落点 |
| --- | ---: | --- |
| `ai_compute_detail_is_loaded_from_specialty_reference` | 1 | 字面/职责迁移：首页的普通服务器、接口、安全、SLA、验收排除条件；索引的场景附加规则；技术需求独立主叶；指标和 SLA 在 `ai-compute-docs.md`，英文拼写仍在术语/抗 AI 页。保留主文种先行和混合总页退役负向断言。 |
| `ai_dedupe_prompt_fix_guidance_is_documented` | 2 | 语义纠正：两个安装根的材料来源限制不再强制分析归零；仍检查只改格式、逐字保留、不作分析的限制，以及缺项、日期、正文外提示、无据新增禁止。 |
| `delivery_scope_rule_is_naturalized_across_current_skill_copies` | 2 | 未决：`声明`、`版本` 明示保留例外未证明；保密标识已在当前复核页，原断言保持。正文清理、真实业务事实例外和跨包一致性全部保持。 |
| `formalization_keeps_only_explicit_literal_boundaries_verbatim` | 3 | 语义纠正 1 项：来源限制不等于禁止分析。职责迁移 1 项：`information-selection.md` 明确引用按原词原强度，`anti-ai-patterns.md` 明确保留直接引语且引用不变。`同语境原样保留`仍未决；原词保留不能证明上下文位置保留。 |
| `lightened_routes_preserve_reviewed_conditions` | 3 | 字面/职责迁移：讲话与主持各自条件叠加人物排序；独立审查意见选新主叶，采购专项按必要性附加；建议信增加第 6 行但仍只有原 5 个兼容主叶。继续准确检查两条 advisory 路由及“不预读全部”“只做语言/格式不加采购专项”。 |
| `news_genres_are_defined_in_authoritative_routing` | 1 | 语义纠正/措辞迁移：消息以报道已发生事实为主；仅“以评论为主要用途”转评论。保留纪要不写会议新闻和事实、判断、责任安排分开的负向边界。 |
| `plain_text_title_boundary_contract_is_explicit` | 4 | 全部未决。没有用 Word 专项标题规则替代纯文本标题与编号正文的四项要求。 |
| `plan_construction_playbook_is_routed_as_an_atomic_leaf` | 3 | 职责迁移及语义纠正：稀疏方案按已有要素取舍、可合自然段，拟/待定保留；行业通用做法可以成为分析建议，但不冒充已定实施事项；可研以决策依据和条件性建议为功能。调研样本边界、建议不写已批项目及旧混合页退役均保持。 |
| `proofreading_layer_stays_ai_writing_quality_only` | 5 | 授权交付替代 2 项：未核引用保留待核，按 `delivery.md` 提出与实际缺项对应的具体确认问题，替代固定核验短句及其禁改措辞。成语同语境、的地得、量词 3 项仍未决；没有以泛称“搭配”证明专项能力。 |
| `report_checklist_is_routed_as_an_atomic_leaf` | 1 | 字面/职责迁移：报告主叶有成稿骨架、复核叶承担文种核对且无成稿骨架；用户指定名称、异常原词、状态、原因责任和不夹请批全部保留。 |
| `reported_genre_coverage_gaps_have_minimum_support` | 1 | 职责迁移：总结/要点分别选独立页，审查意见与采购专项分别检查；函、公告、采购公告的反馈路径、联系人和期限继续检查。 |
| `request_playbook_is_routed_as_an_atomic_leaf` | 1 | 字面迁移：原因完全无法推知时，保留已知事项和请求并在文后询问；有材料或常识支持的一般必要性仍可写。请假禁代填、主送来源、短采购灵活篇幅、长任务所需能力页保留。 |
| `revision_workflow_forbids_new_unprovided_facts` | 1 | 语义纠正：来源限制仍可有据分析；最新底稿为唯一事实源、未支持推断删除、无映射表、不新增正式化事实、正文-only按需等边界保持。 |
| `sparse_notice_does_not_treat_delivery_channel_as_issuer` | 1 | 未决：通知页有对象沿用及缺落款不补，但没有足够证据证明邮箱/渠道/接收方不能确立发文主体的专项边界。原正则未放宽。 |
| `trigger_description_covers_reported_genres` | 1 | 职责迁移：索引用“审查意见、评审意见”承载评审材料；实际主叶处理依据评审记录形成采购、初步设计和一般项目审查结论，并保留只审核既有稿件时的原主文种。 |
| `v141_formal_delivery_review_and_tone_rules_are_documented` | 3 | 字面/职责迁移：格式核对按交付用途启动，缺项由 delivery 放正文外，文号/密级/签发/日期/版记禁编造；既有审稿范围、具体意见、模板优先、禁旧生成器和禁伪精确评分全部保持。 |
| `v147_minimal_borrowing_rules_stay_soft_and_prompt_based` | 1 | 授权用途区分：普通 Word 按当前文种、模板、实际字段核对；正式发文要素按请求使用，只写正文先完成正文。保留字体、页码、换行、已定稿字符不可改、点名缺项简报及无据正式化禁止。 |
| `v148_anti_ai_borrowing_stays_soft_and_official` | 1 | 未决：Token 与调用次数的计量区分不能由英文拼写或泛称单位一致证明。原失败保持。 |
| `v150_genre_playbooks_keep_minimal_borrowing_boundaries` | 1 | 职责迁移：总结/要点独立；周报的字段与服务单位责任在 report；方案、采购表和审查意见显式指向 field-editing；字段单元/分号/指定字段改动在字段页。纪要未决、称呼来源、普通采购不触发算力等负向边界保留。 |
| `v1510_sentence_fixes_keep_sparse_and_field_tasks_fact_bounded` | 2 | 语义纠正：现有字段/表格默认沿用原结构；仅素材或用户要求改成叙述才散文化。加入“不再包含必须显式要字段”的负向断言；报告不填空责任流程成效仍检查。 |
| `v1601_j1_writing_endings_use_natural_terms` | 1 | 职责/措辞迁移：讲话按重点任务、体会或期望自然收束，与场合相称，不再要求每份讲话结尾强制落责任目标。请批收束、评论自然结束和短稿不补保证等边界保留。 |
| `weak_model_suggestion_boundaries_stay_soft` | 1 | 字面迁移：首页原级别保留条款与考察、评估、拟测试、考虑尝试、下一步设想条款共同覆盖；报告名称、可选口径、局部修改范围及拟/建议/可不升级继续检查。 |
| `work_summary_elaboration_stays_in_target_section` | 1 | 职责/措辞迁移：总结保留本期工作与下一步关系、有据一般方向、自然将来时、拟议未决状态、成效须实际反馈；要点承担未来任务及责任节点。旧特定“拟→将在”示例改为一般未来表述与明确未决状态分开，未放开效果保证。 |

## 最终仍失败的 12 个子断言

| 方法 | 数量 | 保留的失败项与未决理由 |
| --- | ---: | --- |
| `test_delivery_scope_rule_is_naturalized_across_current_skill_copies` | 2 | `声明`、`版本`。旧规则明确“用户要求显示”的例外，当前正文清理与泛称用户模板不能证明该例外已承接。 |
| `test_plain_text_title_boundary_contract_is_explicit` | 4 | `纯文本主标题行末不加句号`；`标题后空一行`；层级标题不加句号；编号内容为完整正文句时用正常句末标点。格式页只在相应 Word/正式格式任务加载，不能覆盖所有纯文本交付。 |
| `test_sparse_notice_does_not_treat_delivery_channel_as_issuer` | 1 | 邮箱、渠道、接收单位不反推发文主体的原正则。角色保持与不补缺落款属于相邻规则，未证明这条来源推断边界。 |
| `test_v148_anti_ai_borrowing_stays_soft_and_official` | 1 | `不把 Token 改写成调用次数`。当前算力页分列 Token/调用次数并要求单位一致，但未直接说明不可互換；保留计量语义疑点。 |
| `test_proofreading_layer_stays_ai_writing_quality_only` | 3 | 成语默认同语境保留、的地得、量词。泛称语言、搭配、引用复核没有充分证明旧低置信不硬改与具体专项能力。 |
| `test_formalization_keeps_only_explicit_literal_boundaries_verbatim` | 1 | `同语境原样保留`。已明确原词与强度的保护，但不据此宣布引语、诗词或讲话原文的上下文位置保护已闭合。 |

根任务已确认后续另以少量共性语义原型和真实写稿处理上述问题；本项不预先迁移这些未决断言。

## 运行与旧日志

唯一运行的测试模块：

```text
python -B -m unittest maintenance.tests.test_skill_boundary
Ran 81 tests in 0.757s
FAILED (failures=12)
exit code: 1
```

命令由 Python subprocess 启动，捕获输出后只显示失败方法、失败项与总结，未新增测试日志。AST 核对方法数为 81。另执行 `git diff --check -- maintenance/tests/test_skill_boundary.py`，退出码 0；仅有 Git 后续转换 LF/CRLF 的提示。

根任务原日志 `output/r6-skill-boundary.log` 原样保留，其 SHA-256 为 `D26D2BE4BD8890691AA3E1EE4AF6E125C7CDBD179D775C9C4CC72892818B8A67`。未重写旧失败、未增加 skip、未运行其他模块或真实模型。

本次结论属于维护断言与产品静态职责对应核对，不能充当模型自主选路、实际交付或完整写稿质量通过证据。
