本原子只修复 `delivery_cleanliness` 对完整单个 JSON 围栏的误拒。基线为 `b77f6381438c8fa01f8576c205d13af4b8a987fd`；原请求和完整 D0 见 [fixture.json](fixture.json)，汇总与逐调用绑定见 [result.json](result.json)。未安装或启用 Hook，未运行宿主事件；每次修稿、核验、回显均由一个独立的真实 Claude CLI 会话完成。

| 真实链 | 结果 | 完整回复非空白字符数 |
| --- | --- | --- |
| P6，Alibaba2，基线 3 次调用 | 清理、核验、回显成功；正文逐字保全 | 755 → 589 |
| M6，MiniMax，基线 4 次调用 | 真实核验包为完整 `json` 围栏，解析失败，选回带附注 D0；第一次回显不一致，有限再提示后原稿回显成功 | 579 → 579 |
| M6，同两份真实修稿/核验回应，候选新回显 1 次 | 前两次提示逐字相同，可迁移；候选选 D1，新的真实回显成功 | 579 → 447 |
| M6，候选独立完整链 3 次调用 | 新核验包也是完整 `json` 围栏；核验与回显成功，正文逐字保全 | 579 → 447 |
| C4 干净稿、C5 明确要求 Markdown、C6 明确保留说明 | 基线分别 2、2、3 次调用，均保留完整 D0；C6 有一次有限回显再提示 | 不变 |

共 **18 次真实调用，18 个独立会话**：Alibaba2 DeepSeek 7 次、MiniMax 11 次。18 次的 init、assistant、usage 模型绑定有效，工具、Skills、插件、MCP 清单均为空，工具调用 0，模型重试 0。运行时约定的有限回显再提示有完整记录，不算技术失败后的模型重试。CLI 报告费用合计约 USD 0.965379，仅为 CLI 计费估算；`usage` 与 `modelUsage` 两种口径分别保留，不能当作账单。

候选只在解析 JSON 前识别占据整个回应的普通或 `json` 围栏；旁白、多对象、非对象及其他代码语言仍拒绝。删除项、请求/D0/D1 哈希、四项语义核验、正文保全、回显及失败回退规则均未改。候选源码和本轮 canonical 源码原始字节一致，SHA-256 为 `9b2988d00ba341a708a04f661f3fae1afd6a5e1510e1a017304ea10da783824c`。

P6、M6 来源是此前**未启用 Hook**的自然第五版完整回复，不能据此统计 Hook 失败率。C4/C5 是旧冻结反控，C6 是对真实 P6 D0 明确保留说明的请求变体，不能称为原始自然配对。成功终稿与原正文逐字相同，因此不会新增正文事实或状态，也没有修正原正文已有问题。三个反控和 P6 在候选解析器上复放原真实回应时，每次提示、选择与结果仍相同；这是协议未变的旧真实证据迁移，没有另调候选控制模型。

[归档来源清单](https://github.com/gongyu0918-debug/chinese-official-writing-skill/blob/0721297298b72be7a37b93c6598172791b58e421/maintenance/tests/evidence/hook-quality-build-r1/cleanliness/archive-provenance.json)记录原始文件 SHA 与完整 stream SHA。这里保存原字节 prompt/reply/receipt、事件、结果，以及实际 init/result 的字段摘录；`output/hook-quality-build-r1/cleanliness` 保留全部原始 stream、失败和隔离运行目录。归档不含 HOME、登录目录或完整 thinking stream。局部 `.gitattributes` 禁止换行转换，保证冻结哈希可长期复查。

离线复放命令：

```powershell
python -B -X utf8 maintenance/tests/evidence/hook-quality-build-r1/cleanliness/replay_saved.py
```

[已运行结果](https://github.com/gongyu0918-debug/chinese-official-writing-skill/blob/0721297298b72be7a37b93c6598172791b58e421/maintenance/tests/evidence/hook-quality-build-r1/cleanliness/offline-replay.json)的 11 项均重现记录行为，包括基线 M6 的功能失败；所有已用真实回应先核对对应提示逐字相同，再投给运行时。它不会调用模型、改文件或安装 Hook。[原始 R1 驱动](https://github.com/gongyu0918-debug/chinese-official-writing-skill/blob/0721297298b72be7a37b93c6598172791b58e421/maintenance/tests/evidence/hook-quality-build-r1/cleanliness/source/run_cleanliness.py)和 [R2 驱动](https://github.com/gongyu0918-debug/chinese-official-writing-skill/blob/0721297298b72be7a37b93c6598172791b58e421/maintenance/tests/evidence/hook-quality-build-r1/cleanliness/source/run_candidate_r2.py)按原字节归档，原执行位置是 `output/hook-quality-build-r1/cleanliness`；其目录相对约定不适合直接从 `source/` 发起模型调用。

实际验证：`python -B -X utf8 -m unittest maintenance.tests.test_delivery_cleanliness_capability`，9 项通过，2.275 秒；[quick validate](https://github.com/gongyu0918-debug/chinese-official-writing-skill/blob/0721297298b72be7a37b93c6598172791b58e421/maintenance/tests/evidence/hook-quality-build-r1/cleanliness/quick-validate.json) 返回 `Skill is valid!`。JSON、AST、直链与 diff 检查见 [validation.json](https://github.com/gongyu0918-debug/chinese-official-writing-skill/blob/0721297298b72be7a37b93c6598172791b58e421/maintenance/tests/evidence/hook-quality-build-r1/cleanliness/validation.json)。未跑全量，未提交、合并或发布；由主代理统一提交。

默认 `delivery_review` 接入仍由主代理负责。本原子建议仅在请求明确只交正文、完整 D0 首尾有明显前导语或附注时进入清理；明确保留说明、要求 Markdown/JSON，以及干净正文应旁路。不要因正文内部出现“说明”“字数”就触发，更不能先机械切掉正文。可复用现有 `start(event, record)`、`advance(event, record)`、删除项契约与回显 SHA，无须新建协调器。默认入口仍需独立 core 复放验证，也不能因选择清理阶段而无意省略已有事实/状态检查。

给 core 复放的实际输入：从 `fixture.json` 按 `id` 读取 `request`、`d0`；P6 用 `r1/P6/calls/1..3/{prompt,reply}.txt`，M6 用 `r2-full/M6/calls/1..3/{prompt,reply}.txt`。每次必须先断言 core 返回的 `reason` 与对应 `prompt.txt` 逐字相同；提示变化时不得把旧真实回应冒充新提示下的响应。C4/C5/C6 旁路反控应直接核对 D0 哈希，没有必要追加模型调用。
