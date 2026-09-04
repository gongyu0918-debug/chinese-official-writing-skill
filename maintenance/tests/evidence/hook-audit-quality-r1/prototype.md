# 日期来源旁路原型：NOT_ADMITTED

状态：`NOT_ADMITTED`。本轮保留 [prototype.patch](prototype.patch) 供追溯，不准入产品；`chinese-official-writing/hooks/shared/source_bound_dates.py` 已用固定基线 `5fbb2d26c49d0b780ad11fc4cff008854995ad3f` 的 Git blob 恢复。core、adapter 和其余产品文件均无改动。

原型只在日期来源含示例、模板、旧稿等角色词，或含当前解析器未覆盖的年份/日期写法时，拒绝自动补年并保留输入稿。它不扩大日期自动修复范围，不修改 coordinator。

最小反例的请求为“请写一则新闻稿。活动事实：中心在2026-09-05举办读书交流活动，共20人参加。日期格式示例（不属于活动事实）：2020年9月5日。”输入稿为“中心举办读书交流活动\n\n9月5日，中心举办读书交流活动，共20人参加。”基线把示例中的 2020 年写进活动日期。此前离线同 D0 生命周期回放显示该原型可拒绝这一类歧义修改，但这些人工构造输入不构成真实新闻 D0 的修稿收益证据。

本组 [六稿实际结果](result.md) 只有整改方案，且使用未改动基线 core；它不验证日期原型。没有真实新闻 D0 证明目标收益，因此原型停止在证据补丁，不据此交付修复。正常明确日期进入 preflight 后仍可能以已补年的版本作为恢复依据，原始宿主 D0 的完整保全问题也未解决。

补丁以固定基线为适用对象，可用 `git apply --check maintenance/tests/evidence/hook-audit-quality-r1/prototype.patch` 离线核验可应用性。实际应用和产品准入应另行进行有真实新闻稿的验证；本归档未应用补丁。
