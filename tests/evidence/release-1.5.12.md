# 中文公文写作 1.5.12 发布证据

## 范围与上一发行基线

- 上一发行版固定为 annotated tag `v1.5.11` 解引用提交 `59eed9e4a4873082edaaef0c241186583bd68206`；detached 基线目录为 `output/release-baselines/github-1.5.11-prompt-relief`。
- 本版纳入 4 个已分别提交和验证的最小 Prompt 减负提交：`df8c72a` 删除重复旁白/教学反例，`88bf86d` 将语言模式检查隔离到按需加载的 ANTI-AI 叶子，`53a4181` 删除入口重复思考泄露提醒，`e1149db` 将社区研究构造规则移回维护层。
- 任务路由、reference 加载条件、段落/小节/全文复核顺序、输出模式、修改次数、回退方式、默认联网和三平台发布链没有改变；没有新增生成器、finalizer、检测器、自动清洗、默认阻断或排版脚本。
- 这是从 `origin/main` 以来的第 5 个提交门槛，按 `AGENTS.md` 额外执行独立冷审、固定基线消融、真实写稿盲审、完整回归和发行包校验。
- 小红书 Red SkillHub 明确排除；未调用 Red CLI、dry-run、登录或上传，`redskill/` 历史归档不参与版本同步。

## 独立复核与真实写稿

- 独立 diff reviewer 判定产品修改 `PASS`：未发现核心工作流、直接写作边界、镜像或配置漂移；其独立边界测试为 `44/44 OK`。
- 发布候选使用 4 个逐字真实用户式 prompt，覆盖稀疏事实报告、只审不改的制作说明/无依据否定/虚假对比/机械重复、字段式采购申请、最新版与旧版/参考样文隔离。
- 两名当前候选 writer 与一名固定 `v1.5.11` baseline writer 共形成 12 份输出；独立 verifier 只看逐字 prompt 与匿名 X/Y/Z，判定 `12/12 PASS`。两个当前 writer 相对 baseline 均未出现独有的事实、引用、文种、格式、输出模式、ANTI-AI 语义、字段边界或旧稿回流回退。
- 原 prompt、三名 writer 原始输出、匿名映射和逐项 verifier 判定保存在 `tests/evidence/release-1.5.12-writing/`。子上下文未返回可核验的精确模型 ID，因此本组只记发布级真实写稿 sanity，不宣称指定模型矩阵或统计显著性；未使用 MiniMax。

## 工程回归

- `py -3 -B -m unittest discover -s tests -v`：`151/151 OK`。
- `py -3 -B tools/run_real_prompt_ablation.py --baseline-root output/release-baselines/github-1.5.11-prompt-relief --baseline-label baseline-1.5.11 --current-root . --out output/release-1.5.12/real-prompt-vs-1.5.11`：baseline `108/108`，current `108/108`。
- `npm run eval:official-writing:smoke`：`20/20 PASS`，0 fail、0 error，skill 10 胜，judge consistency `1.0`。
- `py -3 -B tools/run_real_article_eval.py --out output/release-1.5.12/real-article`：skill 10 个样本缺失要素 `0/61`、关键词命中率 `100%`，格式风险、重复事项和反 AI 风险均为 0；9 个匿名占位标签样本仍只作人工线索。
- 27 批评测上下文最大值 `24589`，低于仓库 `<25000` 门槛，并与版本同步前已验证候选一致。
- canonical Skill 通过 `quick_validate.py`；完整单测覆盖 canonical 与五个发行镜像逐文件一致性；`git diff --check` 仅有 Windows 换行提示，无空白错误。

## 发行包预检

- 版本同步脚本将 canonical、五个发行镜像、Claude plugin、README、OpenClaw 市场说明和 skill-card 统一为 `1.5.12`；`redskill/` 未同步。
- ClawHub 发行源 `openclaw/skills/chinese_official_writing/` 为 19 个文件。最终 dry-run 使用发布提交 `f87b6be990e1314442b5532ae7441f21c8d4d34f` 作为 `source-commit`，返回 fingerprint `7371dd14354344ae657b2404a6d135bb3a0d169cdd5db812b8a87cddaad9cfaa`。
- skillhub.cn 使用 `git ls-files chinese-official-writing` 白名单构造临时包，避免 ignored `__pycache__` 混入；临时包 19 个文件，无 `.pyc`、`__pycache__`、finalizer、detector 或 repair 文件，17 个不含专用 `SKILL.md` 的共享文件与 canonical 逐文件 SHA-256 一致。
- skillhub.cn CLI `2026.7.7` 登录身份为 `user_f3d82da7` / `userId=437097`；dry-run 确认 `slug=chinese-official-writing`、`version=1.5.12`。平台专用 frontmatter 含扩展字段，不能用只接受 Agent Skills 基础字段的 canonical quick validator 替代平台 dry-run。

## 发布状态

- GitHub：发布提交 `f87b6be990e1314442b5532ae7441f21c8d4d34f` 已快进到 `main`；annotated tag `v1.5.12` 解引用到同一提交；GitHub Release 为 `https://github.com/gongyu0918-debug/chinese-official-writing-skill/releases/tag/v1.5.12`，非 draft、非 prerelease。
- ClawHub：正式回执 `status=published`、`versionId=k97ej86790086hhs99ga0rqa158ah6fz`、19 个文件、fingerprint `7371dd14354344ae657b2404a6d135bb3a0d169cdd5db812b8a87cddaad9cfaa`。live `latestVersion`、`latest` 与五个正确 tag 均为 1.5.12，`displayName=中文公文写作`，moderation 总体为 clean。隔离安装成功，排除平台生成的 `_meta.json` 和 `.clawhub/origin.json` 后，19 个发行文件与发布源逐文件 SHA-256 一致。版本安全扫描和平台生成 card 在首次核验时仍 pending/missing，因此 `skill verify` 返回 fail；只等待异步状态，不重复发布。
- skillhub.cn：正式回执 `skillId=70149`、`versionId=136989`、19 个文件、fingerprint `5e7301de32ec3dc1e956d14b1ee33bdd224ccee3b5489ed94ab4eaa453de7a7c`、`tags.latest=1.5.12`，`reviewStatus/securityScanStatus/contentAuditStatus` 均为 pending。发布后首次公开搜索和 API 的 `latestVersion` 仍为 1.5.11，五个主题 tag 的公开 API 仍为历史值 1.5.1；不把平台索引延迟或旧主题 tag 表述为发布失败，也不重复提交。公开安装入口切换后的安装哈希尚待补录。

## 回退与剩余风险

- 任一旧硬边界回退、目标问题没有保持、上下文达到或超过 25000、镜像或发行包不一致，停止发布并回退本版候选；索引延迟或异步审核 pending 不触发重复提交。
- ClawHub tags 参数必须作为单一 token 传入：`'--tags=chinese,official-document,writing,gongwen,ai-compute'`，避免产生错误合并 tag key。
- 真实写稿样本规模有限，不能证明所有弱模型、长文、复杂附件或多轮 compact 稳定性；当前修改为删重和分层，不扩大这些能力承诺。
- 发布后补录 GitHub URL、release/tag SHA、ClawHub versionId/fingerprint/扫描状态、SkillHub versionId/fingerprint/审核状态及两平台安装哈希；若正式回执已经成功但客户端报错，先只读 inspect，禁止立即重发。
