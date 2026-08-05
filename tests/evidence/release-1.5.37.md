# 1.5.37 本地候选验证记录

## 当前状态

1.5.37 已合并到本地 `main` 并完成版本面同步，尚未推送、打 tag 或发布到 GitHub、ClawHub、skillhub.cn。记录时本地 `main` 为 `c65d0af329a48884c8e0454ac5d62e61a267e14b`，远端 `origin/main` 仍为 `32bb401e603e40aadd2a5a488a92768c4cf6695c`，仓库中没有 `v1.5.37` tag。

## 本轮改动

- anti-AI 复核文件不再重复展开只审输出契约，改为指向统一规则源；写作边界、文种路由和复核顺序保持不变。
- `prose_lint.py` 收紧三类已复现误报：合法否定指令、编号式“补充信息”正文和中文相邻 `XX` 占位重复报告；高置信风险召回继续保留。
- canonical、Codex、Claude Code、Qwen、Hermes、OpenClaw 镜像及展示元数据统一到 1.5.37。

## 基线与提交

- 固定 1.5.36 产品基线：`8bd4eb8c8b4f233445e07ebf4d3f54ceb5777aa2`。
- anti-AI 契约去重：`ef68ec49`。
- lint 误报修复：`ddd86de4`。
- 组合结果记录：`d0aed66a`。
- 合并本地 `main`：`6488dc13`。
- 版本面同步：`c65d0af3`。

## 合并后验证

| 验证 | 实际结果 |
| --- | --- |
| `python -m unittest discover -s tests` | 442/442，通过 |
| `npm run eval:official-writing:smoke` | 20/20，通过；0 failed、0 errors |
| 固定 1.5.36 确定性消融 | baseline 111/111；current 111/111 |
| `quick_validate.py chinese-official-writing` | `Skill is valid!` |
| `python -m py_compile ...` | `prose_lint.py`、`review_gate.py`、`sync_adapters.py` 通过 |
| `python tools/sync_adapters.py` | 重复执行后无语义差异，镜像同步幂等 |
| `git diff --check` | 通过 |

组合分支此前完成两题 `gpt-5.6-terra`、`high` 真实写稿与独立匿名盲审：相对固定 1.5.36 为 2 胜 0 负，全部稿件的事实、数字、主体、状态和输出模式通过硬检查。详细原始结果见 `1.5.37-integration-anti-ai-lint-result-20260805.md`。

## 剩余风险

1. 真实组合回归为两题，能够验证本轮两项直接交互，不能据此宣称所有文种的统计性提升。
2. writer 自然调用 lint 时仍可能采用 generic 参数；本轮修复检测精度，没有改变调用模式。
3. lint 继续只提供定位线索，不自动改稿；材料原文、合法否定和保护性外扩的最终取舍仍由 Agent 结合语义完成。

## 发布边界

本记录只证明本地 1.5.37 候选可供后续发布决策使用。当前没有 GitHub 推送或 Release、ClawHub 上传、skillhub.cn 上传及公开传播回执。
