# 1.4.8 去 AI 味最小借鉴与记忆机制边界

本轮只吸收社区去 AI 味技能中的抽象检查维度，不复制代码、正则、模板正文、大段 prompt 或固定话术。

## 已核验来源

- `aigc-shed`：论文 AIGC 降重导向，包含检测器专项、目标疑似率、多模型接力和进化日志。只借鉴“模式扫描”思路，不采纳规避检测、目标疑似率、强制每段技法、个人声音、反问和毛边感。
- `humanize-zh`：通用中文人味化，强调口语化、个人色彩和聊天感。公文场景只借鉴“检查句式过齐、连接词重复”的思路，不采纳“说白了”“我觉得”“朋友聊天”等表达。
- `de-ai-writing-cn`：去模板化、低清单堆砌、事实与判断分离。可抽象为公文的“句群节奏、事实锚点、审稿先诊断后修改”。
- Codex 官方 memory 文档：稳定偏好可由 Codex memory 辅助召回，但必须始终适用的团队规则应放在 `AGENTS.md` 或仓库文档。
- Claude Code memory/skills 文档：memory 是可编辑的本地 Markdown；技能应保持简洁，支持文件按需加载，长记忆或宽触发会降低遵循度。
- OpenAI Codex skills/OpenClaw skills 文档：技能由 `SKILL.md` 和可选 `references/`、`scripts/`、`assets/` 组成，应使用渐进式披露，避免把所有内容塞进入口。
- 社区 writing/secretary/self-improving 类记忆技能：可参考“显式记忆、短文件、按需读取”形式，但其安全审计也提示了宽触发、误记、跨项目污染和静默持久化风险。
- Qwen Code 官方文档：项目级 Skill 放在 `.qwen/skills/<skill-name>/SKILL.md`，个人级 Skill 放在 `~/.qwen/skills/<skill-name>/SKILL.md`，通过 `/skills` 查看。
- MiniMax 官方 skills 仓库：采用 `skills/<skill-name>/SKILL.md` 结构，要求技能名为 kebab-case，强调单一目的、文件精简和不要硬编码密钥。
- 智谱 GLM Skills 仓库：采用 `skills/` 集合，面向 Claude Code、OpenCode、OpenClaw、AutoClaw 等 agent 架构，适合共用通用 `skills/` 目录。
- Kimi Code CLI 仓库：当前项目已出现 `.agents/skills` 目录，同时 Kimi CLI 正在演进为 Kimi Code CLI；本仓库只按通用 Agent Skills 目录给出兼容安装提示，不新增 Kimi 专属镜像。
- TRAE 文档和社区资料：支持 `SKILL.md`，可使用 `.agents/skills/`，无需新增专属目录。
- 百度 Comate AI IDE 文档：支持 `.agents/skills/`、`.comate/skills/` 和 `~/.comate/skills/`，且能从 Claude、Codex、Cursor 等外部 agent 目录加载技能，因此本仓库沿用现有 `.agents/skills/`。

## 本轮采纳

1. 新增“句群节奏和模板化痕迹”软性审稿项，覆盖句首重复、连接词链、句长同质化、口号式收束和清单堆叠替代论证。
2. 明确公文去 AI 味不是聊天化，不加入第一人称、反问、口语插入、情绪化判断或故意不完美表达。
3. 用户只要求审稿时，仍输出位置、风险层级和修改建议；用户要求代改时才输出改后正文。
4. 新增 `.qwen/skills/` 目录镜像和 GitHub README 安装提示；MiniMax Skills、GLM Skills（Z.ai/智谱）、AutoClaw、Kimi Code CLI、TRAE、Baidu Comate AI IDE 等共用 `skills/` 或 `.agents/skills/`，不为同一配方重复建镜像。

## 本轮不采纳

- 不新增 lint 硬规则。
- 不新增检测器、疑似率、规避检测、多模型接力、回译链或自进化日志。
- 不新增大规模禁词表。
- 不把通用人味化迁移成公众号口吻、第一人称、聊天化、情绪化或口语化。
- 不把个性化记忆写入默认技能流程。

## 记忆机制建议

目前不建议并入 1.4.8。理由：

- 公文写作技能应优先保持轻量、可迁移、可发布；个人偏好属于本地状态，不适合写进公开发行包。
- “申请默认用妥否，请批示”“常用公司名”等偏好有价值，但必须来自用户明确要求记住或多次确认，不应由模型从单次对话自动推断。
- 若后续实现，建议做成可选本地层，而不是默认技能层：例如 `~/.codex/chinese-official-writing-profile/preferences.md`，只保存少量分文种偏好，并在用户明确同意后写入。
- 文件应控制在 100 行以内，按文种分组；只记录稳定偏好、常用单位名、常用落款、结尾语偏好和明确禁用项，不记录敏感正文、审批内容、金额细节或内部文件原文。
- 读取也应是按需软参考：同文种起草时可参考；本轮用户指令、文种功能和事实边界始终优先于记忆。
