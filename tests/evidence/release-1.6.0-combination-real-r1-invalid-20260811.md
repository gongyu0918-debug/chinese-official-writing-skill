# 1.6.0 组合真实回归 R1 技术无效记录

日期：2026-08-11

R1 运行目录为 `output/release-1.6.0-combination-real/`。两家 provider、五题、两臂共 20 次调用均形成首个 final，return code 均为 0、无超时、无模型重试，但 0/10 配对有效，不进入匿名包或质量裁决。

统一原因是 Windows Codex CLI 的多行 prompt 以最后一个命令行参数传入后，模型只收到首段“第一步必须调用 shell_command 实际执行：”及以前内容，没有收到其后的具体读取命令和 W1—H2 任务。20 份 final 均要求用户补充任务，实际 JSONL 也只显示目录探查，没有按预注册读取规定叶子。

该问题属于 harness 传参错误，不是 Skill、provider 或模型质量失败。R1 的 final、trace、stderr 和 manifest 全部保留，不覆盖、不纳入裁判。修正方式是沿用已验证的 Codex CLI stdin 协议：命令末尾传 `-`，通过 UTF-8 stdin 提供完整 prompt；R2 使用全新输出目录和 mapping 文件，仍保持每个 arm 首个 final、零重试。
