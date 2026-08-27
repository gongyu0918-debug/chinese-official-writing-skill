# HK-004 OpenCode / Hermes Agent adapter R1 结果

## 结论

- 固定基线为已发布 `main@98b018483db938769a20fd5125ba83770566a49b`（v1.6.17），开发分支为 `codex/opencode-hook-r1`。本轮没有修改 description、写作规则、references 或共享门禁语义。
- OpenCode 终态为 `ADAPTER_CANDIDATE_PASS_INTERACTIVE_ONLY`：项目级插件把官方 `session.idle`、`session.messages`、`session.prompt` 映射到现有共享 core；常驻交互 CLI 已完成当前 Skill、同一 session、真实稿、语义判断、逐字回显、终态脱敏。`opencode run` 无头路径实测旁路，不能宣称受 Hook 保护。
- Hermes Agent 终态为 `BASELINE_NOT_REPRODUCED`：`transform_llm_output` 同步变换标记真实通过，但三份当前 Skill 真稿没有出现可机械删除的正文外包装；实际缺口是材料外程序、未来动作和效果升级，需要语义判断。同步 transform 不能安全替代共享多阶段门禁，因此没有制作产品 adapter，也没有留下 HOLD。
- OpenCode 候选只在当前独立分支；未合入 `main`、未推送、未发布。Hermes 没有候选文件可合入。

## 官方依据与宿主边界

### OpenCode

- 官方插件文档：<https://opencode.ai/docs/plugins/>；官方 Skill 文档：<https://opencode.ai/docs/skills/>；官方仓库：<https://github.com/anomalyco/opencode>。
- OpenCode 1.18.23 提供项目级 `.opencode/plugins`、`session.idle` 通知和 SDK session API，但没有同步 `Stop` 或最终文本替换事件。官方 issue 还记录无头退出与 idle/异步插件时序限制：<https://github.com/anomalyco/opencode/issues/16879>、<https://github.com/anomalyco/opencode/issues/23380>、<https://github.com/anomalyco/opencode/issues/32010>、<https://github.com/anomalyco/opencode/issues/21524>。
- 官方源码确认项目 `.opencode/skills` 与外部 `.agents/.claude` Skill 会共同扫描，同名 Skill 只警告并覆盖。首轮三题因此统一作废为 `INVALID_DUPLICATE_SKILL_COLLISION`；唯一重跑设置 `OPENCODE_DISABLE_EXTERNAL_SKILLS=1`，且每个 session 都从 tool metadata 证明加载当前项目副本。产品 adapter 不替用户静默设置该环境变量，只在加载路径精确等于 companion 内 Skill 时启动。

### Hermes Agent

- 官方插件文档：<https://github.com/NousResearch/hermes-agent/blob/main/website/docs/user-guide/features/plugins.md>；官方 Hook 文档：<https://hermes-agent.nousresearch.com/docs/user-guide/features/hooks/>。
- `transform_llm_output` 是同步确定性文本变换；`post_llm_call` 是观察点。`pre_verify` 只在本轮修改代码文件时进入验证，不能覆盖普通写稿；`inject_message` 的 interrupt/queue 语义也不是写作 `Stop`。
- Hermes 0.20.0 的项目插件需 `HERMES_ENABLE_PROJECT_PLUGINS=1` 和 profile 中显式启用；CLI 的插件启用命令没有发现项目插件，因此隔离 profile 只为本轮手工登记，不外推为普通安装体验。

## 生命周期标记

| 宿主 | 结果 | 解释 |
| --- | --- | --- |
| OpenCode headless `run` + async/sync prompt | D0 后进程退出；同 session 留下续写 user message但未唤醒模型 | 不能据此做完整 adapter |
| OpenCode 常驻 `--mini` + 延迟同步 prompt | 同一 session `OC_D0 → OC_D1`，第二次 idle 到达，单次续写 | 只支持交互模式的可见二次生成 |
| Hermes `transform_llm_output` | 原模型文本 `HA_D0`，stdout 为 `HA_D1`，post hook 观察到变换后文本 | 证明 transform 位置，不证明写稿收益 |

