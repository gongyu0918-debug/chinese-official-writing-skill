# 篇章逻辑一致性门槛验证（2026-07-14）

## 结论

本轮不修改产品 Prompt，也不在 `proofreading-checklist.md` 增加“篇章逻辑一致性”小节。

两名独立 reviewer 对 9 个未见用例完成只审不改测试，第三名独立 verifier 逐项复核。没有 reviewer FAIL；仅 Reviewer B 在 P2、P3 的修改建议中各出现一次 WARN，表现为倾向直接采用正文口径，没有先保留“核定摘要、正文、结论哪一处代表真实状态”的条件。两次 WARN 覆盖 2 个 prompt，但只有 2 份输出、1 名 reviewer，未达到“至少 3 份同类失败、覆盖至少 2 个 prompt、涉及 2 名独立 reviewer”的产品修改门槛。

因此，当前 `proofreading-checklist.md` 保持原样。本轮开始前的 SHA-256 为 `AC5B4C1A1F3CC15F588873F183727EFD24CD5B10B5137A0382E7E7A7BD9DD21A`，证据提交中不包含该文件。

## 基线与测试方式

- 工作区基线：`e753cc20ee014fa704071b24c7a6bfa775410210`。
- 写作/审稿入口：当前工作区 `chinese-official-writing` Skill。
- 测试方式：两个相互独立的 reviewer 只读取统一 prompt、当前 Skill 和 prompt 明确引用的长文；不联网，不查看答案或彼此输出，不修改产品文件。
- 核验方式：第三名 verifier 只读取原 prompt、两份 reviewer 原始输出和 prompt 引用的长文，按 PASS/WARN/FAIL 复核漏检、误报、事实选择和修改越界。
- 模型记录：三次任务均为独立 Codex 子上下文；当前运行界面不能核验精确模型 ID，因此本轮记为真实审稿 sanity 和独立复核证据，不包装成跨模型统计结论。

## 用例覆盖

| 用例 | 风险面 | 结果 |
|---|---|---|
| P1 | 3286 个汉字长文干净对照 | 两名 reviewer 均 PASS，无误报 |
| P2 | 3286 个汉字长文摘要与正文远距离冲突 | 核心冲突均检出；A PASS，B WARN |
| P3 | 长文结论与正文远距离冲突 | 核心冲突均检出；A PASS，B WARN |
| P4 | 多因素并行时的直接因果归因和全面推广 | 两名 reviewer 均 PASS |
| P5 | 有限样本外推总体、影响与措施强度升级 | 两名 reviewer 均 PASS |
| P6 | 最新决策状态修改后的采购、合同、部署残留 | 两名 reviewer 均 PASS |
| P7 | 最新责任主体修改后的旧主体残留 | 两名 reviewer 均 PASS |
| P8 | 短稿干净对照 | 两名 reviewer 均 PASS，无误报 |
| P9 | 修改联动干净对照 | 两名 reviewer 均 PASS，无误报 |

长文源文件：

- `output/long-revision-stability-20260714/writer-a-round1.md`：3286 个汉字，SHA-256 `64230B4D9D0546D92E91E2F04224180EA93D54346B50E05E52CB224474C61DE4`。
- `output/long-revision-stability-20260714/writer-b-round1.md`：2646 个汉字，SHA-256 `43ECA72116C0C948ACD9E3496B65266FE99CDC969A8F8042E536302B23F3A474`。

## 门槛统计

| 同类风险 | WARN | FAIL | 分布 | 达到门槛 |
|---|---:|---:|---|---|
| L 摘要/结论与远距离正文不一致 | 2 | 0 | Reviewer B：P2、P3 | 否：仅 2 份、1 名 reviewer |
| E 证据、因果、范围与措施跳跃 | 0 | 0 | 无 | 否 |
| R 最新修改与全文联动残留 | 0 | 0 | 无 | 否 |
| C 干净对照误报 | 0 | 0 | 无 | 否 |

本轮不把 WARN 与 FAIL 混算，也不把样稿中人工设置的问题数量当作 Skill 失败数量。

## 原始证据

- `tests/evidence/coherence-consistency-gate-20260714/prompts.md`
- `tests/evidence/coherence-consistency-gate-20260714/reviewer-a.md`
- `tests/evidence/coherence-consistency-gate-20260714/reviewer-b.md`
- `tests/evidence/coherence-consistency-gate-20260714/verifier.md`

原始文件 SHA-256：

- `prompts.md`：`4953B0875C47ADC3479B9EE4385280492647A81AA35E26898AB79C9147780388`
- `reviewer-a.md`：`2108AA28988DC8A248C5C76759D09FB81F242EDC4F26BE8086F9015662417FA6`
- `reviewer-b.md`：`1158ECDC5E79F9E07B95D19902DB90DE7CECA184C7AF0748A5FBCF866D2636D6`
- `verifier.md`：`5DFAAA256202A970665B1F1170DF10008E5AF31421079AF2B1AE875943009990`

## 工程验证

- `python -B -m unittest discover -s tests`：152/152 通过。
- `npm.cmd run eval:official-writing:smoke`：沙箱内首次执行因 Promptfoo 的 Node 子进程无法启动工作区外 Python，20 个用例均为 error，不能计为有效测试；在沙箱外用同一命令重跑后 20/20 通过，0 error，judge consistency 1.0。
- `python -B C:\Users\admin\.codex\skills\.system\skill-creator\scripts\quick_validate.py chinese-official-writing`：通过，输出 `Skill is valid!`。
- `git diff --check`：通过。

## 尚未证明

- 一个 3000 字以上样本不能证明不同超长文、附件和多文档交叉引用场景的稳定检出率。
- 尚未覆盖多跳因果、条件例外、概念缓慢漂移等更隐蔽的跨章节问题。
- P6、P7 证明了修改残留可被审校发现，没有证明大范围重构后的实际改稿闭环。
- 三份干净对照不足以推导统计意义上的误报率。
- 本轮只检验稿内一致性，不核验外部事实、政策依据或业务决策正确性。

Reviewer B 的条件式事实核定倾向作为后续观察项保留；在另一个独立 reviewer 和第三份输出出现同类失败前，不进入产品 Prompt。
