# 2026-07-09 当前候选发布前综合预检

## 范围

本次预检基于当前本地候选，最近实质修改为 `be140b9` 引入轻量任务路由卡，后续 `0249432`、`3bffd7d` 只记录二次修改链路和旧能力真实回归证据。用户最新口径明确：弱模型写作不要死磕 Markdown 残留等格式噪点，只要内容符合 prompt、要点进入正文、事实边界和禁止事项不破坏，格式噪点按 WARN 记录。

本轮未修改 skill 规则、reference、lint、版本号或发布元数据，只做发布前验证和证据固化。

## 已运行验证

### 同步与 drift

命令：

```powershell
C:\Users\2\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe .\tools\sync_adapters.py
git -C . status --short
```

结果：

- `sync_adapters.py` 已同步 Codex、`.agents`、`.qwen`、Hermes、OpenClaw、README、skill-card 和 Claude plugin 镜像。
- 同步后 `git status --short` 为空，未产生 drift。

### 1.5.2 基线确定性消融

命令：

```powershell
C:\Users\2\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe .\tools\run_real_prompt_ablation.py --baseline-root output\release-baselines\github-1.5.2 --baseline-label baseline-1.5.2 --current-root . --out output\real-prompt-vs-1.5.2-preflight-current
```

摘要：

| Label | Total | Passed | Failed | Warnings | Errors |
| --- | ---: | ---: | ---: | ---: | ---: |
| baseline-1.5.2 | 85 | 85 | 0 | 0 | 0 |
| current | 85 | 85 | 0 | 0 | 0 |

结论：当前候选相对 1.5.2 未触发确定性消融回退。

### 全量 unittest

命令：

```powershell
C:\Users\2\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m unittest discover -s tests
```

结果：

```text
Ran 106 tests in 0.821s
OK
```

### diff check

命令：

```powershell
git -C . diff --check
```

结果：退出码 0。命令输出仅包含 Windows 换行提示，不含 whitespace error。

### quick_validate

命令：

```cmd
C:\Users\2\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe C:\Users\2\.codex\skills\.system\skill-creator\scripts\quick_validate.py chinese-official-writing
```

结果：

```text
Skill is valid!
```

### official-writing smoke

说明：`npm run eval:official-writing:smoke` 在 `cmd.exe` 下因脚本使用裸 `python` 失败，未进入评测逻辑；随后用同一评测脚本和 bundled Python 直接执行。首次非提权执行因沙箱网络禁止访问 npm registry 失败，提权后运行通过。

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
C:\Users\2\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe .\tools\run_real_article_eval.py --out output\real-article-preflight-current
```

摘要：

| 模式 | 样本数 | 平均差异率 | 缺失要素 | 应覆盖要素 | 关键词命中率 | 占位词风险样本 | 占位词命中 | 格式风险 | 重复事项 | 反 AI 风险 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline | 10 | 93.00% | 57 | 61 | 17.43% | 0 | 0 | 0 | 0 | 2 |
| skill | 10 | 0.00% | 0 | 61 | 100.00% | 9 | 16 | 0 | 0 | 0 |

说明：`skill` 路径的占位词风险主要来自“主送单位、发文字号、发文机关、报告主体”等待确认项提示。该工具把正式要素待确认也计入占位风险，因此此项作为人工复核提示记录，不单独判为发布阻断。

## 真实写稿证据串联

本次综合预检沿用并复核以下真实 writer/verifier 证据，不用确定性脚本替代真实写稿判断：

- `tests/evidence/task-route-cards-real-ab-20260709.md`：轻量任务路由卡并入后，弱模型 3 WARN、0 FAIL；强模型 3 PASS。
- `tests/evidence/second-revision-after-route-cards-20260709.md`：弱模型首稿 2 WARN、1 PASS，强模型首稿 3 WARN；用户式二次修改后两组均为 3/3 PASS。
- `tests/evidence/release-readiness-regression-20260709.md`：旧能力真实回归中，弱模型 1 WARN、3 PASS，强模型 2 WARN、2 PASS；0 FAIL，无三次以上共性失败。

根据用户最新口径，弱模型中的标题包装、Markdown 加粗等格式问题只记为 WARN；发布判断优先看内容是否符合 prompt、关键要点是否置入、事实边界是否稳定、二次修改是否能交付。

## 结论

当前本地候选通过发布前综合预检。未观察到相对 1.5.2 的确定性回退，也未在最新真实写稿链路中出现三次以上共性功能失败。剩余风险是弱模型首稿仍可能出现格式包装、轻微口径偏硬或局部表达不够精确；按当前验收口径，这些属于二次修改可处理的 WARN，不作为继续堆 prompt 或发布阻断理由。
