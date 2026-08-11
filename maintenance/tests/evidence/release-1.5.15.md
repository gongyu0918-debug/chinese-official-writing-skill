# 中文公文写作 1.5.15 发布证据

日期：2026-07-16

## 发行边界

- 上一发行基线为 annotated tag `v1.5.14`，解引用提交 `fea1fae4b0c809d3e2b7167d959a3822030b6033`。现有 tag、GitHub Release、ClawHub 和 skillhub.cn 的 1.5.14 均保持不动。
- 产品规则固定在 Candidate B 提交 `b5ef168e617bd0ca9afa1d5d3ca257291a701976`。相对 1.5.14，canonical 技能包只改动 `SKILL.md`、`references/genre-playbooks.md`、`references/task-route-cards.md`、`references/workflow.md`。
- 修改只中和重复的短写偏置：入口由“事实少于字数目标时宁可短写”调整为“篇幅要求不改变事实边界”，workflow 删除同义重复，报告叶子删除“宁可短写”，短通知叶子改为“按已给内容和语气成稿”。事实不编造、事项状态、用户篇幅要求和文种边界继续保留。
- `SKILL.md` frontmatter 还继承 1.5.14 发布后主线已完成的许可元数据统一：技能包 `license` 由 MIT 调整为 MIT-0，并同步版本为 1.5.15；根仓库继续使用 MIT。该项不改变写作规则或工作流。
- 未改变任务路由、reference 加载条件、段落/小节/全文复核顺序、输出模式、修改次数、回滚方式、默认联网和发布链；未新增脚本硬门禁、自动替换、finalizer、detector、repair 或批量清洗。
- Candidate B 之后只纳入自然写稿原稿、匿名盲包和按需收窄记录，不纳入 Candidate C—G、段落组件实验、P1 或 1.6.0 研发内容。
- 小红书 Red SkillHub 继续排除；不调用 Red CLI、dry-run、登录、标签查询或上传，`redskill/` 历史归档不参与同步。

## 发布前 live 核对

- `v1.5.14^{commit}` 为 `fea1fae4b0c809d3e2b7167d959a3822030b6033`；只读核对时 `origin/main` 为 `7b07b76878cc5d5e4a5c273833ff1007904372c1`。tag 与 main 分开记录，不假定相同。
- GitHub 公开 Release 仍为 `https://github.com/gongyu0918-debug/chinese-official-writing-skill/releases/tag/v1.5.14`，不是 draft 或 prerelease。
- ClawHub 公开 `latestVersion.version`、`tags.latest` 和五个正确 tag 均为 1.5.14，`displayName=中文公文写作`，moderation 与版本安全对象均为 clean；direct publish provenance 仍为 unavailable。
- skillhub.cn 精确目标为 `chinese-official-writing`、`skillId=70149`。公开详情、搜索和隔离安装入口均为 1.5.14，Keen、Sanbu 均为 benign。
- 两家商店各自隔离安装的 1.5.14 与本候选相比，归一化后只在 canonical `SKILL.md`、`genre-playbooks.md`、`task-route-cards.md`、`workflow.md` 四个文件存在内容差异。
- 本记录形成时没有 push、tag、GitHub Release、ClawHub publish 或 skillhub.cn publish。

## Candidate B 真实写稿边界

- 两个模型、四个同题任务共保留 8 份有效自然成稿；另保留 Luna T02 首次未读取本 Skill 的原始稿。初始自然触发率按 7/8 记录，同题复跑命中后有效质量样本为 8 份，不用复跑抹除首次路由未命中。
- 8 份有效稿中，只有 Terra T04 实际读取 `genre-playbooks.md` 与 `task-route-cards.md`；其余 7 份只读取入口。因此该组只称 Candidate B 自然入口执行，不称完整渐进式路由。
- 原始任务、模型、thinking、线程、读取记录和逐字符一致性见 `tests/evidence/candidate-b-writing-20260715/provenance.md`；8 份有效稿和 1 份路由未命中稿均原样保留。
- 三稿盲审按用户要求收窄为 Luna T01、T02 两题，每题保留 J1、J2 标签轮换包，共 4 包。盲包 4/4 prompt 与固定任务逐字一致，12/12 稿件位置与冻结来源逐字符一致；J2 只轮换标签，不改变正文。
- 独立 verifier 只读取四个匿名包。Candidate B 在 T01 为 PASS/G0，相对 current 1.5.14 严格胜出；在 T02 为三稿第一，但三稿均低于 1300 字下限，Candidate B 仍判 FAIL/G1，相对 current 1.5.14 只判小胜。J1/J2 标签轮换不改变评级、排序或关键风险，详见 `tests/evidence/candidate-b-three-way-blind-20260715/release-1.5.15-verifier.md`。
- README 只展示 T02 中“3 场管理员培训、58 人参加”一处事实边界节选，明确两个上下文并非同一随机 seed、无 Skill 稿未进入该轮候选/基线双盲排序，也不据此宣称整稿全面胜出。

