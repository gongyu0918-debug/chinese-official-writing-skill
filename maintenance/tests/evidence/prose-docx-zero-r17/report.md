# DOCX 显式零字号最小原型结果（R17）

限定验证通过：已知失败稿新增 6 条 `docx-zero-font-size` 格式风险；其余 11 份非零字号对照稿没有新增该标签。12 份的既有风险结果及无 `--format` 输出均保持一致。此结果证明离线 detector 对本次显式零字号失效有效，不证明 native Agent 已调用候选，也不改变真实稿件的正文质量或渲染结论。

## 候选与接口

- 基线：[prose_lint.py](<F:/Workspaces/chinese-official-writing-skill/output/route-worktrees/reference-rewrite-20260912/output/prose-docx-zero-r17/baseline/scripts/prose_lint.py>)；SHA-256 `d69f2a2f02972f1ed832f1f34af2f8ccd140033c6422f95d3637e920c42b46dc`。
- 候选：[prose_lint.py](<F:/Workspaces/chinese-official-writing-skill/output/route-worktrees/reference-rewrite-20260912/output/prose-docx-zero-r17/candidate/scripts/prose_lint.py>)；SHA-256 `96d79b02e0a23d7ea9eb7427b2b5b21c09cb2e03cd0f7243fdc3ab0fb1a9f460`。
- 当前 HEAD：`88e804348573cf913c14d7c5ceba85d89ecafd02`。原型差异为 52 行增加、4 行删除；canonical 与基线 hash 一致，未改 canonical 或镜像，未 commit。共享工作树已有的编者按和其他并行改动不属于此原型。
- 复用 `read_docx` 的一次 ZIP/XML 遍历与既有部件选择。在 `scan_input_files` 中仅当 `--format` 开启时请求 DOCX 格式 findings；普通文本、stdin、无 format 和只接收字符串的 `scan()` 不新读文件。
- 原有 `read_docx(path, scope)`、`read_text()` 默认返回类型和提取文本保持；格式收集使用可选 keyword 参数。仍输出 path、line、severity、label、match、excerpt 六字段。位置为合并提取文本的行号，并附 XML 部件及该部件内运行序号；不是 Word 页码或 XML 源文件物理行。
- 当前仅检查直接 `w:rPr/w:sz` 的显式零值（包括同值的 `00`），要求运行含非空白 `w:t`。空运行、仅换行/制表符、字段指令、段落标记格式、rPrChange 历史格式不报。直接 vanish 生效时保守排除；webHidden 不作为所有视图中的隐藏依据。
- 仍使用既有 `high` 严重度作格式风险提示，文字为“相应字符可能不可见；按模板核对字号并渲染复核”。默认返回 0；用户显式 `--strict --fail-on high` 才沿用原退出码 1。没有新增门禁、自动改稿或自动修复 DOCX。

## 属性校准与未覆盖

