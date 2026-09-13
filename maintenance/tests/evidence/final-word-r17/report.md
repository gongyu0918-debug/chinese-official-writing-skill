R17 Word 原生批次只读 QA（2026-09-13）

12 次调用全部结束后才收集。11 次技术完成，1 次 GLM 完整落款候选超时且没有 final；找到 12 份 DOCX，全部成功只读导出为一页 PDF，但逐页目视检查只有 11 页可正常阅读。超时调用留下的 DOCX 正文字号为 0，当前 Word 渲染不可读，继续保留失败状态。11 条 final 中，10 条 DOCX 链接能直接对应绑定 runtime 内的原件，另 1 条 WSL 路径未验证可达。不能将“找到 12 份文件”或“导出 12 页”写成 12 次成功交付。

本次仅做完成后的文件收集、文本与链接核对、渲染及逐页目视检查。没有补写稿模型调用、手修测试稿、修改产品或其他批次、安装依赖或 commit。

**绑定与方法**

- 批次为 `output/final-word-native-r17`，父侧明确确认 session 22926 退出 0、12 次结束后开始收集；不是在运行中观察到的等待文件。
- 绑定 runtime：`C:/Users/admin/AppData/Local/Temp/cow-native-final-word-native-r17-d0m5bphs`。DOCX 和尚存的候选、临时、调试文件只从每次调用绑定的 `workspace`、`tmp` 收集。共保留 1084 个文件（含调用时的 `.agents` 上下文），逐个复核原路径和副本 SHA-256，1084/1084 一致；12 份原 DOCX 在 QA 后仍可取得且哈希未变。模型已自行删除的历史临时文件不能追溯恢复，也没有借用其他批次同名文件。
- 本批 binding 回执记录 baseline commit `1ce7112303172478faa2392667a2de1098eb912c`、candidate head `88e804348573cf913c14d7c5ceba85d89ecafd02`；baseline fingerprint `4ac78943f1d5f7660c879360fdee0163f43d8e87dd951838f7a7cddaab81004f`，candidate fingerprint `b4825cba7721136b76639fe82530ad7c73ea3be54b689168d33f588b91c71060`。这些是本批绑定标识，本次没有重新开展全包静态审阅。
- m2 为 `command-code/deepseek-deepseek-v4.1-flash`，m4 为 `ollama-cloud/glm-5.3-flash`；模型、时长、技术错误以每条原始 result 为准。3 条题目与 R15 回收索引保存的原 R8 题目逐字相同；R15 只复用收集与渲染方法，不充当本批结果。
- OOXML 保留段落原文字、标点、段内空格、制表符与日期下划线。只排版稿核对全部五个非空段，仅忽略排版新增空段，不对有字段落做 trim 或空白折叠。Word 返回文本与 OOXML 再做逐段比较；PDF 文本只做去空白辅助比较，不能代替空格保留验证或目视检查。
- 复用 documents 26.905.11957 的只读 QA 流程。按已知环境使用每文件独立的隐藏 Word COM 12.0 实例，禁宏、只读打开、导出 PDF，finally 中关闭文档且释放 COM 引用；之后用指定 bundle Python、pdf2image 和既有 Poppler 以 130 dpi 转 PNG。没有再次探测已知缺少的 bundle soffice，也没有重装依赖。
- 首份 `m2-scope_word_complete_signoff-baseline` 导出成功后的 `Quit` 返回 `RPC 服务器不可用。 (0x800706BA)`，原始异常已保留。文档关闭/引用释放流程已执行，未杀任何 Word 进程；不能据此声称所有实例的退出均无异常。其余 11 份没有记录关闭或退出异常。

**分项结果**

| 调用 | 技术状态 / 秒 | 最终 DOCX 链接对应原件 | 文本核对 | 当前 Word 页数 / 目视 |
| --- | --- | --- | --- | --- |
| m2 完整落款 baseline | 完成 / 80.12 | 是 | 必要字段保留 | 1 / 可读 |
| m2 完整落款 candidate | 完成 / 158.19 | 是 | 必要字段保留；具体补写见下 | 1 / 可读 |
| m2 只排版 baseline | 完成 / 165.69 | 是 | 五段逐字一致 | 1 / 可读 |
| m2 只排版 candidate | 完成 / 80.30 | 是 | 五段逐字一致 | 1 / 可读 |
| m2 日期今天 baseline | 完成 / 146.47 | 是 | 数量、金额、维修、落款保留 | 1 / 可读 |
| m2 日期今天 candidate | 完成 / 84.28 | 是 | 数量、金额、维修、落款保留 | 1 / 可读 |
| m4 完整落款 baseline | 完成 / 135.03 | 是 | 必要字段保留 | 1 / 可读 |
| m4 完整落款 candidate | timeout + missing_final / 420.20 | 无 final | 未交付草稿中必要字段存在 | 1 / 不可读 |
| m4 只排版 baseline | 完成 / 131.34 | 是 | 五段逐字一致 | 1 / 可读 |
| m4 只排版 candidate | 完成 / 83.98 | 未验证：WSL 路径 | 五段逐字一致 | 1 / 可读 |
| m4 日期今天 baseline | 完成 / 135.36 | 是 | 数量、金额、维修、落款保留 | 1 / 可读 |
| m4 日期今天 candidate | 完成 / 159.77 | 是 | 数量、金额、维修、落款保留 | 1 / 可读 |

