# 1.5.8 论文入口与发布记录

日期：2026-07-13

## 发布边界

- 上一发行基线：`v1.5.7=d3755df7deb2456150c61ccb1944aa3982f7edf1`；论文扩展前基线：`11a80be`；本轮候选基础：`aaba577`，发布准备前 HEAD 为 `6c85f936e6d637621cd20b85f0485c6762f3c203`。
- 仓库名 `chinese-official-writing-skill`、slug/skill_identifier `chinese-official-writing`、展示名“中文公文写作”和 ClawHub 包内兼容名 `chinese_official_writing` 均不修改。
- 1.5.8 只把既有中文本科、硕士学位论文和课程论文能力暴露到 canonical description、Agent UI、GitHub README、ClawHub 市场介绍、skill-card、Claude 插件说明和各发行镜像；不改论文/公文路由逻辑、reference 加载、输出模式、复核顺序、默认联网和回滚规则。
- 写作内核仍为由大至小组织、事实和引用可追溯、由小至大复核；论文只使用用户给定事实和已核验检索结果，宁可短写也不补造数据、案例、文献、实验或结论，正文后可给补充材料与论点构造建议。
- 未新增生成器、finalizer、检测器、硬清洗、默认多 Agent、默认联网、AIGC/查重规避或重排版引擎。
- 发布面包括 GitHub、ClawHub、skillhub.cn SkillHub 和小红书 Red SkillHub。Red 使用独立维护副本和独立回执，不与 skillhub.cn 混记。

## 修改和回退

- 产品入口只把“中文学位论文、课程论文”明确为“中文本科、硕士学位论文和课程论文”；其他正文规则不变。单句回退方式是恢复该 description 短语并重新同步适配镜像。
- 版本元数据统一为 `1.5.8`；公开说明增加论文入口、事实与引用边界和试用 prompt，不改变仓库或平台身份。
- 针对市场说明增加静态守卫，要求 canonical、Agent UI、README、marketplace、skill-card 和插件说明均能看到论文能力。
- 首次运行 `python -B -m unittest tests.test_skill_boundary tests.test_real_prompt_ablation -v` 时，旧边界测试发现 marketplace 文案遗漏精确短语“规避人工审核”；补回该短语并保留“规避 AIGC/查重检测”后重跑 53/53 通过。该失败未进入发布候选。

## 发布前验证

- `python -B tools\sync_adapters.py`：通过。
- 一次未提权的重复同步因 `.agents` 目录 ACL 返回 `Permission denied`；未改动产品规则，随后在仓库范围权限下完整重跑，六组镜像和三个市场元数据源全部同步成功。
- `python -B -m unittest tests.test_skill_boundary tests.test_real_prompt_ablation -v`：53/53 通过。
- `python -B -m unittest discover -s tests -v`：145/145 通过。
- `npm run eval:official-writing:smoke`：20/20 PASS，0 fail/error，skill 10 胜，judge consistency 1.0。
- `python -B tools\run_real_prompt_ablation.py --baseline-root output\release-baselines\github-1.5.7-paper --baseline-label baseline-1.5.7 --current-root . --out output\release-1.5.8\deterministic-vs-1.5.7`：1.5.7 基线 102/112，current 112/112；基线失败仅在论文扩展新增守卫。
- `python -B tools\run_real_article_eval.py --out output\release-1.5.8\real-article`：skill 路径 10 个样本关键要素 61/61、关键词命中率 100%、格式/重复/反 AI 风险均为 0；匿名占位标签仍只作人工复核线索。
- `python -B C:\Users\admin\.codex\skills\.system\skill-creator\scripts\quick_validate.py chinese-official-writing`：`Skill is valid!`。
- 完整评测数据 27 批最大上下文 `24915`，低于仓库 `<25000` 门槛。
- `git diff --check`：通过；仅有 Windows 行尾转换提示。

## 混合路由 sanity

- 两名独立原生 Codex writer 各处理 4 个未见 prompt；运行环境未暴露可核验精确模型 ID，因此本组只作 sanity，不计入跨模型统计门槛；未使用 MiniMax。
- 独立 verifier 只读取原 prompt 和匿名输出，判定 8/8 PASS：中文课程论文和研究公文语言的课程论文走论文；本科毕业论文抽检通知按最终交付物走公文；英文硕士论文请求明确排除；所有样本均未编造事实、引用或统计结果。
- 原始 prompt、输出和判定保存于 `tests/evidence/release-1.5.8-routing/`。

## 发行包预检

