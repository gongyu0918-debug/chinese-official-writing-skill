# v1.6.2 插件与 Hook 结构整理预注册

## 固定基线

- 工作树：`codex/v162-package-architecture`
- 固定基线：`2135fba6e05ee9a3d9c9f931237a9eb01b0cc107`
- 已发布产品基线：`v1.6.1^{commit}=239eb72edc9cee513a4f76c13b9ed38f223fe32b`
- 本轮只形成 v1.6.2 本地候选，不发布、不移动 tag、不修改任何宿主配置。

## 问题与证据

当前 canonical Skill 同时充当普通 Skill、Codex 插件根和 WorkBuddy/CodeBuddy 插件根，导致 `.codex-plugin/`、`.codebuddy-plugin/`、宿主 Hook 配置和 `skills/chinese-official-writing/SKILL.md` discovery shim 散落在普通 Skill 根。Claude Code 适配器又嵌套在 `hooks/claude-code/`，宿主边界不直观。

Claude Code 与 CodeBuddy 的官方插件规范均把 `skills/`、`hooks/` 和宿主 manifest 定义在各自插件根内；插件缓存不能依赖插件根外的相对路径。Codex 本地 validator 同样要求 `.codex-plugin/plugin.json` 所在目录形成完整插件根。因此不能只把 manifest 挪进子目录后继续用 `../../SKILL.md` 回指 canonical。

## 候选结构

```text
chinese-official-writing/
  SKILL.md
  agents/
  references/
  scripts/
  hooks/
    README.md
    gate_stop_hook.py
    host_gate_adapter.py
    host-capabilities.json
  plugins/
    codex/
      .codex-plugin/plugin.json
      hooks/hooks.json
      scripts/host_gate_adapter.py
      skills/chinese-official-writing/...
    codebuddy/
      .codebuddy-plugin/plugin.json
      hooks/hooks.json
      scripts/host_gate_adapter.py
      skills/chinese-official-writing/...
    claude-code/
      .claude-plugin/plugin.json
      hooks/hooks.json
      scripts/gate_stop_hook.py
      skills/chinese-official-writing/...
```

普通 Skill 根继续保留真实共享 Hook 核心。三个宿主插件均为自包含生成物；插件内 `skills/<name>/SKILL.md` 是宿主发现范式，不是第二套产品规则。普通 Skill 根不再保留 discovery shim 或宿主 manifest。

## 允许改动

1. 把 Codex、CodeBuddy、Claude Code manifest、Hook 配置和薄适配器归入 `plugins/<host>/`。
2. 将 `hooks/AGENT_GLUE.md` 改为 `hooks/README.md`，写清用途、启用、信任、事件、失败回退、验证范围和宿主入口。
3. 在普通 `SKILL.md` 中只增加一条条件式接引：用户要求启用或排查 Hook 时读取 `hooks/README.md`；普通写稿不加载该说明。
4. 由同步工具从 canonical 生成三个自包含插件和现有纯 Skill 镜像；不允许插件运行时越过自身根目录。
5. 将 Hook 运行超时、键长和摘要长度等散落数值改为具名常量或具名生成策略，行为保持不变。
6. 更新 SkillHub 构建契约，使 1.6.2 清洁包保留 `hooks/` 与 `plugins/` 的清晰层次。

## 明确排除

- 不合入 `length-band-hook-v162` 或 `under-length-hook-v162-v2`。两者真实写稿均为 HOLD；后者 D1 可采用为 0/5。当前产品不得宣称已有自动补字功能。
- 不在本原子拆分 `review_gate.py::evaluate_candidate`、`detect_transaction` 或 Hook 状态机。复杂度审计已确认前两者属于上帝函数风险，后续单独做行为不变拆分。
- 不改变交付门禁的 findings、D0/D1 选择、四次 Stop 上限、事实边界或正文写作规则。
- 不发布 GitHub、SkillHub、ClawHub 或 Red SkillHub。

## 验收门

1. canonical 根无 `.codex-plugin/`、`.codebuddy-plugin/` 和 `skills/`；三个插件根各自仅含一个宿主 manifest，并且没有 `../` 越界引用。
2. 三个插件的 Skill 正文、references、共享 scripts 和 Hook 核心与 canonical 字节一致；插件薄适配器只做宿主协议映射。
3. `hooks/README.md` 明确普通 Skill 不自动启用 Hook、D0 是冲突/失败回退、当前没有自动补字、各宿主验证边界。
4. 现有 Hook、review gate、package boundary、builder 和 adapter 单测全部通过；全量 unittest 与 Promptfoo stub smoke 通过。
5. Codex validator、Claude strict validator、Claude preflight、三宿主无模型事件 smoke、SkillHub 1.6.2 dry-run、quick validate、py_compile、sync 二次幂等和 `git diff --check` 通过。
6. 固定基线与候选的确定性写作消融不退化；canonical 写作正文除条件式 Hook 接引外不变化。
