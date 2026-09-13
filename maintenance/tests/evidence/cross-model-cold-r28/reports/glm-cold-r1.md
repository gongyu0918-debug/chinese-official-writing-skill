冷审完成。以下为中文审查报告。

# 规则冷审报告：current 2.0 对照 previous 1.x

## 一、覆盖范围与方法声明

按 [criteria.md](C:/Users/admin/AppData/Local/Temp/cow-r28-cold-mziawin2/workspace/criteria.md) 与 [manifest.json](C:/Users/admin/AppData/Local/Temp/cow-r28-cold-mziawin2/workspace/manifest.json) 执行：全文读取 current/SKILL.md 与全部 67 个 references（逐一通读，含交叉引用完整性校验，结果“无悬空引用”）；previous 按需对照——SKILL.md、reference-index、genre-routing、genre-checklist、genre-playbooks 枢纽及 3 个合并旧叶、9 个被删旧页（delivery-review-gate、final-review-layers、handling-elements、information-selection、official-style、review-direct-checklist、short-draft-naturalness、task-route-cards、workflow）全文读取，其余共有页先以变更规模核对、再对重点页逐行 diff（含 request、report 核对页、correspondence、procurement-review、speech-address、institution-rules、work-summary、news 两页、minutes、plan-construction、advisory-feedback、complaint-reflection、project-application、format-gbt9704、external-research、compression-details、proofreading-checklist、prose-lint-usage、argument-chains、formal-addressing、anti-ai-patterns、formulaic-language、ai-compute-docs 等）。按 manifest 许可读取 current/scripts 下两个普通脚本全文，并以标准输入做只读冒烟验证（两脚本实测输出与规则页描述一致）；未修改任何输入文件。agents/openai.yaml 与 LICENSE 不在 manifest 范围，未读；未联网、未调用子代理、未读其他评审。静态结论仅证明可达性与条件关系，不据此声称真实写稿胜率、成本或速度。

## 二、确定问题（3 项，均为轻度，可最小修复）

**1. 路由指向悬空：“编号检查步骤”无定义**

- 原句：[compatibility-scene-routing.md](C:/Users/admin/AppData/Local/Temp/cow-r28-cold-mziawin2/workspace/current/references/compatibility-scene-routing.md:21)：“选定主文种后按首页的任务规则写稿；完成稿件后执行编号检查步骤。”
- 证据：`rg` 全 current 仅此一处出现“编号检查”，无任何页面定义该步骤指什么；旧页原句为“继续按 `SKILL.md` 的任务模式和加载条件完成适用的写作与复核”，指向明确。
- 触发：任何经该页选叶的任务（新闻消息、新闻评论、意见建议、整改方案、投诉反映）读到“衔接写作与质量检查”节。
- 影响：执行者需自行猜测是指首页“写作与交付步骤”1—4 还是文稿扫描复核；属路由清晰度缺口，不产生错误规则。最小修复为将该句改回指向首页四步流程，一句话即可。

**2. 审稿意见输出包装的旧约束未迁移**

- 旧原句：previous/references/review-direct-checklist.md：“除非用户明确要求 Markdown，不用表格、加粗标题或多级标题包装。”另有 previous/references/review-checklist.md：“未用 Markdown `**` 加粗包装标签。”
- 现状：[review-checklist.md](C:/Users/admin/AppData/Local/Temp/cow-r28-cold-mziawin2/workspace/current/references/review-checklist.md:5) 仅要求“将问题定位到原句、段落、标题、字段或附件，说明依据”；全 current 无任何关于审稿意见本身包装格式的规则；[SKILL.md](C:/Users/admin/AppData/Local/Temp/cow-r28-cold-mziawin2/workspace/current/SKILL.md:63) 的 Markdown 规则只针对稿件正文。
- 触发：用户要求只审不改或点名范围审稿、且未指定输出格式时。
- 影响：审稿意见可能以 Markdown 表格/加粗/多级标题包装交付（旧版明确避免）；不影响意见内容正确性，属输出格式层的确定回退。最小修复为在 review-checklist 交付段补一句“未指定格式时用普通文本标签逐项输出”。

**3. draft_length 强制步骤无失败降级句**

