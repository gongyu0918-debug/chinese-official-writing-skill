# Hook 离线反例归档：三项历史结果与一项新补证

固定基线：`5fbb2d26c49d0b780ad11fc4cff008854995ad3f`。本目录保存四个受控离线反例的输入、脚本、输出和来源。前三项来自原有两个脚本及其结果，本次只复制、未重跑；第四项是本次单独编写并运行一次的归档补证。没有模型调用、联网、产品修改或宿主安装。

这些反例证明特定合成输入和事件顺序下的 core 行为，不能换算为真实成稿错误率、宿主事件发生率或长期稳定性百分比。旧脚本含手写 D0、模拟工具事件；并发项还主动控制线程写入顺序。日期反例的真实模型另测结论是 [NOT_REPRODUCED](../date-source-real-r1/result.md)，不能用本目录的手写 D0 替代。

## 保存的观察

| 项目 | 原始输入与结果 | 观察及边界 |
| --- | --- | --- |
| 历史 1：日期来源错绑 | [脚本](date_role_repro.py)、[结果](date_role_result.json) | 合成材料的事实日期为 ISO `2026-09-05`，中文 `2020年9月5日` 明确只是非事实格式示例。手写 D0 的 `9月5日` 被补成 2020 年，仍以 `TERMINAL_D0` / `D0` 保存。这里只证明该输入的确定性改写。 |
| 历史 2：最终回显耗尽 | [脚本](state_echo_race_repro.py)、[JSONL 第 1 项](state_echo_race_result.jsonl) | 手工连续给错误最终回显，第 4 次返回 `continue: true`，状态为 `failed_bounded`、`delivery_verified: false`。说明 core 放行边界，未证明原生宿主一定把该回显交付给用户。 |
| 历史 3：迟到写入覆盖终态 | [脚本](state_echo_race_repro.py)、[JSONL 第 2 项](state_echo_race_result.jsonl) | 主动暂停一次 `PostToolUse` 原子写，再完成终态清理，最后释放迟到写入。后续 Stop 后请求和稿件原文仍在、txn 目录已不存在、脱敏状态为空。证明控制顺序下的竞争窗口，未测自然并发频率。 |
| 新补证 4：同 turn 请求重放 | [新脚本](terminal_replay_repro.py)、[完整结果](terminal_replay_result.json)、[运行回执](new-run-receipt.json) | 合成的关闭 Hook 请求，依次提交 `UserPromptSubmit → Stop → 同 turn UserPromptSubmit → Stop`。四次均用未修改基线 core 的独立子进程。本次运行 1 次，退出 0，结果为 `REPRODUCED_OFFLINE`。 |

第四项每一步均返回 `continue: true`、子进程退出 0：

| 步骤 | request 字段存在 | data_retention_state |
| --- | --- | --- |
| 第一次 UserPromptSubmit | 是 | 空 |
| 第一次 Stop | 否 | `raw_turn_data_redacted` |
| 同 turn UserPromptSubmit 重放 | 是 | `raw_turn_data_redacted` |
| 最后一次 Stop | 是 | `raw_turn_data_redacted` |

第一次 Stop 已清理原文；重放恢复了请求，但保留旧脱敏标记，末次 Stop 没有再次清理。此项没有模拟原子写、手改状态或 core 补丁。用合成关闭 Hook 请求是为了直接观察普通放行终态的清理边界。

## 来源与字节完整性

前三项的四个原文件来自本机 `%LOCALAPPDATA%/Temp/cow-hooks-audit-20260905/`，文件名与本目录相同。原文件尚在，本次逐字节复制并比对 SHA-256；没有脱敏、改写或重新执行。此前主审计代理报告已独立运行旧反例；现存旧结果不含独立 shell 退出回执，因此本目录不追补旧运行的退出码或执行次数。

原文件保留了混合 LF、CRLF 和 CRCRLF，包括异常行尾。局部 [.gitattributes](.gitattributes) 对四个旧文件设置 `-text -diff`，使 Git 保留原字节，并避免把历史 CR 当成本次新增空白错误；查看完整内容仍可直接打开文件。新脚本和新结果保留 LF，可正常审查文本 diff。

新补证使用全新系统临时目录，目录基名见 [运行回执](new-run-receipt.json)，完整输出留在其 `run/result.json`，stdout/stderr 留在同目录。提交的新结果与该结果原字节一致。事件的 `cwd` 来自命令提供的基线树；公开 JSON 省略机器绝对路径，记录其来源及实际完整输入的 SHA-256，未把删去 cwd 的展示对象冒充完整原始输入。这个公开结果的格式由新脚本预先定义，不是对旧结果的事后脱敏副本。

[来源清单](source-manifest.json) 记录旧源文件与新文件的 SHA-256、字节数、换行计数和来源类别。归档检查未发现密钥、令牌、真实业务隐私、私有网络地址或硬编码机器绝对路径。材料全部为合成文字。新运行同时记录基线 core 文件 SHA-256：`bb3533d46c99411c4f56c51b437314065696c34e9bdce7d70b42630b3e50cd08`。

## 重执行方式与本次检查

下列命令是未来复核说明；本次归档没有执行前两条。请将占位符替换为实际路径，并使用固定、干净的基线树。

```text
python -B <ARCHIVE>/date_role_repro.py <BASELINE_TREE>
python -B <ARCHIVE>/state_echo_race_repro.py <BASELINE_TREE>
python -B <ARCHIVE>/terminal_replay_repro.py --core-root <BASELINE_TREE> --output <NEW_TEMP_OUTPUT>
```

第三条本次确实运行一次。新脚本拒绝非固定 HEAD、脏基线树和已有输出目录。复跑必须另选不存在的输出目录；不会覆盖本次已保存结果。旧脚本自行创建临时数据目录。

归档验证仅覆盖 Python AST、JSON/JSONL 解析、本文直接链接、源文件与 Git 暂存字节/hash、敏感信息检查、基线产品 diff 及 `git diff --check`；没有重跑旧反例、全量测试或原生宿主。这是审计证据归档，没有候选产品准入或问题已修复的结论。
