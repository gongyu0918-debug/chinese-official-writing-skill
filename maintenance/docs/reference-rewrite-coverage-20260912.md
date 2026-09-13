# Reference 重写覆盖台账（2026-09-13，R6历史快照）

> 历史适用范围：本页保留R6阶段的构造、统计、原始判断和未闭合项。下文“当前”“本次”“尚未闭合”等措辞均指该历史快照，不表示当前canonical状态，不据此判定R16—R18之后的功能缺失或验收结果。
>
> 当前canonical在R19审稿页基础上采用R20入口与交付修正，完整指纹`a8f2f4694450e790bcc7129447f0ccac32cf5ef2bf227e7852604d714dfcddb5`；索引与文种页不变，12次原生中反例及执行缺口另保留。当前页集、结果与待办见[逐页架构归属](reference-rewrite-page-map-20260912.md)、[共性层进度](rewrite-common-layer-progress-20260913.md)和[R19整体完成度审计](../tests/evidence/completion-audit-r19/report.md)（[JSON](../tests/evidence/completion-audit-r19/report.json)）。逐页文件归属不代表逐条语义或实稿已闭合；R19审稿页已采用，Word输入修复也有独立证据，二者快照不同，详见当前进度；下方R6历史统计不追改。

后续判读修订见 [R7 联网与日期校准](../tests/evidence/rewrite-calibration-r7/result.md)：下文相对胜负为原始审阅记录，不等于已确认的规则回退；新原型和新增批次尚未计入 R6 产品收益。

固定旧版为 `main@1ce7112303172478faa2392667a2de1098eb912c`，工作分支为 `codex/reference-rewrite-20260912`。本历史台账的产品边界为 R6（产品检查点 `82ade47a`；`67d18296` 迁移旧测试职责断言；当时读取 HEAD `4bd62020`）。只汇总已落入 canonical 的规则与已归档证据，未采纳的 R7 原型不计入收益或闭合项。整体验收为 **HOLD**，未合 main、推送或发布。

## R6构造与旧页覆盖（原记录）

- 当前 72 个 reference、39 个主叶、41 条路线。固定旧版 50 页中，43 个同名路径仍在、7 个退役或迁出；新增 29 页（26 主叶、2 事务附加、1 交付），共 72 页。逐页来源、当前文件和废弃理由见[逐页映射](reference-rewrite-page-map-20260912.md)，机器允许/排除集合见[路由 manifest](../specs/reference-route-manifest.json)。这些计数证明文件和职责落点，不能证明模型每次按路由执行。
- 讲话/致辞/演讲、完整主持词、书面与现场述职、工作总结、工作要点已分别有主叶；周报/月报和情况综合归报告。决定、决议、议案、公报、命令、意见及部署按功能分开；通报独立于公告/公示/通告。
- 独立技术需求、独立审查意见和采购公告各有主叶。`genre-playbook-procurement-review.md` 是条件附加的采购专项核对页；AI 算力同样只作场景附加，普通服务器、接口、安全、SLA 或验收词不单独触发算力。责任书、倡议书、公开信、讲解、正式宣传材料已补确定入口，建议信归合作性建议。
- 共性页承担材料选择、论证、办理、语言、修改和复核；旧跨文种骨架及 workflow 流程副本退役。审稿统一到 review-checklist，纯审交位置/依据/建议，审后改交完整修改稿；默认独立文后提示，明确只要正文时省略。
- 普通产品保留 `draft_length.py` 和 `prose_lint.py`；篇幅、事实/文种、抗 AI 味、脚本、交付按首页顺序衔接。Hook、生命周期门禁和宿主适配迁到 [Pro 保存分支](pro-hooks-next.md)，普通脚本不具备最终消息生命周期门禁能力。

## 体量与口径

按换行归一后的 Unicode 字符计数，含 Markdown，排除脚本、Hook、维护 manifest 和镜像；是完整文件树体量，不是 token 或单次实际读取量。本次直接读取 canonical 复核，与已归档的 [size.json](../tests/evidence/rewrite-cold-r5/size.json) 一致。

| 范围 | 固定旧 main | R6 canonical | 变化 |
|---|---:|---:|---:|
| SKILL.md | 7,516 | 3,886 | -48.30% |
| reference Markdown | 84,899 | 59,778 | -29.59% |
| reference 页数 | 50 | 72 | +22 |

字符减少成立；是否减少无关伴读与重复执行，必须另据实际读取轨迹判断。

## 静态审计与工程状态

