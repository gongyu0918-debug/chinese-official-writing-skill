# 中文公文写作 1.5.14 发布证据

## 发行范围

- 上一发行基线为 annotated tag `v1.5.13`，解引用提交 `cd2d46c58a5f56b9009c5da08626a88640f2e5b3`。
- 1.5.14 纳入 `f4d79ceeed4f2ae78f8a2522f22f709d63b6056c` 的渐进式路由最小仲裁修复，以及 `b70c7b9e2cf3bccee897514b1bed43c630baee20` 的发布级真实写稿回归证据。
- 产品规则变化只涉及 canonical `SKILL.md` 和 `references/task-route-cards.md` 及五组发行镜像：先判创作、修改、只审不改等输出模式；轻量任务卡完整覆盖材料稀疏说明/通报/报告、未决事项会议纪要、短通知/限字通知和二次局部修改时停止继续加载；已经形成决定、议定事项、结论、一致意见、责任分工或期限，或者用户要求完整正式会议纪要时，进入会议纪要 playbook。
- 未改变事实边界、文种规则、三级复核顺序、输出模式定义、修改次数、默认联网和发布链；未新增脚本硬门禁、自动替换、finalizer、detector、repair 或批量清洗。
- 小红书 Red SkillHub 继续排除；未同步 `redskill/`，不调用 Red CLI、dry-run、登录、标签查询或上传。

## 冷审核与真实写稿回归

- 1.5.13 冷审核只作问题线索和固定基线证据；本版修改以源码复现、确定性测试和重新执行的真实写稿 A/B 为准，没有复用旧实现路径。
- 针对性路由 A/B 覆盖 4 个任务、2 名 writer、16 份成稿；独立盲审为 16/16 PASS，current 8 份成稿均正确命中轻量卡或会议纪要 playbook，未出现事实、文种、格式或输出模式回退。
- 发布级功能回归使用 15 个真实用户式 prompt、2 名反向映射 writer，固定 `v1.5.13` 与 current 共生成 60 份成稿；两名独立 verifier 只看原 prompt 和匿名稿件。
- 综合盲审两版均为 29 PASS、1 对称 WARN、0 FAIL；硬边界盲审两版均为 30 PASS、0 WARN、0 FAIL。对称 WARN 是一名 writer 在两版的同一未决纪要样本中都未显式复述“尚未形成决定、责任和期限”，但均保持建议、观察和再次评估的未决口径。
- 未发现 current 独有的事实编造、状态升级、文种混写、格式破坏、只审不改失效、正文外说明回流、局部修改越界、旧稿事实回流、普通采购误入 AI 算力或 AI 算力参数补造。

## 发布前验证

- `python -B -m unittest discover -s tests -v`：174/174 OK。
- `python -B tools/run_real_prompt_ablation.py --baseline-root output/release-baselines/github-1.5.13-cold-audit --baseline-label baseline-1.5.13 --current-root . --out output/release-1.5.14/real-prompt-vs-1.5.13`：baseline 108/108，current 108/108。该工具不调用 LLM，只作确定性支撑。
- `$env:PROMPTFOO_PYTHON='C:\Users\admin\AppData\Local\Programs\Python\Python313\python.exe'; npm run eval:official-writing:smoke`：20/20 PASS，0 failed，0 errors；skill 10 胜，judge consistency 1.0。
- `python -B tools/run_real_article_eval.py --out output/release-1.5.14/real-article`：skill 10 个样本缺失要素 0/61、关键词命中率 100%，格式风险、重复事项和反 AI 风险均为 0；9 个匿名占位标签样本仍只作人工线索。
- `python -B C:\Users\admin\.codex\skills\.system\skill-creator\scripts\quick_validate.py chinese-official-writing`：`Skill is valid!`。
- `python -B tools/sync_adapters.py`：在允许写入受保护适配目录后完成 canonical、共享目录、`.agents`、`.qwen`、Hermes、OpenClaw、README、skill card 和 Claude 插件清单同步。首次沙箱内尝试在 `.agents` 权限处失败，不计为通过；重跑成功后，发行版本面不再残留 1.5.13。

## 发行包预检

- ClawHub 发行目录为 19 个文件，违规缓存、finalizer、detector、repair 文件为 0；平台 `SKILL.md` 正文与 canonical 正文一致，包内许可为 MIT-0。
- skillhub.cn 临时包以 `git ls-files chinese-official-writing` 的 18 个跟踪文件为白名单构造，再加入 `_meta.json`，共 19 个文件；没有递归带入 canonical 目录下被 Git 忽略的 Python 缓存。
- skillhub.cn 包的 17 个非 `SKILL.md` 共享文件与 canonical 逐文件 SHA-256 一致，平台专用 `SKILL.md` 正文与 canonical 正文一致；`slug=chinese-official-writing`、`version=1.5.14`、`license=MIT-0`。
- skillhub.cn CLI dry-run 返回 `{"dryRun": true, "slug": "chinese-official-writing", "version": "1.5.14"}`。
- GitHub 仓库许可继续为 MIT；ClawHub 和 skillhub.cn 包继续维持 MIT-0，不追溯改写历史版本。

## 发布状态

