# R20 旧测试责任迁移结果

当前 81 个方法均有通过证据，未解的静态失败方法为 0。本轮迁移 50 个方法，另外 31 个方法不变，方法名、版本常量、显式两跳路由 helper 和 R18 两个真实 CLI 方法均保留。没有删测试、skip、expectedFailure，也没有修改产品来满足旧句。

这项结果是文档、路由、镜像及普通 CLI 契约通过，不能解释成 81 项真实写稿能力全部验收。未验证的具体实稿责任列在后文。

## 验证及快照

开始时 HEAD 为 `95e29838e7f8cf4ef54c7433870eb5d8ab214458`，工作树干净。范围仅为 `maintenance/tests/test_skill_boundary.py` 和本证据目录。产品、镜像、版本常量、其他测试未由本子任务修改；父任务并行修改的规格/进度文件和 `review-boundaries-r20` 不属于本次改动。

| 快照 | SHA-256 |
| --- | --- |
| 原测试副本 | `5c36737545e84d0a04ddcca17d2107ec564484904050f0db01195d7851713233` |
| 唯一一次完整模块运行的测试文件 | `ff1cb058268fbac51c4895c98a39e0f848cb324449199327ba8234e35e4145e0` |
| 最终测试文件 | `5b3f8bdd9775c4539269520d70ac3e0571059f9b02fe165a97c448f8dadd92f5` |

完整模块只执行一次：

```text
C:/Users/admin/AppData/Local/Programs/Python/Python313/python.exe -B -m unittest -v maintenance.tests.test_skill_boundary
```

结果：`Ran 81 tests in 0.838s / OK`，进程退出码 0，0 failure、0 error、0 skip。日志为 `module-python313.log`，执行元数据为 `module-run.json`。使用显式 Python 3.13，没有调用 PATH 中缺 yaml 的 Python，没有安装依赖。

完整运行之后，复查旧短稿页的“整稿代码围栏/横线包装”责任，确认产品脚本 `format_marker_findings` 仍有对应检测。因此只给 `test_long_form_headings_warn_against_markdown_bold` 增加 3 个真实 CLI 正反例：代码围栏、正文横线、无包装正常正文；分别核对 `markdown-code-fence`、`markdown-horizontal-rule` 及无这两类提示。

仅复验这个方法：

```text
C:/Users/admin/AppData/Local/Programs/Python/Python313/python.exe -B -m unittest -v maintenance.tests.test_skill_boundary.SkillBoundaryTests.test_long_form_headings_warn_against_markdown_bold
```

结果：`Ran 1 test in 0.400s / OK`，退出码 0。没有再次运行 81 方法模块。`audit.py` 用保存的完整运行 hash 还原并校验当时测试快照，AST 比较确认最终文件仅此一个方法在完整运行后改变，其余 80 个方法完全一致。因此最终通过数 81 的依据是“一次完整运行 + 唯一后改方法复验”，不是声称最终 hash 又跑过整模块。

R18 的两个 CLI 方法原样保留，完整模块执行时实际运行了 2 个 `draft_length` 与 3 个 `prose_lint` subprocess：保留 nonspace=8/cjk=2、stdin、JSON、指定上下限、正文与文后提示隔离、三种交付模式以及结构/格式参数。本轮合计 8 个 CLI 输入案例，没有模拟 subprocess 返回值。

`git diff --check -- maintenance/tests/test_skill_boundary.py` 通过。`audit.py` 的方法集合、50/31 改动划分、helper/CLI/常量不变、日志 hash、两阶段测试文件绑定及产品/镜像无差异检查通过。准备迁移时修复过证据生成脚本的 CRLF 缩进和快照还原空行错误，均在证据断言阶段发现；它们没有运行第二次完整模块，也未写入错误产品内容。

## 责任如何承接

逐方法说明在 `method-migration.md`，机器可读表为 `migration-catalog.json`。每项保留原方法名，记录责任组、调整理由、当前明确页及测试行号。原模块副本和 `module-tested-before-wrappers.py` 可对照具体旧/新断言。

