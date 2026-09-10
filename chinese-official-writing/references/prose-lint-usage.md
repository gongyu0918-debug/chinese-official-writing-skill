# 草稿检查脚本使用

仅在准备调用 `scripts/prose_lint.py` 检查草稿时读取。

检查 `.txt`、`.md` 或 `.docx` 草稿时可使用 `scripts/prose_lint.py`。执行时，以本次已读 `SKILL.md` 所在目录解析脚本路径，使用带引号的脚本与草稿绝对路径。需要检查重复事项和格式噪点时加 `--structure --format`。脚本只提示语言、格式和重复风险，不检查文种要素完整性；已按增项专页起草或整体改写的稿件由该页完成成稿复核；其他文种和办理要素仍按 `references/handling-elements.md` 与命中的文种检查叶复核，报告使用 `references/genre-checklist-report.md`，请示和申请使用 `references/genre-checklist-request.md`，可研只审使用 `references/genre-checklist-feasibility-review.md`，其他文种使用 `references/genre-checklist.md`。脚本不自动改写；不得把脚本结果作为不加判断的硬性清洗命令。