- GitHub：annotated tag `v1.5.14` 解引用到发布提交 `fea1fae4b0c809d3e2b7167d959a3822030b6033`，远端 `main` 首次发布时与该提交一致；公开 Release 为 `https://github.com/gongyu0918-debug/chinese-official-writing-skill/releases/tag/v1.5.14`，不是 draft 或 prerelease。发布回执记录提交可使 `origin/main` 在 tag 之后继续前进，但不得移动发布 tag。
- ClawHub：使用最终发布提交作为显式 `source-commit` 的 dry-run 返回 `status=would-publish`、`version=1.5.14`、`fileCount=19`、fingerprint `eae11169981bff3f142910a0503421e9b1e131230252df959e9642ce71902b99`。正式命令正常结束但未打印发布回执；未重复提交，随后只读 inspect 已确认公开 `latestVersion.version`、`tags.latest` 及五个正确 tag 均为 1.5.14，19 个上传文件齐全，moderation 总体 clean。隔离安装成功，19 个发行文件逐文件 SHA-256 一致，只多平台生成的 `_meta.json` 和 `.clawhub/origin.json`。复核时版本安全对象、VirusTotal 和 SkillSpector 均已 clean；`skill verify` 只因平台 card 尚未生成而以 `card.missing` 返回 fail。verify 同时显示 `provenance.source=unavailable`，因此不能宣称 ClawHub 已存储或解析 GitHub source commit。
- skillhub.cn：精确 slug `chinese-official-writing` 已一次提交成功，回执为 `skillId=70149`、`versionId=138838`、19 个文件、fingerprint `52be400012652828d7efbe43d0df3940b3171aba92056e7407c94d8b4e85b50e`、`tags.latest=1.5.14`；以下为发布完成时快照：`reviewStatus`、`securityScanStatus`、`contentAuditStatus` 均为 pending，owner dashboard 已显示 1.5.14，图标审核 passed，但 `latestApprovedVersion`、公开搜索和安装入口仍为 1.5.13，Keen、Sanbu 均为 queued。后续只继续轮询，不重复提交，不把旧索引安装结果写成本版安装证据；2026-07-16 已另行确认公开详情、搜索和隔离安装均切到 1.5.14，Keen、Sanbu 均为 benign。

## 发布后 GitHub 首页与授权整理

- 本次整理继续使用 1.5.14 版本号，只推进 GitHub `main`，不移动 `v1.5.14` tag，不重新提交 ClawHub 或 skillhub.cn。
- README 保留并前置总介绍、核心能力和适用范围，新增通俗工作流、渐进式路由、轻量审查层和 Markdown-first 实现说明。安装区收束为商店入口、一条通用安装命令和手动入口说明；平台目录映射归入原有目录结构表。
- README 删除内部 unittest、Promptfoo、同步、发布和复跑命令，只展示经证据文件支撑的模型消融、真实写稿摘要及同题独立样稿节选。文末只保留一个“规范与参考”区，社区来源只列 1.5.14 当前仍能定位的借鉴点。
- 早期 270 任务测试在仓库内只称脱敏聚合摘要；路由 A/B 同时披露内容 16/16、路由 14/16 和 1.5.14 current 8/8；同题节选明确为不同独立上下文、非同一随机 seed，并记录无 Skill 样稿未进入候选/基线双盲排序以及带 Skill S2 的保护性说明 WARN。
- 根仓库继续以 MIT 展示；可直接安装的 canonical、通用 Agent、`.agents`、Qwen Code、Hermes、OpenClaw 包和 Claude plugin 元数据统一声明 MIT-0，完整条款见根目录 `LICENSE-SKILL`。测试、评测、工具、证据、迭代和维护材料继续使用 MIT。
- 相对 `v1.5.14`，canonical `SKILL.md` 可执行正文的归一化 SHA-256 前后均为 `1350d1a6ee69dab3d43f5527d574a43cbdfe8ad6cb1f02ea5a7dd30cb836699c`；canonical `references/`、`scripts/`，OpenClaw/ClawHub 与 skillhub.cn 介绍文件及 `redskill/` 均无内容 diff。各平台 `SKILL.md` 只调整许可元数据，写作 description、路由、事实边界、输出模式和复核流程保持 1.5.14 发布状态。
- `python -B -m unittest discover -s tests -v`：174/174 OK。
- `python -B C:\Users\admin\.codex\skills\.system\skill-creator\scripts\quick_validate.py chinese-official-writing`：`Skill is valid!`。
- 本次没有重新生成写稿样本。原因是写作正文、references 和运行脚本未变；功能性写稿回归继续引用发布 1.5.14 前完成的 60 份真实成稿和独立 verifier 结论，本次用正文哈希、相对 `v1.5.14` 的无 diff 证明及最小 smoke 确认没有引入新的写稿路径。

## 剩余风险与停止条件

- 真实写稿结论覆盖 15 个短稿/改稿场景，不等同 current 全 29 文种、3000 字以上长文、多附件合稿、多轮 compact 或 Word 版式矩阵；本版不扩大相关能力承诺。
- 评测 provider 仍会对 F01 否定式“不得补写会议决定”保守多读会议纪要 playbook，并会因 F14 会议名称中的“论证会”多读 argument reference；两项均未造成 60 份正文中的用户可见回退。继续扩张否定正则可能吞掉同句后半的真实责任和期限，因此本版记录但不做一例一修。
- 发布完成时，ClawHub 的 card、skillhub.cn 的审核、公开索引和安装入口仍为异步状态；提交成功与公开审核完成分开表述，只轮询，不重复发布。2026-07-16 的后续只读核对已确认 skillhub.cn 公开详情、搜索和隔离安装均切到 1.5.14，Keen、Sanbu 均为 benign。
- 任一 current 独有的事实、文种、格式或输出模式回退，任一 19 文件清单不闭合，ClawHub 如返回可解析 source commit 且不等于发布 tag 解引用提交，或 skillhub.cn 返回的 `skillId` 不是 70149，立即停止后续发布并核查，不自动重试。
