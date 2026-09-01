# 可选交付复核 Hook

交付复核 Hook 是中文公文写作 Skill 的可选增强。普通 Skill 可以独立完成起草、改写、压缩和复核；启用 Hook 后，Agent 会在完整初稿形成后增加一次有界交付检查，帮助发现其已覆盖的事实、状态和结构风险。检查未通过或运行异常时，优先交付原始完整稿，不反复改写。

## 适合什么时候用

- 对数字、主体、未决状态和办理表述较敏感的正式材料；
- 希望在交付前再做一次机器可复核检查的任务；
- 已接受用少量额外生成时间换取一道交付检查的用户。

Hook 会增加事件处理和有限的修订核验，因此通常比普通 Skill 慢。多数能力最多修订一次；超长收束在首次压缩仍超限时最多再压缩一次。重要材料仍建议由责任人员完成事实核对和正式审签。

## 默认状态与知情边界

- 下载、安装或调用普通 Skill 不会自动启用 Hook。
- 本目录只保存静态能力与兼容文件，不自动识别宿主、不生成安装包、不安装插件、不修改配置，也不主动联网。
- 用户明确要求为某个宿主启用 Hook 后，Agent 先展示宿主、目标目录和拟复制文件；用户确认后才组装胶水层。组装、安装、启用和宿主信任确认分开进行。
- 启用后，Hook 仅使用宿主传入的当前任务事件，并在宿主提供的本地插件数据目录保存请求、初稿、门禁状态和输出哈希；不收集已安装 Agent 清单，不上传稿件或运行记录。

## 本地数据留存

已启用 companion 时，Hook 为完成当前有界生命周期，会在宿主提供的插件数据目录下暂存本轮原请求、D0、候选稿和核验包。正常到达终态 Stop，或 Stop 判定本轮不启动门禁后，原请求、原稿、候选稿、删除 span、观察包和事务文件会立即删除或从记录中移除；本地只保留 hash、字数、阶段、选择结果和交付状态等不含正文的回执。重复 Stop 只读取已脱敏状态，不重建事务。

Hermes Agent 的单次同步复核不建立磁盘事务：请求、D0 和候选只保留在当前进程内存，回合结束即移除；宿主 INFO/显式 debug 摘要只含动作、原因、字符数和 hash，不含正文。

宿主或进程在终态前异常退出时，未完成事务可能仍留在宿主 adapter 数据根下的 `candidate-ai-gate-hook`。需要清理时，先按下文“暂停或关闭”中的宿主关闭方式停用或移除 companion，核对该宿主说明中的绝对数据根，只删除其下精确的 `candidate-ai-gate-hook` 子目录；不要删除数据父目录、用户目录或其他插件目录。当前 Hook 不联网外传这些快照，也不读取凭证文件。

## 宿主适配说明

内部按“能力核心 + 静态适配层”组织。`core/` 只有一份门禁能力；`adapters/<host>/` 只保存对应宿主的 manifest、事件配置、薄适配器和说明。Agent 不应把 adapter 目录本身当成可安装插件，也不得跨目录建立运行时相对引用。

| 宿主 | 适配说明 | 启用前检查 |
| --- | --- | --- |
| Codex | [`adapters/codex/README.md`](adapters/codex/README.md) | 展示组装清单；校验 manifest；完成插件注册、信任确认和事件检查。无法确认运行条件时使用普通 Skill。 |
| WorkBuddy / CodeBuddy | [`adapters/codebuddy/README.md`](adapters/codebuddy/README.md) | 展示组装清单；运行 `codebuddy plugin validate`；用户确认后加载插件根。 |
| Claude Code | [`adapters/claude-code/README.md`](adapters/claude-code/README.md) | 展示组装清单；运行 `claude plugin validate --strict`；用户确认后用 `--plugin-dir` 加载或安装。 |
| ZCode | [`adapters/zcode/README.md`](adapters/zcode/README.md) | 展示组装清单；确认 `.zcode-plugin`、三类 Hook 与 Skill 被发现；用户确认后才登记或启用插件根。 |
| Qwen Code | [`adapters/qwen-code/README.md`](adapters/qwen-code/README.md) | 展示组装清单并完成本地事件 smoke；用户确认后安装 native extension，用 `qwen extensions list` 核对版本、Skill 和启用状态。 |
| Kimi Code CLI | [`adapters/kimi-code/README.md`](adapters/kimi-code/README.md) | 展示组装清单；用户确认后通过 `/plugins install` 安装并用 `/plugins info` 核对；单 Stop 上限见适配说明。 |
| OpenCode | [`adapters/opencode/README.md`](adapters/opencode/README.md) | 只支持常驻交互 CLI；预览并合并项目级 `.opencode/` 覆盖，核对实际 Skill 来源后做同一 session 在线 smoke。`opencode run` 明确旁路。 |
| Hermes Agent | [`adapters/hermes-agent/README.md`](adapters/hermes-agent/README.md) | 已验证0.20.5与0.20.6，更高版本先重跑生命周期 smoke；组装为 profile 用户插件，用 `hermes plugins enable` 明确启用，再在新建、不可恢复的 `chat -q/--query/--query-file` 单题预加载 companion 命名空间 Skill 做同回合同步 smoke。交互、resume/continue、`--oneshot` 和 gateway 不支持。 |
| DeepSeek Harness | [`adapters/deepseek-harness/README.md`](adapters/deepseek-harness/README.md) | 组装为原生 Profile Bundle；安装后核对 bundle 配置层、实际 Skill 来源和当前 open turn 多 Stop 回执。当前只在线验证0.1.1-rc.2 headless。 |

