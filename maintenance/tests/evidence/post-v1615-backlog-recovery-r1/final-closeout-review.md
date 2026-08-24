# v1.6.15 后恢复分支最终收口复核

日期：2026-08-24。

## 结论

`PASS_RESEARCH_CLOSEOUT / NOT_MAIN_READY`。本轮完成短稿稳定性诊断、完整日期原子的失败收缩与恢复、公开状态台账收口，以及付费提纲候选的本地整合。没有修改、合并、推送或发布 `main`；没有移动 tag；没有改写三个平台。

短稿诊断不支持“v1.6.15 系统性比提示词更短”的判断。五条 Codex CLI 路线、三题、v1.6.14/v1.6.15 共30臂中，短于完整提示词为4臂对3臂，短于材料段为0臂对0臂。逐稿复核显示，部分较短稿完整承担了申请、新闻或情况说明的文种功能；若机械要求正文长于提示词，会把指令文字也当成正文配额，并诱导模型用材料外程序、活动过程或未来安排换长度。

真实残余风险是：活动新闻两版各4/5路线省略完整日期中的年份；MiniMax 单一样本出现材料外活动过程和后续安排；多条路线会补当前日期。`WR-001-DATE` 两轮最小提示均提升年份命中，但 Ollama 两轮继续补造材料外活动过程，故该重复提示词方向终止，产品已恢复至 v1.6.15 字节，不留失败候选。

## 30提交检查点

- 固定公开基线：`main=origin/main@8aab5e61e65c0411b4bd6580173c2a107986fdcb`；已发布产品 tag：`v1.6.15^{commit}=762b84d49c35cb956ce464fa8aab5dd08f1ad113`。
- 检查前研究 HEAD：`2e586d10f774cf01d3a90c26230bb92263fbe78a`，相对 `main` 30个提交。
- 自上一检查点 `b987ee14` 后17个变更路径全部位于 `maintenance/`，Skill、reference、Hook、adapter、description 和版本元数据均无新增差异。
- 整个研究分支相对 `main` 的产品差异仍只有 `OC-003` 四个 reference 及四套普通镜像；该原子为 `ACCEPTED_RESEARCH_CANDIDATE_NOT_MERGED`，不能因状态和工程测试通过而合入公开版。
- `codex/paid-outline-review@8f1d31fe6feb839f02611f21192a45563865a8c3` 已本地快进到 current main 加 OT-001/组合生命周期、OT-002 和 RF-001 的整合状态；公开分支只记录这一状态，不包含付费源码。未推送、未发布付费包。

## 最终验证

- `git diff --check main...HEAD`：通过。
- 最近五提交路径检查：`RECENT_COUNT=17`，`RECENT_NON_MAINT=0`。
- `python -m unittest maintenance.tests.test_status_ledger_consistency maintenance.tests.test_repository_reachability maintenance.tests.test_skill_boundary`：90/90通过。
- 首次误用仓内旧路径 `python maintenance/tools/quick_validate.py ...`：文件不存在，退出2，不计为通过。
- 改用当前 skill-creator 入口 `python -B C:\Users\admin\.codex\skills\.system\skill-creator\scripts\quick_validate.py chinese-official-writing`：通过，输出 `Skill is valid!`。
- 复核时 `main`、本研究 worktree、`wr001-date-r1`、`paid-outline-review`、`paid-consolidated-v1615-r1` 均为 clean；`main=origin/main`。

## 剩余风险与停止边界

1. 不能从 SkillHub 一次点赞回落推导具体质量原因；公开 API 不提供对应用户、稿件或评价文本。
2. 活动新闻完整年份是跨版本、跨 provider 的真实风险，但追加同义提示已出现材料外扩写副作用；下轮若继续，应换新题先查日期/落款取舍或路由位置，不重复堆同一句禁令。
3. 短稿继续按“材料利用、必要原因或即时作用、文种功能、事实边界、直接可用性”逐项判断；字数和提示词长度只作诊断信号，不作单独硬门。
4. `OC-003` 仍有 Alibaba 材料外程序；付费组合生命周期仅有 CodeBuddy 单一在线样本；RF-001 的严格版式、字体环境和多页表现仍需更多 Word 实件验证。
5. 本记录只收口研究事实，不授权 `main` 合并、推送、tag、GitHub Release、SkillHub 或 ClawHub 写入。
