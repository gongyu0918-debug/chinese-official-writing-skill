# SkillHub 发布 frontmatter 减载结果（v1.6.2）

结论：`ENGINEERING PASS / OFFLINE DRY-RUN PASS / ELIGIBLE FOR LOCAL INTEGRATION`。

## 改动

- 新增 `tools/build_skillhub_package.py`，只从 `git ls-files` 的 canonical Skill 构建全新输出目录，拒绝覆盖已有目录。
- 清洁包排除 `agents/openai.yaml`、包内 `LICENSE`、缓存和未跟踪研究产物；GitHub 根 MIT/MIT-0 许可证及插件 manifest 不变。
- SkillHub 专用 `SKILL.md` 只含平台强制的 `slug/version/displayName`、平台摘要和 tags、Agent 运行必需的 `name/description`。
- `homepage`、`license`、GitHub 地址、兼容 Agent 列表、安装路径和嵌套平台 metadata 均不进入发布包入口。
- `_meta.json` 只含 `slug` 与 `version`。
- `AGENTS.md` 将该构建器固定为后续 SkillHub 清洁包入口。

## 对照审计

通过 SkillHub 公开下载 API 只读加载压缩包到内存，未安装第三方 Skill：

| Skill | 文件数 | 包内 LICENSE |
| --- | ---: | --- |
| `dev-expert` | 38 | 无 |
| `moways00001` | 8 | 无 |
| `xcrawl` | 2 | 无 |

这只支持“SkillHub 包无需重复携带 LICENSE 文件”的减载方向，不用于推断第三方写作质量或安全性。

## 验证

- `python -B -m unittest tests.test_skillhub_package_builder -v`：3/3 PASS。
- `python -B -m unittest discover -s tests -p 'test_*.py'`：492/492 PASS。
- `OFFICIAL_WRITING_EVAL_STUB=1 npm.cmd run eval:official-writing:smoke`：20/20 PASS，0 fail/error，run `eval-jkO-2026-08-11T09:53:41`。
- `python -B tools/run_real_prompt_ablation.py --baseline-root ...skill-frontmatter-relief-v1602 --current-root ...skillhub-publish-frontmatter-relief-v1602`：baseline 111/111，current 111/111。
- `python .../quick_validate.py chinese-official-writing`：`Skill is valid!`。
- `python .../plugin-creator/scripts/validate_plugin.py .`：PASS。
- `claude plugin validate .`：PASS，保留原有 author 缺失 warning；未登录 Claude、未调用模型。
- `python -m py_compile tools/build_skillhub_package.py`：使用系统临时 pycache，PASS。
- 构建器两次分别生成 39 文件；均无 `LICENSE` 和 `agents/openai.yaml`，发布入口 GitHub/homepage/license/兼容列表命中 0。
- 本机 SkillHub CLI 2026.8.5：`publish <package> --version 1.6.2 --dry-run --json` 返回 `dryRun=true`、正确 slug/version；dry-run 不发 HTTP，不读取或提交 token。
- `git diff --check`：PASS。

## 边界

- 本轮不发布、不上传、不登录、不改版本面。
- 该原子只证明发布包可重复构建、字段更少且离线预检通过，不声称写稿质量提升。
- SkillHub CLI 当前仍强制 `slug/version/displayName` 位于专用发布 frontmatter，不能把这三项继续删除后仍声称 CLI 可发布。