- 原句：[writing-rules.md](C:/Users/admin/AppData/Local/Temp/cow-r28-cold-mziawin2/workspace/current/references/writing-rules.md:21)：“有篇幅要求（含上述下限）时，将稿件保存为临时文件……按实际上下限运行”；对照同页第 35 行“运行受限时完成可做的检查，如实记录未完成项”——该容错句仅覆盖第三步文稿扫描。
- 触发：环境无法运行 python 或脚本不可用，且稿件触发篇幅要求。注意“含上述下限”使每篇普通完整短稿（默认 80 字下限）都落入该步骤。
- 影响：规则层面存在无降级路径的强制工具步骤；实际影响轻（可人工计数），但与第三步的容错设计不对称。最小修复为补“运行受限时按同口径人工计数并如实记录”一句。

## 三、未证风险（静态无法证实发生与否，仅列触发条件）

1. **“结论限定尾句/编号疲劳”从页面层移入脚本建议**。旧 final-review-layers 原句“事实已经完整……不在句后追加对该结论的限定”“频繁`一是、二是、三是`……只有显得机械或不合文种时调整”。当前无页面文字，仅由 prose_lint 的 negative-boundary-tail、unresolved-conclusion-tail、frequent-list-markers 命中建议承载。触发：脚本运行受限（writing-rules 第 35 行允许降级）或命中被保留时，页面层无语义规则可依；正常路径脚本必跑，故仅为降级场景风险。
2. **复扫防循环句缺失**。旧 final-review-layers：“已判定保留的原句即使再次命中，也不循环修改。”当前 [prose-lint-usage.md](C:/Users/admin/AppData/Local/Temp/cow-r28-cold-mziawin2/workspace/current/references/prose-lint-usage.md:11) 只有“合理用语及引用经核对可保留”“最终采用已检查文本”。触发：复扫再次命中已保留项；当前文本不强制循环，但少一句显式防护。
3. **检索触发面较旧版放宽**。[SKILL.md](C:/Users/admin/AppData/Local/Temp/cow-r28-cold-mziawin2/workspace/current/SKILL.md:52) 与 external-research.md 新增“不熟悉的新文种、新材料类型、特殊事务场景，或需要核查通用写法、必备要素、正式格式和常用语”即定向联网核查（旧版仅“用户明确要求或时效事实”）。有“常规已知文种沿用已有路线”、一次补搜上限、来源核验约束兜底，且用户材料仍为准、不构成事实污染；但“不熟悉”取决于执行者自评，边界更宽，可能增加检索频次。
4. **“进行态归纳”案例细则删除**。旧 information-selection 原句“意见卡已经回收、由中心留存且中心负责汇总时，写‘中心正在汇总分析’，不另写‘尚无统计结果’”。当前 [writing-rules.md](C:/Users/admin/AppData/Local/Temp/cow-r28-cold-mziawin2/workspace/current/references/writing-rules.md:9) 仅保留概括原则“分清信息未给与业务未定、暂无结果与是否启动”。触发：材料同时给出已收集对象、责任主体与对应职责的组合；概括原则可推出同结论，但少了案例锚点，判断口径可能分化。
5. **reference-index 未列 format-gbt9704**。功能仍可达（SKILL.md 第 46 行直接点名叠加条件），仅当执行者习惯“只查索引找加读页”时可能漏加；索引页自身未承诺穷举全部资料，列为低风险观察。

## 四、旧清理规则的迁移分析（按要求分四种交付形态）

先区分两类 Markdown：规则文件本身使用 Markdown 语法（标题、表格、反引号、frontmatter）是规则载体，脚本对 `.md` 输入有 frontmatter 分隔线豁免，不会把规则文件语法误判为稿件残留；稿件中的 `**`、`###`、代码围栏、`---` 才是交付残留检查对象。旧清理规则来源共核对 6 处（previous/SKILL.md“正文不用 Markdown `**` 加粗、`###`、代码块或 `---` 横线包装；只有用户明确要求 Markdown 文档格式时才按其格式要求处理”；task-route-cards“Markdown 加粗、标题井号、横线等属于格式噪点”；short-draft-naturalness“不添加……Markdown 加粗、代码围栏或横线包装”；review-direct-checklist 与 review-checklist、proofreading-checklist、information-selection 的对应条目）。当前去向：

