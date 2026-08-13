# 篇幅不足 Hook 三宿主真实在线生命周期结果

日期：2026-08-14
结论：**HOLD，不合并、不发布。**

## 固定对象

- 已合并本地 `main`：`b0b5012e3fda118119ba91dbb1c924bc4af35965`。
- 篇幅不足候选：`b81222fa043866fad13c3c9de72d5fe4aae40b52`。
- 当前 `under_length/runtime.py` SHA-256：`e16bc5af70afedbe323ac8c3a8b987e8cfa9cf4c3ecbeec0d68410b0e20036e4`。
- Codex、CodeBuddy、Claude Code 三份 companion 内该文件的 SHA-256 均与候选一致。
- 本轮只测试 under-only：用户明确给出字数下限或区间、D0 低于下限 10% 以上时触发；不包含超长压缩。

## 最新候选的真实执行

| 宿主 | 精确模型与档位 | 技术结果 | 篇幅事务 | 选择与交付 | 结论 |
| --- | --- | --- | --- | --- | --- |
| Codex CLI 0.144.6 | `alibaba-token-plan-2/deepseek-v4-flash-0731`，max | exit 0；当前 companion；真实 Hook | D0 819 字，D1 1036 字，终态 `under_length_complete` | D1 因 `under_length_number_added_dropped_or_changed` 被拒；选择 D0；选择 hash、交付 hash 与终稿 hash 均为 `dfba02ca...4e1020` | 生命周期与失败回退有效；但 D0 含过程旁白和 Markdown 分隔，不是可直接交付正文，因此质量不通过 |
| Claude Code 2.1.195 | `ollama-cloud/deepseek-v4-flash:0731`，max | exit 0；当前 companion；8 次 hook_started/response | D0 170 字，D1 327 字，终态 `under_length_complete` | 语义验收拒绝 D1；选择 D0；选择与交付 hash 均为 `81deedd5...c588` | 生命周期、语义拒绝和逐字回退有效；未形成可采纳 D1 |
| CodeBuddy Code 2.136.0 | `opencode-go/deepseek-v4-flash`，max | 当前重跑在模型调用前返回 `Authentication required`；0 input/output token | 当前重跑无事务 | 当前重跑无选择、无交付 | `ENV_AUTH_INVALID`；保留环境事实，不冒充当前在线重跑成功 |

关键原始记录 SHA-256：

- Codex 当前事务：`fbdbef75e9ad1694b048baa6a8bbfc50186326f03ca4948e1c2f61e2647e3ee9`；stdout：`f0e4732590f8dba88c72c3dd66272291747244a88dd35be980ae04177906bfc6`。
- Claude 当前事务：`151b6531743c385b5f0e41ff2dea81db2d7a4a9a42ee9bfc882c15d392dd668c`；stdout：`c203412af8a01ee1abf7863e5a27d55f7376d3dadb2efea64a79ed79637d6027`。
- CodeBuddy 当前无效 stdout：`e19286bf84cfd2bf7745ab7798364a0b405d463811d1fa1f24afa12e24c873d3`。

## 旧在线样本与当前修复复放

旧实现曾分别在三个宿主走完真实触发、修订、选择和精确回显：

- Claude：147→889 字，旧实现错误选择含材料外流程的 D1。
- CodeBuddy：180→816 字，因数量锚变化选择 D0，逐字回显闭环。
- Codex：314→532 字，因仍低于下限选择 D0，逐字回显闭环。

将三组原始 D0/D1 原样交给当前 `b81222fa` 复放后：

- Claude 旧不安全 D1 现被 `under_length_unsupported_added_process` 拒绝；
- CodeBuddy 旧 D1 也被新增流程检查拒绝；
- Codex 旧 D1 继续因低于下限被拒绝。

进一步核对确认，旧 CodeBuddy 成功包与当前包的 `hooks/hooks.json`、`scripts/host_gate_adapter.py`、中央 `gate_stop_hook.py` SHA-256 逐字相同；变化仅在宿主无关的 `under_length/runtime.py`。结合 CodeBuddy 官方 Stop/插件根契约、旧在线完整事务、当前 D0/D1 复放，以及同一当前 runtime 在 Codex、Claude Code 的在线执行，可将 CodeBuddy 宿主生命周期证据迁移到当前候选。这里明确标为“迁移证据”，不称当前在线重跑成功。

这证明当前修复命中了已暴露的坏候选，也证明三宿主胶水可运行；但仍不能证明篇幅能力能够稳定产生可采纳的 D1。

## 无效或旁证运行

- Claude 1000—1100 字触发样本已正确进入 `under_length_awaiting_revision`，但模型在 12 分钟内未返回修订，精确终止，记环境/模型未完成。
- Claude 与 CodeBuddy 各有一个当前指纹的带宽内样本，没有误触发篇幅事务，可作无误触发旁证。
- 一次 Codex 调用遗漏 `features.hooks=true`，只算无 Hook 对照，不计生命周期。
- 一次 Codex detached 包装破坏中文编码，整次作废，不从中保留局部结果。

## 准入判断

当前只证明：

1. Codex 与 Claude Code 可以在真实在线宿主中触发 under 事务、请求一次 D1、拒绝不合格 D1，并逐字交付 D0；
2. 当前机械检查能拦住真实运行中暴露的新增流程、数字变化和仍未达下限；
3. 普通带宽内稿件不会因该能力误触发。

当前仍未证明：

1. 任一当前候选 D1 能通过机械与语义检查并成为可直接使用的终稿；
2. SOL max 对当前可采纳 D1 的同源增量终审。

因此不运行没有合格 D1 的 SOL 盲审，也不把“安全回退”写成“篇幅问题已解决”。下一步先用最简强制路由修好篇幅语义，获得至少一份当前指纹的 D1 选择后，再交独立 SOL max 审核该同源 D0/D1。只有 CodeBuddy 宿主协议文件或中央 coordinator 后续发生变化时，才补当前登录态下的在线复测。独立 on/off 写稿胜负不作为本能力准入门。
