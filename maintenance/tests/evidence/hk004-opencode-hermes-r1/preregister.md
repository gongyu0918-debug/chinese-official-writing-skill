# HK-004 OpenCode / Hermes Agent adapter R1 预登记

## 固定边界

- 基线：`main@98b018483db938769a20fd5125ba83770566a49b`（已发布 v1.6.17）。
- 候选只研究 OpenCode 与 Hermes Agent 的宿主胶水，不修改写作规则、description、references 或共享门禁语义。
- 普通 Skill 路径保持独立；adapter、安装、启用和宿主信任仍是四个不同事实。
- 写稿使用便宜模型。首选 OpenCode `opencodex/ollama-cloud/deepseek-v4-flash:0731`、Hermes `ollama-cloud/deepseek-v4-flash:0731`；技术失败时每宿主最多改用 MiniMax M3 一次。Kimi、Grok、Qwen Max 不用于普通写稿。
- 不使用 GUI 或电脑控制，不发布、不合并、不推送，不触碰付费分支。

## 官方能力前提

### OpenCode

- 官方插件支持 `event`、`message.updated`、`session.idle`、工具前后事件及 SDK session API。
- 当前公开插件契约没有同步 `Stop`/`AfterAgent` 或最终文本替换事件。因此只验证受限路径：首次 `session.idle` 读取当前 D0，必要时向同一 session 发一次有界续写，第二次 `session.idle` 收口。
- 若 headless `run` 在第一次 idle 后退出，先试 `promptAsync`，仅允许再试一次同步 `prompt`；两者均不能稳定交付最终续写时，终态记 `LIFECYCLE_LIMITED`，不造完整 adapter。

#### R1b 常驻 CLI 区分实验

- R1 的 headless `run` 已分别用 `promptAsync` 与同步 `prompt` 复现“续写消息进入同一 session、模型未被唤醒、进程仅交付 D0”。为区分无头进程提前退出与 idle 唤醒本身失效，追加一次常驻 `--mini` CLI 原子。
- 插件在首次 idle 后延迟 1200ms 调用一次同步 `session.prompt`；只看同一 session 是否出现 `OC_D1` 和第二次有效 idle，不追加写稿、不改门禁。
- 成功也只能支持“常驻交互 CLI 的可见二次生成”，不能外推为 headless、同步拦截或最终文本替换；失败则 OpenCode 直接收口 `LIFECYCLE_LIMITED`，不再换事件或堆轮询。

### Hermes Agent

- 官方插件 `transform_llm_output` 在交付前同步接收最终文本，可用经典程序变换替换输出；`post_llm_call` 仅观察。
- 能继续模型循环的 `pre_verify` 官方限定为本轮已有代码文件变更，不能用于普通写稿。
- 本轮只验证无需额外推理的交付洁净度原子。不得把 transform-only adapter 宣称为共享多 Stop 门禁，也不得用 `inject_message` 的中断副作用模拟官方未提供的写稿 Stop。

## 阶段一：真实宿主生命周期标记

1. OpenCode：模型首稿只输出 `OC_D0`。插件在第一次 idle 记录脱敏消息形状并发出“只输出 `OC_D1`”的同 session 续写；成功条件为同一 session 观察到第二次 idle，最终可见文本为 `OC_D1`，且没有无限续写。
2. Hermes：模型首稿只输出 `HA_D0`。项目插件的 `transform_llm_output` 同步替换为 `HA_D1`；成功条件为 one-shot stdout 仅见 `HA_D1`，并观察到 transform 与 post-LLM 生命周期。
3. 生命周期标记只证明事件位置，不计写稿质量。

## 阶段二：真实写稿

固定三题，均要求“只输出可直接使用的完整正文，不解释过程”，不设字数下限：

1. 稀疏采购申请：现有推理服务器利用率连续两周超过90%，每日18个任务排队，拟采购2台服务器，预算与供应商尚未确定；须保留未决状态，可作一层缓解排队、提高处理效率的预期判断。
2. 活动新闻：2026年8月18日举办阅读交流活动，48人参加，其中45人完成现场环节，3人于8月20日补测；一名参与者表示“交流让我找到新的阅读方法”，后续意见待核；不得扩大为48人全体成效。
3. 情况说明：系统联调已完成，验收材料未附；培训尚未开展但可安排；采购事项仍在比选，未形成决定；须区分完成、材料未附、未开展和可安排。

### OpenCode 成功条件

- 使用当前 canonical Skill，D0 与 adapter 候选使用同一宿主、同一模型和同一题面。
- 受限续写能完成当前所选单能力的全部必要阶段并到达终态；最终正文没有候选独有的事实、状态、主体、文种或直接可用性硬回退。
- 若宿主只显示 D0 后又显示 D1，必须在 README 明示可见双稿体验；不能写成同步拦截。

### Hermes 成功条件

- 当前 checkout 的 canonical Skill 由隔离项目插件以只读、带命名空间的 skill 注册，并用 `--skills` 显式预载；不得用 profile 内可能过时的同名副本冒充当前基线。
- 先看无插件 D0 是否真实出现未请求包装。只有至少一稿出现包装才制作确定性删除原型。
- 候选只允许删除位于正文外、可机械识别的过程说明、字数、自评、横线、代码围栏或纯提示标签；正文字符顺序必须保持为 D0 的子序列，事实、状态、日期、数字和标题正文不得变化。
- 至少两题包装下降且三题无硬回退才进入 adapter；否则终态记 `BASELINE_NOT_REPRODUCED` 或 `TRANSFORM_REJECTED`。

## 终态与工程门

- 不保留 `HOLD`。每个宿主只能收口为 `ADAPTER_CANDIDATE_PASS`、`LIFECYCLE_LIMITED`、`BASELINE_NOT_REPRODUCED`、`TRANSFORM_REJECTED` 或 `TECHNICAL_INVALID`。
- 只有真实生命周期与真实稿先通过，才补 assembler、manifest、静态契约、聚焦测试、host-capabilities 和说明。
- 若形成产品候选，运行直接相关 adapter/unit/smoke、companion 组装、`quick_validate.py`、`git diff --check`，并提交到当前独立分支；不自动合入 main。
