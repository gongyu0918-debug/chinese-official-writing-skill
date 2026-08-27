# HK-004 Hermes Agent adapter R2 结果

## 结论

`HK-004-HERMES-R2` 已合并到本地 `main`、未推送、未发布，形成 Hermes Agent 单次写后复核能力。当前明确支持已验证的 Hermes Agent 0.20.5—0.20.6 新建、不可恢复 `hermes chat -q/--query/--query-file` 单题：profile 用户插件被官方 CLI 列出和启停，精确 companion Skill 预载后，同一回合在 `transform_llm_output` 内只调用一次宿主管理的 LLM，严格选择 D0 或完整 D1，失败保留 D0，`post_llm_call` 再闭合 task、turn 与用户可见响应 hash。

本轮不把它写成共享多 Stop 门禁，也不宣称支持交互 CLI、resume/continue、`hermes --oneshot` 或 gateway。0.20.5—0.20.6 的 one-shot 路径在预载 Skill 前没有同步等待原生插件完成加载；更关键的是，宿主在 `transform_llm_output` 前已经持久化 D0。确定性 D0→D1 后恢复同一 session 实测读回 D0，因此产品代码本身拒绝可恢复会话，不只在说明中提示。

## 宿主与安装事实

- 固定公开基线：`main@c784e3721db8f170015e1220ea92c815f747a89a`，已发布产品 tag `v1.6.18@67a68257f8a79220a38e961ced932bcb022cf86b`。
- 开发分支/worktree：`codex/hermes-lifecycle-r2` / `F:\Workspaces\chinese-official-writing-skill-worktrees\hermes-lifecycle-r2`；本地 `main` 先快进到候选提交，再用本记录提交收口。
- Hermes 从0.20.0先更新到0.20.5、upstream `86221181`。本次继续验证时官方检查显示落后10个提交；第一次 `hermes update --yes` 因 GitHub TLS 握手失败退出，代码未变且 gateway 已恢复。只读 `git ls-remote` 随后成功，唯一重试把安装更新并收敛到 upstream `a9611f3c6f7ff287a4f10f71a77d7c5a808ea1c8`，版本仍为0.20.5。
- 验证期间上游又发布0.20.6。官方 `hermes update --yes` 因浅克隆历史分叉按自身流程重置到 `5fc308a70719a83cccdbba4c0e39c23f5a8239d5`，安装工作树随后为 `main...origin/main` 且无未提交文件。Windows 自替换窗口第一次调用 launcher 暂时失败，新 `hermes.exe` 落盘后版本命令恢复；更新器没有实际恢复 gateway，故再次用官方 `hermes gateway start` 启动，并由 status 确认 PID 67496 运行。
- Hermes 0.20.5 运行时可以在显式环境开关下扫描项目插件，但 `hermes plugins list/enable` 仍不枚举项目插件。候选因此只把 profile 用户插件目录写成默认安装路径。
- 本地 `main` 重新组装物为54文件，fingerprint `6115fb292bd72883db9ef624bdf51e520152de064f0ed2d95fed77e8b9b87bce`；`hermes plugins doctor ... --ci` 验证为0个工具、7个 Hook。它与候选 worktree 的 `7991fbd26bff60c91a2c08ea7edd7f8e96e7c48a17936878e47aa56f17dbe910` 仅有9个文本文件的 CRLF/LF 字节差异，逐文件换行归一化后内容相同；指纹按实际组装字节记录，不以宽泛换行改写破坏既有镜像字节一致契约。候选未申请工具覆盖权限，manifest 中一项非官方 `skill_namespace` 字段已删除。

## 生命周期问题与修复

