# 中文公文写作 Skill

面向中文公文写作的 Codex Skill。适用于起草、改写、校对和复核中文正式材料，不面向英文写作。

它聚焦正式工作材料的可用性：文种清楚、视角稳定、论点前置、数据有依据、段落能落到事项安排，减少 AI 味、解释腔和模板腔。

## 触发范围

实际触发条件写在 `chinese-official-writing/SKILL.md` 的 YAML `description` 中。它覆盖通知、请示、报告、说明、方案、申请、函、复函、批复、意见、决定、公告、公示、通报、会议纪要、工作要点、工作总结、调研报告、可研报告、实施方案、建设方案、审查材料，以及 AI 算力服务可研、算力资源采购、服务器租赁、GPU 租赁和技术服务需求等正式材料。

部分平台或 GitHub 页面只展示 README 简介、插件摘要或 description 前半段，因此看起来会比实际触发条件更短。以 `SKILL.md` 头部 `description` 为准。

## 核心功能

- **公文文种适配**：支持通知、请示、报告、说明、方案、申请、函、复函、批复、意见、决定、公告、公示、通报、会议纪要、工作要点、工作总结、调研报告、可研报告、实施方案、建设方案、审查材料等。
- **分层写作流程**：先列提纲，再拆段落，再写小段要点，最后分段成文、逐段复核、章节复核、全文复核。
- **视角控制**：保持发文单位、报告单位、项目单位、集团公司或主管部门视角，避免写成“教别人怎么写报告”的说明文。
- **低 AI 味检查**：识别二元对照句、递进套句、机械并列句等高频 AI 句式，提示旁白式、口语化、空泛化表达。
- **文种要素核查**：按文种检查主送机关、来文依据、附件、时限、联系人、议定事项、资金来源、绩效目标、验收要求等要素。
- **中文公文格式参考**：内置 GB/T 9704-2012 常见版式参考，实际使用时以单位模板优先。
- **AI 算力类材料增强**：针对算力服务可研、算力资源采购、GPU/服务器租赁、云端部署成本对比、SLA、并发、验收、运维、数据安全等技术类正式文稿提供专项写法。
- **多 Agent 工具适配**：提供 Codex/OpenAI Skill、OpenClaw/ClawHub、Claude Code 插件和 Hermes 技能目录的兼容结构。

## 适用场景

### 通用中文公文

- 部门通知、项目请示、情况报告、工作总结、调研报告、实施方案、会议纪要；
- 国企、事业单位、机关部门内部正式材料；
- 带批注 Word 文档的改写、压缩、顺稿和风格统一；
- 需要去掉 AI 味、解释腔、口语化表达的正式文稿。

### AI 公司和技术服务类文档

- 算力服务可行性研究报告；
- 算力资源采购或租赁方案；
- GPU/服务器租赁技术需求；
- 云端部署与本地租赁成本对比；
- SLA、并发、日志审计、资源调度、运维验收章节；
- 数据安全、敏感数据不出域、调用可追溯、责任可界定等章节。

## 不适用场景

- 英文写作；
- 文学创作、营销软文、社交媒体文案；
- 需要法律、财务、采购、政策最终定稿责任的场景。此类材料可以用作初稿或复核辅助，但必须由专业人员最终审核。

## 安装

### Codex / OpenAI Skill

将 `chinese-official-writing` 文件夹复制到 Codex skills 目录：

```powershell
Copy-Item -Recurse .\chinese-official-writing "$env:USERPROFILE\.codex\skills\chinese-official-writing"
```

使用时在提示词中调用：

```text
Use $chinese-official-writing 起草一份项目实施方案，保持中文公文风格。
```

### OpenClaw / ClawHub

仓库提供 `openclaw/skills/chinese_official_writing/` 作为 OpenClaw/ClawHub 适配目录。主技能目录为了兼容 Codex 与 Claude Code 使用 kebab-case 名称；OpenClaw 适配副本使用 snake_case `name: chinese_official_writing`，并保留 `metadata.openclaw`。

发布时使用 ClawHub CLI 指向 OpenClaw 适配目录：

```powershell
clawhub skill publish .\openclaw\skills\chinese_official_writing --slug chinese-official-writing --name "中文公文写作" --version 1.1.0 --tags "chinese,official-document,writing,gongwen,ai-compute"
```

### Claude Code

仓库包含 `.claude-plugin/plugin.json` 插件元数据和根目录 `skills/chinese-official-writing/` 技能副本。Claude Code 按插件目录读取时，可从插件根目录加载技能资源。

### Hermes

仓库包含 `hermes/skills/chinese-official-writing/`，并在该副本 `SKILL.md` 中加入顶层 `version` 和 `metadata.hermes`。该目录为 Hermes 风格技能副本。

适配目录由 `tools/sync_adapters.py` 从主技能目录同步生成：

```powershell
python .\tools\sync_adapters.py
```

