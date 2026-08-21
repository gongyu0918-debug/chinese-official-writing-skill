# SB-001 章节均衡真实顺稿终止记录

## 结论

`SB-001` 当前提示词/路由方向终止，产品不合入 main，不再以 HOLD 交付。目标本身有价值：多路稿件能把问题事实移入“存在问题”，把责任主体、期限和未决状态移入“下一步工作”，并保持短通知、采购申请不被段长门误伤；但 R3.1—R3.5 经过路由减载、底稿形态触发、输出隔离和近场卡后仍有候选独有硬回退。

最终 R3.5 中，Luna、Ollama、MiniMax 和 OpenCode 重试均完成目标搬移；Alibaba 出现正文前旁白、同一“存在问题”章节重复、A/C 整稿重复、把“尚未形成决定”改成“待核查后再行研究”，并夹入无关残片。OpenCode 首次只输出“以下交付”承诺而未给正文，重试才完成。按预登记停止边界，不再向第三处堆叠同义规则。

## 原子过程

- R3：在 `final-review-layers.md` 增加只搬移已有事实、保留主体/期限/状态、不按段长判失衡；MiniMax 形成目标改善，其他路线可达不稳。
- R3.1：补 `workflow.md + final-review-layers.md` 路由；引用负担增加，结果分化。
- R3.2：只转读 `final-review-layers.md`；Ollama、MiniMax 可精确搬移，Alibaba 仍有正文前说明。
- R3.3：让底稿形态也能触发；Luna、OpenCode、MiniMax通过，Alibaba只搬问题未搬责任，Ollama出现服务侧 `</think>` 泄漏并重复成稿。
- R3.4：增加路由过程与正文隔离；Luna通过，Alibaba跨题带入A稿单位并漏标题，Ollama未执行搬移。
- R3.5：把规则移到已稳定读取的近场任务卡并删除原叶重复；目标通过面扩大，但Alibaba硬回退和OpenCode首次未交稿触发停止。

## R3.5 Codex Desktop 样本

| 模型 | task | 结果 |
|---|---|---|
| Luna max | `01a025a4-3675-7871-a380-02af4bfd74b0` | 目标搬移，控制安全 |
| OpenCode Go DeepSeek V4 Pro max | `01a0259e-4be0-7823-8438-7b2de5297347` | 首次只交旁白、未交正文，质量失败 |
| OpenCode Go 重试 max | `01a025a4-365d-7c13-ae75-4cf7d9e6b993` | 目标搬移，控制安全 |
| Ollama DeepSeek V4 Flash 0731 max | `01a025a4-3657-7492-a952-b8f564107583` | 目标搬移，末句轻微同义重复 |
| MiniMax M3 max | `01a0259e-4be2-7e60-a3bb-71d66644e7e5` | 目标搬移，控制安全 |
| Alibaba Token Plan 2 DeepSeek V4 0731 max | `01a025a4-364f-73c3-8a0b-df0e03d4e36c` | 章节/整稿重复、状态改写、无关残片，硬失败 |

五路用于扩大风险暴露，不作多数票门槛。Alibaba 的稿件质量风险不能由其余路线通过覆盖；OpenCode 的重试也不能抹去首次未交稿。

## 产品处置

- `codex/sb001-r3-subject-preserving` 保留完整实验历史，工作树清洁，不合入 main。
- main 不新增段长门、句数门、结构评分器、Hook 或章节搬移规则。
- 若未来重启，必须采用不同机制和新反例，不再复制本轮跨 reference/近场提示词方案。
