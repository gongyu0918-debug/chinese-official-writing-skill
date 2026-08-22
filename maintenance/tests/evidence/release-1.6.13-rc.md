# v1.6.13 本地候选基线

日期：2026-08-22

状态：`PREPARING`。本文件先登记发行边界；完成最终验证和三平台 dry-run 后再冻结为本地候选。

## 固定对象与范围

- 上一正式产品 tag：`v1.6.12^{commit}=ae4a25b497fab1ccdd621ffbf21e43501701f8b9`。
- 上一远端发布回执：`origin/main@48e061f50111ebf61f1c94edec8a36dff3e1c434`。
- 本轮候选内容基线：`main@b572102f083f41c0180f0f14f62570340cae1d38`。
- 本地候选分支：`codex/release-v1.6.13`。
- 目标版本：`1.6.13`。
- 公开候选只包含已合入 main 的 `WR-013`、`WR-011`、`UL-005` 与联网来源用途/命中页绑定，以及对应测试、镜像、规格和证据。
- `codex/paid-outline-review` 不反向合入；公开树不含 `outline_assist`、付费提纲 coordinator、胶水、测试或详细实现规格。

## 真实写稿依据

- `WR-013`：五条 Codex Desktop 路线验证材料和常识支持的一层原因、即时作用、发布者角色，以及非新闻控制。
- `WR-011`：三轮25份真实稿后，五条最终路线守住来源身份、原始出处、冲突和限定结论边界。
- `UL-005`：WorkBuddy / CodeBuddy 同一 D0 生命周期拒绝含强保障、材料外用途和多余请批语的风险 D1，并接受只含同一事实 span 低强度推断的受控 D1。
- 联网来源用途：R2f—R2h 共15份真实稿，最终五条路线均绑定实际打开的上海命中页 URL；严格工具调用次数不由提示词作确定性保证。

## 待完成发布门

- 固定 v1.6.12 做 ancestry 与精确 DIFF 核对。
- 版本面定向测试、全量 unittest、quick validation、镜像二次同步和 `git diff --check`。
- SkillHub.cn 清洁包与 ClawHub 33文件无 Hook 包的文件数、禁入项、规范化指纹和 dry-run。
- GitHub、SkillHub.cn、ClawHub 正式回执与公开传播复核。