## 真实写稿先行

### OpenCode 同稿原型

模型为 `opencodex/ollama-cloud/deepseek-v4-flash:0731`。以下仅计 `OPENCODE_DISABLE_EXTERNAL_SKILLS=1` 后、tool metadata 指向当前项目 Skill 的三份有效 session；首轮重名污染不计。

| 题目 | D0 → 同稿复核结果 | 判断 |
| --- | --- | --- |
| 稀疏采购申请 | 159字符 `afd950ae...` → 150字符 `3fc9c8a8...`；删除材料外“待确定后另行报批”，保留利用率、18个排队、2台、预算/供应商未定和一层预期作用 | 目标解决 |
| 活动新闻 | 120字符 `e7fdc046...` → 122字符 `ea8f61e6...`；恢复补测完整年份并收紧为“后续意见待核”，但仍有 Markdown 加粗和材料外“围绕阅读方法展开交流” | 部分改善，仍非直接可用；不是候选独有回退 |
| 情况说明 | 134字符 `e3f0ff3e...` → 74字符 `d9aba00b...`；删除“材料正在整理/另行报送/采购结果后另行报告”，保留完成、未附、未开展、可安排与未决 | 目标解决 |

三题中2题解决主要目标，3题都作出目标修正，没有候选新增的事实、状态、主体、文种或篇幅硬回退，达到预登记的工程化阈值；新闻残余风险不被包装成成功。

### Hermes 当前 Skill 基线

模型为 `ollama-cloud/deepseek-v4-flash:0731`，显式预载隔离项目注册的当前 checkout Skill。

| 题目 | 观察 |
| --- | --- |
| 采购申请 | 没有正文外包装；新增业务增长、采购程序、型号配置、另行报批及较强效果 |
| 活动新闻 | 没有包装，事实范围基本安全 |
| 情况说明 | 没有包装；新增验收材料另行补送、培训实施条件/安排和采购结果后报告 |

机械包装目标为0/3；两份风险稿的修复需要语义判断，不能由只删固定 wrapper 的 transform 安全完成。因此按预登记直接收口 `BASELINE_NOT_REPRODUCED`，不为“有 adapter”而制造无写稿收益的胶水。

## 最终 OpenCode companion 在线执行

### 情况说明：共享门禁语义 KEEP

- OpenCode 1.18.23；模型 `opencodex/alibaba-token-plan-2/deepseek-v4-flash-0731`；session `ses_fbe8b9247ffe2iyBzOW84F2jVr`。
- tool metadata 的 Skill 目录精确为组装包 `.opencode/skills/chinese-official-writing`。
- D0 为86字符，SHA-256 `0083df065211a7875deed2ced9aec39304d852efd61474a39d2eb29fd23c9f4e`。共享门禁把“采购事项仍在比选，尚未形成决定”送入语义判断；模型基于题面明确的未决状态选择 `KEEP`，没有因门禁过严删掉有效状态。
- 两次内部续写分别完成结构化判断和逐字 emit；最终正文与 D0 同 SHA-256。终态回执为 `hook_phase=complete`、`delivery_verified=true`、`stop_attempts=2`、`data_retention_state=raw_turn_data_redacted`，原请求/正文关键词扫描为0命中。
- 该首个在线样本没有宿主级 reasoning effort 回执，只作为生命周期证据，不标成 `max` 写稿样本。

### 活动新闻：显式 max 配置

