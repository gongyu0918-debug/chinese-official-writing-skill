# R8 Word 产物恢复与核对

核对日期：2026-09-13。范围仅为 `combined-native-r8-word` 的 3 个请求 × 2 个模型 × baseline/candidate，共 12 次历史调用；没有调用模型、重写稿件或修改产品。

**12 份 DOCX 均从绑定的原临时目录恢复，恢复前后及渲染后 SHA-256 一致。** 其中 11 份含对应申请或只排版文本，另 1 份是仅含 `XX` 的生成调试产物。4 份只排版文件均保留给定文字、数字、标点和日期空字段。12 份均经只读导出和逐页图像检查，均为单页，未见缺字、裁切、重叠或意外空白页。

这补齐了 **R8 历史文件可恢复性、文字核对和本机版式检查**；不能写成“12 次完整交付通过”，也不能写成当前候选通过。原调用仍为 6 次技术完成、6 次超时缺 final；已完成调用中还存在具体事实增补和交付链接问题。

## 来源与证据限度

| 项目 | 绑定或核对结果 |
| --- | --- |
| 原绑定 | `output/combined-native-r8-word/binding.json`；本次保存副本 `source-binding.json` |
| baseline 源提交 | `1ce7112303172478faa2392667a2de1098eb912c` |
| R8 candidate Git HEAD | `85ee17b2c06874a81ada872ef8812bebe93f3627`；这是原绑定字段，不是本次当前产品 HEAD |
| R8 candidate 冻结源 | `output/combined-candidate-r8/skill` |
| baseline snapshot fingerprint | `4ac78943f1d5f7660c879360fdee0163f43d8e87dd951838f7a7cddaab81004f` |
| candidate snapshot fingerprint | `dfe6889f3335f601b539e3f584656ca8fe080fc2493a6d5ad4e1421ab4b2cb9d` |
| 模型 / effort | `m3 = minimax-cn/MiniMax-M3`；`m4 = ollama-cloud/glm-5.3-flash`；12 条记录均为 `medium` |
| 原运行器 | Codex CLI `0.153.4`；超时 240 秒；每次独立 workspace；runner SHA `dd94c31fafcdfd1442b5ee97d671b05857a5800f3ba58d204de1263660bb4184` |
| 原运行目录 | `C:\Users\admin\AppData\Local\Temp\cow-native-combined-native-r8-word-4p4c252d`；只检查绑定中这 12 个调用的 workspace |
| 归档指针 | `maintenance/tests/evidence/common-layer-r10/archive-e.json` |
| ZIP | `F:\Workspaces\chinese-official-writing-skill-archives\experiments\reference-rewrite-20260913-common-layer\native-writing-batch-e.zip` |
| ZIP SHA-256 | `8dd5dc9b7cb8a2e9b30520d654a809fbb873699e675842b800c1f3afef3c1804`，与索引一致 |
| ZIP 目录核对 | 全包 1821 个条目；Word 组 226 个条目；全包没有 `.docx` 或 `.pdf` 条目。未加载其他组原始稿件或 trace |
| 记录一致性 | 当前 12 个单次 result 与 6 个 final，共 18 个文件，均与 ZIP 对应条目逐字节同 SHA |

原 result 的 `draft_sha256` 是 final 文本哈希，不能拿来证明 DOCX 哈希。原归档没有 DOCX 字节或当时 DOCX SHA；因此本次能证明“从绑定的原路径读取并保全了当前仍存的文件，且其文本与原记录相互印证”，不能补造历史文件自生成时起未变化的证明。恢复文件 SHA 见文末表及 `recovery-index.json`。

保存的 3 组历史 PDF/PNG 位于各调用目录的 `historical-qa/`，保留源路径和 SHA，仅作历史旁证。本次版式结论使用从恢复 DOCX 新导出的 `qa-current/` 图像。

## 原请求与文字核对口径

| case | 原请求的决定性要求 | 核对方法与结果 |
| --- | --- | --- |
| `scope_word_complete_signoff` | 旧打印机经常卡纸；教务处拟购一台；预算 1800 元；报学校审批；完整申请、落款完整并排成 Word | 3 份有标题、主送、申请事项、预算、请批语和教务处落款，日期为当时当天 2026 年 9 月 13 日；M3 baseline 仅为 `XX`，没有形成对应正文 |
| `scope_word_today` | 增加 8 月 20 日维修后仍卡纸；完整申请；落款教务处；日期用今天；Word | 4 份均有维修事实、1 台、1800 元、教务处及 2026 年 9 月 13 日落款。当天草稿日期按本轮已明确口径允许，不重开日期争论 |
| `scope_word_format_only` | 尚未定稿，只排版；所有文字、数字、标点和空字段原样保留 | 4 份逐项与给定 5 个非空段落完全一致，包括 `购置打印机申请`、`学校：`、正文中的 `1800`、`申请单位：教务处`、`日期：____年__月__日`。只忽略排版新增的空段，不忽略文字内的空格或标点 |

