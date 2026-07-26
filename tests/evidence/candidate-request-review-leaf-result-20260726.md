# Candidate：请示/申请细查叶验证结果

## 结论

`PASS`。保留产品提交 `fc630e9417c8df590e7c88a818f691664aa60ee0` 在独立研究分支，暂不合并、不改版本号、不发布。

本候选只把请示、申请的既有细查小节从通用 `genre-checklist.md` 迁入 review-only 叶 `genre-checklist-request.md`。请示、申请起草叶 `genre-playbook-request.md` 的 SHA-256 在固定 1.5.25 与 Candidate 中均为 `B0F4BA841D175C92D27B51B1888588782619F26A866BD068532857D7DFE5AEEE`。

## 实际减载

| 路径 | 1.5.25 | Candidate | 变化 |
| --- | ---: | ---: | ---: |
| 通用文种细查叶 | 3583 字符 | 3033 字符 | -550 |
| 请示/申请细查叶 | 不存在 | 626 字符 | 新增按需叶 |
| `review-checklist` + 请示/申请文种细查 | 9707 字符 | 6750 字符 | -2957，约 -30.46% |

若只看被替换的文种细查文件，按需叶相对原通用叶减少约 82.53%。起草任务不读取新细查叶。

## 工程验证

1. `python -m unittest discover -s tests`
   - 结果：`372` 项通过，`0` 失败。
2. `C:\Users\admin\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe evals/official-writing/run_eval.py --suite smoke --judge-batch-size 2`
   - 结果：`20/20` 通过，`0` error。
   - 首次在 Windows 沙箱内由 Node 启动 Python 失败，改用已核验的 bundled Python 并获批复跑后通过；前次失败记为环境噪声。
3. `python tools/run_real_prompt_ablation.py --baseline-root <github-1.5.25-product> --baseline-label 1.5.25 --current-root . --out output/candidate-request-review-leaf-ablation-20260726`
   - 结果：固定 1.5.25 `108/108`，Candidate `108/108`。
4. `python tools/sync_adapters.py`
   - 结果：canonical 与五个发行镜像完成同步；新旧细查叶分别只有一个 reference 内容哈希。
5. `python <skill-creator>/scripts/quick_validate.py chinese-official-writing`
   - 结果：`Skill is valid!`
6. `git diff --check`
   - 结果：通过；仅显示工作区 CRLF 提示。

## 真实 A/B

### 条件

- Candidate：`fc630e9417c8df590e7c88a818f691664aa60ee0`
- Baseline：`776a32e60f7bb0afe37f439b2710b6d0b43d40e8`
- 调度参数：`gpt-5.6-sol`、`ultra`
- 每题使用同一个自然语言任务文件，各取首个技术有效输出，不补抽。
- writer、硬边界 verifier 和匿名 judge 相互独立。
- 本轮不生成 No-Skill；本候选只回答相对上一发行基线的原子迁移是否可保留。

运行时界面未向 writer 独立暴露模型和 thinking 字段，因此模型条件可核验到调度参数，运行时二次读取值为 `unavailable`。

### 硬边界

R01—R03 共六份首稿全部 `PASS`。没有事实、数字、日期、主体、状态、文种、格式、输出模式或 P0 回退，均可进入匿名盲审。R01 Candidate 在任务文件首次尚未落盘时停止，文件进入预注册路径后才读取并生成首稿；没有使用替代输入或补抽，该环境事件不改变成稿有效性。

### 匿名盲审

盲审映射在判定后解盲：

| 任务 | 匿名映射 | 判定 |
| --- | --- | --- |
| R01 内部费用申请审稿 | A=Baseline，B=Candidate | Candidate 胜；Candidate `PASS`，Baseline `WARN` |
| R02 正式请示审稿 | A=Baseline，B=Candidate | Candidate 胜；Candidate `PASS`，Baseline `WARN` |
| R03 请示审后直接改稿 | A=Candidate，B=Baseline | Baseline 小胜；两稿均 `PASS` |

R03 的负项只有“现请示同意”略显生硬，未涉及硬边界。按预注册规则补一对同题、同条件噪声复验，不换题、不补 Prompt：

| 任务 | 匿名映射 | 硬边界 | 判定 |
| --- | --- | --- | --- |
| R03N | A=Baseline，B=Candidate | 两稿均 `PASS` | Candidate 小胜；两稿均 `PASS` |

R03 两次独立运行一胜一负，差异集中在轻微衔接和版式，未形成 Candidate 稳定负项。请示/申请只审不改的两项则均由 Candidate 明确胜出，且胜因与本轮减载目标一致：审稿建议更贴近已有材料，较少泛化外围程序。

## 验收判断

- 三个预注册任务均无 Candidate 独有硬回退：满足。
- 至少一题 Candidate 明确胜出：满足，实际为 R01、R02 两题。
- 唯一软负项经预注册同题复验后没有继续为负：满足。
- 不追加同义 Prompt、不修改起草叶、不扩大测试矩阵：满足。

因此保留本原子提交，作为后续合并候选。该结论只覆盖请示/申请审稿和审后改稿路由；其他文种拆分仍须各自在独立 worktree 验证。

## 原始证据

忽略目录：`output/candidate-request-review-leaf-real-ab-20260726/`

- `hard-verifier.md`
- `blind/blind-judge.md`
- `R03N-hard-verifier.md`
- `blind/R03N-blind-judge.md`
- R01—R03、R03N 的 task、Candidate/Baseline 首稿与 provenance