- OpenCode 官方 Agent 透传参数显式设置 `reasoningEffort=max`；模型仍为 Alibaba Token Plan 2；session `ses_fbe80a5eaffer4ShXSN1LkpvIX`。OpenCode export 记录了模型和 reasoning token，但不回显 effort 名称，因此证据表述只写“配置为 max”，不伪造宿主回执。
- D0/最终均为130字符，SHA-256 `0524f23461752fb24caeaf5d08ac840665d1e7ac2ae62b44818338539ffb4d49`。稿件保留两个完整日期、48/45/3三层范围、单人引语和“后续意见待核”；“提供阅读交流的机会”是一层低强度即时作用，没有写成48人全体既成成效，也没有补造活动过程。
- 当前稿没有语义 finding，门禁只做一次逐字 emit；终态 `stop_attempts=1`，原始文本脱敏扫描为0命中。

### 无头旁路

- `opencode run` 使用同一组装包和 Alibaba Token Plan 2，session `ses_fbe896b02ffe0bhit5mdApLpoM`；Skill 路径正确，输出一份184字符采购申请。
- adapter 明确不启动，`COW_OPENCODE_GATE_DATA` 不存在；该稿标题含 Markdown `#`，如实说明无头普通 Skill 路径没有 Hook 兜底。

## P1 冷审修复与在线复核

第一次最终冷审发现两项 P1：延迟 `session.prompt` 没有在发送前重新绑定原始外部回合；未终态模块重载只靠内存状态，可能重复消费同一 D0。候选没有按原结论直接交付，而是增加不含正文的 adapter 相位文件和共享 core `HostAbort` 精确脱敏事件：

- 延迟发送前重新读取同一 session，外部用户消息 ID、末次助理消息 ID/hash 或续写计数任一变化即取消旧续写；对抗 smoke 在延迟窗口插入新用户消息，结果为0次 prompt、旧事务原文0命中。
- 模块在首个 block 后、prompt 前重载时，不猜测恢复已消费的门禁相位；重载实例精确中止旧事务并保留可见 D0，原实例的延迟任务读取不到待派发相位，不会重复 prompt。结果为0次 prompt、旧事务原文0命中。
- 同名外部 Skill 获胜时，既不启动项目门禁，也不留下 `UserPromptSubmit` 暂存原文；结果为0次 prompt、警告可见、原文0命中。
- core 单测确认 `HostAbort` 只清理当前 session/turn，回执保留受限原因码与 `failed_open_host_abort`，不保留请求或草稿。

修复后又用 OpenCode 1.18.23、`opencodex/alibaba-token-plan-2/deepseek-v4-flash-0731` 和配置 `reasoningEffort=max` 跑一份无字数限制采购申请，session 为 `ses_fbe6805e3ffebMTw91aWxQUZ8x`。tool metadata 精确命中最新52文件 companion 内 Skill；D0 与最终回显均为320字符、SHA-256 `7374e9aba1b424731305a3d1c86b0afff640a6c0cc18e2c2247713862728863c`。稿件保留92%、18个排队、拟采购2台、预算/供应商尚未确定和后续按比选完善方案，原因与时效影响为题面事实直接支持的一层推断；“明确设备配置、预算金额及采购等具体事项”语言略生硬，记写作 WARN，不冒充满分稿，也不是 adapter 新增回退。

该在线周期只需一次 emit 续写，终态回执为 `hook_phase=complete`、`delivery_verified=true`、`stop_attempts=1`、`data_retention_state=raw_turn_data_redacted`；门禁数据根只有1份脱敏回执，原请求/正文扫描0命中，`opencode-adapter-state` 文件数为0。OpenCode export 记录了精确模型与 reasoning token，但仍未回显 effort 名称，所以只表述为“配置 max”。

## 工程结果