对全部 12 份还核对了：DOCX 全部 `w:t` 文字与主体段落一致；Word 只读读回与 XML 文字一致；PDF 提取文字与 XML 去除空白后相同；未发现页眉、页脚、脚注、尾注或批注故事部分；DOCX 内没有“文后提示”“结构说明”“脚本复核”“检查结果”“文件位置”等包装提示。这里的检查是对已恢复文件本身，不等同于评定原 final 的所有说明正确。

## 逐次结果

“明确绝对路径”表示 final 中的目标能定位到本次实际找到的原文件；没有重放原宿主 UI 点击，所以不把它提升为当时下载点击成功。“占位链接”和“相对链接”另列。

| 调用 ID | 原技术状态 | 正文 / 只排版核对 | 原交付链接证据 | 本次版式 |
| --- | --- | --- | --- | --- |
| m3-complete-baseline | 超时 240.03 秒；无 final | **严重：`out.docx` 只有 6 处 `XX`，无真实标题、正文和落款** | 无 final、无交付证据 | 单页能打开，但不是申请成稿 |
| m3-complete-candidate | returncode 0；101.84 秒 | 要素在；**严重：擅加“本年度办公经费中列支”；另加入“黑白激光”采购类别**。日常打印影响、购置目的可作合理分析，不以“原文没逐字写”一概否定 | `/abs/path/关于购置打印机的申请.docx` 是占位路径，未定位实际文件 | 单页可读；无裁切重叠 |
| m3-format-baseline | returncode 0；92.86 秒 | 5 个非空段文字逐字一致；日期空字段保留 | `/abs/path/购置打印机申请.docx` 是占位路径 | 单页可读；主送和字段随正文缩进，属于可改善的版式细节，不是文字失真 |
| m3-format-candidate | returncode 0；193.03 秒 | 5 个非空段文字逐字一致；日期空字段保留 | DOCX 是相对链接；另带两个辅助脚本链接，不能证明宿主可直接解析文件 | 单页可读；主送也缩进；署名、日期右排 |
| m3-today-baseline | returncode 0；157.70 秒 | 维修事实、数量、预算、落款完整；没有擅填经费来源 | 明确绝对路径，原文件在；未重放 UI 点击 | 单页可读；标题、主送、正文、落款分开 |
| m3-today-candidate | returncode 0；138.66 秒 | 要素在；**严重：擅加“资金从本单位办公经费中列支”**，不能由办公采购常识确定经费来源 | `/abs/path/教务处关于购置打印机的申请.docx` 是占位路径 | 单页可读；无裁切重叠 |
| m4-complete-baseline | 超时 240.17 秒；无 final | 申请要素完整；金额大小写一致；用途和常见直接影响属于可接受分析 | 无 final、无交付证据 | 单页可读；署名、日期与正文间留白较大，但无跨页或脱离阅读顺序 |
| m4-complete-candidate | returncode 0；142.81 秒 | 申请事项完整；标题采用“请示”。这是普通学校事务申请的文种选择待校准点，不据此声称 Word 丢文 | 明确绝对路径，原文件在；未重放 UI 点击 | 单页可读；标题、正文、落款完整 |
| m4-format-baseline | 超时 240.20 秒；无 final | 5 个非空段文字逐字一致；日期空字段保留 | 无 final、无交付证据 | 单页可读；主送顶格、署名日期右排 |
| m4-format-candidate | 超时 240.17 秒；无 final | 5 个非空段文字逐字一致；日期空字段保留 | 无 final、无交付证据 | 单页可读；主送顶格、署名日期右排 |
| m4-today-baseline | 超时 240.03 秒；无 final | 维修事实、数量、预算、落款完整；无经费来源增补 | 无 final、无交付证据 | 单页可读；无裁切重叠 |
| m4-today-candidate | 超时 240.20 秒；无 final | 维修事实、数量、预算、落款完整；虽为仅 2308 字节的最小 OOXML 包，文字能正常读取与显示 | 无 final、无交付证据 | 单页可读；无缺字或重叠 |

上述 ID 中 complete / today / format 分别缩写原 `scope_word_complete_signoff` / `scope_word_today` / `scope_word_format_only`；下面文件表和机器索引使用完整 ID。

`m3-complete-baseline` 的原 result `item_29` 已把多处文字写作 `XX`，`item_36` 成功生成 `out.docx`，与恢复内容相符；不是本次恢复丢失中文字。旁边 `test.docx` 只是 `test` 调试文件，没有当成申请成品重复恢复。

