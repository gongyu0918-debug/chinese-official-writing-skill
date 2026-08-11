# 否定约束回声与长稿旁白最小消融

- 日期：2026-07-14
- 固定基线：`c7e2caf9f0604bf4466d28423778a0e1b501c717`
- 范围：本地候选，不升版本、不推送、不发布

## 结论

真实写稿最小 A/B sanity 支持“两处显式否定示例是约束回声的可能放大因素”，据此保留两处最小改写。原规则中的“由于……未提供”示例改为正向交付目标“缺项说明放在正文外”，没有删除事实状态、禁止编造、输出模式、路由、复核顺序或 ANTI-AI 边界。该结果不证明单一根因或严格因果。

“Markdown 规则重复”和“否定式约束”可以在评测层归入同一上位问题：约束回声型旁白。两者是可能共同作用的诱因，现有证据不足以断言只有一个根因。后续仍按具体规则逐项消融，不做整篇 Prompt 的批量去否定。

## 先复现再修改

固定基线下，两名独立 Codex writer 各完成三份未见长稿：

1. 内部知识检索试用情况报告，900—1100字；
2. 政务服务登录页面异常阶段情况报告，1300—1500字；
3. 档案数字化试点阶段评估报告，1800—2200字。

三组材料均给出明确数字、时间线和未决状态，要求只输出可直接使用的报告。基线六份输出反复出现“本报告不作……”“不能据此……”“现阶段只能……”以及面向写作者的操作说明，形成可复现的正文旁白。无 Skill 对照同样存在旁白，提示模型本身也可能有保护性解释倾向。候选只改两处示例后，两个独立 writer 的旁白线索均明显减少，支持这两处示例与旁白增加相关；不同上下文不是同 seed，不能据此证明相对无 Skill 的严格因果放大。

历史证据 `material-narration-version-ab-and-cleaner-rollback-20260710.md` 也显示，较大范围中性化曾把命中率降低约43%，但未消除问题；后来增加硬 cleaner 的方案因真实链路和回滚风险未保留。本轮因此只测试最小 Prompt 改写。

原始样稿：

- `negative-constraint-echo-20260714-writing/prompts.md`
- `negative-constraint-echo-20260714-writing/baseline-writer-a.md`
- `negative-constraint-echo-20260714-writing/baseline-writer-b.md`
- `negative-constraint-echo-20260714-writing/candidate-writer-a.md`
- `negative-constraint-echo-20260714-writing/candidate-writer-b.md`
- `negative-constraint-echo-20260714-writing/no-skill-writer.md`
- `negative-constraint-echo-20260714-writing/verifier-a.md`
- `negative-constraint-echo-20260714-writing/verifier-b.md`

本地 rollout 的 `turn_context.model` 显示五个 writer 和两名 verifier 均为 `gpt-5.6-sol`，具体线程 ID 见 `prompts.md`。它们是独立上下文，但不是同 seed 重复采样，因此仍记为真实写稿 sanity，不登记为统计模型矩阵；未调用 MiniMax。

## 规则映射

复现旁白主要对应三类规则：

| 成稿症状 | 主要来源 | 处理 |
| --- | --- | --- |
| “现有材料未提供……”反复自述材料状态 | `SKILL.md` 事实不足段、`workflow.md` 缺失事实处理 | 对已复现的显式示例做消融 |
| “本报告不作……”“不能据此……”自证边界 | 禁止编造、结论强度和未决状态规则 | 保留；只删除会被照抄的示例 |
| AI 身份、处理过程、交付说明泄露 | 输出模式、最终复核、ANTI-AI 叶子 | 保留，属于已复现的必要硬边界 |

长任务会按需加载 `SKILL.md`、任务卡、文种 playbook、论证链、正式表达、工作流和办理要素，规则曝光量高于轻量路由；重复约束是可能的放大因素。`argument-chains.md` 不含本轮两个“材料未提供”示例，可作为静态对照。ANTI-AI 叶子不是默认起草预读项，也不是历史旁白的起因。

## 社区取证边界

公开社区中可以找到多模型的重复、长上下文漂移、推理循环和格式不遵循报告，例如：

- GLM：`zai-org/GLM-4#599`（重复回答）、`#779`（长上下文注意力漂移）；
- Qwen：`QwenLM/Qwen3#925`（长输出重复）、`QwenLM/Qwen3.6#145`（推理循环）；
- DeepSeek：`deepseek-ai/DeepSeek-V3#1229`（冗长重复）、`DeepSeek-R1#9`（结构输出不遵循）；
- Codex：`openai/codex#27587`（多层指令冲突）；
- Gemini：Google AI Developers Forum 的长对话重复旧回答反馈，以及官方长上下文说明。

这些是社区个案或用户报告，不能当成厂商确认的稳定缺陷，也不能证明某个中文固定词是某一品牌专属口癖。本轮只据此确认“重复、指令回声、长上下文漂移、过程泄露、格式不遵循”值得跨模型观察；没有加入 GLM、Qwen、DeepSeek、Gemini 或 GPT 专属禁词表，也没有为未复现风险预设新规则。

来源：

