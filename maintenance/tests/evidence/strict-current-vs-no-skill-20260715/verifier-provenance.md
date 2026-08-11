# 严格同模型匿名盲审来源记录

匿名包在 commit `86b0f9e` 中先行冻结；该提交没有 condition mapping。4 个 judge 使用 projectless 独立上下文，只接收对应匿名包文本，不读取仓库、原始条件文件、其他 judge 结果或映射。

创建 judge 前，临时隐藏全局和项目两个 `chinese-official-writing` 可发现入口。4 个 judge 的 rollout 技能清单均未列出该 Skill，相关工具调用计数均为 0；`turn_context` 记录的 model 与 high effort 和预设一致。3 个 judge 在 10 分钟观察窗内完成；Terra writer / Sol judge 在观察窗结束时仍运行，按未完成暂记，随后自然完成。两个入口已恢复并核对：全局 1.2.18 SHA-256 为 `44BDCF85399E0FEBA87A90A82611B9F336A4580075F91919E0DDE7063DEF6E83`，项目 1.5.14 SHA-256 为 `85545D10FB503E3DA013B0292BB0310596A279F9FA99A81124528631C2A0811F`。

| writer 匿名包 | judge model | thinking | thread | 输入匹配 | 状态 |
| --- | --- | --- | --- | --- | --- |
| LUNA | `gpt-5.6-terra` | high | `019f64c2-96ac-7e30-8603-4d4684c656ae` | 是 | completed |
| LUNA | `gpt-5.6-sol` | high | `019f64c2-b358-7712-b5cc-93decd7fad80` | 是 | completed |
| TERRA | `gpt-5.6-luna` | high | `019f64c2-c57a-7532-9dc4-2a8d96999e9c` | 是 | completed |
| TERRA | `gpt-5.6-sol` | high | `019f64c2-e17d-7da3-b1f5-fd2af571d63d` | 是 | completed |

judge 可以自行拆分审读任务；这属于评测过程，不计入 Skill 本体能力。公开结论只采用最终盲审原文，经下一提交揭盲后映射。落盘时只移除了 8 处 Markdown 行尾双空格，文字、标点和判断未改。
