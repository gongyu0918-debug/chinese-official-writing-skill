# MT-006 运行时语义 Reference 减载 R1

## 结论

候选分成两类处理：

1. 建议对象与处置权、共性问题归并、正式稿直接交付等会改变成稿的正向语义，完成五条低成本路线的真实写稿 A/B 和一次最小修复复跑。
2. 重复的“不属于哪些意见”、`不会新增模型/API/脚本门`、`不改变 prose_lint` 等维护声明，只删除运行时冗余，不改变写稿决策；按用户校准不再为其单独消耗真实写稿，只做语义保留断言、镜像一致性和最小校验。

所选候选相对 `main@f574c06d4586eea17d78911cf40e12114e479656` 共减少 canonical 运行时文件 2,926 bytes；不改 Hook、description 和发行结构。候选已 fast-forward 合入 `main@b484c4ad45578f930cbdbe33ec3a55a9c8322585`，当前状态为 `REAL_WRITING_PASSED / ENGINEERING_VERIFIED / MERGED_MAIN / RELEASE_CANDIDATE_V1.6.26`。

## 范围与字节变化

| 文件 | 基线 bytes | 候选 bytes | 减少 |
| --- | ---: | ---: | ---: |
| `SKILL.md` | 26,634 | 26,569 | 65 |
| `genre-checklist-report.md` | 3,269 | 2,876 | 393 |
| `genre-playbook-advisory-feedback.md` | 6,733 | 5,475 | 1,258 |
| `genre-playbook-complaint-reflection.md` | 4,933 | 4,611 | 322 |
| `genre-playbook-plan-construction.md` | 1,307 | 1,032 | 275 |
| `proofreading-checklist.md` | 4,434 | 3,821 | 613 |

这些数字是仓库 canonical 文件的净变化，不冒充每个任务都会同时省读 2,926 bytes。实际单次收益取决于任务读取的叶子。

## 真实写稿

测试使用 Codex CLI 0.144.6，隔离导出对应提交的 Skill，五条路线均使用 `max`：

- `alibaba-token-plan-2/deepseek-v4-flash-0731`
- `alibaba-token-plan/deepseek-v4-flash-0731`
- `ollama-cloud/deepseek-v4-flash:0731`
- `opencode-go/deepseek-v4-flash`
- `minimax-cn/MiniMax-M3`

R2 比较 `d071078c9ce927ad4e20fe55518d1b0790b38367` 与 `f77f099331d776fd62a837679b3a60ef8634325c`，覆盖多对象意见建议、无可夸事实的建议反馈、第一方投诉、正式下行指导控制和收到投诉的内部说明，共 50 份输出。49 份技术有效；Ollama 的一份投诉候选出现用户 Skill 污染，只作无效样本。正向规则保留了处置权、未决状态和共性归并，正式下行控制未误转合作性语气，投诉候选也减少了正文外过程说明。但多对象建议候选有 3/5 在正文前附过程说明或分隔线，因此没有直接准入。

R3 只检验这一回退，比较 `8e5fa758b63e6967b92901bfab9f09c4079e98ca` 与最小修复 `3a612187c3c64f5426f017715b4266f67c3284b7`。五家 10 份输出全部技术有效，候选 5/5 从标题或事实铺垫直接进入正文，0/5 附过程说明、分隔线或代码围栏；审核部门与平台运营方的权限、六项材料、20MB/PDF/CSV/ZIP、主体关系和未决状态均以原词或等义表达保留，正文均长于提示词和事实材料。

R3 自动规则报出 4 个 raw hard failure，其中 3 个来自逐字匹配未识别`有待研究确定`、`尚未确定`等未决等义表达，另 1 个来自基线 MiniMax 的代码围栏；人工逐稿复核后均不是候选目标硬回退。MiniMax 候选仍有材料外日期、泛化说明或配合表态的单模型波动，但该问题不是本次正向单句修复导致，记为既有模型风险，不据此把合理的一层归因、作用或条件性结论判为失败。

R2/R3 本地汇总 SHA-256：

- R2 `summary.json`：`62DCA7E897EF40BEC6F3A817EE3D63E710C06FC88E66DD095A68FAC138149EE4`
- R3 `summary.json`：`963065B1443F1BC5E3F19990F12BBE52DB4DE3739364F394C5D9B801377B7696`

## 结构减载与工程验证

删除的维护性文字不再做独立五路 A/B；用直接断言确认保留以下产品语义：合作性建议与正式权力关系仍分流，建议对象和处置权仍明确，第一方投诉路由仍存在，事实/状态/请求边界仍保留，校对脚本仍只作提示。

已运行：

```text
python -m unittest maintenance.tests.test_advisory_feedback_leaf maintenance.tests.test_complaint_reflection_leaf maintenance.tests.test_skill_boundary
Ran 92 tests ... OK

python C:\Users\admin\.codex\skills\.system\skill-creator\scripts\quick_validate.py <skill-dir>
canonical、agent-skills、qwen-code、qwenwork、hermes：5/5 valid
```

OpenClaw 镜像按其既有 manifest 使用 `category` 扩展字段，通用 Codex validator 会报该字段不在白名单，仍由仓库的 OpenClaw 专项契约和 92 项定向测试验证，不把通用 validator 的宿主差异写成产品失败。

## 未纳入本原子的项目

- `task-route-cards.md` 的固定 `800字以上` 与 `review-checklist.md` 的 260/300/500、5—10% 等数字是独立魔法数字原子，需要另做真实任务验证。
- `final-review-layers.md`、`review-checklist.md` 中更早的重复维护语句未随手批量删除，避免把本次范围扩大成不可归因的大清理。
- 当前候选已合并本地 `main`，尚未推送或发布；v1.6.26 发行工作树将在发布前运行一次仓库全量门。
