# 可选交付门禁 Hook

这里保存真实可执行的共享 Hook 核心和宿主适配源。它不是普通写稿规则，也不会因为安装 Skill 自动启用。只有用户明确要求安装、启用、适配或排查 Hook 时，Agent 才需要读取本页。

## 能解决什么

Hook 在模型已经形成完整原稿 D0 后运行一次有界交付复核：保存 D0，调用 `scripts/review_gate.py` 检查已支持的事实、状态和结构约束，只在候选稿通过机械检查与语义核验后选择 D1；任一层失败、冲突或状态不完整时逐字回退 D0。它不会绕过宿主信任、权限或插件启用流程。

当前没有自动补足字数或自动压缩篇幅功能。历史篇幅候选在真实写稿中没有形成可采用的稳定 D1，未进入本目录。现有门禁也不能替代初稿完整性检查、事实核对或人工审稿。

## 三层边界

1. `SKILL.md` 与 references 决定写什么、如何写，先形成完整 D0。
2. `scripts/prose_lint.py` 是可选的只读提示工具，不改稿，也不向 Hook 传递报告。
3. 明确启用的生命周期 Hook 保存 D0，并按 `references/delivery-review-gate.md` 执行一次有界复核。协议冲突时只回退 D0，不重新进入写稿循环。

## 插件入口

三套插件都在 `plugins/` 下，彼此独立且自包含。不要只复制 manifest、`hooks/` 或 `scripts/`；插件缓存必须同时保留其 `skills/chinese-official-writing/` 运行副本。

如果本页是从某个已安装插件的 `skills/chinese-official-writing/hooks/` 中读取的，不要再向外寻找同级 `plugins/`；直接以宿主提供的 `PLUGIN_ROOT`、`CODEBUDDY_PLUGIN_ROOT` 或 `CLAUDE_PLUGIN_ROOT` 作为当前插件根。

| 宿主 | 插件根 | 使用方式 | 已验证边界 |
| --- | --- | --- | --- |
| Codex | `plugins/codex/` | 按 Codex 本地 marketplace 流程注册整个插件根，再由用户启用并确认 Hook 信任 | manifest 校验与隔离注册；尚不能据此宣称真实生命周期已验证 |
| WorkBuddy / CodeBuddy | `plugins/codebuddy/` | 当前会话显式加载整个插件根，例如 `codebuddy --plugin-dir plugins/codebuddy` | 官方 manifest 契约与本地校验；真实生命周期仍需独立实跑 |
| Claude Code | `plugins/claude-code/` | `claude --plugin-dir plugins/claude-code` | Claude Code 2.1.195 下已验证 UserPromptSubmit、PostToolUse:Read、Stop 与 D0 回退；Bash 和有效 D1 尚未验证 |

安装、插件注册、功能启用、Hook 信任和真实执行是五件事。任何 Agent 做胶水适配时，先读取本页与 `host-capabilities.json`，再核对宿主官方事件字段和插件根变量；没有官方契约或真实执行证据时，保持关闭并说明未知项。

## 共享调用链

```text
宿主 manifest
  -> 宿主 hooks/hooks.json
  -> 宿主适配器
  -> plugins/<host>/skills/chinese-official-writing/hooks/gate_stop_hook.py
  -> plugins/<host>/skills/chinese-official-writing/scripts/review_gate.py
```

Codex 和 CodeBuddy 的适配器由根 `hooks/host_gate_adapter.py` 同步生成；Claude Code 使用独立适配器。三者只转换宿主事件与返回协议，不修改门禁发现、修订、验证、D0/D1 选择或四次 Stop 上限。

三个插件的 `UserPromptSubmit`、`PostToolUse` 命令上限均为 10 秒，`Stop` 上限为 30 秒；同步器用具名策略校验这三项，超时后按宿主协议失败开放或回退 D0。共享核心调用 `review_gate.py` 的内部上限为 20 秒，由代码常量统一控制。

## 验证顺序

1. 运行 `python -B maintenance/tools/sync_adapters.py`，确认第二次同步无差异。
2. 分别校验三个插件根；Claude Code 可运行 `python -B maintenance/tools/preflight_claude_hooks.py`。
3. 在隔离的宿主配置和数据目录中复放 UserPromptSubmit、PostToolUse:Read、Stop，确认插件内部路径、D0 回退和审计状态。
4. 只有另行授权后才运行真实模型写稿 A/B。静态 manifest 通过不能写成 Hook 已真实生效。

能力状态与已验证范围以 [`host-capabilities.json`](host-capabilities.json) 为准。