文后提示与正文的物理隔离成立，但 2 处 final 说明值得保留为历史失败证据：M3 complete candidate 先把未提供的经费渠道写进 DOCX，再在文后让用户替换，不能抵消正文增补；M3 format candidate 把 `学校：` 主送行理解为待填空字段并建议填入或删除，不适合当作只排版交付的必要提示。这些内容未进入 DOCX。

## 渲染过程与范围

已按 documents 技能读取规则并解析工作区依赖，使用 bundle `26.905.11957` 的 Python 和 PowerShell。先运行技能 `render_docx.py`，限制 PATH 为 bundle，结果因 `LibreOffice soffice.exe was not found on PATH` 退出，日志在 `packaged-render-probe.log`。没有使用用户安装的桌面 LibreOffice。

随后用本机 `Word.Application` COM（报告版本 `12.0`）只读打开恢复副本，关闭宏、关闭提示并隐藏窗口，导出 PDF；每份单独创建实例，处理首轮复用实例遇到的 RPC 断连。脚本为 `render-recovered.ps1`。由 bundle 的 `pdf2image` 和 Poppler 将 PDF 转成 130 DPI PNG，并使用 `view_image` 原图逐份检查 12 页；全部输入 DOCX 渲染前后 SHA 不变。`word-render-results.json` 保留 PDF 页数、读回文字、图像路径和 PDF SHA，`content-checks.json` 保留文本核对布尔结果。

结论仅覆盖这批普通单页申请在该本机渲染路径中的可读性，不是 GB/T 9704 全项目认证，不是跨平台、红头、复杂表格、多页附件验收。原只排版请求没有要求统一使用红头或正式发文版记，不能据此额外判缺项。

## 下一步最少补什么

1. **R8 文件恢复本身无需重跑模型。** 12 份原文件已保全，现有文字和版式结果可以更新原先“尚未恢复 / 未视觉检查”的证据限度。
2. 若要证明最终候选普通 Word 功能，最少仍需在冻结最终候选上重跑这 3 个原请求，保存真正最终 DOCX、SHA、原 final 中可定位的持久路径及逐页预览。它们分别覆盖完整落款、显式今天、只排版逐字保留，不能互相替代；若继续保留双模型对照，则为 3 × 2 = 6 次 candidate 调用。本次没有执行，也不新增任务门禁。
3. 如需完整的“最终候选优于 / 不退于 1.x 金线”Word 对照，应按原 3 请求 × 2 模型 × 2 arms 完成对照；R8 历史文本可作为已知基线现象，6 次缺 final 的旧调用不能计为历史完整交付通过。不要为补旧归档再盲目重跑 R8。
4. 下一轮应直接看见的改进证据：不再留下 `XX` 调试成品；不再把预算推成已确定经费来源；只排版仍保留日期空字段；final 使用保存后的真实文件路径；正文、文后提示、辅助脚本分开。日期和一般目的 / 直接影响沿用本轮已确定口径，不重新收紧。

## 恢复文件与 SHA-256

以下均为原文件逐字节副本；不是改稿或重新生成。完整原路径、大小、时间戳、原 final 链接、原记录哈希见 `recovery-index.json`。`original-call-evidence.json` 仅摘录相关命令的生成 / 读回 / 文件位置证据。

