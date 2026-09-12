# Reference 重写覆盖台账（2026-09-12）

本台账只记录文件级覆盖，不把“文件已改”当作“功能已证明等价”。基线是 `main@1ce71123`，候选架构基线为 `ab9bdd1d`。main 有 50 个 reference，候选保留 49 个并删除 1 个已被替代的混合目录；当前候选字节数和语义覆盖仍需以逐页映射及组合实写闭合，不能由字符变化直接推定等价。完整逐页归属见 `maintenance/docs/reference-rewrite-page-map-20260912.md`。

## 已重写但仍需语义/实写验收

| 基线页面 | 候选归位 | 主要语义范围 | 当前状态 |
| --- | --- | --- | --- |
| `SKILL.md` | `SKILL.md` | 触发、模式、事实状态、正文交付、Hook 边界 | 新契约已写；正文洁净 A/B 仍需复测 |
| `reference-index.md` | 同名页 | 模式→主文种→共性页→停止点 | 静态通过；组合路由待矩阵 |
| `genre-routing.md` | 同名页 | 文种、行文关系、混合材料判定 | 静态通过；跨文种待实写 |
| `task-route-cards.md` | 同名页 | 稀疏材料、短通知、局部修改短路 | 静态通过；旧边界测试待迁移 |
| `genre-checklist.md` | 同名页 | 未覆盖文种功能反查 | 结构已收束；覆盖缺口待盘点 |
| `genre-playbooks.md` | 已删除 | 旧混合目录跳转 | 功能由专页、`genre-routing.md` 和 `genre-checklist.md` 替代，需验证无旧路由残留 |
| `workflow.md` | 同名页 | 起草、改稿、压缩、复核、交付、停止 | 已重写；真实组合待验 |
| `information-selection.md` | 同名页 | 事实、分析、状态、缺项、二次修改 | 已重写；事实保真待验 |
| `handling-elements.md` | 同名页 | 主体、对象、依据、期限、责任、附件等 | 已重写；字段/采购组合待验 |
| `argument-chains.md` | 同名页 | 事实→判断→事项论证 | 已重写；可研/方案组合待验 |
| `official-style.md` | 同名页 | 正式、平实、去口语表达 | 已重写；自然度待验 |
| `formal-addressing.md` | 同名页 | 称谓、关系、敬谦语 | 已重写；讲话/函件待验 |
| `formulaic-language.md` | 同名页 | 开端、来文、承启、固定收束、历史模板 | 已收束；文种功能衔接待验 |
| `anti-ai-patterns.md` | 同名页 | 旁白、教学腔、包装、状态升级 | 已压缩；旧表达覆盖待审 |
| `proofreading-checklist.md` | 同名页 | 引用、数字、日期、术语、稿内一致性 | 已压缩；校对组合待验 |
| `final-review-layers.md` | 同名页 | 硬边界、稿内质量、场景交付 | 已重写；门禁边界待验 |
| `review-checklist.md` | 同名页 | 段落、小节、全文综合复核 | 已压缩；旧审校范围待验 |
| `ai-compute-docs.md` | 同名页 | 算力需求、成本、技术、SLA、安全、验收 | 单一附加页已回填；组合 A/B 曾因共有旁白不通过，需重跑 |
| `prose-lint-usage.md` | 同名页 | 脚本路径、参数、结果解释 | 已重写；真实调用待验 |

## 轻改或保留语义的新文种页

以下页面本轮没有整体重写，只做了边界性修改或保留已有实证语义：`genre-playbook-deliberation-deployment.md`、`genre-playbook-minutes.md`、`genre-playbook-notice-publication.md`、`genre-playbook-procurement-review.md`、`genre-playbook-request.md`。它们仍需与新入口逐一做组合写稿，不得因文件未大改就视为自动通过。

## 当前保留、尚未纳入本批语义重写的页面

`ai-compute-examples.md`、`compatibility-scene-routing.md`、`compression-details.md`、`delivery-review-gate.md`、`external-research.md`、`field-editing.md`、`format-gbt9704.md`、`genre-checklist-feasibility-review.md`、`genre-checklist-report.md`、`genre-checklist-request.md`、`genre-playbook-advisory-feedback.md`、`genre-playbook-complaint-reflection.md`、`genre-playbook-correspondence.md`、`genre-playbook-institution-rules.md`、`genre-playbook-news-commentary.md`、`genre-playbook-news-message.md`、`genre-playbook-plan-construction.md`、`genre-playbook-project-application.md`、`genre-playbook-remediation-plan.md`、`genre-playbook-research-feasibility.md`、`genre-playbook-speech-address.md`、`genre-playbook-work-summary.md`、`review-direct-checklist.md`、`short-draft-naturalness.md`、`speech-person-order.md`、`structure-editing.md`、`technical-terms.md`。

其中 `delivery-review-gate.md` 与 Hook 门禁绑定，Hook 目录冻结；新闻、新闻评论及已有实证单文种页优先保留，但仍要检查新路由是否漏读或多读。保留不等于免审，后续按主文种、模式和附加页组合验证。

## 测试状态

- 新增重写契约与 reachability 测试：24 项通过。
- Skill frontmatter/脚手架校验：通过。
- Hook 目录相对 main：无差异。
- 算力报告同题技术 A/B：R3 在 `alibaba-token-plan-2/qwen3.8-flash` 完成，两臂 receipt 有效，候选读取 6 页、基线读取 8 页；摘要已留档，尚不足以代表五通道组合验收。
- 旧 `test_skill_boundary` 与 `test_real_prompt_ablation`：94 项中 78 项失败、3 项错误，主要绑定重写前标题、旧路由文本和旧确定性输出；尚未迁移完成。

因此，本台账当前结论是“部分重写、部分验证”，不是“全量功能等价”或“可合并”。
