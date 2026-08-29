# HK-004 CLI R1 Hook 三路独立冷审

日期：2026-08-30。固定对象为公开 `main@7b59ee0e650ea65c25c2f3246dfc4c422c264e15` 与证据提交 `29b85894f7606343e79cbc0bd6835be5d08d1508`。三路均在独立 Codex Desktop 任务中只读审查 Git 对象、原始回执与官方宿主协议；不写新稿、不修改产品、不查阅其他审稿任务结论，思考强度均为 ultra。

| 审稿模型 | Codex 任务 | 独立终判 | 可复现要点 |
| --- | --- | --- | --- |
| Alibaba Token Plan 2 Qwen3.8 Max | `01a04e42-b7f4-7393-9d09-7f5414f5144f` | `PASS_WITH_RISKS` | 五条S2正文计数在排除独立标题后成立；十份S1正文后续10/10直读均不薄；产品与Hook core 0差异；本机Pro终审在非公文审稿报告上触发且只给问题代码、无位置，作为本机付费Hook作用域观察，不外推到公开core |
| xAI Grok 4.6 | `01a04e42-b7f4-7393-9d09-7f3fb787f149` | `PASS_WITH_RISKS` | 未发现Hook core阻断缺陷；Qwen 0.22.3应降级普通Skill；CodeBuddy 2.141.0隔离证据和provider注入被过述；Kimi/OpenCode/OpenClaw精确失败分类成立；一宿主一profile与可移植终态记录仍需加强 |
| Ollama Cloud Kimi K3 | `01a04e42-b7f4-7393-9d09-7f1bea5e1668` | `PASS_WITH_RISKS` | 自纠正标题计数误判后确认S2范围；Qwen Hook/无Hook消融成立；Kimi D0本身不安全，不能把选D0写成安全；OpenCode 1.18.25不能继承1.18.23；CodeBuddy当时缺可提交生命周期记录 |

## 交叉裁决

1. 三路一致：没有本轮引入的 Hook core 阻断问题；`29b85894` 对产品、core、adapter、references、description 均为0差异；Qwen 0.22.3没有安全的正文替换/撤回控制点，只推荐普通 Skill；Kimi 0.39.1、OpenCode 1.18.25、OpenClaw不能继承旧版本或内容生成成功。
2. 接受 CodeBuddy 证据范围异议。全局 `CODEBUDDY_PLUGIN_DATA` 记录能与同 session、同终稿 SHA-256 精确绑定，足以证明真实 profile 一次 Stop、emit、delivery verification 和脱敏；但运行没有隔离 data root，stdout 显示 `apiKeySource=copilot.tencent.com`，必要 reference 读取被拒，因此不再称 `CURRENT_CLI_PASS` 或“OpenCodex注入已证明”。状态改为 `CURRENT_REAL_PROFILE_LIFECYCLE_PASS / REFERENCE_READ_DENIED / PROVIDER_INJECTION_UNVERIFIED`。
3. 对 CodeBuddy 终稿“依托现有设备难以在预定时间内完成扫描”采用不过严裁决：它没有新增具体日期、时长或数字，不按硬完成期限失败；但材料未明示存在“预定时间”，故记单 provider 软性无依据时间框架，并从“无条件事实状态质量PASS”中剔除。短稿结论由四家无争议当前 companion、Qwen无Hook消融及其他跨文种样本继续支撑。
4. Qwen 审稿任务上的本机 Pro Hook 误触属于 `official-writing-pro-local@0.3.0` 的独立观察，不是本轮公开产品 diff；当前公开 core 不因该样本修改。

## 官方协议

- Qwen Code Hooks：<https://qwenlm.github.io/qwen-code-docs/en/users/features/hooks/>
- CodeBuddy CLI Hooks：<https://www.codebuddy.ai/docs/cli/hooks>

三路审稿任务均已形成最终回答。Kimi 任务意外留下的未跟踪 `.cmprd` 临时镜像和可视化临时目录已在核对精确路径后删除；未删除任何产品、证据或用户既有文件。Grok 与 Qwen 审稿 worktree 保持干净。
