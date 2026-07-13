# 1.5.10 纯公文边界恢复与发布记录

日期：2026-07-13

## 发布范围

- 以 `v1.5.9=a2e489658988f404a6ea5a627eda165da89e9a86` 为上一发行版，以 `e11159802fb90e9b21a00cfa0afc1a824a1ff705` 为拆分后的纯公文对照基线。
- 恢复完整公文入口和 15 份公文 reference；普通论文、开题报告、独立文献综述已迁出本仓库发行包。
- 保持原有任务模式、文种路由、办理要素、由大至小成文、由小至大复核、渐进加载、输出模式、默认联网和回退方式不变。
- 只实施三处逐句修订：稀疏材料不补固定章节；初步意见不升级为虚构研究结论；字段式底稿默认保留结构，只有明确要求成篇时才组织为连贯自然段。
- 未新增生成器、finalizer、检测器、硬清洗、默认多 Agent、默认联网、排版引擎或论文路由。

## 基线消融与真实 A/B

- 对比纯公文基线 `e111598`：确定性消融 baseline 101/106，current 106/106；基线只在本轮新增或改写的 P091、P096、P105、P106、P107 支撑项失败。
- 对比上一发行版 `v1.5.9`：确定性消融 baseline 60/106，current 106/106。该工具不调用 LLM，只作工程支撑证据。
- 逐句匿名 A/B 第一轮中，S1 持平、S2 候选更好；S3 成篇正文虽均通过，但候选略有字段转述痕迹，因此追加一句内收紧并重测。
- S3 第二轮中，字段保留和成篇正文两项均由独立 verifier 判候选更好；未观察到事实、结构或输出模式回退。
- 发布级三名 writer 完成 6 个未见任务，覆盖请示、通知、正式化改稿、只审不改、限字压缩和论文排除路由；独立 verifier 判 6/6 PASS，无发布阻断。精确模型 ID 无法核验，只记独立真实写稿 sanity。

## 工程验证

- `py -3 -B -m unittest discover -s tests -v`：143/143 通过。沙箱内临时目录清理被 Windows 权限拒绝，沙箱外原命令通过，未出现断言失败。
- `py -3 -B evals\official-writing\run_eval.py --suite smoke --judge-batch-size 2`：沙箱外 20/20 通过，0 fail/error，skill 10 胜，judge consistency 1.0。沙箱内三次均因 Node 子进程不能访问 Python 而产生20项启动错误，未计作质量结果。
- `py -3 -B tools\run_real_article_eval.py --out output\release-1.5.10\real-article-eval`：skill 路径 10 个样本关键要素 61/61、关键词命中率100%、格式/重复/反 AI 风险为0；匿名占位标签风险仍只作人工线索。
- `py -3 -B C:\Users\admin\.codex\skills\.system\skill-creator\scripts\quick_validate.py chinese-official-writing`：`Skill is valid!`。
- 完整评测数据27批最大上下文 `24789`，低于仓库 `<25000` 门槛。
- `git diff --check`：通过，仅有 Windows 行尾转换提示。
- 第5次提交门槛前复跑：完整单测仍为143/143通过，Promptfoo smoke仍为20/20通过；纯公文基线消融仍为101/106对106/106，1.5.9基线消融仍为60/106对106/106，未出现新增回退。

## 发行包预检

- canonical 按 `git ls-files chinese-official-writing` 白名单为18个文件。
- ClawHub 源为19个文件，即 canonical 加市场 README。
- skillhub.cn 临时包 `output/skillhub-release-1.5.10/publish-package` 为19个文件。
- 发布前曾验证 Red 历史副本为18个文件，且与 SkillHub 包的共用文件相对路径缺失0、额外0、SHA-256 mismatch 0；自本次发布收尾起，Red 已退出后续发布和一致性门禁。
- 四个发行面中的论文专项文件为0；三个可上传目录中的 `.pyc` 和 `__pycache__` 为0。

## 发布状态

- GitHub：`origin/main` 和 `v1.5.10` 均指向发布提交 `7e5fec70ba78ad6d1c4b4ae34952697b4794c03e`；Release 已公开：`https://github.com/gongyu0918-debug/chinese-official-writing-skill/releases/tag/v1.5.10`。
- ClawHub：1.5.10 已发布，`versionId=k974c72ypn50rpd6s43zff7mn58afjd8`，19个文件，fingerprint `617315ce6fff6800c7a3b3f96978207234f6192c6cab037124a8b1ed16687c30`；`latest` 和5个正确标签均指向1.5.10。总体 moderation 为 clean，但版本级扫描仍为 pending，`legacyReason=pending.scan`。
- ClawHub 隔离安装：使用 `--version 1.5.10 --force-install` 安装成功；排除平台生成的 `_meta.json` 和 `.clawhub/origin.json` 后，19个正文文件与发布源相比缺失0、额外0、SHA-256 mismatch 0。
- skillhub.cn：1.5.10 已提交到 `skillId=70149`，`versionId=136272`，19个文件，fingerprint `9ac3e4c0a347830db58ea178e0223bf142d20206a25486d13f3ae49afde5914c`，回执 `tags.latest=1.5.10`；公开搜索索引已切换到1.5.10并显示纯公文边界说明，三项审核状态仍为 pending。
- 小红书 Red SkillHub：1.5.10 dry-run 曾通过，真实上传达到100后被服务端以“Skill ID 已被占用”拒绝，没有 submitted 回执，故未发布。用户随后明确决定停止该发布面；后续不再执行 Red 的发布、更新、dry-run、登录续期、标签查询或冲突处理。
