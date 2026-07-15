# 五次提交轻量 review

## 范围结论

review 范围为 `7b07b76878cc5d5e4a5c273833ff1007904372c1..74532f74c6447f6a8d235ab0818ef3c3b50caa35`。31 个变更文件全部位于 `tests/evidence/`，没有修改 Skill 本体、reference、路由、README、版本、运行脚本或发布文件。该范围可以继续用于风险定位，不能作为产品修复或发布完成证明。

## 预注册与揭盲限制

- 无 Skill 方案先于输出提交：`0790cd2` 为预注册，`fd4218c` 为结果。
- 历史版本方案先于输出提交：`d0e37e7` 为首版预注册，`74532f7` 为 GPT-5.5 结果。
- `6bb0c5e` 在写作开始前补入 1.5.3 断点；`74532f7` 又在结果形成后把 GPT-5.5 改称补充定位，并加入 LUNA / TERRA 主测与句法观察。这部分属于第二阶段计划和事后审计说明，不追溯称为首轮预注册观察项。
- GPT-5.5 匿名包、verifier 结果和映射在同一提交中保存。文件和 thread 记录支持先盲审后揭盲的运行叙述，但 Git 提交顺序不能独立证明该时序。后续矩阵把匿名包与 verifier 原始结果先提交，再单独提交映射和汇总。
- TERRA 当前版与无 Skill 的两次交叉判断没有完整保留原始报告和 thread，阶段报告已收紧表述。相关结论只作风险线索，后续重新盲审后再进入产品裁决。

## harness 边界

`71e07e7` 已把 harness 固定为历史诊断条件。外部 agent 的分阶段调用、独立审校、返修轮次和运行轨迹不属于 Skill 能力；harness 结果不触发产品修改，也不作为发布通过依据。任何可借鉴点必须改写为同一上下文可执行的软性方法，并重新通过原生 Skill 对无 Skill 的 A/B。

## 实际验证

- `python -m unittest discover -s tests`：174/174 通过。
- `python .\tools\run_real_prompt_ablation.py --baseline-root output\release-baselines\github-1.5.13-cold-audit --baseline-label baseline-1.5.13 --current-root . --out output\five-commit-check-20260715`：baseline 108/108，current 108/108。
- `C:\Users\admin\AppData\Local\Programs\Python\Python313\python.exe evals\official-writing\run_eval.py --suite smoke --judge-batch-size 2`：沙箱内 Node 无法启动 Python provider，20 项均为环境错误；在允许该子进程执行的同一入口复跑后为 20/20 通过、0 error、judge consistency 1.0。
- `git diff --check 7b07b76878cc5d5e4a5c273833ff1007904372c1..74532f74c6447f6a8d235ab0818ef3c3b50caa35`：发现既有证据文件的 Markdown 行尾空格和 EOF 空行，属于格式噪声；不能把整个范围表述为 diff check clean。
