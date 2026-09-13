# 文稿扫描

扫描被审原稿或拟交付稿件，支持 `.txt`、`.md`、`.docx`。以已读 SKILL.md 所在目录定位脚本，草稿使用带引号的绝对路径：

```text
python "<Skill目录>/scripts/prose_lint.py" --delivery-mode draft-body --structure --format "<草稿绝对路径>"
```

按扫描对象选择模式：稿件正文用 `draft-body`，正文连同独立文后提示用 `gap-note-allowed`，审稿意见本身用 `review-only`。审核收到的原稿仍用 `draft-body`，原文件保留，修改另存新稿。

需要标准输入时用 `-` 代替路径，并将实际文本通过管道传入。对照风险位置、材料和修改范围修正问题；合理用语及引用经核对可保留。正文实质修改后复扫，最终采用已检查文本。

读取或运行失败时核对路径与格式；仍无法执行时如实记录未完成的检查。
