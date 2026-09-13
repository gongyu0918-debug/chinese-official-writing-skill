# DOCX 显式零字号原型预登记（R17）

授权范围是输出目录原型与本证据目录；不改 canonical、镜像或真实 DOCX，不 commit，不跑新模型。当前独立工作树 HEAD 为 `88e804348573cf913c14d7c5ceba85d89ecafd02`。canonical 脚本 SHA-256 为 `d69f2a2f02972f1ed832f1f34af2f8ccd140033c6422f95d3637e920c42b46dc`；运行前后核对。

基线和候选分别保存为 `output/prose-docx-zero-r17/baseline/scripts/prose_lint.py`、`output/prose-docx-zero-r17/candidate/scripts/prose_lint.py`。只在 CLI `--format` 且输入真实 `.docx` 时收集文本运行直接 `w:rPr/w:sz` 或 `w:rPr/w:szCs` 的显式零值；忽略没有非空白 `w:t` 的运行及非运行格式节点。只读报告，使用既有 Finding 的 path、line、severity、label、match、excerpt 六字段；位置给出部件、部件内运行序号及提取文本行号。正文提取、既有检查结果、无 `--format` 和普通文本行为保持一致。

复用现有 ZIP 打开、XML 遍历、正文/页眉/页脚/脚注/尾注/批注部件选择和 InputReadError 流程，不另写字体引擎。只查直接运行属性，不递归寻找 rPrChange 等历史格式。字号继承、样式优先级、字体安装、字符缩放、行距挤压及实际渲染均不属于本原型。字号属性只构成风险提示；特别是 szCs 仅作用于复杂文字，不能据此断言整个运行已经不可见。

依据：[Microsoft FontSize](https://learn.microsoft.com/en-us/dotnet/api/documentformat.openxml.wordprocessing.fontsize?view=openxml-3.0.1)、[FontSizeComplexScript](https://learn.microsoft.com/en-us/dotnet/api/documentformat.openxml.wordprocessing.fontsizecomplexscript?view=openxml-3.0.1) 分别说明 sz/szCs 采用半磅单位并存在样式继承。本地 `read_docx`、`scan_input_files` 和既有 XML 审计是实现与失效证据。格式节点值为零是本次检测目标，不由网页推断真实稿件效果。

先比较 `output/final-word-qa-r17/artifact-inventory.json` 绑定的 12 份 recovered 原件；运行前后核对 SHA-256，保留每臂命令、stdout、stderr、退出码及 hash。目标文件 `m4-scope_word_complete_signoff-candidate` 的 SHA-256 必须为 `0989cecd96b1e85a5bc7eccdb7b0e4ca16260ecb23ae61161a5fd5fe19a6e068`，既有审计列出段落 2、3、4、5、7、8 的 6 个非空零字号运行；标题字号 44 不应被报。候选应新增 6 个定位风险，基线不具此检测；其他 11 份不新增零字号风险，去掉新标签后候选结果与基线一致。12 份另比较无 format 输出，须完全一致。

然后用少量直接构造的 ZIP/XML fixtures 检查 sz、szCs、双属性单运行、正常/空白/无文本/段落格式/历史格式反例、表格及页眉等部件位置、普通文本和 stdin、flag gating、三种交付模式与 strict/读取错误退出码。继承零字号 fixture 明记预期不检测，以揭示边界而非声称正常。优先真实稿件比较，不因一个正例通过扩大测试范围或添加模型运行。

登记后、首轮验证前校准：主任务指出 `w:szCs` 只用于复杂文字，纯中文/拉丁 run 的 szCs=0 不足以认定风险。当前最小原型收窄为有文本运行的直接 `w:sz=0`，szCs 单独为零保持未覆盖；新增中文/拉丁 szCs-only 反例。直接 vanish/webHidden 标记生效的运行不报；隐藏状态继承不展开。提示保持格式风险，不把属性命中升级为正文质量 FAIL；默认 CLI 返回 0，既有显式 --strict 行为保留。

首轮验证后代码复核：移除 webHidden 的排除，不把一个视图相关属性当成所有视图中的隐藏；直接 vanish 生效仍保守排除。增加 webHidden 不阻止零字号风险的反例校准。首轮脚本及调用结果另存 `output/prose-docx-zero-r17/round1/`，最终再次绑定候选 hash 验证。

验收分别报告：确定性 detector 是否命中；正常样本是否新增零字号误报；输出/读取兼容性；原件和 canonical 是否未改；native Agent 是否实际调用候选。最后一项本轮未验证，不用离线命中证明真实生命周期改善。
