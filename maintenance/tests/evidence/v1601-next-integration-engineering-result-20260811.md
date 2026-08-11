# v1.6.0 后续组合工程验证

日期：2026-08-11

固定基线：`9abc48794ebf82b8e918c593ebdada8cc080fe61`

产品检查点：`0692292b1378eb86d70014b3d7a5cc130b0da43a`

分支：`codex/v1601-next-integration`

## 组合范围

本组合只纳入：

- 根 `AGENTS.md` 工程控制面去重和历史归档；
- Codex Hook 生命周期入口迁入专属 `hooks/`，并把交付门禁资产限制在 canonical 与 Codex 插件表面；
- 在既有 anti-AI 高频表达复核线索中增加 `先……再……`。

没有纳入 description、`收束` 自然化、`顺稿` 自然化，也没有带入对应预注册、真实写稿、盲审或运行结果文件。A1 只作为用户明确要求的复核线索功能纳入；独立真实 A/B 未证明质量提升，本记录不作质量收益声明。

## 第五提交暂停审查

`0692292b` 是本组合相对固定 main 的第 5 个提交。按根 `AGENTS.md` 暂停继续开发，完成轻量 review、精确基线比较和完整回归后，才新增本结果记录。

- 相对固定 main：26 个文件，281 行增加、11710 行删除，净减少 11429 行。
- 第 5 提交相对前一检查点 `f1346978`：7 个文件，8 行增加、6 行删除；产品变化仅为六份同文 `anti-ai-patterns.md` 各增加一个 `先……再……` 线索，另有两条边界断言。
- canonical `SKILL.md` 未变化；canonical references 只变化 `anti-ai-patterns.md`，未混入 description、A2 或 A3。
- `tests/evidence/` 中没有带入本轮预注册、盲审和真实运行证据。
- `references/delivery-review-gate.md`、`hooks/gate_stop_hook.py`、`scripts/review_gate.py` 只保留在 canonical 与 Codex 插件 Skill 表面；`.agents`、`.qwen`、Hermes 和 OpenClaw/ClawHub 镜像均不含这些文件。
- SkillHub clean package allowlist 为 33 个文件，包含三项 Codex 门禁资产，不包含 `agents/openai.yaml`。

## 实际验证

| 检查 | 实际结果 |
| --- | --- |
| `python -B -m unittest tests.test_agents_control_plane tests.test_gate_stop_hook tests.test_skill_boundary` | 89/89 通过 |
| `python -B -m unittest discover -s tests` | 479/479 通过 |
| `$env:OFFICIAL_WRITING_EVAL_STUB='1'; npm.cmd run eval:official-writing:smoke` | 20/20 通过，0 failed、0 errors，eval `eval-18C-2026-08-11T05:49:42` |
| 固定 main 确定性消融 | `main-9abc4879` 111/111，current 111/111 |
| Skill Creator `quick_validate.py chinese-official-writing` | `Skill is valid!` |
| Plugin Creator `validate_plugin.py .` | 通过 |
| 相关 Hook、review gate、prose lint 与 adapter sync 脚本编译 | 有效复跑 7/7 通过 |
| 镜像、Codex/ClawHub 门禁边界、33 文件 allowlist、插件版本和 Hook 路径专项 | 4/4 通过 |
| `tools/sync_adapters.py` 连续两次 | 两次同步后摘要均为 `3ce7476bf9b253bb2518b3ec450c7b48e5e0e8e9`，幂等 |
| `git diff --check` | 通过 |
| 最终工作树状态 | 提交前仅本结果文件，产品树无漂移 |

首次脚本编译命令为避免落盘把 `py_compile` 的输出指向 Windows `NUL`，`py_compile` 因目标不是普通文件返回 `FileExistsError`。该失败发生在写入任何字节码之前，不是产品编译失败；随后改用系统临时目录逐个编译同一组 7 个文件，全部通过，临时目录退出后自动清理。

## 结论与剩余风险

第 5 提交后的暂停 review 和完整工程回归通过，组合可继续作为下一阶段集成基线。确定性工程门和 stub smoke 不能替代真实模型质量判断；A1 仅具备 feature-only 资格，不声称降低了 `先……再……` 的实际出现率。description、A2 和 A3 仍在组合范围外。