4 份只排版稿都完整保留 `购置打印机申请`、`学校：`、给定正文、`申请单位：教务处`、`日期：____年__月__日`，空日期没有被填入今天。8 份起草稿的 XML 文本均有一台打印机、预算 1800 元、报学校审批的请求、教务处署名和 `2026年9月13日`；本轮“今天”的核对基准为 2026-09-13。4 份维修题均保留 8 月 20 日维修后仍经常卡纸，没有改为维修完成即正常使用。未见新增资金列支来源、已批准购置状态、正文混入文后提示，或非空页眉页脚/批注等其他故事文本。12 份均无跟踪插入、删除或宏部件。

全部 12 份的 Word/OOXML 逐段文本一致，PDF 去空白文本也与正文一致；这包括不可读的字号 0 文件，因此文字可提取不能证明排版成功。每一张 PNG 均单独打开目视检查，页码、PNG 路径与 SHA 及具体观察记录在 `visual-review.json`。

**实际问题及边界**

1. **高：超时调用留下的 DOCX 当前不可读。** `m4-scope_word_complete_signoff-candidate` 的原件 SHA-256 为 `0989cecd96b1e85a5bc7eccdb7b0e4ca16260ecb23ae61161a5fd5fe19a6e068`。标题直接 `w:sz=44`（22 pt）；主送、两段正文、结语、署名、日期的 6 个非空 run 直接 `w:sz=0`，另有 1 个空 run 也为 0，字体为 `仿宋_GB2312`。未发现显式 `w:w` 字符缩放，settings 的字符压缩控制为 `doNotCompress`。当前独立 Word 只读渲染显示主送、正文和落款缩成细点、字形叠在一起，只有标题正常。这是该保留 SHA 的文件内容和当前呈现证据，不能只归因为早先 COM 查询异常或字体环境。没有重跑其他引擎，不能推断历史 LibreOffice 截图是否来自相同 SHA，也不据此确定超时根因。最小后续处理是由父侧定位生成时写入字号 0 的步骤；本轮保持原稿及失败证据。
2. **中：GLM 只排版候选的最终链接未对应当前 Windows 文件路径。** final 使用 `/mnt/c/Users/admin/AppData/Local/Temp/cow-native-final-word-native-r17-d0m5bphs/m4-scope_word_format_only-candidate/workspace/购置打印机申请.docx`。实际文件位于绑定的 `C:/Users/.../workspace/购置打印机申请.docx`，SHA 为 `2c8ff85259ef988b41ab062bd9a7fe03cd57eeb311d0459af5507b72a154b627`。没有已验证的 WSL 映射，因此未用路径猜测追认为链接成功。最小建议是 final 使用已核对的原生绝对路径。本次仅做本地路径与文件核对，没有执行 Codex UI 点击、下载或其他机器上的链接回放。
3. **中：只排版候选的文后提示误判既有内容。** DeepSeek 候选说“学校：”之后通常接主送名称、正文结尾语为空或缺位；给定 `学校：` 已可作为接收对象，正文也已有 `请予批准。`。GLM 候选说“学校”与日期均留空，同样将接收对象误判为空字段。GLM baseline 也把 `学校：` 称为“空字段”，故该类误称并非候选独有。最小建议是提示缺项前对照原文；用户要求保留空字段，不代表学校称呼必为空。问题位于 final 提示，4 份 DOCX 本身仍逐字保留，不能倒写成正文被改坏。
4. **中：两处具体补写缺少材料支持。** DeepSeek 完整落款候选写“日常需打印的通知、表格和教学材料较多”，其中实际工作量“较多”没有给定依据；GLM 超时草稿写“近期打印试卷、成绩单等各类教务材料时经常卡纸”，具体使用情节也未提供。后者仅记录为未完成调用实物中的内容问题，不追认成已交付正文。旧/现用打印机的老旧概括、卡纸对日常办公的一般影响、购置目的和必要性可由材料与常识支持，本次没有将这些正常推理计为错误。最小建议是收回无依据的具体材料量和近期使用情节。