- canonical 为 19 个跟踪文件；ClawHub 目录为 20 个文件，即 canonical 内容加市场 `README.md`；无 `.pyc` 或 `__pycache__`。
- ClawHub dry-run 返回 `status=would-publish`、`slug=chinese-official-writing`、`displayName=中文公文写作`、`version=1.5.8`、`latestVersion=1.5.7`、`fileCount=20`、fingerprint `a1d1dd72c07bc37804c5ee8a6cc8480a44c89e3af951e75ad9b724d6f10a9136`。
- skillhub.cn 临时包 `output/skillhub-release-1.5.8/publish-package` 为 20 个文件，即 canonical 19 个文件加 `_meta.json`；按 `git ls-files` 显式复制，未递归带入缓存。
- SkillHub dry-run 返回 `dryRun=true`、`slug=chinese-official-writing`、`version=1.5.8`。
- 小红书官方 CLI 0.1.1 普通 Windows shim 仍静默退出；兼容入口 `whoami` 返回 `loggedIn=true`，实时标签包含“内容创作”和“职场办公”。
- GitHub、ClawHub 和 skillhub.cn 完成发布后，已由同版本 SkillHub 包同步 `redskill/skills/chinese-official-writing/`，只删除 Red CLI 不支持的 `agents/openai.yaml`；预期 19 文件、实际 19 文件，缺失、额外和 SHA-256 mismatch 均为 0。
- Red dry-run payload 为 `skill_identifier=chinese-official-writing`、`name=中文公文写作`、无引号版本 `1.5.8`、`original=true`、`content_tag_ids=[1002,1004]`、bundle SHA-256 `b81d523c4dec67fc8dc5fdbea01251d11223eed6b79b45147a63b15b22df2ff9`、93871 bytes。
- 通用 Codex `quick_validate.py` 对 Red/SkillHub 包返回“Unexpected key(s)”并拒绝顶层 `slug/version/displayName/summary/tags/homepage`；这些是目标平台所需元数据，未为通过另一平台 validator 而删除。小红书官方 CLI dry-run 已接受该包，此差异记为非阻断平台兼容项。

## 独立冷审

- 独立 reviewer 对 staged diff、三个本地发行目录和测试输出交叉核验，结论为 P0 0、P1 0、`publish_blocking=false`，建议提交。
- Reviewer 确认 canonical 产品 diff 只改 description 短语和版本，仓库名、slug/skill_identifier、展示名、OpenClaw 兼容名和核心工作流均未改变；19/20/20 文件清单、共享文件哈希、无缓存和 `git diff --cached --check` 均通过。
- P2 仅要求正式发布后补齐三个平台回执，并提醒 Red 必须显式传无引号版本 `1.5.8`；Red 完成同步、SHA-256 和真实回执前，不得宣称四面完成。

## 发布状态

- 发布 commit：`bde04db86fe59dbc374742f53e67bfa0d4800376`；annotated tag `v1.5.8` 解引用到同一提交。GitHub `origin/main` 在发布时指向该提交，release 已公开且不是 draft/prerelease：`https://github.com/gongyu0918-debug/chinese-official-writing-skill/releases/tag/v1.5.8`。仓库名保持 `chinese-official-writing-skill`，description 已增加论文入口。
- ClawHub：`chinese-official-writing@1.5.8` 已公开，`versionId=k976nekbayaave0egabm5p0b1h8ac5b5`、20 文件、fingerprint `a1d1dd72c07bc37804c5ee8a6cc8480a44c89e3af951e75ad9b724d6f10a9136`；`latestVersion.version`、`tags.latest` 和五个正确 tag 均为 1.5.8，`displayName=中文公文写作`，source commit 为发布提交。总体 moderation 为 clean；VirusTotal/LLM clean，但 Skillspector 有 2 项 MEDIUM/CAUTION，故 `hasWarnings=true`。
- skillhub.cn：已向原 slug 和 `skillId=70149` 提交 1.5.8，返回 `ok=true`、`versionId=136083`、20 文件、fingerprint `c9f1b8fb0ecc0119376968207dfdd55930f6e7f0ab529eea987f83dcc14f889d`、`tags.latest=1.5.8`；`reviewStatus/securityScanStatus/contentAuditStatus=pending`。公开搜索仍显示版本 1.5.7，但 description 已更新，暂只表述为“已提交”。
- 小红书 Red SkillHub：1.5.8 尚未发布成功。第一次真实提交在上传前因 token 过期停止；`login --agent` 用现有 refresh token 静默续期成功。第二次完成上传后，服务端返回 `SUBMIT_REJECTED: Skill ID 已被占用`，未返回 `RESULT_JSON.status=submitted` 或新的平台 ID。当前最后成功回执仍为 1.5.7 的 `skill_id=8494`、`version_id=100041`、`audit_request_id=8494_100041_17833860685024`。未改 identifier，也未创建第二个 skill。

## 已知风险

- 本轮证明入口路由和既有边界在短样本中稳定，不承诺弱模型无人值守、完整论文独立生成、文献真实性、统计有效性或 AIGC/查重规避。
- 真实长论文仍可能出现篇幅不足、论点重复、引用状态误写或章节比例失衡；稀疏材料下继续优先短写和文后构造建议。
- skillhub.cn 与 Red SkillHub 均有异步审核或索引延迟；提交成功与公开可见必须分开表述。
- Red 1.5.8 当前不是审核延迟，而是服务端在提交阶段明确拒绝；后续需确认当前 OAuth 账号对 `skill_id=8494` 的归属，或使用平台正式支持的既有 skill 更新入口，不能重复盲传或换 identifier 绕过。