1. `ctx.llm.complete_structured()` 在 Ollama Cloud 标记可用，但 Alibaba Token Plan 2 经本机 OpenCodex 兼容入口返回 HTTP 400。候选改为恰好一次 `ctx.llm.complete()`，本地严格解析唯一 JSON；结构错误、超时或异常不追加第二次调用。
2. 预载 Skill 的首次 `on_skill_lifecycle` 没有 session，且与 `on_session_start` 跨线程。原 `threading.local()` 在真实 `chat -q` 中得到 `pending=0`，导致未设防。最新版宿主的该事件仍携带 `task_id`，且与随后 `session_id` 相同；候选因此只在30秒内、仅受支持的新建 query、`task_id=session_id` 时一次性精确绑定。不支持的 argv 不再留下 pending；缺 `task_id`、标识不等或不支持的宿主面均安全旁路；两条并行 pending 记录按各自精确 ID 绑定，不使用“下一个 CLI”队列。
3. 冷审指出原候选只在 transform 阶段记 hash，没有闭合 `post_llm_call` 的响应与回合。产品现保存预期终稿 hash，并要求 post 的非空 task、turn 和可见响应三者精确匹配；错 task、错 turn、错响应均禁用该 session 到 finalize。同 session 两个回合重叠时不覆盖状态；即使旧轮的辅助调用已经开始，owner token 失效后也丢弃 D1、保留 D0。最终 owner 复核、预期 hash 提交与返回选择在线性化锁内完成，正常 post 后消费唯一一次 session 激活。
4. 冷审后追加的宿主持久化诊断不是原预登记成功项，不追写成预登记结论。0.20.5 upstream `a9611f3c` 的隔离 probe session `20260827_192539_07ec36` 对用户交付 `HA_R2_D1`，post 也观察到 D1；随后不加载 Skill 恢复同一 session，Hermes 明示只有1条历史 user message并逐字返回 `HA_R2_D0`。0.20.6 upstream `5fc308a7` 的当前源码仍在 transform 前调用 `_persist_session`。候选因此新增 argv 级边界，只允许 `chat` 为首个命令 token 且 inline 与 query-file 二选一的新建单题，拒绝交互、`--resume/-r`、`--continue/-c`、one-shot 和 gateway；one-shot 混合、`gateway chat -q` 及 `-q + --query-file` 异常组合均不启用。
5. Hermes 会在 Agent 初始化时重置早期命名 logger，one-shot 又会 `logging.disable(logging.CRITICAL)` 并把 stdout/stderr 指向空设备。候选正常路径不写正文事务；显式 `HERMES_PLUGINS_DEBUG=1` 时，新建 `chat -q` 可见无正文的 lifecycle、action、字符数和 hash 摘要。one-shot 不以日志或 usage 冒充 Hook 已运行。
6. Token Plan 2 的一篇稀疏采购稿新增“设备检修/故障时缺少冗余、增购后留出冗余”，不属于允许的一层合理推断。审稿提示只增加这一原子反例，同时保留“缓解资源紧张、减少排队、提升处理时效”。首次固定 D0 修订223→180字虽删除外扩，但合并了含“拟增购两台”的硬锚句，产品门禁正确回退；增加“硬锚句不跨句合并/搬移”的最小修订约束后，同一 D0 223→182字，模型动作 `REPLACE`，产品硬锚 parser 接受。
7. 冷审发现 prompt 已要求 `KEEP` 的 `final_text` 为空，但 parser 曾接受完整 D0 回显。现已收紧为只接受空字符串；回显正文、附加字段、无效 issue 或不完整 D1 均保留原始 D0，不尝试第二次模型调用。

## 真实稿与同稿结果

| 样本 | 宿主/模型 | 结果 | 结论 |
|---|---|---|---|
| 0.20.6 稀疏采购申请 R19 | Hermes `chat --query-file` / Alibaba Token Plan 2 DeepSeek V4 Flash max | 128→128字符 `KEEP`；post 四项闭合均为 true | 128字符正文长于116字符任务文本；保留2台、10个工作日、93%、每天约16项、拟增购2台和三项未决，原因前置，无故障、冗余、程序或承诺外扩 |
| 0.20.6 更新后产品标记 R17 | Hermes `chat --query-file` / Ollama Cloud DeepSeek V4 Flash max | 15→15字符 `KEEP`；`pending=1/bound=true/armed=true`，post 四项闭合均为 true | upstream `5fc308a7` 的当前宿主仍完成插件注册、跨线程绑定、一次辅助调用和同回合闭合；此后产品只改版本说明 |
| `--query-file` 产品标记 R15 | Hermes `chat --query-file` / Ollama Cloud DeepSeek V4 Flash max | 20→20字符 `KEEP`；`pending=1/bound=true/armed=true`，post 四项闭合均为 true | 首次证明官方文件单题入口可完成同回合闭合；后续只收紧异常 argv，并由 R17 重跑正常路径 |
| 更新后产品标记 R13 | Hermes `chat -q` / Ollama Cloud DeepSeek V4 Flash max | 9→9字符 `KEEP`；`task_match=True`、`turn_match=True`、`response_match=True`、`history_match=True` | upstream `a9611f3c` 上当前插件、Skill 预载、同回合 transform、一次辅助调用和 post hash 闭合成立 |
| resume 旁路 | 同一 R13 session / Ollama Cloud | 再次显式传同名 Skill和`--resume`，主模型输出 `HA_R2_RESUME_BYPASS`；日志中辅助调用总数保持1 | 产品 argv 门确实拒绝可恢复 session |
| transform 持久化反例 | Hermes probe / Ollama Cloud | 首轮用户可见与 post 均为 `HA_R2_D1`；恢复同一 session 后返回 `HA_R2_D0` | 宿主保存的是 transform 前 D0，交互/恢复不能支持 |
| 更新后稀疏采购申请 R13 | Hermes `chat -q` / Alibaba Token Plan 2 DeepSeek V4 Flash max | 133→133字符 `KEEP`，post 四项闭合均为 true | 原因前置，保留2台、10个工作日、93%、约16项和三项未决；未新增故障、冗余、程序或承诺 |
| 稀疏采购申请 | Hermes `chat -q` / Alibaba Token Plan 2 DeepSeek V4 Flash max | 195→195，`KEEP` | 保留2台、10个工作日、93%、约16项和三项未决；有合理原因/预期作用，无故障或冗余外扩 |
| 状态未决情况说明 | Hermes `chat -q` / Ollama Cloud DeepSeek V4 Flash max | 77→77，`KEEP` | 区分已完成、记录已形成未附、尚未开展但可安排、询价中且未决；无状态升级 |
| 采购失败稿固定 D0 R1 | Hermes probe / Alibaba Token Plan 2 | 223→180，`REPLACE` | 删除故障/冗余外扩，但安全合并硬锚句；产品 parser 以 `anchor_relation_unverified` 回退，作为反例保留 |
| 同一固定 D0 R2 | Hermes probe / Alibaba Token Plan 2 | 223→182，`REPLACE` | 只删除外扩并保持硬锚句边界；所有数字、数量、拟购、三项未决和合理影响保留，产品 parser 接受 |