Qwen Code 必须使用 native extension；便携 Agent Plugin v1 仍不会加载 Hook。Kimi Code CLI 已有 native plugin adapter，但 0.38.0 每回合只接受一次 Stop 阻断：可完成当前 D0 的首次检查和一次续写，不能对续写终稿再次运行 Stop，因此不得宣称与多 Stop 宿主等价闭环。OpenCode 1.18.23 只有常驻交互 CLI 完成了 `session.idle → session.prompt → session.idle` 的同一 session 闭环；中间稿与结构化响应对用户可见，`run` 无头命令不会启动门禁。延迟期间会重新绑定原回合；用户提交新任务、同名外部 Skill 获胜或未终态模块重载时，旧事务精确脱敏并安全回退当前 D0，不把旧续写串入新任务。Hermes Agent 0.20.5—0.20.6 只在新建、不可恢复的 `chat -q/--query/--query-file` 单题完成验证：`transform_llm_output` 内使用一次宿主管理的 LLM 调用同步选择 D0 或终稿，`post_llm_call` 再闭合 task、turn 与可见响应 hash；当前只支持 `delivery_review`，失败逐字回退 D0。宿主会在 transform 前保存 D0，因此交互、resume/continue、`--oneshot` 和 gateway 都明确旁路，不宣称与共享多 Stop 门禁等价。DeepSeek Harness 0.1.1-rc.2 的官方 Claude Code bridge 在 Stop 载荷中不带 D0；当前 companion 改用原生 `agent/turn-stopping` 读取同一 open turn 的内存成稿，并已在 headless 完成三次 Stop 的 D0→内部核验→逐字终稿闭环。其他 profile 和 capability 未在线复跑。OpenClaw 仍为普通 Skill。没有官方依据或真实 smoke 时，不宣称新增宿主兼容。

## 可选能力

companion 默认使用既有交付复核。用户也可在组装前明确选择[保护性外扩精确删除](capabilities/protective_expansion/README.md)、[篇幅不足补足](capabilities/under_length/README.md)、[超长收束](capabilities/over_length/README.md)、[交付洁净度](capabilities/delivery_cleanliness/README.md)或[重复句整理](capabilities/repetition_cleanup/README.md)。超长收束先查重复，再压缩衔接和句式；其余能力各自只处理说明页列明的单一风险。六种能力静态互斥，判断不确定时保留原稿。

## 工作方式

```text
SKILL.md 与 references 形成完整 D0
  -> 可选 prose_lint 只读提示
  -> 已启用 Hook 保存 D0
  -> 所选静态能力做一次有界检查
  -> 候选通过该能力的机械与语义核验时选择 D1
  -> 其余情况回退 D0
```

`references/delivery-review-gate.md` 是 Hook 专用协议，不属于普通写稿的默认加载资料。Hook 与 `prose_lint.py` 各自运行，前者负责交付复核，后者提供只读语言与格式提示。数据暂存与终态脱敏边界见上文“本地数据留存”。

## Agent 组装清单

只有用户明确要求启用时才执行以下步骤：

