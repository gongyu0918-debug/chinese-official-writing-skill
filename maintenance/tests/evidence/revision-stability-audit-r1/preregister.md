# 同稿七轮修改稳定性验证 R1

## 固定范围

- 产品基线：`5fbb2d26c49d0b780ad11fc4cff008854995ad3f`。
- 产品候选：`22772262b34f43e5cd975fb8b0aaa2f945aa5adb`。
- 两条既有低价路线：Alibaba Token Plan 2 DeepSeek V4 Flash 与 MiniMax M3，均配置 `max`。
- 两臂、两路线，各自新建一个真实 CLI session，每个 session 七轮，共 4 个 session、28 份完整稿。
- 用户已授权独立 CLI/Harness 真实改稿；本轮题面及精确检查清单已由根代理确认。材料明确为虚构测试材料，不代表现实统计。
- 只评估普通 Skill 的连续修改，不安装、不启用 Hook，不改产品，不以本轮宣称真实 compaction 恢复通过。

## 真实会话协议

本机已检查 Desktop `codex-cli 0.153.1`：`exec --help` 与 `exec resume --help` 均返回 0。初始命令不带 `--ephemeral`，让 CLI 持久化会话；第 2—7 轮使用 `codex exec resume <明确 session ID>`，只发送本轮增量指令，不拼接历史、不重新提供旧稿假装恢复。

沿用 `complaint-reflection-r1/desktop_writer.py` 的 Desktop CLI 选择、plugins/apps/memories 关闭、既有模型目录与本地模型入口、只读沙箱和 never 审批配置。新 runner 的 skills.config 启用与禁用项均指向 SKILL.md 文件，按[官方启停示例](https://learn.chatgpt.com/docs/build-skills#enable-or-disable-local-codex-skills)修正旧 wrapper 使用目录的问题；不改旧二十稿冻结来源。全局同名安装仍保留，并继续依据实际 trace 检查污染。每轮保留模型与隔离参数；resume 的工作目录固定在对应 runtime。

协议依据：[官方非交互模式](https://learn.chatgpt.com/docs/non-interactive-mode)确认指定 ID 的 exec resume，以及 JSONL 中的 `thread.started.thread_id` 和 `turn.completed.usage`。帮助与官方契约只证明命令支持；只有实际 4 条链的日志才能证明本轮真实续写成立。

## 冻结与留存

首次 `--prepare` 要求工作树完全 clean，解析两臂固定 commit，导出并记录产品文件数和 SHA-256 fingerprint；完整题面、每轮字面线索及人工检查清单冻结进 fixture。默认新目录为 `output/revision-stability-audit-r1/r1`，不覆盖已有目录或孤立原始证据。

每个 session、每轮记录真实 thread ID、来源 session ID、实际 CLI argv、当前增量 prompt、完整 trace/stderr/final、usage、耗时、hash、已观察的 reference 读取和技术失败。第 2—7 轮的 ID 必须与第 1 轮一致；不同 provider/arm 的 ID 必须独立。

## 题链与判定

七轮全文题面和检查清单见 `cases.json`：初稿 → 更新统计和状态 → 交换两小节 → 删除指定事项 → 新增一个独立自然段 → 650 字上限压缩 → 仅撤销第 3 轮调序并保持其他变更。

- 技术失败（调用失败、超时、缺终稿、session ID 缺失/不一致、无 turn.completed、用户 Skill 或 Hook 污染）才停止该链；不自动重试，不丢弃失败记录。
- 篇幅、事实、状态、文种、直接交付或局部修改失败均保留并继续后续轮次，观察后续恢复。R1 的 900—1100 字要求不构成阻止整个链继续的技术门。
- 字面 required/forbidden 及字数仅是观察线索；状态、责任归属、材料外事实和合理分析由人工逐稿复核。不得把逐字不匹配直接换算为语义失败率。
- R7 相对 R6 的客观检查：只交换“（一）场景核验”与“（二）目录归集”两块，调整序号；块内及其他正文完全保持。只忽略文件换行风格和首尾空白，不忽略内部措辞变化。结构无法定位时记无法计算，不能冒充 PASS。
- 分别报告：技术有效轮次/28、语义与直接交付通过稿数/技术有效稿数、完整七轮 session 数/4、R7 局部修改精确保持结果；保留两臂与 provider 明细，不把 4 条相关序列当成 28 个独立样本。

## 命令

```powershell
py -3 -B maintenance/tests/evidence/revision-stability-audit-r1/run_chain.py --prepare
py -3 -B maintenance/tests/evidence/revision-stability-audit-r1/run_chain.py --provider alibaba2 --arm baseline
py -3 -B maintenance/tests/evidence/revision-stability-audit-r1/run_chain.py --provider alibaba2 --arm candidate
py -3 -B maintenance/tests/evidence/revision-stability-audit-r1/run_chain.py --provider minimax --arm baseline
py -3 -B maintenance/tests/evidence/revision-stability-audit-r1/run_chain.py --provider minimax --arm candidate
py -3 -B maintenance/tests/evidence/revision-stability-audit-r1/run_chain.py --summarize
```

以上真实写稿命令尚未在本记录创建时运行；由根代理提交、prepare 后启动。
