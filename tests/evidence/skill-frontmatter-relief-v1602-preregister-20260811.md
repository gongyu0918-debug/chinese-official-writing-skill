# SKILL frontmatter 元数据减载预注册（v1.6.2）

## 固定边界

- 固定基线：`d17cb8853274ba6dec4d686171daf4f8972a0ec8`。
- 候选只处理六个运行面 `SKILL.md` 的 frontmatter、`tools/sync_adapters.py` 的同步逻辑和直接相关测试；不改 description 正文、运行时写作规则、references、Hook 协议、路由条件、版本号或发布状态。
- 通用入口统一只保留 `name`、现有 `description` 和顶层 `tags`。删除 `license`、整块 `metadata`、兼容 Agent 列表、安装路径、平台版本和展示字段。
- GitHub 根 `LICENSE`（MIT）与 `LICENSE-SKILL`（MIT-0）保留；Codex/Claude 插件 manifest 的 MIT 声明保留。SkillHub clean 包构建时排除包内 `LICENSE`，不把许可证全文重复上传；OpenClaw/ClawHub 纯包现有 MIT-0 `LICENSE` 本轮不改。
- Red SkillHub 专用表面不在本轮范围。

## 工程验收

1. 六个 frontmatter 均可由 YAML 解析，且只含 `name`、`description`、`tags`。
2. canonical、`skills/`、`.agents/`、`.qwen/`、Hermes、OpenClaw 的正文与既有运行规则保持一致；OpenClaw 的下划线 name 保持不变。
3. `tags` 固定为 `chinese, official-document, writing, gongwen, ai-compute`。
4. 同步器连续运行两次幂等；版本与许可只由同步器常量、根许可证和插件 manifest 承担，不再回写 SKILL frontmatter。
5. SkillHub clean allowlist 为 canonical 去除 `agents/openai.yaml` 与 `LICENSE`；不得混入缓存或仓库文件。
6. focused tests、全量 unittest、Promptfoo stub smoke、固定基线确定性消融、quick validate、插件校验、镜像一致性、`git diff --check` 全部通过。

## 真实链路验证

- 写手：Alibaba Token Plan `deepseek-v4-flash-0731` max、Ollama Cloud `deepseek-v4-flash:0731` max、MiniMax M3 max。
- 每家 3 个成对任务：短事务通知、长篇事实受限报告、只审不改；AB/BA 平衡，首个 final、零重试，共 9 对/18 次调用。
- 两臂只允许 frontmatter 元数据不同；每次 trace 必须实际读取对应 `SKILL.md`，否则该臂无效。
- 硬边界：题面事实、数字、未决状态、联系人/落款、篇幅与输出范围；另检查正文不得泄露 license、Agent 兼容名单、安装路径、仓库或平台元数据。
- 任一可复现 Candidate 独有事实遗漏、状态改变、错误路由或元数据泄漏即停止，不合入。若无目标硬回退，只能结论为 `REAL NON-INFERIOR METADATA RELIEF`，不宣称整体写作质量提升。

## 独立审查

- 真实输出先匿名、后由 SOL max 复核硬边界与可直接采用成本；出现明显分歧时再交 Kimi/Qwen/Grok 交叉审查。
- 解盲前不读 mapping，不以单次模型波动否决或美化候选。
