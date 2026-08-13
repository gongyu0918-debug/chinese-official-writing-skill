# v1.6.4 候选真实写稿结果

## 目的与口径

本轮先用真实成稿暴露问题，再做最小规则修正；工程测试不作为写作质量替代品。六题冻结于 `8d66af04`。质量终审只看题面和稿件自身是否解决目标，不以旧版本总体胜负作为新增功能准入门。

## 模型任务

| 题目 | GUI 任务 | 指定模型 | 档位 |
| --- | --- | --- | --- |
| W1—W2 | `019ffb80-ae07-77e0-8349-5f86170d6ac0` | `opencode-go/deepseek-v4-flash` | max |
| W3—W4 | `019ffb78-ebd2-77a0-a106-c6561bea1227` | `ollama-cloud/deepseek-v4-flash:0731` | max |
| W5—W6 | `019ffb80-ed10-7981-9cdf-07a779784a1f` | `alibaba-token-plan/deepseek-v4-flash-0731` | max |
| 独立终审 | `019ffb90-920d-7e92-bce4-bb610d62b027` | `gpt-5.6-sol` | max |
| W5/W6 校准复核 | `019ffb9c-75a1-7c03-b6a8-aa0f62428406` | `gpt-5.6-sol` | max |

任务记录证明上述模型路线是本轮明确指定值；它不是外部 provider 账单回执。误建的 Luna/Qwen 任务不计入正式结果。

## 最终稿哈希与结论

| 稿件 | SHA-256 | 非空白字符 | 事实安全 | 完整要求 |
| --- | --- | ---: | --- | --- |
| W1 | `3A65AB5CA72F8703CAB1B989B6CBA6334FE110789CE27B00140C88A7E03632A9` | 130 | PASS | PASS |
| W2 | `98946212FF202139C4101BFD6DE77A26B92F29167FE6AF9BBB8DCCC762EC0080` | 534 | PASS | 用户口径 PASS；SOL 对下游否定链删除范围有分歧 |
| W3 | `36B2348DD8B8D4491095D2FD9B5FB8A153FB777DFFA26296119D2101BD0772B2` | 94 | PASS | FAIL：低于350字下限 |
| W4 | `0011E9934D9AD5B7F29B39A8A39878EDE2743095F72CF4DD31DAC2A6D167653C` | 107 | PASS | FAIL：低于280字下限 |
| W5 | `4A002163F093DA8E04C2689515567BAD4A8CA5ABAEC03F0E63727EF58CBAE269` | 123 | PASS | FAIL：低于320字下限 |
| W6 | `21C0B679269CF3843B4E9A401B12B34566998AE94A08AF021EB4EE4CC414AD7C` | 231 | PASS | FAIL：低于450字下限 |

## 真实稿驱动的修正

- `cc436889`：Ollama R1 在采购和事故新闻中补造设备影响、群众体验、流程承诺、交通影响、绕行提醒和未来公布；新增“材料稀薄时宁可交事实完整短稿”的边界。R2 的 W3/W4 不再外扩。
- `be881bdd`：OpenCode Go R1 漏判资金自证、采购下游连续否定和无期限承诺；补充审稿规则。R2 能自然识别并给出只审不改意见。
- `b0727071`：Alibaba R1 为活动新闻补造开放、体验、秩序和意义，为总结补造稳定、高效、支撑和结果承诺；R2 不再出现这些内容。
- `6e2b589c`：SOL 指出 W5 单句卡片化；增加稀薄活动新闻的一至两段连贯要求。最终 W5 的结构、事实和自然度复核通过。
- `0b00a3b3`：SOL 首轮把“拟完善、拟优化”归纳为未来改进判得过严；按用户校准，允许自然未来时归纳，只禁止保证性结果和材料外成效。最终 W6 的事实、计划强度、保护性外扩和“综上所述”归纳均通过。

## 未解决问题

- W3—W6 均证明当前普通语义层会优先守住事实边界，但不能在稀薄材料下同时满足高字数下限。篇幅不足 Hook 仍是独立待办，本候选不宣称已解决篇幅。
- W2 的“合同未签、设备未到、验收未实施”下游链，SOL 建议根据文种决定保留或压缩；用户最终口径明确此处应删。原始分歧保留，不以裁判票覆盖产品口径。
- 保护性外扩 Hook 的功能级同稿删除与回退已有独立证据；本组六稿主要验证普通语义层，没有冒充三宿主在线 Hook 生命周期。

## 必要工程检查

- `python -B -m unittest maintenance.tests.test_editorial_delete_contract maintenance.tests.test_protective_expansion_lifecycle maintenance.tests.test_hook_layer_contract maintenance.tests.test_repository_reachability -q`：28/28 PASS。
- canonical Skill quick validate：PASS。
- `protective_expansion` 三宿主静态组装：Codex 45、CodeBuddy 44、Claude Code 44 文件；均为 `enabled=false`、`installed=false`、`network_used=false`。
- 全量维护单测只在准备合并时运行：首次 568/573，5 项均为测试锁定旧新闻/总结全文、旧 OpenClaw 版本措辞或已移出最近五次表格的旧证据名；更新为关键语义合同后，最终 573/573 PASS。修复只改测试，不改产品。
- `python -B maintenance/tools/sync_adapters.py`：完成，普通镜像已同步。
- `git diff --check 851eaa7d..HEAD`：PASS。
