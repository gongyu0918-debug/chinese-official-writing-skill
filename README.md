# 中文公文写作 Skill

[![Version](https://img.shields.io/badge/version-1.5.15-blue)](https://github.com/gongyu0918-debug/chinese-official-writing-skill/releases/tag/v1.5.15)
[![ClawHub](https://img.shields.io/badge/ClawHub-chinese--official--writing-2f80ed)](https://clawhub.ai/gongyu0918-debug/skills/chinese-official-writing)
[![SkillHub](https://img.shields.io/badge/SkillHub-chinese--official--writing-e8590c)](https://skillhub.cn/skills/chinese-official-writing)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

中文公文写作 Skill 面向正式材料起草、改写、压缩和复核，提供文种路由、行文关系判断、办理要素核对、论证链条、标题核验、重复事项检测、主体视角校验、自然表达审查和技术类材料专项约束。它先判断创作、修改、只审不改或排版交付，再按任务加载轻量卡、文种 playbook 和专项资料，让事实、文种、格式与交付方式保持在同一条写作链上。

事实、数字和事项状态以用户材料为准；用户已有模板、标题顺序、字段结构和最新版底稿优先保留。成稿以正式、平实、可执行为主，兼顾公文语气、自然表达和低 AI 味。

## 核心能力

- **文种与行文关系**：区分法定公文、事务文书和工作材料，按上行、下行和平行关系控制语气、结构与办理要求。
- **事实与模板边界**：锁定主体、数字、日期、责任、期限、附件和事项状态，保留用户模板、字段顺序与最新版底稿。
- **办理要素与论证链**：按请示、报告、通知协调、方案建设、可研审查和技术材料选择相应的办理要素与论证路径。
- **渐进式路由**：短任务使用轻量卡，完整公文进入对应文种叶子，技术类材料按需加载专项规则。
- **创作、改稿与复核**：分别处理从零起草、基于底稿修改、只审不改、压缩和 Word 正文衔接。
- **轻量审查**：分层核对事实、视角、标题、格式、重复事项和模板化表达，并提供可选的确定性风险线索。
- **技术材料专项写作**：覆盖 AI 算力、GPU/服务器租赁、成本比较、SLA、并发、安全、运维和验收。
- **多平台适配**：同一 canonical 技能包同步到 Codex、Claude Code、OpenClaw、Hermes、Qwen Code 和通用 Agent Skills 目录。

## 适用范围

| 场景 | 主要内容 |
| --- | --- |
| 法定公文 | 通知、请示、报告、函、批复、意见、决定、公告、通告、公报、通报、议案、决议、命令（令）、纪要 |
| 事务与工作材料 | 说明、申请、复函、公示、征求意见函、工作要点、总结、调研报告、讲话稿、致辞、述职报告 |
| 方案与审查材料 | 实施方案、建设方案、可研报告、采购公告、审查材料、项目论证和办理要素核对 |
| 技术类正式材料 | AI 算力服务可研、GPU/服务器租赁、模型服务需求、成本比较、SLA、并发、安全、运维和验收 |
| 改稿与复核 | 顺稿、压缩、去口语化、降 AI 味、文种校验、格式核验、只审不改、Word 正文衔接 |

## 它怎么解决这些问题

普通写作提示往往只告诉模型“写一份报告”或“改得正式一点”，文种、主体视角、事实状态、用户模板和交付方式容易在长稿或多轮修改中互相挤占。这个 Skill 把写作拆成一条可检查的链路：

任务模式 → 文种与行文关系 → 办理要素 → 轻量卡或文种叶子 → 正文 → 分段、小节和全文复核。

- 先分任务模式：区分从零起草、基于底稿修改、只审不改和 Word/排版衔接，避免审稿任务被改成重写。
- 再定文种功能：按上行、下行和平行关系选择语气、结构和办理要素，请示与报告、函与复函各走自己的规则。
- 锁定事实状态：金额、日期、主体、责任、期限、附件和联系人按已确认、未决、缺失分别处理，用户模板和字段顺序优先保留。
- 材料暂缺时正文优先完成，影响执行的必要缺口放在文后简短提示；后续轮次继续执行新的修改要求。
- 成稿后进入轻量审查层，依次核对事实、文种、标题、格式、重复事项和模板化表达，局部修正已经确认的问题。

## 实现与技术栈

这是一个 Markdown-first 的 Agent Skill。核心规则和 references 全部使用中文 Markdown 编写，不懂代码也能直接阅读、审查和修改。YAML frontmatter 负责名称、触发描述、版本和许可；Python 只承担可选的确定性检查；各平台适配包从同一 canonical 技能目录同步，正文规则保持一致。

| 组成 | 作用 |
| --- | --- |
| `SKILL.md` | 判断何时启用、选择任务模式，并给出事实、输出和复核主流程 |
| `references/task-route-cards.md` | 为稀疏说明、未决纪要、短通知和二次局部修改提供轻量路径 |
| 文种与专项 references | 按需补充文种骨架、办理要素、论证链、GB/T 9704 格式和 AI 算力材料规则 |
| 分层复核 references | 从段落、小节到全文检查事实、视角、结构、格式和自然表达 |
| `scripts/prose_lint.py` | 提供可选的格式、重复和成品残留线索，作为轻量审查层的确定性补充 |
| `agents/openai.yaml` | 提供界面展示和默认调用信息 |

渐进式路由让短任务只读取轻量卡，完整公文再进入相应文种叶子，技术类材料只加载命中的专项规则。这样既保留必要边界，也减少无关规则对真实写稿的干扰。

## 快速安装

当前工作版本：`chinese-official-writing@1.5.15`

平台入口：[ClawHub](https://clawhub.ai/gongyu0918-debug/skills/chinese-official-writing) · [skillhub.cn](https://skillhub.cn/skills/chinese-official-writing)。通用 Agent Skills 安装器可直接使用：

```powershell
npx skills add https://github.com/gongyu0918-debug/chinese-official-writing-skill --skill chinese-official-writing
```

从 GitHub 手动部署时，主技能入口为 `chinese-official-writing/`；各平台镜像和 Claude Code 插件入口见下方目录结构。

## 模型消融与真实写稿

测试从早期无 Skill/带 Skill 对照，逐步扩展到固定版本消融、真实写稿盲审和多轮改稿。下表汇总 1.5.15 发布前复核及其继承的 1.5.14 发布证据。原始任务、成稿、匿名映射、独立复核和汇总记录均保存在仓库内；早期 270 任务模型消融保留脱敏聚合摘要。

| 调试方向 | 主要稿件与边界 | 当前证据 |
| --- | --- | --- |
| 无 Skill / 带 Skill 模型消融 | 27 类文体，每类 10 个任务，覆盖通用公文和算力类正式材料 | 270 个任务、540 段对比材料；写稿 9/9 批有效，2 批评估补跑后为 9/9 |
| 渐进式路由 | 未决/已决会议纪要、稀疏情况说明、短通知、二次局部修改 | 针对性 A/B 共 16 份成稿，内容 16/16 PASS，路由 14/16；两次 over-read 均在 v1.5.13，1.5.14 为 8/8 |
| 事实、文种与格式 | 请示、报告、通知、说明、会议纪要、字段式申请、主送、落款、普通采购与 AI 算力需求 | 固定 v1.5.13 与 1.5.14 的硬边界盲审均为 30/30 PASS |
| 输出模式 | 起草、改稿、只审不改、只输出正文、最新版/旧稿合稿、单点日期修改 | 15 个真实用户式任务、2 名反向映射 writer，共 60 份成稿 |
| 多轮与长稿 | 三轮连续改稿、长文事实和标题稳定、第三轮单点修改 | 一个原始任务的完整改稿链中，事实、状态和标题顺序保持稳定；6 份稿中 1 份达到精确 CJK 下限 |
| Candidate B 定向实写 | 多材料报告、异常报告、说明、会议纪要 | 8 份有效同题成稿与 1 份初始路由未命中原稿均留存；该组只作局部风险核验，不单独宣传整稿胜率 |
| 工程回归 | 单元测试、固定上一版消融、Promptfoo、公开样文 | 175/175；两版均 108/108；Promptfoo 20/20；公开样文缺失要素 0/61 |

60 份发布级真实写稿由两名独立 verifier 盲审。综合结果中，v1.5.13 与 1.5.14 都是 29 PASS、1 个对称 WARN、0 FAIL；硬边界复核两版均为 30 PASS、0 WARN、0 FAIL。真实模型小样本评测与发布级写稿覆盖会议纪要、情况说明、通知、请示、报告、字段式申请、只审不改、普通采购、AI 算力需求和旧稿防回流。

### 同题独立写作节选

两份完整成稿来自同一原始任务、`gpt-5.6-luna` medium 和相同宿主外壳下的独立上下文，并非同一随机 seed。按盲审统一口径去除空白、保留标点后，无 Skill 成稿为 1868 字符，Candidate B 带 Skill 成稿为 1756 字符，相差 112 字符，以较短稿为基数计算为 6.38%。本组两稿均进入 Candidate B 三稿匿名盲审；旧节选中“无 Skill 样稿未进入该轮候选/基线双盲排序”的限制已经排除。

```text
模型：gpt-5.6-luna（medium）
原始任务首句：请根据以下材料，起草一份 1600—1900 字的《市图书馆自助借还设备试运行阶段报告》，供馆务会审议。只输出可直接使用的报告正文。
```

完整材料见 [`prompts.md`](tests/evidence/no-skill-risk-ablation-20260715/prompts.md)，模型、思考档位和读取记录见 [`provenance.md`](tests/evidence/candidate-b-writing-20260715/provenance.md)。匿名盲审将 Candidate B 判为 PASS、G0、整体第一，将无 Skill 稿判为 FAIL、G2、整体第三。下面截取两稿“馆务会意见及下一阶段安排”的对应段落。

无 Skill 成稿采用六项固定列表，并写入材料没有给出的读者数量、业务类型、技术服务方配合、设备排队、人工引导等安排：

> 6月26日，馆务会听取阶段汇报后提出，继续运行至8月31日，补充高峰时段测试后，再研究是否扩大设备数量。会议未形成新增采购决定。按照会议意见，7月至8月重点做好以下工作：一是记录晚间时段设备使用量、读者数量和业务类型，为评估服务时段提供依据；二是持续跟踪少儿图书识别情况，分类记录识别失败图书及处理结果；三是收集预约书取书路径反馈，优化标识和引导；四是完整记录设备离线、恢复时间、处置方式及网络状态，配合技术服务方查找共同原因；五是补充高峰时段测试，重点观察设备排队、人工引导、故障处理和服务承载情况；六是根据测试数据和读者反馈，形成阶段性分析材料。

Candidate B 带 Skill 成稿围绕材料明确的会议意见、四项记录对象和未决状态组织段落：

> 6月26日，馆务会听取了自助借还设备试运行阶段汇报，会议意见为继续运行至8月31日，补充高峰时段测试后再研究是否扩大设备数量。会议未形成新增采购决定。根据会议意见，现阶段工作重点仍为继续试运行、补充测试和收集数据，不对新增设备数量及采购安排作出提前结论。
>
> 7月至8月，拟重点记录晚间使用量、少儿图书识别情况、预约书取书路径反馈和设备离线情况。其中，晚间使用量用于观察延长服务时段的实际需求；少儿图书识别情况用于继续掌握相关设备使用效果；预约书取书路径反馈用于了解读者查询和取书过程中的实际感受；设备离线情况用于补充运行记录，继续观察离线发生的时间、持续时长和恢复情况。上述事项目前作为下一阶段重点记录内容，具体设备调整方案、责任分工和新增采购安排尚未确定。

原始任务、两份完整输出和盲审结论见 [`prompts.md`](tests/evidence/no-skill-risk-ablation-20260715/prompts.md)、[`luna-t01.md（无 Skill）`](tests/evidence/strict-no-skill-20260715/luna-t01.md)、[`luna-t01.md（Candidate B）`](tests/evidence/candidate-b-writing-20260715/luna-t01.md) 和 [`release-1.5.15-verifier.md`](tests/evidence/candidate-b-three-way-blind-20260715/release-1.5.15-verifier.md)。

### 原创与证据链

技能规则、references 和 scripts 在本仓库持续迭代，各平台技能目录由 canonical 包同步生成。规范与社区项目用于校验文种、流程形态和风险维度；具体规则经过本仓库复现、取舍和 A/B 后进入主线。1.5.15 延续“原始任务 → 隔离 writer → 匿名映射 → 独立 verifier → 汇总报告 → 发布回执”的证据链，Git 历史记录每次修改和验证；早期大规模消融公开脱敏聚合摘要。

主要证据：

- [`release-1.5.15.md`](tests/evidence/release-1.5.15.md)
- [`release-1.5.14.md`](tests/evidence/release-1.5.14.md)
- [`functional-regression-vs-1.5.13-20260715.md`](tests/evidence/functional-regression-vs-1.5.13-20260715.md)
- [`route-arbitration-20260715.md`](tests/evidence/route-arbitration-20260715.md)
- [`negative-constraint-echo-20260714.md`](tests/evidence/negative-constraint-echo-20260714.md)
- [`agent-public-ablation-summary.md`](tests/evidence/agent-public-ablation-summary.md)
- [`long-revision-stability-20260714.md`](tests/evidence/long-revision-stability-20260714.md)
- [`genre-real-writing-coverage-20260714.md`](tests/evidence/genre-real-writing-coverage-20260714.md)

## 目录结构

| 路径 | 用途 |
| --- | --- |
| `chinese-official-writing/` | Codex / OpenAI 使用的 canonical 技能包 |
| `skills/chinese-official-writing/` | Claude Code、MiniMax Skills、GLM Skills（Z.ai/智谱）、AutoClaw、Kimi Code CLI 和通用 Agent Skills 镜像 |
| `.agents/skills/chinese-official-writing/` | TRAE、Baidu Comate AI IDE 等 `.agents/skills` 兼容平台镜像 |
| `.qwen/skills/chinese-official-writing/` | Qwen Code 镜像 |
| `hermes/skills/chinese-official-writing/` | Hermes 镜像 |
| `openclaw/skills/chinese_official_writing/` | OpenClaw / ClawHub 发行镜像 |
| `.claude-plugin/plugin.json` | Claude Code 插件入口 |
| `tests/`、`evals/` | 测试案例、原始 prompt、成稿、盲审与评测配置 |
| `tools/` | 镜像同步与评测工具 |

## 开源许可

仓库首页统一按 [MIT](https://spdx.org/licenses/MIT.html) 展示，具体授权边界如下：

| 范围 | 许可 |
| --- | --- |
| 可直接安装的技能包 | [MIT-0](https://spdx.org/licenses/MIT-0)，见 [`LICENSE-SKILL`](LICENSE-SKILL)。以 `openclaw/skills/chinese_official_writing/` 为基准，canonical、通用 Agent、`.agents`、Qwen Code 和 Hermes 镜像采用同一许可 |
| 包外维护材料 | MIT，见 [`LICENSE`](LICENSE)。包括根 README、tests、evals、tools、测试证据、迭代记录和维护文档 |

技能包目录内的 `SKILL.md`、`references/`、`scripts/` 与随包元数据统一采用 MIT-0。仓库引用的外部规范和第三方项目沿用各自许可。

## 规范与参考

- [党政机关公文处理工作条例](https://www.gov.cn/zwgk/2013-02/22/content_2337704.htm)
- [GB/T 9704-2012](https://openstd.samr.gov.cn/bzgk/std/newGbInfo?hcno=F3CC9BEF482524C895FDA7A08BB4A70E)
- [ClawHub：official-doc-writer（正式交付前要素核对卡）](https://clawhub.ai/wonderslife/skills/official-doc-writer)
- [SkillHub：govwriter-pro（创作与修改模式的素材边界）](https://api.skillhub.cn/api/v1/skills/govwriter-pro)
- [jpeggdev/humanize-writing](https://github.com/jpeggdev/humanize-writing)、[blader/humanizer](https://github.com/blader/humanizer)、[brandonwise/humanizer](https://github.com/brandonwise/humanizer)（成簇问题、孤立词与密度复核）
