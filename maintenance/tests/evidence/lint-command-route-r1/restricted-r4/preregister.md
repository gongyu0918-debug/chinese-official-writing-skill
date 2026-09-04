# stdin/help 最小修正：受限 MCP 接口 A/B 预注册

状态：`PROTOTYPE_ONLY / MODEL_NOT_STARTED`。只使用现有Claude Code 2.1.195及既有本地模型入口，不恢复任意Shell模型调用，不修改系统代理、注册表或网络设置。

## 产品原子与比较对象

控制产品固定 `5cb696fe`，即R3已有绝对路径说明的候选。实验仅在 `references/final-review-layers.md` 工具提示增加一句：“正文尚未落盘时可经标准输入传入，文件参数用 `-`；参数用法先看 `--help`。” 保留其余脚本、Skill、事实状态与复核规则；不镜像。

两臂均通过同一受限接口重新运行，同一R3的264字通知原稿和同一原始用户prompt，新增系统映射仅说明Skill/D0对应文档ID，两臂逐字相同。固定两条既有低价路线 `alibaba-token-plan-2/deepseek-v4-flash-0731` 与 `minimax-cn/MiniMax-M3`，均max：2路线×2臂=4份真实完整稿。旧R3原生命令稿只作背景证据，不合并进本次受限接口质量分母。

本轮是**受限工具接口实验**，不是原生命令A/B，不证明原生Shell权限隔离。原型绝对路径的文档正确性、stdin/help的读取/复扫收益和最终稿质量分别判断；基线本来会用help/stdin时，记目标增益未复现。

## 能力范围

- `read_document(id)` 只接受冻结清单内的 `SKILL.md`、34份普通references、`scripts/prose_lint.py` 与 `D0`；不接受调用者给出的路径或URL，不暴露Hook或维护文件。启动时验证文档SHA并缓存为只读文本。
- `prose_lint(args,text)` 只以固定解释器 `-I -B -X utf8`、固定且逐次验SHA的脚本、`shell=False` 执行；只支持枚举的format/structure/json/delivery-mode参数、stdin `-` 或独立 `--help`。不开放strict、编码、文件路径、Shell符号、脚本选择或其他程序。文本只是stdin数据。
- 模型无内置工具：`--tools ""`、`--disable-slash-commands`、`--strict-mcp-config`只加载本地stdio服务器、精确allowedTools及dontAsk。不开放Shell、网络、注册表、通用Read或Agent。沿用既有Claude进程环境构造，真实凭据不读入证据；不新增系统隔离层。
- 工具日志仅由固定harness写入运行目录，记录工具调用参数、stdin文本、返回码、输出、输入输出字节与SHA。模型不能指定日志路径或修改产品。

## 无模型门与停止条件

在任何模型调用前，以MCP客户端完成两臂stdio initialize/tools-list；工具集合必须恰为2项。分别验证D0读取、帮助、原稿Markdown finding与清理正文的正常stdin扫描；拒绝任意绝对路径、目录穿越、URL、注册表ID、空字节ID、越界argv、Shell片段、strict及未知tool。日志须证明只有3次固定程序执行且均shell=False；模型调用数为0。runner只在匹配当前fixture的contract PASS后允许运行。

每份逐行读取CLI init；工具清单不等于这2个MCP工具或init模型不符时立即终止该进程，并写停止标记阻断本批后续模型调用。正常样本继续核对只暴露这2个MCP工具，init/assistant/modelUsage均绑定同一预登记模型；所有读入文本与程序都有冻结SHA。任一边界不能确实收口即停止候选并记录，不用改权限或增加系统兜底继续。首次样本结束立即向主代理报告，再决定其余预登记样本的执行；不自动补跑、不增加路线。

## 观察与判断

主要结果是实际初扫、处理finding后对正确修订正文的复扫，是否无需写临时稿/读取脚本源码，以及成功读取文档的UTF-8字节总量（重复读取计入，另列去重）。工具拒绝、无效参数、空文本扫描和“返回码0但没有正确复扫”均如实记录。若控制本来已成功且不读源码，不据四份正文PASS认定新增说明有效。

逐份保留完整正文、工具输入输出、真实argv、模型绑定、CLI usage与费用字段。CLI费用仅是宿主报告值，不能冒充供应商账单。事实、日期、数量、未决状态、通知结构和正文交付分别审查；四份合成通知不估计普遍无错率。

本次按范围扩张/第5个提交进行最小review与基线diff，直接反控由上述无模型边界测试承担；产品轻量消融即同工具下仅删除新增一句的控制臂。模型结果未完成前不追加工程门，不合并、推送或发布。

Git LF产品字节：控制final-review 9029 → 实验 9129，仅增100 bytes；不是静态减载原子。

## 无模型环境修正记录

首次离线fixture固定于`d1db8952`，stdio握手和两工具清单正常；原稿lint因Windows下隔离Python的stdin解码产生代理字符并在输出时触发UnicodeEncodeError，未形成contract PASS，没有调用模型。原始fixture和stderr/calls完整保留于`contract-attempt-01/`。固定解释器增加`-X utf8`，不更改用户正文或lint脚本；新fixture在新目录重新验证。模型driver同时改为逐行init守卫，异常立即终止并阻断后续调用；此变化只属于受限实验控制。
