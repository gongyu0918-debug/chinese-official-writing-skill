# 1.5.21 发布证据

日期：2026-07-22

## 变更边界

1.5.21 以 `v1.5.20=025e500206b3140546f7789c6746996e170da8d9` 为固定功能基线，只纳入制度类专项路由：

- 新增制度、规定、办法、管理办法、实施细则和操作规程叶子，区分连续条文、章条结构、实施细则、操作规程以及“印发通知 + 附件”交付形态。
- 材料边界继续沿用 1.5.20；法律政策依据、职责权限、处罚、生效、解释和废止等事项仅按材料状态写入。
- 完整制度初稿形成后转读既有 `anti-ai-patterns.md`，只压缩不承载新规则的成簇解释性重复。

本版没有修改信息选择、P0 边界、其他文种路由、用户模板、篇幅预算、脚本、Hook、FSM、输出模式、修改次数或回退链。R2—R7 条文合并、叶子拆分和相邻条文门禁实验均未进入发行包。

## 真实写作与硬检查

制度叶验证覆盖管理办法、来访登记制度、印发通知与操作规程、实施细则和短篇规定。写手、硬核验员和匿名盲审相互独立；Candidate 与 1.5.20 使用同一自然语言原始任务，各取首个技术有效输出，不补抽。

- 首轮共性问题是“规则写完后再解释”。一次最小修复只增加成稿后转读既有 ANTI-AI 叶子，未增加替换表或文种特例。
- 修复后既有三题中，印发通知与操作规程一题 Candidate 胜；管理办法、来访登记制度两题仍由 1.5.20 小胜。
- 补测的实施细则和短篇规定两题均由 Candidate 小胜，Candidate 硬检查均为 PASS；实施细则的 1.5.20 对照出现两处材料外程序或职责扩张。
- 新增两题未见 Candidate 独有的事实、数字、日期、主体、职责、条件、状态、文种、篇幅、输出模式或 P0 回退。

这组证据支持制度文种覆盖和路由能力扩展，不宣称所有制度稿都比 1.5.20 更优。

## 发布前工程验证

发行工作树从实时 `origin/main=2d0edb99ff96c854ae208e1473832e6c9bad1f3f` 建立，仅迁移产品提交 `06b53a2`、`7b731b7`，再同步 1.5.21 版本面。实际结果：

- `python -m unittest discover -s tests`：353/353 通过；临时目录固定在发行工作树内。
- `python tools/run_real_prompt_ablation.py --baseline-root <v1.5.20> --baseline-label v1.5.20 --current-root . --out <out>`：v1.5.20 为 108/108，current 为 108/108。
- `python evals/official-writing/run_eval.py --suite smoke --judge-batch-size 2`：沙箱内 Node 无法启动已存在的 Python，20 项均未进入产品逻辑；显式使用系统 Python 并在沙箱外按原条件复跑后为 20/20 通过、0 failed、0 errors，Skill 10/10，judge consistency 1.0。
- `python <skill-creator>/scripts/quick_validate.py chinese-official-writing`：`Skill is valid!`。
- `python -m unittest tests.test_skill_boundary`：50/50 通过。
- `python tools/sync_adapters.py`：canonical 与五套发行镜像同步完成；`git diff --check` 通过。
- canonical 和 OpenClaw 发行目录的忽略文件检查为空；两个 23 文件清洁包的相对路径完全一致，排除平台 frontmatter 后共享文件 SHA-256 mismatch 为 0，缓存、研究输出和 R7 门禁文件均为 0。
- ClawHub dry-run：`status=would-publish`、目标版本 1.5.21、最新公开版本 1.5.20、23 个文件、fingerprint `0a37eb753bbd32053114c9314e2bc869d11ebc7bf87e07c6e6229b381b59068a`。
- skillhub.cn dry-run：目标 `chinese-official-writing@1.5.21`，23 个文件；临时包只补平台要求的 `slug`、`displayName`。

Promptfoo 前两次 20 errors 均由 Windows 沙箱拒绝 Node 启动 Python 引起，不计为产品失败，也不写成通过；只采用沙箱外有效复跑结果。

发布回执补录后，README 将实际单测总数由 352 更新为 353，静态测试仍期待旧值并出现 1/50 失败。该问题只涉及证据断言，不涉及技能包；测试期望同步为 353 后，全量 353/353 再次通过。发行 tag 保持不动，发布后主线只追加回执与该验证夹具修正。

## 已知边界

- 五份制度类 Candidate 稿均出现不同程度的短条偏多，四份出现职责或程序重复解释；现有删除条文粒度保护和自动相邻条文合并方案分别出现硬回退或没有收益，本版不纳入。
- 材料外职责或条件在两份既有稿中出现，未达到三个正常场景的共性阈值；继续保留人工签发复核。
- DOCX 已核验 OOXML、A4、页边距、字体字号、章条层级、页码字段和通知附件关系；本机缺少 LibreOffice/`soffice`，逐页分页、孤行和字体替代效果为 `unavailable`。
- 本次真实写稿是制度类定向样本，不替代全量文种、跨模型和 3000 字以上长文矩阵。

## 发布回执

- GitHub：`main` 已快进到发布提交 `9a98dac5f9475662cb5e4adb579828c8480c23e0`；annotated tag object 为 `761d7fb68482498399a155768f5945560c99b9c7`，解引用提交为发布提交；[v1.5.21 Release](https://github.com/gongyu0918-debug/chinese-official-writing-skill/releases/tag/v1.5.21) 已公开并设为 Latest。
- ClawHub：使用 23 文件清洁目录正式提交一次，返回 `status=published`、`versionId=k9707pnea6z33nnyk1m00dg3sd8b0jr9`、fingerprint `0a37eb753bbd32053114c9314e2bc869d11ebc7bf87e07c6e6229b381b59068a`。首次公开查询仍为 `latestVersion=1.5.20`，精确查询 1.5.21 暂时返回 `Version not found`；公开 moderation 为 clean，但对应仍公开的 1.5.20，不推断 1.5.21 已完成扫描，也不重复提交。
- skillhub.cn：向既有 `skillId=70149` 正式提交一次，返回 `ok=true`、`versionId=153125`、23 文件、fingerprint `0a0261f1e19d17cbc746fcc5c919f2d3d6bd913e2f7068b91e47081589296b47`、`tags.latest=1.5.21`；`reviewStatus`、`securityScanStatus` 和 `contentAuditStatus` 均为 pending。首次公开详情仍显示 1.5.20，按异步审核和传播处理，不重复提交。

小红书 Red SkillHub 继续排除。提交成功、公开 latest、审核和安全扫描分别记录，不互相推断。