- **默认正式稿（纯文本）**：规则在 [SKILL.md:63](C:/Users/admin/AppData/Local/Temp/cow-r28-cold-mziawin2/workspace/current/SKILL.md:63)（默认纯文本标题/编号规范、“用户明确要求 Markdown 时使用对应格式”）+ [proofreading-checklist.md](C:/Users/admin/AppData/Local/Temp/cow-r28-cold-mziawin2/workspace/current/references/proofreading-checklist.md:7)“Markdown 残留是否符合交付形态”+ anti-ai-patterns 表达保真“纯文本和 Word 按已选交付格式检查空格、标点、编号与装饰符号”。路径：SKILL.md → writing-rules 第三步（必读 anti-ai-patterns，校对时加 proofreading-checklist）→ prose-lint-usage → `scripts/prose_lint.py --delivery-mode draft-body --structure --format`（脚本含代码围栏、横线、文后提示标题加粗等检查，实测可用）。
- **审后改稿**：[review-checklist.md:13](C:/Users/admin/AppData/Local/Temp/cow-r28-cold-mziawin2/workspace/current/references/review-checklist.md:13)“改后稿复核、意见写法、AI 味替代表达及文后提示，沿用共性写作页的相应规则”→ writing-rules 第 33 行“所有成稿、改后稿和审核任务读取 anti-ai-patterns”+ [prose-lint-usage.md:9](C:/Users/admin/AppData/Local/Temp/cow-r28-cold-mziawin2/workspace/current/references/prose-lint-usage.md:9)“审核收到的原稿仍用 draft-body，原文件保留，修改另存新稿”；改后稿作为拟交付稿件按 draft-body（带文后提示用 gap-note-allowed）复扫，残留清理同默认正式稿路径。
- **明确 Markdown**：唯一显式规则为 SKILL.md 第 63 行“用户明确要求 Markdown 时使用对应格式”；proofreading 的“符合交付形态”按该形态适配；脚本支持 `.md` 且豁免 frontmatter。与旧版口径持平（旧版同样只有一句条件许可，无 Markdown 排版细则页）。
- **Word**：[format-gbt9704.md:27](C:/Users/admin/AppData/Local/Temp/cow-r28-cold-mziawin2/workspace/current/references/format-gbt9704.md:27)“不得把 Markdown `**加粗**`、代码块或 `###` 标题标记原样带入正式 Word”+ 同页“（一）小标题。正文……”改为小标题独立成段的整理规则；路径为 SKILL.md 第三步“需要 Word、docx、GB/T 9704、红头或正式版式时叠加 references/format-gbt9704.md”。
- **文后提示分隔**：writing-rules 第 51 行“默认在完整稿件后空一行，以无编号‘文后提示’单列”（承接旧 information-selection“不用 Markdown 横线分隔”），脚本 external-note-boundary 检查提示区前的 `---`。

结论：旧清理规则除“审稿意见不用 Markdown 包装”（确定问题 2）外全部迁移且有明确落点；未发现把规则文件语法当作稿件残留处理的混淆。

## 五、实际改进（静态可证）

