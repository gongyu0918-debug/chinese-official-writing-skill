# 测试记录

以下均为 Python `-B` 直接执行的脚本行为测试，未使用全量 discover：

- `python -B maintenance/tests/test_script_quality_r1.py`：5/5 PASS（含围栏文后提示、四反引号包三反引号、`+`/`_`/`__` Markdown、标识符/乘式负例、长附件清单、围栏占位去重和未知编码）。
- `python -B maintenance/tests/test_reading_process_lint.py`：4/4 PASS。
- `python -B maintenance/tests/test_markdown_opt_in.py`：4/4 PASS。
- `python -B maintenance/tests/test_placeholder_blind_spot_fix.py`：4/4 PASS。
- `python -B maintenance/tests/test_scene_filler_lint.py`：5/5 PASS。
- `python -B maintenance/tests/test_explanatory_tail_cluster.py`：8/8 PASS。
- 从 `test_review_regressions.py` 仅选择 `ProseLintStructureTests`、`UnresolvedStateChainTests`、`ProseLintCliTests`、`CleanProseCorpusTests`：87/87 PASS。

以上测试覆盖正文/文后提示边界、审核引文、Markdown opt-in、占位、结构、格式、附件长编号、围栏重叠去重和未知编码返回码。未运行 `test_protective_negative_tail_lint.py` 全文件作为候选门禁：其中5项是维护文档措辞契约失败，不属于本脚本行为，且相关脚本行为已由上述选择类回归覆盖。

主代理在提交 `bf79a234` 后运行 `python -B -m unittest maintenance.tests.test_draft_length -v`：12/12 PASS，8.727秒。检查TXT/MD/DOCX、表格计数、文后提示分区、输入错误、上下限及计数不启动文稿复核；与上述117项合计129项脚本行为测试。

`python C:/Users/admin/.codex/skills/.system/skill-creator/scripts/quick_validate.py chinese-official-writing` 返回 `Skill is valid!`；`git diff c2577f53 --check` 通过。主代理复核时仅将正则实现说明从用户可见的风险建议移入代码注释，并修正辅助函数docstring，检测逻辑未变。此后用AST解析确认语法有效，不为注释和提示措辞重复整批测试。
