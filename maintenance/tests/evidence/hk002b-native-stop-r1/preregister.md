# HK-002b Codex 原生 Stop 最小验证 R1

本轮只验证既有 Hook 的 Codex 原生事件生命周期，固定产品 Git 为 4fd63ce344fec440bbbbc664a7ebd7934751e04e。随后集成树的文档合入和函数提取不改变本轮冻结包；不边运行边读取可变产品。

只有两个独立 CLI 任务：明确正在被写成尚未开展的冻结 D0，以及正常对照。均先使用精确 ollama-cloud/glm-5.3-flash / max。本机已缓存的原生 Codex CLI 版本为 0.151.0。实际模型提交数由事件另计，不能把两个 CLI 任务说成两次上游调用。不重跑前轮 42 调用，不扩大到五路批量。

产品和组装器已经从冻结 Git 导出到本树 output/hk002b-native-stop-r1/frozen-source。完整 companion 由冻结的 maintenance/tools/assemble_hook_companion.py 组装，能力为 delivery_review，共 64 个文件。组装前已展示 [assembly-preview.md](assembly-preview.md)。仅在各例独立 CODEX_HOME 中通过原生 marketplace add、plugin add 注册和启用；所有 home、profile、work、catalog 和原始输出只存本树 output。

首轮提示只放真实材料和冻结 D0 文件位置。文件是被检初稿，不是材料来源或最新更正。模型实际读取当前已安装完整 companion 的 SKILL.md 与该文件，首次逐字提交 D0；随后按原生 Stop 要求提交 repair、verdict 和最终回显。首稿与冻结文本 SHA 不同就不能计入冻结 D0 验证。不声称错误由模型自然成稿产生。

分别检查安装、启用、调用级信任、成功读页、UserPromptSubmit、Stop、实际修订和核验、最终输出 SHA、脱敏终态及回退。--dangerously-bypass-hook-trust 只证明本次调用允许 Hook，不证明永久信任。不开 --ignore-user-config，因为它会屏蔽所测插件。

为保留宿主 turn_context，省略 --ephemeral；隔离 home 中的完整会话日志与 catalog 不入库。请求 route/effort、宿主观察到的 model/effort、上游返回模型身份分开记录。原生续行使用同一路线同一会话，不声称跨 provider 独立核验。候选或已完成进程不能替代事实核验通过；full_draft_fact_verified 保持 false。

失败、超时、误改、绑定不一致和回退均先报告并保留。首轮一次只运行指定 case，无自动重试。必要调整强度或新 attempt 时单独记录，禁止覆盖旧尝试。产品、全局配置、AGENTS、发布及 Pro 均不由本子任务修改。

官方依据：[Codex Hooks](https://learn.chatgpt.com/docs/hooks)，由根任务于 2026-09-09 核对。Stop 提供 turn_id、stop_hook_active、last_assistant_message，block/reason 可发起原生续行。

预期命令按顺序为：python runner.py prepare；python runner.py setup --case error；python runner.py run --case error。先复核错误例和全部失败，再启动 control 的 setup 与 run。runner 默认 max，目录按 case/attempt 隔离。
