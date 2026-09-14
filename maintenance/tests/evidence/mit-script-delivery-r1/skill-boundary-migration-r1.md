# test_skill_boundary 迁移报告

## 范围与结果

- 工作树：`F:/Workspaces/chinese-official-writing-skill/output/route-worktrees/reference-rewrite-20260912`；分支 `codex/reference-rewrite-20260912`；接手检查点 `67a77146`；本次报告生成时 HEAD `67a7714635bcd92e6e32fb9e3feb0dd2dcb9620d`。
- 本子任务仅修改 `maintenance/tests/test_skill_boundary.py` 和本报告；没有修改产品、同步适配器或提交。运行期间根任务调整申请叶并同步镜像，相关结果以报告本次运行状态为准。
- 依据：`maintenance/specs/reference-rewrite-20260912.md`（B/C/D/E/G）及 `maintenance/docs/reference-rewrite-page-map-20260912.md` 的 50 页归属和新建页表；逐页读取现行正文，旧测试方法来自接手检查点。
- 方法数：原 81，现 81；删除 0，新增 0，skip 0。AST 比较显示 64 个方法更新，17 个方法原样保留。
- 接手首次运行：81 个顶层测试，69 failures + 22 errors；统计包含各平台 subTest。当时 4 个镜像 failure 来自并行申请叶更新，不能把它们归为陈旧断言。
- 本次结果：75 个顶层测试通过，6 个顶层测试保留失败；16 failures，0 errors，0 skipped。当前镜像字节校验通过。**模块仍未通过，不能报告全绿。**

## 迁移取舍

1. `workflow.md` 删除后，任务模式、材料筛选、局部动作、篇幅及复核分别绑定 SKILL、information-selection、structure-editing、field-editing、compression-details 和编号检查，测试不拼接任意文种页寻找词语。
2. `genre-playbooks.md` 与通知/公开发布、研究/可研等混合页删除后，测试直接校验索引中的功能行、独立主叶存在以及该页自身功能。报告起草与报告细查分开；纪要、请示/申请、函、方案、制度、新闻、整改和采购仍分别保护其事实/状态与文种职责。
3. 旧 37 行路由快照和哈希不再代表新架构；用显式功能→主叶映射、五个兼容场景、每个根目录的链接解析和质量检查衔接替代。原图无环、镜像字节、包目录/许可/版本检查保持。
4. 首页 description 精简不代表取消文种。将较少见文种和新闻别名检查迁到显式索引/兼容场景行，同时保留简短 discovery、主动触发和场景词不改文种的边界。
5. 旧短稿“终止读页/不读主文种”按 spec C/D 与 page-map #48 明确替代为：两个独立轻量条件、保留唯一主文种、任务范围内减读，完成后进入编号检查。保留会议未决、短通知不新增办理安排和事实不足时不填结构等功能。
6. 旧“默认不外搜/仅用户请求或时效事实联网”按 spec 与 page-map #8 替代为不熟悉文种/材料/通用写法时定向研究；常规已知文种、单位名不触发样文搜索、用户业务事实不由网络替换、来源用途与一次补搜停止点仍有断言。
7. 原逐段、逐节、全文三级复核的目标是改动范围与合稿质量。按 spec E 的明确新编排迁为局部及关联段落、整体稿全文、编号顺序、改后复扫、最终发送已查文本，不恢复逐小段逐小节强制步骤，也不允许“最多修一次”限制。
8. MIT Hooks 的删除以 spec E 与 page-map #7 为依据：保留 hook-free 包面、普通 draft_length/prose_lint 文件与 MIT 许可；README 许可断言改为普通 Skill/references/scripts/兼容包范围。未测试或宣称 Pro 生命周期。
9. 旧“收束”禁词与某标题/示例出现次数只保护自然结束和不机械清洗，改为新闻评论自然结束、文种尾语、实际办理落点、正式词按语境及持续推进非禁词的契约。未改变用户指定尾语逐字保留。
10. 申请叶按根任务的实时文本保护完整理由、材料和常识支持的一般必要性、可选短格式、请批动作、字段/长篇路径及请假原因边界；不恢复“短稿只能一句”或默认强制一两段。

## 普通脚本实际调用

