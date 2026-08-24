# WR-001-DATE-R2 合并减载预登记

日期：2026-08-24。

R1 日期目标三路命中，但 Ollama Candidate 仍补材料外活动过程和后续安排，未满足成稿门。R2 不增新语义，只把独立日期 bullet 合并到紧邻的时间事实 bullet，并把日期句缩为：

> 完整年月日照录，不缩为月日；材料仅有月日时不补年份。

相对 R1 减少一个 bullet 和重复的“材料给出、正文首次出现该日期、完整年月日”框架。canonical 与四套镜像同步；其他产品字节不变。

真实写稿只跑 R1 已暴露问题的 Ollama Candidate 和作为控制的 Alibaba Candidate，同题、同模型、`max`、隔离 Skill、Hook 关闭。对应 Baseline 复用 R1 的有效原稿，不重复耗费输入 token。

准入：两条 Candidate 均读取精确 Skill、保留完整日期及48/45/3/46和未汇总状态，只交正文；不得新增具体活动过程、后续安排、长期作用或 Markdown。Ollama 再现任一硬回退即停止本方向；两条均通过后才补确定性镜像测试和扩大到其余 provider。
