# v1.6.3 本地候选

日期：2026-08-13

结论：`LOCAL CANDIDATE READY / NO PUSH / NO TAG / NO RELEASE / NO UPLOAD`。

## 固定基线与范围

- 已发布基线：`v1.6.2^{commit}=7d794b10f7acd320c90c2d311af9466fca732cfe`。
- 发布后 `main` 基点：`6f4904aef5f36fde8364192b64bcb0d7425bf393`；相对 v1.6.2 仅增加发布回执，没有产品路径改动。
- 本地候选产品提交：`8339c5da6e5e8ef2b2264036dbe93eba774704a0`（从 `53abd97c66cc4dcdf012db9df7bc06d9f41877b5` 以 `-x` 引入）。
- 本地候选分类信号提交：`2e2e45464918f1755d69d5d6da3276f7aa9f16bf`（从 `128bae86b77d2009836a116a37f1b698de0d083b` 以 `-x` 引入）。
- 本证据提交只同步候选版本面并记录实际验证；不改写已发布 v1.6.2 事实，不创建 tag，不推送，不创建 GitHub Release，不上传任何平台。

## 纳入原子

1. **Hook 纯审稿短语旁路。** 仅修改 `hooks/core/gate_stop_hook.py` 及其测试。`只审不改`、`仅审不改`、`只检查不修改正文` 在已启用 Hook 且已读取 Skill 后直接放行，不创建 transaction；“审后改写”“先审再改”“不是只审不改”和材料中引用该短语而实际要求起草的反例仍进入原门禁。它不改普通无 Hook 写稿链，不涉及保护性删除、编辑性否定或篇幅补写。
2. **SkillHub 清洁包分类检索信号。** 仅修改 `build_skillhub_package.py` 的专用摘要和 tags 及契约测试；加入 `office-efficiency`、`content-creation`，并在摘要保留中文公文、事务材料、新闻稿件与新闻评论信号。canonical frontmatter 和其他平台包不增加平台字段。该原子只证明本地 package/payload；未上传，因此不宣称 SkillHub 分类已变更或生效。
3. **候选版本同步。** 静态 Codex、Claude Code、WorkBuddy/CodeBuddy companion 和纯 Skill 镜像标为 `1.6.3`；README 继续明确 GitHub 当前已发布版本为 `1.6.2`。OpenClaw 兼容包随 canonical 镜像版本同步为候选 1.6.3，但没有 ClawHub 上传或发布主张。

## 明确排除

- 普通语义/新闻候选 `0bcddc3b8da759e5a96641a6f94f030ace9ce5d3`：17 个有效对中候选 8 胜、基线 9 胜，并有候选独有硬失败；源分支 `codex/v163-fast-semantic-release` 的 `maintenance/tests/evidence/v163-fast-semantic-release/RESULT-20260813.md` 结论为 `HOLD`。
- 篇幅 Hook `bf2bd0d39d3a25bc1f2103d02ca17439d8d83fe9`：源分支 `codex/v163-under-length-hook` 的 `maintenance/tests/evidence/v163-under-length-hook/preregister.md` 记录为 `PREREGISTERED / R1 INVALIDATED`，未完成新一轮真实验证。
- 保护性外扩/编辑性否定 Hook：用户明确排除；其新冻结与外部执行也未形成可转移的最终准入结论。
- 其他 Hook 适用性/质量研究：不以 `PASS_WITH_RISKS` 或生命周期可用性替代产品质量准入。

## 实际验证

| 检查 | 结果 |
| --- | --- |
| 聚焦 unit：边界、SkillHub builder、Hook 层契约、Stop Hook | 105/105 PASS |
| 全量 unittest | 551/551 PASS |
| Promptfoo stub smoke | 20/20 PASS，`eval-bFq-2026-08-13T08:23:38` |
| 固定 v1.6.2 确定性消融 | v1.6.2 111/111；候选 111/111 |
| canonical quick validate | `Skill is valid!` |
| 两轮 `sync_adapters.py` | 已实际运行；第二轮无差异 |
| SkillHub 清洁候选包 | 48 文件，`LICENSE.md` 与根 MIT 字节一致；不含 `agents/openai.yaml` 和无扩展名 `LICENSE` |
| `git diff --check` | PASS |

首次候选版本同步后，105 项聚焦测试发现三个静态 companion manifest 仍为 `1.6.2`，而同步脚本已是 `1.6.3`；该失败未被计作通过。随后同步 manifest，重跑同一 105 项测试、smoke、清洁包构建和 canonical 校验，均通过。

## 本地包与发布边界

- 最终本地包：`output/v1.6.3-local-candidate/skillhub-package-final`，版本 `1.6.3`，slug `chinese-official-writing`。
- 未执行 SkillHub CLI dry-run 或正式上传；未触碰 ClawHub、Red SkillHub、GitHub Release 或远端分支。
- 后续若取得单独的发布授权，仍须基于本提交重新构建清洁包、执行当次平台 dry-run、核对提交/tag/远端与平台回执；平台分类、审核和公开索引需分别回读。
