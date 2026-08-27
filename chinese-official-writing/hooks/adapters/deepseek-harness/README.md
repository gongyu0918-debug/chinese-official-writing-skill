# DeepSeek Harness Hook companion

本目录是 DeepSeek Harness（DSH）的原生 Cordis Profile Bundle 适配层。它直接使用 `agent/pre-step`、`tools/post-execute` 与 `agent/turn-stopping`：从当前 open turn 的内存事件取得完整 D0，按同一 turn 重建 Stop 次序，并用 `agent.steer()` 续写。它不依赖会话 JSONL，也不修改 DSH 本体。

DSH 0.1.1-rc.2 自带的 Claude Code Hook bridge 在 Stop 载荷中不提供 `last_assistant_message`，不能直接满足本门禁的 D0 绑定要求；因此本 companion 使用原生插件，不把协议名称相似当作完整兼容。

组装后的 companion 根目录包含 `package.json`、`cordis.patch.yml`、`index.mjs`、静态能力配置和一份 canonical Skill。组装本身不安装、不启用、不联网，也不修改任何 DSH profile。用户确认目标 profile 后，使用绝对路径安装并重启该 profile：

```text
dsh plugin --profile <profile> add <absolute-companion-directory>
dsh --profile <profile> --dump-config
```

配置树中必须出现 `id: chinese-official-writing-gate-dsh`。停用时运行 `dsh plugin --profile <profile> remove chinese-official-writing-gate-dsh`，然后重启该 profile；不要删除整个 `$DSH_HOME` 或 profile 目录。

OpenCodex 2.32.0 已原生提供 DSH 导出面。先把新配置导出到未占用路径，再人工核对并合并到目标 `$DSH_HOME/settings.yaml`：

```text
opencodex export --client dsh --out <new-settings-yaml>
```

`agent-default-model` 必须逐字选择已导出的 provider/model；不要为模型补写导出文件未声明的 `reasoningEfforts`，否则 DSH 会在网络请求前拒绝不受支持的推理档位。导出文件只使用回环代理占位，不应写入真实密钥。

默认数据父目录是 `$DSH_HOME/plugin-data/chinese-official-writing-gate`；只有绝对路径环境变量 `COW_DSH_GATE_DATA` 才会覆盖它。共享核心在其下创建 `candidate-ai-gate-hook`，终态删除正文、请求和事务文件，只保留 hash/阶段回执；异常退出仍可能留下当前未完成事务，需先停用 companion，再只清理这个精确数据子目录。

组装时必须明确能力：默认 `delivery_review`；还可静态选择 `protective_expansion`、`under_length`、`over_length`、`delivery_cleanliness`、`repetition_cleanup`。当前在线证据只覆盖 Windows、DSH 0.1.1-rc.2、headless profile 和 `delivery_review` 多 Stop 闭环；TUI、Web 及其他 capability 不据此宣称在线通过。Python/core 不可用或超过宿主 Stop 上限时，adapter 优先逐字回退本轮 D0。
