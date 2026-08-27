# Hermes Agent Hook companion

本目录是 Hermes Agent 的静态适配层，已验证 Hermes Agent 0.20.5 与0.20.6；更高版本须先重跑生命周期 smoke。它把当前包内 `chinese-official-writing` Skill 注册为 `chinese-official-writing-gate:chinese-official-writing`，只在新建且不可恢复的 `hermes chat -q/--query/--query-file` 单题中、该精确 Skill 实际预加载后，为完整 D0 增加一次同步写后复核。

组装后的 companion 根目录包含 `plugin.yaml`、`__init__.py`、`hook-capability.json`、`skills/chinese-official-writing/`、README 和 MIT LICENSE。组装器只生成文件，不复制到 Hermes、不启用插件、不修改配置，也不启动模型调用。

## 启用

先展示并确认目标目录，再把完整 companion 目录复制到当前 Hermes profile 的 `plugins/chinese-official-writing-gate/`。Windows 默认 profile 通常位于 `%LOCALAPPDATA%\hermes`，其他安装以 `HERMES_HOME` 为准。复制完成后由用户明确执行：

```text
hermes plugins enable chinese-official-writing-gate
```

已验证的新建单次 query 通过以下 Skill 标识启用写后复核：

```text
hermes chat -q "<写稿任务>" -Q --skills chinese-official-writing-gate:chinese-official-writing
hermes chat --query-file "<UTF-8任务文件>" -Q --skills chinese-official-writing-gate:chinese-official-writing
```

Hermes 0.20.5 的运行时可以扫描项目 `.hermes/plugins`，但同版本 `hermes plugins list/enable` 仍不枚举项目插件；因此本 companion 默认采用官方 CLI 可列出、可启停的 profile 用户插件目录，不把项目插件写成已支持的安装路径。

Hermes 0.20.5—0.20.6 的 `--oneshot/-z` 路径在预载 Skill 前不能稳定保证原生插件已完成同步加载；本 companion 不把 one-shot 写成已支持。交互 CLI、`--resume/-r`、`--continue/-c` 和 gateway 也不启用本复核：当前宿主在 `transform_llm_output` 前持久化 D0，恢复会话会读取变换前文本。需要单题时使用新建的 `hermes chat -q ... -Q` 或 `hermes chat --query-file ... -Q`，不要恢复该 session；`chat` 必须是首个命令 token，其他排列安全旁路。

## 行为与边界

- 当前只支持静态 `delivery_review`；Hermes 组装器会拒绝其他 capability，不把单次同步复核宣称为共享多 Stop 门禁。
- 空 session 的预载事件只有同时携带非空 `task_id`、当前 argv 已是受支持的单题，且其值在30秒内与随后新建 query 的 CLI `session_id` 精确相等时才绑定，并且只消费一次。不支持的 one-shot/交互 argv 不登记 pending；缺 `task_id` 或标识不等时安全旁路；相同标识到达非 CLI、交互或可恢复会话时只丢弃该次预载，不转绑其他 session。
- `transform_llm_output` 在主工具循环完成后、最终交付前运行。插件使用当前会话已有的 provider、模型和凭据调用一次宿主管理的 `ctx.llm.complete()`；不覆盖 provider 或模型，不读取密钥。不同供应商的 token 计费由 Hermes 和用户所选服务决定。
- 使用普通 chat completion 加严格本地 JSON 解析，是因为部分 OpenAI 兼容代理不接受结构化 `response_format`。解析、超时、模型调用、锚点检查或插件异常均逐字保留 D0，不追加第二次模型调用。
- KEEP 的 `final_text` 必须为空，回显 D0 也按无效响应安全回退；REPLACE 必须给出完整正文，并通过数字、日期、数量、引语、字段和未决状态关系的确定性反控。关系仍需二次语义判断时同样回退 D0。
- `post_llm_call` 必须与当前 `task_id`、`turn_id` 和预期终稿 hash 精确闭合；标识或可见响应不一致时禁用该 session 直到 finalize。一个 session 只消费一次激活；辅助调用期间出现同 session 重叠轮次时 owner 失效，旧轮 D1 不会返回。
- 当前请求说“本次关闭 Hook”或属于只审不改时不调用写后模型。普通 Skill 安装不会启用本插件；未使用本 companion 的命名空间 Skill 时也不会启动。
- 请求、D0 和候选只在插件进程内存中保存到本回合结束，插件不写正文事务文件、不上传日志。Hermes 自身仍按宿主规则保存 session；0.20.5—0.20.6 保存的是 transform 前 D0，所以该 session 不得恢复。宿主收集 INFO 记录时，审计摘要只含动作、原因、标识闭合结果、字符数和 hash；在已支持的新建单题路径显式设置官方 `HERMES_PLUGINS_DEBUG=1` 时，同一无正文摘要也会写到 stderr 和宿主诊断日志。进程异常退出时插件内存随进程释放。
- Hermes 会执行所有已注册的 output transform，再采用首个非空结果。不要同时启用另一个会改写最终文本的 transform 插件，否则输出顺序和额外 token 消耗由宿主插件顺序决定。

## 关闭

当前任务可直接说“本次关闭 Hook，按普通 Skill 完成”。完全关闭使用：

```text
hermes plugins disable chinese-official-writing-gate
```

停用后仍可使用普通 `chinese-official-writing` Skill；停用、移除和删除 profile 插件目录是不同操作，移除目录前应先核对绝对路径并确认插件已停用。
