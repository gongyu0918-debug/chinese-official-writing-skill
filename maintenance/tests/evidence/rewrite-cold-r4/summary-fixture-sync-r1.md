# 工作总结、工作要点与周期报告维护 fixture 同步 R1

## 范围

本轮只衔接维护用 `maintenance/evals/official-writing/providers/agent_writer.py`、`maintenance/tests/test_promptfoo_eval.py` 和 `maintenance/tests/test_reference_rewrite_contract.py`。该 provider 是显式 `genre` 映射的确定性 fixture，用于维护测试；它不代表原生 Agent 的真实文件读取，也不从任意自然语言样本猜测文种。

## 显式映射

| genre | 唯一主叶 | 条件附加页 |
|---|---|---|
| `工作要点` | `references/genre-playbook-work-priorities.md` | 按既有通用路由条件加载 |
| `工作总结` | `references/genre-playbook-work-summary.md` | 按既有通用路由条件加载 |
| `周报`、`月报` | `references/genre-playbook-report.md` | 任务明确要求字段式或保留字段名、字段顺序、字段换行时，附加 `references/field-editing.md` |

- 起草、只审核、审核后重写三种模式共用同一主叶选择逻辑。新增测试逐一确认上述四个显式 genre 在三种模式下只有一个 `genre-playbook-*` 主叶。
- 周报、月报不再命中工作总结或工作要点；普通周期报告不加载字段页，只有明确字段要求时才加载。
- 没有为测试样本增加自然语言文种推断或专用分支；原有信息选择、审核和终稿检查链保持既有 fixture 行为。

## 文件差异

- `maintenance/evals/official-writing/providers/agent_writer.py`：登记工作要点主叶和字段附加页；将 `工作要点`、`工作总结`、`周报`、`月报` 分入各自明确集合；让起草和审核共用的主叶函数及完整路由保持同一归属；加入周期报告字段条件函数。
- `maintenance/tests/test_promptfoo_eval.py`：增加四个 genre × 三种模式的唯一主叶检查，以及普通周报、字段式周报、字段式月报、字段式工作总结的条件附加页检查。
- `maintenance/tests/test_reference_rewrite_contract.py`：把 `genre-playbook-work-priorities.md` 加入候选新增页面集合。当前共享差异中的主持词、述职两页登记属于前一独立原子。

## 验证

1. `python -m unittest maintenance.tests.test_promptfoo_eval`：PASS，30 项全部通过。
2. `python -m unittest maintenance.tests.test_promptfoo_eval.PromptfooProviderTests.test_summary_priorities_and_periodic_reports_keep_one_primary_across_modes maintenance.tests.test_promptfoo_eval.PromptfooProviderTests.test_periodic_report_field_editing_is_conditional`：PASS，2 项全部通过。
3. `python -m unittest maintenance.tests.test_reference_rewrite_contract.ReferenceRewriteContractTests.test_all_reference_pages_have_explicit_architecture_mapping`：PASS，1 项通过。
4. `python -m unittest maintenance.tests.test_reference_rewrite_contract`：运行 27 项，1 项失败。失败为 `test_mirror_contains_rewritten_overlay`，具体是 canonical `reference-index.md` 与镜像不同；镜像明确不在本原子修改范围内。其余 26 项通过。
5. `git diff --check -- maintenance/evals/official-writing/providers/agent_writer.py maintenance/tests/test_promptfoo_eval.py maintenance/tests/test_reference_rewrite_contract.py`：PASS；仅输出工作区既有的 LF/CRLF 提示，无空白错误。

## 状态边界

未修改产品、manifest、镜像、`run_eval.py` 或其他合同断言，未提交。`output/summary-priorities-native-r1` 的原生比较由独立原子负责；现有报告、周报正文可供评审，但全量文本质量仍未验收，本 fixture 结果不构成质量通过结论。
