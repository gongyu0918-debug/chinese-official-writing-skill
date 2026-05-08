# 中文公文写作 Skill

这是一个面向中文正式材料写作的 Agent Skill，适合起草、改写和复核通知、请示、报告、说明、方案、函、批复、会议纪要、调研报告、可研报告、实施方案、建设方案、审查材料等文稿。

它主要解决三类问题：文种容易混、视角容易漂、正文容易带解释腔。使用时，Skill 会先帮助 agent 搭好提纲和段落安排，再按公文语气逐段成文，并在最后检查口语化、AI 味句式、数据缺口和事项落点。

本仓库已分别适配 Codex/OpenAI Skill、Claude Code、OpenClaw/ClawHub、deepseek-tui 和 Hermes。不同 agent 的技能目录规则不完全一致，因此仓库保留一个主技能目录，并通过同步脚本生成各平台副本。

## 适合写什么

- 常见公文：通知、请示、报告、说明、方案、申请、函、复函、批复、意见、决定、公告、公示、通报、会议纪要。
- 工作材料：工作要点、工作总结、调研报告、可研报告、实施方案、建设方案、审查材料。
- 技术类正式材料：AI 算力服务可研、算力资源采购或租赁、GPU/服务器租赁、云端部署成本对比、SLA 与并发保障、数据安全和运维验收章节。
- Word 文稿处理：带批注文档的改写、压缩、顺稿、去口语化和风格统一。

不建议用于英文写作、文学创作、营销软文、社交媒体文案。涉及法律、财务、采购、审计和政策依据的正式上报材料，应由专业人员最终复核。

## 它会重点管什么

- **文种**：请示要有请批事项，报告不夹带审批请求，通知要写清对象、时限和办理要求。
- **视角**：从发文单位、报告单位或项目单位出发，不写成旁观者点评。
- **段落**：每段围绕一个判断展开，先写结论，再补事实、依据和工作落点。
- **语言**：减少解释腔、教学腔、口语判断和高频 AI 句式。
- **数据**：实际数据不编造；测算数据写清来源和用途；空缺数据保留待补。
- **算力类材料**：围绕需求来源、Token 或资源换算、费用比较、SLA、并发、安全、交付和验收展开。

## 目录怎么选

- `chinese-official-writing/`：主技能目录，供 Codex/OpenAI Skill 使用，也是其他适配目录的源文件。
- `skills/chinese-official-writing/`：Claude Code 可读取的技能副本，deepseek-tui 也会识别项目根目录的 `skills/`。
- `.agents/skills/chinese-official-writing/`：deepseek-tui 与兼容 `.agents/skills` 约定的 agent 使用。
- `openclaw/skills/chinese_official_writing/`：OpenClaw/ClawHub 发布目录，frontmatter 中的 `name` 使用 snake_case。
- `hermes/skills/chinese-official-writing/`：Hermes 适配目录，保留顶层 `version` 和 `metadata.hermes`。

适配目录由脚本统一生成：

```powershell
python .\tools\sync_adapters.py
```

## 安装与调用

### Codex

```powershell
Copy-Item -Recurse .\chinese-official-writing "$env:USERPROFILE\.codex\skills\chinese-official-writing"
```

调用示例：

```text
Use $chinese-official-writing 起草一份关于年度数据治理工作的通知，要求文种准确、事项清楚、避免 AI 味。
```

### Claude Code

```bash
claude --plugin-dir .
```

调用示例：

```text
Use the chinese-official-writing skill to revise this Chinese implementation plan. Keep the issuing-unit viewpoint, remove teaching voice, and preserve official-document style.
```

### OpenClaw / ClawHub

```powershell
clawhub skill publish .\openclaw\skills\chinese_official_writing --slug chinese-official-writing --name "中文公文写作" --version 1.2.1 --tags "chinese,official-document,writing,gongwen,ai-compute"
```

调用示例：

```text
使用中文公文写作技能，按建设方案文体重写以下材料。重点说明需求来源、成本测算、实施安排和建设成效，不写成概念解释。
```

### deepseek-tui

项目内使用：

```powershell
python .\tools\sync_adapters.py
deepseek
```

进入 deepseek-tui 后：

```text
/skills
/skill chinese-official-writing
```

调用示例：

```text
请使用 chinese-official-writing 技能，起草一份项目请示。要求一文一事，先写请批事项，再写依据、现状、资金或资源需求，结尾使用正式请批语。
```

### Hermes

将适配目录复制到 Hermes 可读取的 skills 目录，或在项目中直接引用 `hermes/skills/chinese-official-writing/`。

```powershell
Copy-Item -Recurse .\hermes\skills\chinese-official-writing "<Hermes skills 目录>\chinese-official-writing"
```

调用示例：

```text
Use the chinese-official-writing skill to draft a Chinese feasibility study section. Focus on demand, cost, risk, implementation, and acceptance; avoid casual or explanatory wording.
```

## 文稿检查脚本

`prose_lint.py` 用来检查草稿中的高风险表达。它只提示问题，不自动改写。

```powershell
python .\chinese-official-writing\scripts\prose_lint.py .\draft.md
python .\chinese-official-writing\scripts\prose_lint.py .\draft.docx
```

可检查的风险包括：二元包装句、旁白式表达、教学腔、口语化判断、模板化过渡词，以及算力类文档中缺少指标支撑的空泛技术表述。

## 测试情况

仓库只保留脱敏测试摘要，不保存原始公文、真实项目材料、内部路径或个人信息。

- 通用公文对比测试：启用 Skill 的输出在文种格式、正文视角、正式要素和初稿可用性上更稳定。
- AI 算力类文档对比测试：启用 Skill 后，文稿更容易把需求来源、Token/资源需求、成本比较、SLA、并发、运维、验收和数据安全责任连成完整论证。
- 扩展泛化测试：覆盖 22 类常见文体和 5 类 AI 算力技术文档，并分别设置短文、长文任务。

这些测试用于验证规则和流程有效性，不代表具体事实、政策依据、金额和采购结论已经通过业务审核。

## 维护说明

修改主技能目录后，运行同步脚本更新各平台适配副本：

```powershell
python .\tools\sync_adapters.py
```

发布前建议执行：

```powershell
python .\chinese-official-writing\scripts\prose_lint.py README.md chinese-official-writing\SKILL.md
python .\tools\run_ablation.py --out output\expanded-ablation
```

## License

MIT-0。发布到 ClawHub 的 Skill 按 ClawHub/OpenClaw 规则视为 MIT-0 许可。
