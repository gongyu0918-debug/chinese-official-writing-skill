# 自然字数上限原型 R2：技术中断，未准入

R1 保持 [HOLD](length-result.md)。R2 只给自然压缩表达增加问句排除，保留原有解析与 10% 容差；原型也已撤回，没有准入解析或新增产品胶水。

本轮是明示新任务：从清洁流程已验证的 M6 D1 读取 447 字正文，SHA-256 `761c588587bbf7831d5072059a813f07460ef2bb843f31f1471db0fcf23eacc4`，原字节作为 D0。新请求为“请把这份纪要压到400字以内，保留全部事实、责任、期限和未决状态，只输出完整正文。”，SHA-256 `ff27d67ab1d14f06debcb2c2ad0dc964aae4ae4dcb215a67f76deac4a6606c54`。来源清洁链选择 D1、精确回显且 `delivery_verified:true`；本次不代表原 M6 的 500 字任务。

基线不识别新请求，不触发、不新增模型调用。R2 解析 400，447>440，触发现有 `over_length`。三个“是否需要／是否应／检查…是否合适”问句在两处解析均被排除。共享 contract/anchors 固定为 R1 基线，以避开并行修改。

唯一 MiniMax M3 max 链尝试两次调用，0 retry：观察步骤在 15.187 秒返回有效 CLEAR；压缩步骤在 300.094 秒 `TimeoutExpired`。后者 `result_count=0`、reply 文件为空，没有可用候选，没有语义核验、选择或交付。两次 init 工具、MCP、Skills、plugins 清单均为空；超时调用没有 usage/result，完整绑定与成本无法确认。该结果属于技术中断，不据此判定正文质量变好或变差，已停止调用。

原始 runner 异常后把上一次内部 CLEAR JSON 写入了旧命名 `final-visible.txt`。其中 304 字符是内部协议 JSON，**不是交付正文**；原文件保留，由[更正记录](length/r2/result-clarification.json)明确其不可用状态。不能把 runner 已完成写文件或 parse 通过说成质量收益。

实际命令：

```text
python -B output/hook-quality-build-r1/length/r2/run_r2.py --prepare
python -B output/hook-quality-build-r1/length/r2/run_r2.py
```

prepare exit 0；真实 runner 非零退出，工具记录 exit 1。未重跑同题，未补永久产品 tests。fixture SHA-256 `d378079d6e9aabc84278e38c92fe9a0d29e3f34dc9effef0ad7488bd93151755`。完整 prompt、空 reply、receipt、stream、冻结产品及 diff 见[归档清单](length/manifest.json)；不包含私有 runtime/HOME。
