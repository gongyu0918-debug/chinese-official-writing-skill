# 第二次五提交检查点

## 范围

独立只读 review 检查 `74532f7..a7bc0b9`，重点检查 `71e07e7..a7bc0b9`。该范围 5 个提交、17 个变更文件，全部位于 `tests/evidence/`；没有修改 Skill、README、runtime、版本号或发布文件。

`a7bc0b9` 的提交说明把范围写成“8 份输出和 provenance”，实际还包含 `no-skill-quality-gate-plan.md` 的 GitHub 展示规则。这是提交说明遗漏，真实 diff 共 10 个文件、247 行新增；本记录补充准确范围，不把原提交说明继续作为完整 scope 证据。

## 独立 review 结论

- 8/8 严格无 Skill 任务 `<input>` 与固定 prompt 逐字一致，模型和 medium thinking 与记录一致；两个可发现 Skill 目录在创建前隐藏、创建后恢复。
- 线程仍自动收到共同的 Codex 基础指令和宿主 `AGENTS.md`。严格 N 与自然触发当前 1.5.14 的 16 个 writer 使用同一份宿主文本，SHA-256 均为 `47C370389D2FC51701BCEAC240FF93E933B0ACD484E44D4176395471BF95055F`。因此准确口径是“任务输入无额外测试控制语、两组宿主一致”，不是“整个会话只有原始 prompt”。
- 旧 S514 writer 带有版本读取、测试身份和输出标记等控制语，不能与严格 N 配对；现已改用自然触发的当前 1.5.14 新直写稿。
- 单案例展示与 36 对发布门槛的适用范围原有冲突，现已区分：单个全面领先稿可更新案例展示；整体 80%—90% 声明和发布仍须达到每模型 10/12、总计 30/36，且硬回退为 0。
- 12 个留出任务目前只固定了文种和篇幅类别，尚未固定完整 prompt。首个产品候选修改前必须先提交完整留出任务。
- 匿名包虽已先提交，原始文件名仍可反查条件。verifier 必须使用无仓库访问的独立 projectless 上下文，只接收匿名包文本，并保留原始输入记录。

结论为 WARN、无 FAIL；上述口径修正完成后可继续严格盲审，尚不能据此宣称总体质量门槛已达成。

## 本地回归

- `python -m unittest discover -s tests -v`：174/174 PASS。
- `python .\tools\run_real_prompt_ablation.py --baseline-root .\output\release-baselines\github-1.5.13-cold-audit --baseline-label baseline-1.5.13 --current-root . --out .\output\checkpoint-vs-1.5.13-20260715`：baseline 108/108，current 108/108。
- `C:\Users\admin\AppData\Local\Programs\Python\Python313\python.exe .\evals\official-writing\run_eval.py --suite smoke --judge-batch-size 2`：20/20 PASS，0 error，judge consistency 1.0。
- `git diff --check 74532f7..a7bc0b9`：无输出。

首次确定性消融调用使用了不存在的 `output/release-baselines/github-1.5.13`，返回目录不存在；随后改用已存在且固定到 `cd2d46c58a5f56b9009c5da08626a88640f2e5b3` 的 `github-1.5.13-cold-audit` 重跑并得到上述 108/108 结果。
