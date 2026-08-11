# 外部 scene-lint 合并包隔离审计（2026-08-01）

## 裁决

`NEEDS-REPAIR / NO MERGE`。

桌面外部包提出的两条 `scene-filler` 检测规则具有继续做原子候选的价值，但包本身不具备直接并入当前主线的证据条件。本记录只保存审计结论，不合入外部产品代码。

## 来源与可复核性

- 对象：`中文公文写作-1.5.32-scene-lint-证据与合并包-20260801.rar`。
- SHA-256：`E43F63D3B8EB99EDA466A1A29CBB0C87F786CB81EFB4A1A0F5C48B3BDEA6C840`。
- 解包检查未见嵌套压缩包、路径穿越、重解析点、联网或子进程调用。
- 包内声称的提交 `45e3a19`、`2045d6e` 不在当前 Git 对象库，包内也没有可核验的 Git bundle。
- 包内 Baseline 缺少 `references/delivery-review-gate.md`、`scripts/gate_stop_hook.py` 和 `scripts/review_gate.py`，不是完整 current main。

## 隔离复验

- Candidate 相对包内 Baseline 的实际产品差异为 `prose_lint.py` 中两条全局 `scene-filler` pattern，外加镜像和证据文件。
- 从当前 `origin/main=cdb74bf` 的隔离副本应用六份产品 hunk 后，既有 407 项单测通过。
- 7 个 medium、5 个 low 定向词均命中；12 条 clean corpus、28 个历史稿均无新增命中。
- 包内新闻样本命中 3 处；正常事实表达“在工作人员指导下”产生 1 个 low 提示。
- 外部包没有提供可复跑的 T1—T6 原始 Prompt 和盲审回执，也没有报告、方案、可研只审三类定向回归。

## 可复用边界

后续如继续，只从当前主线重建“两条 pattern＋正反例单测”的独立候选，并先处理合法表述的提示成本，再补报告、方案和可研只审回归。外部包的提交声明、Baseline arm、硬编码 runner、版本文件和结论性文档不直接复用。

本候选与方案叶、报告叶、可研只审叶保持隔离，不据本次静态检测结果推断真实写稿质量。
