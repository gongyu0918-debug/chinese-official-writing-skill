# 日期来源角色真实 D0：NOT_REPRODUCED

按 [预登记](preregister.md) 和 [固定题面](case.json)，两条既有低价路线各自然生成一份新闻消息，随后将同一 D0 原样送入固定基线 `5fbb2d26` 的默认 Hook。没有指定日期写法，没有改造初稿或补抽样。

| 路线 | 自然 D0 日期 | Hook finding | 真实回显次数 | 可见终稿 |
| --- | --- | ---: | ---: | --- |
| Alibaba Token Plan 2 / DeepSeek V4 Flash | 2026年9月5日 | 0 | 1 | 与 D0 完全相同 |
| MiniMax / M3 | 2026年9月5日 | 0 | 1 | 与 D0 完全相同 |

两份独立生成的 D0 恰好相同，正文均为：

```text
中心举办读书交流活动

2026年9月5日，中心举办读书交流活动，共20人参加。
```

各自的 D0 和可见终稿正文 SHA-256 均为 `353db1634bb8796131c8b92857aa9d49f4f1401c73dd736efa218a9c8dfee2e5`，按 UTF-8、LF 换行计算。两稿均未包含被排除的示例年份，也未新增活动内容、效果或后续安排；`delivery_verified=true`。

共完成 2 次真实生成和 2 次真实回显。四次调用的 init、assistant、usage 模型名分别与指定路线完全一致；每次 init 的 tools、mcp_servers、skills、plugins 均为空，实际 tool_use 为 0，未自动重试或切换路线。CLI 实报版本均为 2.1.195。合计顶层 usage：input 21,517，cache-read input 640，output 2,770；CLI 报告费用约 0.293803 USD，仅是宿主字段，不是实际扣费证明。

两次真实生成和两次 Hook 复放都正常完成，实际 provider 命令退出码均为 0。完整两稿、四次绑定/工具禁用/usage、输入和 raw 文件 hash 见 [result.json](result.json)；完整 prompt、stream、stderr、回复与 core 事件留在未提交的 `output/date-source-real-r1/r1/`。

实际命令结构如下，机器绝对路径以占位符表示；先 prepare，再各运行一次 provider。

```text
python -B maintenance/tests/evidence/date-source-real-r1/run.py --prepare --output output/date-source-real-r1/r1 --core-root <BASELINE_TREE>
python -B maintenance/tests/evidence/date-source-real-r1/run.py --provider alibaba2 --output output/date-source-real-r1/r1 --core-root <BASELINE_TREE>
python -B maintenance/tests/evidence/date-source-real-r1/run.py --provider minimax --output output/date-source-real-r1/r1 --core-root <BASELINE_TREE>
```

本轮结论为 `NOT_REPRODUCED`。未展示日期旁路候选的真实收益，故没有应用 [旧原型](../hook-audit-quality-r1/prototype.md)，未进入正常完整日期候选反控，也未修改产品、adapter 或镜像。已知离线错年反例仍成立，本组结果不能证明问题消失，更不能推广为总体可靠率。

验证：`run.py --help`、AST、题面与禁工具 argv 检查、本地直链、两稿及四次调用 hash/绑定核验、`git diff --check` 通过；canonical 和 packages 与固定基线一致。未运行全量测试。本实验的激活事件映射自 Harness 的上下文读取，不是原生宿主 Hook 安装或模型主动读取 Skill 的证明。
