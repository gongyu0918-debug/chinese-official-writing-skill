# 1.5.4 发布证据

## 范围

1.5.4 是在远端 `v1.5.3` 和本地轻量路由卡候选之上的合并发布候选。本轮不是覆盖远端 `v1.5.3`，而是在保留远端事实边界修复的基础上，上移一个小版本号发布：

- 合并远端 `v1.5.3` 相对 `v1.5.2` 的事实边界修复，覆盖 `P086-P095`：版慎通使用报告不误改调研报告、正文外提醒不编号成第七章、文表附件一致性、采购/可研/会议纪要不套模板补空、建议事项不改成执行命令、只审不改不用 Markdown 包装、稀疏材料不补处置链条、字段式采购不新增用途、系统异常不包装核心系统、事实不清审稿不降成低风险套话。
- 新增轻量 `references/task-route-cards.md`，用于材料稀疏、短稿、低上下文局部修改和二次局部修改时优先读取短卡片，再按需转读长 reference。
- 不新增 lint 硬规则、默认联网、强阻断、排版脚本或重型入口 prompt。
- 弱模型写作验收口径调整为：Markdown 残留、标题包装等格式噪点记 WARN，不作为内容失败；重点看 prompt 遵循、要点置入、事实边界、禁止事项和二次修改可交付性。

历史说明：仓库中曾记录过一个早期 `1.5.3` 本地候选被阻断；后续查询发现远端已存在 `v1.5.3` tag，且该 tag 指向旧提交 `b4535b9 fix: close final 1.5.3 fact-boundary blockers`。为避免覆盖远端 tag 或制造版本歧义，本次已验证候选上移为 `1.5.4` 发布候选；不复用被阻断候选的结论，也不强推覆盖 `v1.5.3`。

## 验证

### 版本同步

命令：

```powershell
C:\Users\2\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe .\tools\sync_adapters.py
```

结果：

- `chinese-official-writing/SKILL.md`、Codex 镜像、`.agents`、`.qwen`、Hermes、OpenClaw、README、skill-card 和 Claude plugin 均同步到 `1.5.4`。
- `tools/sync_adapters.py` 版本常量为 `VERSION = "1.5.4"`。

### 1.5.2 基线消融

命令：

```powershell
C:\Users\2\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe .\tools\run_real_prompt_ablation.py --baseline-root output\release-baselines\github-1.5.2 --baseline-label baseline-1.5.2 --current-root . --out output\real-prompt-vs-1.5.2-release-1.5.4-merged
```

结果：

| Label | Total | Passed | Failed | Warnings | Errors |
| --- | ---: | ---: | ---: | ---: | ---: |
| baseline-1.5.2 | 95 | 84 | 11 | 7 | 4 |
| current | 95 | 95 | 0 | 0 | 0 |

说明：`baseline-1.5.2` 的失败集中在远端 `v1.5.3` 已新增的事实边界和本轮保留的后续边界用例；`current` 全部通过。

### 1.5.3 基线消融

命令：

```powershell
C:\Users\2\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe .\tools\run_real_prompt_ablation.py --baseline-root output\release-baselines\github-1.5.3 --baseline-label baseline-1.5.3 --current-root . --out output\real-prompt-vs-1.5.3-release-1.5.4-merged
```

结果：

| Label | Total | Passed | Failed | Warnings | Errors |
| --- | ---: | ---: | ---: | ---: | ---: |
| baseline-1.5.3 | 95 | 95 | 0 | 0 | 0 |
| current | 95 | 95 | 0 | 0 | 0 |

说明：本轮相对远端 `v1.5.3` 没有确定性消融回退；新增轻量路由卡没有破坏远端已修复的事实边界。

### unittest

命令：

```powershell
C:\Users\2\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m unittest discover -s tests
```

结果：

```text
Ran 107 tests
OK
```

### quick_validate

命令：

```cmd
C:\Users\2\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe C:\Users\2\.codex\skills\.system\skill-creator\scripts\quick_validate.py chinese-official-writing
```

结果：

```text
Skill is valid!
```

### diff check

命令：

```powershell
git -C . diff --check
```

结果：退出码 0；仅有 Windows 换行提示，无 whitespace error。

### official-writing smoke

非提权环境下 promptfoo 依赖访问 npm registry 被沙箱网络拦截；提权后运行同一评测入口通过。

命令：

```cmd
C:\Users\2\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe evals\official-writing\run_eval.py --suite smoke --judge-batch-size 2
```

结果：

```text
Results:
  20 passed (100%)
  0 failed (0%)
  0 errors (0%)

skill_win_rate: 1.0
judge_consistency_rate: 1.0
```

### 真实样文回归

命令：