1. **一文种一主叶落地**。67 个 references 中 41 个 genre-playbook 单文种主叶，[reference-index.md](C:/Users/admin/AppData/Local/Temp/cow-r28-cold-mziawin2/workspace/current/references/reference-index.md) 逐一对应；旧版三层混行（genre-playbooks 枢纽 6 文种合 3 行骨架、genre-checklist 文种清单、formulaic-language 20 类直接叶）取消。旧 deliberation-deployment 拆为意见/决定/决议/议案/公报/命令/部署 7 个满页，notice-publication 拆为通知/通报/公开发布/采购公告，research-feasibility 拆为调研/可研。旧 genre-routing 的文种功能目录下放至各叶，genre-routing 收窄为冲突判定页，与 SKILL.md 第 33 行“有冲突时先读”的条件一致。无强制无关叶伴读：全部叠加页（transaction 两页、procurement-review、ai-compute-docs、speech-person-order、argument-chains、field-editing）均有明确触发条件，compatibility-scene-routing 第 3 行明示“按任务选读一个对应专页，不预读全部专页”。
2. **入口与必读链减负**（按字节数与页数静态计，不推断实际耗时）。SKILL.md 由 18680 字节降至 6025；删除了强制前置的 information-selection、文稿蓝图/段落地图（workflow）、task-route-cards 轻量卡层、final-review-layers 三层总审、review-direct-checklist（并入 15 行 review-checklist）、short-draft-naturalness、handling-elements 要素表、official-style 语气表。典型起草必读链为 SKILL.md+索引+主叶+writing-rules+anti-ai-patterns+prose-lint-usage（合计约 20—25KB），低于旧版 SKILL.md 单页加前置页的必读量。
3. **与用户标准逐条对齐**。writing-rules 第 7 行“材料与常识支持的原因、目的、影响、合理下一步、自然延续和结论可展开……现状与建议分清”落实“合理有据分析允许”；第 11 行落款日期规则与用户标准表述一致（未给日期补系统确认的当天草稿日期，指定留空/待定按要求保留）；第 51—53 行落实“默认文后提示、明确只要稿件时省略”；第 45—49 行交付消息旁白清理适用于整条消息（含开头、文后提示、结束语），对应“正文外且隔离的旁白不计正文回退、正文内污染要处理”的执行细则。genre-playbook-request 将旧“材料只写设备老旧不推成运行缓慢”改为“可对日常使用需要作一般判断；具体故障、损失、政策条款、采购程序或审批结论仍以材料为准”，属授权放宽而非事实边界失守。
4. **工具链与规则页一致（实测）**。draft_length.py 支持 `--min-chars/--max-chars/--count-mode cjk/--json`、标准输入 `-`、`.txt/.md/.docx`，统计口径为“文后提示”之前，与 writing-rules/compression-details 描述一致；prose_lint.py 支持 draft-body/gap-note-allowed/review-only/generic 四模式、标准输入、`.md/.docx`、frontmatter 豁免，与 prose-lint-usage 一致；两脚本标准输入冒烟验证通过。
5. **事务场景路由互斥清晰**。reference-index 第 38—39 行：意见建议/投诉反映/整改方案经 compatibility-scene-routing 分流；整改进展报告＝报告主叶+transaction-remediation-report，反馈报告＝报告主叶+transaction-feedback-report，“两者不改用整改方案或合作性意见建议骨架”，堵住旧版骨架混用。
6. **防循环/防编造约束完整迁移**。external-research 保留一次补搜上限、URL 逐字使用、命中页未实际打开不得称已核验；format-gbt9704“不得编造文号、密级、紧急程度、签发人、印章”；field-editing、structure-editing 与旧版逐字持平；新闻消息的声明级核验规则（不外推“截至发稿未见”、不自建机构序位）完整保留。
7. **重复与冲突检查**。未发现页面间规则冲突；“报告不写请批语”等少数规则在称谓页、用语页、主叶、复核页、路由页多处出现，属各叶自足设计的同义重申且语义一致，未见因单次不遵循而追加的重复规则；未发现构建/维护约束泄入写稿规则链（README 的开源署名与 Pro 分线内容仅在能力咨询路径读取，与旧版结构一致）。

## 六、无需恢复的旧约束

1. delivery-review-gate 全部有限状态机/一次性门禁协议：旧页自声明“普通 SKILL.md 不加载本页”，且其引用的 scripts/review_gate.py 在 previous/scripts 中本就不存在；属 Hook 产品线，按用户授权移出（README“Hook 后续归 Pro 专属能力，普通版保留独立运行的检查脚本”），普通版无功能损失，不当作隐性回退。
2. task-route-cards 四类轻量卡及“卡片覆盖即止”机制：已被更薄入口+单叶替代，恢复只会多一层路由。
3. short-draft-naturalness 独立短稿页：核心已并入 writing-rules“完成文种动作即可收束……上限无需填满”及 news-message 等叶的短稿规则。
4. workflow 的文稿蓝图/段落地图/急件专节：蓝图步骤与 README“不必先填完要素核对卡”的产品定位相悖；急件中“不编造紧急程度”已在 format-gbt9704，“先形成可报送正文”已在 writing-rules 第 13 行。
5. information-selection 作为强制前置页：保留原则并入 writing-rules 第一步，文后提示格式细则由 writing-rules 与脚本承载。
6. official-style 轻量语气替换表：口语转正式语体原则保留于 anti-ai-patterns 表达保真及脚本 casual 规则。
7. review-direct-checklist 作为独立定向审稿入口：并入 review-checklist（“审核默认检查全文；用户限定范围时按其要求”），除确定问题 2 的输出格式句外无需恢复。
8. handling-elements 文种要素表：要素已分入各主叶的骨架与专项核对节。
9. 旧 ai-compute-docs 的三种文种结构（算力可研/采购租赁方案/技术需求）：已拆至 genre-playbook-feasibility、plan-construction、technical-requirements，ai-compute-docs 收窄为场景附加规则，与 SKILL.md“主文种继续承担文种路由”一致。

## 七、结论

current 2.0 的重构方向（一文种一主叶、薄入口、共性写作页收口、脚本核验闭环）与 criteria 用户标准一致，旧约束迁移基本完整；确定问题仅 3 项轻度缺陷（一句话级可修复），无死循环、无普遍漏读、无页面冲突、无构建约束泄入。必要修改限上述 3 处最小可归因范围，各补一句即可，不改产品与文件结构。