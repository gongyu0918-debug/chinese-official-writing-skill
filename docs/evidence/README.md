# 项目维护历史索引

本目录保存不需要在每次 Codex run 中注入、但必须长期可追溯的项目维护记录。这里的材料是证据和历史背景，不是当前运行时指令；当前规则以仓库根 [`AGENTS.md`](../../AGENTS.md) 为准。

## AGENTS 历史快照

- [`AGENTS-history-through-v1.5.39.md`](AGENTS-history-through-v1.5.39.md) 是精简前根 `AGENTS.md` 的完整 Git blob 快照，覆盖 1.4.1—1.5.39 的发布、接手、候选实验、阻断、回滚、评测和平台传播流水。
- 为保持迁移前后事实和检索关键词完全一致，快照正文未改写。正文中的 `tests/evidence/...`、`tools/...`、`output/...` 等路径均以仓库根为起点解释，不以本目录为起点。
- 快照中的“当前”“最新”“待发布”等措辞只表示记录写入当时的状态，不覆盖根 `AGENTS.md` 的当前发布基线。

## 逐版发布证据

- 1.5.x 的发布门禁、提交与 tag、清洁包、平台回执和传播状态保存在 `tests/evidence/release-1.5.x.md`。
- 当前最新发布证据：[`release-1.5.41.md`](../../tests/evidence/release-1.5.41.md)。
- 相邻正式版本：[`release-1.5.40.md`](../../tests/evidence/release-1.5.40.md)、[`release-1.5.39.md`](../../tests/evidence/release-1.5.39.md)。
- 1.5.39 自包含 A/B、匿名裁决及 Word 对齐修复：[`v1539-compact-repro-pack-20260808.md`](../../tests/evidence/v1539-compact-repro-pack-20260808.md)。
- 其他预注册、候选、盲审、消融和真实写稿记录继续在 `tests/evidence/` 中按版本号、候选代号或日期检索。

## 根 AGENTS.md 的控制面依据

- [OpenAI 官方 AGENTS.md 指南](https://learn.chatgpt.com/docs/agent-configuration/agents-md)：Codex 每次 run 构建指令链，按全局到项目根、再到当前目录合并；`project_doc_max_bytes` 默认 32 KiB，并建议规则保持简洁。
- [agentsmd/agents.md](https://github.com/agentsmd/agents.md)：把 `AGENTS.md` 定位为面向 coding agents 的 README，示例集中于开发环境、测试和 PR 约束。
- [agentmd/agent.md](https://github.com/agentmd/agent.md)：建议的工程章节包括项目结构、build/test、代码风格、架构、测试、安全、Git 和配置。
- 本仓库据此把根 `AGENTS.md` 限定为工程控制面；产品写作行为只保存在 canonical Skill 和 references，不在根文件复述。

## 取证规则

1. 判断当前发布状态时，优先核对根 `AGENTS.md` 与对应 `release-<version>.md`，再按需回看历史快照。
2. 候选基线、发布提交、annotated tag object、tag 解引用提交、GitHub Release、平台上传回执、公开 latest 和审核/索引传播是不同事实，不得互相代替。
3. 历史记录含 pending 或公开索引滞后时，不得据此重复提交；应先核对正式回执和当前公开状态。
4. 未发布候选和隔离实验不得改称正式版本，也不得从历史快照直接恢复到产品树。
