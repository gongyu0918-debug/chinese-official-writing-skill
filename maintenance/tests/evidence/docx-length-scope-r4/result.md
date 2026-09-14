# DOCX 篇幅读取范围修复

## 问题复现

用最小 DOCX ZIP 写入三部分：`word/document.xml` 为“正文六字计数”（6 个非空白字符），`word/header1.xml` 为“页眉字”（3 个），`word/comments.xml` 为“批注不应计入正文长度中啊呀”（13 个）。修复前实际执行：

```text
python chinese-official-writing/scripts/draft_length.py --json <scope-repro.docx>
```

输出要点：

```text
CLI_EXIT 0
count: 22
scope: draft-before-postscript
```

原因是 `draft_length.py` 复用 `prose_lint.read_text()` 的默认 DOCX 读取结果；原 `read_docx()` 会依次抽取主文档、页眉、页脚、脚注、尾注和批注。这个默认范围适合全文风险检查，不适合正文篇幅。

## 修复

- `read_docx(path, scope="all")` 保持旧默认；新增 `scope="main-document"` 时只解析 `word/document.xml`。正常表格仍由主文档 XML 的 `w:t` 文本进入计数。
- `read_text(..., docx_scope="all")` 保持旧 API 默认和 TXT/MD/STDIN 路径；参数只在 DOCX 时传给 `read_docx()`。
- `draft_length.py` 唯一改动是调用 `read_text(..., docx_scope="main-document")`，随后继续用既有 `body_lines()` 排除正文中的“文后提示”。
- 主文档部件缺失时，篇幅 CLI 按坏 DOCX 返回技术错误；未增加脚注计数开关或其他范围。

同一复现文件修复后：

```text
EXIT 0
COUNT 6
SCOPE draft-before-postscript
```

## CLI 与边界验证

同一正文“正文六字计数”分别写入 TXT、MD 和 DOCX；DOCX 另含页眉、页脚、脚注、尾注和批注。实际调用三个路径后：

```text
LENGTH_EXIT 0
LENGTH_COUNTS [6, 6, 6]
LENGTH_SCOPES ['draft-before-postscript', 'draft-before-postscript', 'draft-before-postscript']
```

同一 DOCX 的页脚含“作为AI”。默认调用 `prose_lint.py --json <same.docx>` 仍返回：

```text
LINT_EXIT 0
LINT_LABELS ['thought-leak']
```

这证明普通 lint 仍检查非正文部件。新增测试还覆盖：主文档表格计入；页眉/批注中的“文后提示”既不计数也不截断主文档；主文档自己的“文后提示”及其后内容仍排除；损坏 ZIP 和缺少 `word/document.xml` 均返回退出码 2、JSON `[]` 和明确错误。

## 测试

```text
python -B -m unittest maintenance.tests.test_review_regressions maintenance.tests.test_draft_length
Ran 103 tests in 12.697s
OK

python -B -m unittest maintenance.tests.test_draft_length
Ran 12 tests in 9.109s
OK

git diff --check -- chinese-official-writing/scripts/prose_lint.py chinese-official-writing/scripts/draft_length.py maintenance/tests/test_draft_length.py
通过；仅出现工作区既有 LF→CRLF 提示。
```

本子任务只修改 `prose_lint.py` 的 `read_docx/read_text` 区域、`draft_length.py` 和 `test_draft_length.py`。共享工作树中 `PATTERNS` 的并行差异不是本子任务所作；规则页、镜像、provider 均未修改，也未提交。
