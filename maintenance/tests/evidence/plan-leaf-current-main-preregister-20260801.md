# 方案起草叶 current-main 独立候选预注册（2026-08-01）

## 固定对象

- 当前主线与 Baseline：`origin/main=cdb74bf92471d8f4979c85d7fafe67eec5c7f6e4`。
- 旧方案叶产品：`35f55689bff76d581046c3e443f5fb9247095392`。
- 研究分支：`codex/plan-leaf-current-main-v1532`；只在隔离 worktree 实施，不改版本号、不发布。

## 单变量

从当前主线重建方案叶，不直接 cherry-pick 旧提交：

1. 新增 `references/genre-playbook-plan-construction.md`，只承接当前 `genre-playbooks.md` 已有的方案、实施方案和建设方案规则。
2. `SKILL.md` 增加该叶的直接路由；`genre-playbooks.md` 删除已经迁出的建设方案条目。
3. 同步五个发行镜像，并补与新路由直接相关的确定性测试。

规则语义、事实边界、篇幅、模板、输出模式、复核顺序和脚本均不改变；不包含报告叶、可研只审 R1/R2、scene-lint 或其他候选。

## 工程门

- 全量 unittest。
- Promptfoo smoke。
- Skill Creator `quick_validate.py`。
- current-main 固定确定性消融。
- canonical 与五个镜像一致性。
- `git diff --check`。

工程门失败即停止，不进入真实写稿。

## 真实验证

复用既有《综合窗口电子材料归集实施方案》A/B 及其有效匿名盲审；该次 Candidate 实际只读取方案叶，Baseline 读取原完整 playbook，两稿均无硬回退，Baseline 小胜来自可选细节复用，独立裁决未归因为方案叶。

再补两组逐字一致的自然任务：

1. 常规方案起草：事实和阶段安排充分，核验范围、任务、进度、责任和验收是否完整保留。
2. 既有方案局部改稿：用户模板、小标题、数字、职责、决定与未决状态均需锁定，核验专叶不会改变非目标内容。

Candidate 与 Baseline 使用同模型、同 thinking、首个技术有效输出；写手、trace verifier 和匿名 judge 分离。真正运行失败与产品失败分开记录，不补抽新题。

## 判定

- `PASS`：两组新测试均无事实、数字、主体、状态、文种、格式、篇幅、用户模板或输出模式硬回退；未发现可归因于拆叶的直接修改成本上升；结合既有有效 A/B，方案叶至少不劣于 current main。
- `MIXED`：出现轻微胜负但归因不清，保持隔离并报告，不用同义 Prompt 修补。
- `FAIL`：出现与拆叶相关的硬回退、错路由、跨文种读取或稳定质量下降，不合并。
