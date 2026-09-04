# R4：叶页 stdin/help 提示的受限接口真实结果

读取量口径补充：本报告原有字节表是MCP服务端返回的文档原文字节。R6归档时只读核对完整trace发现，Claude把源码响应持久化并只传回约3.3KB预览；这些请求不能称为58KB源码完整进入上下文。下文“源码请求”仅计请求整份文件的动作，宿主可见响应量另列；原始fixture、raw和SHA未改。[12稿读取面复核](../reading-surface-audit.json)

结论：本轮四份稿的正文未观察到事实、日期、数量、未决状态、通知结构或正文交付硬错；**没有复现两路线的源码减载收益，也没有稳定的终稿复扫改善**。候选仍为未准入原型，不能以正文通过代替目标收益。后续位置修正须另立原子，不追加本候选样本碰运气。

这是两臂同工具、同原始用户 prompt、同 D0 的受限 MCP 接口实验，不是原生 Shell 命令 A/B。R3原生命令结果仅作背景，未进入本轮分母。模型仅可读取冻结 ID 和调用固定 lint；无临时文件写入能力，因此不能从“没有临时写入失败”推导普通宿主收益。

## 冻结与实际调用

- Harness/实验产品：`9e9f55753f95091b2f8d5093e18654c5b8c32dfb`；控制产品：`5cb696fe`。实验仅在 `references/final-review-layers.md` 增加同一句 stdin/help 说明，Git LF 9029 → 9129 bytes，其他产品文件相同。
- [fixture](real-ab/fixture.json) SHA-256：`0188bfcba09430625f6b444e4d60b29e99d88f3ccfa951a932e79b41a8f2c5d8`；两臂 [manifest](real-ab/manifests/control.json) / [manifest](real-ab/manifests/experiment.json) 固定产品、D0、解释器和脚本。
- 同一 Claude Code 2.1.195，通过既有 Alibaba2 DeepSeek 与 MiniMax M3 路线，均 max，独立新会话。执行顺序为 Alibaba2控制、MiniMax实验、Alibaba2实验、MiniMax控制，没有重试。四份 init/assistant/modelUsage 均为各自登记的精确模型名。
- 两臂各19项真实 stdio contract PASS，模型调用0；工具清单恰为 `read_document` / `prose_lint`，每臂仅3次固定 `python -I -B -X utf8 <frozen script>` 执行且 `shell=False`。任意路径、URL、注册表 ID、未知工具、Shell参数片段和越界参数均拒绝。[完整反控](real-ab/contract.json)
- 四份实际 CLI init 均先于模型事件出现，工具精确为 `mcp__audit__read_document` / `mcp__audit__prose_lint`，MCP connected，skills/plugins 均空；技术违规均为 `[]`。无 Bash、Read、Web、Agent 或额外工具。

实际顶层命令共四次，仅替换 provider/arm：

```text
python maintenance/tests/evidence/lint-command-route-r1/restricted-r4/run_restricted.py --output-root output/lint-command-route-r1/restricted-r4-r2 --provider alibaba2 --arm control
python maintenance/tests/evidence/lint-command-route-r1/restricted-r4/run_restricted.py --output-root output/lint-command-route-r1/restricted-r4-r2 --provider minimax --arm experiment
python maintenance/tests/evidence/lint-command-route-r1/restricted-r4/run_restricted.py --output-root output/lint-command-route-r1/restricted-r4-r2 --provider alibaba2 --arm experiment
python maintenance/tests/evidence/lint-command-route-r1/restricted-r4/run_restricted.py --output-root output/lint-command-route-r1/restricted-r4-r2 --provider minimax --arm control
```

每份 `invocation.json` 保存实际 Claude argv、原始用户 prompt、cwd 和模型绑定；`tool-calls.jsonl` 保存每个工具输入、固定程序 argv、stdout/stderr 和状态；`stream.jsonl` 保存完整宿主输出。未复制 runtime 配置或真实凭据。

## 结果分列

| 路线/臂 | 服务端文档bytes | 可见响应bytes | 源码请求 | lint拒绝 | 成功help | 对最终正文有效复扫 | 秒 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Alibaba2控制 | 106862 | 52275 | 1 | 1 | 0 | 0 | 50.594 |
| Alibaba2实验 | 108834 | 54276 | 1 | 0 | 1 | 1 | 33.500 |
| MiniMax控制 | 86295 | 31476 | 1 | 2 | 0 | 1 | 23.875 |
| MiniMax实验 | 86295 | 31482 | 1 | 2 | 0 | 0 | 23.125 |

