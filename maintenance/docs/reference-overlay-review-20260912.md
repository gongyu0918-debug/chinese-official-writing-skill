# 场景附加叶复核（2026-09-12）

附加叶只在主文种和交付模式已经确定后加载。它补充一个稳定的应用场景或局部交付条件，不承担主文种骨架，也不因一个泛关键词命中。

## 保留为附加叶

| 页面 | 触发 | 主文种仍由谁负责 | 备注 |
| --- | --- | --- | --- |
| `ai-compute-docs.md` | 算力、GPU、模型推理/训练、智算中心、Token、并发或模型服务等组合信号 | 报告、方案、采购或技术材料页 | 唯一算力场景叶；安全、SLA、验收单独出现不触发 |
| `speech-person-order.md` | 讲话、致辞、演讲等正文需要安排具体人物称谓/开场顺序 | `genre-playbook-speech-address.md` | 只处理开场称谓顺序，不改变讲话骨架；普通讲话不自动读取 |

`technical-terms.md`、`ai-compute-examples.md`是算力叶的二级资料，不是独立路由；只有术语统一或需要示例时继续读取。

整改进展/整改情况报告和反馈情况报告是报告主文种上的事务附加页，不是新的文种骨架；成稿直交付是交付模式附加页，不参与文种选择。

当前旧规则中没有一套独立的“领导讲话”规则页。`genre-playbook-speech-address.md` 已承担讲话的场合、身份、听众、事实基础和任务要求；`formal-addressing.md` 与 `speech-person-order.md` 分别承担关系称谓和具体人物排序。因而普通讲话只读讲话主叶，只有用户明确要求领导身份口吻、领导开场称谓或领导讲话专项校审时，才在现有能力页上按需叠加；不为此新造一个空的领导讲话页。后续若出现一组稳定、已有实证且不能归入上述页面的领导讲话规则，再以同题 A/B 证明后增页。

## 保持为模式或能力页

- `short-draft-naturalness.md`、`compression-details.md`：篇幅和压缩是交付模式，不是应用场景。
- `format-gbt9704.md`、`prose-lint-usage.md`、`delivery-review-gate.md`：格式、脚本、Hook 是交付工具，不能改变主文种。
- `anti-ai-patterns.md`、`proofreading-checklist.md`、`final-review-layers.md`、`review-checklist.md`：终稿质量能力，按复核信号叠加。
- `external-research.md`、`formal-addressing.md`、`formulaic-language.md`、`handling-elements.md`、`argument-chains.md`：共性能力或资料条件；不要为字符数改造成场景页。
- `compatibility-scene-routing.md`、`genre-routing.md`、`genre-playbooks.md`：路由页或兼容分流页，不能作为附加规则承载完整骨架。

新闻消息和新闻评论保留为独立文种页；它们不是附加叶。任何新增附加叶都必须先证明触发信号稳定、无关伴读减少，并通过同题主文种 A/B，才能接入索引。
