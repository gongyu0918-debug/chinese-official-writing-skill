# R11 篇幅处理单句补测

本记录在 8 次调用完成后整理，不冒充预注册。试验来源与变化已在运行前冻结的 `output/common-layer-refine-r11/build.json`、`changes.diff` 中记录。

R10 的 Qwen 润色稿删去有效原句后仅 74 字。字数脚本实际检出不足，Agent 仍转而向用户索要新事实。因此尝试把共性页的一句篇幅处理改为：对照材料和原稿恢复误删的有效内容，或以有据分析补足表达，调整后复测；确实没有可用信息再提示。没有改计数脚本、返回码或新增路由。

基线为原 R10，候选仅改上述一句。原生 Codex CLI 同题双臂：Qwen 通道 0（medium）与 DeepSeek 通道 2（provider-default），题目为 guards_grammar_quote、grammar_correct_control，共 4 对、8 次，全部完成有效输出。

```text
python -B maintenance/tests/evidence/mit-script-delivery-r1/run_eval.py --output output/common-layer-native-r11-length --baseline-dir output/common-layer-experiment-r10/candidate --candidate-dir output/common-layer-refine-r11/skill --models 0 2 --cases guards_grammar_quote grammar_correct_control --effort medium --timeout 240 --isolated-profile
```

初读：两臂均保留有效内容、改对量词；对本就正确的给定工作记录均保留原文。这说明 R10 单次 74 字与量词问题均未在本轮原规则重复中复现；不能将 R11 的正确稿件直接当作修复因果证据。校对给定片段与重新起草独立完整稿区分，避免硬扩已经正确的原文。

独立审阅只读取匿名完整消息，见 `output/common-layer-blind-r11/packet.json`，SHA-256 `990d72e7b39c92751679793b266e4c146edc1621933ab282b9bd3e884627ae16`。原消息中的临时路径做匿名替换，正文未整理或代改。候选没有进入 canonical 或后续 R12，以保留单一归因。
