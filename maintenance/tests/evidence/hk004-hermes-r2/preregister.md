# HK-004 Hermes Agent adapter R2 预登记

## 固定边界

- 公开基线：`main@c784e3721db8f170015e1220ea92c815f747a89a`（已发布 v1.6.18）。候选分支为 `codex/hermes-lifecycle-r2`，只在独立 worktree 工作。
- 宿主基线：Hermes Agent `0.20.5`，本机官方 checkout `ef46ec03e11452eab74e261147668fb64a3d9fd3`。本轮先用官方 CLI 真跑，不用 GUI、电脑控制或自建 harness 冒充宿主。
- 只研究 Hermes 写后生命周期和最小静态 adapter；不修改 description、写作 reference、共享门禁语义或普通 Skill 路径，不触碰付费分支。
- 写稿和写后复核都使用便宜模型。首选 `ollama-cloud/deepseek-v4-flash:0731`，技术失败时只改用已配置的 DeepSeek V4 Flash 或 MiniMax M3 一次；Kimi K3、Grok 4.6、Qwen Max 不用于写稿。
- 插件、普通 Skill、安装、启用和宿主信任是不同事实。候选不得修改用户现有 Hermes 配置；真实测试使用隔离配置和项目插件开关。
- 本轮不合并 `main`、不推送、不发布。所有有效改动必须提交；原始稿件和含正文运行日志只留在忽略的 `output/hk004-hermes-r2/`。

### 启动前宿主发现

Hermes 0.20.5 的运行时 loader 会在 `HERMES_ENABLE_PROJECT_PLUGINS=1` 时扫描项目 `.hermes/plugins`，但同版本 `hermes plugins list/enable` 的枚举实现仍只有 bundled、用户插件和 entry point，没有加入项目插件。因此项目插件可以被 loader 看见，却无法走官方 CLI 的 list/enable 启用流程；R1 的这项安装体验问题仍存在。

本轮不修改外部 Hermes checkout，也不手工篡改真实用户配置。隔离测试改把同一 probe 复制到隔离 `HERMES_HOME/plugins/`，用官方 `hermes plugins enable` 启用。若形成产品候选，默认组装为可复制到用户插件目录并由 CLI 明确启停的静态 companion；项目级安装只能作为手工配置的受限选项，不写成已由 CLI 支持。

## 重开依据

R1 在 Hermes 0.20.0 只验证了确定性 `transform_llm_output`，三题又没有复现可机械删除的正文外包装，因此以 `BASELINE_NOT_REPRODUCED` 终止。Hermes 0.20.5 的官方插件 API 现可在插件内调用宿主管理的 `ctx.llm.complete_structured()`：它沿用当前 provider、模型和凭据，执行一次有超时的结构化 LLM 调用，不启动工具循环。`transform_llm_output` 仍在主工具循环完成后、`post_llm_call` 和最终交付前同步执行，首个非空字符串可以替换最终文本。

这使“同一 D0 写后语义复核后直接交付 D0 或 D1”成为新的可验证假设，不再等同于 R1 被拒绝的 transform-only 机械清理。新增调用会真实消耗 token，必须显式启用、只调用一次、失败回退 D0。

### 在线兼容修正

`ctx.llm.complete_structured()` 在 Ollama Cloud 标记原子可用，但通过本机 OpenCodex 兼容代理调用 Alibaba Token Plan 2 时，主模型正常、插件结构化调用因供应商不接受该 `response_format` 返回 HTTP 400；插件已逐字回退 D0。为保持多 provider 可用性和“一次调用”预算，R2 后续统一改用同一官方 `ctx.llm.complete()`，由插件在本地对唯一 JSON 对象作严格解析和字段校验；不在 structured 失败后追加第二次模型调用。该变化不改变写稿问题、验收标准或 fail-open 边界。

## 阶段一：生命周期标记

在隔离项目插件中注册当前 checkout 的 `chinese-official-writing` Skill，并记录脱敏事件摘要。固定原子：

1. 主模型只输出 `HA_R2_D0`。
2. `pre_llm_call` 记录当前 session/task/turn 与原始请求摘要；`on_skill_lifecycle` 只有观察到本插件注册的当前 Skill `action=loaded` 才为该 session/task 设防。
3. `transform_llm_output` 只在已设防事务中调用一次宿主管理的 `ctx.llm.complete()`，要求返回唯一 JSON 对象 `{"action":"REPLACE","issues":["WRAPPER_OR_GENRE"],"final_text":"HA_R2_D1"}`，经本地严格解析后返回 `HA_R2_D1`。
4. `post_llm_call` 必须观察到 D1，并立即清除该事务内存；插件 LLM 自身不得递归触发主回合的 transform。

