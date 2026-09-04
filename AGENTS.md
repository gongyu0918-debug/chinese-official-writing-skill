# Agent 工作纪律

本文件是唯一活动开发纪律；[历史归档](maintenance/docs/archive/AGENTS-legacy-20260819.md)仅供追溯。产品规则只放 `chinese-official-writing/SKILL.md` 及其 `references/`；需求状态见[轻量规格](maintenance/specs/README.md)，发布事实见[证据索引](maintenance/docs/evidence/README.md)。

## 开发与验证

1. 新构想、核心能力与 Skill/Agent/工具链改动先查 GitHub、官方文档和社区，优先复用，保持职责清楚、实现简单。大 diff、长文件、review、第三方对比优先交 subagent，主代理复核结论。
2. 写作或 Hook 修稿能力先做最小 reference、prompt、路由或同稿修订原型，立即跑真实写稿或生命周期。
3. 目标风险可复现下降且无候选独有的事实、状态、文种、指令或直接可用性硬回退后，才补必要胶水、适配、镜像、组装、反控与回退；兜底须解决目标风险，不要求总体文采胜出。真实稿失败先修产品或停候选，不靠扩大量表、裁判和工程门替代质量改进。
4. Hook 比较同一 D0 的开关结果与最终选择，独立成稿仅作副作用观察。协议和胶水未变可迁移旧在线证据，列明当前未重跑的宿主。
5. 文档跑链接/结构检查与 `git diff --check`；产品在真实结果通过后跑相关 unit/smoke、quick validate 及必要编译/镜像检查。全量门原则上只在合并或发布前跑一次，核对上一发布 tag、ancestry、精确 diff、版本、清洁包、禁入文件与 fingerprint。

## Git 与外部操作

1. 修改前核对仓库、分支、HEAD、工作树、基线和授权，保留来源不明的改动。功能改动、较大改动及研究、基线、发布工作使用独立 worktree。
2. 所有代码和文档改动提交 Git，说明目的、范围和实际验证。每累计 5 次 commit 或范围明显扩大，暂停做 review、baseline diff、轻量消融和相关回归。
3. 未获当次明确授权，不合并 main、不推送、不移动 tag、不创建 Release、不上传或删除平台版本。
4. 禁止破坏性重置、force push 和无边界清理；删除须路径已核准、工作树干净、成果可恢复。不提交密钥、令牌、Cookie、登录态、私有地址或未脱敏数据。

## 产品边界

- `chinese-official-writing/` 为 canonical，其 `hooks/core/` 是唯一门禁核心、`hooks/adapters/` 为静态适配；`packages/` 放公开兼容包，`maintenance/` 放维护和证据，`output/` 默认不提交。
- main 不含付费提纲 Hook、胶水、测试和详细规格；`codex/paid-outline-review` 保持“当前 main + 付费提纲增量”。公开语义、共享 Hook 和修复按[同步规则](maintenance/specs/public-paid-sync.md)进入付费分支，提纲不得反向进入 main，付费发布另行授权。
- Skill 安装、companion 组装、插件安装、启用、信任和真实执行分别举证。仓库及仓内包使用根 [LICENSE](LICENSE)（MIT），第三方保留自身许可。

## 交付

报告摘要、branch、commit、实际命令与结果、量化变化、未完成和剩余风险。未运行不写通过，环境失败、无效样本、真实回退和 verifier 分歧如实保留。写作平实，UI 简洁，不堆解释、自证或装饰。
