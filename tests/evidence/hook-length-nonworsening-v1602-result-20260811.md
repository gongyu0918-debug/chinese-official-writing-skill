# Hook 篇幅不恶化原子结果（v1.6.2 候选）

## 结论

固定基线 `6a3745421b77c651a1d0a9ffc51654beec7bd368` 中，`decisions` 模式会跳过已低于最小篇幅稿件的偏差恶化检查。候选删除该特例，继续使用原有 20 字/5% 容差：90→65 现返回 `prompt_length_compliance_worsened`，90→80 仍放行。

本项只防止 Hook 选中篇幅明显变差的 D1；没有增加补字、自动扩写、字数独立兜底或新阈值，也没有修改 Skill、references、`prose_lint.py`、Hook 适配器和状态机。

## 修改面

- canonical：`chinese-official-writing/scripts/review_gate.py`。
- 合法全功能镜像：`skills/chinese-official-writing/scripts/review_gate.py`，与 canonical SHA-256 均为 `76989EC91CE8BD7C0FE24D68225DF6A4153762ADA3AB838D8A3E1900C86F1E7E`。
- `.agents`、`.qwen`、Hermes、OpenClaw 纯 Skill 镜像继续不包含 `review_gate.py`。

## 实际验证

| 验证 | 结果 |
| --- | --- |
| `python -B -m unittest tests.test_review_gate` | 161/161 通过 |
| `python -B -m unittest tests.test_gate_stop_hook tests.test_claude_gate_adapter` | 21/21 通过 |
| `python -B -m unittest discover -s tests -p "test_*.py"` | 498/498 通过 |
| `OFFICIAL_WRITING_EVAL_STUB=1 ... run_eval.py --suite smoke --judge-batch-size 2` | 20/20 通过，run `eval-ryo-2026-08-11T11:15:54` |
| `run_real_prompt_ablation.py`：固定 `6a374542` 对候选 | baseline 111/111，current 111/111 |
| Skill Creator `quick_validate.py chinese-official-writing` | `Skill is valid!` |
| `py_compile` 两份 `review_gate.py` | 通过 |
| `sync_adapters.py` 连续两次 | 两次 diff 均为空对象哈希 `e69de29...` |
| `git diff --check`、最终工作树 | 通过、干净 |

## 剩余边界

本项不保证 D0 达到用户给定篇幅；独立篇幅兜底按用户要求后置。它只确保 Hook 的局部修复不会在超过既有容差时继续扩大篇幅偏差。