- <https://github.com/zai-org/GLM-4/issues/599>
- <https://github.com/zai-org/GLM-4/issues/779>
- <https://github.com/QwenLM/Qwen3/issues/925>
- <https://github.com/QwenLM/Qwen3.6/issues/145>
- <https://github.com/deepseek-ai/DeepSeek-V3/issues/1229>
- <https://github.com/deepseek-ai/DeepSeek-R1/issues/9>
- <https://github.com/openai/codex/issues/27587>
- <https://discuss.ai.google.dev/t/gemini-3-0-pro-is-ignoring-my-current-prompts-and-repeating-old-answers-in-longer-chats/111307>
- <https://ai.google.dev/gemini-api/docs/long-context>

## 候选改动

只改两句：

1. `SKILL.md` 删除“也避免把‘由于……未提供’等缺项说明写进正文”，保留为“缺项说明放在正文外”；
2. `workflow.md` 删除“也避免把‘由于政策依据、截止时间等尚未提供’这类缺项说明写进正文”，保留为“缺项说明放在正文外”。

同步更新确定性用例 P036 和边界测试，确保正向目标存在、两个显式诱导示例不再回流到 canonical 和仍维护的 GitHub、ClawHub、skillhub.cn 镜像。`redskill/` 是停止同步的历史归档，仍保留旧文本；没有为本轮修改它。没有改写其余否定规则；若后续某条规则也达到共性门槛，再单独消融。

## 真实写稿 A/B

机械启发式只统计材料视角、保护性否定、自证边界和写作操作说明等线索，不作为质量裁决：

| 输出组 | 三稿线索命中 |
| --- | ---: |
| 基线 writer A | 23 |
| 基线 writer B | 24 |
| 候选 writer A | 4 |
| 候选 writer B | 2 |
| 无 Skill 对照 | 26 |

候选两名 writer 平均 3 次，固定基线平均 23.5 次，下降约87%。六份候选稿均处于用户字数范围内。

匿名映射在盲审完成后解封：R1=候选 B，R2=候选 A，R3=基线 B，R4=基线 A。两名独立 verifier 只看原 prompt 与匿名输出：

| Verifier | 候选 | 基线 | 回归判断 |
| --- | --- | --- | --- |
| A | R1、R2 各 2 PASS、1 WARN | R3、R4 六稿均因旁白 FAIL | 未发现事实外扩、状态升级或格式回退 |
| B | R1、R2 事实、状态、文种、篇幅均 PASS，旁白为 WARN | R3、R4 旁白 FAIL、文种 WARN | 未发现候选独有的事实或状态回退 |

两名 verifier 排序均为 R1、R2 明显优于 R3、R4。候选 S2 仍有少量“不能据此认定因果”等保护性说明，故本轮只称显著改善，不称彻底消除。

可选 `draft-body` lint 中，候选没有 medium/high 旁白命中。候选样稿的“口径”低级高频提示高于基线，这是非阻断残余风险；既有 ANTI-AI 高频表达复核已经覆盖此类词汇过用，本轮不为单次指标追加第三处 Prompt 修改。

## 工程验证

- `python -B -m unittest discover -s tests -v`：152/152 PASS。
- `python -B tools/run_real_prompt_ablation.py --baseline-root output/negative-narration-20260714/baseline-head-c7e2caf --baseline-label current-c7e2caf --current-root . --out output/negative-narration-20260714/canonical-ablation`：固定基线 107/108，候选 108/108；基线只在新增的等价正向措辞守卫 P036 失败。该工具不调用 LLM，只作工程证据。
- `npm run eval:official-writing:smoke`：20/20 PASS。沙箱内首次运行因 Promptfoo 无法启动 Python provider 得到 20 errors；获准在沙箱外复跑后通过，失败属于执行环境而非产品结果。
- `python -B tools/run_real_article_eval.py --out output/negative-narration-20260714/real-article-current`：10/10 样本关键要素完整，格式风险、重复事项和 ANTI-AI 风险为 0；9个样本仍有该工具的匿名占位词风险提示，需按工具说明人工复核。该脚本仍是确定性回归，不替代真实 writer/verifier。
- 完整数据集分 27 批的最大上下文为 24574 字符，低于仓库 `<25000` 门槛。
- `python -B C:/Users/admin/.codex/skills/.system/skill-creator/scripts/quick_validate.py chinese-official-writing`：PASS。
- `git diff --check`：PASS。

## 保留与回退判断

保留本次两句改写。它针对两个独立 writer、三个不同 prompt、两名独立 verifier 均确认的共性问题，且没有观察到事实、未决状态、文种、篇幅、格式或旧工作流回退。

不采纳以下扩大方案：

- 批量删除全部“不、不要、不得、不能”；
- 恢复显式否定示例来强化边界；
- 为不同模型建立中文固定口癖禁词表；
- 新增自动替换、硬清洗、finalizer 或默认多 Agent；
- 因社区个案提前防治尚未复现的问题。

后续若删去某条否定约束导致测试失败，优先改成“保留什么、放在哪里、保持何种强度”的正向目标；只有正向等价表达仍无法守住事实或格式边界时，才保留必要的精确否定，并单独记录原因。
