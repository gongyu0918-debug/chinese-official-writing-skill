# v1.6.22 冻结发布面与下一版本候选主线合入

日期：2026-08-31。

## 结论

- v1.6.22 明日发布源固定为 `codex/release-v1.6.22@62ba9e8206e5b11f08a8f28ebdfe95b08e30ccfe`，独立 worktree 为 `F:\Workspaces\chinese-official-writing-skill\output\release-worktrees\release-v1.6.22`。
- 下一版本候选 `codex/post-v1622-hook-contract-r1@ad732865eb8face14133581ad7f56d10e41cb1d5` 已通过 `git merge --ff-only` 合入 `main`。该增量不属于 v1.6.22，明日不得从当前 `main` 创建 v1.6.22 tag、GitHub Release 或重新生成平台包。
- 未创建或移动 tag，未推送，未向 GitHub、SkillHub.cn、ClawHub 或其他平台发布。

## 冻结包核对

- SkillHub.cn 目录：`output\release-v1.6.22\skillhub-clean`，82文件；slug `chinese-official-writing`，展示名“中文公文写作”，版本 `1.6.22`。既有规范化 fingerprint 为 `6b97bb1ef28789360004b1a580ee724fef2c97f4758ebd2a9bf141a378457ed2`。
- 使用冻结 worktree 的 `maintenance/tools/build_skillhub_package.py --version 1.6.22` 重新生成82文件临时包，并按相对路径与逐文件 SHA-256 对照：`SKILLHUB_REBUILD_EXACT=true`。
- ClawHub 目录：`packages\openclaw\skills\chinese_official_writing`，33文件；name `chinese_official_writing`，版本 `1.6.22`，Hook、`agents/openai.yaml`、付费提纲和红头路径命中0。既有规范化 fingerprint 为 `0ce2f2e2b3929d65e9970b73d0c31d67f69ce36e09dedc59538cf434db754427`。
- 冻结 release worktree 在核对前后均无 tracked 修改。当前 main 的 SkillHub 包会包含下一版本 Hook 增量，因此即使版本字段仍显示1.6.22，也不是允许发布的1.6.22包。

## 合入前证据

- `main@62ba9e82` 是候选祖先，`main...codex/post-v1622-hook-contract-r1` 为 `0 7`，可以纯 fast-forward，无冲突或 merge commit。
- 候选相对冻结提交不改公开 README、canonical `SKILL.md`、ClawHub `SKILL.md` 或 SkillHub builder；只改变已验证的 Hook 契约、Stop 生命周期、直接测试与状态证据。
- 候选直接 Hook/adapter/under-length 回归102/102、状态一致性12/12、全量756/756、独立冷审101/101、Python AST 3/3、JSON 1/1、adapter同步幂等及 `git diff --check` 均通过，详细命令见 [`result.md`](result.md)。

## 合入后验证

- `python -B -m unittest maintenance.tests.test_gate_stop_hook maintenance.tests.test_host_gate_adapter maintenance.tests.test_under_length_capability maintenance.tests.test_hook_layer_contract`：102/102通过，55.680秒。
- `python -B -m unittest maintenance.tests.test_skill_boundary maintenance.tests.test_skillhub_package_builder maintenance.tests.test_status_ledger_consistency`：95/95通过，0.938秒。
- 状态转换前后的 `test_status_ledger_consistency` 均为12/12；`git diff --check` 通过。冻结 release worktree 前后均保持清洁，未因主线快进移动 `codex/release-v1.6.22`。

## 明日发布边界

1. GitHub tag 与 Release 必须绑定冻结提交 `62ba9e8206e5b11f08a8f28ebdfe95b08e30ccfe`，不得绑定当前 main。
   若需要把 GitHub 远端 `main` 更新到本版，须先重新确认 `origin/main` 是冻结提交的祖先，再显式使用冻结 refspec `codex/release-v1.6.22:main`；禁止普通 `git push origin main`，因为本地 main 已含下一版本增量。
2. SkillHub.cn 只使用冻结 worktree 中已逐文件核对的82文件 `skillhub-clean`。
3. ClawHub 只使用冻结 worktree 中的33文件 `packages/openclaw/skills/chinese_official_writing`，继续不含 Hook。
4. 平台每个版本仍只提交一次；正式写入前重新核对冻结 worktree HEAD、工作树、文件数、slug、展示名、版本和禁入路径，但不得从 main 重建替换冻结包。
