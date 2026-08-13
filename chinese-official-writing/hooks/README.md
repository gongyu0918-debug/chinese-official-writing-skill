# 可选交付复核 Hook

交付复核 Hook 是中文公文写作 Skill 的可选增强。普通 Skill 可以独立完成起草、改写、压缩和复核；启用 Hook 后，Agent 会在完整初稿形成后增加一次有界交付检查，帮助发现其已覆盖的事实、状态和结构风险。检查未通过或运行异常时，优先交付原始完整稿，不反复改写。

## 适合什么时候用

- 对数字、主体、未决状态和办理表述较敏感的正式材料；
- 希望在交付前再做一次机器可复核检查的任务；
- 已接受用少量额外生成时间换取一道交付检查的用户。

Hook 会增加事件处理和最多一次局部修订核验，因此通常比普通 Skill 慢。重要材料仍建议由责任人员完成事实核对和正式审签。

## 默认状态与知情边界

- 下载、安装或调用普通 Skill 不会自动启用 Hook。
- 本目录只保存静态能力与兼容文件，不自动识别宿主、不生成安装包、不安装插件、不修改配置，也不主动联网。
- 用户明确要求为某个宿主启用 Hook 后，Agent 先展示宿主、目标目录和拟复制文件；用户确认后才组装胶水层。组装、安装、启用和宿主信任确认分开进行。
- 启用后，Hook 仅使用宿主传入的当前任务事件，并在宿主提供的本地插件数据目录保存请求、初稿、门禁状态和输出哈希；不收集已安装 Agent 清单，不上传稿件或运行记录。

## 开启或关闭

### 当前任务临时关闭

直接对 Agent 说：

> 本次关闭 Hook，按普通 Skill 完成。

也可说“本次不要用 Hook”或“跳过交付门禁”。该任务会记录 `bypass=user_requested`，不创建门禁事务，不调用门禁，也不阻断终稿。已启用的 companion 仍会收到宿主事件；这里关闭的是本 Skill 当前任务的交付门禁。说“不要关闭 Hook”“继续使用 Hook”不会误触发关闭；“不要用脚本”等泛化要求也不会关闭 Hook。

### 完全关闭

| 宿主 | 完全关闭方式 |
| --- | --- |
| Codex | 使用普通 Skill，不安装 Hook companion；已安装时用 `codex plugin remove <插件>@<marketplace>` 移除。 |
| WorkBuddy / CodeBuddy | 启动时不传 `--plugin-dir`；已安装插件可用 `codebuddy plugin disable <插件>` 禁用。 |
| Claude Code | 启动时不传 `--plugin-dir`；已安装插件可用 `claude plugin disable <插件>` 禁用。 |

完全关闭后仍按 `SKILL.md`、references 和可选的 `scripts/prose_lint.py` 运行，写稿闭环不依赖 Hook。

## 宿主适配说明

内部按“能力核心 + 静态适配层”组织。`core/` 只有一份门禁能力；`adapters/<host>/` 只保存对应宿主的 manifest、事件配置、薄适配器和说明。Agent 不应把 adapter 目录本身当成可安装插件，也不得跨目录建立运行时相对引用。

| 宿主 | 适配说明 | 启用前检查 |
| --- | --- | --- |
| Codex | [`adapters/codex/README.md`](adapters/codex/README.md) | 展示组装清单；校验 manifest；完成插件注册、信任确认和事件检查。无法确认运行条件时使用普通 Skill。 |
| WorkBuddy / CodeBuddy | [`adapters/codebuddy/README.md`](adapters/codebuddy/README.md) | 展示组装清单；运行 `codebuddy plugin validate`；用户确认后加载插件根。 |
| Claude Code | [`adapters/claude-code/README.md`](adapters/claude-code/README.md) | 展示组装清单；运行 `claude plugin validate --strict`；用户确认后用 `--plugin-dir` 加载或安装。 |

Qwen Code、Hermes、OpenClaw、OpenCode 等没有本仓库内置的生命周期 Hook adapter，仍可使用普通 Skill。Agent 如需新增宿主胶水层，应先核对该宿主官方事件、插件根变量、数据目录和信任机制，再按现有 adapter 的最小职责实现；没有官方依据或真实 smoke 时，不宣称已兼容。

## 可选能力

companion 默认使用既有交付复核。用户也可在组装前明确选择[保护性外扩精确删除](capabilities/protective_expansion/README.md)：它只删除经语义观察确认、在当前文种中没有独立作用的原文片段，不补写进行态、责任主体或篇幅。两种能力不会在同一任务中并行运行；没有完整材料可见性或判断不确定时保留原稿。

## 工作方式

```text
SKILL.md 与 references 形成完整 D0
  -> 可选 prose_lint 只读提示
  -> 已启用 Hook 保存 D0
  -> review_gate 做一次有界检查
  -> 候选通过机械与语义核验时选择 D1
  -> 其余情况回退 D0
```

`references/delivery-review-gate.md` 是 Hook 专用协议，不属于普通写稿的默认加载资料。Hook 与 `prose_lint.py` 各自运行，前者负责交付复核，后者提供只读语言与格式提示。

## Agent 组装清单

只有用户明确要求启用时才执行以下步骤：

1. 读取本页、`host-capabilities.json` 和目标宿主的 adapter README。
2. 向用户展示目标目录、将要复制的文件和所选能力；未特别选择时使用既有交付复核，选择 `protective_expansion` 时写入静态能力配置。
3. 在新目录中放入目标宿主唯一的 manifest 与 `hooks/hooks.json`。
4. 复制薄适配器到 `scripts/`；复制完整 canonical Skill 到 `skills/chinese-official-writing/`，并将 `core/gate_stop_hook.py` 放到该 Skill 的 `hooks/gate_stop_hook.py`。
5. 保留 `SKILL.md`、references、`scripts/review_gate.py`、MIT LICENSE 和本说明；禁止父目录回指、外部 symlink、其他宿主 manifest 和自动安装代码。
6. 先运行宿主 validator 和离线事件 smoke，再由用户决定是否安装或加载。组装完成不得自动进入安装步骤。

可用性和数据边界见 [`host-capabilities.json`](host-capabilities.json)。
