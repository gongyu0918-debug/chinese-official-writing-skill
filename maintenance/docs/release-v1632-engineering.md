# v1.6.32 工程验证

工程发布门通过。当前没有未收束的工程回归；真实写稿结论与外部发布回执由发布任务分别记录。本检查没有推送、打 tag、发布或更改本机安装。

- 工作树：`output/release-worktrees/release-v1.6.32`。
- 公开基线：`77dfcfacefeaa91fd2d181b3187d249baf730bc5`（v1.6.31）。
- 写作规则冻结：`0f088b8228971b53e02f216818cde713bc7c72e3`；工程检查时产品 HEAD 为 `6ab6be6acf3f236cd997f55388fa65f0cb544d1b`，后者仅补齐七个适配 manifest/package 的版本字段。
- 本工程变动仅涉及测试、静态验证工具和本报告；没有修改 canonical、构建工具、版本 manifest 或生成发布包。

## 检查范围

复用已验证的两级路由工程断言，按当前公开树的 `package_fixtures.generated_packages()` 生成临时兼容包，不恢复仓库内的产品镜像。首页必须明确链接两级索引，测试才读取对应页；原有条件和排除项继续逐条断言，不能通过扫描任意专叶凑规则命中。

公开基线首页 35 条加载条件在索引和场景页中逐字保留，无重复；五段场景判定原文及其排除条件同样保真。测试固定公开基线摘要，并显式阻止导入本基线不存在的增项专叶及入口。canonical 与五个按需生成兼容包逐项验证路径、八个质量检查衔接、前置直达、轻量卡不足时回索引、只审不改边界。

静态 `run_real_prompt_ablation.py` 保留 P111、P112 的旧完整证据组；新增组同时要求首页真实索引入口、原全部文种条件和原全部叶规则。逐项删去任一必要证据必须判失败。此工具不调用写稿模型；更新后回测未修改的公开基线，111/111 个案例通过。

## 实际执行

命令工作目录为发布树；注明公开基线的对照在未修改的 `output/route-worktrees/public-repository-cleanup` 执行。Python 为 `C:/Users/admin/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe`。

| 命令或检查 | 结果 |
| --- | --- |
| `python -m unittest maintenance.tests.test_skill_boundary maintenance.tests.test_advisory_feedback_leaf maintenance.tests.test_complaint_reflection_leaf maintenance.tests.test_oc003_feasibility_state_layering maintenance.tests.test_repository_reachability maintenance.tests.test_real_prompt_ablation` | 115 项，17.612 秒；111 通过，4 项版本期望/manifest 一致性失败。两级路由及生成包内容断言无失败。 |
| 定向执行 `test_skill_boundary` 的 `test_claude_plugin_manifest_version_matches_skill_and_sync_script`、`test_codex_plugin_version_and_hook_path_track_canonical_skill`、`test_openclaw_bundle_readme_is_current_and_contains_no_publish_command`、`test_openclaw_github_package_is_current_mit_and_hook_free` | 版本字段与测试常量同步后 4/4 通过，0.019 秒。 |
| `python -m unittest discover -s maintenance/tests -p test_*.py` | 唯一一次全量：827 项、135.475 秒；824 通过，3 项当前安装版本字符串期望过期。原失败日志保留。 |
| `python -m unittest maintenance.tests.test_status_ledger_consistency` | 将三处当前 README 安装命令期望从 1.6.31 更新为 1.6.32 后，16/16 通过，0.021 秒；历史发布状态和回执断言不变。 |
| 未修改公开基线执行上述三个失败方法 | 3/3 通过，确认是随当前版本更新的期望位置，不是历史发布证据损坏。 |
| 候选 `run_real_prompt_ablation.py` 的 `evaluate_root(公开基线, ...)` | 111/111 静态案例通过。 |
| Hermes Python 执行 `C:/Users/admin/.codex/skills/.system/skill-creator/scripts/quick_validate.py <Skill目录>` | canonical 和四个普通兼容包通过；OpenClaw 的通用 schema 差异见下。 |
| `python -m py_compile` 对本次七个测试文件及 `maintenance/tools/run_real_prompt_ablation.py` | 通过。 |
| `git diff --check` | 通过，Git 仅提示工作区 LF/CRLF 转换。 |

全量中的三个方法是 `StatusLedgerConsistencyTests.test_v1622_is_published_and_public_indexes_are_closed`、`test_v1624_is_published_with_frozen_product_and_single_receipts`、`test_v1625_is_published_with_frozen_product_and_single_success_receipts`。失败点均为当前 README 安装命令的 `chinese-official-writing@1.6.31` 字符串，未修改任何历史回执、历史版本或状态要求。最后仅回归该套件，没有第二次全量，也不表述为“827 项一次全绿”。

OpenClaw 保留平台所需 `category`，通用 quick_validate 拒绝该字段。对未改动公开 v1.6.31 基线按相同生成机制构建的 OpenClaw 包，运行同一命令得到完全相同的错误。平台专用边界检查通过；没有为了通用校验器去删除平台字段。

## 证据与限制

原日志集中在 `output/release-v1632-engineering/`：首轮定向失败、版本定向通过、唯一全量、账本定向通过及基线对照、静态基线案例、当前和基线 OpenClaw schema 结果均保留。`log-manifest.json` 记录各文件 SHA-256 与大小，供发布任务归档核验。

工程结果不替代真实稿质量评估，不证明所有宿主已经实际运行，也不代表市场上传、传播或审核完成。当前工程范围内没有待补测试；外部发布与用户可见状态由各平台回执验证。