- [旧共性审计](../tests/evidence/rewrite-cold-r5/legacy-common-parity-r5.md)和[旧文种审计](../tests/evidence/rewrite-cold-r5/legacy-genre-parity-r5.md)分别核对 23 页、26 页，technical-terms 另有逐行相同记录。它们针对 R5 当时快照，属于静态语义对照，不是当前实写质量通过。
- [R5 汇总](../tests/evidence/rewrite-cold-r5/result.md)记载补回有据分析、既有字段形态、使用报告正反组织、消息内分析、条件可研建议与事务入口。[全文种冷审](../tests/evidence/rewrite-cold-r5/cold-all-genres-r5.md)逐页覆盖 72 个 reference，[工作流与脚本冷审](../tests/evidence/rewrite-cold-r5/cold-workflow-scripts-r5.md)独立检查 30 个共性页和两个脚本；未找到有明确指令证据的强制循环、主叶孤岛或产品内构建/发布命令。这不证明模型不会混读、重读或不交稿。
- R6 已归档的相关确定性检查：`python -B -m unittest maintenance.tests.test_reference_rewrite_contract maintenance.tests.test_promptfoo_eval maintenance.tests.test_draft_length maintenance.tests.test_review_regressions maintenance.tests.test_reference_uniqueness maintenance.tests.test_mit_script_boundary`，176 项通过。provider/contract 夹具 63 项及 DOCX 修复 107 项脚本/字数测试、4 项镜像边界按各自范围另记，不能相加为互不重叠的总成绩。DOCX 脚本修复提交 `d06d51f8`，包括后续页眉页脚扫描与缺少主文档报错。
- [旧边界迁移 R6](../tests/evidence/legacy-boundary-migration-r6/result.md)：`python -B -m unittest maintenance.tests.test_skill_boundary`，81 个方法全部保留；75 个方法通过、6 个方法有 12 个子断言失败，退出码 1。原 23 个失败方法/41 个子断言中 29 个子断言经职责迁移或语义纠正处理，其余继续暴露，没有删除、skip 或 expectedFailure。
- 早期[脚本与交付证据](../tests/evidence/mit-script-delivery-r1/result.md)中的 171 项聚焦通过，以及旧全套 386 项中 116 失败、25 错误，是历史快照。R6 的 176 项及单模块迁移没有覆盖或取代旧全套失败清单；当前全量合并门尚未运行。本次仅更新文档并检查链接/结构/字符数，不重跑模型、产品测试或全量门。

## 真实写稿：按组保留正反结果

[R5 汇总](../tests/evidence/rewrite-cold-r5/result.md)归档 122 次 native 调用，117 技术有效、5 无效，其中含此前 50 次 R4 调用。采购分工 8 对为候选 6 较好/1 较弱/1 相当；旧语义修复 10 对为 5/3/2；与旧 main 的事务/技术组合 16 项中 12 对可比，结果 1/3/8，另 4 项有无效臂。一份候选仅有预告没有正文。可研单段提醒试验仍有多段反例，未纳入 R6；历史较弱与未采纳试验均保留。

[R6 实写报告](../tests/evidence/rewrite-validation-r6/result.md)有六组 62 次 Codex CLI native 调用，61 技术有效、1 无效。完整终稿未清理旁白；绑定、原始轨迹、Word 与快照见该报告及 [R6 归档清单](../tests/evidence/rewrite-validation-r6/archive.json)。三类对照分别成立，不汇总成整体胜率：

| 证据组 | 实际对照与数量 | 候选相对结果 | 结论边界 |
|---|---|---|---|
| 冷审修复复验 | 冻结 R5 对 13 页局部修复包，10 对/20 次 | 2 较好、1 较弱、7 相当 | 建议信具体经历扩写减少；不是旧 main 整体比较，也不归功于后续 DOCX 脚本修复 |
| 剩余文种组合 | 旧 main 对完整 R6，12 对/24 次 | 7 较好、3 较弱、2 相当 | 批复、公告、通报、报告事务、投诉及平行回函出现相对改善；增项申请、整改方案、部署仍有较弱反例 |
| 已知反例复测 | 旧 main 对完整 R6，9 项/18 次 | 8 对可比为 1 较好、6 较弱、1 相当；另 1 项仅候选可评 | 候选均交完整稿，技术需求、讲解和部分公开信仍有事实/程序扩写；定向反例不代表随机总体胜率 |

技术有效只反映进程、最终消息和入口轨迹等基本条件，不能当作内容合格。审核校准允许有据原因、意义、风险、合理预期和拟议建议；需要限制的是缺少支持却写定的具体历史、现场特征、责任、技术实现或程序，不能机械要求每句在材料里有原文。

实际读取方面，普通服务器公告和技术需求在该组两侧均避开算力附加页，不能据此声称改后减少了多少误触；DeepSeek 采购公告仍读通用公告页，MiniMax 回函仍读批复页。部分任务重读首页不证明强制循环。两通道四份真实 DOCX 已保存并提取：DeepSeek 两侧均删除定稿数字周围空格，属于格式任务的文字范围偏移；GLM 两侧原样保留。未渲染，视觉版式未经验证。

## R6阶段尚未闭合（原记录）

1. 旧边界的 12 个失败子断言：声明/业务版本明示保留 2 项；主标题无句号、标题后空行、层级标题无句号及编号正文句末标点 4 项；渠道不推发文主体 1 项；Token 不改调用次数 1 项；成语同语境、的地得、量词 3 项；引用原文同语境保护 1 项。R7 原型尚未采纳，不能预记解决。
2. 旧页逐条功能与跨场景组合仍未全部闭合。敏感信息按接收/发布范围复核已有落点，但旧涉密人工复核专项未凭当前一般条款证明等价；细分能力须保留证据边界。
3. 技术需求、公开信、讲解的有据展开仍出现具体事实或程序扩写；增项申请、整改方案和部署等也有较弱样本。合理分析能力须保留，不能靠一概禁止推断消除问题。
4. 正文外技能/脚本/自评旁白、字段与状态扩写、局部修改范围失守、额外主叶读取及偶发不交正文仍需处理。临时稿扫描通过不证明最终消息合格，脚本返回也不能替代交付证据。
5. Word 文字保留存在通道差异且尚未渲染；当前未完成全量合并门，不以聚焦测试、文件覆盖或有终稿数量宣称整体不劣于旧版。候选保持 HOLD，合并与发布另据授权和完整验证判断。
