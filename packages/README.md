# 兼容包目录

这里保存由 canonical Skill 派生的平台兼容包。写作规则以 `chinese-official-writing/` 为唯一来源；兼容包只调整目录、名称或平台元数据。

| 目录 | 用途 |
| --- | --- |
| `agent-skills/` | 通用 Agent Skills 兼容面，也供 MiniMax、GLM、ZCode、Kimi Code CLI、TRAE 等读取通用 Skill 结构 |
| `qwen-code/` | Qwen Code 兼容面 |
| `qwenwork/` | QwenWork（Qwen 办公）静态 Skill 兼容面，不声明 Hook 生命周期 |
| `hermes/` | Hermes 兼容面 |
| `openclaw/` | OpenClaw 兼容面，不含交付 Hook |
| `red-skillhub/` | Red SkillHub 专用发布面 |

这些目录保留普通 Skill、references 和脚本。Hook 已移至独立分支，后续归 Pro 专属；保存位置和许可界限见 [Hook 去向便条](../maintenance/docs/pro-hooks-next.md)。