三篇当前 Skill 原型还覆盖活动新闻和情况说明：H1 164字、H2 155字均安全 `KEEP`；H3 171→169字删除标题叠词。它们用于形成审稿原子，不替代最终 product companion 的 inline/query-file 生命周期证据。

## 明确限制

- 交互 CLI / resume / continue：`UNSUPPORTED_HOST_LIMIT_PERSISTENCE_ORDER`。0.20.6 upstream `5fc308a7` 仍先持久化 D0、后执行 transform；0.20.5 的确定性恢复实验已复现状态分叉，产品代码主动拒绝这些 argv。
- `hermes --oneshot`：`UNSUPPORTED_HOST_LIMIT`。0.20.6 当前源码仍只在显式未知 toolset 校验时同步 `discover_plugins()`；正常 one-shot 在预载 Skill 前不能稳定保证插件已注册。0.20.5 upstream `a9611f3c` 的更新后实测仍只有主模型1次 API 调用；0.20.6 不用重复付费调用冒充协议变化。
- gateway/并发：`NOT_LIVE_VERIFIED`。产品当前完全拒绝 gateway；同 session 回合重叠只在单测证明安全旁路，不外推为 gateway 支持。
- 当前只有 `delivery_review`，最多一次辅助调用；不支持保护性删除、篇幅不足、超长、洁净度或重复清理等共享多阶段能力。
- 同时启用其他 output transform 时，Hermes 采用首个非空 transform 的宿主顺序，未做组合验证。
- 审稿模型无效、超时、生成完整 D1 失败或硬锚关系仍需语义判断时保留 D0；安全回退不等于目标修复成功。

## 工程验证

- `python -B -m unittest maintenance.tests.test_hermes_gate_adapter`：20/20 通过。
- Hermes 及直接相关契约、组包、状态账、消融和边界测试：122/122 通过。
- `python -B -m unittest discover -s maintenance/tests -p 'test_*.py'`：721/721 通过。
- `quick_validate.py chinese-official-writing`、`git diff --check`、JSON 解析均通过。
- `hermes plugins doctor <final-companion> --ci`：导入、manifest 和注册通过，0 tool、7 hook。

## 主要命令

```text
hermes update --yes
hermes update --check
hermes update --plan
hermes --version
hermes gateway status
hermes gateway start
hermes plugins list --plain --no-bundled
hermes plugins enable chinese-official-writing-gate
hermes plugins doctor <companion> --ci
hermes chat -q <prompt> -Q --provider ollama-cloud --model deepseek-v4-flash:0731 --reasoning max --skills chinese-official-writing-gate:chinese-official-writing
hermes chat --query-file <path> -Q --provider ollama-cloud --model deepseek-v4-flash:0731 --reasoning max --skills chinese-official-writing-gate:chinese-official-writing
hermes chat -q <prompt> -Q --provider opencodex --model alibaba-token-plan-2/deepseek-v4-flash-0731 --reasoning max --skills chinese-official-writing-gate:chinese-official-writing
python -B -m unittest maintenance.tests.test_hermes_gate_adapter
python maintenance/tools/assemble_hook_companion.py --host hermes-agent --output <new-output>
```

原始正文、usage、session DB 和事件 JSONL 只留在忽略的 `output/hk004-hermes-r2/`；可提交证据只保留脱敏结果、失败/接受 fixture 与 hash。一次误把 Hermes profile 根指向用户目录产生的空目录/配置已按精确创建时间移到忽略的 `output/hk004-hermes-r2/accidental-hermes-home-backup-20260827-181637/`，原路径不再存在，备份可恢复。没有修改 description、普通写作 references、付费分支或已发布 tag；没有合并、推送或发布。
