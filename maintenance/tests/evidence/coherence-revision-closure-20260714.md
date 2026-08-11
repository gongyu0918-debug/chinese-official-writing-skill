# 实际改稿闭环验证（2026-07-14）

## 结论

本轮完成了“改稿—双独立复核—第三方核验—局部返修—再次核验”的实际闭环，不修改产品 Prompt，也不在 `proofreading-checklist.md` 增加“篇章逻辑一致性”小节。

两名 fresh writer 分别完成 R1 长篇决策状态联动和 R2 正文/附件主体期限联动，共 4 份首轮改稿。两名独立 reviewer 首轮均判 4/4 PASS；第三名 verifier 复核后将 Writer B-R1 降为 WARN：末段范围限定仍只写“核查、确认、更新、复核”，没有纳入已经决定开展的“本次统一字段库试用”。其余 3 份为 PASS，没有 writer FAIL。

Writer B 随后按真实第二轮修改要求只修这一处。第三方 verifier 判 PASS；字符级核对显示第二轮相对第一轮 R1 恰好完成一次指定短语替换，其他内容完全相同，局部返修闭环完成。

首轮只有 1 份 WARN，来自 1 个 prompt、1 名 writer；两名 reviewer 还共同漏掉了该处。没有达到“至少 3 份同类失败、覆盖至少 2 个 prompt、涉及 2 名 writer，并经 2 名独立 reviewer 共同确认”的产品修改门槛。

## 基线与产品边界

- 工作区基线：`e6cbedb58ae2292082426472c2dc9f30842f8185`。
- 执行入口：当前工作区 `.agents/skills/chinese-official-writing/SKILL.md`。
- `proofreading-checklist.md` 保持原样，SHA-256 `AC5B4C1A1F3CC15F588873F183727EFD24CD5B10B5137A0382E7E7A7BD9DD21A`。
- 本轮不新增脚本、自动替换、评分器、默认多 Agent、默认联网或新工作流阶段。
- writer、reviewer 和 verifier 均为独立 Codex 子上下文；当前界面不能核验精确模型 ID，因此本轮记真实改稿 sanity，不作跨模型统计结论。

## 测试设计

### R1 长篇决策状态联动

以 `output/long-revision-stability-20260714/writer-a-round1.md` 为冻结底稿，底稿 3286 个汉字，SHA-256 `64230B4D9D0546D92E91E2F04224180EA93D54346B50E05E52CB224474C61DE4`。

用户新增决定为：7月20日至8月2日，在受理、审批两个环节的18个事项中试用统一字段库；尚未决定是否扩大到全部132个事项；8月5日前同时汇总第二轮核验和试用情况，提交专题会议研究下一步安排。第二轮系统更新、7月25日抽取30个事项核验、74个问题及58/16状态等其他事实保持不变。

该任务检查新决定是否贯穿“主要进展—存在问题—下一步安排—末段范围限定”，并检查原有数字、责任、期限和结论强度是否保真。

### R2 正文与附件选择性联动

通知底稿同时包含接收/汇总职责和技术职责。用户只把接收、汇总单位改为数据管理处，把报送截止改为7月22日17时，把汇总期限改为7月25日；信息技术部继续负责账号状态核验和技术问题答复。

该任务检查正文、附件填报说明、主体、期限和渠道能否同步，同时避免把信息技术部的技术职责一并误改。

## 首轮结果

| 输出 | Reviewer A | Reviewer B | 第三方 verifier | 结论 |
|---|---|---|---|---|
| Writer A-R1 | PASS | PASS | PASS | 长文新决策和原有事实完整联动 |
| Writer A-R2 | PASS | PASS | PASS | 正文、附件、主体、期限和技术职责均正确 |
| Writer B-R1 | PASS | PASS | WARN | 末段范围限定漏纳入本次试用 |
| Writer B-R2 | PASS | PASS | PASS | 选择性主体联动正确，无旧期限残留 |

Writer B-R1 新增“开展统一字段库试用”同层级自然段被 verifier 判为必要组织，不属于结构破坏；WARN 只来自末段范围限定未同步。

两名 reviewer 对主要修改判断准确，但共同漏掉同一句轻微范围残留。该结果说明双独立审稿不能等同于穷尽式复核，第三方抽检仍有价值；本轮不据此把默认多 Agent 写入产品流程。

## 第二轮局部返修

第二轮只要求 Writer B 在末段范围限定中纳入本次统一字段库试用，其他文字、段落、顺序、数字、状态、责任和期限不变。

- 第三方 verifier：PASS，确认旧范围残留已经消除，没有新矛盾。
- 字符级核对：第一轮目标旧短语命中 1 次，第二轮目标新短语命中 1 次，`EXACT_SINGLE_REPLACEMENT=True`。
- 第一轮 R1 规范化字符数 4061，第二轮 4071；差异仅为“及本次统一字段库试用”这一处增量。

## 门槛判断

| 同类问题 | WARN | FAIL | prompt | writer | 双 reviewer 共同确认 | 达到门槛 |
|---|---:|---:|---:|---:|---|---|
| 范围限定句未随新决定联动 | 1 | 0 | 1 | 1 | 否 | 否 |
| 决策状态或试用安排未落实 | 0 | 0 | 0 | 0 | 不适用 | 否 |
| 责任主体或期限残留 | 0 | 0 | 0 | 0 | 不适用 | 否 |
| 无关事实、数字或状态改变 | 0 | 0 | 0 | 0 | 不适用 | 否 |
| 新增事实、扩大决定或结构破坏 | 0 | 0 | 0 | 0 | 不适用 | 否 |

本轮不把两名 reviewer 对同一处的漏检重复计算为两份 writer 失败，也不把返修前后的同一问题重复计数。

## 原始证据

- `tests/evidence/coherence-revision-closure-20260714/writer-prompts.md`
- `tests/evidence/coherence-revision-closure-20260714/writer-a.md`
- `tests/evidence/coherence-revision-closure-20260714/writer-b.md`
- `tests/evidence/coherence-revision-closure-20260714/reviewer-a.md`
- `tests/evidence/coherence-revision-closure-20260714/reviewer-b.md`
- `tests/evidence/coherence-revision-closure-20260714/verifier.md`
- `tests/evidence/coherence-revision-closure-20260714/writer-b-r1-round2.md`
- `tests/evidence/coherence-revision-closure-20260714/verifier-round2.md`

## 工程验证

- `python -B -m unittest discover -s tests`：152/152 通过。
- `npm.cmd run eval:official-writing:smoke`：20/20 通过，0 error，judge consistency 1.0；因 Promptfoo 的 Node 子进程需要启动工作区外 Python，本次直接在沙箱外运行，未把沙箱内 provider error 记作有效测试。
- `python -B C:\Users\admin\.codex\skills\.system\skill-creator\scripts\quick_validate.py chinese-official-writing`：通过，输出 `Skill is valid!`。
- `git diff --check` 和提交后工作区状态：提交前后分别核对。

## 尚未证明

- 三轮以上连续修改后的旧状态清除能力。
- 删除整段、调整章节顺序、更换标题或合并附件后的结构联动。
- 多附件、多底稿和跨文件引用中的主体、数字、期限同步。
- 隐含代词、简称和同义责任表述造成的非逐字残留。
- 不同长文文种和更多干净改稿对照中的稳定性。
- 外部事实真实性、业务决定合理性或正式程序完备性。

下一轮如继续测试，优先选择“删除整段并重排章节”与“正文—表格—两个附件同步”两个不同 prompt；仍按共性门槛决定是否进入产品 Prompt。