## 工程验证

- `python -m unittest discover -s tests`：175/175 OK。
- `& 'C:\Users\admin\AppData\Local\Programs\Python\Python313\python.exe' .\evals\official-writing\run_eval.py --suite smoke --judge-batch-size 2`：在允许 Node 启动 Python provider 后，Promptfoo 20/20 PASS，0 failed、0 errors；skill 10 胜，judge consistency 1.0。沙箱内的初始运行在 provider 启动前报 Python 不可用，不计为测试通过。
- `python .\tools\run_real_prompt_ablation.py --baseline-root F:\Workspaces\chinese-official-writing-skill\output\release-baselines\github-1.5.14 --baseline-label baseline-1.5.14 --current-root . --out output\real-prompt-vs-1.5.14-release-1.5.15`：baseline 108/108，current 108/108。该工具不调用 LLM，只作确定性支撑。
- `python .\tools\run_real_prompt_ablation.py --baseline-root F:\Workspaces\chinese-official-writing-skill\output\release-baselines\candidate-b-b5ef168 --baseline-label candidate-b-b5ef168 --current-root . --out output\real-prompt-vs-candidate-b-release-1.5.15`：Candidate B 108/108，current 108/108，说明版本、镜像、README 和发布证据准备未改变确定性行为。
- `python .\tools\run_real_article_eval.py --out output\real-article-release-1.5.15`：skill 10 个样本缺失要素 0/61、关键词命中 61/61，格式风险、重复事项和反 AI 风险均为 0；9 个匿名占位标签样本、16 次占位词命中仍只作人工线索。
- `python C:\Users\admin\.codex\skills\.system\skill-creator\scripts\quick_validate.py .\chinese-official-writing`：`Skill is valid!`。
- `python .\tools\sync_adapters.py`：canonical、共享目录、`.agents`、`.qwen`、Hermes、OpenClaw、README、skill card 和 Claude plugin 版本面同步到 1.5.15；`redskill/` 未同步。

## 发行包预检

- canonical 白名单由 `git ls-files chinese-official-writing` 得到 18 个文件。物理目录另有两个测试生成的 ignored `scripts/__pycache__/*.pyc`，构包时不递归复制，因此未进入发行包。
- ClawHub 源 `openclaw/skills/chinese_official_writing/` 为 19 个跟踪文件：17 个 canonical 共享文件、平台 `SKILL.md` 和 `README.md`。物理文件 19，缺失、额外和违规文件均为 0；17 个共享文件逐文件 SHA-256 mismatch 为 0，平台 `SKILL.md` 可执行正文与 canonical 一致。
- 清空失效代理后的 ClawHub 官方 dry-run 返回 `status=would-publish`、`version=1.5.15`、`latestVersion=1.5.14`、`fileCount=19`、fingerprint `53363a15e884f94b9ce821641e81099fb7f4145035220ead0ca95c4e005150b6`。
- skillhub.cn 临时包按 canonical 18 文件白名单复制，再加入 `_meta.json`，共 19 个文件。17 个共享文件逐文件 SHA-256 mismatch 为 0，平台 `SKILL.md` 可执行正文与 canonical 一致，违规文件为 0。
- `python C:\Users\admin\.skillhub\skills_store_cli.py --skip-self-upgrade publish .\output\release-1.5.15\packages\skillhub-cn --version 1.5.15 --dry-run --json` 返回 `{"dryRun": true, "slug": "chinese-official-writing", "version": "1.5.15"}`。该 dry-run 不返回平台 fingerprint；正式 fingerprint 只能以提交回执为准。
- GitHub 仓库继续按 MIT 展示，可安装技能包及两家商店发行包为 MIT-0。

## 正式发布与发布后核对

