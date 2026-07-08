# 2026-07-09 SKILL 入口事实边界拆行实验记录

## 目的

用户提出弱模型可能不是看不到规则，而是入口规则过多、单行信息密度过高导致注意力崩溃。本轮只测试一个最小候选：不删规则、不改 reference、不新增 lint 和脚本，仅把 `SKILL.md` 中“起草或改写”下的 4 条高密度长句拆成 8 条短句，并同步各 agent 镜像。

## 修改范围

- `chinese-official-writing/SKILL.md`
- `.agents/skills/chinese-official-writing/SKILL.md`
- `.qwen/skills/chinese-official-writing/SKILL.md`
- `hermes/skills/chinese-official-writing/SKILL.md`
- `skills/chinese-official-writing/SKILL.md`

候选只降低单条 bullet 的扫描密度，不改变术语和事实边界：正文外待确认、不要调查问卷、不要补强判断、不要补造责任部门和后续动作、后续轮次不得阻断。

## 确定性验证

- `python -m unittest tests.test_real_prompt_ablation tests.test_skill_boundary`
  - 结果：41 tests OK
- `python .\tools\run_real_prompt_ablation.py --baseline-root output\release-baselines\github-1.5.2 --baseline-label baseline-1.5.2 --current-root . --out output\real-prompt-vs-1.5.2-split-drafting-rules`
  - 结果：baseline-1.5.2 85/85，current 85/85
- 入口片段统计：
  - 字符数：983 -> 1003
  - 最大单行长度：181 -> 132
  - 行数：10 -> 14

确定性验证只能证明包结构和脚本用例没有回退，不能证明真实写作质量改善。

## 真实写作 A/B

模型和分组：

- B-WEAK：1.5.2 基线，`gpt-5.3-codex-spark`，low
- C-WEAK：当前拆行候选，`gpt-5.3-codex-spark`，low
- B-STRONG：1.5.2 基线，`gpt-5.5`，low
- C-STRONG：当前拆行候选，`gpt-5.5`，low

5 个自然语言 prompt 覆盖：

- TestAgent 版本排查通知，检查动作关系和时间点。
- openclaw 安装情况报告，检查不编日期、过程和整改。
- 世界杯期间禁止赌球和考勤提醒通知，检查语气柔和和不补执行链条。
- 5090 电脑采购情况说明，检查要点置入和事实边界。
- 260 字以内通知压缩，检查联系人、反馈渠道和落款保留。

独立 verifier 评分：

| Prompt | B-WEAK | C-WEAK | B-STRONG | C-STRONG |
| --- | --- | --- | --- | --- |
| P1 | WARN | WARN | PASS | PASS |
| P2 | WARN | PASS | WARN | WARN |
| P3 | WARN | WARN | PASS | PASS |
| P4 | PASS | WARN | PASS | WARN |
| P5 | PASS | FAIL | PASS | PASS |

## 主要发现

拆行候选的收益有限：

- C-WEAK 的 Markdown 加粗残留少于 B-WEAK。
- P2 比 B-WEAK 更贴近用户要求。

但真实风险更大：

- C-WEAK P5 把“清查结果通过 OA 反馈至信息技术部”改成“由联系人李明通过电话12345678确认反馈”，将联系人电话误写为反馈方式，并遗漏 OA 渠道，属于事实关系错误。
- C-WEAK P4 增加“避免未验证即盲目扩展”“租约类成本波动”等未给判断。
- C-WEAK P3 增加“不主张一刀切管理”“坚决态度”等用户未给管理判断。
- C-STRONG P4 也出现扩写“稿件审校、规则匹配、模型响应、任务路由”等未给细节的边界放松。

## 结论

当前拆行候选不保留。它改善了弱模型的部分 Markdown 表现，但代价是弱模型事实关系和压缩改写准确性回退，收益不足以覆盖风险。本轮应撤回 SKILL 镜像改动，只保留测试证据和接手记录。

后续如果继续做提示压缩，应先做只读信息熵和重复表达审查，再每次只动一个小块，并固定使用弱/强模型真实 A/B。优先关注：

- 时间点不要改成截止时间。
- 报送至、反馈至、下发至、由谁执行的动作关系不能改错。
- 联系人、电话、反馈渠道不能互相替代。
- 正式正文不要残留 Markdown 加粗。
