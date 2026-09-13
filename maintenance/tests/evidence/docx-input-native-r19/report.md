# R19 收到零字号 Word 后审核修复：独立 QA

四次原生调用均给出 final，四个链接都绑定到另存 DOCX；四份稿件的正文、金额、落款及日期均完整可读，原件保持不变。GLM 候选实际调用新扫描器并处理了六条零字号提示；DeepSeek 候选没有调用扫描器。两份旧脚本基线都自主发现并修复了同一问题，因此本组证明了新检测器在一次真实调用中的有效性，未证明候选独有的成稿质量收益。

另列一处相对版式观察：GLM 候选的署名明显偏到日期左上侧，与 final 所称的对位方式不一致。它仍然可读，不能据此判为 Word 不可用或严格 GB/T 硬失败。

## 输入、范围与证据绑定

唯一原件为 `output/docx-input-native-r19/received-application.docx`，SHA-256：

`0989cecd96b1e85a5bc7eccdb7b0e4ca16260ecb23ae61161a5fd5fe19a6e068`

原件共 8 个段落，其中 7 个含文字；标题 `w:sz=44`，其余 6 个含文字 run 为 `w:sz=0`。另有一个空 run 也带零值，因此“7 个零字号节点”与“7 处文字”不能混用。

本组只处理父任务已确认 terminal 的 DeepSeek、GLM 两批，各 baseline/candidate 一次。收集快照保留两批 `binding.json`、四份完整 `result.json`、四份完整 final、原始 trace/stderr，以及运行目录中仍存在的文件。`result.invalid=[]` 且 `returncode=0` 四次均成立；收集器中旧字段 `native_reported_technical_invalid=null` 未作技术通过依据，结论使用留存的原生 `result.invalid`。没有把中间命令报错改记为技术超时。

原生 workspace 中的扫描脚本 hash 已核对：baseline 均为 `d69f2a2f02972f1ed832f1f34af2f8ccd140033c6422f95d3637e920c42b46dc`，candidate 均为 `96d79b02e0a23d7ea9eb7427b2b5b21c09cb2e03cd0f7243fdc3ab0fb1a9f460`。绑定的是本组冻结快照，不追认与父任务后来规则修改的组合验证。

`artifact-inventory.json` 留存 8 个 DOCX：4 个输入和 4 个 final 另存稿；`collection-index.json` 仅选 4 个另存稿进行渲染。输入即使被 final 作为对照链接提及，也不当作修好稿。没有缺 final、无法绑定的另存 Word 或未链接 DOCX。GLM 基线另有 19 个、GLM 候选另有 20 个非 DOCX 文件留存，包含解包 XML、脚本、PDF/PNG 等调试/预览件，均未混作交付 Word。DeepSeek 两次已清理调试文件，原生命令仍保存在 trace。

## 原生调用与修复归因

| 调用 | 真实扫描 | 实际修复证据 | 可支持的结论 |
| --- | --- | --- | --- |
| DeepSeek baseline | 原 DOCX、改后 DOCX 各一次，旧脚本均输出 `No prose risks found.` | `dump_fmt.py` 输出正文 `0.00pt`，再读 XML，自行修改字体 | 旧扫描器没有告警，模型仍自主修复 |
| DeepSeek candidate | 全 trace 的 26 条已完成 command 中没有调用 `prose_lint.py` | `w2_inspect.py`、读取 XML、`w2_fix.py`；改后正文 16pt | 修复成功，不能归因于未执行的新扫描器 |
| GLM baseline | 原稿一次、改后两次，旧脚本均无风险提示 | XML 零值检查及 zipfile 替换，7 个节点改为 32，其中 1 个为空 run | 旧扫描器没有告警，模型仍自主修复 |
| GLM candidate | 原 DOCX 用 `draft-body --structure --format`，返回 6 条 `high: docx-zero-font-size`、退出码 0；改后同参复扫无风险 | 修改新文件后，6 个含文字零值全部消失 | 新检测器真实被调用、提示被处理，未增加硬退出门禁 |

