# WR-028 相关 reference 审计

## 与候选直接相关

1. **路由缺口**：`SKILL.md` 只有普通方案叶入口，整改方案会落入约 1 KB 的通用骨架；没有一处同时说明问题—措施对应、未启动/进行中/完成状态、原因证据强度和未来措施授权。
2. **规则碰撞**：`SKILL.md`、`information-selection.md` 对润色、情况说明和材料外处置的保护是正确的，但在用户明确授权制定本单位整改方案时，模型容易把“不得新增处置”误读为不得设计未来措施。应由专项叶给出窄边界，不修改通用事实规则。
3. **短稿误压**：`short-draft-naturalness.md` 正确禁止为凑上限补流程；整改短稿仍须完成措施功能并保留已给整改状态。专项叶应说明短稿压缩目录和同源事项，不删整改措施或明示未决状态。
4. **固定骨架风险**：`genre-checklist.md`、`handling-elements.md` 和普通方案叶把责任、进度、保障、验收列作常见要素，模型容易进一步套出专班、销号、月报、第一责任人和精确子节点。专项叶应以任务复杂度和材料授权决定粒度，不把这些表面结构设为必备。
5. **控制边界**：整改进展报告、情况说明、投诉/问题反映和普通实施方案已有“不另拟整改方案”保护，方向正确；新增路由必须依赖用户明确的“制定整改方案”意图，而不能只看正文出现“整改”。

## 暂不随候选修改的观察

- 普通实施方案基线仍可能补造回退方案、旧系统并行、培训和咨询点。这是通用方案叶的既有问题，和整改专叶 diff 无关；另行登记反例后再做真稿原子，不在 WR-028 顺手扩写。
- `review-checklist.md` 约 16.5 KB、`handling-elements.md` 约 8.1 KB、`genre-checklist.md` 约 7.4 KB，显式整改方案若仍叠读会增加无关上下文。先观察直达专叶后的真实读取；只有候选稿已经通过且仍跨 provider 多读，才考虑减载，不把读量优化与正文规则同时修改。
- `SKILL.md` 的通用起草边界和 `information-selection.md` 不应为整改方案全局放宽，否则会把情况说明、投诉、审稿和正式化改写重新暴露给材料外整改动作。

## 结构检查

- 扫描 canonical 产品 50 个 Markdown 文件，共识别 34 个 `references/*.md` 引用。
- 未发现指向不存在文件的内部 reference 链接。
- 未发现未被 canonical Markdown 引用的孤儿 reference 文件。

## 本轮横向检查

- canonical references 体积最大的四页是 `review-checklist.md` 16,510 bytes、`workflow.md` 15,443 bytes、`delivery-review-gate.md` 14,544 bytes、`anti-ai-patterns.md` 14,162 bytes。仅有文件较长不能形成拆叶候选；既往 `REVIEW-LAYER-SPLIT-R1` 因真实路由0/10与0/5已经终止，没有新的跨 provider 读取证据时不复活旧机制。
- 没有在普通语义叶中发现 `HOLD`、发布状态、候选验证或维护命令残留。`delivery-review-gate.md` 中的 Hook、脚本和状态机说明属于明确的宿主协议页，普通写稿不加载，不应与普通 reference 减载混为一谈。
- 仍有三组数字值得独立验证而不是因“看起来像魔法数字”直接删除：`workflow.md` 的5%—10%上限余量与章节百分比分配、`genre-playbook-news-commentary.md` 的90%—110%约字范围、`delivery-review-gate.md` 的20字/5%机械净增量。前两组会影响真实篇幅和长稿结构，后者只影响 Hook；应分别固定真实任务做 A/B，不能组合修改。
- R2 新出现 Alibaba1、Ollama 两份正文前过程说明，已达到 `CL-001-NOHK-R2` 的跨 provider 新反例条件；该问题与整改状态句无关，另开正文交付原子。MiniMax 单家读取9份 reference 的过载尚未跨 provider 复现，只登记观察。

## 候选处理范围

只新增 `references/genre-playbook-remediation-plan.md`，并在 canonical `SKILL.md` 增加明确意图直达和表项。R2 另在专叶强化一处材料状态先落位。候选不改 description、Hook、通用短稿页、通用事实边界、普通方案叶或其他文种叶。
