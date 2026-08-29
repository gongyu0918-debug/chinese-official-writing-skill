# 中文公文写作 Skill

[![Version](https://img.shields.io/badge/version-1.6.20-blue)](https://github.com/gongyu0918-debug/chinese-official-writing-skill/releases/tag/v1.6.20)
[![ClawHub](https://img.shields.io/badge/ClawHub-chinese--official--writing-2f80ed)](https://clawhub.ai/gongyu0918-debug/skills/chinese-official-writing)
[![SkillHub](https://img.shields.io/badge/SkillHub-chinese--official--writing-e8590c)](https://skillhub.cn/skills/chinese-official-writing)
[![SkillHub downloads: 50k+](https://img.shields.io/badge/SkillHub%20downloads-50k%2B-2f855a)](https://skillhub.cn/skills/chinese-official-writing)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

中文公文写作 Skill 面向正式材料起草、改写、压缩和复核，提供文种路由、行文关系判断、办理要素核对、论证链条、标题核验、重复事项检测、主体视角校验、自然表达审查和技术类材料专项约束。它先判断创作、修改、只审不改或排版交付，再按任务加载轻量卡、文种 playbook 和专项资料，让事实、文种、格式与交付方式保持在同一条写作链上。

事实、数字和事项状态以用户材料为准；用户已有模板、标题顺序、字段结构和最新版底稿优先保留。成稿以正式、平实、可执行为主，兼顾公文语气、自然表达和低 AI 味。

本项目提供写作和复核辅助；法律、财务、采购、审计、政策适用、保密审查和正式签发结论由相应责任主体确认。项目面向来源明确的实际写作任务，不面向批量语料生成、批量改写未知来源文本、规避人工审核或生成可冒充真实签发文件的完整编号、日期和印章信息。

## 核心能力

- **文种与行文关系**：区分法定公文、事务文书和工作材料，按上行、下行和平行关系控制语气、结构与办理要求。
- **事实与模板边界**：锁定主体、数字、日期、责任、期限、附件和事项状态，保留用户模板、字段顺序与最新版底稿。
- **办理要素与论证链**：按请示、报告、通知协调、方案建设、可研审查和技术材料选择相应的办理要素与论证路径。
- **制度类专项路由**：按制度、规定、办法、实施细则和操作规程选择连续条文、章条结构、职责程序及印发附件关系。
- **新闻与评论写作**：覆盖新闻稿、新闻消息、快讯、活动报道、新闻通稿、新闻评论、时评和评论员文章，区分事实报道与观点表达。
- **渐进式路由**：短任务使用轻量卡，完整公文进入对应文种叶子，技术类材料按需加载专项规则。
- **创作、改稿与复核**：分别处理从零起草、基于底稿修改、只审不改、压缩和 Word 正文衔接。
- **轻量审查**：分层核对事实、视角、标题、格式、重复事项和模板化表达，并提供可选的确定性风险线索。
- **技术材料专项写作**：覆盖 AI 算力、GPU/服务器租赁、成本比较、SLA、并发、安全、运维和验收。
- **多平台适配**：同一 canonical 技能包同步到 Codex、Claude Code、WorkBuddy/CodeBuddy、Hermes、Qwen Code、QwenWork（Qwen 办公）、OpenClaw 和通用 Agent Skills 目录。

## 适用范围

| 场景 | 主要内容 |
| --- | --- |
| 法定公文 | 通知、请示、报告、函、批复、意见、决定、公告、通告、公报、通报、议案、决议、命令（令）、纪要 |
| 事务与工作材料 | 制度、规定、办法、管理办法、实施细则、操作规程、说明、申请、复函、公示、征求意见函、工作要点、总结、调研报告、讲话稿、致辞、述职报告 |
| 新闻与评论稿件 | 新闻稿、新闻消息、快讯、活动报道、活动新闻稿、新闻通稿、新闻评论、时评、评论员文章 |
| 方案与审查材料 | 实施方案、建设方案、可研报告、采购公告、审查材料、项目论证和办理要素核对 |
| 技术类正式材料 | AI 算力服务可研、GPU/服务器租赁、模型服务需求、成本比较、SLA、并发、安全、运维和验收 |
| 改稿与复核 | 润色修改、压缩、去口语化、降 AI 味、文种校验、格式核验、只审不改、Word 正文衔接 |

## 它怎么解决这些问题

普通写作提示往往只告诉模型“写一份报告”或“改得正式一点”，文种、主体视角、事实状态、用户模板和交付方式容易在长稿或多轮修改中互相挤占。这个 Skill 把写作拆成一条可检查的链路：

任务模式 → 文种与行文关系 → 办理要素 → 轻量卡或文种叶子 → 正文 → 分段、小节和全文复核。

- 确定任务模式：区分从零起草、基于底稿修改、只审不改和 Word/排版衔接，避免审稿任务被改成重写。
- 确定文种功能：按上行、下行和平行关系选择语气、结构和办理要素，请示与报告、函与复函各走自己的规则。
- 锁定事实状态：金额、日期、主体、责任、期限、附件和联系人按已确认、未决、缺失分别处理，用户模板和字段顺序优先保留。
- 材料暂缺时正文优先完成，影响执行的必要缺口放在文后简短提示；后续轮次继续执行新的修改要求。
- 成稿后进入轻量审查层，依次核对事实、文种、标题、格式、重复事项和模板化表达，局部修正已经确认的问题。

## 实现与技术栈

这是一个 Markdown-first 的 Agent Skill。核心规则和 references 全部使用中文 Markdown 编写，不懂代码也能直接阅读、审查和修改。通用 YAML frontmatter 只保留名称、触发描述和标签；版本与许可由发布包和宿主 manifest 承担。Python 只承担可选的确定性检查；各平台适配包从同一 canonical 技能目录同步，正文规则保持一致。

| 组成 | 作用 |
| --- | --- |
| `SKILL.md` | 判断何时启用、选择任务模式，并给出事实、输出和复核主流程 |
| `references/task-route-cards.md` | 为稀疏说明、未决纪要、短通知和二次局部修改提供轻量路径 |
| 文种与专项 references | 按需补充文种骨架、办理要素、论证链、GB/T 9704 格式和 AI 算力材料规则 |
| 分层复核 references | 从段落、小节到全文检查事实、视角、结构、格式和自然表达 |
| `scripts/prose_lint.py` | 提供可选的格式、重复和成品残留线索，作为轻量审查层的确定性补充 |
| 可选交付 Hook | 一份门禁核心配合 Codex、Claude Code、WorkBuddy/CodeBuddy、ZCode、Qwen Code、Kimi Code CLI、OpenCode、Hermes Agent 与 DeepSeek Harness 静态适配层；由用户明确启用，未通过时优先保留完整初稿；各宿主只承诺其已验证生命周期 |
| `agents/openai.yaml` | 提供界面展示和默认调用信息 |

渐进式路由让短任务只读取轻量卡，完整公文再进入相应文种叶子，技术类材料只加载命中的专项规则。这样既保留必要边界，也减少无关规则对真实写稿的干扰。

## 快速安装

当前 GitHub 发布版本：`chinese-official-writing@1.6.20`。

平台入口：[ClawHub](https://clawhub.ai/gongyu0918-debug/skills/chinese-official-writing) · [skillhub.cn](https://skillhub.cn/skills/chinese-official-writing)。通用 Agent Skills 安装器可直接使用：

```powershell
npx skills add https://github.com/gongyu0918-debug/chinese-official-writing-skill --skill chinese-official-writing
```

QwenWork 可使用 [`packages/qwenwork/`](packages/qwenwork/) 中的无 Hook 静态 Skill 包；个人安装目录与组织 ZIP 结构见该目录说明。

## 模型消融与真实写稿

下表只保留最近 5 次版本验证。原始任务、成稿、匿名映射、独立复核和完整发布记录保存在 `maintenance/`。

| 调试方向 | 主要稿件与边界 | 当前证据 |
| --- | --- | --- |
| 1.6.20 新闻完整日期写后修复与 Hook 使用顺序 | 对唯一完整来源日期、唯一目标新闻文种做 Stop 前机械补年；多日期、非新闻、歧义材料和其他 capability 均旁路；Hook README 先说明安装使用，再列彻底删除 | 三 provider 九次 Claude Code 真实生命周期中3次精确修复、3次目标稿自然正确、3次控制逐字不变；Alibaba Token Plan 2 与 OpenCode Go 达到预登记门。四个 references 减载原子经五路190次真实任务后全部拒绝并恢复产品字节；ClawHub 仍发布无 Hook 包 |
| 1.6.19 Hermes 与 DeepSeek Harness 有界适配 | Hermes 0.20.5—0.20.6 只支持新建且不可恢复的单题；DeepSeek Harness 0.1.1-rc.2 只支持 Windows headless Profile Bundle 与 `delivery_review` | Hermes 完成采购、情况说明和固定失败稿的真实生命周期；DSH 用 Alibaba 与 OpenCode Go 两份当前 Skill 真稿闭合多 Stop、终稿 hash 与脱敏；交互、恢复、one-shot/gateway、TUI/Web、POSIX 和其他 capability 不外推；不改写作规则或 references |
| 1.6.18 OpenCode 交互 Hook 与宿主边界 | OpenCode 1.18.23 常驻交互模式把 `session.idle`、同一 session 续写与共享门禁连接起来；无头 `run` 明确旁路，Hermes 同步变换未复现可安全机械处理的真稿目标 | 三份同稿原型均有目标修正，其中采购申请、情况说明解决目标，活动新闻仍保留包装风险；Alibaba Token Plan 2 的320字符采购申请完成回合重绑、单所有者、终态脱敏在线闭环；不改写作规则或 references |
| 1.6.17 写稿稳定性与状态收口 | 分开验证持续动作、证据未附、短采购原因与影响、长报告结论范围；没有跨模型共同目标失败，不新增写作规则、Hook 或统一篇幅门 | `WR-014-R6/R6b`、`WR-013c`、`WR-020a2` 完成预登记真实写稿；Ollama 单家状态外推、长稿技术失效和无 Hook 直写包装作为残余风险保留 |
| 1.6.16 算力可研状态与点名完整性审查 | 既有可研摘要的点名核对停在窄审查叶；允许核算已给数据、说明缺项影响并提出一层条件性研究意见，不把未决事项写成已启动程序或反向条件结论 | `OC-003` 先完成状态分层，再经五路真实审稿验证成本、技术指标、验收主体与依据四项均可达；公开版不增加程序模板、数值阈值或新 Hook |

### 制度正文示例

以下脱敏示例展示制度类材料如何保留职责、时限和状态边界，不以补足篇幅为由增加程序、承诺或免责声明。

```text
明川市政务服务中心服务事项信息变更管理办法（试行）

第一条　本办法适用于市政务服务中心综合窗口办理的服务事项信息变更。本办法所称服务事项信息，包括事项名称、申请材料、办理时限、办理方式、咨询电话等。

第二条　服务事项信息变更由业务科室提出。业务科室应当填写服务事项信息变更单，写明变更内容、变更理由和拟生效日期。变更涉及增加申请材料、延长办理时限或者暂停办理的，应当同时附业务主管部门书面意见。

第三条　运行管理科负责对变更单进行核对，核对内容包括变更单填写是否完整、拟变更内容与现有系统配置是否一致。变更单材料不完整的，退回业务科室补正；材料完整的，应当在2个工作日内反馈核对结果。

第四条　信息技术科根据确认后的变更单在测试环境进行配置，业务科室负责对配置结果进行核验。核验通过的，信息技术科应当在拟生效日期前1个工作日完成正式环境发布；核验未通过的，信息技术科应当恢复测试环境原配置，并将问题退回业务科室。

第五条　因系统安全风险或者上级紧急通知需要当天完成变更的，业务科室应当在变更单上标注“紧急”。经运行管理科负责人确认后，信息技术科可以当天完成配置，业务科室应当在2个工作日内补齐变更单。

第六条　每次变更应当记录变更前后的内容、操作人员、发布时间和核验结果，变更记录保存2年。

第七条　运行管理科应当每季度汇总变更次数、退回补正情况以及紧急变更情况。

第八条　本办法自印发之日起试行6个月。
```

### 原创与证据链

技能规则、references 和 scripts 在本仓库持续迭代，各平台技能目录由 canonical 包同步生成。规范与社区项目用于校验文种、流程形态和风险维度；具体规则经过复现、取舍和 A/B 后进入主线，Git 历史记录每次修改和验证。

最近 5 份证据：[`release-1.6.20.md`](maintenance/tests/evidence/release-1.6.20.md) · [`release-1.6.20-rc.md`](maintenance/tests/evidence/release-1.6.20-rc.md) · [`ah002-news-date-completeness-r1/live-result.md`](maintenance/tests/evidence/ah002-news-date-completeness-r1/live-result.md) · [`reference-slimming-r1/result.md`](maintenance/tests/evidence/reference-slimming-r1/result.md) · [`release-1.6.19.md`](maintenance/tests/evidence/release-1.6.19.md)。完整记录见 [`maintenance/docs/evidence/README.md`](maintenance/docs/evidence/README.md)。

## 目录结构

| 路径 | 用途 |
| --- | --- |
| `chinese-official-writing/` | 通用 canonical Agent Skill；不启用 Hook 也可独立完成写稿与复核 |
| `chinese-official-writing/hooks/` | 可选交付复核说明、唯一能力核心和宿主静态适配层；见 [Hook 使用说明](chinese-official-writing/hooks/README.md) |
| `chinese-official-writing/hooks/adapters/codex/` | Codex Hook 静态兼容文件与使用指引 |
| `chinese-official-writing/hooks/adapters/codebuddy/` | WorkBuddy/CodeBuddy Hook 静态兼容文件与使用指引 |
| `chinese-official-writing/hooks/adapters/claude-code/` | Claude Code Hook 静态兼容文件与使用指引 |
| `chinese-official-writing/hooks/adapters/zcode/` | ZCode Hook 静态兼容文件与使用指引 |
| `chinese-official-writing/hooks/adapters/qwen-code/` | Qwen Code native extension Hook 静态兼容文件与使用指引 |
| `chinese-official-writing/hooks/adapters/kimi-code/` | Kimi Code CLI native plugin Hook 静态兼容文件、单 Stop 边界与使用指引 |
| `chinese-official-writing/hooks/adapters/opencode/` | OpenCode 项目级交互插件、同名 Skill 来源保护、无头旁路与使用指引 |
| `chinese-official-writing/hooks/adapters/hermes-agent/` | Hermes Agent 新建、不可恢复单题的有界复核插件与宿主限制 |
| `chinese-official-writing/hooks/adapters/deepseek-harness/` | DeepSeek Harness headless Profile Bundle、OpenCodex 配置与生命周期边界 |
| `packages/agent-skills/` | 通用 Agent Skills、MiniMax Skills、GLM Skills（Z.ai/智谱）、ZCode、AutoClaw、Kimi Code CLI、TRAE、Baidu Comate AI IDE 等兼容包 |
| `packages/qwen-code/` | Qwen Code 兼容包 |
| `packages/qwenwork/` | QwenWork（Qwen 办公）静态 Skill 兼容包，不声明 Hook 生命周期 |
| `packages/hermes/` | Hermes 兼容包 |
| `packages/openclaw/` | OpenClaw 兼容包，不含 Hook 和交付门禁 |
| `packages/red-skillhub/` | Red SkillHub 专用包 |
| `packages/` | 各平台普通兼容包总目录；见 [兼容包索引](packages/README.md) |
| `maintenance/` | 测试、评测、构建工具、原始证据和维护记录；见 [维护区索引](maintenance/README.md) |

## 开源许可

本仓库采用 [MIT License](LICENSE)。

## 规范与参考

- [党政机关公文处理工作条例](https://www.gov.cn/zwgk/2013-02/22/content_2337704.htm)
- [GB/T 9704-2012](https://openstd.samr.gov.cn/bzgk/std/newGbInfo?hcno=F3CC9BEF482524C895FDA7A08BB4A70E)
- [ClawHub：official-doc-writer（正式交付前要素核对卡）](https://clawhub.ai/wonderslife/skills/official-doc-writer)
- [SkillHub：govwriter-pro（创作与修改模式的素材边界）](https://api.skillhub.cn/api/v1/skills/govwriter-pro)
- [jpeggdev/humanize-writing](https://github.com/jpeggdev/humanize-writing)、[blader/humanizer](https://github.com/blader/humanizer)、[brandonwise/humanizer](https://github.com/brandonwise/humanizer)（成簇问题、孤立词与密度复核）
