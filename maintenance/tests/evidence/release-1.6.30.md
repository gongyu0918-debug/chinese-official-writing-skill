# 1.6.30 发布登记

产品tag：`v1.6.30` → `d2f97ba05e592712ec4b73decceefb3fd29d7c5e`。产品逐文件匹配冻结候选 `0e8cae083d27abd8fe911855a3f07f0ffbcc0842`；发布分支仅接入远端1.6.29维护记录、发布说明与当前版本断言，没有带入本地main后续R25/R26规则。

GitHub main已快进，Release公开。ClawHub正式提交一次成功，versionId为 `k97fg24vy5pcg95ye8y0ay4hq58e0br8`；SkillHub正式提交一次成功，versionId为 `298731`。首次公开核验两平台尚未检出新版本，SkillHub回执的审核/内容审核/安全扫描均为pending。接受回执不等于公开索引或审核完成，最终观察见[平台状态](release-v1630/publication-evidence.json)。不重复上传。

范围见[发布说明](release-v1630/release-notes.md)，[发布前验证](release-v1630/preflight.json)保留本轮107项minimal、88/38文件精确指纹；复用[冻结候选](release-v1630-candidate/README.md)的817项全量与五处Skill校验，产品未改不重复在线写稿或全量回归。保留首次换行字节和版本断言检查失败，随后已修正通过。

本地main的后续工作未覆盖或回退。原始发布回执、正式提交标记与只读核验保存在 `release-v1630/`；后续证据提交不移动产品tag。

第二次只读核验：ClawHub 1.6.30已公开，38个文件SHA256全部匹配冻结清单，安全扫描clean；SkillHub仍未检出1.6.30，成功回执和审核pending保留。没有重复发布。