## 目录结构

```text
.
├── .claude-plugin/
│   └── plugin.json             # Claude Code 插件元数据
├── chinese-official-writing/    # 主技能目录
│   ├── SKILL.md
│   ├── agents/
│   │   └── openai.yaml
│   ├── references/
│   │   ├── workflow.md
│   │   ├── official-style.md
│   │   ├── genre-checklist.md
│   │   ├── anti-ai-patterns.md
│   │   ├── format-gbt9704.md
│   │   ├── ai-compute-docs.md
│   │   └── review-checklist.md
│   └── scripts/
│       └── prose_lint.py
├── skills/
│   └── chinese-official-writing/ # Claude Code 技能副本
├── openclaw/
│   └── skills/
│       └── chinese_official_writing/ # OpenClaw/ClawHub 技能副本
├── hermes/
│   └── skills/
│       └── chinese-official-writing/ # Hermes 技能副本
├── tests/
│   ├── evidence/                # 脱敏测试摘要
│   └── prompts/                 # 脱敏合成提示
└── tools/
    ├── run_ablation.py
    └── sync_adapters.py
```

## 多工具适配状态

- **Codex / OpenAI Skill**：使用主目录 `chinese-official-writing/`，`SKILL.md` 包含完整 description、工作流、反例和引用资料。
- **OpenClaw / ClawHub**：使用 `openclaw/skills/chinese_official_writing/`，已按 snake_case 技能名生成适配副本，并保留 OpenClaw 元数据。
- **Claude Code**：使用 `.claude-plugin/plugin.json` 和根目录 `skills/chinese-official-writing/`，符合插件目录和技能目录分离的布局。
- **Hermes**：使用 `hermes/skills/chinese-official-writing/`，包含 Hermes 元数据和顶层版本字段。

适配依据参考 Claude Code 插件文档、Claude Agent Skills 文档、OpenClaw/ClawHub 技能文档和 Hermes Skills 文档。不同工具的目录习惯并不完全相同，因此本仓库以主技能目录为单一来源，通过同步脚本生成适配副本。

## 文稿检查脚本

`prose_lint.py` 只提示风险，不自动改写。

```powershell
python .\chinese-official-writing\scripts\prose_lint.py .\draft.md
python .\chinese-official-writing\scripts\prose_lint.py .\draft.docx
```

可检查：

- 高 AI 味句式；
- 旁白式、教学式表达；
- 口语化表达；
- 模板化过渡词；
- 算力类文档中的空泛技术表述。

## 脱敏测试结论

本仓库只保留脱敏测试摘要，不包含原始测试文稿、真实项目材料、内部文件名或用户数据。

### 通用公文脱敏对比测试

同一组常见中文公文任务下，一组不使用 Skill，只给最小写作提示；另一组使用本 Skill。结果显示：

- Skill 输出未触发已知 AI 句式和模板化表达检查；
- 非 Skill 输出出现二元包装句和模板化表达风险；
- 旧版通用测试摘要显示，独立审查更倾向 Skill 输出，认为其文种格式、正文视角、正式要素和初稿可用性更好。

### AI 算力类文档脱敏对比测试

同一组算力服务可研、GPU 租赁、云端成本对比、SLA 与数据安全任务下，一组不使用 Skill，另一组使用本 Skill。结果显示：

- Skill 输出更能说明“为什么租”“Token/资源需求从哪里来”“成本如何比较”“SLA 和并发如何保障”“验收和运维如何落地”；
- 非 Skill 输出通常能说明主题，但更像概括性说明；
- Skill 输出更接近技术类正式文稿初稿要求，便于继续补充数据、采购边界、验收指标和责任安排。

### 扩展泛化消融

扩展测试覆盖通知、请示、报告、说明、方案、申请、函、复函、批复、意见、决定、公告、公示、通报、会议纪要、工作要点、工作总结、调研报告、可研报告、实施方案、建设方案、审查材料等文体，并分别设置短文和长文任务。脱敏测试结果显示：

- 使用 Skill 的输出在文种要素、主办单位视角、事项落点和正式程度上更稳定；
- 不使用 Skill 的输出更容易出现旁白式开头、解释腔、口语化判断和泛化总结；
- 技术类长文中，Skill 输出对 Token 需求、费用换算、云端成本、租赁成本、SLA、并发、安全和验收的连接更清楚。

## 使用建议

- 写长文时先让 Skill 输出提纲和段落安排，再逐章写正文；
- 有真实数据时优先使用真实数据，没有数据时明确写成测算或留空；
- 单位有 Word 模板时，以单位模板优先；
- 生成的具体日期、金额、政策依据、机构名称和责任分工必须人工复核；
- 对正式上报、采购、合同、审计和涉法材料，应由相关专业人员复核后再使用。

## License

MIT-0。发布到 ClawHub 的 Skill 按 ClawHub/OpenClaw 规则视为 MIT-0 许可。