- 文稿复核测试从 prose-lint-usage.md 提取文档命令，确认解释器、带引号的 Skill 绝对路径、draft-body 模式和稿件路径；实际用 stdin 启动 prose_lint.py --delivery-mode draft-body --structure --format --json -，JSON 返回可解析，退出码为 0。另校验 review-only/gap-note-allowed 使用对象、修复/复扫和运行失败说明。
- 篇幅测试实际调用 draft_length.py --count-mode nonspace/cjk --min-chars N --max-chars N --json -。固定输入“正文ABC12。”加独立文后提示，结果 nonspace=8、cjk=2，范围为 draft-before-postscript，状态 within；文后提示未计入。两种模式各运行一次。
- 这些是命令和范围的 smoke，不是模型真实写稿、字体排版、Hook 生命周期或全部文种真实质量证据。

## 尚未证明的旧语义

| 编号 | 原测试保护的旧规则 | 当前相关落点与已承接部分 | 保留失败及处理建议 |
| --- | --- | --- | --- |
| U1 | 清除 AI 旁白时仍保留材料本身的领导要求、声明、版本或保密标识。 | anti-ai-patterns 保留真实领导背景；final-review-layers 有事实、字段、附件和批注保护，但未区分真实声明/版本/保密标识与正文外包装。 | delivery_scope 的 3 条失败。请核对是否存在等价材料语义并作定向保真测试；未证明前不以泛称“事实保留”自动关闭。 |
| U2 | 纯文本主标题不加句号、标题后空一行；层级标题无句号；完整编号正文句正常标点。 | SKILL 仅普通文本标题；format-gbt9704 与 advisory-feedback 有 Word/专门场景层级规则，不能证明所有纯文本任务承接。 | plain_text_title 的 4 条失败，当前按 delivery.md 作为交付归属定位。应确认纯文本边界的真实落点，避免强制扩大 Word 页伴读。 |
| U3 | 引号内、明确原文/引语或要求逐字保留者保留字面；同语境原样保留。 | information-selection 有用户逐字限制且分析层归零；anti-ai-patterns 保留引语；proofreading 仅通用引用一致性。 | formalization 的 2 条失败。普通口语可调整已经通过，显式引语的窄边界尚无完整落点。 |
| U4 | 成语默认同语境保留；未核引用使用正文外核实提示而不把引文本身替换为“请核实出处”；校对覆盖的地得与量词。 | 引用/数据待核状态已由 final-review-layers 明确保护，病句搭配/数字/主体一致性已迁移；proofreading 未承接成语语境及两类细校对点。 | proofreading 的 5 条失败。核实提示句的原字面暂留为缺口证据，后续可以用等价非破坏性提示契约替代，不要求永久保留旧句。 |
| U5 | 邮箱、反馈渠道或接收方出现的名称不能反推发文主体；当前日期也不能自动补主体/落款。 | notice 已保护已给对象、主送称谓及不自行补落款；SKILL 已保护日期缺失。但尚未明确渠道与发文主体是不同角色。 | sparse_notice 的 1 条失败；正则只接受渠道/接收方不得推出发文主体这一关系，不靠单词同时出现通过。 |
| U6 | 术语改写不得把 Token 改为调用次数。 | ai-compute-docs 列出 Token/调用次数并保持单位一致；technical-terms 仅四项缩写，anti-ai-patterns 有官方拼写保护。 | v148 的 1 条失败，现行明确单位区分未证明；应确认 Token 单位边界可否由现有数值口径契约直接覆盖，并提供证据。 |

以上均标为待确认语义，**不等同于已证实的模型真实回退**。本子任务没有补产品，也没有通过删断言或 skip 掩盖缺口。

## 逐项结果与保护功能

下表方法名与原模块一一对应；“迁移”表示改到当前归属，不代表全部语义或真实写作质量已验收。未改方法仍执行原断言。

