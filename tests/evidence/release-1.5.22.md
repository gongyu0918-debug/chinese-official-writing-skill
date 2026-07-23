# 1.5.22 发布证据

日期：2026-07-23

## 变更边界

1.5.22 以 `v1.5.21=9a98dac5f9475662cb5e4adb579828c8480c23e0` 为固定发行基线，只发布已经完成工程验证和真实 A/B 的入口与叶子原子减负：

- 将低频职责声明和 Word 交付细则移出常驻入口，完整规则保留在 README 与 `format-gbt9704.md`。
- 保留 AI 算力专项触发入口，把专项质量细则交给既有 `ai-compute-docs.md`。
- 去重占位符、Markdown 和二次事实映射的重复入口说明。
- 删除轻量任务路由卡中的弱模型测试优先级话语，保留 Markdown 清理、事实边界、要点和用户禁止项规则。

相对 1.5.21，canonical `SKILL.md` 由 10,631 个规范化字符降至 10,103 个，减少 528 个，约 4.97%。本版不修改信息选择、P0 边界、文种功能、用户模板、篇幅预算、脚本、Hook、FSM、输出模式、修改次数或回退链。

会议纪要新增叶子、审稿模式整体下沉、Word 叶子复合去重、proofreading 工具边界删减和 genre playbook 实现保证删减均未通过各自验收，已经完整撤回；失败证据保留，但不进入发行产品。

## 真实写作与验证边界

已保留原子的真实 A/B 覆盖报告、通知、纪要、Word 交付、AI 算力材料、占位符与 Markdown 清理、二次事实修改和轻量路由。汇总为 Candidate 11 胜、4 平、1 个孤立负例；唯一负例是情况说明末段重复复述，随后按用户授权用原题逐字复现两组，Candidate 2/2 胜且未再出现该问题，因此登记为采样波动。全部保留原子均未出现 Candidate 独有的事实、数字、日期、主体、状态、文种、格式、输出模式或 P0 硬回退。

该汇总按各原子既有证据计数，不把失败候选、工程消融或静态检查包装成真实写作胜场。精确任务、原稿哈希、匿名映射和判定见：

- `entry-specialty-relief-20260722.md`
- `entry-specialty-relief-ai-compute-20260722.md`
- `entry-duplicate-placeholder-relief-20260722.md`
- `entry-duplicate-markdown-relief-20260722.md`
- `entry-second-revision-dedup-preregister-20260723.md`
- `task-route-cards-runtime-noise-preregister-20260723.md`
- `reference-high-entropy-inventory-20260723.md`

## 发布前验证

固定基线为 `v1.5.21=9a98dac5f9475662cb5e4adb579828c8480c23e0`。发布准备工作树实际完成：

- `python -m unittest discover -s tests`：355/355 通过。
- `python -m unittest tests.test_skill_boundary`：52/52 通过。
- `python tools/run_real_prompt_ablation.py --baseline-root output/release-baselines/github-1.5.21-product --baseline-label v1.5.21 --current-root . --out output/release-1.5.22/deterministic`：固定基线 108/108，当前版本 108/108。
- `C:\Users\admin\AppData\Local\Programs\Python\Python313\python.exe evals\official-writing\run_eval.py --suite smoke --judge-batch-size 2`：20/20 通过，Skill 10 胜，judge consistency 1.0。
- `C:\Users\admin\AppData\Local\Programs\Python\Python313\python.exe C:\Users\admin\.codex\skills\.system\skill-creator\scripts\quick_validate.py chinese-official-writing`：`Skill is valid!`。
- `python -m unittest tests.test_skill_boundary.SkillBoundaryTests.test_primary_adapter_mirrors_match_canonical_bytes tests.test_skill_boundary.SkillBoundaryTests.test_packaged_resource_mirrors_match_canonical_bytes`：2/2 通过。
- `git diff --check`：通过。

ClawHub 与 skillhub.cn 清洁包均为 23 个文件，不含缓存、测试、研究产物及仅供 Codex Hook 使用的 `delivery-review-gate.md`、`gate_stop_hook.py`、`review_gate.py`。本地排序清单 fingerprint 分别为 `635f7c218a9b7811c6c4a91b446d0dcf50daf6869da845072a85d8f94014de98` 和 `bb75cbab54a2dfbea23f8b609eb186bcbd3d705077efea5f6dc7e86d355d2d1f`；平台打包 fingerprint 以 dry-run 和正式回执为准。

独立发布范围审计确认 6 组保留改动与证据一致，已撤回的格式、校对和 playbook 实验没有进入发行产品；README 徽章、发行证据和 AGENTS 状态段已在正式提交前补齐。两家商店 dry-run 待发布提交形成后使用实际 source commit 运行。

## 发布回执

待 GitHub、ClawHub 和 skillhub.cn 各完成一次提交后补录。小红书 Red SkillHub 继续排除；提交成功、公开 latest、审核和安全扫描分别记录，不互相推断。
