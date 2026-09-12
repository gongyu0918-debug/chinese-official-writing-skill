# 草稿检查脚本使用

仅在确定需要 `scripts/prose_lint.py` 扫描草稿时读取本页。

## 调用

以本次已读 `SKILL.md` 所在目录定位脚本，使用草稿绝对路径并保留引号：

```text
python "<Skill绝对目录>/scripts/prose_lint.py" --delivery-mode draft-body "<草稿绝对路径>"
```

需要重复事项和格式噪点时追加 `--structure --format`。输入可为 `.txt`、`.md` 或 `.docx`。

## 解释

脚本提示语言、旁白、格式、结构和重复风险，不判断文种要素完整性，不自动改写。文种功能、办理要素、事实和状态仍按首叶、`handling-elements.md`、`final-review-layers.md` 和对应审查页判断。返回码表示扫描完成或技术失败，不等于正文质量结论；高风险结果由调用方决定人工修改或重试。

用户明确要求交付门禁时才读取 `delivery-review-gate.md` 并调用 `review_gate.py`；普通写稿不启用门禁。
