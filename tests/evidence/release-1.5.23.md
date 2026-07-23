# 1.5.23 发布准备证据

## 范围

1.5.23 以 `v1.5.22=7628619da8e05cc03c86d27d5a95eb8cee8fde05` 为固定产品基线，只合入已经独立验证通过的 AI 专项叶子减负：

- 纯 AI 技术需求直接读取 `references/ai-compute-docs.md`；
- AI 与请示、申请、采购、可研、报告、说明、审查、公告、通知、函或方案组合时，继续读取 `references/genre-playbooks.md` 和相应文种规则；
- `genre-playbooks.md` 原有 AI 专项正文迁入既有 AI 叶子，事实边界、文种功能、输出模式、复核顺序、脚本、Hook、FSM 和回退链不变。

独立候选分支为 `codex/release-1.5.23-ai-only`，产品提交 `4eacfce`，结果证据提交 `2848e91`。整合分支通过合并提交 `e74e84a` 保留候选历史。

52 字符的 CI/发布命令入口减负在独立分支 `codex/release-1.5.23-ci-command-relief` 验证。其工程门和硬核验通过，但匿名盲审为 Candidate 2 胜 1 负，不满足预注册的三题均胜或难分，因此按 MIXED 冻结；产品提交 `7ec7f3a` 未进入本版。

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

环境噪声单独记录：

- 沙箱内 unittest 首次收集 358 项，149 项因 `tempfile` 目录 ACL 报错，未出现产品断言失败；以同一系统 Python 在获批权限下原样复跑后 358/358 通过；
- Promptfoo 首次沿用 Hermes 失效 Python 路径，随后改用系统 Python 时又被沙箱阻止 Node 启动子进程；在获批权限下按相同评测入口复跑后 20/20 通过。

## 版本面与状态

- canonical、五套镜像、Claude 插件、OpenClaw 说明和公开 README 统一为 `1.5.23`；
- 发行包继续采用 MIT-0，仓库工程材料采用 MIT；
- 本记录形成时尚未创建 tag、GitHub Release，也未向 GitHub、ClawHub 或 skillhub.cn 推送/发布；
- 发布前仍须重新核验 `origin/main`、tag 占用、发行文件清单和平台实时状态，不把本地准备状态写成远端已发布。

当前结论：候选具备合入本地 `main` 并进入 push 前核验的条件；实际远端推送与三平台发布另行执行。