字节为成功 `read_document` 的UTF-8原文，含D0与脚本；本轮各样本均无重复读取，去重值相同。每份源码读取均为完整58290 bytes。有效复扫要求 stdin 与最终正文仅允许首尾空白不同，且实际成功执行同时带 `--format --structure` 的扫描；单纯exit0或扫原稿不计。

Alibaba2实验在源码前读到了新增句，少一次漏 `-` 拒绝并做了终稿复扫；但它仍请求整份源码，总读取反增1972 bytes（其中100 bytes为产品新增句，其余来自不同reference选择），只能记录单样本工具步骤改善。MiniMax两臂均未读final-review，实验文字没有曝光；控制的终稿复扫还多于实验，不能归因为新增句的稳定收益。

MiniMax实验曾以 `['-']` 扫含加粗原稿并得到 `No prose risks found.`，随后加format/structure才命中Markdown噪点；另一次 `--help` 带了正文，被封闭接口拒绝。这证明“扫描返回0”与“按目标规则完成有效检查”必须区分。封闭工具确实阻止了无效调用，不能据此宣称模型主动选对了命令。

四份正文均去掉标题Markdown加粗，保留源稿全部实质事实和未决状态。Alibaba2两臂、MiniMax实验只做这一变更，正文相同（260个非空白字符）；MiniMax控制另删重复的“请按上述范围报送信息。”，249个非空白字符，无事实删失。用户无硬篇幅上限，不能用较短篇幅判胜。[逐份量化与作者人工复核](real-ab/metrics.json)

| 完整正文 | 实际命令 | 完整模型trace | 工具原文 |
| --- | --- | --- | --- |
| [Alibaba2控制](real-ab/raw/alibaba2/control/final.txt) | [argv](real-ab/raw/alibaba2/control/invocation.json) | [trace](real-ab/raw/alibaba2/control/stream.jsonl) | [calls](real-ab/raw/alibaba2/control/tool-calls.jsonl) |
| [Alibaba2实验](real-ab/raw/alibaba2/experiment/final.txt) | [argv](real-ab/raw/alibaba2/experiment/invocation.json) | [trace](real-ab/raw/alibaba2/experiment/stream.jsonl) | [calls](real-ab/raw/alibaba2/experiment/tool-calls.jsonl) |
| [MiniMax控制](real-ab/raw/minimax/control/final.txt) | [argv](real-ab/raw/minimax/control/invocation.json) | [trace](real-ab/raw/minimax/control/stream.jsonl) | [calls](real-ab/raw/minimax/control/tool-calls.jsonl) |
| [MiniMax实验](real-ab/raw/minimax/experiment/final.txt) | [argv](real-ab/raw/minimax/experiment/invocation.json) | [trace](real-ab/raw/minimax/experiment/stream.jsonl) | [calls](real-ab/raw/minimax/experiment/tool-calls.jsonl) |

各receipt保留CLI usage和模型usage，宿主费用估计依次为$0.207927、$0.142737、$0.1780545、$0.1663425，合计$0.695061；这些不是供应商账单或低价路线实付证明。输入读取字节也不等于模型token节省。

## 边界与保留项

- 首次无模型UTF-8失败未删改，见[原fixture](contract-attempt-01/fixture.json)及[工具原文](contract-attempt-01/contract/control-calls.jsonl)。修复只为固定解释器增加 `-X utf8`；模型阶段没有重跑或无效样本替换。
- 初始原型 `d1db8952` 是事后工具清单检查；本轮模型全部使用 `9e9f5575` 的逐行显式init mismatch即时停止版本。窄审随后指出缺失init而先来assistant/result还需即时停止，本轮四份均有合规先行init，未触发该缺口；后续原子冻结前用无模型反控补齐。
- [SHA256清单](real-ab/SHA256.json) 覆盖38个证据文件；raw与contract通过局部gitattributes按原字节存储。四份同题合成通知不估计普遍无错率，也不代表4—7版真实修改稳定性。
- 没有镜像、合并、推送、tag或发布；绝对路径文档正确性与本次stdin/help减载判断仍是两个原子。
