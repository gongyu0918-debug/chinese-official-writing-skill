# 请示/申请叶子拆分真实 A/B 结果（2026-07-26）

## 结论

本候选达到合并条件。请示/申请起草路径从通用 `genre-playbooks.md` 拆到独立
`genre-playbook-request.md` 后，命中路径由 3928 字符降至 551 字符，减少 3377
字符（85.97%）。三组正常场景真实 A/B 中，两名独立盲审分别给出 Candidate
3 胜 0 负、2 胜 0 负 1 平；六份成稿的硬边界均为 PASS，未出现 P0
保护性外扩。没有同一问题机制在三个场景复现，因此不追加 Prompt 修复。

本结论只说明该原子拆分相对固定 main 基线不回退且具有写作侧正向证据，不把
确定性消融解释为真实写作质量，也不外推为全量文种结论。

## 固定对象

- 固定 main 基线：`faba4c1f410b3007d60671b3d2ead6d78a2ea8a4`
- Candidate 产品提交：`123d0d13a3879075b82457d7e012b314b8623413`
- 重启预注册提交：`fceefed2d17a71b2f7b5d66f59f6fd23de6442b7`
- 正确路由预注册提交：`baf1d10198f70d63b2a7e935df9404e25e721582`
- Candidate 分支：`codex/1.5.25-candidate-request-leaf-v1524`

## 路由有效性

最初三组局部改稿只命中 `task-route-cards.md`，Candidate 与 Baseline 均未读取
请示/申请起草规则，不能回答叶子拆分是否影响起草质量。该组只保留为路由烟测，
不计入胜负，也没有据此修改产品。

随后按预注册补做三组自然起草任务：

1. DQ01：防磁柜购置请示；
2. DQ02：网络安全培训请示；
3. DQ03：场地使用申请。

Candidate 实际读取 `genre-playbook-request.md`，Baseline 实际读取
`genre-playbooks.md`；每题两侧使用逐字一致原始输入，各取首个技术有效输出，
未补抽。运行环境继承一致，但原始回执未暴露精确模型名与 thinking 档位，因此
这两个字段记为 `unavailable`，不作推断。

## 匿名盲审

匿名映射：

- DQ01：A = Candidate，B = Baseline；
- DQ02：A = Baseline，B = Candidate；
- DQ03：A = Candidate，B = Baseline。

Judge 1：

- DQ01：Candidate 胜；
- DQ02：Candidate 胜；
- DQ03：Candidate 胜。

Judge 2：

- DQ01：Candidate 胜；
- DQ02：Candidate 胜；
- DQ03：难分。

独立硬边界核验：

- 六稿事实、数字、日期、主体、待批状态、文种、格式和输出模式全部 PASS；
- 无空稿、标记残留、材料外事实、材料外程序承诺、自证边界或外围未决；
- 未发现 P0 保护性外扩；
- `prose_lint.py --structure --format` 对六稿均报告 `No prose risks found`。

可观察差异中，Baseline 在 DQ01 出现近距离重复解释，在 DQ02 句子负担略重；
DQ03 两侧均可直接使用。三题没有共同失败机制，不满足共性修复门槛。

## 工程验证

- `python -m unittest discover -s tests`
  - 结果：`Ran 370 tests`，`OK`。
- `C:\Users\admin\AppData\Local\Programs\Python\Python313\python.exe evals/official-writing/run_eval.py --suite smoke --judge-batch-size 2`
  - 结果：20/20 通过；skill 10、baseline 0、tie 0、invalid 0，judge consistency 1.0。
  - 说明：沙箱内前三次运行分别受 Hermes Python 路径和 Node 无法启动系统 Python
    影响，均作为环境噪声保留；使用同一系统 Python 在获批环境复跑后通过。
- `C:\Users\admin\AppData\Local\Programs\Python\Python313\python.exe tools/run_real_prompt_ablation.py --baseline-root <main-worktree> --baseline-label faba4c1 --current-root . --out output/request-leaf-restart-ablation-20260726`
  - 结果：Baseline 108/108，Candidate 108/108。
- `C:\Users\admin\AppData\Local\Programs\Python\Python313\python.exe C:\Users\admin\.codex\skills\.system\skill-creator\scripts\quick_validate.py chinese-official-writing`
  - 结果：`Skill is valid!`。
- `C:\Users\admin\AppData\Local\Programs\Python\Python313\python.exe tools/sync_adapters.py --help`
  - 结果：该脚本没有单独的帮助分支，仍执行了同步；canonical、各适配镜像、
    README 与插件元数据同步后工作树无新增产品 diff。
- `git diff --check`
  - 结果：通过；仅提示现有工作副本未来可能进行 LF/CRLF 转换，无空白错误。

## 边界与剩余风险

- 本轮没有重跑 true No-Skill；结论只比较 Candidate 与稳定 main。
- 新增真实写作证据为三个正常短篇请示/申请场景，未覆盖复杂长篇、严重缺项或多轮修改。
- 精确模型名和 thinking 档位在运行回执中不可用。
- 原始稿件、provenance、匿名包和盲审全文位于忽略目录
  `output/candidate-request-leaf-draft-ab-20260726/`，不进入发行包。
