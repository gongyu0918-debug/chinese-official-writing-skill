# 早期工作树清理与资源释放（2026-09-15）

按用户当日授权清理"有研究结果的早期工作树"，解决新建聊天创建工作树卡顿。注册工作树由 384 个降为 5 个；全部分支（652 条）与 tag 未删除，本次未推送。

## 保留

- 主工作区（main，eb20eed0）。
- `C:/Users/admin/.codex/worktrees/9ef3/chinese-official-writing-skill`（游离 1ce71123）：未加载线程"公文 Skill 1.x：两日稳定版更新"引用。
- `C:/Users/admin/.codex/worktrees/5039/chinese-official-writing-skill`（codex/mit-speech-revision-r10）及其两个嵌套工作树：未加载线程"接手 MIT 公文写作 Skill 后续构建"引用。

用户明确要求新的、正在构建的线程工作树保留，老旧非活跃的清理；以上为仅有的线程占用项。

## 释放方式与验证

- 379 个非保留目标分批释放：
  - 120 个经 `git worktree remove`，其中 119 个有完整日志，1 个在停止慢速通道时已完成移除但未落日志，经前后注册列表核对无残留。
  - 255 个经"`git status --porcelain` 干净校验 → 同卷改名 `.trash-20260915` → `git worktree prune`"释放，避免逐文件删除拖慢主流程；257 个改名目录（含下述顽固项）由 4 个并行后台任务永久删除，进度与失败记录在 `output/wt-cleanup-20260915/trash-delete-bucket-*.log`。
  - 2 个 Temp 审计基线（7d794b10、612c0566）：本地仅有删除类差异，完整内容由 `refs/archive/wt-cleanup-20260915/13-*`、`/14-*` 归档引用保护后清理。
- 2 个有真实未提交改动的顽固项先保全再释放：
  - `codex/jargon-shungao-naturalize-v1601`：未提交状态（30 文件、60 行增删）提交为 489fba47 后释放。
  - `codex/p0-negative-close-full-skill-v1541`：工作树差异为换行符假差异，文件 blob fd7792ed 与分支提交 f7566d79 内容完全一致，无需保留提交即释放。
- 34 个游离研究点（含两个发布基线 8086ff25、4b135c50）建 `refs/archive/wt-cleanup-20260915/*` 归档引用，防 gc 丢失；干净工作树均可用 `git worktree add <path> <branch>` 一步重建。

## 验证结果

- `git worktree list`：384 → 5，44ms。
- 新建+删除测试工作树（新聊天场景）：add 2.78s、remove 1.59s，不再卡顿。
- 主工作区 `git status` 干净，main 与 origin/main 同步；未推送、未动 tag。
- 652 条分支全部保留，任一研究工作树可按分支名重建。
