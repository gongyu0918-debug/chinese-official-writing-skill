# Candidate A 三稿盲审取证

日期：2026-07-15

本目录先提交四份匿名裁判原文，来源映射在本提交中继续封存。裁判只收到已提交的匿名 A/B/C 稿件包，不收到来源标签。

| 稿件包 | SHA-256 | 裁判模型 | thinking | thread ID | 原文 |
|---|---|---|---|---|---|
| `blind-packet-luna.md` | `CC2CAE543315ED68F694E75D87CFAE2D836DC10E5FE9589EE63D65EB9CBC12F9` | `gpt-5.6-terra` | high | `019f64f5-7c1e-7082-b3ce-9f55a6d816d0` | `judge-terra-on-luna.md` |
| `blind-packet-luna.md` | `CC2CAE543315ED68F694E75D87CFAE2D836DC10E5FE9589EE63D65EB9CBC12F9` | `gpt-5.6-sol` | high | `019f64f5-9694-73b1-967f-83d0c801246d` | `judge-sol-on-luna.md` |
| `blind-packet-terra.md` | `4775776F8CFEBDF8D9E13F9E7FA4F18C04C4E3BC188E10BE591F2FFD2C45214E` | `gpt-5.6-luna` | high | `019f64f5-aff8-7b23-b525-714073488d07` | `judge-luna-on-terra.md` |
| `blind-packet-terra.md` | `4775776F8CFEBDF8D9E13F9E7FA4F18C04C4E3BC188E10BE591F2FFD2C45214E` | `gpt-5.6-sol` | high | `019f64f5-c7b6-77a2-a60a-a3ce9fd37c1f` | `judge-sol-on-terra.md` |

## 输入与隔离核验

- 四个 session 的 `turn_context` 均核验到上表模型和 high thinking。
- 四个 session 的委派 `<input>` 与对应匿名包逐字符一致：Luna 包长度 17536，Terra 包长度 16785，四组均为 `INPUT_EXACT=True`。
- 创建裁判线程前，`C:\Users\admin\.codex\skills\chinese-official-writing` 与项目 `.agents\skills\chinese-official-writing` 均临时移出可发现路径。
- 全局备份 `SKILL.md` 哈希为 `44BDCF85399E0FEBA87A90A82611B9F336A4580075F91919E0DDE7063DEF6E83`；项目候选备份哈希为 `B5AE6B40ECC1298D4357E919DD2EBDFC6ADC80F75BA924FA1BE6F0F76295D7AF`。
- 四份裁判完成后，两处入口已恢复，恢复哈希与上述记录逐项一致。
- session 中出现的产品名仅来自共同的 memory summary 描述，不是可用 Skill 项，也没有向裁判提供版本、来源映射或候选结论。

## 裁判口径

篇幅只用于判断用户明示范围是否遵循；范围内的长短不构成质量票。裁判先检查事实、未决状态、文种、格式、Prompt 和输出模式，再比较信息利用、段落推进、主体宾语、结论强度、可读性、自然度、机械感和直接采用成本。

本文件不作来源解盲，也不汇总候选胜负。

