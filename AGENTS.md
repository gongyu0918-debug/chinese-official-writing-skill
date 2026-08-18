# Agent 工作纪律

## 当前指令

本文件是仓库唯一活动开发纪律。旧版长文已移至 [AGENTS 历史归档](maintenance/docs/archive/AGENTS-legacy-20260819.md)，只供追溯，不读取为当前指令。

产品写稿规则只写入 `chinese-official-writing/SKILL.md` 与 `references/`；需求、状态和覆盖关系见 [轻量规格](maintenance/specs/README.md)，发布事实见 [证据索引](maintenance/docs/evidence/README.md)。

## 真实结果优先

1. 写作规则、文种规则、语言质量或 Hook 修稿能力，先做最小 reference、prompt、强制路由或同稿修订原型，立即运行少量真实写稿或真实生命周期。
2. 只有目标问题得到可复现改善，且没有候选独有的事实、状态、文种、指令或直接可用性硬回退，才开始补 coordinator、adapter、组装、镜像和故障回退。新增兜底能力不要求总体文采票数胜过旧版，但必须解决目标风险。
3. 真实稿失败时先修产品或停止候选；不得用扩大量表、增加裁判、重复全量测试或堆工程门替代质量改进。
4. 真实结果通过后，只补本改动直接需要的确定性反控、路由、镜像、hash 和故障回退。全量测试原则上只在准备合并或发布前运行一次。
5. Hook 能力优先比较同一 D0 的关闭/开启结果与最终选择；独立两次写稿只作副作用观察。宿主协议和胶水未变化时，可迁移旧在线证据，但必须明确哪些宿主未在当前候选重跑。
6. 未运行的命令不得写成通过；环境失败、无效样本、真实回退和 verifier 分歧如实保留。

## 修改与 Git

1. 修改前确认仓库、分支、HEAD、工作树、固定基线和用户授权；保留来源不明的现有改动。
2. 所有代码和文档修改都提交到 Git。commit message 说明目的、范围和实际验证。
3. 研究、基线、发布和可能污染主线的工作使用独立 worktree。每累计5次 commit 或范围明显扩大时，暂停做轻量 review、基线对比和直接相关回归。
4. 未经当次明确授权，不合并 `main`、不推送、不移动 tag、不创建 Release、不上传或删除任何平台版本。
5. 禁止破坏性重置、force push 和无边界批量清理。只删除路径已核准、工作树干净且成果可恢复的对象。

## 公开版与付费候选

- `main` 是公开版主线，不包含提纲审核 Hook、胶水、测试或详细实现规格。
- `codex/paid-outline-review` 是“当前 `main` + 付费提纲增量”。公开版的 Skill 语义、共享 Hook 和修复默认同步到该分支；提纲增量不得反向进入 `main`。
- 付费分支更新、冲突处理、差异 allowlist 和最小验证按 [public-paid-sync.md](maintenance/specs/public-paid-sync.md) 执行。任何付费包发布仍需单独授权。

## 仓库边界

- `chinese-official-writing/` 是 canonical 产品；`hooks/core/` 是唯一门禁核心，`hooks/adapters/` 是宿主静态适配。
- `packages/` 是公开兼容包；`maintenance/` 是工具、测试、规格和证据；`output/` 默认不提交。
- 普通 Skill 安装、Hook companion 组装、插件安装、启用、信任和真实执行是不同事实，不能互相冒充。
- 当前仓库和仓内包使用根 `LICENSE`（MIT）；第三方材料沿用自身许可。

## 最小交付门

- 文档或规格：直接链接/结构检查 + `git diff --check`。
- 产品或脚本：真实结果通过后，再跑直接相关 unit/smoke、quick validate、必要镜像或编译检查。
- 合并或发布：固定上一发布 tag，核对 ancestry、精确 DIFF、版本、清洁包、禁入文件和 fingerprint，再运行一次所需全量门。
- 交付时报告修改摘要、branch、commit、实际命令与结果、量化变化和剩余风险。

## 安全

不提交密钥、令牌、Cookie、登录态、私有地址或未脱敏数据。外部写入、发布和删除只在明确授权范围内执行。