[`w:sz`](https://learn.microsoft.com/en-us/dotnet/api/documentformat.openxml.wordprocessing.fontsize?view=openxml-3.0.1) 采用半磅单位并用于非复杂文字；[`w:szCs`](https://learn.microsoft.com/en-us/dotnet/api/documentformat.openxml.wordprocessing.fontsizecomplexscript?view=openxml-3.0.1) 针对复杂文字。按主任务校准，原型未将 szCs-only 零值报为中文/拉丁不可读；该负例已验证。实际字种选择和强制复杂文字格式不由本原型完整解析，不宣称任意字种的零属性一定影响可见性。

样式/文档默认字号继承、继承的隐藏状态、字体安装/替代、字符压缩、字距、行距挤压和实际渲染均未覆盖。继承零字号 fixture 预期无新标签，专门记录检测边界，不能把它当成版式正常。全包扫描的页眉、页脚、脚注、尾注和批注沿用既有范围；是否发布这些部件仍由使用场景判断。

首轮曾排除 webHidden；代码复核后删除该排除，并再次冻结和验证。首轮脚本/manifest/result/原始调用输出留在 [round1/](<F:/Workspaces/chinese-official-writing-skill/output/route-worktrees/reference-rewrite-20260912/output/prose-docx-zero-r17/round1>)，最终结果见当前目录。未用新一次采样替代旧证据。

## 真实 12 份原件比较

输入由 [原件清单](<F:/Workspaces/chinese-official-writing-skill/output/route-worktrees/reference-rewrite-20260912/output/final-word-qa-r17/artifact-inventory.json>) 的 recovered 路径与 SHA-256 绑定；不是重新生成的模型稿。每份运行前后 hash 均一致。[冻结输入及脚本 hash](<F:/Workspaces/chinese-official-writing-skill/output/route-worktrees/reference-rewrite-20260912/output/prose-docx-zero-r17/input-manifest.json>) 保留绑定。

| 原件 ID | 基线零字号风险 | 候选零字号风险 | 原有 findings / 无 format |
| --- | ---: | ---: | --- |
| `m2-scope_word_complete_signoff-baseline` | 0 | 0 | 相同 / 相同 |
| `m2-scope_word_complete_signoff-candidate` | 0 | 0 | 相同 / 相同 |
| `m2-scope_word_format_only-baseline` | 0 | 0 | 相同 / 相同 |
| `m2-scope_word_format_only-candidate` | 0 | 0 | 相同 / 相同 |
| `m2-scope_word_today-baseline` | 0 | 0 | 相同 / 相同 |
| `m2-scope_word_today-candidate` | 0 | 0 | 相同 / 相同 |
| `m4-scope_word_complete_signoff-baseline` | 0 | 0 | 相同 / 相同 |
| `m4-scope_word_complete_signoff-candidate` | 0 | 6 | 相同 / 相同 |
| `m4-scope_word_format_only-baseline` | 0 | 0 | 相同 / 相同 |
| `m4-scope_word_format_only-candidate` | 0 | 0 | 相同 / 相同 |
| `m4-scope_word_today-baseline` | 0 | 0 | 相同 / 相同 |
| `m4-scope_word_today-candidate` | 0 | 0 | 相同 / 相同 |

失败稿 SHA-256：`0989cecd96b1e85a5bc7eccdb7b0e4ca16260ecb23ae61161a5fd5fe19a6e068`。新增定位为主文档 run 2、3、4、5、7、8（合并提取文本行 3、4、5、6、8、9），对应主送、两段正文、请批语、落款和日期。标题的显式字号 44 未报。[六条实际 stdout](<F:/Workspaces/chinese-official-writing-skill/output/route-worktrees/reference-rewrite-20260912/output/prose-docx-zero-r17/calls/m4-scope_word_complete_signoff-candidate-format/candidate/stdout.txt>) 可直接核查。

## 实际命令与检查

```text
C:/Users/admin/AppData/Local/Programs/Python/Python313/python.exe -B maintenance/tests/evidence/prose-docx-zero-r17/run_probe.py
```

最终运行退出码 0。共 130 条有界断言（包括输入 hash、字段协议和不变性检查），76 次本地 CLI 调用；这些不是 130 个独立能力测试。真实原件占 48 次调用：12 份 × 2 臂 × format 开/关。余下是少量直接 ZIP/XML fixtures 的正反例及协议比较，无模型调用。

真实稿件使用 `--json --format --structure --delivery-mode draft-body`，关闭 format 时保留其他参数。fixture 验证显式 sz/双属性不重复、szCs-only 不报、空白/无文本/段落及历史属性、vanish=false 与 webHidden、表格/附属部件、OOXML Strict namespace、继承未覆盖、普通文本/stdin、三种交付模式、默认与 strict 退出码、文本输出以及后续 XML 部件解析失败时不泄露半成品 findings。另直接比较 12 份的 `read_docx` 两种 scope，文本完全相同。

每次调用的命令、输入和脚本 hash、stdout/stderr 原件及其 hash、退出码均在 [calls/](<F:/Workspaces/chinese-official-writing-skill/output/route-worktrees/reference-rewrite-20260912/output/prose-docx-zero-r17/calls>)。[完整结果 JSON](<F:/Workspaces/chinese-official-writing-skill/output/route-worktrees/reference-rewrite-20260912/output/prose-docx-zero-r17/result.json>) 收录逐条断言及调用记录；[简洁摘要 JSON](<F:/Workspaces/chinese-official-writing-skill/output/route-worktrees/reference-rewrite-20260912/output/prose-docx-zero-r17/summary.json>) 便于主任务引用。报告不把 JSON 命中当作 native 执行证据。

## 尚未完成与风险

- `native_candidate_invocation = NOT_RUN`。未验证 Agent 是否读取、调用并处理新风险；未修改原始失败 DOCX，也未证明正文或实际版式已修复。
- 当前只建议将此候选交主任务复核；如后续纳入 canonical，应按最终 hash 重新绑定相关最小测试及 native 调用证据。此报告不授权采用、合并、安装或发布。
- 首轮和最终证据均保留；候选范围始终只有一份普通脚本与本任务 evidence/output，未复制完整字体引擎，未新建模型测试。

## 主任务后续采用记录

主任务复核代码与12份实物对照后，按最终SHA纳入canonical，并同步五份仓库镜像。原型阶段的“未改canonical”是当时事实，不重写原回执。完整采用包冻结在output/reference-verification-r17-adopted/candidate，文件表指纹6dd2520d9782a4d1f85f8ee20c33b8aca3b49bd0414120bb3612a2157752e84d；相对编者按采用包仅脚本改变。

采用后运行ProseLintCliTests、test_draft_length、test_mit_script_boundary，29项通过，日志在采用目录minimum-script-tests.log。当前真实原件检出成立，native写稿调用新分支仍为NOT_RUN，原始超时和不可读稿未修复或追认成功。未合main、安装、推送或发布。