成功条件：最终 stdout 只交付 D1；同一事务各有一次 pre/skill/transform/plugin-LLM/post，post 的响应 hash 等于 D1；无第二次 transform、无限循环或跨任务串稿。结构化响应无效、超时或抛错时必须逐字交付 D0，并记录 `fail_open`。

## 阶段二：当前 Skill 三题同稿复核

三题均要求“只输出可直接使用的完整正文，不解释过程”，不设字数下限。每题由主模型先形成完整 D0；同一 `transform_llm_output` 只调用一次结构化审稿，最多选择原样 `KEEP` 或返回完整 D1。D0 是不可变回退稿，不允许二次返修。

### H1 稀疏采购申请

某中心现有两台推理服务器过去10个工作日平均利用率为93%，工作日每天约16项任务等待；拟增购两台推理服务器用于缓解资源紧张，预算额度、采购方式和供应商均未确定。要求写采购申请正文，可以基于这些事实和常识写一层合理原因及预期作用，但不能把拟采购、待定事项或预期作用写成既成事实。

目标检查：避免过度保守导致正文短薄；保留93%、10个工作日、约16项、两台和三项未决状态；允许“缓解资源紧张、提高任务处理效率”等低强度预期判断，不把合理推断误删。

### H2 活动新闻

2026年8月24日，某单位举办业务能力提升活动，共52人参加；其中49人当天完成实操，3人于2026年8月26日补测。一名参与者表示“这次演练让我更清楚实际操作中的薄弱环节”。收集到的改进意见仍待分类核对。要求以主办方口吻写活动新闻正文。

目标检查：两个完整日期、52/49/3范围、补测状态、单人引语和意见待核均保留；影响谓语不能由49人或1人扩大为52人全体成效；可以作一层与活动直接相关、低强度的意义判断。

### H3 情况说明

数据接口联调已完成，但验收记录已形成而未随材料附送；岗位培训尚未开展，具备场地和讲师条件，可另行安排；设备采购正在询价比选，尚未形成采购决定。要求写情况说明正文。

目标检查：区分“已完成”“记录已形成但未附”“明确未开展但可安排”“正在比选且未决”；允许单独指出未决状态，不把“可安排”升级为“已安排”，也不凭空增加责任主体、期限或办理承诺。

## 写后审稿协议

- 输入只包含原始任务和 D0；审稿指令必须明确：合理原因、低强度预期作用、基于事实和常识的一层结论不是天然风险，不能因谨慎而机械删除。
- 只有发现事实/数字/日期/主体/状态升级、材料外程序或责任、文种错位、范围扩大、正文外包装、明显失衡或不直接可用时才 `REPLACE`；否则 `KEEP`。
- D1 必须是完整正文，不得附加说明、自评、字数或 Markdown 围栏。D1 为空、不是字符串、与 schema 不符或超过有界长度时回退 D0。
- 审稿只允许一次；插件不指定或更换用户模型/凭据，不把辅助调用伪装成免费能力。记录 provider/model、token 数、动作、字符数和 hash，不记录正文。

## 进入产品 adapter 的条件

- 三题均形成有效主模型 D0；至少两题出现明确的目标问题并由同稿 D1 安全改善，或 D0 已安全时正确 `KEEP`。不能以独立重写替代同稿证据。
- 三题均无候选独有的事实、状态、主体、数字、日期、文种、合理推断、篇幅或直接可用性硬回退。评判不把“篇幅较短”或“存在合理推断”单独视为失败。
- 生命周期标记和三题均证明：当前 Skill 确实加载、恰好一次辅助调用、最终交付只见选定正文、post 观察到同一正文、错误路径逐字回退 D0。
- 只有以上成立才补 `hooks/adapters/hermes-agent/`、assembler、宿主能力表、说明和直接相关测试；否则收口为 `SEMANTIC_REVIEW_REJECTED`、`LIFECYCLE_INVALID` 或 `TECHNICAL_INVALID`，不保留 `HOLD`，也不硬造 adapter。

## 工程门

若形成产品候选，先重跑同题生命周期，再执行 Hermes adapter 单元/smoke、companion 组装、镜像边界、`python maintenance/quick_validate.py`、`git diff --check` 和只读 review。测试通过后提交候选分支；不自动合入 `main`。
