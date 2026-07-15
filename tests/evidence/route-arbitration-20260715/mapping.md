# A/B 揭盲映射

- Writer C：A = 固定 `v1.5.13` 基线；B = current。
- Writer D：A = current；B = 固定 `v1.5.13` 基线。
- 固定基线目录：`output/release-baselines/github-1.5.13-cold-audit`。
- 固定基线提交：`cd2d46c58a5f56b9009c5da08626a88640f2e5b3`。

盲审完成后才按本表揭盲。`verifier-blind.md` 未读取本文件，也未推断 A/B 对应版本。

揭盲结果：盲审记录的两份 route over-read 分别为 Writer C 的 R1-A、Writer D 的 R1-B，均属于固定 `v1.5.13` 基线。current 的两份 R1 均只读取 `SKILL.md` 和 `references/task-route-cards.md`。
