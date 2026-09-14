# 讲话、主持词与述职维护 fixture 同步 R1

## 范围

本轮只更新维护用 `maintenance/evals/official-writing/providers/agent_writer.py` 及两份最小测试。该 provider 是确定性维护 fixture，只验证显式 `genre` 到 reference 的映射，不代表原生 Agent 已按产品索引完成真实路由，也不从自然任务正文猜测主持词或述职文种。

## 显式映射

| genre | 唯一主叶 |
|---|---|
| `会议主持词`、`主持词`、`主持串词` | `references/genre-playbook-meeting-host.md` |
| `书面述职`、`述职报告`、`履职情况报告`、`现场述职发言` | `references/genre-playbook-duty-report.md` |
| `讲话稿`、`讲话`、`致辞`、`演讲` | `references/genre-playbook-speech-address.md` |

- 起草、只审核和审核后改写均复用同一显式主叶选择函数；新增测试逐一确认七个新增 genre 在三种任务模式下只有一个 `genre-playbook-*` 主叶。
- `speech-person-order.md` 只在显式讲话或主持 genre 且任务要求人物/职务/称谓顺序时叠加；述职即使出现同类文字也不加载该页。
- 原有 `information-selection.md`、审核页和终稿检查链保持既有 provider 行为，本轮未扩展 harness 阶段或自然语言分类规则。

## 文件差异

- `maintenance/evals/official-writing/providers/agent_writer.py`：新增两个 reference 映射、两个显式 genre 集合，并接入起草/审核共同的主叶选择及条件人物排序。
- `maintenance/tests/test_promptfoo_eval.py`：增加七个 genre × 三种模式的唯一主叶检查；扩展人物排序覆盖主持并排除述职。
- `maintenance/tests/test_reference_rewrite_contract.py`：在候选新增页面集合中加入 `genre-playbook-meeting-host.md` 和 `genre-playbook-duty-report.md`。

## 验证

1. `python -m unittest maintenance.tests.test_promptfoo_eval`：PASS，28 项全部通过。
2. `python -m unittest maintenance.tests.test_promptfoo_eval.PromptfooProviderTests.test_host_and_duty_genres_keep_one_primary_across_modes maintenance.tests.test_promptfoo_eval.PromptfooProviderTests.test_speech_person_order_is_a_conditional_overlay`：PASS，2 项全部通过。
3. `python -m unittest maintenance.tests.test_reference_rewrite_contract.ReferenceRewriteContractTests.test_all_reference_pages_have_explicit_architecture_mapping`：首次在主持/述职页面加入集合后 PASS；最终复跑时并行原子新增 `genre-playbook-work-priorities.md`，该测试因集合尚未包含该页而失败。主持/述职两页仍已在集合中，本轮未代替该原子登记其页面。
4. `git diff --check -- maintenance/evals/official-writing/providers/agent_writer.py maintenance/tests/test_promptfoo_eval.py maintenance/tests/test_reference_rewrite_contract.py`：PASS。
5. `python -m unittest maintenance.tests.test_reference_rewrite_contract`：最终运行 27 项，5 项失败。失败均由并行产品/维护状态或本轮禁止修改的范围引起，未顺带修复：
   - `test_all_reference_pages_have_explicit_architecture_mapping`：并行新增的 `genre-playbook-work-priorities.md` 尚未进入该测试的新增页面集合。
   - `test_machine_readable_manifest_closes_current_leaf_set`：最终失败首先报告并行新增的 `genre-playbook-work-priorities.md` 尚未进入 manifest；此前一次运行还报告 `genre-routing.md` 直接链接两个新叶而其 manifest `allowed_reads` 尚未包含这两个路径。本轮明确不改 manifest。
   - `test_mirror_contains_rewritten_overlay`：canonical `reference-index.md` 与未同步镜像不同；本轮明确不改镜像。
   - `test_sparse_plan_can_omit_unprovided_structure_sections`：并行调整后的方案页不再含旧断言要求的两个逐字句子。
   - `test_speech_page_keeps_sparse_theme_material_at_original_strength`：拆分后的讲话页保留同义事实边界，但不再含旧断言要求的逐字句子。

## 状态

未修改产品、manifest、镜像、`maintenance/evals/official-writing/run_eval.py` 或证据用 `run_eval.py`，未提交。真实写稿首叶命中和文本质量仍以根任务冻结的独立运行结果为准。
