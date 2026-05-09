---
name: chinese_official_writing
description: 用于起草、改写和复核中文公文及正式工作材料，覆盖通知、请示、报告、说明、方案、申请、函、复函、批复、意见、决定、公告、公示、通报、会议纪要、工作要点、工作总结、调研报告、可研报告、实施方案、建设方案、审查材料，以及 AI 算力服务可研、算力采购或租赁、GPU/服务器租赁、技术服务需求等材料；强调文种准确、主体视角稳定、论点清楚、数据可追溯、公文语气自然、低 AI 味。不用于英文写作。
license: MIT-0
metadata:
  openclaw:
    version: "1.2.10"
    emoji: "📝"
    tags:
      - chinese
      - official-document
      - writing
      - gongwen
      - ai-compute
---

# 中文公文写作 Skill

[![ClawHub](https://img.shields.io/badge/ClawHub-chinese--official--writing-blue)](https://clawhub.ai/gongyu0918-debug/chinese-official-writing)
[![License](https://img.shields.io/badge/license-MIT--0-green)](LICENSE)
[![Language](https://img.shields.io/badge/language-中文公文-red)](#适用范围)

中文公文写作 Skill 面向正式材料起草、改写和复核场景，提供文种路由、文稿蓝图、主体视角校验、低 AI 味审查和技术类材料专项论证约束。

主要覆盖文种要素校正、主体视角统一、句式风险压降和技术类材料论证。AI 算力、服务器租赁、云端部署成本对比等材料按 **需求来源 -> Token/资源测算 -> 成本比较 -> SLA/并发/安全/验收** 组织正文。

## 适用范围

| 类型 | 覆盖内容 |
| --- | --- |
| 常见公文 | 通知、请示、报告、说明、方案、申请、函、复函、批复、意见、决定、公告、公示、通报、会议纪要 |
| 工作材料 | 工作要点、工作总结、调研报告、可研报告、实施方案、建设方案、审查材料 |
| 技术类正式材料 | AI 算力服务可研、算力资源采购或租赁、GPU/服务器租赁、云端部署成本对比、SLA 与并发保障、数据安全、运维验收 |
| Word 文稿 | 带批注文档改写、压缩、顺稿、去口语化、统一文风 |

适用边界为中文正式材料。英文写作、文学创作、营销软文、社交媒体文案不在覆盖范围内。法律、财务、采购、审计和政策依据类正式上报材料保留人工复核环节。

## 核心能力

- **文种路由**：按通知、请示、报告、函、批复、会议纪要等不同文种补齐必要要素。
- **文稿蓝图**：先搭提纲，再列段落，再逐段成文，避免整篇一次性铺开后失控。
- **视角控制**：从发文单位、项目单位或报告单位出发写，不写成教学说明。
- **低 AI 味审查**：内置反例库和 `prose_lint.py`，提示二元包装句、旁白句、口语化判断和空泛技术表述。
- **算力类专项约束**：对 Token、云端成本、租赁服务、SLA、并发、安全和验收做链式论证。
- **多平台适配**：已适配 Codex/OpenAI Skill、Claude Code、OpenClaw/ClawHub、deepseek-tui 和 Hermes。

## 安装 Prompt

### Codex / OpenAI Skill

```text
请从 GitHub 仓库 https://github.com/gongyu0918-debug/chinese-official-writing-skill 拉取 chinese-official-writing/ 目录，并将其安装到 Codex 的 skills 目录，目标路径为 ~/.codex/skills/chinese-official-writing。只安装该 Skill 目录，不安装 tests/、output/ 或其他适配目录；安装后确认 SKILL.md、references/、scripts/ 和 agents/ 均已保留。
```

### OpenClaw / ClawHub

```text
请从 GitHub 仓库 https://github.com/gongyu0918-debug/chinese-official-writing-skill 拉取 openclaw/skills/chinese_official_writing/ 目录，并将其安装为 OpenClaw/ClawHub 可识别的 chinese-official-writing 技能。该适配目录的 frontmatter 使用 name: chinese_official_writing；安装后确认显示名称为“中文公文写作”，用于中文公文、可研报告、建设方案和 AI 算力采购租赁类正式材料写作。
```

已发布版本：`chinese-official-writing@1.2.10`

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
| `.agents/skills/chinese-official-writing/` | deepseek-tui 与兼容 `.agents/skills` 的 agent |
| `openclaw/skills/chinese_official_writing/` | OpenClaw/ClawHub 发布目录 |
| `hermes/skills/chinese-official-writing/` | Hermes 适配目录 |

同步各平台副本：

```powershell
python .\tools\sync_adapters.py
```

## 评测数据

公开仓库保留脱敏测试摘要，不保存原始公文、真实项目材料、内部路径或个人信息。

### 本地 smoke/regression 消融

测试任务分为 Baseline 与 Skill 两组，覆盖文种适配、反 AI 规则和算力类论证链。每类文种 10 次，共 270 个任务。

| 指标 | Baseline | Skill |
| --- | ---: | ---: |
| 任务数 | 270 | 270 |
| high 风险 | 351 | 0 |
| medium 风险 | 432 | 0 |
| low 风险 | 811 | 1 |
| 总风险 | 1594 | 1 |

### DeepSeek A/B/C 隔离消融

Writer A 调用技能规则，Writer B 按普通提示生成，Evaluator C 使用独立上下文评估。A/B 写稿覆盖 27 类文体、每类 10 次，共 540 段对比样稿；C 有效评估 7/9 个批次，自动解析出的明确判断为 A=29、B=3、Tie=1。未返回的 2 个批次单列为待复跑。

本地 smoke/regression 采用相同数量、相同结构的合成反例模板。各文种 Baseline 风险数均为 59；Skill 输出在文种层面未命中风险，另有 1 条全局术语重复提示未归入单一文种。

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

评测范围限定为脱敏测试样本。事实、政策依据、金额和采购结论保留人工复核环节。

DeepSeek A/B/C 评估项：文种契合、主体视角、段落逻辑、正式语气、低 AI 味表达，以及算力类文稿中的“需求 -> Token/资源 -> 成本 -> SLA/安全/验收”链条。Tie 表示未形成明确优劣或两组输出各有优势。

## 文稿检查脚本

`prose_lint.py` 检查草稿中的高风险表达。脚本仅提示问题，不自动改写。

```powershell
python .\chinese-official-writing\scripts\prose_lint.py .\draft.md
python .\chinese-official-writing\scripts\prose_lint.py .\draft.docx
```

可检查的风险包括：二元包装句、旁白式表达、教学腔、口语化判断、模板化过渡词，以及算力类文档中缺少指标支撑的空泛技术表述。

## 发布前检查

```powershell
python .\chinese-official-writing\scripts\prose_lint.py README.md chinese-official-writing\SKILL.md
python .\tools\run_ablation.py --out output\expanded-ablation
python .\tools\run_deepseek_ablation.py --genres-per-batch 3 --out output\deepseek-public-ablation-v2
```

## License

MIT-0。发布到 ClawHub 的 Skill 按 ClawHub/OpenClaw 规则视为 MIT-0 许可。

## Agent 使用规则

安装后执行写作任务时，仍按以下规则处理：

1. 先确认文种、受文对象、发文或报告主体、核心结论、必要数据、最新底稿和用户批注。
2. 成文前先搭文稿蓝图：提纲 -> 段落安排 -> 小段要点。
3. 按章节或段落生成正文，每段只服务一个论点，通常按“结论前置、事实支撑、判断归纳、事项落点”展开。
4. 从发文单位、报告单位、项目单位或主管单位视角写，不使用旁观者、教师或评论员口吻。
5. 数据和判断要可追溯；不编造实际数据，测算和预估必须标明性质。
6. 起草算力、采购、租赁或服务器租赁材料时，论证重点放在需求来源、Token/资源换算、成本比较、SLA、并发、安全、交付和验收。
7. 检查 `.txt`、`.md` 或 `.docx` 草稿时，可使用 `scripts/prose_lint.py`。脚本只提示风险，不自动改写。
