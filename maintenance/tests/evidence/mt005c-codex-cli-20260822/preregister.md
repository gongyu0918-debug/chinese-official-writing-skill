# MT-005c Codex CLI 隔离 A/B 预注册

## 目标

只验证把 description 末尾受众句合入开头后，Codex CLI 的隐式触发、相邻误触发和真实成稿是否出现可归因变化。该补充试验不替代既有五路 Codex Desktop 三十份有效稿，也不扩大到其他 description 枚举。

## 固定差异

- 两臂从当前集成分支同一份 `chinese-official-writing/` 机械复制，SKILL 正文、references、scripts 和 hooks 完全相同。
- baseline 使用204字 description；candidate 只替换为193字 description，减少11字。
- 运行前必须证明两个 Skill 树只有 canonical `SKILL.md` 的 description 单行不同。

## 隔离

- 使用 Codex CLI `0.144.6`、`--ignore-user-config`、`--ignore-rules`、`--ephemeral`、`--sandbox read-only`。
- 每臂位于独立临时仓库的 `.agents/skills/chinese-official-writing/`。
- 用单次 CLI 配置覆盖禁用 `C:/Users/admin/.agents/skills/chinese-official-writing/SKILL.md` 与 `C:/Users/admin/.codex/skills/chinese-official-writing/SKILL.md`；不修改用户配置。
- trace 出现任一用户级同名 Skill 路径即记 `TECHNICAL_INVALID`。

## 样本和顺序

固定三题及顺序见 `cases.json`：行业协会通知、学校系统通知、小红书社团招新负向边界。每题两臂各一次，共6次；使用 `gpt-5.6-terra`、`medium`，不自动替换模型、不重试质量失败。

## 判定

- 正向题必须由 trace 证明读取本臂精确 `SKILL.md`，并交付非空正文；负向题不得读取该 Skill。
- 正文必须保留 `cases.json` 的 required 项，不得出现 forbidden 项。一般目的、即时作用或低强度动作按既有规则接受，不把措辞差异机械判成失败。
- 任一非零退出、空正文、用户级同名 Skill 污染或 trace 无法归因均记技术无效，不进入写稿胜负。
- candidate 两个正向均触发、负向不触发且无 candidate 独有硬回退，才可与既有五路证据共同支持接入；若结果相同，只证明 CLI 下不劣，不冒充 description 改善。
