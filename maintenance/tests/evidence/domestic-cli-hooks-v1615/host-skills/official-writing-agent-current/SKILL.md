---
name: official-writing-agent-current
description: 仅用于当前仓库通用 Agent Skills 包的隔离真实写稿验证；用户明确调用时使用。
disable-model-invocation: true
---

# 当前 Agent Skills 包验证入口

先使用只读工具完整读取 `packages/agent-skills/skills/chinese-official-writing/SKILL.md`，再严格执行该文件的规则。此后将 `packages/agent-skills/skills/chinese-official-writing/` 视为 Skill 根目录，其中所有相对 reference 路径均从该目录解析。不得改用任何用户目录或全局目录下的同名 Skill。

只交付用户要求的稿件，不提及本验证入口。
