# 日期来源旁路：同稿 core 复放

冻结基线 `3532afd6619ac6256558e9552b92d03da5ae9c0f`；最终候选产品提交 `976bb8a4e11a56e314c7328ff163267e805ad9f9`。本证据只运行实际 core 子进程和有界文件读取，没有新模型调用、假造 repair/verdict JSON、宿主安装或新的题目抽样。

## 自然真实反例

主代理已有 Claude CLI + Alibaba2 原生运行 `native-frozen-normal` 的首次 Stop 自然省略年份。原请求给出目标事实日期 `2026-09-05`，另有明确不得写入消息的格式示例 `2020年9月5日`。本次直接提取第 1 行 `UserPromptSubmit.prompt` 和第 4 行首次 `Stop.native_event.last_assistant_message`；两臂接收原字符串，保留原换行和 Markdown，未改造 D0 或题面。首次 Stop 的 `fault_injected=false`。

| 同一原始 D0 | baseline | candidate |
| --- | --- | --- |
| `9月5日，中心举办读书交流活动，共20人参加。` | 实际选稿为 `2020年9月5日` | 最终可见稿逐字保留原 D0 |
| 日期防损 | 引入示例年份 | 通过本例 |
| 日期完整性 | 错年 | 仍失败，保留漏年 |

两臂均为 `TERMINAL_D0` / `selected=D0`，精确回显后 `delivery_verified=true`，终态原始数据清理标记成立，删除失败为 0。这里的 `D0` 是 core 预处理后的快照标签，不能据此认定输出等于宿主原稿；本例 baseline 的日期审计和最终 hash 已证实引入了 2020 年。

来源与脱敏显示见 [native-source.json](https://github.com/gongyu0918-debug/chinese-official-writing-skill/blob/0721297298b72be7a37b93c6598172791b58e421/maintenance/tests/evidence/hook-four-fixes-r1/date-core/native-source.json)，完整可见文本及结果见 [native-results.json](native-results.json)。公开请求显示只替换两处本地插件路径前缀，**不是实际执行输入**；原始请求 SHA 和 trace SHA 保留。精确复放脚本只接受对应原始 trace，并按 SHA 验证后使用未修改请求。

另一个 `native-frozen-wrong` 首次 D0 已写入“参加人员现场交流了读书心得”，材料没有提供此活动内容。本次仅登记这一原有事实越界，未把它算作日期候选的新回退或已修好的问题，也未对它追加配对运行。

## 原六例最终复放

[inputs.json](https://github.com/gongyu0918-debug/chinese-official-writing-skill/blob/0721297298b72be7a37b93c6598172791b58e421/maintenance/tests/evidence/hook-four-fixes-r1/date-core/inputs.json) 保留原四份真实 D0、原请求及两个明确标注的来源角色请求变体；与先前纯函数输入中的六条记录完全一致。[results.json](results.json) 保存脱敏观察和按 SHA 去重的完整可见文本。

- 三份旧真实漏年稿，两臂都只补回材料中的 2026 年；输出一致。
- 一份旧真实完整日期稿，两臂都逐字保持。
- 同一 TRAINING D0 的两个来源角色请求变体，baseline 均错补 2020 年，candidate 均逐字保持 D0。这是旧真实稿的请求变体，不能说成在变体题面下自然生成，也不代表两次独立自然发生。

六例两臂共 48 次 core 事件，全部直接 emit、精确回显至终态。新增自然反例两臂再运行 8 次事件。最终证据共 7 组输入、5 份不同真实 D0、14 条生命周期和 56 次 core 事件；没有模型修订待续。R1 的 48 次旧复放单独保留，不混入上述统计；它使用了会转 CRLF 的 `git archive`，且候选尚缺最终两行 stale-block 防护，已由 `run-final` 取代。

## 实际执行与复现

最终 baseline 使用 `git cat-file --batch` 的二进制 stdout 导出原始 Git blob，不进行换行转换。脚本在首次 core 事件前固定源码快照，强校验候选 core/date hash。每次运行使用全新目录，拒绝覆盖旧记录；每步保存事件、原始 stdout/stderr、记录和事务状态。只有 core 直接 emit 的正文可由薄 wrapper 精确回显，任何模型修订请求都保留待续。

实际执行以下两条命令，均 exit 0；分别为 48 和 8 次真实 core 事件。复跑需从相同候选源码执行，并改用新的 output 路径：

```powershell
python -B -X utf8 maintenance/tests/evidence/hook-four-fixes-r1/date-core/replay_core.py --repo-root . --output output/hook-four-fixes-r1/date-core/run-final
python -B -X utf8 maintenance/tests/evidence/hook-four-fixes-r1/date-core/replay_native_d0.py --repo-root . --native-events output/hook-four-fixes-r1/native-frozen-normal/native-events.jsonl --output output/hook-four-fixes-r1/date-core/run-native-natural
```

原始 trace、事件和事务副本留在对应 `output/`，不提交含本机路径的原始记录。两个脚本 [replay_core.py](https://github.com/gongyu0918-debug/chinese-official-writing-skill/blob/0721297298b72be7a37b93c6598172791b58e421/maintenance/tests/evidence/hook-four-fixes-r1/date-core/replay_core.py)、[replay_native_d0.py](https://github.com/gongyu0918-debug/chinese-official-writing-skill/blob/0721297298b72be7a37b93c6598172791b58e421/maintenance/tests/evidence/hook-four-fixes-r1/date-core/replay_native_d0.py) 及本目录 JSON、链接、字节绑定的最小检查见 [validation.json](https://github.com/gongyu0918-debug/chinese-official-writing-skill/blob/0721297298b72be7a37b93c6598172791b58e421/maintenance/tests/evidence/hook-four-fixes-r1/date-core/validation.json)。未重跑全量测试。

## 限制

这证明列明输入中默认 delivery_review core 的最终选稿降低了错误补年风险。新增自然样本保留漏年，不能宣称日期完整性已修好；不能从一份被观察到的反例估计总体发生率。echo 由薄 wrapper 按 core 输出逐字完成，这不是新模型响应或新增宿主在线证据。正常自动补年仍没有独立保留原始宿主 D0 恢复快照，本证据不覆盖未分类日期、所有来源角色或总体成稿质量。

## 关键 SHA-256

| 对象 | SHA-256 |
| --- | --- |
| 最终 candidate core | `969235f48c8a7f8592b84742257b08315e823326c76d4198e7e12b7cc5eb32ea` |
| 最终 candidate 日期模块 | `5f28a20b0b32cda9f4610fbbabfbb7592819272662abba852d8c3f96b85aae3a` |
| baseline core 原始 Git bytes | `049d153a66edf5ce0f3a24fb07aa25153778fad89bdebdd19584c32e202c0b62` |
| baseline 日期模块原始 Git bytes | `d1e5b9da5607bfa7b3e27be8642e77e34a352617c52cf8d41fba8c19e0fbd015` |
| run-final 原始结果 | `93d2b8832470f707b0c8a57724cedfc6cc974a366a938fae23f3d2769f40c5fe` |
| run-native-natural 原始结果 | `2a2a0c8e9d5390feffff0005d327c82cb2b9c4641a51db48603ca72f6122eba0` |
| 自然 D0 / candidate 可见稿 | `d0928563b721c2adf6d2e0246591553e8a06df03c48cccb4ecbd486933059e6a` |
| 自然 D0 的 baseline 错年可见稿 | `9bd1df2ddf9de0ce969f93702e383850cd43ad5bc48bda0a330214084b3c9d73` |
