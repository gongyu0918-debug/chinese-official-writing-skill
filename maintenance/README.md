# 维护区

本目录保存仓库测试、评测、构建工具和证据，不属于普通 Skill 的运行上下文。

| 路径 | 用途 |
| --- | --- |
| `tools/` | 同步、清洁包构建、规则审计、消融与证据生成工具 |
| `evals/official-writing/` | Promptfoo 写稿评测入口与 provider |
| `evals/ai-dedupe/` | AI 味、重复和同质化检查说明及本地扫描工具 |
| `tests/` | 单元测试、fixture、预注册和真实执行证据 |
| `docs/evidence/` | 发布与维护历史索引 |
| `docs/待办.md` | 当前已完成事项、未闭环验证、后续独立原子和明确边界 |
| [Hook 去向便条](docs/pro-hooks-next.md) | Hook 保存分支、许可界限与未来 Pro 接续；当前暂缓激活 |
| `specs/` | 长期产品需求、当前状态与需求到真实证据的轻量覆盖矩阵 |

## 工具索引

| 文件 | 用途 |
| --- | --- |
| `tools/sync_adapters.py` | 从 canonical 同步普通平台兼容包 |
| `tools/build_skillhub_package.py` | 构建 SkillHub 清洁包 |
| `tools/build_v162_cold_audit_packet.py` | 构建 v1.6.0 到 v1.6.2 的只读冷审差异包 |
| `tools/check_ab_provenance.py` | 检查 A/B 证据来源绑定 |
| `tools/audit_product_surface.py` | 检查产品规则中的工程命令和工具路由 |
| `tools/audit_reference_uniqueness.py` | 检查规则重复与交付路由位置 |
| `tools/validate_reference_manifest.py` | 核验维护区路由清单和产品页面对应关系 |
| `tools/deterministic_capture.py` | 保存确定性评测捕获结果 |
| `tools/run_ablation.py` | 运行基础消融 |
| `tools/run_agent_ablation.py` | 运行 Agent 写作消融 |
| `tools/run_real_prompt_ablation.py` | 运行不调用 LLM 的真实题面确定性门 |
| `tools/run_real_article_eval.py` | 运行真实文章评测 |
| `tools/run_revision_instruction_eval.py` | 运行二次修改指令评测 |
| `tools/build_agent_eval_packet.py` | 构建 Agent 评测包 |

产品需求与当前缺口先看 `specs/README.md`；发布事实和历史证据从 `docs/evidence/README.md` 进入；真实写稿原始记录从对应 `tests/evidence/` 预注册或结果文件进入。