| 调用 / 恢复文件 | SHA-256 |
| --- | --- |
| [m3-scope_word_complete_signoff-baseline / out.docx](<F:/Workspaces/chinese-official-writing-skill/output/route-worktrees/reference-rewrite-20260912/output/rewrite-word-recovery-r15/m3-scope_word_complete_signoff-baseline/out.docx>) | `80270673e982e6389fb71d353480d725cf0f071b6b692efa47d5dbb93d29e968` |
| [m3-scope_word_complete_signoff-candidate / 关于购置打印机的申请.docx](<F:/Workspaces/chinese-official-writing-skill/output/route-worktrees/reference-rewrite-20260912/output/rewrite-word-recovery-r15/m3-scope_word_complete_signoff-candidate/关于购置打印机的申请.docx>) | `79f0d967b671802683fdf1b630990829ec028ae81984c1a6af4cf3b3f3d3a5d8` |
| [m3-scope_word_format_only-baseline / 购置打印机申请.docx](<F:/Workspaces/chinese-official-writing-skill/output/route-worktrees/reference-rewrite-20260912/output/rewrite-word-recovery-r15/m3-scope_word_format_only-baseline/购置打印机申请.docx>) | `30361e35cec63a5f8ee563522067d2e5062415198b1c74da217569c82e53aa06` |
| [m3-scope_word_format_only-candidate / 购置打印机申请.docx](<F:/Workspaces/chinese-official-writing-skill/output/route-worktrees/reference-rewrite-20260912/output/rewrite-word-recovery-r15/m3-scope_word_format_only-candidate/购置打印机申请.docx>) | `b27cf8bfb9c5d0b10594ee54a40057601e16230b5fb420d63856e6f6ac6367ec` |
| [m3-scope_word_today-baseline / 打印机购置申请.docx](<F:/Workspaces/chinese-official-writing-skill/output/route-worktrees/reference-rewrite-20260912/output/rewrite-word-recovery-r15/m3-scope_word_today-baseline/打印机购置申请.docx>) | `af5568abf8943edd2e5c01473b2ad66a1142588e2936abb052182c16fc1d4ac3` |
| [m3-scope_word_today-candidate / 教务处关于购置打印机的申请.docx](<F:/Workspaces/chinese-official-writing-skill/output/route-worktrees/reference-rewrite-20260912/output/rewrite-word-recovery-r15/m3-scope_word_today-candidate/教务处关于购置打印机的申请.docx>) | `364b7ace4fdcdf99d78b80e4f9aa259fbb175b8df68216ab9aa3f47b7187cc7c` |
| [m4-scope_word_complete_signoff-baseline / 教务处关于购置打印机的申请.docx](<F:/Workspaces/chinese-official-writing-skill/output/route-worktrees/reference-rewrite-20260912/output/rewrite-word-recovery-r15/m4-scope_word_complete_signoff-baseline/教务处关于购置打印机的申请.docx>) | `004c6c04c0ca25361d5d78922e4583fa346d3051201f490e182fbd2f785a6d0a` |
| [m4-scope_word_complete_signoff-candidate / 关于购置打印机的请示.docx](<F:/Workspaces/chinese-official-writing-skill/output/route-worktrees/reference-rewrite-20260912/output/rewrite-word-recovery-r15/m4-scope_word_complete_signoff-candidate/关于购置打印机的请示.docx>) | `8323e34e014ab3fb728da54f7a2a4a991afb7318817e444ac13551bc588d4739` |
| [m4-scope_word_format_only-baseline / 购置打印机申请.docx](<F:/Workspaces/chinese-official-writing-skill/output/route-worktrees/reference-rewrite-20260912/output/rewrite-word-recovery-r15/m4-scope_word_format_only-baseline/购置打印机申请.docx>) | `f95761415419e16f558a2f7b171fc6eb79c6ff53a4a6efb143ee1f9cbcde75d4` |
| [m4-scope_word_format_only-candidate / 购置打印机申请.docx](<F:/Workspaces/chinese-official-writing-skill/output/route-worktrees/reference-rewrite-20260912/output/rewrite-word-recovery-r15/m4-scope_word_format_only-candidate/购置打印机申请.docx>) | `f02b47760f6d6dff47d4ca6f49c068cc88be6f5857d1b7f41e39070728e11edd` |
| [m4-scope_word_today-baseline / 教务处关于购置新打印机的申请.docx](<F:/Workspaces/chinese-official-writing-skill/output/route-worktrees/reference-rewrite-20260912/output/rewrite-word-recovery-r15/m4-scope_word_today-baseline/教务处关于购置新打印机的申请.docx>) | `7d20711159c84284ea9cc61009befed71c45905a80dc46f2ed7faac21d2157cf` |
| [m4-scope_word_today-candidate / 教务处关于购置打印机的申请.docx](<F:/Workspaces/chinese-official-writing-skill/output/route-worktrees/reference-rewrite-20260912/output/rewrite-word-recovery-r15/m4-scope_word_today-candidate/教务处关于购置打印机的申请.docx>) | `b72c28268dd2fc4213baed41d1c250a792de69f68fc459ec1e12262d344994f5` |

核对索引：[recovery-index.json](<F:/Workspaces/chinese-official-writing-skill/output/route-worktrees/reference-rewrite-20260912/output/rewrite-word-recovery-r15/recovery-index.json>)；[content-checks.json](<F:/Workspaces/chinese-official-writing-skill/output/route-worktrees/reference-rewrite-20260912/output/rewrite-word-recovery-r15/content-checks.json>)；[word-render-results.json](<F:/Workspaces/chinese-official-writing-skill/output/route-worktrees/reference-rewrite-20260912/output/rewrite-word-recovery-r15/word-render-results.json>)；[original-call-evidence.json](<F:/Workspaces/chinese-official-writing-skill/output/route-worktrees/reference-rewrite-20260912/output/rewrite-word-recovery-r15/original-call-evidence.json>)。
