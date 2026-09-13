# 中文公文 Skill Reference 重构当前架构

更新时间：2026-09-13。本文记录冻结的 `output/reference-integration-r16/candidate` 及其待纳入维护适配，是维护索引，不是产品运行规则或完成证明。该候选有67个references、40个具名主叶；canonical与mirrors由主任务在真实结果核对后应用。本轮另有 `output/reference-integration-r16-rule-refinement/candidate` 的compression/news-commentary两页修正，同名prose_lint局部修复另行绑定，均不回写原组合快照。page map与route manifest用于维护核对，不能替代真实文件和写稿验证。

## 一、当前主线

当前运行顺序是：

```text
用户需求拆解
→ 选择一个主文种页或事务主叶
→ writing-rules.md：材料与分析、成稿与篇幅
→ 事实与文种复核、anti-ai-patterns.md、文稿扫描
→ writing-rules.md 的交付步骤
```

用户需求先拆为任务与交付件、稿件用途和主体对象、底稿与修改范围、篇幅与形式。随后保留用户限定的模板、最新版底稿、标题和字段，按本次实际用途选择主叶；标题固定不改变正文应完成的请批、汇报等功能。`reference-index.md` 是常规索引，`genre-routing.md` 只处理标题、模板、用途或行文关系冲突，兼容场景由专门分流页处理。用途明确但无适用专页时，`genre-checklist.md` 按模板、材料及已确认通用写法完成正文；陌生写法沿首页规则定向核查，不再回跳重选主叶。

起草、改写、压缩、审核和格式处理是同一文种上的任务动作。旧 workflow 的有效动作已进入入口、共性写作、结构编辑、字段编辑和压缩等现有页面。普通完整短稿保留自然段组织与80字要求，全部稿件使用同一共性主线；复杂材料按实际任务补充专项能力。

## 二、写稿、改稿和审稿的同文种衔接

- **写稿**：选定主文种或事务主叶后，读取 `writing-rules.md`；专项论证、格式和场景能力按任务叠加。
- **改稿**：沿用同一主文种和最新版底稿，按实际动作加读 `structure-editing.md`、`field-editing.md` 或其他必要页；语体与表达保真由统一的 `anti-ai-patterns.md` 承接。局部修改只检查改动及关联段落。
- **审稿**：仍先确定稿件所属主文种或事务叶，再叠加 `review-checklist.md`。只审时交付问题位置、风险和建议；审查并改稿时落实已确认问题并交付改后稿。

三类任务均使用 `writing-rules.md` 的编号流程：材料与分析；成稿与篇幅（适用时运行 `draft_length.py`）；事实与文种、抗 AI 味及适用校对，再按 `prose-lint-usage.md` 运行 `prose_lint.py`；最后交付。`information-selection.md`、`handling-elements.md`、`final-review-layers.md`、`delivery.md`、`task-route-cards.md`、`short-draft-naturalness.md` 的有效共性内容在候选中归并至 writing-rules；`official-style.md` 的语言与语义保真归 anti-ai。退役页在候选中撤下，legacy_coverage保留原来源，行文关系仍由 formal-addressing 承担。脚本结果、缺项和未处理风险按交付步骤处理，文后提示与正文分开。

## 三、五类规则页

“五类规则页”继续作为维护索引语义，按实际文件职责理解：

1. **文种页**：承担报告、请示/申请、通知、函、纪要、讲话、方案、制度、新闻等正文功能、骨架和本类状态边界。
2. **事务/场景页**：处理整改报告、反馈报告、意见建议、投诉反映、采购或其他稳定业务场景；有明确主文种时作为附加页，没有主文种的兼容材料才由专门事务主叶承担。
3. **写作流程页**：承担信息选择、办理要素、论证、结构、字段、压缩、语言和格式动作，不重新选择文种。
4. **复核流程页**：承担审核范围、事实与文种复核、抗 AI 味、校对和专项检查，不反向启动总路由。
5. **条件附加页**：只在稳定信号出现时补充算力、人物顺序、技术术语等能力，不替代主文种。

`reference-index.md` 和 `genre-routing.md` 提供选路支持；共性写作页承担统一流程和交付。页数减少与功能层次是两件事，写作和复核的相邻步骤可以在同一页中清楚组织。

## 四、单叶隔离协议

“单叶隔离协议”保留以下当前可执行约束：

1. 一项独立稿件只选一个必要主文种页或事务主叶；多份稿件逐份选路。
2. 共性写作及抗 AI 味检查统一执行；专项能力和场景附加页由当前任务决定，业务关键词结合用途判断。
3. 主叶负责本类功能，共性页负责跨文种动作；同一规则不在多页复制为不同强度。
4. 附加页和专项核对完成后沿共性步骤复核与交付；避免反复重选文种或在检查完成前结束。
5. 事实、合理分析、未定状态和实质缺项分别表达；推断的主体、范围和强度与材料及常识依据相称。
6. 页面职责由正文和路由清单维护，不要求每个产品页增加 YAML 页头、`allowed_reads`、`forbidden_reads` 或其他尚未落地的构建契约。

