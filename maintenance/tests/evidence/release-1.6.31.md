# 1.6.31 发布记录

2026-09-09，经用户明确授权，GitHub、SkillHub.cn、ClawHub各正式提交一次。

- 产品tag：`v1.6.31` → `076b6675ceca6d33b2a2579b076871538c2b0656`；发行分支：`codex/release-v1.6.31`。原子推送main和tag成功。[GitHub Release](https://github.com/gongyu0918-debug/chinese-official-writing-skill/releases/tag/v1.6.31)已公开，非草稿、非预发布。
- SkillHub：接受回执`versionId=301059`，88文件；review/content/security均pending。发布后两次只读精确版本核验仍“找不到该版本”，公开传播未确认，不重复上传。
- ClawHub：接受回执`k97dcmb7rh6r5rt4v5kzexsch18e3gxa`，38文件，status=published；回执latestVersion仍1.6.30。发布后两次只读精确版本核验仍Version not found，公开传播和审核未确认，不重复上传。

范围从冻结`9e5b246a`抽取R25两处有据分析规则及五套镜像，canonical净增1354字节；后续本地main的Hook、增项申请与讲话规则不进入本版。本地main及Pro安装未改动。

验证：冻结候选817项全量与五处Skill校验沿用，本轮命令`py -3.13 -B -X utf8 -m unittest maintenance.tests.test_skill_boundary maintenance.tests.test_status_ledger_consistency maintenance.tests.test_skillhub_package_builder maintenance.tests.test_repository_reachability`通过107项（1.177秒）；无新模型调用。SkillHub 88/88、ClawHub 38/38文件SHA与冻结manifest完全一致，独立复核canonical 88/88匹配冻结Git blob。

失败与修复：新checkout及首次archive恢复受CRLF转换影响，初次包字节检查失败；以git cat-file原始blob恢复后重建final并通过逐字节检查。平台提交均在修复之后。SkillHub发布前两次CLI参数/ZIP错误保留，最终正确预查确认版本不存在。未把这些失败计作通过。

逐项命令、接受回执、原字节检查和公开核验见[结构化结果](https://github.com/gongyu0918-debug/chinese-official-writing-skill/blob/0721297298b72be7a37b93c6598172791b58e421/maintenance/tests/evidence/release-v1631/publication-evidence.json)及同目录JSON；[冻结候选](release-v1631-candidate/README.md)保留原时点状态。后续证据提交不移动产品tag。
