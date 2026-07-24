# 1.5.23 发布准备证据

## 范围

1.5.23 以 `v1.5.22=7628619da8e05cc03c86d27d5a95eb8cee8fde05` 为固定产品基线，只合入已经独立验证通过的 AI 专项叶子减负：

- 纯 AI 技术需求直接读取 `references/ai-compute-docs.md`；
- AI 与请示、申请、采购、可研、报告、说明、审查、公告、通知、函或方案组合时，继续读取 `references/genre-playbooks.md` 和相应文种规则；
- `genre-playbooks.md` 原有 AI 专项正文迁入既有 AI 叶子，事实边界、文种功能、输出模式、复核顺序、脚本、Hook、FSM 和回退链不变。

独立候选分支为 `codex/release-1.5.23-ai-only`，产品提交 `4eacfce`，结果证据提交 `2848e91`。整合分支通过合并提交 `e74e84a` 保留候选历史。

52 字符的 CI/发布命令入口减负在独立分支 `codex/release-1.5.23-ci-command-relief` 验证。其工程门和硬核验通过，初轮匿名盲审为 Candidate 2 胜 1 负。唯一负例只涉及联系人与联系电话分行偏好，没有事实、状态、P0 或材料外扩差异，因此另从固定基线建立 `codex/release-1.5.23-ci-command-relief-retest`，精确复放同一产品变量并预注册两组同题复现。复测产品提交为 `5b10da7`，结果提交为 `9d0ad64`，详见 `entry-ci-command-relief-retest-result-20260724.md`。

复测首批四次运行均在读取前遭遇对称的 Windows ACL 启动错误，按预注册判技术无效；唯一允许的同条件重试得到四份技术有效首稿。硬核验三份 PASS，一份仅因联系人行尾含两个空格为 WARN，无事实、数字、状态、P0 或材料外扩回退；匿名盲审一组 Baseline 胜、一组 Candidate 胜，胜负仍只来自同一换行偏好。由此可确认初轮负例含抽样波动，但无法证明删除该说明后稳定不负于基线；按复测预注册结论为 FAIL，产品提交 `7ec7f3a`、`5b10da7` 均未进入本版。

`genre-playbooks.md` 的维护尾句减负另在 `codex/release-1.5.23-genre-tail-relief-retest` 精确复放，产品提交 `8911d60`，结果提交 `de989bd`。全量 unittest 358/358、固定 1.5.23 确定性消融两侧 108/108、quick validate 和镜像检查均通过；但正常自然任务及唯一允许的同条件重试中，Candidate 与 Baseline 都只读取 `SKILL.md`、`information-selection.md` 和 `task-route-cards.md`，没有加载被修改的 `genre-playbooks.md`。按预注册该测试为 INVALID/STOP，不改变产品结论，也未进入本版。

其余历史减负只保留为下一轮研究：review-mode 紧凑化仅有 1 胜 1 负、改动 35 字且缺少可独立复现的产品提交；纪要清单叶子实际路径由 3042 增至 3045 个字符，不能计作减负。两者均未合入 1.5.23。大幅回退且已有完整 Git 记录的 proofreading toolchain、proofreading prefix 和 format leaf 方向不再作为本版候选；发布前已核验三处 detached worktree 均位于 `output/research-worktrees/`、工作树干净、提交对象可读，随后仅清理物理 worktree，Git 提交 `6261427`、`bc1477c`、`9040aae` 继续保留。其他未合并候选及其 worktree 保留为下一轮研究。

## 确定性收益

- 纯 AI 专项 reference 负载由 6695 个字符降至 3332 个，减少 3363 个，约 50.2%；
- 计入常驻 `SKILL.md` 后，所选上下文由 17824 个字符降至 13591 个，减少 4233 个，约 23.7%；
- 普通文种和 AI 混合文种的加载路径保持不变。

## 真实写稿

Candidate 与固定 1.5.22 使用 `gpt-5.6-sol / ultra`、逐字一致原始任务，各侧由独立 writer 按顺序保留首个技术有效输出，不补抽、不二次修订。三题覆盖：

1. 模型推理服务技术需求；
2. GPU 算力租赁服务采购公告；
3. 模型服务平台建设可行性研究报告。

独立硬核验中 Candidate 3/3 PASS；Baseline 两题 PASS，一题因无锚定强化为 WARN。匿名盲审为 Candidate 2 胜、1 难分，未出现 Candidate 独有的事实、数字、日期、主体、状态、文种、格式、输出模式、P0 或材料外扩回退。原始任务、哈希、匿名映射和评审结论见 `release-1.5.23-ai-only-result-20260724.md`。

