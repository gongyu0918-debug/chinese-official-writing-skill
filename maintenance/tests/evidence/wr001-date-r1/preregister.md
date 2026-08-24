# WR-001-DATE-R1 活动新闻完整日期原子预登记

日期：2026-08-24。

## 固定反例

`v1615-like-signal-short-writing-r1` 的同一活动新闻中，Ollama、Alibaba Token Plan 2、OpenCode Go、MiniMax 在 v1.6.14 与 v1.6.15 两版都把材料给出的“2026年8月20日”缩成“8月20日”；Luna 两版均完整保留。该缺口跨版本4/5复现，属于既有事实保留不稳定，不归因给 v1.6.15 新增规则，也不以点赞变化证明因果。

## 唯一候选

只在 `references/genre-playbook-news-message.md` 的时间事实规则后增加一句：

> 材料给出完整年月日时，正文首次出现该日期应照录完整年月日，不缩成月日；材料只给月日时不反向补年份。

canonical 与四套普通镜像同步。除此之外不改 SKILL、description、信息选择、活动效果、短稿篇幅、Hook、lint 或路由。

## 真实写稿

- 题面、输出要求与 R1 的 `S2-ACTIVITY-NEWS` 完全相同。
- Baseline：已发布 `v1.6.15@762b84d4`。
- Candidate：本分支 HEAD；运行前须证明 Skill 树除上述一句及镜像外无产品差异。
- 首轮路线：Ollama DeepSeek V4 Flash 0731、Alibaba Token Plan 2 DeepSeek V4 Flash 0731、MiniMax M3，均通过 Codex CLI 0.144.6、`max`、隔离 Skill、Hook 关闭。前两路验证已复现日期缺口；MiniMax Baseline 是 R1 后的未改产品反序复测，Candidate 同时观察上轮材料外细节是否重现。

## 准入

1. Candidate 三路均保留 `2026年8月20日`，Baseline 至少两路继续复现缩写，才能证明目标原子有可观察增量。
2. Candidate 必须保留48名、45名/人、3名/人、46份、单人原话范围和意见卡未汇总状态；不得新增讲解人、分组依据、指定篇目、书面答题、后续优化或其他材料外活动细节。
3. Candidate 只交普通文本正文，不得代码块、Markdown 标题、自证或字符说明；文稿不得因保留年份而变得过短、重复日期或丢掉一层合理即时作用。
4. 目标通过且无 Candidate 独有硬回退后，才补镜像/边界确定性测试并讨论合入；任一路真实硬回退先缩小或停止，不增加更多日期/活动枚举。

本轮不合入 main、不推送、不发布。
