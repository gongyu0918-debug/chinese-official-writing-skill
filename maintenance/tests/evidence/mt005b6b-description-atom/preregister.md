# MT-005b6b Description 单原子预登记

日期：2026-08-24。

## 固定变化

- 基线：`main@e3ed9bb374fd13234ea0eff9ea61c9e0f3cc7e69` 的204字 description。
- 候选：只把枚举中的 `实施细则` 缩为 `细则`，其余 description 和整个 Skill 树逐字不动；预期204→202字。
- 不同时删除、合并或改写 `制度、规定、办法、管理办法、操作规程`、受众描述和正文规则。

## 真实 A/B

- 宿主：Codex CLI 0.144.6；模型 `opencode-go/deepseek-v4-flash`、low、无 fallback。
- 基线/候选各在独立临时 Skill 根运行；禁用用户目录两份同名 Skill；`--ignore-user-config --ignore-rules --sandbox read-only --ephemeral`。
- 只使用 Codex CLI，不使用电脑控制、图形端或第三方写稿服务；运行本身允许真实 token 消耗。
- 每题同一 prompt、同一模型、同一权限；运行顺序为正向 baseline→candidate、边界 candidate→baseline，降低固定顺序偏差。

## 两个固定样本

1. `implementation_rules`：根据给定主体、范围、频次、检查项、记录和生效日期，起草《市政务服务中心自助终端巡检实施细则（试行）》。两臂都必须自主读取隔离根中的准确 Skill，保留全部事实和状态，不新增职责、报告渠道、整改期限、依据或适用对象。
2. `home_rules_boundary`：为本人和室友写周末厨房收纳细则。两臂都不得读取公文 Skill；候选若因新增泛词 `细则` 而触发，直接判误触发。文本仍须保留给定轮值、时间和私人边界。

## 决策

- 通过：两臂正向均准确触发，候选无独有事实/状态/文种/交付回退；两臂边界均不触发。随后才同步 canonical 普通镜像并补工程门。
- 拒绝：候选漏触发、误触发或出现独有硬回退，恢复204字基线并登记 `REJECTED_NO_MERGE`，不以2字收益覆盖。
- 技术失败：只修环境/参数；不得把无终稿、错误 Skill 或 provider fallback 计入质量样本。