## 整合工程验证

在 `codex/release-1.5.23-integration` 实际执行：

- 全量 unittest：358/358 通过；
- Promptfoo smoke：20/20 通过，0 failure，0 error；
- 固定 1.5.22 确定性消融：Baseline 107/108，Candidate 108/108；Baseline 唯一失败是本版新增的 AI 专项迁移断言，不是既有能力回退；
- canonical quick validate：通过；
- `tools/sync_adapters.py`：canonical 与五套镜像同步；
- `git diff --check`：通过。

在本轮减负噪声复核收口提交 `0c80afee79b61ef0efc0ad61135cf6bf7c5a4655` 上再次执行发布门：

- 全量 unittest：358/358 通过；
- Promptfoo smoke：20/20 通过，0 failure，0 error，judge consistency 1.0；
- 固定 1.5.22 确定性消融：Baseline 107/108，Candidate 108/108；
- canonical quick validate：通过；
- 镜像同步后无内容差异；Git 曾因 LF/CRLF 规范化短暂显示五个 `SKILL.md` 为修改，`git diff` 为空，按索引规范化后工作树恢复干净；
- OpenClaw/ClawHub 发行镜像为 23 个文件，未包含 `review_gate.py`、`gate_stop_hook.py`、`delivery-review-gate.md`、测试、证据、缓存或 `.pyc` 文件。

环境噪声单独记录：

- 沙箱内 unittest 首次收集 358 项，149 项因 `tempfile` 目录 ACL 报错，未出现产品断言失败；以同一系统 Python 在获批权限下原样复跑后 358/358 通过；
- Promptfoo 首次沿用 Hermes 失效 Python 路径，随后改用系统 Python 时又被沙箱阻止 Node 启动子进程；在获批权限下按相同评测入口复跑后 20/20 通过。

## 版本面与发布回执

- canonical、五套镜像、Claude 插件、OpenClaw 说明和公开 README 统一为 `1.5.23`；
- 发行包继续采用 MIT-0，仓库工程材料采用 MIT；
- 发布前重新核验 `origin/main=31ec7ca19d1a48f57f5ee09a3261b6eddaad8193`，GitHub、ClawHub 和 skillhub.cn 当时均为 1.5.22，`v1.5.23` tag 与 GitHub Release 均未占用；
- ClawHub dry-run 返回 `status=would-publish`、公开基线 1.5.22、目标版本 1.5.23、23 文件和 fingerprint `ea9704defb77af3d7587c397a6f634e72699c6138967b79c53b157acdfe65bfb`；
- skillhub.cn dry-run 返回 `dryRun=true`、slug `chinese-official-writing`、目标版本 1.5.23。

正式发布回执：

- GitHub：`main` 快进到发布提交 `1bf33384cc3d2ff9a17da16fcd8f1936b43c253b`。annotated tag `v1.5.23` 的 tag object 为 `7ca328566e0736150cfbc057d7d6eacf0e24a5ef`，解引用提交同为发布提交；正式 Release 已公开：`https://github.com/gongyu0918-debug/chinese-official-writing-skill/releases/tag/v1.5.23`，`draft=false`、`prerelease=false`。
- ClawHub：使用 dry-run 核验过的 23 文件清洁包正式提交一次，返回 `status=published`、`versionId=k975803yfr1r803szmprs4p7en8b5fnf`、fingerprint `ea9704defb77af3d7587c397a6f634e72699c6138967b79c53b157acdfe65bfb`。正式回执中的 `latestVersion` 仍为 1.5.22；立即精确查询 1.5.23 返回传播窗口中的 `Version not found`，随后公开查询遇到路由/速率限制，故 1.5.23 的实时 moderation 和公开 latest 暂记 `unavailable`，不从旧版 clean 状态推断，也不重复提交。
- skillhub.cn：向既有 `skillId=70149` 正式提交一次，返回 `ok=true`、`versionId=159789`、23 文件、fingerprint `7ae9dd7811949518a7447b0295b4966c6d6fe4bcfee531376932daac0694cbb6`、`tags.latest=1.5.23`；`reviewStatus`、`securityScanStatus` 和 `contentAuditStatus` 均为 pending。首次公开搜索仍显示 1.5.22，按异步审核和传播处理，不重复提交。
- 小红书 Red SkillHub 继续排除；本轮未调用 Red 上传、登录或查询命令。

当前结论：1.5.23 已完成 GitHub、ClawHub 和 skillhub.cn 各一次正式提交；GitHub 已公开，两家商店的公开索引和审核状态按异步传播继续只读核验。
