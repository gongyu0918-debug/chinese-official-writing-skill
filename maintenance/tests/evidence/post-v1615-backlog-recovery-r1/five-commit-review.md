# v1.6.15 后恢复分支五提交复核

日期：2026-08-24。

## 结论

`PASS_FOR_CONTINUED_RESEARCH / NOT_MAIN_READY`。`codex/post-v1615-backlog-recovery-r1` 自 `main` 累计25个提交后暂停复核。最新提交只修规格、台账、证据索引和状态一致性测试，没有改变 Skill、reference、Hook 或 description。分支全部产品差异仍限于 `OC-003` 的四个 reference 及四套普通镜像；真实写稿残余风险不因工程检查通过而消失，候选不合入 main、不发布。

## 范围与基线

- 固定公开基线：`main@8aab5e61`，已发布产品 tag：`v1.6.15^{commit}=762b84d4`。
- 复核提交：`b987ee14`；相对父提交仅6个维护区文件，产品和 Hook 路径为0。
- `main...HEAD` 产品差异为 `ai-compute-docs.md`、`argument-chains.md`、`genre-checklist-feasibility-review.md`、`workflow.md` 及四套普通镜像；SKILL、description、Hook core、adapter 和发行元数据差异为0。
- `OC-003` 当前仍是 `ACCEPTED_RESEARCH_CANDIDATE_NOT_MERGED`：Luna通过、Ollama带警告通过、Alibaba仍有材料外程序，另外两路样本指令边界无效。

## 直接回归与消融

- `python -m unittest maintenance.tests.test_status_ledger_consistency maintenance.tests.test_repository_reachability maintenance.tests.test_skill_boundary`：89/89通过。
- `git diff --check main...HEAD`：通过。
- skill-creator `quick_validate.py`：canonical、Agent Skills、Qwen Code、Hermes 四套通过；OpenClaw 包因其既有 `category` frontmatter 不在 Codex validator 允许字段内而退出1。该文件不在本分支差异中，仓库自身边界/镜像测试已通过；不把外部 validator 不兼容写成产品回退或通过。
- 状态消融：移除本轮新增映射会使 `test_status_ledger_consistency` 的 OC-003、v1.6.15、WR-012/description 关闭状态或 HK-004 发布状态断言失败；该测试只防维护状态漂移，不承担写稿质量评价。

## 剩余风险

- `OC-003` 尚未达到跨 provider 稳定准入，不能因四套镜像一致就合入公开版。
- 点赞回落只能证明平台计数变化，不能定位具体稿件问题；须另做 v1.6.14/v1.6.15 同题真实写稿。
- 无字数上限的短事务稿若因过度保守短于提示词并漏掉原因、作用或文种功能，应判质量回退；不以机械字符比代替人工事实和功能核对。
