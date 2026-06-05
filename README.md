# 中文公文写作 Skill

[![ClawHub](https://img.shields.io/badge/ClawHub-chinese--official--writing-blue)](https://clawhub.ai/gongyu0918-debug/chinese-official-writing)
[![License](https://img.shields.io/badge/license-MIT--0-green)](LICENSE)
[![Language](https://img.shields.io/badge/language-中文公文-red)](#适用范围)

中文公文写作 Skill 面向正式材料起草、改写和复核场景，提供文种路由、行文关系判断、办理要素核对、论证链条、标题二次核验、重复事项检测、主体视角校验、敬谦称谓检查、低 AI 味审查和技术类材料专项约束。

主要覆盖文种功能校正、办理要素完整性、主体视角统一、句式风险压降和技术类材料论证。AI 算力、服务器租赁、云端部署成本对比等材料按 **需求来源 -> Token/资源测算 -> 成本比较 -> SLA/并发/安全/验收** 组织正文。

## 适用范围

| 类型 | 覆盖内容 |
| --- | --- |
| 法定公文 | 通知、请示、报告、函、批复、意见、决定、公告、通告、通报、会议纪要，以及命令（令）、决议、公报、议案的基础功能识别 |
| 常用事务文书 | 说明、申请、复函、公示、征求意见函等日常办理材料 |
| 工作材料 | 工作要点、工作总结、调研报告、可研报告、实施方案、建设方案、审查材料、讲话稿、致辞、述职报告 |
| 技术类正式材料 | AI 算力服务可研、算力资源采购或租赁、GPU/服务器租赁、云端部署成本对比、SLA 与并发保障、数据安全、运维验收 |
| Word 文稿 | 带批注文档改写、压缩、顺稿、去口语化、统一文风 |

适用边界为中文正式材料。英文写作、文学创作、营销软文、社交媒体文案不在覆盖范围内。法律、财务、采购、审计和政策依据类正式上报材料保留人工复核环节。

### 触发条件与非适用范围

建议在用户明确提出中文公文、中文正式工作材料、正式报告、请示、方案、可研、建设方案、审查材料、AI 算力采购/租赁材料，或提出顺稿、压缩、去口语化、降 AI 味、文种校验、办理要素核对时启用本 Skill。

不建议在英文写作、文学创作、营销文案、社交媒体文案、闲聊回复、代码说明、通用翻译、模型训练、批量语料生成、批量改写未知来源文本、规避人工审核、生成可冒充真实签发文件的完整编号/日期/印章信息等场景启用。

本 Skill 只提供写作和复核辅助，不替代法律、财务、采购、审计、政策依据、保密审查和正式签发判断。用户未提供依据时，不编造真实单位、真实政策、真实金额、真实日期、电话、邮箱或审批结论。

## 核心能力

- **文种路由**：按通知、请示、报告、函、批复、会议纪要等不同文种判断功能边界，并区分法定公文、事务文书和工作材料。
- **行文关系**：区分上行文、下行文和平行文，控制语气、结构、请批语和办理要求。
- **办理要素核对**：按文种核对发文主体、受文对象、事项、依据、时限、责任、附件、反馈渠道和请批事项。
- **论证链条**：按请示、报告、通知协调、方案建设、可研审查和 AI 算力技术材料选择不同论证路径。
- **标题二次核验**：默认不改主标题；固定标题检查正文是否贴题，生成标题检查是否漂移、重复或过度承诺。
- **重复事项检测**：检查相邻段落和相邻章节是否换词重复，避免批量生成后的胶水连接。
- **文稿蓝图**：先搭提纲，再列段落，再逐段成文，避免整篇一次性铺开后失控。
- **视角控制**：从发文单位、项目单位或报告单位出发写，不写成教学说明。
- **低 AI 味审查**：内置反例库和 `prose_lint.py`，提示二元包装句、旁白句、思考泄露、口语化判断、结构化草稿腔和空泛技术表述；除事实、文种、行文关系和过程泄露外，风格类问题只作为质量建议。
- **格式边界**：补充 GB/T 9704-2012 常用格式要素，但正式红头、文号、签发、印章和版记以用户模板和人工复核为准。
- **格式噪点检查**：提示半角标点、数字空格、千位分隔符、频繁编号、Emoji、装饰符号和表格滥用风险。
- **算力类专项约束**：对 Token、云端成本、租赁服务、SLA、并发、安全和验收做链式论证。
- **多平台适配**：已适配 Codex/OpenAI Skill、Claude Code、OpenClaw/ClawHub、Hermes 及通用 Skill Markdown 目录。

## 社区经验来源

| 来源 | 吸收内容 |
| --- | --- |
| 官方规范 | 以《党政机关公文处理工作条例》和 GB/T 9704-2012 作为文种功能和格式基础 |
| ClawHub / GitHub 公文 Skill | 借鉴格式规范、模板分层、质量清单和渐进式披露 |
| TRAE 中文社区公文 Skill 分享 | 借鉴对话式收集公文要素、Word 导出和格式可配置思路 |
| 中文提示词/开发者社区 | 借鉴结构化提示词、任务规则拆解和去 AI 味表达约束 |
| SkillHub 导航 | 当前未检索到可直接作为核心规则来源的专门公文写作 Skill |

社区来源只作辅助经验。文种定义、格式规范和用户自有模板优先。

## 安装 Prompt

### Codex / OpenAI Skill

```text
请从 GitHub 仓库 https://github.com/gongyu0918-debug/chinese-official-writing-skill 拉取 chinese-official-writing/ 目录，并将其安装到 Codex 的 skills 目录，目标路径为 ~/.codex/skills/chinese-official-writing。只安装该 Skill 目录，不安装 tests/、output/ 或其他适配目录；安装后确认 SKILL.md、references/、scripts/ 和 agents/ 均已保留。
```

### OpenClaw / ClawHub

```text
请从 GitHub 仓库 https://github.com/gongyu0918-debug/chinese-official-writing-skill 拉取 openclaw/skills/chinese_official_writing/ 目录，并将其安装为 OpenClaw/ClawHub 可识别的 chinese-official-writing 技能。该适配目录的 frontmatter 使用 name: chinese_official_writing；安装后确认显示名称为“中文公文写作”，用于中文公文、可研报告、建设方案和 AI 算力采购租赁类正式材料写作。
```

当前工作版本：`chinese-official-writing@1.3.0`

### Claude Code

```text
请从 GitHub 仓库 https://github.com/gongyu0918-debug/chinese-official-writing-skill 拉取完整仓库，并将仓库根目录作为 Claude Code 插件目录。安装后确认 .claude-plugin/plugin.json 存在，并加载 skills/chinese-official-writing/ 作为中文公文写作 Skill 目录；不要把 openclaw/、hermes/ 或 output/ 当作 Claude Code 主技能目录。
```

### deepseek-tui

```text
请从 GitHub 仓库 https://github.com/gongyu0918-debug/chinese-official-writing-skill 拉取 .agents/skills/chinese-official-writing/ 目录，并将其作为 deepseek-tui 的中文公文写作 Skill。若当前项目只识别 skills/，则改为拉取 skills/chinese-official-writing/。只安装对应的 Skill 目录，不安装 tests/ 或 output/；安装后进入 deepseek-tui，使用 /skills 确认可见，再用 /skill chinese-official-writing 启用。
```

### Hermes

```text
请从 GitHub 仓库 https://github.com/gongyu0918-debug/chinese-official-writing-skill 拉取 hermes/skills/chinese-official-writing/ 目录，并将其安装为 Hermes 的 chinese-official-writing 技能。安装时保留 SKILL.md、references/ 和 scripts/，不要使用根目录 chinese-official-writing/ 替代 Hermes 适配目录。
```

## 试用 Prompt

通用公文：

```text
使用中文公文写作 Skill，起草一份项目请示。要求一文一事，先写请批事项，再写依据、现状、资金或资源需求，结尾使用正式请批语。
```

技术类正式材料：

```text
使用中文公文写作 Skill，起草一段 AI 算力资源租赁方案。要求写明 Token 需求来源、云端部署成本上升因素、租赁服务对 SLA、并发和数据安全的保障安排。
```

审稿与降 AI 味：

```text
使用中文公文写作 Skill，检查这段建设方案是否存在视角错位、解释腔、口语化判断和二元对照句，只给出需要修改的位置和建议。
```

## 目录结构

| 路径 | 用途 |
| --- | --- |
| `chinese-official-writing/` | 主技能目录，供 Codex/OpenAI Skill 使用 |
| `skills/chinese-official-writing/` | Claude Code 与部分通用 skills 目录约定 |
| `.agents/skills/chinese-official-writing/` | 兼容 `.agents/skills` 约定的 agent |
| `openclaw/skills/chinese_official_writing/` | OpenClaw/ClawHub 发布目录 |
| `hermes/skills/chinese-official-writing/` | Hermes 适配目录 |
| `chinese-official-writing/references/` | 文种路由、办理要素、论证链条、格式和复核规则 |

命名约定：仓库、Codex、Claude Code、Hermes 和 ClawHub slug 使用 `chinese-official-writing`；OpenClaw 适配目录和 frontmatter 使用 `chinese_official_writing`，用于兼容其当前匹配规则。不要把主技能名统一改成下划线形式。

同步各平台副本：

```powershell
python .\tools\sync_adapters.py
```

## 评测数据

公开仓库保留脱敏测试摘要，不保存原始公文、真实项目材料、内部路径或个人信息。

### Promptfoo 社区式消融

新增 Promptfoo 作为发布前主评测入口。默认本地运行使用确定性本地草稿（stub）做规则回归，不调用真实模型；接入真实模型时需设置 `OFFICIAL_WRITING_AGENT_COMMAND`。评测使用固定 JSONL 数据集，同时生成 baseline 和 Skill 两组输出；Promptfoo 负责批量运行、确定性断言、JSON/HTML 结果导出，本地汇总脚本再用随机 A/B 顺序做 pairwise judge。输出目录 `output/promptfoo/` 已被 `.gitignore` 排除。

```powershell
npm run eval:official-writing:smoke
npm run eval:official-writing
npm run eval:official-writing:view
```

Smoke 覆盖 5 个文种、每类 2 个场景，共 10 条；full 覆盖 27 个文种、每类 10 个场景，共 270 条。汇总指标包括 Skill win、baseline win、tie、invalid、硬规则通过率、lint 风险下降率、占位词风险率、judge 一致率、平均耗时和估算成本。Full 评测中 `needs_manual_review` 超过 2% 会非零退出；空输出、缺 case 或 judge 空返回始终非零退出。

### 本地 smoke/regression 消融

本地 smoke/regression 采用合成反例模板，测试文种适配、反 AI 规则和算力类论证链的回归稳定性。每类文种 10 次，共 270 个任务。该组测试用于检查规则是否失效，不作为真实语料泛化胜率。

| 指标 | Baseline | Skill |
| --- | ---: | ---: |
| 任务数 | 270 | 270 |
| high 风险 | 54 | 0 |
| medium 风险 | 729 | 0 |
| low 风险 | 811 | 1 |
| 总风险 | 1594 | 1 |

### 真实样文回归

真实样文回归选取通知、报告、请示、批复、函、复函、公示公告、通报、采购公告和征求意见函 10 组公开文章，公开摘要只展示匿名样本编号、文种类别和关键办理要素，不保存原文正文，不展示具体文章标题和链接。差异率按关键要素缺失率计算，不按逐字相似度计算。该组用于回归检查，不代表真实业务表现。为避免把关键词命中误读为质量证明，评测同时输出关键词命中率和占位词风险；占位词风险表示草稿直接写入了“发文机关、发文字号、主送单位”等匿名标签，需要进入人工或 LLM judge 复核。

| 模式 | 样本数 | 平均差异率 | 缺失要素 | 应覆盖要素 | 关键词命中率 | 占位词风险样本 | 占位词命中 | 格式风险 | 重复事项 | 反 AI 风险 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Baseline | 10 | 93.00% | 57 | 61 | 17.43% | 0 | 0 | 0 | 0 | 2 |
| Skill | 10 | 0.00% | 0 | 61 | 100.00% | 9 | 16 | 0 | 0 | 0 |

复跑命令：

```powershell
python .\tools\run_real_article_eval.py
```

### DeepSeek A/B/C 隔离消融

Writer A 调用技能规则，Writer B 按普通提示生成，Evaluator C 使用独立上下文评估。A/B 写稿覆盖 27 类文体、每类 10 次，共 540 段对比样稿。Evaluator C 按 9 个批次出具文种级评估意见；其中 2 个批次曾空返回，已在不重写 A/B 样稿的情况下补跑 C 轮。下表记录文种评估是否形成有效结论，不折算逐任务胜率。

本地 smoke/regression 采用相同数量、相同结构的合成反例模板，因此各文种 Baseline 风险数均为 59。Skill 输出在文种层面未命中风险，另有 1 条全局术语重复提示未归入单一文种。下表中的风险数来自本地合成消融；DeepSeek 列只记录 A/B 样稿生成数量和 C 轮评估是否形成有效结论。

| 文种 | 本地消融次数 | Baseline 风险 | Skill 风险 | DeepSeek A/B 生成 | C 评估状态 |
| --- | ---: | ---: | ---: | ---: | --- |
| 通知 | 10 | 59 | 0 | 10 | 有效 |
| 请示 | 10 | 59 | 0 | 10 | 有效 |
| 报告 | 10 | 59 | 0 | 10 | 有效 |
| 说明 | 10 | 59 | 0 | 10 | 有效 |
| 方案 | 10 | 59 | 0 | 10 | 有效 |
| 申请 | 10 | 59 | 0 | 10 | 有效 |
| 函 | 10 | 59 | 0 | 10 | 有效 |
| 复函 | 10 | 59 | 0 | 10 | 有效 |
| 批复 | 10 | 59 | 0 | 10 | 有效 |
| 意见 | 10 | 59 | 0 | 10 | 有效 |
| 决定 | 10 | 59 | 0 | 10 | 有效 |
| 公告 | 10 | 59 | 0 | 10 | 有效 |
| 公示 | 10 | 59 | 0 | 10 | 有效 |
| 通报 | 10 | 59 | 0 | 10 | 有效 |
| 会议纪要 | 10 | 59 | 0 | 10 | 有效 |
| 工作要点 | 10 | 59 | 0 | 10 | 有效 |
| 工作总结 | 10 | 59 | 0 | 10 | 有效 |
| 调研报告 | 10 | 59 | 0 | 10 | 有效 |
| 可研报告 | 10 | 59 | 0 | 10 | 有效 |
| 实施方案 | 10 | 59 | 0 | 10 | 有效 |
| 建设方案 | 10 | 59 | 0 | 10 | 有效 |
| 审查材料 | 10 | 59 | 0 | 10 | 有效 |
| 算力服务可研报告 | 10 | 59 | 0 | 10 | 有效 |
| 算力资源采购方案 | 10 | 59 | 0 | 10 | 有效 |
| GPU/服务器租赁技术需求 | 10 | 59 | 0 | 10 | 有效 |
| 云端部署成本对比说明 | 10 | 59 | 0 | 10 | 有效 |
| 技术服务审查材料 | 10 | 59 | 0 | 10 | 有效 |

评测范围限定为脱敏测试样本，结果用于观察规则约束和工作流差异。事实、政策依据、金额和采购结论保留人工复核环节。

DeepSeek A/B/C 评估项：文种契合、主体视角、段落逻辑、正式语气、低 AI 味表达，以及算力类文稿中的“需求 -> Token/资源 -> 成本 -> SLA/安全/验收”链条。Tie 表示未形成明确优劣或两组输出各有优势。

## 文稿检查脚本

`prose_lint.py` 检查草稿中的高风险表达。脚本仅提示问题，不自动改写。需要检查重复事项和格式噪点时加 `--structure --format`。

```powershell
python .\chinese-official-writing\scripts\prose_lint.py .\draft.md
python .\chinese-official-writing\scripts\prose_lint.py .\draft.docx
python .\chinese-official-writing\scripts\prose_lint.py .\draft.docx --structure --format
```

可检查的风险包括：二元包装句、旁白式表达、教学腔、思考过程泄露、口语化判断、模板化过渡词、项目卡片式摘要、测算说明腔、必要性罗列、相邻段落重复事项、格式噪点，以及算力类文档中缺少指标支撑的空泛技术表述。

## 发布前检查

```powershell
python .\chinese-official-writing\scripts\prose_lint.py README.md chinese-official-writing\SKILL.md
python .\tools\run_revision_instruction_eval.py --agent none --out output\revision-instruction-eval-task-packet
npm run eval:official-writing:smoke
python .\tools\run_ablation.py --out output\expanded-ablation
python .\tools\run_real_prompt_ablation.py --baseline-root output\release-baselines\github-1.2.26 --baseline-label baseline-1.2.26 --current-root . --out output\real-prompt-ablation
python .\tools\run_agent_ablation.py --genres-per-batch 1 --out output\agent-public-ablation
```

README/SKILL 自检若命中触发条件、加载条件或适用范围说明文本，按文档自述噪音人工确认，不等同于草稿正文缺陷。

## 参考来源

- [党政机关公文处理工作条例](https://www.gov.cn/zwgk/2013-02/22/content_2337704.htm)
- [GB/T 9704-2012](https://openstd.samr.gov.cn/bzgk/std/newGbInfo?hcno=F3CC9BEF482524C895FDA7A08BB4A70E)
- [KaguraNanaga/official-document-writing-skill](https://github.com/KaguraNanaga/official-document-writing-skill)
- [ClawHub official-doc-writer](https://clawhub.ai/wonderslife/official-doc-writer)
- [TRAE 公文 Skill 分享](https://forum.trae.cn/t/topic/2123)

## License

MIT-0。发布到 ClawHub 的 Skill 按 ClawHub/OpenClaw 规则视为 MIT-0 许可。
