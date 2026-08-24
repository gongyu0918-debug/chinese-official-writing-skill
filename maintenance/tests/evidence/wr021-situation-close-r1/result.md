# WR-021-SITUATION-CLOSE-R1 情况说明未决收束结果

日期：2026-08-25。

## 结论

`TERMINATED_BASELINE_NOT_REPRODUCED / WAIT_NEW_COUNTEREXAMPLE`。

全新馆藏数字资源异常题的三条 Baseline 均技术有效，Ollama、OpenCode 两稿都自然止于当前未决状态；只有 Alibaba 新增“待核验和排查结果明确后，将另行说明”。实际复现率为1/3，未达到预登记的至少2/3，因此不启动 Candidate，不修改轻量情况说明卡，不增加“说明/通报/反馈”枚举禁令。

这项结果修正了上一轮的风险强度：材料外披露承诺确实存在，Alibaba 已在两份不同情况说明中连续出现；但它没有在第二题跨 provider 稳定复现，当前通用规则对 Ollama、OpenCode 已能形成完整且自然的正文。只有出现新的跨 provider 反例，或 Alibaba 在更多不同文种/素材上持续复现，才重新开启新原子。

## 逐稿裁定

| provider | 字符（去空白） | 事实与状态 | 后续承诺 | 裁定 |
| --- | ---: | --- | --- | --- |
| Ollama DeepSeek V4 Flash 0731 | 217 | 17/12/5、时间、日志截图、文件转换服务及原因/内容影响/责任未决状态完整 | 无 | `PASS` |
| Alibaba Token Plan 2 DeepSeek V4 Flash 0731 | 253 | 核心事实与状态完整 | “待核验和排查结果明确后，将另行说明” | `HARD_FAIL_MATERIAL_EXTERNAL_COMMITMENT` |
| OpenCode Go DeepSeek V4 Flash | 210 | 核心事实与状态完整 | 无 | `PASS` |

自动检查把三稿的“相关文件内容是否受到影响正在核验”误报为漏项，因为预登记短语只列了“是否受影响”，没有覆盖“是否受到影响”。人工逐字核对确认三稿都保留了该状态；这个 verifier 分歧不改变后续承诺的1/3结果，也不在事后改动预登记词表制造通过。

Ollama、OpenCode 两稿均短于完整提示词但长于材料，事实完整、文种成立、正文可直接使用；不以短于提示词判失败，也不增加统一篇幅门。

## 证据与命令

- Baseline：`main@0ded0ddf94a8425dc6083d13b5b278c6a8e91363`，71 文件，fingerprint `39542c6037d84c72668636267ebdc8e0928aadd4e9fe0523749e53464f955d6b`。
- 运行：`python -B maintenance/tests/evidence/wr021-situation-close-r1/run_eval.py --prepare-arm baseline`，随后三次 `--provider <ollama|alibaba2|opencode> --arm baseline`，最后 `--summarize`。
- 忽略目录原始汇总：`output/wr021-situation-close-r1/summary.json`，SHA-256 `b093e09c97cb392db74759d354f02b13c246c857cda6bb367df1d21f7fe1ddfe`。

本原子没有产品、Hook、description、镜像、版本或平台改动；没有 push、tag、Release 或平台写入。
