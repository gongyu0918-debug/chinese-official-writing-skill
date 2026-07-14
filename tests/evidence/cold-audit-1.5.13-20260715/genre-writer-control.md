# T13-T33 writer 控制指令与完成回报

## 用途

本文件补记主 agent 向 Writer C、Writer D 下发的共同控制条件，以及两名 writer 完成后的自报。各题完整 prompt、成稿和 `ROUTE` 保持在对应 writer 原始文件中，本文件不改写原始成稿。

## 共同控制条件

T13-T26、T27-T30、T31-T33 三轮均向 Writer C、Writer D 分别下发以下边界：

- 只从 detached 基线 `output/release-baselines/github-1.5.13-cold-audit/` 读取 v1.5.13 的 `chinese-official-writing/SKILL.md` 及按题实际命中的 references；
- 完整读取所选文件，不预读无关 reference；
- 不读取当前工作树实现、冷审总报告、其他 evidence、另一名 writer 或 verifier 输出；
- 不联网，不修改产品文件或 Prompt；
- 每题保存完整原 prompt、可直接交付的成稿和一条 `ROUTE`，并把 `WEB` 记为 `no`；
- Writer C、Writer D 写入不同文件，不互读，不暂存，不提交。

对应文件：

- T13-T26：`genre-matrix-writer-c.md`、`genre-matrix-writer-d.md`；
- T27-T30：`genre-gap-writer-c.md`、`genre-gap-writer-d.md`；
- T31-T33：`genre-final-writer-c.md`、`genre-final-writer-d.md`。

T1-T12 的控制指令已原样保存在 `baseline-writer-a.md` 开头；Writer B 使用同一任务包，其输出保存在 `baseline-writer-b.md`。

## 完成回报

- Writer C 在 T13-T26 完成后回报：14 个题目、原 prompt、成稿和 `ROUTE` 齐全，全程未联网，未读取当前实现或其他 evidence；T27-T30、T31-T33 完成后再次回报结构完整、未联网、未暂存或提交。
- Writer D 在三轮完成后分别回报题目、prompt、成稿、`ROUTE`、`WEB=no` 数量一致，未联网，未读取另一名 writer、verifier、总报告或当前实现，`git diff --check` 退出码为 0。

## 证据限制

以上内容记录实际下发的任务协议和 writer 完成自报，不是操作系统级文件访问日志，也不能独立证明进程没有读取其他路径。冷审结论只把它作为隔离执行的协议证据；具体内容质量由与 writer 分离的 verifier 按原 prompt 和成稿判定，`ROUTE` 仍只按自报统计。
