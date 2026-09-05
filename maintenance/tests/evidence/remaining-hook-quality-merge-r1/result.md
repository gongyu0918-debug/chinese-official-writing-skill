# 剩余 Hook 与新闻日期规则合入 main

用户授权可合并时合并，并要求随后按普通自然语言任务继续检查 reference。已将本地 main 从 `37f22146f64cf2dfcaea7a8a5afba40750215803` 快进到产品提交 `a2a817d1ddf82c9ba0dcc6bbcc9df684767f9b41`，[合并回执](raw/merge-receipt.json)确认 main 清洁；未推送或发布，`v1.6.27` tag 不变。本文和需求登记为后续文档提交，不改变产品。

## 合并依据

- 原候选 `cda59d8b` 的 14 个产品差异、260 个归档文件 Git blob、事实日期原子及五镜像已独立复核。SKILL.md 和最终 workflow 均等于原基线；失败的多轮规则没有进入最终产品。[独立复核](raw/review.json)、[精确范围](raw/scope-check.json)
- 原候选全量运行 806 项，因两个复杂度子项失败而停止合并：`_bootstrap_transaction_locked` 85 行超过80，`_handle_stop` 判定点26超过25。[首次完整回执](raw/full-tests.json)
- 仅将输入写入和脱敏终态处理提取为两个 helper，不改阈值、锁范围、输入路径、取消意图或交付选择。两个函数分别降为76行/17判定点、64行/24判定点。真实同D0的两种取消时序、正常回显、失败回执刷新及相邻活动事务复放保持原结果，68项复杂度/core测试通过。[重构与复放](raw/refactor/result.json)、[精确补丁](raw/refactor/refactor.patch)
- 因代码已变且首次门失败，在最终提交重新跑全量：**806/806 通过，142.069秒**。[最终命令与输出](raw/full-tests-final.json)
- 五套 quick validate 通过；重构后再次构造的本地 SkillHub 清洁包仍为86文件，相对重构前只有 core 内容变化，无新增版本或上传。原始字节树 fingerprint 为 `67546e3cd7f59ca0b95371a3d5fb5cf0ed38f6d8edeb7890e7981d06bd718a7c`，算法和逐文件SHA见[最终包记录](raw/package-check-final.json)，[五套验证命令](raw/package-check.json)。

```text
python -X utf8 -B -m unittest discover -s maintenance/tests -p "test_*.py"
git merge --ff-only --quiet a2a817d1ddf82c9ba0dcc6bbcc9df684767f9b41
```

## 仍未完成

[上一轮50次真实写稿/修改](../remaining-hook-quality-r1/result.md)及失败轨迹保持，不因合并改写。DSH只证明SDK取消当前回合，OpenCode只证明插件停止与失败分类；CodeBuddy/Kimi独立硬停、已显示正文、持续I/O故障、没有后续清理事件及两个turn都bootstrap时的后缀碰撞均保留。纯helper重构无新增模型调用，不能升级宿主或成稿质量证据。

后续质量测试使用自然语言的进展报告和会议纪要任务，每类连续修改五版，由现有两家低价模型各自独立会话完成。普通题面不点名Skill、不指定reference路径、不注入规则全文；记录是否自然启用、实际读取、正文完整性、事实/状态保真、删改准确性与压缩结果。用户需要正常任务和不同说法下的稳定性提升，不将目标误解为穷举环境/提示词，也不以测试数量推算通用可靠率。付费同步仍由其专属任务负责。

[原始证据清单](raw-manifest.json)固定归档字节；raw禁止Git换行转换。重构报告中原始source-root指向执行时的output，未将整份runtime或第三方依赖入库。