完整扫描命令、输出及具体 trace 行号在 `trace-audit.json`。关键位置：DeepSeek baseline `item_11/28/68`；DeepSeek candidate `item_6/12/22/30`；GLM baseline `item_19/26/35/37`；GLM candidate `item_17/24/26`。保留全部 agent messages，不只保留 final 摘要。

DeepSeek 候选漏读/漏执行扫描流程是本次观察到的覆盖缺口。变化的脚本未被调用，不能把这一遗漏归因于零字号实现，也不在本组修改路由规则。

## 内容、可读性和版式分开判断

四份交付稿的原始 8 段文本（含空段）与原件逐字一致，7 个非空段落也分别核对一致。保留了教务处、学校、打印机一台、预算 1800 元、2026 年 9 月 13 日及原有申请理由、请批语；没有增加正文业务事实、文号、印章或其他签发要素。这里验证的是对输入的保真，不是对申请事实做外部真实性调查。没有额外表格、其他 story 文字、修订插入/删除或宏。

四份交付 DOCX 均已用 Microsoft Word 12.0 COM 只读打开并导出 PDF，再生成页面 PNG。四页均通过实际 `view_image` 全页目视：标题、主送、三段正文、署名和日期完整，无裁切、重叠、空白正文或不可读金额。Word/XML 段落一致，PDF 去空白文本与 XML 一致，Word/PDF 页数均为一页；文字比对仅作内容佐证，可读结论来自页图。

| 调用 | 交付 DOCX SHA-256 | 字号修复 | 页图观察 |
| --- | --- | --- | --- |
| DeepSeek baseline | `6ff48bc8580be0cb7dfa3128571230df41a1c7d895add047f51a3465575b76d5` | 6→0 个含文字零字号 | 完整可读；署名、日期右缘对齐 |
| DeepSeek candidate | `86bf5ca6c46415da9d47d01676d39de954dceb6d51b258d12fdd729ed5bfaefc` | 6→0 | 完整可读；署名、日期一起比基线靠左 |
| GLM baseline | `b31d8c1881342a911636382384c5d4c3177ec2fee4bab83b8272185bc6200cb5` | 6→0 | 完整可读；署名在日期上方，仍集中于右侧 |
| GLM candidate | `fda54a81280f3a5d53e3f80a69b4496714ce05c44cc6cb73b54bb9c7fb79d901` | 6→0 | 完整可读；署名明显偏到日期左上侧，单列版式观察 |

GLM 候选的署名 `right=3200`，日期 `right=640`，两者相差 2560 twip，即 128pt，等于 8 个 16pt 字宽；final 却称署名右缘在日期右端左 2 字处，并说对位正确。该落款移动是本机页图可见的相对版式问题及自述不一致，不影响事实保留和零字号修复结论。本题未要求严格红头，不据此作全面国标判定。

父任务复看候选页：

[GLM candidate 第 1 页](F:/Workspaces/chinese-official-writing-skill/output/route-worktrees/reference-rewrite-20260912/output/docx-input-qa-r19/renders/glm--m4-review_existing_docx-candidate/docx-001/page-001.png)

## 完整消息中的旁白与多余提示

- DeepSeek baseline 含英文操作旁白；final 较长，列出元数据/缩略图清理、主送对象、采购规格和红头签发提醒。正文没有混入这些说明。其将空白缩略图用作 Word 实际不可见证明，证据强度过高；本轮只渲染另存 final，不用缩略图替代原件渲染。
- DeepSeek candidate final 把 `sz=0` 解释成“约 1pt”，且称删去落款上方空段，实际第 6 段仍为空段。其文后缺项建议扩到经费来源、机型、采购方式/比价、联系人、故障记录、预算是否含耗材、报价单，并再主动提供模板补写；这些没有污染 DOCX，仍属超过本次修复所必需的提示。
- GLM baseline final 将 7 个字号节点写成 7 处文字，未区分空 run；中间将缺少 `szCs` 说成字体回退问题，未在该中文/拉丁稿上证实。final 交付链接及改后全文，随后解释删除命令被拦截、临时文件未清理，保留了工具/环境旁白。
- GLM candidate 中间误说不是 A4，后续主动修正为原稿 A4，最终没有更改页面大小；final 的“落款对位正确”与本次页图不一致。关于缺少指定字体、PDF 使用替代字体的说明保留为模型自述，本次未审计字体安装。

