# 2026-09-09 仓库整理

基线：公开 `main` 的 `07212972`（v1.6.31 发布回执提交）。本次仅整理证据、生成副本及维护入口，更新下载徽章；不带入本地 `f171e82f` 后续写作或 Hook 候选，不移动产品 tag、不重新上传平台版本。

## 范围与恢复

- 公开基线证据 3,365 文件、34,004,802 bytes；2,227 文件、29,005,848 bytes 转冷归档，必要摘要及测试依赖 1,138 文件、4,998,954 bytes 保持热区。元数据另存，热区字节为迁移前原始文件的口径。
- ZIP 覆盖源提交全部 3,365 份证据，逐份原始 Git 字节 SHA-256 回读一致。当前树退出全部 142 份 JSONL；原始回执、失败和冻结规则仍可按路径提取。恢复见[分层归档](archiving.md)、[归档摘要](archive.json)。
- 58 份保留文档的 258 处链接改为源提交永久链接。补齐规格索引缺少的 v1.6.31 冻结记录入口；一处源提交本已缺失的 `r2-amendment.md` 明示为缺口，未补造证据。
- 六组历史安装副本从当前树移除 212 文件。唯一规则源为 `chinese-official-writing/`，Hook core/adapters 保留；平台安装包按需生成到 `output/compatibility-packages/`。旧副本恢复元数据见[packages](../../../packages/archived-copies.json)。
- [SkillHub 公开接口](https://api.skillhub.cn/api/v1/skills/chinese-official-writing)本次返回 downloads=115884、installs=53；README 下载徽章改为 `115k+`，不混用安装量。

## 依据与限制

[Anthropic skill-creator](https://github.com/anthropics/skills/blob/41bbe19d1a1a7eaab5e7bb9050a417e5c6cffc8f/skills/skill-creator/SKILL.md)将逐轮结果放在 Skill 同级 workspace。对 [OpenAI skills](https://github.com/openai/skills/tree/49f948faa9258a0c61caceaf225e179651397431) 和该 Anthropic 仓库的定点检查用于参考源码与运行产物分离，不构成“所有 Skill 仓库都不应提交测试”的结论。必要测试代码和用例继续公开。

冷归档提取不等于复放历史模型或宿主；本轮不运行新的真实写稿。Git 历史仍保留旧文件，当前树收缩不等于历史仓库体积也同步清零。

## 验证

- `py -m unittest discover -s maintenance/tests -p 'test_*.py'`：824 项，823 通过；唯一失败为旧徽章测试仍固定要求 `50k+`。将其期望同步为本次已核验的 `115k+` 后，`py -m unittest maintenance.tests.test_readme_badges -q` 1/1 通过。没有为这一个断言改动重跑其余 823 项，保留首次失败记录。
- 归档工具完整性测试 4/4；生成器、包边界和评测消费者迁移最小测试 178/178。
- Skill quick_validate 通过。独立复核确认 2,227 条冷记录的 Git blob、大小、SHA-256 和源路径逐项一致；一次真实 Git 提取校验通过，当前证据区无 JSONL 运行流水。
- canonical 88 个文件相对 `07212972` 的 Git 字节未变：35 references、47 Hook 文件、2 scripts、1 Agent 元数据及3个根文件；仅保留一个 `SKILL.md` 入口，不是只保留一个产品文件。五种安装包可按需生成，真实宿主生命周期未重跑。
- `git diff --check` 通过；没有产品新版本、tag 变动或平台重复上传。
