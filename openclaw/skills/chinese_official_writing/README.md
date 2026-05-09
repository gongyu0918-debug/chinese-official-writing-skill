# 中文公文写作 Skill

[![ClawHub](https://img.shields.io/badge/ClawHub-chinese--official--writing-blue)](https://github.com/gongyu0918-debug/chinese-official-writing-skill)
[![License](https://img.shields.io/badge/license-MIT--0-green)](LICENSE)
[![Language](https://img.shields.io/badge/language-中文公文-red)](#适用范围)

面向中文正式材料写作的 Agent Skill，专门约束 agent 生成更接近正式公文、工作材料和技术类正式文稿的草稿。

它重点解决三个问题：

- **文种不稳**：请示写成报告、说明写成方案、函写成通知。
- **视角漂移**：正文像外部顾问讲解，缺少发文单位、报告单位或项目单位立场。
- **AI 味重**：出现二元对照句、旁白式开场、口语化判断等解释腔表达。

对 AI 算力、服务器租赁、云端部署成本对比等材料，Skill 会额外约束论证链条：**需求来源 -> Token/资源测算 -> 成本比较 -> SLA/并发/安全/验收**。

## 适用范围

| 类型 | 覆盖内容 |
| --- | --- |
| 常见公文 | 通知、请示、报告、说明、方案、申请、函、复函、批复、意见、决定、公告、公示、通报、会议纪要 |
| 工作材料 | 工作要点、工作总结、调研报告、可研报告、实施方案、建设方案、审查材料 |
| 技术类正式材料 | AI 算力服务可研、算力资源采购或租赁、GPU/服务器租赁、云端部署成本对比、SLA 与并发保障、数据安全、运维验收 |
| Word 文稿 | 带批注文档改写、压缩、顺稿、去口语化、统一文风 |

不建议用于英文写作、文学创作、营销软文、社交媒体文案。涉及法律、财务、采购、审计和政策依据的正式上报材料，应由专业人员最终复核。

## 核心能力

- **文种路由**：按通知、请示、报告、函、批复、会议纪要等不同文种补齐必要要素。
- **文稿蓝图**：先搭提纲，再列段落，再逐段成文，避免整篇一次性铺开后失控。
- **视角控制**：从发文单位、项目单位或报告单位出发写，不写成教学说明。
- **低 AI 味审查**：内置反例库和 `prose_lint.py`，提示二元包装句、旁白句、口语化判断和空泛技术表述。
- **算力类专项约束**：对 Token、云端成本、租赁服务、SLA、并发、安全和验收做链式论证。
- **多平台适配**：已适配 Codex/OpenAI Skill、Claude Code、OpenClaw/ClawHub、deepseek-tui 和 Hermes。

## 安装 Prompt

如果你的 agent 支持通过自然语言执行安装任务，可以直接复制下面的安装 prompt。这里默认 agent 能访问 GitHub，不要求额外安装 SkillHub、ClawHub 或其他 CLI；prompt 只说明从哪里拉取、安装哪个目录、保留哪些文件。

### Codex / OpenAI Skill

```text
请从 GitHub 仓库 https://github.com/gongyu0918-debug/chinese-official-writing-skill 拉取 chinese-official-writing/ 目录，并将其安装到 Codex 的 skills 目录，目标路径为 ~/.codex/skills/chinese-official-writing。只安装该 Skill 目录，不安装 tests/、output/ 或其他适配目录；安装后确认 SKILL.md、references/、scripts/ 和 agents/ 均已保留。
```

### OpenClaw / ClawHub

```text
请从 GitHub 仓库 https://github.com/gongyu0918-debug/chinese-official-writing-skill 拉取 openclaw/skills/chinese_official_writing/ 目录，并将其安装为 OpenClaw/ClawHub 可识别的 chinese-official-writing 技能。该适配目录的 frontmatter 使用 name: chinese_official_writing；安装后确认显示名称为“中文公文写作”，用于中文公文、可研报告、建设方案和 AI 算力采购租赁类正式材料写作。
```

已发布版本：`chinese-official-writing@1.2.6`

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

## 快速试用

通用公文：

```text
使用中文公文写作 Skill，起草一份项目请示。要求一文一事，先写请批事项，再写依据、现状、资金或资源需求，结尾使用正式请批语。
```

技术类正式材料：

```text
使用中文公文写作 Skill，起草一段 AI 算力资源租赁方案。要求说明 Token 需求从哪里来、云端部署成本为什么会上升、租赁服务如何保障 SLA、并发和数据安全。
```

审稿与降 AI 味：

```text
使用中文公文写作 Skill，检查这段建设方案是否存在视角错位、解释腔、口语化判断和二元对照句，只给出需要修改的位置和建议。
```

## 目录说明

| 路径 | 用途 |
| --- | --- |
| `chinese-official-writing/` | 主技能目录，供 Codex/OpenAI Skill 使用 |
| `skills/chinese-official-writing/` | Claude Code 与部分通用 skills 目录约定 |
| `.agents/skills/chinese-official-writing/` | deepseek-tui 与兼容 `.agents/skills` 的 agent |
| `openclaw/skills/chinese_official_writing/` | OpenClaw/ClawHub 发布目录 |
| `hermes/skills/chinese-official-writing/` | Hermes 适配目录 |

修改主技能目录后，运行同步脚本更新各平台副本：

```powershell
python .\tools\sync_adapters.py
```

## 评测数据

仓库只保留脱敏测试摘要，不保存原始公文、真实项目材料、内部路径或个人信息。

### 本地 smoke/regression 消融

本地脚本生成 Baseline 与 Skill 两组合成输出，用于检查文种覆盖、反 AI 规则和算力类论证链。每类文种 10 次，共 270 个任务。

| 指标 | Baseline | Skill |
| --- | ---: | ---: |
| 任务数 | 270 | 270 |
| high 风险 | 351 | 0 |
| medium 风险 | 432 | 0 |
| low 风险 | 811 | 1 |
| 总风险 | 1594 | 1 |

### DeepSeek A/B/C 隔离消融

Writer A 显式使用本 Skill，Writer B 只按普通提示生成，Evaluator C 使用独立上下文评估。全量 A/B 写稿覆盖 27 类文体、每类 10 次，共 540 段对比样稿；C 有效评估 7/9 个批次，自动解析出的明确判断为 A=29、B=3、Tie=1。未返回的 2 个批次单列为待复跑，不纳入结论。

下表列出每个文种的消融次数和本地风险扫描结果。由于本地 smoke/regression 使用相同数量、相同结构的合成反例模板，各文种 Baseline 风险数均为 59；Skill 输出在文种层面未命中风险，另有 1 条 Skill 全局术语重复提示未归入单一文种。该表用于验证规则覆盖和回归稳定性，不等同于真实公文语料的自然分布。

| 文种 | 本地消融次数 | Baseline 风险 | Skill 风险 | DeepSeek A/B 生成 | C 独立评估 |
| --- | ---: | ---: | ---: | ---: | --- |
| 通知 | 10 | 59 | 0 | 10 | 待复跑 |
| 请示 | 10 | 59 | 0 | 10 | 待复跑 |
| 报告 | 10 | 59 | 0 | 10 | 待复跑 |
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
| 工作要点 | 10 | 59 | 0 | 10 | 待复跑 |
| 工作总结 | 10 | 59 | 0 | 10 | 待复跑 |
| 调研报告 | 10 | 59 | 0 | 10 | 待复跑 |
| 可研报告 | 10 | 59 | 0 | 10 | 有效 |
| 实施方案 | 10 | 59 | 0 | 10 | 有效 |
| 建设方案 | 10 | 59 | 0 | 10 | 有效 |
| 审查材料 | 10 | 59 | 0 | 10 | 有效 |
| 算力服务可研报告 | 10 | 59 | 0 | 10 | 有效 |
| 算力资源采购方案 | 10 | 59 | 0 | 10 | 有效 |
| GPU/服务器租赁技术需求 | 10 | 59 | 0 | 10 | 有效 |
| 云端部署成本对比说明 | 10 | 59 | 0 | 10 | 有效 |
| 技术服务审查材料 | 10 | 59 | 0 | 10 | 有效 |

评测结论只证明规则约束和工作流在测试样本中有效，不代表具体事实、政策依据、金额、采购结论已经通过业务审核。

DeepSeek A/B/C 的判断标准包括文种契合、主体视角、段落逻辑、正式语气、低 AI 味表达，以及算力类文稿中的“需求 -> Token/资源 -> 成本 -> SLA/安全/验收”链条。Tie 表示评估者未给出明确优劣或两组输出各有优势。

## 文稿检查脚本

`prose_lint.py` 用来检查草稿中的高风险表达。它只提示问题，不自动改写。

```powershell
python .\chinese-official-writing\scripts\prose_lint.py .\draft.md
python .\chinese-official-writing\scripts\prose_lint.py .\draft.docx
```

可检查的风险包括：二元包装句、旁白式表达、教学腔、口语化判断、模板化过渡词，以及算力类文档中缺少指标支撑的空泛技术表述。

## 设计取舍

这个 README 采用开源项目常见的结构：先说明定位，再给安装、快速试用、功能表、评测数据和维护命令。这样做是为了让 ClawHub 用户在前几屏内判断三件事：能不能用、怎么装、效果有没有证据。

本 Skill 参考了社区同类 Skill 的格式规范、文种路由和模板思路，但没有复制任何第三方项目内容；公文风格以公开公文写作规则和公开示例抽象出的句式模式为基础。

## 发布前检查

```powershell
python .\chinese-official-writing\scripts\prose_lint.py README.md chinese-official-writing\SKILL.md
python .\tools\run_ablation.py --out output\expanded-ablation
python .\tools\run_deepseek_ablation.py --genres-per-batch 3 --out output\deepseek-public-ablation-v2
```

## License

MIT-0。发布到 ClawHub 的 Skill 按 ClawHub/OpenClaw 规则视为 MIT-0 许可。
