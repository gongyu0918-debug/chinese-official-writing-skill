# 中文公文写作 1.5.11 发布证据

日期：2026-07-13

## 范围

1.5.11 固定上一发行基线为 `v1.5.10=7e5fec70ba78ad6d1c4b4ae34952697b4794c03e`，包含两项小范围修复：

1. `0686ea3770b14a36dc560221c21d33e03daf9447`：共性检查成品正文中的制作版本、内部受众、只读核对、校验门禁、审核状态、重复解释、小字结论、制作/免责/边界/方法自述和重复标题；不扫描正文外审稿意见，不删除用户明确要求显示的标签或材料业务事实。
2. ANTI-AI Prompt 层语义复核：频次和词形只作定位线索，由模型通读确认无前文依据的否定、虚假对比和机械重复；只改确认有问题的局部。事实、引用、术语、否定范围和论断强度保持不变，真实比较、制度政策、职责边界、直接引语和必要术语重复保留。

没有新增自动替换表、finalizer、默认 lint 阻断、默认联网、默认多 Agent、写稿阶段或 reference 预加载。任务路由、段落/小节/全文复核顺序、输出模式、修改次数、回滚方式和三平台发布链不变。

## 社区最小借鉴

发布前只核对社区方案的检查维度，未复制代码、正则、Prompt 或替换表：

- [`jpeggdev/humanize-writing`](https://github.com/jpeggdev/humanize-writing)：只借鉴连接组织和重复线索按成簇观察的思路。
- [`blader/humanizer`](https://github.com/blader/humanizer)：只借鉴不要因孤立常用连接词直接判错的边界。
- [`brandonwise/humanizer`](https://github.com/brandonwise/humanizer)：只借鉴按密度发现候选位置的思路，拒绝自动修复、打分和固定替换。

本仓库落地为 Prompt 语义判断与局部改写，明确拒绝检测规避、口语化注入、第一人称“人味化”、自动替换和固定次数硬门槛。

## 确定性与工程验证

- `py -3 -B -m unittest discover -s tests -v`：151/151 PASS。
- `py -3 -B tools\run_real_prompt_ablation.py --baseline-root output\release-baselines\github-1.5.10 --baseline-label baseline-1.5.10 --current-root . --out output\real-prompt-vs-1.5.10-release-1.5.11-r3`：baseline 106/108，current 108/108；baseline 只在新增 P108、P109 失败。
- `npm run eval:official-writing:smoke`：20/20 PASS，skill 10 wins，0 fail/error，judge consistency 1.0。
- `py -3 -B tools\run_real_article_eval.py --out output\real-article-release-1.5.11-final`：skill 61/61 必要点，差异率 0，格式风险 0，重复事项 0，反 AI 风险 0；占位词风险仍只作人工复核线索。
- `py -3 -B C:\Users\admin\.codex\skills\.system\skill-creator\scripts\quick_validate.py chinese-official-writing`：`Skill is valid!`。
- 完整评测 27 批 `MAX_CONTEXT=24968`，低于仓库 `<25000` 门槛，余量 32 字符。
- `git diff --check`：PASS，仅有 Windows LF/CRLF 提示。
- canonical、Codex、Qwen、Hermes、OpenClaw 和共享入口镜像一致性测试通过。

确定性消融和 Promptfoo stub 只证明工程支撑，不作为真实写作质量证明。

## 真实写作、A/B 与 cold review

原始 prompt、输出、匿名判定和揭盲结果见 `tests/evidence/real-writing-1.5.11-anti-ai.md`。

- 首轮 ANTI-AI A/B 暴露一个格式 WARN 和一处不必要同义改写，候选未直接发布。
- 收紧后的首轮双 writer 复测为 3 PASS、1 WARN；WARN 为漏写“检索模块仍在本地”，已如实降级并触发完整 S2 二次复测，不以该轮宣称通过。
- 完整 S2 二次复测由两名 current writer 独立运行，均逐字保留真实比较、审校/检索模块、12 个月及 180/120 万元，verifier 判 2/2 PASS，前述 blocker 解阻。
- 较长上下文样本同时覆盖真实比较、制度引语、职责边界、必要术语重复、未决强度和机械句式；verifier 判 current PASS、1.5.10 WARN，优先 current。
- 六组其他功能回归中，current 与 1.5.10 均为 4 PASS、2 WARN、0 FAIL；无事实编造、文种错位、否定范围破坏或输出模式硬失败。
- 最终源码 cold review 发现的新旧默认审稿字段冲突已修复：用户指定格式时严格服从；未指定时恢复既有“位置、风险层级、修改建议”。
- 未使用 MiniMax；子上下文无法返回可核验的精确模型 ID，因此不宣称完成指定模型矩阵。

## 发行包与发布状态

- ClawHub 最终 dry-run：`slug=chinese-official-writing`、`version=1.5.11`、19 个文件、无缓存、fingerprint `ebb3faa433bdd453b08d69ce70962ee93e0ea03ba483e39cad64e75424ea6d75`；正式发布时需带 release commit source metadata。
- skillhub.cn dry-run：`slug=chinese-official-writing`、`version=1.5.11`；临时包 19 个文件、17 个 Git 跟踪共享文件 SHA-256 一致、无 `.pyc` 或 `__pycache__`。
- GitHub、ClawHub 和 skillhub.cn 尚未正式发布；正式回执、release commit、tag、versionId、fingerprint、审核状态和安装 smoke 在发布后补录。
- 小红书 Red SkillHub 明确排除，未调用 Red CLI、dry-run、登录或上传。

## 剩余风险与回退

- 上下文预算只剩 32 字符；1.5.11 不再增加运行时入口 Prompt。后续新增内容优先放叶子 reference，并重新统计全部 27 批。
- 静态 `prose_lint.py` 仍会把单个二元句式列为 medium 风险提示，这是旧行为；它不自动改写，模型仍须按本轮语义边界判断。
- 真实写作样本规模有限，不能证明统计显著性、所有弱模型稳定性或长文全覆盖。
- 若发布后安装包与 release commit 不一致、任何旧硬边界回退或平台 latest 未切换，停止继续推送并回退到 `v1.5.10`。