1. 读取本页、`host-capabilities.json` 和目标宿主的 adapter README。
2. 向用户展示目标目录、将要复制的文件和所选能力；未特别选择时使用既有交付复核，选择 `protective_expansion`、`under_length`、`over_length`、`delivery_cleanliness` 或 `repetition_cleanup` 时写入静态能力配置。
3. 在新目录中放入目标宿主唯一的 manifest；使用外部 Hook 配置的宿主同时放入唯一的 `hooks/hooks.json`，Kimi Code CLI 的 Hook 保持在 `kimi.plugin.json` 内联声明，Hermes 使用根 `plugin.yaml`，DeepSeek Harness 使用根 `package.json` 与 `cordis.patch.yml`。OpenCode 没有 companion manifest，使用其官方项目级 `.opencode/plugins/` 自动发现。
4. 普通 manifest 宿主把薄适配器放到 `scripts/`、Skill 放到 `skills/chinese-official-writing/`；Hermes 的 `__init__.py` 与 `plugin.yaml` 位于 companion 根；DeepSeek Harness 的 `index.mjs` 位于 bundle 根；OpenCode 则使用 `.opencode/plugins/chinese-official-writing-gate.js`、`.opencode/skills/chinese-official-writing/` 与 `.opencode/hook-capability.json`。各布局都只复制一份完整 canonical Skill，并将 `core/gate_stop_hook.py` 放到包内 Skill 的 `hooks/gate_stop_hook.py`；Hermes 另复制 `core/single_pass_final_review.py`，不从仓库父目录运行时回指。
5. 保留 `SKILL.md`、references、`scripts/review_gate.py`、MIT LICENSE 和本说明；禁止父目录回指、外部 symlink、其他宿主 manifest 和自动安装代码。
6. 先运行宿主 validator 和离线事件 smoke，再由用户决定是否安装或加载。组装完成不得自动进入安装步骤。

可用性和数据边界见 [`host-capabilities.json`](host-capabilities.json)。

## 暂停或关闭

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
| ZCode | 不在插件目录中登记或启用 companion；已登记时从 ZCode 插件配置中停用或移除。 |
| Qwen Code | 使用普通 Skill，不安装 native extension；已安装时用 `qwen extensions disable chinese-official-writing-gate` 停用，或用 `qwen extensions uninstall chinese-official-writing-gate` 移除。 |
| Kimi Code CLI | 使用普通 Skill，不安装 plugin；已安装时通过 `/plugins disable chinese-official-writing-gate` 停用，或通过 `/plugins remove chinese-official-writing-gate` 移除。 |
| OpenCode | 使用普通 Skill，不把 companion 的项目级 `.opencode/plugins/chinese-official-writing-gate.js` 合入目标项目；已合入时先停用 OpenCode，再只移除该文件及本 companion 的同名 Skill/能力配置，不覆盖项目内其他 `.opencode` 内容。 |
| Hermes Agent | 使用普通 Skill，不安装 profile 用户插件；已启用时运行 `hermes plugins disable chinese-official-writing-gate`。 |
| DeepSeek Harness | 使用普通 Skill，不向目标 profile 安装 bundle；已安装时运行 `dsh plugin --profile <profile> remove chinese-official-writing-gate-dsh`，然后重启该 profile。 |

完全关闭后仍按 `SKILL.md`、references 和可选的 `scripts/prose_lint.py` 运行，写稿闭环不依赖 Hook。

## 永久移除包内 Hook

只需要普通 Skill 时，可以通过本页语义说明永久移除本地 Skill 包内的 Hook 源文件。此操作只在用户明确要求并再次确认后进行；普通调用不自动清理文件。

用户明确要求永久移除时，Agent 先展示当前 Skill 根目录和以下唯一范围，等待用户再次确认：

1. 从当前 Skill 的 `SKILL.md` 删除唯一包含 `hooks/README.md` 的接引段；当前结构中它是最后一段；
2. 删除同一 Skill 根目录下的 `hooks/`，不解析、不跟随、不删除其他路径；
3. 保留 `SKILL.md` 其他正文、references、scripts、LICENSE 和包外文件。

确认后使用宿主提供的文件编辑能力完成这两个精确动作，并复核 `SKILL.md` 不再引用 `hooks/`。若接引段不是唯一命中、`hooks/` 不在当前 Skill 根目录内或它是符号链接，立即停止，不做部分删除。已安装或已加载的 companion 应先使用上表的宿主原生命令停用或移除；不要修改宿主插件缓存。没有再次确认时只说明步骤，不执行删除。
