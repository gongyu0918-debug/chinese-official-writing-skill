# Word Markdown 清理句原子减载预注册

## 背景

- 固定基线：`cde03cca2a36bc124d0c5b4420c8f89ebcfad5de`。
- 隔离分支：`codex/1.5.28-candidate-word-markdown-check-relief-v1527`。
- 历史候选 `candidate-word-review-relief-v1526` 一次删除四条 Word 专项复核细则，真实 A/B 一胜一负并出现保护性外扩，已判 `FAIL`。

本候选不复活四条整体迁移，只验证其中与上轮负项机制无关、且存在双重近场锚点的一小句。

## 单变量

1. 只修改 `review-checklist.md` 第 98 行同一条目：
   - 删除“正式 Word 输出前是否已清除 Markdown `**`、代码块和 `###` 标题标记”这一重复半句；
   - 保留“文号、密级、签发人、印章是否未被编造”。
2. Markdown 清理能力继续由同一文件第 13 行的通用交付检查，以及 `format-gbt9704.md` 第 27 行的 Word 近场检查承载。
3. 上轮整体迁移涉及的正式交付核对卡、正式要素范围和点名缺项短列三条全部原样保留。
4. 不修改 `SKILL.md`、路由、reference 加载条件、复核顺序、输出模式、事实边界、脚本、Hook、FSM、修改次数、回退或发布链。
5. canonical 与发行镜像同步，只更新确定性单一来源断言。

## 工程验证

1. Word 与 review 定向边界测试。
2. `python -m unittest discover -s tests`。
3. Promptfoo smoke。
4. 固定 `cde03cc` 确定性消融。
5. Skill Creator `quick_validate.py`。
6. 镜像一致性与 `git diff --check`。

## 真实 A/B

最多两题四稿，同模型、同 thinking、逐字一致原始输入，各臂只取首个技术有效输出：

- WM01：正式请示 Word 只审不改，正文含 Markdown 标题与加粗，同时缺文号、签发人和版记。
- WM02：会议纪要 Word 只审不改，正文含 Markdown 标题与代码块，同时需要核验材料已给的议定事项、责任单位和期限。

两臂均须自然读取 `review-checklist.md` 与 `format-gbt9704.md`。writer、hard verifier 和匿名 judge 相互独立；先检查 Markdown、文号、签发人、版记、议定事项、责任和期限，再比较遗漏、保护性外扩和直接修改成本。

## 验收

- 两题均无 Candidate 独有的事实、主体、状态、文种、格式、输出模式或 P0 回退。
- Candidate 两题均不劣于 Baseline；出现一题 Baseline 明确胜出即 `FAIL`。
- 只有读取链对称且两题至少持平，才说明这条重复半句具备迁移资格。
- 不因单题措辞差异追加 Prompt，不补抽，不改版本号，不发布。
