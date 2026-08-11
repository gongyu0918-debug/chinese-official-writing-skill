# 中文公文写作 1.5.16 紧急发布证据

## 发布目标

1.5.16 处理线上反馈最集中的保护性外扩：正文围绕材料未谈到的外围事项反复写“尚未、不能据此、不足以说明”，或者把实质缺口扩成材料外核实程序、责任和未来承诺。紧急版的目标是让日常正常材料明显减少这类整稿级风险，同时保持 1.5.15 的事实、文种、格式、输出模式和长文能力。

它是一版可用性修复，不宣称覆盖所有特殊材料，也不以三个任务推导 80%—90% 的统计胜率。材料本身无法完成用户点名章节、稀疏材料强行扩成长稿等问题进入 1.6.x 研究范围。

## 基线与组成

- 发布后文档基点：`5258929786c85613fc8baf2a88994c969eab2803`。
- 固定功能基线：`cd0772fcd763eaa34bb32361c2f8d2cdee39a291`（1.5.15）。
- Candidate V 预注册源提交：`946c8087a34fae047a786aa526628fc096269b6e`，发布分支移植提交 `ac86b91`。
- Candidate V 产品源提交：`f72e4e5d2184c35aaba1e867ec60200b20e691a1`，发布分支移植提交 `54ab4ce`。
- 纠正 A/B 与一次局修证据源提交：`e0582e365fe141b2f24b550836012ea04a87dee6`，发布分支移植提交 `8a144ab`。
- 版本面提交：`ec5a039`。

产品改动集中在信息选择规则归属：`SKILL.md` 只保留总纲，新增 `references/information-selection.md` 作为唯一展开处，多个 reference 删除同义复述并保留文种或专项规则。任务路由、输出模式、用户模板、事实锚、长文提纲与篇幅预算、多轮改稿、Word 交付和三级复核沿用 1.5.15。Candidate Q/S/W 的 detector、review gate、FSM、正则和段内公式均未进入发布分支。

## 真实 A/B 裁决

三题均使用 `gpt-5.6-sol`、`ultra`，Candidate V 与 1.5.15 接收逐字一致的原始输入，各取首个技术有效输出。完整记录见 [`candidate-v-real-ab-result-20260717.md`](candidate-v-real-ab-result-20260717.md)。

- P-B1：Candidate V 保留材料内进度，把材料没有提供的具体原因和整改措施列为实质缺口；1.5.15 新增了 5 项核实程序或未来承诺。纠正盲审判 Candidate V 胜。该材料无法直接支撑用户点名的两个章节，因此只用于说明材料外程序风险，不用作日常成稿能力门槛。
- P-CN：两版均完整保留故障时段、恢复时间、影响、线下受理 217 件和原因排查状态，保护性外扩均为 0。Candidate V 的标题和落款未显式呈现发文机关，记为单样本 G1 观察项。
- T01：Candidate V 和 1.5.15 均有保护性解释，Candidate V 避免了 1.5.15 新增的研究时间点和决策依据，纠正盲审判 Candidate V 小胜。唯一一次 D1 清除了目标 P0，但出现较多数据折算和同义复述，因此 D1 不进入产品默认输出；稀疏长稿继续在 1.6.x 拆分验证。

紧急版裁决以日常材料可用性为准：Candidate V 对两题的高优先级材料外程序风险均有下降，正常故障报告没有事实、状态、文种、格式或输出模式回退。单样本标题呈现和稀疏长稿观感作为已知风险公开保留。

## 工程验证

在 `output/release-worktrees/release-1.5.16-candidate-v` 实际运行：

