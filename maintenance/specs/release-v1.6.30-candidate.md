# 1.6.30 拆分候选

状态：FROZEN_CANDIDATE / NOT_RELEASED。107项minimal、817项全量、五处Skill校验通过。计划用于2026-09-09的小版本；不创建定时发布任务。

以已发布 `v1.6.29` 为祖先，从检查时main `c7778f2627d025bc34f106cb8cb74bcf03fb011b` 拆出已经完成的README更新。源产品取 `bb3eae9d`，只迁移包内README、能力咨询入口、Hook说明回链和五套普通镜像。小修复是能力范围答复补全、区分一般用法与具体写稿、区分普通说明与Hook说明，不新增Hook实现修复。

保留1.6.29的全部写作reference、脚本和Hook实现；排除R25全局有据分析、R26增项专页与路由、开发规范改动及其研究工程。main继续保留这些后续更新，不回退main，不从main整包发布本候选。

历史真实验证来自 `cf4836c3` 的 `maintenance/tests/evidence/skill-package-readme/`，最终FAQ补全见 `bb3eae9d` 的integration.md。共20次技术完成调用，不是20篇写稿质量通过；最终能力、Hook咨询和真实写稿分流有有限证据，保留早期漏读和稿件问题。FAQ随后两处文字补全及免费页面链接未重新跑模型。本轮不改变这些规则，迁移该证据并核对精确字节，重新执行候选minimal与包检查；不宣称新的宿主隔离或在线写稿通过。

冻结提交与包指纹见[候选验收](../tests/evidence/release-v1630-candidate/README.md)。版本元数据为1.6.30候选；公开发布状态仍为1.6.29。发布需用户后续指令，不推送、不建tag、不上传。