| 责任组 | 当前保护的内容 | 不再作为现行要求的部分 |
| --- | --- | --- |
| G01 通知角色 | 通知对象保留原称谓，落款/文号采用已有信息；参加、报送等动作须材料明确；审核分别核对发文主体和动作主体；已挂接 R18 `notice_receiver` 同题四稿正证 | 不要求通知页必须再次写旧邮箱反推例句，也不重跑已经覆盖的接收方/发文主体题 |
| G02 算力单位 | 算力页分别列 Token、调用次数、用户数、并发；单位保持一致，Token 主线承接费用，承载性能不混作 Token 单价；已挂接 R18 `compute_units` 同题四稿正证 | 不在术语拼写页强求 Token/调用次数整句；本题单价未给，不能推广成实际金额或混合费率换算通过 |
| G03 标题编号 | 主标题独行、行末无句号、标题后空行；层级标题与统领正文分开；完整编号句保留句末标点；模板/明确 Markdown 例外；Word 标题标记清理；整稿围栏/横线实际检测 | 不依赖退役短稿页，也不以 Word 标题规则代替纯文本标题责任 |
| G04 语言保真 | 成语按原语境保留，误引/搭配/语境错误才改；引语/逐字原文保留字面与语境，授权改写例外；的地得按句法、量词按对象、低把握保留并核查；正式化保身份、条件、否定范围、先后及强度；必要否定与独立办理例外 | 不要求保留旧套话清单位置、机械次数、固定口语例句和“持续推进”词禁；持续推进缺主体期限时的处理转到申请细查页继续检查 |
| G05 CLI | R18 的 5 个真实调用保留，额外 3 个包装检测正反例 | 不用命令文字出现替代真实执行 |
| G06 多轮与事实 | 本轮有效材料/最新版及更正；旧稿样文/模型补写重新核依据；不回退旧主送、落款、标题；结构动作、句段节粒度、删除完整单元、禁止换词回流、主体变化同步；缺信息/业务未定、暂无结果/是否启动、合计差额/其余正常明确分开；未解问题文后接续 | 不强制内部映射表形式；来源限定不等于禁止合理分析；缺落款默认省略已由当前确认当天草稿日期及指定留空规则替代，业务日期与正式签发边界仍保留 |
| G07 镜像/路由 | 六个根分别读取自身明确路线、当前共性及审稿/语言/扫描页；入口→索引→兼容页严格两跳；原资源镜像、元数据、历史卡及版本测试不删 | 首页不再必须直链所有共性细项；不把历史平台卡当当前加载规则 |
| G08 文种条件 | 报告细查条件/状态/接口原词；请示申请理由与请假特殊条件、主送/主体、未定后续；纪要归属/待议及责任期限不代填；制度权限/例外与通知附件；函件商洽/请批/审批答复权限与条件反馈；采购的响应期限、提交方式、联系方式及缺项按发布目的保留；评论时间锚/约数篇幅/推演范围；外搜触发/来源用途/一次补搜及停止 | 取消短材料卡片终点和按长短新增通用分流；直接使用已选主文种及统一共性流程。函的反馈字段按实际目的触发，请批语也适用于请求批准的函 |

主要迁移使用含条件、动作、对象或例外的规则片段，保持所属页明确；没有搜索任意页来凑通过，也没有仅用 manifest、页名或一个关键词替代全部细项。现有 `test_reference_rewrite_contract.py`/`test_reference_uniqueness.py` 用于辨认既有覆盖，未在本轮额外运行。它们不替代本模块的标题、语法、底稿动作及 CLI 专项。

## 已有实稿及仍未覆盖的责任

**证据状态更正：此前报告遗漏了 R18 已有证据，把 G01/G02 继续列成未补实稿，这一判断已撤回。** 已实际核对两批 `binding.json`、八份完整 final 及对应 result，实际 case 名是 `notice_receiver`、`compute_units`，不是 `scope_compute_cost_units`。它们已被 R19 completion audit 明确接入旧 G01/G02 责任，不需要重新运行。

| 已有同题证据 | 实际输入与覆盖结论 | 范围限制 |
| --- | --- | --- |
| G01 `notice_receiver`，Qwen m0、DeepSeek m2，各 baseline/candidate，共 4 稿 | 输入为各业务科在 9 月 20 日前，将报名表发至市培训中心邮箱 `pxzx@example.org`，王老师接收，发文单位和成文日期还没有给。4 稿均把市培训中心用于接收邮箱/联系语境，没有反推为发文落款，业务科、邮箱、联系人仍保留。 | 此项正证只支持接收方不充当发文主体。Qwen 候选增加“组织填写”，两通道存在日期/落款占位、额外提示和明显旁白，不能一并算作合格，更不能推广成所有主体歧义场景均通过。 |
| G02 `compute_units`，Qwen m0、DeepSeek m2，各 baseline/candidate，共 4 稿 | 输入为试用期调用模型 1200 次、输入输出合计 800 万 Token，按 Token 计费，单价及总额尚待核实。4 稿分别保留 1200 次与 800 万 Token，未将两种计量互换，保留按 Token 计费和单价/费用总额待核，未代填金额。 | 没有已知单价，因此不覆盖实际金额乘算、输入/输出不同费率、币种或计量倍数换算。基线及部分候选的额外计费依据、服务周期或假设费用仍需独立评价；不把本题核心口径通过扩大为全部费用叙述通过。 |

八份 result 均 `returncode=0`、`invalid=[]`。Qwen 通道为 `alibaba-token-plan/qwen3.8-flash`，DeepSeek 为 `command-code/deepseek-deepseek-v4.1-flash`。两批四个题臂的完整路径、final/result SHA-256、原始提示和冻结指纹已写入 `summary.json` 的 `existing_native_evidence_binding`；原生成果没有编辑。