```powershell
C:\Users\2\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe .\tools\run_real_article_eval.py --out output\real-article-release-1.5.4-merged
```

摘要：

| 模式 | 样本数 | 平均差异率 | 缺失要素 | 应覆盖要素 | 关键词命中率 | 占位词风险样本 | 占位词命中 | 格式风险 | 重复事项 | 反 AI 风险 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline | 10 | 93.00% | 57 | 61 | 17.43% | 0 | 0 | 0 | 0 | 2 |
| skill | 10 | 0.00% | 0 | 61 | 100.00% | 9 | 16 | 0 | 0 | 0 |

说明：`skill` 路径的占位风险主要来自“主送单位、发文字号、发文机关、报告主体”等正式要素待确认项，作为人工复核提示，不作为发布阻断。

### 真实写稿/verifier 证据

本次发布不只依赖确定性脚本；最近真实 writer/verifier 证据包括：

- `tests/evidence/task-route-cards-real-ab-20260709.md`：轻量任务路由卡并入后，弱模型 3 WARN、0 FAIL；强模型 3 PASS。
- `tests/evidence/second-revision-after-route-cards-20260709.md`：用户式二次修改后，弱模型和强模型均为 3/3 PASS。
- `tests/evidence/release-readiness-regression-20260709.md`：旧能力真实回归 0 FAIL，无三次以上共性失败。
- `tests/evidence/preflight-current-20260709.md`：综合预检通过，弱模型格式噪点按 WARN 记录。
- 本轮合并后另跑 3 个自然语言真实 prompt：版慎通使用情况报告、材料稀疏的数据治理通报、字段式硬盘采购二次修改。弱模型 `gpt-5.3-codex-spark` 低思考为 3 WARN、0 FAIL，主要是 Markdown 标题和一处轻微事实扩展；强模型 `gpt-5.5` 低思考为 3 PASS。独立 verifier 只看 prompt 和成稿，结论为无三次以上共性功能失败。

## 结论

1.5.4 当前候选可发布。它保留远端 `v1.5.3` 的事实边界修复，并合入本地轻量路由卡；相对 `1.5.2` 和远端 `1.5.3` 均没有确定性消融回退。真实写稿链路中未出现三次以上共性功能失败；弱模型首稿仍可能有格式噪点和轻微事实扩展，但二次修改可交付，按本轮验收口径不构成发布阻断。

## 发布状态

### GitHub

- Commit: `20776d4 release: merge 1.5.3 fact boundaries for 1.5.4`
- Push: `git push origin main v1.5.4`
- 远端核查：`refs/heads/main` 和 `refs/tags/v1.5.4` 均指向 `20776d4ad9eb0e6c4a3ce3dce5e965c365033928`。

### ClawHub

- 发布命令：`npx --yes clawhub publish openclaw\skills\chinese_official_writing --slug=chinese-official-writing --name=中文公文写作 --version=1.5.4 --tags=chinese,official-document,writing,gongwen,ai-compute --changelog=1.5.4合并事实边界修复并补充轻量任务路由卡`
- 发布结果：`Published chinese-official-writing@1.5.4 (k97fd7dhkmdhc7snnm4qze4xg98a4k7t)`。
- 远端核查：`displayName=中文公文写作`，`latestVersion.version=1.5.4`，`metadata.version=1.5.4`，`metadata.openclaw.version=1.5.4`，`tags.latest=1.5.4`，版本列表包含 `1.5.4`，moderation `clean`。
- 注意：远端 tags 中仍可见历史 `1.4.15` 遗留的带引号 tag key（`"chinese`、`ai-compute"`）；本轮发布命令使用等号参数，未新增带引号 tag。

### SkillHub

- 临时包：`output\skillhub-release-1.5.4\publish-package`，包含 `SKILL.md`、`_meta.json`、`agents/openai.yaml`、14 个 `references/*.md` 和 `scripts/prose_lint.py`，已删除 `__pycache__` 和 `.pyc`。
- Dry-run：`{"dryRun": true, "slug": "chinese-official-writing", "version": "1.5.4"}`。
- 发布结果：`ok=true`，`slug=chinese-official-writing`，`version=1.5.4`，`skillId=70149`，`versionId=132166`，`fileCount=19`，`fingerprint=c2d096c36281e13ab1d2bd363058e21574591b9ef82b74a8da97020fae45970c`，`reviewStatus=pending`，`securityScanStatus=pending`，`contentAuditStatus=pending`，`tags.latest=1.5.4`。
- 后续核查：`skillhub search chinese-official-writing --json` 在提交后仍显示搜索索引版本 `1.5.3`；按发布返回状态判断，SkillHub 已提交但公开搜索/审核切换仍有延迟，不把它描述成已经公开 live。
