# 1.5.20 发布证据

日期：2026-07-21

## 变更边界

1.5.20 以 `v1.5.19=e22b0150666974f38c4ce9c3b75cf6757091e646` 为固定发行基线，只纳入两项独立验证通过的渐进式路由减载：

- Candidate BB 将公开来源核验细则从默认复杂工作流移入 `external-research.md`，只在用户明确要求搜索、核验公开来源或任务含时效事实时加载。默认复杂写稿净减少约 125 字符；核验任务用小叶子替代完整工作流时减少约 6078 字符。
- Candidate BC 将 `genre-checklist.md` 的报告检查项原文移入 `genre-checklist-report.md`。报告细查从 3705 字符的全量文种清单切换到 156 字符叶子，减少 3549 字符；其他文种仍读取原清单。

两项都只改变 reference 加载位置，不改信息选择、事实锚、文种骨架、用户模板、篇幅预算、段内写法、复核顺序、脚本、Hook、输出模式、修改次数或回退链。OpenClaw 普通包继续排除 `delivery-review-gate.md`、`gate_stop_hook.py` 和 `review_gate.py`。

## 真实写稿

Candidate BB 使用普通复杂报告、公开来源核验说明和复杂二次改稿做三组同模型 A/B，独立盲审三题均判 Candidate 胜；第三题 Baseline 有一处无依据补全来源发布主体，未达到共性门槛。

Candidate BC 使用公共停车场暑期运行报告、馆藏档案数字化进展报告、暑期课程预约试运行报告做三组 `gpt-5.6-sol / ultra` 同题 A/B，各取首个技术有效输出，不补抽。匿名映射解盲后，三题均为 Candidate 胜，其中一题小胜、一题微弱胜、一题胜。六稿硬检查全部通过，无 P0 保护性外扩，也没有单篇同一机制达到 3 处。

以上只支持“确定性减载成立，真实写稿未观察到质量回退”。不把语言胜负全部归因于字符减少，也不宣称所有模型和文种普遍提升。

## 工程验证

发布候选实际结果：

- `py -3.13 -m unittest discover -s tests`：352/352 通过；临时目录固定在发布 worktree 内，未再触发 Windows Temp ACL 噪声。
- `py -3.13 tools/run_real_prompt_ablation.py --baseline-root <1.5.19> --baseline-label v1.5.19 --current-root . --out <out>`：v1.5.19 为 108/108，current 为 108/108。
- `py -3.13 evals/official-writing/run_eval.py --suite smoke --judge-batch-size 2`：20/20 通过，0 failed，0 errors；Skill 10/10，judge consistency 1.0。
- `py -3.13 <skill-creator>/scripts/quick_validate.py chinese-official-writing`：通过。
- `python tools/sync_adapters.py`、镜像一致性单元测试、OpenClaw 三项运行时排除检查和 `git diff --check`：通过。
- ClawHub 与 skillhub.cn dry-run：待发布提交形成后使用真实 source commit 和带 slug 的临时 SkillHub 包复跑。

累计提交后的独立轻量 review 初始结论为 WARN：报告叶子交叉引用和 Promptfoo 外部核验触发条件需对齐。发布分支已做最小修正，定向测试通过；最终发布级回归待补录。

## 已知边界

- 本版没有扩大 Hook、FSM 或自动改稿能力；普通 ClawHub 包仍是纯 Skill 边界。
- 报告与外部核验叶子由 Agent 按入口条件读取；不支持渐进式 reference 的宿主可能仍一次性加载完整包，但规则内容不丢失。
- 两轮真实 A/B 各 3 题，能排除已观察到的明显回退，不能替代全量文种和跨模型矩阵。
- 报告叶子只拆报告，不在本版继续拆通知、纪要、请示等其他文种。

## 发布回执

- GitHub：待发布。
- ClawHub：待 dry-run、发布和公开状态核验。
- skillhub.cn：待 dry-run、向既有 `skillId=70149` 发布和公开状态核验。

小红书 Red SkillHub 继续排除。提交成功、公开 latest、审核和安全扫描分别记录，不互相推断。