- GitHub：发布前确认远端 `main` 精确为旧头 `7b07b76878cc5d5e4a5c273833ff1007904372c1` 且是候选祖先，随后无强推快进到发布提交 `cd0772fcd763eaa34bb32361c2f8d2cdee39a291`。annotated tag `v1.5.15` 的 tag object 为 `cc76e3970b3bd5413f9fd046ec8339a4132bd432`，解引用提交为 `cd0772fcd763eaa34bb32361c2f8d2cdee39a291`；公开 Release 为 `https://github.com/gongyu0918-debug/chinese-official-writing-skill/releases/tag/v1.5.15`，已是 Latest Release，`draft=false`、`prerelease=false`。发布回执文档可在 tag 后继续推进 `main`，但不得移动发布 tag。
- ClawHub：正式命令只提交一次，返回 `status=published`、`versionId=k9782v3jbeyehv7e7mkgemdbph8ajd38`、19 个文件和 source fingerprint `53363a15e884f94b9ce821641e81099fb7f4145035220ead0ca95c4e005150b6`。公开 `latestVersion.version`、`tags.latest` 和 `chinese`、`official-document`、`writing`、`gongwen`、`ai-compute` 五个正确 tag 均已切到 1.5.15，`displayName=中文公文写作`，moderation 为 clean、无 suspicious 或 malware。隔离安装共 21 个文件；排除平台生成的 `_meta.json` 与 `.clawhub/origin.json` 后，19/19 相对路径和 SHA-256 与发行源一致，缺失、额外和 mismatch 均为 0。
- ClawHub 版本级 verify 在约 5 分钟轮询后仍为异步状态：static scan clean，VirusTotal raw 为 stale、归一化为 pending，SkillSpector 尚无结果；card 未生成，provenance 明确为 unavailable，signature 为 unsigned。当前 verify fail 只由 `card.missing`、`security.status_not_clean`、`security.pending` 造成，不写成恶意判定或安全扫描失败，也不重复发布。
- skillhub.cn：精确 slug `chinese-official-writing` 只提交一次，正式回执为 `skillId=70149`、`versionId=139337`、19 个文件、fingerprint `428e844eb283c844ffbace10d27b4d79da70083020c444e8f9c1985895a260f9`、`tags.latest=1.5.15`，提交时 `reviewStatus`、`securityScanStatus`、`contentAuditStatus` 均为 pending。后续 owner 只读状态已为 `reviewStatus=approved`、`latestApprovedVersion=1.5.15`、`status=listed`，图标审核 passed；公开详情和搜索均已切到 1.5.15。
- skillhub.cn 隔离安装返回 1.5.15，共 19 个文件；排除平台在 `_meta.json` 中补入的 `ownerId`、`publishedAt` 后，18/18 文件与提交包逐文件 SHA-256 一致，缺失、额外和 mismatch 均为 0。平台签名验证 `ok=true`、`content_hash_match=true`，内容 hash 为 `efa622a30f064a1bbbfa13fd1549d8f6eb962a620e886cfe23a4a630b51c567b`。最终只读复核时 Keen、Sanbu 均已为 benign；owner GET 不再返回独立 `securityScanStatus`、`contentAuditStatus`，不能从 review approved 或外部报告结果推断这两个内部字段已 clean。
- 本轮没有调用小红书 Red SkillHub 的发布、dry-run、登录、标签或上传接口。

## 剩余风险与停止条件

- Candidate B 真实写稿只覆盖两个模型、四个任务，盲审收窄到 Luna 的两个任务；不等同全 29 文种、3000 字以上长文、多附件合稿、多轮 compact、跨模型大矩阵或 Word 版式验证。
- T02 的 Candidate B 稿虽在三稿中事实边界最稳，但仍未达到 1300 字下限；本版只能说明中和重复短写偏置后的相对改善，不能宣称已解决精确篇幅遵循。
- 初始自然触发存在 1/8 未读取 Skill；reference 实际加载只在 1/8 有记录，继续作为触发与路由可靠性风险，不与本次单变量修改混并。
- 段落观感、节奏和任务锚机制仍处于独立研发验证，不进入 1.5.15，也不以本版发布结论替代后续验证。
- ClawHub provenance 仍为 unavailable，版本级 security 聚合和 card 尚在异步；skillhub.cn owner GET 不暴露独立的安全扫描和内容审核字段。平台未返回的信息不作推断，只继续只读轮询。
- 两家商店正式提交均已各一次成功。后续若出现 source fingerprint 或安装文件哈希不一致、公开版本回退、平台给出恶意或拒绝结论，立即停止并核查；pending、card missing 或 provenance unavailable 不触发重复提交。
