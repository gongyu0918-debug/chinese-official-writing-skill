# 1.5.3 发布证据

## 范围

1.5.3 是 1.5.2 后的最小发布候选。本轮只发布已经验证通过的本地候选：

- 新增轻量 `references/task-route-cards.md`，用于材料稀疏、短稿、低上下文局部修改和二次局部修改时优先读取短卡片，再按需转读长 reference。
- 不新增 lint 硬规则、默认联网、强阻断、排版脚本或重型入口 prompt。
- 弱模型写作验收口径调整为：Markdown 残留、标题包装等格式噪点记 WARN，不作为内容失败；重点看 prompt 遵循、要点置入、事实边界、禁止事项和二次修改可交付性。

历史说明：仓库中曾记录过一个早期 `1.5.3` 本地候选被阻断；本次候选是在后续多轮回退、轻量路由卡、二次修改链路和发布前预检之后重新形成的 `1.5.3` 发布候选，不复用被阻断候选的结论。

## 验证

### 版本同步

命令：

```powershell
C:\Users\2\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe .\tools\sync_adapters.py
```

结果：

- `chinese-official-writing/SKILL.md`、Codex 镜像、`.agents`、`.qwen`、Hermes、OpenClaw、README、skill-card 和 Claude plugin 均同步到 `1.5.3`。
- `tools/sync_adapters.py` 版本常量为 `VERSION = "1.5.3"`。

### 1.5.2 基线消融

命令：

```powershell
C:\Users\2\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe .\tools\run_real_prompt_ablation.py --baseline-root output\release-baselines\github-1.5.2 --baseline-label baseline-1.5.2 --current-root . --out output\real-prompt-vs-1.5.2-release-1.5.3
```

结果：

| Label | Total | Passed | Failed | Warnings | Errors |
| --- | ---: | ---: | ---: | ---: | ---: |
| baseline-1.5.2 | 85 | 85 | 0 | 0 | 0 |
| current | 85 | 85 | 0 | 0 | 0 |

### unittest

命令：

```powershell
C:\Users\2\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m unittest discover -s tests
```

结果：

```text
Ran 106 tests in 0.756s
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
C:\Users\2\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe .\tools\run_real_article_eval.py --out output\real-article-release-1.5.3
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

## 结论

1.5.3 当前候选可发布。它没有相对 1.5.2 的确定性消融回退；真实写稿链路中未出现三次以上共性功能失败；弱模型首稿仍可能有格式噪点，但二次修改可交付，按本轮验收口径不构成发布阻断。
