# WR-003/004 最小工程集成结果

## 结论

WR-003 跨文种责任承载与合理推断、WR-004 约20类事务文体功能和常用语路由已完成真实写稿优先验证，并进入独立分支的最小集成候选。WR-005 普通短稿自然度继续 HOLD，不在本原子中修改 lint、Hook 或篇幅能力。

## 真实写稿依据

- 三条指定 DeepSeek V4 Flash 路线共取得20份可分析真实稿；最初3次输出采集失效保留，技术复跑只补取缺失稿，不补题。
- WR-003 的责任承载在20稿中成立；候选直连又复测演讲词一般延续和责任书事实边界。责任主体存在不等于事实已获授权，材料外程序、承诺、互动和责任扩张仍按硬失败记录。
- WR-004 原型文种功能19/20成立，唯一缺口为编者按缺少显式标识；候选直连稿写出`编者按：`并通过。最终直连复测只读取 SKILL、information-selection、formulaic-language，保留`3月至6月`且不补年份，独立 SOL max 对事实、状态、时间锚、责任主体、文种、篇幅和直接使用全部判 PASS。
- WR-005 未通过：20稿中11稿未达到用户篇幅要求，3稿残留 Markdown，另有不同形态的重复或拖沓。该结论不反推 WR-003/004 失败。

## 集成范围

- canonical 新增中央事务文体参考，并在 SKILL 中采用直接叶路由。
- 信息选择补充责任承载、相对时间锚和近场事实约束。
- 新闻消息叶补充编者按显式标识；事务路由卡排除已由中央直接叶覆盖的任务。
- 四套普通兼容包由 `sync_adapters.py` 同步；未修改 Hook、版本号、许可证、README 或发行配置。

## 实际最小验证

1. `python -B -m unittest maintenance.tests.test_information_selection_classification maintenance.tests.test_skill_boundary.SkillBoundaryTests.test_openclaw_github_package_is_current_mit_and_hook_free maintenance.tests.test_skill_boundary.SkillBoundaryTests.test_candidate_ac_anchors_fact_relations_to_explicit_material maintenance.tests.test_description_news_trigger -q`
   - 7 tests，PASS。
2. `python -B -m unittest maintenance.tests.test_repository_reachability maintenance.tests.test_skillhub_package_builder -q`
   - 7 tests，PASS。
3. `python -B C:\Users\admin\.codex\skills\.system\skill-creator\scripts\quick_validate.py <skill-dir>` 分别验证 canonical、Agent Skills、Qwen Code、Hermes，均 PASS。第一次误用不存在的仓库内路径 `maintenance/tools/quick_validate.py`，脚本未启动；纠正到 Skill Creator 的真实入口后重跑。
4. `python -B maintenance/tools/sync_adapters.py` 连续运行两次；第二次未产生新的同步差异。
5. `git diff --check`，PASS。

通用 `quick_validate.py` 对 OpenClaw 包仍会因其既有平台专用 `category` frontmatter 报错；本原子没有改变该字段，专用 OpenClaw 文件集合、MIT、无 Hook 边界测试已通过。聚焦测试第一次运行的另一个失败是 README 引用既有但缺失的 `release-1.6.5-rc.md`，在固定基线同样存在，且 README 不在本原子范围，因此未借本次语义集成顺手修改。

## 剩余风险

- WR-005 仍需分别处理普通路径篇幅、Markdown 洁净输出和短稿重复；不得把已发布 Hook 当作普通语义层已经解决。
- `综上所述` 只有承担真实归纳作用时才应保留；现有 lint 的词面提示仍需在 WR-005 独立原子中校准。
- 当前候选尚未合入 `main`、未改版本、未构建发行包、未发布。