| 测试方法 | 状态 | 保护功能/本次可观测契约 |
| --- | --- | --- |
| `test_only_one_agent_handoff_entrypoint_remains` | 原样通过 | only one agent handoff entrypoint remains |
| `test_canonical_skill_declares_positive_trigger_boundary` | 迁移通过 | Discovery stays concise; execution and fact boundaries live in the body. |
| `test_skill_frontmatter_keeps_only_discovery_fields_and_tags` | 原样通过 | skill frontmatter keeps only discovery fields and tags |
| `test_openclaw_github_package_is_current_mit_and_hook_free` | 原样通过 | openclaw github package is current mit and hook free |
| `test_qwenwork_package_has_official_layout_and_bounded_claims` | 原样通过 | qwenwork package has official layout and bounded claims |
| `test_ai_compute_detail_is_loaded_from_specialty_reference` | 迁移通过 | Compute overlays require a primary genre and explicit compute signals. |
| `test_adapter_skill_copies_keep_boundaries` | 迁移通过 | Every adapter keeps the same entry, fact and out-of-scope boundaries. |
| `test_delivery_scope_rule_is_naturalized_across_current_skill_copies` | 保留失败（3） | Clean body and separate delivery notes survive in every package. |
| `test_entry_excludes_only_non_obvious_out_of_scope_tasks` | 迁移通过 | Out-of-scope examples stay concise and limited to adjacent writing tasks. |
| `test_drafting_rules_are_split_for_prompt_following` | 迁移通过 | Users' requirements precede genre selection; task actions are separated. |
| `test_long_form_headings_warn_against_markdown_bold` | 迁移通过 | Plain titles and final-body packaging remain distinct from explicit Markdown. |
| `test_plain_text_title_boundary_contract_is_explicit` | 保留失败（4） | Unresolved: plain-text title punctuation and blank-line boundaries must survive. |
| `test_style_references_keep_precise_routes_without_common_error_catchall` | 迁移通过 | Language and anti-AI risks have named conditional routes, not a catch-all. |
| `test_second_revision_fact_mapping_has_one_complete_entry_rule` | 迁移通过 | Fact mapping is internal and correction-triggered; revisions remain nonblocking. |
| `test_packaged_resource_mirrors_match_canonical_bytes` | 原样通过 | packaged resource mirrors match canonical bytes |
| `test_canonical_and_plain_packages_exclude_gate_sources_and_keep_scripts` | 原样通过 | canonical and plain packages exclude gate sources and keep scripts |
| `test_skillhub_clean_package_allowlist_has_expected_file_count` | 原样通过 | skillhub clean package allowlist has expected file count |
| `test_reference_loading_table_keeps_progressive_disclosure` | 迁移通过 | The new index selects one genre, conditional capabilities and a review bridge. |
| `test_lightened_routes_preserve_reviewed_conditions` | 迁移通过 | Replace obsolete row hashes with explicit primary-function and scene mappings. |
| `test_lightened_indices_resolve_from_each_skill_root_and_keep_quality_bridges` | 迁移通过 | Each installed root resolves its own routes and reaches ordered quality checks. |
| `test_task_route_cards_keep_sparse_tasks_lightweight` | 迁移通过 | Sparse drafts and local edits independently shorten work without dropping genres. |
| `test_missing_metric_visibility_does_not_become_plan_state` | 迁移通过 | Missing source data must not become a business decision or plan state. |
| `test_sparse_length_rule_keeps_fact_boundary_without_short_first_priority` | 迁移通过 | Length preserves facts and justified analysis; unsupported filling stays forbidden. |
| `test_light_route_is_terminal_until_an_explicit_escalation_condition` | 迁移通过 | Spec replaces terminal cards with one retained genre and bounded final checks. |
| `test_sparse_notice_does_not_treat_delivery_channel_as_issuer` | 保留失败（1） | Unresolved: contact channels or recipients cannot establish the issuing subject. |
| `test_workflow_sparse_line_relief_keeps_carriers_and_route_graph` | 迁移通过 | Sparse reports keep factual carriers while the removed workflow has explicit owners. |
| `test_reference_links_form_an_acyclic_graph` | 原样通过 | reference links form an acyclic graph |
| `test_trigger_description_covers_reported_genres` | 迁移通过 | Compact discovery delegates less common names to the explicit genre index. |
| `test_multi_round_revision_rules_keep_structure_and_genre_format` | 迁移通过 | The structure owner preserves latest-draft actions, granularity and labels. |
| `test_legal_genres_have_checklist_and_handling_elements` | 迁移通过 | Legal genre functions are independent leaves and handling stays a common checklist. |
| `test_reported_genre_coverage_gaps_have_minimum_support` | 迁移通过 | Previously reported genres still route to pages with their own useful functions. |
| `test_genre_authority_uses_the_defined_routing_source` | 迁移通过 | Uncertain genre relations route to the decision tree and official writing sources. |
| `test_report_checklist_is_routed_as_an_atomic_leaf` | 迁移通过 | Report drafting and review separate while title, cause, status and function survive. |
| `test_feasibility_review_checklist_is_an_atomic_leaf` | 迁移通过 | Targeted feasibility review remains scoped to claims and evidence already supplied. |
| `test_minutes_playbook_is_routed_as_an_atomic_leaf` | 迁移通过 | Minutes retain decisions, attribution and unresolved states in one primary leaf. |
| `test_request_playbook_is_routed_as_an_atomic_leaf` | 迁移通过 | Requests retain a reason-to-request relation, flexible length and leave constraints. |
| `test_plan_construction_playbook_is_routed_as_an_atomic_leaf` | 迁移通过 | Plans keep their action skeleton distinct from research and feasibility decisions. |
| `test_remediation_plan_has_a_state_preserving_atomic_leaf` | 迁移通过 | Remediation retains state, bounded reasons and executable authorized future actions. |
| `test_request_review_checklist_is_routed_as_an_atomic_leaf` | 迁移通过 | Requests have a targeted review owner which preserves real internal templates. |
| `test_institution_rules_have_a_dedicated_routed_leaf` | 迁移通过 | Institutional variants keep rule structure, authority bounds and optional Word routing. |
| `test_news_message_uses_one_frontmatter_cluster_and_six_body_aliases` | 迁移通过 | News discovery stays compact while six aliases route and factual constraints survive. |
| `test_news_commentary_uses_clustered_frontmatter_and_precise_body_route` | 迁移通过 | Explicit commentary intent routes consistently; incidental words do not change genre. |
| `test_news_commentary_leaf_is_bounded_and_non_templated` | 迁移通过 | news commentary leaf is bounded and non templated |
| `test_news_genres_are_defined_in_authoritative_routing` | 迁移通过 | The routing tree distinguishes factual news, meeting records and commentary judgments. |
| `test_format_reference_clarifies_document_number_brackets` | 原样通过 | format reference clarifies document number brackets |
| `test_final_drafts_must_not_keep_unfinished_placeholders` | 迁移通过 | Final text clears placeholders while requested templates and missing dates stay honest. |
| `test_clawhub_v160_page_copy_is_kept_only_as_internal_history` | 原样通过 | clawhub v160 page copy is kept only as internal history |
| `test_openclaw_bundle_readme_is_current_and_contains_no_publish_command` | 原样通过 | openclaw bundle readme is current and contains no publish command |
| `test_readme_does_not_route_to_prompt_only_chatbot_repo` | 原样通过 | readme does not route to prompt only chatbot repo |
| `test_readme_documents_domestic_agent_install_paths` | 原样通过 | readme documents domestic agent install paths |
| `test_public_package_versions_match_skill_and_sync_script` | 原样通过 | public package versions match skill and sync script |
| `test_repository_and_current_packages_use_mit` | 迁移通过 | repository and current packages use mit |
| `test_lint_ci_invocation_stays_out_of_writer_context` | 原样通过 | lint ci invocation stays out of writer context |
| `test_revision_workflow_forbids_new_unprovided_facts` | 迁移通过 | Latest-source corrections remove unsupported facts and respect body-only delivery. |
| `test_staged_review_workflow_remains_intact` | 迁移通过 | Review covers local scopes and assembled drafts; old mandatory micro-stages are superseded. |
| `test_v140_mode_routing_material_mapping_and_format_bridge_are_documented` | 迁移通过 | Mode, material, semantic risk and Word bridges have separate owners. |
| `test_v141_formal_delivery_review_and_tone_rules_are_documented` | 迁移通过 | Unified review preserves scope, concrete advice and separate formal-format checks. |
| `test_v141_search_boundary_stays_lightweight_and_opt_in` | 迁移通过 | Spec replaces opt-in-only search with bounded research for unfamiliar writing needs. |
| `test_v144_common_real_writing_risks_and_adoption_gate_are_documented` | 迁移通过 | Field, length, evidence, format and maintenance constraints stay on their owners. |
| `test_candidate_ac_anchors_fact_relations_to_explicit_material` | 迁移通过 | Relations, incomplete dates and remainder arithmetic keep their original meaning. |
| `test_fact_sufficiency_guidance_is_soft_and_non_blocking` | 迁移通过 | Draft usable content now and carry only consequential gaps through permitted delivery. |
| `test_v147_minimal_borrowing_rules_stay_soft_and_prompt_based` | 迁移通过 | Formatting, formalization and evidence review stay contextual and do not overwrite sources. |
| `test_v148_anti_ai_borrowing_stays_soft_and_official` | 保留失败（1） | Rhythm advice is contextual and preserves genre, facts, subjects and technical names. |
| `test_v1601_j1_writing_endings_use_natural_terms` | 迁移通过 | Endings serve genre function; the rewrite permits natural wording instead of a word ban. |
| `test_v1511_anti_ai_frequency_review_is_prompt_driven_and_local` | 迁移通过 | Frequency discovers semantic risks; local repair preserves fact units and negative scope. |
| `test_continuous_negation_is_position_independent_without_word_ban` | 迁移通过 | Negation is evaluated by function regardless of position, with no token substitution. |
| `test_sustained_progress_example_is_removed_only_from_redundant_cliche_list` | 迁移通过 | Stock wording remains contextual; sustained progress is a clue, never a banned term. |
| `test_v150_genre_playbooks_keep_minimal_borrowing_boundaries` | 迁移通过 | Genre-specific field, actor and procurement boundaries survive mixed-page retirement. |
| `test_playbook_template_priority_uses_entry_semantics_without_leaf_duplication` | 迁移通过 | Template priority is carried by the entry, with no duplicated legacy boilerplate. |
| `test_work_summary_elaboration_stays_in_target_section` | 迁移通过 | Work summaries keep supported next steps without claiming unobserved effects. |
| `test_ordinary_letter_leaf_is_self_contained_without_default_supplemental_reads` | 迁移通过 | Ordinary correspondence preserves relational tone and optional handling fields. |
| `test_weak_model_suggestion_boundaries_stay_soft` | 迁移通过 | Suggestions and evaluations stay tentative through local edits and report routing. |
| `test_proofreading_layer_stays_ai_writing_quality_only` | 保留失败（5） | Language, quotation fidelity and consistency remain scoped; missing detail stays visible. |
| `test_formalization_keeps_only_explicit_literal_boundaries_verbatim` | 保留失败（2） | Ordinary speech can be formalized; explicit quotations keep a distinct literal boundary. |
| `test_v1510_sentence_fixes_keep_sparse_and_field_tasks_fact_bounded` | 迁移通过 | Sparse reports omit unsupported sections; fields change form only when they are source material. |
| `test_review_command_includes_interpreter_and_draft_path` | 迁移通过 | Run the documented standalone script invocation, including mode and stdin contract. |
| `test_ai_dedupe_prompt_fix_guidance_is_documented` | 迁移通过 | Dedupe never invents facts or missing fields; delivery notes stay outside the body. |
| `test_openclaw_agent_rules_include_v140_routing_and_format_bridge` | 迁移通过 | OpenClaw carries current mode, source, format and delivery routes without legacy workflow. |
| `test_openclaw_skill_card_source_is_tracked_but_not_packaged_directly` | 原样通过 | openclaw skill card source is tracked but not packaged directly |
| `test_openclaw_skill_card_uses_absolute_links_and_key_genres` | 原样通过 | openclaw skill card uses absolute links and key genres |
| `test_readme_summarizes_current_engineering_and_real_writing_evidence` | 迁移通过 | readme summarizes current engineering and real writing evidence |

## 验证命令与边界

- `python -B -m unittest maintenance.tests.test_skill_boundary`：81 tests，FAILED（failures=16）；无 errors/skip。运行中的 subprocess smoke 通过。完整命令运行结果与报告内存运行一致。
- `git diff --check -- maintenance/tests/test_skill_boundary.py`：通过；仅有 Git 的 LF→CRLF 提示，不是空白错误。
- 原检查点与当前 AST 的 test_* 方法集合比较：81 对 81，缺失集合与新增集合均为空；没有 expectedFailure、skip 或动态移除测试。
- 本次未运行 unittest discover、真实模型写稿或 Pro 生命周期测试：本子任务仅承担指定模块迁移，避免替根任务扩大验证范围。
- 未提交、未同步、未合并；output 下的报告通常被忽略，由根任务决定如何收录证据。
