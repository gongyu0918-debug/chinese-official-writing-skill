# 超长收束、短稿局部去重与 README 示例结果

结论：**候选通过目标功能验证与独立冷审修复复核，已进入 v1.6.8 发布候选。**

## 真实写稿先行

先用 `ollama-cloud/deepseek-v4-flash:0731` 和 `alibaba-token-plan-2/deepseek-v4-flash-0731`（均为 max）运行短稿、超长压缩和制度示例。R1 共5次调用，均技术有效：

| 样本 | 非空白字符 | 结果 |
| --- | ---: | --- |
| O01 工作情况报告 | 238 | 达到420字上限，但开头和结尾重复责任表述，不准入 |
| O02 采购请示 | 237 | 数字、用途、资金和请示事项完整，可用 |
| S01 短通知 | 94 | 一个局部一个事项，无同义复述，可用 |
| S02 培训简报 | 74 | 原因和安排各写一次，可用 |
| R01 制度示例 | 874 | 为补足篇幅增加材料外通用条款，不可用 |

R2、R3 继续只修失败项。O01 在273字和206字两版中仍重复责任；制度示例从920字的材料外补充收缩为572字事实安全稿。由此确定：公开层不增加制度禁写词表，README 使用事实安全的校定稿；短稿叶只补充“一处一个事项、同一原因只写一次”；超长能力必须在内部验收中检查跨段职责复述。

## 真实 Hook 生命周期

固定超长 D0 为498个非空白字符，用户上限为420字。前四次探路分别暴露并保留以下事实：

- 模型直接写成201字时，能力未触发，带宽内旁路正确；
- “不得解释；最终正文不超过420字”曾被上限解析器误当成材料解释，已移除该歧义并增加反控；
- 模型未读取 Skill 时 `skill_seen=false`，能力按知情边界不启动；
- “正文不超过420字”下正文恰为462字，等于上限110%，没有越过“超过10%”阈值。

以系统层强制读取唯一 Skill 入口、并将规格明确为“全文不超过420字”后，Claude Code + Alibaba DeepSeek V4 Flash max 完成真实事务：

| 轮次 | D0→D1 | 事务结果 | 质量结果 |
| --- | --- | --- | --- |
| R5 | 498→340 | 一次压缩，D1 选择、终稿回显和哈希闭合 | 结尾仍逐项复述三科室职责，人工判不通过 |
| R6 | 498→285 | 一次压缩，`over_length_complete`，D1 选择、终稿回显和哈希闭合 | 数字、状态、职责与关系完整；结尾只保留12件在办事项的必要承接，通过 |

R6 共记录 `UserPromptSubmit`、`PostToolUse` 和5次 `Stop`；外层重试0，耗时154.469秒。D0 SHA-256 为 `1435a612a92782e0777a513beb2a5175bae8cd7f00d1479ab5e9e6297845d556`，D1/终稿 SHA-256 为 `a268bc338c58c3914f0ed600a97d48c4f18ee8b85b85d485d9eca2f0633a25f0`，运行摘要 SHA-256 为 `3caf83018a64fd7e12eeb6e9c9574af6caee29601034a9a044deb2687ea14777`。

## 独立终审

`gpt-5.6-sol` max 只读核验同一 D0/D1，外层重试0，返回：篇幅、事实、状态、职责关系、结构和非重复均 `PASS`，总判定 `PASS`。裁决 SHA-256 为 `0ce22295b79008ee0b350d316577771d1a875249a90e37ccae122dd2cdadd1fd`。

## 冷审修复与真实稿重放

Grok 4.6 ultra 对高代码量 Hook 与脚本做了两轮独立只读审查。合并前已修复：重复清理达到上限后绕过语义核验、多条字数规格未按文本最后指令取值、runtime 丢失造成 D0 回显循环、终态重复进入、明确状态升级和责任主体变化未被机械门保护，以及同篇“已完成事项 + 拟完善事项”造成的状态误判。否定式“本公司不负责/不承担”不再被错抽成责任主体。

最终机械门重新读取上述真实 R6 的原始事务记录：D0 498字、D1 285字，返回 `mechanical_reason=null`；D1 SHA-256 仍与在线事务选择凭证一致。该重放只验证冷审修复没有误杀已通过的真实稿，不替代原在线生命周期与 SOL max 终审。

## 产品边界

- 超长能力只在明确上限或区间且完整稿超过上限10%以上时启用；先做重复语义观察，再最多两次压缩和一次语义核验。
- 合并前路径复核发现“仅删除重复句即达标”曾直接选择 D1；现已统一改为先进入同一语义核验。
- 合并前生命周期复核还发现事务启动后模块丢失会重复请求 D0；现已改为一次有限恢复，精确回显即完成，否则记录技术失败并停止循环。
- 普通 Skill、短稿、带宽内稿件、只审任务和当前任务关闭 Hook 时不启动该能力。
- 失败、未达标、硬锚变化、语义不明或回显不一致时交付逐字 D0。
- 当前只完成 Claude Code 的真实在线 D1；Codex、CodeBuddy 本轮只验证静态组装，不把文件存在写成在线成功。
- README 历史 evidence 保持原文不变，公开示例已替换为当前事实安全的八条制度正文。

## 最小工程检查

- `python -B -m unittest maintenance.tests.test_over_length_capability maintenance.tests.test_hook_layer_contract -q`
- `python -B -m py_compile chinese-official-writing/hooks/capabilities/over_length/runtime.py chinese-official-writing/hooks/core/gate_stop_hook.py chinese-official-writing/hooks/adapters/host_gate_adapter.py chinese-official-writing/hooks/adapters/claude-code/gate_stop_hook.py maintenance/tools/assemble_hook_companion.py`
- 三宿主 companion 静态组装与 Markdown 本地链接检查
- `git diff --check`

完整工程检查仅在准备合并和发布时运行一次，不以其替代上述真实稿件结果。
