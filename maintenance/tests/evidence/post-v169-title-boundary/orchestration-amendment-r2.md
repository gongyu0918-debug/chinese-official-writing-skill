# 标题边界真实写稿 R2 编排修订

R1 在两个 provider 的首个基线臂均于本地 CLI 参数检查阶段退出，stderr 同为 `No prompt provided via stdin.`，stdout 为空、终稿不存在。没有形成模型请求或写稿结果，整轮记为 `ENV_ORCHESTRATION_INVALID`，不得计入样本，也不将其称为模型重试。

R2 唯一修订是把同一 prompt 从 PowerShell 管道输入改为 Codex CLI 的位置参数。模型、`max` 档位、四个任务、固定基线与候选、ABBA 顺序、零模型重试和判定标准均不变；R2 使用新的空输出目录一次性执行。
