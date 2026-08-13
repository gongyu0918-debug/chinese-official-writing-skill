# 维护区

本目录保存仓库测试、评测、构建工具和证据，不属于普通 Skill 的运行上下文。

| 路径 | 用途 |
| --- | --- |
| `tools/` | 同步、清洁包构建、Hook companion 临时组装、消融与证据生成工具 |
| `evals/official-writing/` | Promptfoo 写稿评测入口与 provider |
| `evals/ai-dedupe/` | AI 味、重复和同质化检查说明及本地扫描工具 |
| `tests/` | 单元测试、fixture、预注册和真实执行证据 |
| `docs/evidence/` | 发布与维护历史索引 |
| `docs/待办.md` | 当前已完成事项、未闭环验证、后续独立原子和明确边界 |

## 工具索引

| 文件 | 用途 |
| --- | --- |
| `tools/sync_adapters.py` | 从 canonical 同步普通平台兼容包 |
| `tools/build_skillhub_package.py` | 构建 SkillHub 清洁包 |
| `tools/assemble_hook_companion.py` | 在临时目录或明确授权的目标目录按静态清单组装单一宿主 companion；不安装、不启用、不联网 |
| `tools/build_v162_cold_audit_packet.py` | 构建 v1.6.0 到 v1.6.2 的只读冷审差异包 |
| `tools/preflight_claude_hooks.py` | 校验 Claude Code companion 结构与版本 |
| `tools/check_ab_provenance.py` | 检查 A/B 证据来源绑定 |
| `tools/deterministic_capture.py` | 保存确定性评测捕获结果 |
| `tools/run_ablation.py` | 运行基础消融 |
| `tools/run_agent_ablation.py` | 运行 Agent 写作消融 |
| `tools/run_real_prompt_ablation.py` | 运行不调用 LLM 的真实题面确定性门 |
| `tools/run_real_article_eval.py` | 运行真实文章评测 |
| `tools/run_revision_instruction_eval.py` | 运行二次修改指令评测 |
| `tools/build_agent_eval_packet.py` | 构建 Agent 评测包 |

发布事实和历史证据从 `docs/evidence/README.md` 进入；真实写稿原始记录从对应 `tests/evidence/` 预注册或结果文件进入。
