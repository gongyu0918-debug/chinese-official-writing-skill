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

## 安装 Prompt

如果你的 agent 支持通过自然语言执行安装任务，可以直接复制下面的安装 prompt。这里默认 agent 能访问 GitHub，不要求额外安装 SkillHub、ClawHub 或其他 CLI；prompt 只说明从哪个仓库拉取、安装哪个目录、保留哪些文件。

### Codex / OpenAI Skill

安装 prompt：

```text
请从 GitHub 仓库 https://github.com/gongyu0918-debug/chinese-official-writing-skill 拉取 chinese-official-writing/ 目录，并将其安装到 Codex 的 skills 目录，目标路径为 ~/.codex/skills/chinese-official-writing。只安装该 Skill 目录，不安装 tests/、output/ 或其他适配目录；安装后确认 SKILL.md、references/、scripts/ 和 agents/ 均已保留。
```

手动命令：

```powershell
Copy-Item -Recurse .\chinese-official-writing "$env:USERPROFILE\.codex\skills\chinese-official-writing"
```

### Claude Code

安装 prompt：

```text
请从 GitHub 仓库 https://github.com/gongyu0918-debug/chinese-official-writing-skill 拉取完整仓库，并将仓库根目录作为 Claude Code 插件目录。安装后确认 .claude-plugin/plugin.json 存在，并加载 skills/chinese-official-writing/ 作为中文公文写作 Skill 目录；不要把 openclaw/、hermes/ 或 output/ 当作 Claude Code 主技能目录。
```

本地插件方式：

```bash
claude --plugin-dir .
```

### OpenClaw / ClawHub

安装 prompt：

```text
请从 GitHub 仓库 https://github.com/gongyu0918-debug/chinese-official-writing-skill 拉取 openclaw/skills/chinese_official_writing/ 目录，并将其安装为 OpenClaw/ClawHub 可识别的 chinese-official-writing 技能。该适配目录的 frontmatter 使用 name: chinese_official_writing；安装后确认显示名称为“中文公文写作”，用于中文公文、可研报告、建设方案和 AI 算力采购租赁类正式材料写作。
```

已发布版本：

`chinese-official-writing@1.2.4`

### deepseek-tui

安装 prompt：

```text
请从 GitHub 仓库 https://github.com/gongyu0918-debug/chinese-official-writing-skill 拉取 .agents/skills/chinese-official-writing/ 目录，并将其作为 deepseek-tui 的中文公文写作 Skill。若当前项目只识别 skills/，则改为拉取 skills/chinese-official-writing/。只安装对应的 Skill 目录，不安装 tests/ 或 output/；安装后进入 deepseek-tui，使用 /skills 确认可见，再用 /skill chinese-official-writing 启用。
```

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

### Hermes

安装 prompt：

```text
请从 GitHub 仓库 https://github.com/gongyu0918-debug/chinese-official-writing-skill 拉取 hermes/skills/chinese-official-writing/ 目录，并将其安装为 Hermes 的 chinese-official-writing 技能。安装时保留 SKILL.md、references/ 和 scripts/，不要使用根目录 chinese-official-writing/ 替代 Hermes 适配目录。
```

手动复制：

```powershell
Copy-Item -Recurse .\hermes\skills\chinese-official-writing "<Hermes skills 目录>\chinese-official-writing"
```

## 安装后试用

```text
使用中文公文写作 Skill，起草一份项目请示。要求一文一事，先写请批事项，再写依据、现状、资金或资源需求，结尾使用正式请批语。
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