## 只读与工具验证

收集前、收集后、渲染后核对了共享源文件和四个实际 native 输入；原生 `result.input_document` 的前后 hash 也逐一对照，均为预期原件 hash。4 个原生另存文件、4 个收集副本的 hash 在渲染前后均不变。

复用的 `render-readonly.ps1` 仅增加显式 `CollectionRoot` 和路径约束，默认仍为 R17；自定义根必须在本 worktree 的 `output` 下，index/input 必须在收集根内，拒绝越界及 reparse point 路径。保留宏禁用、隐藏的独立 Word 实例、只读打开、关闭不保存和 hash 复核。首份导出成功后 `Quit` 返回 `RPC 服务器不可用 (0x800706BA)`，原记录保留为 cleanup note；PDF、页数、文字、页图及 hash 校验均成功，未将它掩盖或改记为超时，未杀用户 Word 进程。

本轮只新增 R19 `qa.py` helper，并按上述范围修改 R17 renderer；产品、`build.py`、`preregister.md`、`run_eval.py` 未由本子任务修改。父侧并行改动不纳入本子任务。未 commit，未启动模型，未重跑 R17 12 份稿，未修原件或交付稿。

执行验证使用捆绑 Python：`C:/Users/admin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe`。

| 验证 | 命令/记录 | 结果 |
| --- | --- | --- |
| helper 最小验证 | `python.exe -B maintenance/tests/evidence/docx-input-native-r19/qa.py self-test` | exit 0；链接角色/越界、零值与 szCs、输入变化分类、收集门控和依赖检查通过 |
| renderer 语法/路径验证 | PowerShell `Parser.ParseFile` 及 6 个路径用例；`preparation/renderer-result.json` | 语法无错误，6 例符合预期，Word COM 尝试 0 |
| 只收集已结束批次 | `python.exe -B maintenance/tests/evidence/docx-input-native-r19/qa.py collect --completed-batches` | exit 0；4 calls、8 DOCX、4 render selected |
| 只读 Word 渲染 | `render-readonly.ps1 -CollectionRoot <本目录绝对路径>` | exit 0；4/4 导出成功，各 1 页；保留首份 Quit RPC note |
| PDF 页图/内容佐证 | `python.exe -B maintenance/tests/evidence/docx-input-native-r19/qa.py pages` | exit 0；4 DOCX、4 页；随后实际目视全部 4 页 |
| 汇总绑定 | `python.exe -B output/docx-input-qa-r19/finalize-review.py` | exit 0；4 页 hash、源文段、零值、原件、原生结果与命令数断言通过 |

准备阶段的辅助 shell 曾有括号输入错误；只读诊断中曾查错证据文件名、使用了 PowerShell 不展开的 glob、相对路径比较失败，均在读操作失败后修正。它们没有启动额外模型/Word、改变输入或重新渲染交付稿，也没有作为产品失败计数。

`summary.json` 给逐调用结论与最终文件绑定；`visual-review.json` 绑定每页 PNG hash、目视记录和落款 XML；`trace-audit.json` 留存扫描证据、完整消息及命令索引。初始 `page-index.json` 和收集清单的 pending 目视字段作为阶段快照保留，完成状态以随后生成的 `visual-review.json` 为准。

未覆盖继承样式零字号、复杂文字字号实际选用、字体安装与跨机器渲染、所有挤压/遮挡成因，也未对完整红头/国标作认证。本组只是一份真实原件、两个模型各一对；不把 4/4 修复成功升级成广泛写作收益，且保留 GLM 候选的落款版式观察。
