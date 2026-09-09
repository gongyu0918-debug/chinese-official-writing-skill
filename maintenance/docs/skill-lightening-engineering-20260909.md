# SKILL.md 组合减负工程合并检查（2026-09-09）

工程门已满足本地合并所需条件。产品组合是否最终接纳，还需与同树真实写稿对照合并判断；本报告不把静态检查当作写稿质量证明。未合 main、推送、发布或更新本机安装。

- 工作树：`output/route-worktrees/skill-lightening-merge-check`，分支 `codex/skill-lightening-merge-check`。
- 共同基线：`f171e82fbe2849af4ec50f3605845ae315d456d8`。
- 组合产品冻结：`9149182bae37d6031b26ae061ce5d85bbfb3938f`。
- 工程变动不修改 canonical；仅迁移验证入口、补充完整等价证据组、同步五个现有公开兼容包中的本次三个路径。

## 验证器和镜像变动

旧断言把文种条件、加载表及所有资源入口固定在首页。现通过首页明确存在的 `references/reference-index.md` 和 `references/compatibility-scene-routing.md` 读取原条件，保留原来的内容、排除条件和质量桥断言；没有扫描全部专叶来凑命中。

新增保真检查固定 f171 原首页的 36 条加载条件及 5 段场景直达条件的摘要，检查移植后完整、无重复。索引新增的场景分流行单独排除，原 36 行在两级表中逐字保留。六套 Skill 根目录逐项验证两级表第一列路径和 8 个质量桥文件存在；未命中或卡片不足时回索引、首页直达保留原条件、只审不改保留轻入口均有断言。

`run_real_prompt_ablation.py` 是静态规则可达性检查，不调用写稿模型。P111、P112 保留原完整证据组，新增组同时要求首页真实索引入口、原全部路由条件和原全部专叶条件。负向测试逐项去除证据，确认不能因剩余任一规则命中而错误通过。更新后的工具回测 f171 原树，111/111 个静态案例通过。

五包为 agent-skills、qwen-code、qwenwork、hermes、openclaw。每包只移植 f171 到组合产品的 `SKILL.md` 差异及两份新增 reference；没有调用全量同步生成脚本。前四包各 42 文件，OpenClaw 41 文件。平台 frontmatter 和 Hook 排除保持；其他既有文件逐一按 LF 归一后与 f171 匹配。red-skillhub 平台快照未改。

投诉镜像测试的 11 个对象为 6 个由当前 canonical 即时组装的临时 companion fixture，加上述 5 个公开包。没有读取本机旧安装，也没有同步额外公开产品目录。

## 实际测试和失败处理

工作目录均为上述组合树，基线六方法对照除外。PowerShell 的 `python` 实际是 `C:/Users/admin/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe`。

| 实跑命令或检查 | 结果 |
| --- | --- |
| `python -m unittest maintenance.tests.test_skill_boundary` | 完成入口迁移与两项新增测试后 83/83 通过，0.140 秒。 |
| `python -m unittest discover -s maintenance/tests -p test_*.py` | 唯一一次全量，847 项、159.659 秒；30 个失败子项及 1 个错误，归并为下列 6 个方法。原日志保留。 |
| 在 f171 原树执行同 6 个失败方法 | 6/6 通过，4.536 秒。确认差异来自本次移植后验证器仍固定原位置。 |
| `python -m unittest maintenance.tests.test_skill_boundary maintenance.tests.test_advisory_feedback_leaf maintenance.tests.test_complaint_reflection_leaf maintenance.tests.test_oc003_feasibility_state_layering maintenance.tests.test_repository_reachability maintenance.tests.test_real_prompt_ablation` | 补齐迁移后的最终受影响套件 115/115 通过，17.973 秒，覆盖全量出现的全部失败方法及所有修改测试。 |
| 候选 `run_real_prompt_ablation.py` 的 `evaluate_root(f171原树, ...)` | 111/111 通过，未破坏旧布局基线判定。 |
| `python -m py_compile` 对本次 6 个测试文件及 `maintenance/tools/run_real_prompt_ablation.py` | 通过。 |
| 同一 Hermes Python 执行 `C:/Users/admin/.codex/skills/.system/skill-creator/scripts/quick_validate.py <Skill目录>` | canonical 及 4 个普通包通过；OpenClaw 见下述既有 schema 差异。 |
| 包文件清单、仅三个路径变动、frontmatter/禁入文件、其他文件保真检查 | 五包通过；两份新 reference 内容与 canonical 一致。 |
| `git diff --check` | 通过；仅 Git 的 LF/CRLF 工作区转换提示。 |

全量中六个失败方法为：

1. `AdvisoryFeedbackLeafTests.test_direct_route_keeps_cooperative_feedback_separate_from_power_guidance`。
2. `ComplaintReflectionLeafTests.test_direct_route_is_separate_from_advisory_and_received_records`。
3. `ComplaintReflectionLeafTests.test_leaf_matches_all_public_and_companion_mirrors`。
4. `FeasibilityStateLayeringTests.test_named_completeness_review_stops_before_option_library`。
5. `RepositoryReachabilityTests.test_every_canonical_reference_and_script_has_an_entrypoint`。
6. `RealPromptAblationTests.test_current_skill_passes_real_prompt_cases`（P111、P112）。

上述失败均由验证代码迁移解决，canonical 规则没有为通过测试而加句。首轮边界检查中的交付范围镜像失败，初步曾误读为基线旧包不同步；精读断言后确认它比较整页正文，失败来自本次首页尚未镜像。仅应用本次三文件差异后消失，没有修补旧交付规则。

quick_validate 首次从 Python 子进程调用裸 `python` 时解析到另一解释器，报 `ModuleNotFoundError: No module named 'yaml'`；改用当前 `sys.executable`，不安装依赖。OpenClaw 的既有 `category` 被通用 Skill 校验器拒绝。对 f171 原版 OpenClaw SKILL.md 运行同一命令，得到完全相同的 `Unexpected key(s) in SKILL.md frontmatter: category`；保留平台字段，平台专用边界测试通过。该差异不归因于减负，也未宣称通用验证器六包全绿。

## 证据与剩余边界

原始工程证据归档：`F:/Workspaces/chinese-official-writing-skill-archives/experiments/skill-lightening-20260909/merge-engineering-evidence.zip`。

SHA-256：`5e787df61f175ea118ddee2617c9964797c206785dea397bbdb0989dcf6067dc`。共 12 个成员，逐项解压内容与原文件匹配；包含首次失败、全量失败、基线对照、最终定向回归、包范围审计及 quick_validate 原始结果。当前工作树原日志在 `output/merge-gate/`。

没有重跑第二次全量；最后改动仅涉及上述受影响验证器，115 项定向回归已覆盖。不得将结果表述为“最终产品全量 848 项一次全绿”。工程检查没有发现仍未收束的本次回归；模型波动、交汇路由实际加载和成稿质量由根任务真实稿证据另行判定。产品版本、远端、发布包和本机安装均未推进。