- `python -B -m unittest discover -s tests`：176/176 通过。
- `python -B tools/run_real_prompt_ablation.py --baseline-root F:\Workspaces\chinese-official-writing-skill\output\release-baselines\github-1.5.15-candidate-k --baseline-label baseline-1.5.15 --current-root . --out output\release-1.5.16-deterministic-vs-1.5.15`：baseline 108/108，current 108/108。该工具不调用 LLM，只证明确定性支撑未回退。
- `python -B tools/run_real_prompt_ablation.py --baseline-root F:\Workspaces\chinese-official-writing-skill\output\research-worktrees\candidate-v-low-density-info-selection-1.6 --baseline-label candidate-v-f72e4e5 --current-root . --out output\release-1.5.16-deterministic-vs-candidate-v`：Candidate V 产品与最终发布候选均为 108/108，说明版本面、README 和证据提交没有改变产品行为。
- `python -B -m unittest tests.test_skill_boundary tests.test_real_prompt_ablation`：55/55 通过。
- `python -B evals\official-writing\run_eval.py --suite smoke --judge-batch-size 2`：20/20 通过，judge 10/10 选择 skill，重复评审一致率 1.0。
- `python -B tools/run_real_article_eval.py --out output\real-article-release-1.5.16`：Skill 路径 10 个公开样文的缺失要素 0/61、关键词命中 61/61；9 个匿名占位词风险样本继续作为人工复核提示，不把该确定性结果当作真实写作质量评分。
- `python -B C:\Users\admin\.codex\skills\.system\skill-creator\scripts\quick_validate.py chinese-official-writing`：`Skill is valid!`。
- `python -B tools\sync_adapters.py`：完成 canonical、共享目录、`.agents`、`.qwen`、Hermes、OpenClaw、README、skill card 和 Claude plugin 的镜像同步；脚本重写的 12 个文件与已提交内容 blob 一致，没有新增内容差异。
- `git diff --check`：通过。

第一次在受限沙箱中执行 unittest 时，`TemporaryDirectory` 清理返回 `WinError 5`；外层权限同命令通过。Promptfoo 首次在沙箱中因 Node 无法启动已存在的 Python 返回 20 个环境错误；指定系统 Python 并在外层权限复跑后 20/20 通过。两项均按环境噪声记录，没有写成产品失败。

## README 与版本面

- canonical、共享目录、`.agents`、`.qwen`、Hermes、OpenClaw、Claude plugin、skill card、同步常量和公开当前版本均为 1.5.16。
- README 保留既有对外结构和同题独立写作节选，只更新版本面并增加本证据入口。
- 展示的 1.5.15 带 Skill 成稿片段停在会议已形成的期限和责任分工，未出现“未形成决定、尚未确定、不能据此”等保护性外扩。原始 Prompt 中的未决状态属于来源事实，不按成稿 P0 计。

## 剩余风险与后续研究

- 材料无法支撑明确章节时，首稿可能短写或在文后列实质缺口。
- 单样本出现发文机关在标题和落款中未显式呈现。
- 稀疏长稿可能残留保护性解释；一次局部删减也可能转为数据折算和同义复述。
- 当前 lint 只能提供表面线索，语义关联和观感仍由 Agent 或人工判断。

这些风险不扩写成 1.5.16 的新 Prompt，也不引入默认硬门禁。Candidate H 的段内公式变量、Candidate W 的检测与一次局修变量继续在 1.6.x 独立验证。

## 发布状态

- GitHub：`main` 已快进到发布提交 `172d1140905e38ce16ab6a16e89d9cb50248285e`；annotated tag `v1.5.16` 的 tag object 为 `d24b1a42434b3048e263343a45c730df94748a33`，解引用提交与发布提交一致。Latest Release 为 `https://github.com/gongyu0918-debug/chinese-official-writing-skill/releases/tag/v1.5.16`，`draft=false`、`prerelease=false`。首次创建 Release 时 GitHub API 读取 latest 超时；确认 Release 尚不存在后只重试创建操作，未重复推送 main 或 tag。
- ClawHub：dry-run 与正式提交的 20 文件 fingerprint 均为 `b0aac7188804f04a17f6c945f038dd0746d2441edfb1672014fdb58186cbcacf`。正式提交只执行一次，返回 `status=published`、`versionId=k971781h9nhev0ty8ynw2t4xqn8aqee5`、`fileCount=20`。首次发布后只读检查仍显示公开 1.5.15，查询 1.5.16 返回异步传播中的 `Version not found`；不重复提交，待公开切换后再做隔离安装和 20 文件哈希闭环。
- skillhub.cn：dry-run 返回精确 slug `chinese-official-writing` 和版本 1.5.16。正式提交只执行一次，回执为 `skillId=70149`、`versionId=141943`、20 个文件、fingerprint `db89678dbfbcba502e15cc080e9a00cae36ec16fadc378a150371d3ca5ddcfb4`、`tags.latest=1.5.16`；提交时 review、security scan、content audit 均为 pending。2026-07-17 只读复核显示公开 `latestVersion=1.5.16`，Keen、Sanbu 仍为 queued；公开切换不替代内部审核字段，也不触发重复提交。
- 小红书 Red SkillHub 未调用。ClawHub 与 skillhub.cn 的公开切换、扫描与隔离安装哈希在异步完成后补记；pending、`Version not found` 或公开索引暂未切换均不触发重复发布。