另记录两项非阻断观察：DeepSeek 日期今天候选标题使用“请示”，而题目称“申请”；这属于主文种选择，由父侧写作复核，不计为 Word 文件损坏。该页“预算1800”与“元。”分行，金额未丢失，属于可改善的短行。DeepSeek 日期今天 baseline 的主送有约两字缩进；本题要求普通 Word，不新增严格版式门槛。自动请求词探针未命中 DeepSeek 日期今天候选，但人工可见“拟购置”与“妥否，请批示。”，未据探针判定遗漏请求。

**证据与复现**

完整路径、SHA-256、技术失败、最终原始链接均保存在 [artifact-inventory.json](F:/Workspaces/chinese-official-writing-skill/output/route-worktrees/reference-rewrite-20260912/output/final-word-qa-r17/artifact-inventory.json)。它逐份列出原 DOCX、回收副本、原始 result/final、PDF、每页 PNG，并区分最终链接所指与无已验证 final 链接的文件；final 的 `draft_sha256` 是最终消息字节哈希，不是 DOCX 哈希。11 条现存 final 的实际哈希均与 result 的 `draft_sha256` 相同。24 份 binding/result/final 原始回执已保留在 QA 输出的 `receipts` 目录，缺失 final 未补造。

- [collection-index.json](F:/Workspaces/chinese-official-writing-skill/output/route-worktrees/reference-rewrite-20260912/output/final-word-qa-r17/collection-index.json)：绑定、全部原件及调试文件清单、原始结果、原始最终消息、逐段文本和链接解析。
- [preservation-audit.json](F:/Workspaces/chinese-official-writing-skill/output/route-worktrees/reference-rewrite-20260912/output/final-word-qa-r17/preservation-audit.json)：1084 个源文件/副本复核计数、逐调用记录、24 份回执路径与哈希；保存失败 0。
- [word-render-results.json](F:/Workspaces/chinese-official-writing-skill/output/route-worktrees/reference-rewrite-20260912/output/final-word-qa-r17/word-render-results.json)、[page-index.json](F:/Workspaces/chinese-official-writing-skill/output/route-worktrees/reference-rewrite-20260912/output/final-word-qa-r17/page-index.json)：Word 版本、只读打开、导出、关闭异常、PDF/PNG 哈希与文本比较。
- [visual-review.json](F:/Workspaces/chinese-official-writing-skill/output/route-worktrees/reference-rewrite-20260912/output/final-word-qa-r17/visual-review.json)：12 页逐页目视记录，11 PASS、1 FAIL。
- [xml-format-audit.json](F:/Workspaces/chinese-official-writing-skill/output/route-worktrees/reference-rewrite-20260912/output/final-word-qa-r17/xml-format-audit.json)：各份逐 run 字号/字体/段落属性与 XML 部件哈希；问题原件的 document/styles/settings 原始 XML 另保存在 `xml-diagnostics`。
- [summary.json](F:/Workspaces/chinese-official-writing-skill/output/route-worktrees/reference-rewrite-20260912/output/final-word-qa-r17/summary.json)：分项机器计数，不给出产品整体通过结论。

在本工作树内执行的命令如下。`collect` 明确要求父侧已确认完成且拒绝覆盖既有 collection；渲染与 `pages` 的输出已保留，本次没有为了修稿重复渲染。

```powershell
& 'C:/Users/admin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -B maintenance/tests/evidence/final-word-r17/test_qa.py
& 'C:/Users/admin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -B maintenance/tests/evidence/final-word-r17/qa.py collect --completed-batch --draft-date 2026-09-13
& 'C:/Users/admin/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/powershell/pwsh.exe' -NoProfile -File maintenance/tests/evidence/final-word-r17/render-readonly.ps1
& 'C:/Users/admin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -B maintenance/tests/evidence/final-word-r17/qa.py pages
# 在逐页人工打开图像后，记录观察并复核源文件/副本及回执：
& 'C:/Users/admin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -B maintenance/tests/evidence/final-word-r17/finish_qa.py
```

准备工具的 8 个最小测试全部通过；覆盖段内空格/制表符/空日期、五段保留、最终与调试文件区分、越界路径和事实探针不冒充完整验收。原始测试输出为 `test-qa-output.txt`。PowerShell 渲染脚本在执行前通过语法解析；实际渲染进程退出 0，12/12 只读导出成功，但已如上分别记录目视失败与退出告警。没有做模型重复采样、产品回归、其他 Word/Office 版本兼容认证、打印机实打或历史超时根因复演；本轮证据不证明模型今后每次执行都会相同。
