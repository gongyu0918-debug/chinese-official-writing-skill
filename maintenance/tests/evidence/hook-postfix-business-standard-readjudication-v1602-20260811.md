# Post-fix Hook 业务口径复核

日期：2026-08-11

结论：`OPTIONAL COMPANION ELIGIBLE / PRE-REGISTERED HARD GATE SATISFIED UNDER USER STANDARD / NO QUALITY-UPLIFT CLAIM / ONE HARD OBSERVATION`

## 为什么复核

原始匿名裁判按极窄材料字面，把“按计划推进办结”“确保按期完成”“按规定程序继续推进”等常规公文衔接直接视为新增计划或承诺，据此把 P003、P009 同时计为 Enabled 独有状态硬失败，并形成 `HOLD`。原判和原始裁判均保留在 `tests/evidence/hook-postfix-real-ab-v1602-postfix-result-20260811.md` 及证据提交 `ec09a3e5`，不删除、不改写。

用户随后明确业务口径：对已经给出的在办事项，未新增具体主体、期限、制度内容或决定状态的“按程序推进、按既定安排、按计划推进、确保按期完成”等常规后续工作表述，属于正式材料的合理衔接，不按硬事实外扩处理。只有增加具体程序事实，或把已完成、在办、未决、已决定等状态实质改写，才计硬失败。

## 逐项复核

- P002 / T2：内容是纯审稿建议，不是交付正文中的既成事实。“采购方组织验收”等建议可能过实，可记质量问题，但没有把它写成已发生事实，facts/state 均不作硬失败。
- P003 / T3：75件工单仍写“正在办理”，7项问题仍写“正在处理”；“将按计划推进办结”“按照既定安排逐项抓好落实，确保各项工作按期完成”未新增具体主体、期限或程序，也没有把在办写成已办。facts/state 改判为 PASS；两臂均未达到800字，length 仍 FAIL。
- P009 / T3：常规“按规定程序、按既定安排”本身不判错，但稿件另行补入“逐项登记”“按核验意见推进修正”“目录管理工作要求”“已落实维护和管理”等具体未给工作事实，并把已经更新完成的42项元数据写成“按工作计划持续推进相关工作”。这改变完成/在办关系，facts/state 仍为硬失败。

Kimi 的独立匿名判定与该口径一致：P002 两稿 facts/state PASS；P003 两稿 facts/state PASS；P009 Enabled 为 WARN 且 facts/state PASS，但明确指出42项元数据的当前事项表述含混。另一次不读取 mapping 的业务口径复核则把 P009 的元数据状态改写判为硬失败。两种宽严判断都只留下 P009 一个观察点，不再形成两个独立配对重复。

## 对预注册停线的影响

有效矩阵仍为9/9配对、18/18调用、三个 provider 各3对。按用户业务口径重新分类后：

- Enabled 独有 state/facts 硬失败只剩 P009 一对，没有在第二个独立配对重复；
- Enabled 独有 length 失败只在 P001 出现一次；
- 纯审稿 bypass 三家3/3无 transaction、无 Stop block、无代改；
- 六个 Enabled 写稿最终均原样发射 D0，D1为0。

预注册的发布停线要求同一硬维度或可归纳机制至少在两个独立配对重复。复核后该条件不成立，因此撤销“重复硬失败导致 HOLD”的发布归因。这里的“非劣”只表示预注册硬门通过，不表示统计质量领先：SOL 主票仍为 Enabled 1胜、Disabled 7胜、1难分；Kimi、Grok均为 Enabled 2胜、Disabled 5胜、2难分。

## 保留风险

- P009 是一例真实的完成/在办关系含混，继续作为长稿观察项，不追加一例一修规则。
- 六个写稿 Enabled 均多一次 Stop block，最后只再次发射不变 D0；存在明确延迟成本。
- 本轮没有 D1，不能证明 Hook 改稿收益，也不能证明 length-nonworsening 的真实 D1 效果。
- Hook 未捕获 P009 的状态问题，不能描述为全面事实、文种、要素或篇幅兜底；只可作为默认关闭、用户显式启用的窄域有界伴随物。

## 发布边界

在完整保留原裁判分歧、单例风险和流程成本的前提下，Hook 可继续留在 MIT SkillHub 完整包中作为可选伴随物。普通 Skill 安装不自动启用；Codex 仍需安装、启用与信任，Claude Code 与 WorkBuddy/CodeBuddy 仍需显式加载。ClawHub/OpenClaw 继续冻结且不含 Hook。

本复核没有修改 Hook、`review_gate.py`、`prose_lint.py`、普通 Skill 写稿规则或冻结原始证据；未合并 `main`、未推送、未发布。