- 新增项目级 adapter：`hooks/adapters/opencode/opencode_gate_plugin.js` 与说明页；不生成 manifest，不修改 `opencode.json`，不自动安装、启用或设置隔离开关。
- 组装器新增 `opencode` 布局：`.opencode/plugins/chinese-official-writing-gate.js`、`.opencode/skills/chinese-official-writing/`、`.opencode/hook-capability.json`。P1 修复后最终组装仍为52文件，fingerprint `0cd827bc11a32565877cab89e745d10d6f71b3daf50ce741457637435fbbe88c`。
- adapter 只映射当前 external user 后的 assistant 文本；只有实际加载 companion 内 Skill 才启动。共享 core 缺失、非法响应、续写失败或达到宿主上限时失败开放，不把错误消息标成终稿。
- adapter 在进程重启后先读取当前 turn 的终态脱敏回执；若是已消费但未终态的 adapter 周期，则不重放，精确中止并脱敏后保留 D0。模块重载、延迟期间新任务和同名外部 Skill 三条 smoke 已覆盖这些路径。
- 本轮新增离线 Node/Python 生命周期 smoke，并把 OpenCode 纳入六类 capability 的静态组装、SkillHub 源包与边界回归；发布平台无操作。

## 实际命令

```text
opencodex --version
opencodex models live
opencode --version
opencode models opencodex --verbose
hermes --version
py -3 maintenance/tools/assemble_hook_companion.py --host opencode --output <isolated-output> --capability delivery_review
node --check chinese-official-writing/hooks/adapters/opencode/opencode_gate_plugin.js
py -3 -m unittest maintenance.tests.test_opencode_gate_adapter -v
opencode --mini --no-replay --model opencodex/alibaba-token-plan-2/deepseek-v4-flash-0731 --prompt <fixed-real-writing-prompt>
opencode run --model opencodex/alibaba-token-plan-2/deepseek-v4-flash-0731 <fixed-procurement-prompt>
opencode export <session-id>
py -3 -m unittest maintenance.tests.test_opencode_gate_adapter maintenance.tests.test_gate_stop_hook maintenance.tests.test_hook_layer_contract maintenance.tests.test_delivery_cleanliness_capability maintenance.tests.test_repetition_cleanup_capability maintenance.tests.test_skill_boundary maintenance.tests.test_skillhub_package_builder maintenance.tests.test_repository_reachability maintenance.tests.test_claude_gate_adapter maintenance.tests.test_complexity_contract -v
py -3 -B C:\Users\admin\.codex\skills\.system\skill-creator\scripts\quick_validate.py chinese-official-writing
```

OpenCode 在线命令同时使用独立绝对 `OPENCODE_DB`、`COW_OPENCODE_GATE_DATA` 与 `OPENCODE_DISABLE_EXTERNAL_SKILLS=1`；活动新闻样本在 `OPENCODE_CONFIG_CONTENT` 的 `agent.build.reasoningEffort` 中显式传入 `max`。原始数据库、session export、TUI 日志和 Hermes stdout 保存在忽略的 `output/hk004-opencode-hermes-r1/`，不进入产品包。

P1 修复后的扩展回归实际为167/167通过，Skill Creator quick validate 返回 `Skill is valid!`。首次误用仓库内已不存在的 `maintenance/tools/quick_validate.py`，命令未启动；改用上列真实入口后复跑通过，失败命令不计为产品失败，也不隐去。

## 剩余风险

- OpenCode 不是同步 Stop：用户会看到 D0、中间结构化判断和最终回显；已覆盖的新任务竞态和未终态模块重载会安全回退并脱敏，但任意位置硬杀进程、Python/core 同时不可用仍可能留下未完成事务，必须按说明精确清理。
- OpenCode `run` 仍不受门禁保护；常驻交互证据不能外推到 web、ACP、其他版本或其他平台。
- 项目与用户级同名 Skill 的发现顺序不稳定；adapter 会拒绝错误来源，但用户仍需清理旧副本或在隔离验证中显式关闭外部 Skill。
- 本轮只在线跑默认 `delivery_review`。其他 capability 共享同一 core 且静态组装/离线生命周期通过，但没有在 OpenCode 逐项重跑真实在线 D1；不能把静态可组装写成各能力在线全覆盖。
- Hermes 目前只有 transform 标记证据，没有产品 adapter；若以后出现跨模型可复现、可机械删除且正文子序列不变的真实 wrapper 反例，再按新原子重开，不沿本轮语义失败硬扩 transform。
