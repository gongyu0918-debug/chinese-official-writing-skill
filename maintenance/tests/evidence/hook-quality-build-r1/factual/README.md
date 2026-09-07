# 事实来源修正原子：HOLD

基线 `b77f6381438c8fa01f8576c205d13af4b8a987fd`，只产生 prompt/固定输入实验和证据，未修改产品。模型均为 Alibaba2 `alibaba-token-plan-2/deepseek-v4-flash-0731`。累计 7 次独立真实 CLI 调用，6 次技术有效；1 次 P6 基线 180.047 秒超时，失败保留且未重试。

M5 的有效同稿对照显示局部纠错收益；P6 候选也相对真实 D0 修正主办方和已审核程序，但基线超时使其无法形成有效提示 A/B。合理承接保留未全通过，P6 仍有无据参会范围，不能称完整事实核验。

**原合同最终纠错交付数为 0，6 份有效回复全部选回 D0。** R3 排除外围包装影响后，真实模型只删除两处无据“信息部”，其他字符逐字保留；机械锚全部通过，但四项数字上下文关系包使 `single_pass` 按设计回退。当前合同没有独立关系 verifier，本原子 HOLD，不直接放宽锚，不增加裁判流水。

[archive-summary.json](archive-summary.json) 是含 R3 的最终累计索引；[result.json](result.json) 保留 R1/R2 的 6 次历史范围，未覆盖重写。[initial-review.json](initial-review.json)、[candidate-r2/review.json](candidate-r2/review.json)、[candidate-r3/review.json](candidate-r3/review.json) 保留逐稿引文、真实选稿结果及边界。

归档保留实际 prompt/reply/receipt、调用参数、模型提案与解析最终选择、init/result 和 assistant模型/正文摘录、全流 SHA256、冻结合同和提示差分。完整 stream 留在 output 源路径，未把摘录冒充全流；runtime、HOME和配置未纳入。原驱动只作来源追溯，其 HERE 布局绑定原 output 路径，不声称可直接从本归档目录复跑。实际命令及验证在各轮 JSON；未执行原生 Hook 或产品全量测试。