讲话、主持词和述职已分别有 `genre-playbook-speech-address.md`、`genre-playbook-meeting-host.md`、`genre-playbook-duty-report.md`。编者按已有独立 `genre-playbook-editorial-note.md`，由编发身份、编发目的和阅读方向成稿，按语与被编发正文分清。采购公告在同叶按征集响应、结果告知、终止等发布目的取要素，不强加另一目的的字段。函页按不相隶属关系与权限处理商洽、请批及审批答复，与上下级批复区分。既有原生复函额外读取等历史反例保留，修正落盘不等于单叶隔离全部达成。

## 五、路由清单

“路由清单”由两层组成：

- 产品内的 `reference-index.md` 给出常规用途的主叶和条件加读页。`genre-routing.md` 的重复文种表已在冻结候选撤去，保留功能、模板、行文关系及冲突判定；未覆盖功能页也不再复列主叶目录。
- 维护区的 `maintenance/specs/reference-route-manifest.json` 记录页面、触发信号、主叶、附加页、复核页和停止信息；本次按67个实际页面的命名链接重建读取集合，保留40个具名主叶。43条路线由40条主叶路线及整改报告、反馈报告、采购审查三条事务叠加路线组成；独立编者按是新增项，通报是补齐旧清单遗漏，不以固定计数代替实际路径。清单用于发现无关伴读、双主叶、循环和不可达页。

manifest 是维护快照，不是 Agent 每轮生成的交付模式清单，也不是“文件已列入即完成验证”的证明。其内容必须随最终应用的产品文件校准；冻结候选尚未应用时，针对旧canonical运行会出现预期差异，不能为通过测试回改产品。page map 中的 `rewrite`、`retain` 和 `delete` 仅表示架构处置，仍需结合逐页语义核验和真实写稿判断。

## 六、普通脚本与 Pro Hook

普通 MIT 产品当前保留两个相互独立的脚本：

- `chinese-official-writing/scripts/draft_length.py`：只在篇幅步骤按条件运行，提供正文计数。
- `chinese-official-writing/scripts/prose_lint.py`：在文稿复核步骤运行，提供确定性风险提示。

两者按不同阶段调用，不合并，也不具备 Agent 生命周期或强制交付门禁能力。Agent 仍需解释结果、处理已确认问题，并对修改后的相关内容复核。

Hook 核心、交付门禁、宿主适配和 `review_gate.py` 不在当前 MIT 产品入口或活动构建链中。保存资产位于 Pro 独立分支 `codex/pro-hooks-preserved-20260912@3b6f273b6ee4ea583e7c0ade8311ad1f262d7159`，状态与已验边界见 `maintenance/docs/pro-hooks-next.md`。保存分支的既有本地协议验证不能写成当前 MIT 已启用 Hook，也不能证明所有宿主生命周期已重新验证。

## 七、已建成与未验证

### R16 已纳入开发候选

- 当前入口已经按“需求拆解 → 主叶 → 共性写作及必要附加 → 复核 → 交付”组织。
- 常规索引、文种判定、主文种/事务页、共性写作、条件附加和复核均已有实现；交付与相邻共性步骤合在一页。
- MIT 产品保留 `draft_length.py` 与 `prose_lint.py`，Hook 资产已与普通产品分离并可在 Pro 保存分支追溯。
- page map 与 route manifest 已建立，可用于继续核对职责归属和组合读取。

### 仍未验证或未闭合

- 全部旧规则的逐条语义归属、所有页面冷审和跨场景组合真实写稿尚未闭合。
- 当前候选尚未证明与基线全量等价，也未证明无候选独有硬回退；静态文件存在、字符减少或单叶通过都不能替代组合验证。
- 编者按、采购公告用途、函的审批功能及重复路由表已应用，真实组合有双方优劣，不能据单项或结构减载宣布最终通过。
- 整包冷审的压缩有效下限、评论修改范围、行内代码制作残留，以及实际写稿发现的办理条件误报已修正。最新文件绑定为 `output/reference-integration-r16-adopted/adoption.json`；原快照与历史结果保持不变。
- 普通短稿、复杂稿、局部改稿、Word、脚本真实调用及正文/文后提示隔离仍需按当前 Spec 完成覆盖。

本次构造与验证证据：

- [完整候选构建记录](../../output/reference-integration-r16/build.json)及[组合实写预登记](../tests/evidence/integration-r16/preregister.md)：绑定各冻结组件，实写结果由主任务另行核对。
- [完整候选冷审](../../output/full-skill-cold-r16/report.md)及[两页规则修正记录](../../output/reference-integration-r16-rule-refinement/build.json)：区分静态发现、局部修正与针对性复验。
- [目录原型](../tests/evidence/genre-router-r16/preregister.md)、[采购/函用途原型](../tests/evidence/genre-purpose-r16/preregister.md)、[编者按原型](../tests/evidence/editorial-note-r16/preregister.md)与[共性归并边界原型](../tests/evidence/common-layer-r16-attribution/preregister.md)：保留单项来源及未闭合状态，不改历史证据。

`agent_writer.py`只是维护评测的预选上下文适配，本次仅将退役路径改向新owner；其确定性路由不能作为native读取证据。当前已同步五份仓库镜像，Word、旧1.x金线、最终候选的整体合并验收仍待闭合。

只有逐页语义、组合路由、真实写稿、脚本边界和正文洁净度均有匹配证据后，才能进入合并判断。
