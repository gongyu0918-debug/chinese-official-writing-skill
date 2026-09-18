# 2.0.5 发布记录

2026-09-18按用户授权发布当前main。产品提交为`79ee5083c9101bccd5ed88e4c39fe7b2ab4de279`，注释标签`2.0.5`固定指向该提交；后续维护回执提交不移动产品标签。

| 平台 | 结果 | 回执 |
| --- | --- | --- |
| GitHub | Release已创建 | [中文公文写作2.0.5](https://github.com/gongyu0918-debug/chinese-official-writing-skill/releases/tag/2.0.5) |
| SkillHub | 提交成功；审核pending | skillId 70149 / versionId 323746，75文件 |
| ClawHub | published | versionId k974dtp3p57aaphvmzmbq7cnrd8en39z，74文件 |

每个平台正式提交一次。SkillHub和ClawHub的成功回执即为本轮完成依据，没有提交后的公开页面、索引、版本传播查询或重复上传。审核状态照实登记，不将pending表述为审核通过。

## 发布内容

新增经费预算和信息化建设场景参考，补强采购价格/验收对应及整改状态/统计口径。对比2.0.4，相关规则仅5个文件，采购更正公告实验未进入发布。发布准备只更新两份README版本号，保留示例、下载量徽章及其日期。

写稿依据为[上轮采纳证据](../scenario-leaves-validation-20260918/results.md)：16对原生A/B与2对限定复测，共36次；最终实际读取页对应15对。上轮完整记录了持平、改善、弱点及审阅分歧，本轮没有重复模型调用，也没有宣称普遍省钱或提速。

## 工程验证

- `python -B maintenance/tests/evidence/release-2.0.5-20260918/prepare.py`：8项路径、Skill结构、打包脚本smoke和SkillHub本地预检通过。
- ClawHub直接Node CLI预检为would-publish；正式回执与预检的fingerprint一致。SkillHub本地dry-run仅返回slug及version，不提供fingerprint；正式回执指纹原样保存，未冒充经过同口径比较，见publication-receipts.json。
- canonical 75文件；两个平台使用各自的清洁目录，逐文件SHA-256及文件集合对应已提交产品。无Hook、维护文件、缓存或适配归档混入。SKILL.md、references与scripts同授权main@f00101bd。
- 未改脚本，沿用之前142项脚本行为检查，仅补发布包smoke。没有运行旧的规则关键词/整句断言。
- `git diff --check`通过；新tag继承2.0.4历史。main与新tag原子推送成功，无强推或移动旧tag。
- 桌面WorkBuddy和其他适配归档未更改。

本机普通写作层已同步：166个安装文件与宿主缓存一致，README版本号及本次规则逐字节匹配发布提交，见local-sync.json。Hook启用/信任单独核对，本轮未重跑宿主生命周期或付费在线服务。
