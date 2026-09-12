# SKILL/reference 整体重写映射（2026-09-12）

本映射以当前 `main@1ce71123` 的 canonical `SKILL.md` 与 50 个 reference 为源，不以旧文件名或历史分支的拆分结果直接当作新架构。每条规则先归类，再写入一个唯一职责的页面；已经真实验证且职责单一的新叶只复用，不重复改写。

## A. 直接复用的新叶

以下页面职责单一、已有真实写稿或路由证据，本轮保留正文语义，只重新接入新索引：

- `genre-playbook-news-message.md`
- `genre-playbook-news-commentary.md`
- `genre-playbook-advisory-feedback.md`
- `genre-playbook-complaint-reflection.md`
- `genre-playbook-remediation-plan.md`
- `genre-playbook-project-application.md`
- `genre-playbook-institution-rules.md`
- `genre-playbook-notice-publication.md`
- `genre-playbook-deliberation-deployment.md`
- `genre-playbook-speech-address.md`
- `genre-playbook-research-feasibility.md`
- `genre-playbook-procurement-review.md`
- `genre-playbook-correspondence.md`
- `genre-playbook-minutes.md`
- `speech-person-order.md`
- `compatibility-scene-routing.md`

## B. 共享核心重写

这些页面承担旧入口、混合规则或重复总审，改为短合同和明确停止条件：

| 旧页面 | 新职责 | 处理方式 |
| --- | --- | --- |
| `SKILL.md` | 触发、四类任务模式、核心事实边界、交付形态、最终回收 | 重写为最小主入口；不重复展开专叶规则 |
| `reference-index.md` | 唯一路由表和停止条件 | 重写为“任务信号→唯一首叶→允许叠加→停止” |
| `genre-routing.md` | 文种与行文关系判定 | 删除重复骨架，只保留判定树和冲突处理 |
| `workflow.md` | 起草/改稿/复核/排版的共用动作 | 只保留跨文种动作，字段、结构、压缩移回专页 |
| `information-selection.md` | 事实、分析、状态、缺项和来源边界 | 保留为全任务唯一事实选择契约 |
| `handling-elements.md` | 办理要素抽取与缺项登记 | 删除文种长清单，改由文种叶补充 |
| `argument-chains.md` | 论证动作选择 | 按“事实→判断→事项”组织，删除文种重复模板 |
| `final-review-layers.md` | 终稿硬门和复核顺序 | 只保留硬门、正文洁净和停止条件 |
| `review-checklist.md` | 综合审稿任务专用 | 不再重复入口硬边界和脚本说明 |
| `anti-ai-patterns.md` | 语言风险语义判断 | 保留反例和语义边界，删除通用交付契约重复 |
| `proofreading-checklist.md` | 轻量校对 | 只保留语言、引用和稿内一致性 |
| `task-route-cards.md` | 轻量任务是否可短路 | 删除会议纪要专属规则，改为通用短路判定 |

## C. 混合旧叶重写

### `genre-checklist.md`

不再承载二十多个文种的完整骨架。保留一个短的文种功能反查页；通知、决定、函、公示、采购公告、会议纪要、讲话、调研、方案等均回指各自专叶。文种专叶未覆盖的法定文种只保留功能判定，不复制成稿模板。

### `ai-compute-docs.md`

保留为一个场景附加叶，不把“算力可研、采购/租赁、技术需求”做成三套并列路由。先由主文种页决定报告、方案、采购或技术材料的交付骨架，再在确有算力信号时叠加本页；本页只补需求口径、成本路径、服务条件、SLA、安全和验收的算力表达。术语表和段落示例继续按需叠加，不随普通报告、方案或采购稿自动加载。

## D. 规则归位原则

1. 一个规则只在一个 canonical 页面承担正文；其他页面只写触发条件和链接。
2. 文种叶只写文种功能、结构和该文种的事实边界，不写全局事实规则。
3. 全局硬边界只保留在 `SKILL.md` 与最终交付契约，质量建议不升级成硬门。
4. 轻量任务卡只决定是否短路，不复制任何会议、通知或报告专属规则。
5. 每个路由都必须给出停止点；没有停止点的“可按需读取”不算完成路由。
6. 规则优先用正向动作表达：写什么、保留什么、何时转读；只有无法表达安全边界时才使用连续的“不/不得”限制。
7. 新叶的事实语义、未决状态、称谓和新旧文种衔接以当前 main 真实证据为锚，不因重写追求短而改变。

## E. 验证顺序

1. 先做旧规则到新页面的语义映射和链接图，确认每条旧规则至少有一个新归属。
2. 再跑确定性路由、引用可达性、镜像和旧反例门。
3. 再做同题真实写稿 A/B，记录实际读取集合和停点，不以文件字符数代替。
4. 最后按五条当前便宜通道扩展文种组合；出现候选独有事实、状态、文种或必要内容硬回退即暂停。

本文件是重写工作底图，不表示产品已经改写或可以合并。
