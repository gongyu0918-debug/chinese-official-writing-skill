# 下一版本 SkillHub 分类引导研究结果

## 平台契约

- SkillHub 公开分类接口 `GET /api/v1/categories` 返回一级键 `office-efficiency`（办公效率）和 `content-creation`（内容创作）。
- 本机 SkillHub CLI 发布 payload 只发送 `slug`、`version`、`displayName`、`summary`、`description`、`tags`、`license`、`homepage` 和 `changelog`，不发送 `category`、`subCategories` 或 `categoryIds`。
- SkillHub 普通个人/社区网页发布表单同样不展示分类选择，也不发送 `categoryIds`；企业发布表单才提供“分类（可多选）”并发送 `categoryIds`。
- `_meta.json` 在 CLI 中被视为本地/签名辅助元数据，不是分类 payload。另加一个分类配套文件不能证明后台会读取。

因此，普通个人发布能可靠提供给后台分类器的只有摘要、描述和 tags。分类最终仍由平台审核/分类器决定，包内信号不能被表述为强制分区。

## 最小候选

- 只改 SkillHub 专用 builder；canonical `SKILL.md` 和其他平台包不加平台分类字段。
- SkillHub 专用 tags 前置加入 `office-efficiency`、`content-creation`，保留原有五个业务标签。
- SkillHub 专用摘要明确包含中文公文、事务性材料、新闻稿件、新闻评论、办公效率和内容创作。
- 不修改公开版本号，不上传任何版本。

## 实际验证

- `maintenance.tests.test_skillhub_package_builder` 与 `maintenance.tests.test_skill_boundary`：79/79 PASS。
- 研究包：48 文件；版本仅用 `1.6.3-test` 本地坐标。
- SkillHub CLI dry-run：`dryRun=true`、slug `chinese-official-writing`、version `1.6.3-test`；没有 HTTP 上传。
- 研究包 `SKILL.md` 实际包含两个目标 tags 和新摘要；通用 canonical 正文未改。

## 下一版准入

发布后分别核对上传回执、`tags.latest`、公开 `latestVersion`、`skill.category` 和 `skill.subCategories`。只有公开详情进入办公效率或内容创作，才能说分类引导生效；仍落在行业专业时，保留平台分类结果，不通过重复上传同版本纠正。