证据入口：

- `maintenance/tests/evidence/common-compression-r18/results.md`：已明确记录通知不反推主体，以及次数、Token、费用待核状态保留。
- `maintenance/tests/evidence/completion-audit-r19/report.md`：通知映射与第 1 项补齐顺序明确 G01/G02 已有 R18 同题正证，不重跑。
- `output/common-compression-native-r18-qwen/binding.json`，对应 `m0-notice_receiver-{baseline,candidate}.final.txt`、`m0-compute_units-{baseline,candidate}.final.txt`。
- `output/common-compression-native-r18-deepseek/binding.json`，对应 `m2-notice_receiver-{baseline,candidate}.final.txt`、`m2-compute_units-{baseline,candidate}.final.txt`。

仍保留的证据边界：

1. **G04：具体口语正式化样例。** “老板关心”“钱花得值”“马上要搞”等原例的身份、评价、程序及承诺强度已有通用语义保护；本次未核对这些具体样例的原生输出，不能宣称逐例验证完成。
2. **G03/G04/G06/G08：生成时的实际遵循。** 本次文档断言与 8 个 CLI 输入不替代其他真实写稿证据。应继续按既有场景映射核对复杂上下文中的主体、状态、旧稿回流和缺项范围，不能因为本模块不运行模型，就把已有实稿一律标成未验证。

这些是证据边界，不是新增能力清单或待恢复的旧措辞。本轮没有为过绿修改产品，也没有继续追求字符减少。R18 正证只绑定其原冻结任务，不追认后续尚未采用的导航原型或其他规则组合。

## 未采用导航原型对旧句断言的静态影响

只读对照 `output/delivery-narration-r20-navigation/{baseline,candidate}` 的两个差异文件：候选 `SKILL.md` SHA-256 为 `90def8e990a93be1d79fda4156db0f744064b7be08e139d17aed05b93d4afe1b`，候选 `references/writing-rules.md` 为 `6265022ba67e9d9738ed55a3f1b013bfbe9ec1f8f4cc81195bf37ee0775b5c0f`。这是静态影响清单，没有运行原型测试，没有把当前断言改成未采用规则。

| 当前方法 | 行号 | 会失配的旧句/位置要求 |
| --- | ---: | --- |
| `test_canonical_skill_declares_positive_trigger_boundary` | 123 | 要求首页仍有“读取 writing-rules 完成取材、成稿、复核及交付”旧句；原型改到末尾四步导航 |
| `test_delivery_scope_rule_is_naturalized_across_current_skill_copies` | 225 | 要求“正式正文清除 AI 身份……”整句出现一次；原型改为四组禁令 |
| `test_drafting_rules_are_split_for_prompt_following` | 254 | 要求第三步 section 内立即出现“选定主文种后，读取 writing-rules”；原型把流程入口移至末尾。251 行按 `## 路由主线` 截段也不再有相同边界，但 split 本身不报错 |
| `test_second_revision_fact_mapping_has_one_complete_entry_rule` | 309 | 要求共性页含“路由、工具过程与自评留在内部”旧句；原型改成内部过程说明与完整消息禁令 |
| `test_reference_loading_table_keeps_progressive_disclosure` | 390 | 要求“选定主文种后，读取……完成取材、成稿、复核及交付”旧句 |
| `test_light_route_is_terminal_until_an_explicit_escalation_condition` | 487 | 要求“选定主文种后，读取 writing-rules”旧连接句 |
| `test_revision_workflow_forbids_new_unprovided_facts` | 945 | 同样要求“路由、工具过程与自评留在内部”旧句 |

共 7 个现有方法命中旧句/位置差异。若只修改 canonical 而不同步镜像，还会有入口/资源同一性检查失败，那属于同步差异，不能算导航语义损失。检查过的两个 reference 测试模块未发现同类旧整句被这两个差异直接移除；这不是测试通过声明。原型采用与否、行为是否改善仍由主任务证据决定。

此次更正仅更新本报告和 `summary.json` 的证据衔接，测试文件 SHA-256 仍为 `5b3f8bdd9775c4539269520d70ac3e0571059f9b02fe165a97c448f8dadd92f5`，没有新测试或模型调用。`audit.py` 是首次收束时的历史生成脚本，其 G01/G02 初始 pending 文案已由本节和 summary 中 `evidence_correction` 明确取代；未重新运行该脚本覆盖本次更正。

R17 原日志 SHA-256 仍为 `7833d5d508919da66dba978374db4dba25da58c6d8aba6892dea5c12cef624c8`，未覆盖。R17 的 78 failure + 35 error 是 subtest 事件，不是 113 项能力失败；R18 的 50 个受影响方法、76 failure + 34 error 也是历史状态。本轮记录在独立目录，不把环境失败日志混入。

未运行模型、未运行全仓套件、未 commit。父任务后续可按范围审阅并统一提交。
