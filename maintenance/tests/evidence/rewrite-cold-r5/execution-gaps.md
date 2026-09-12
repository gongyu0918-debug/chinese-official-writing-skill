# R5 四份无效样本的只读执行缺口诊断

本次只读四份样本的 `result.json`、`trace.jsonl`、`stderr.txt`、所属组 `binding.json`，以及 binding 指定 runtime 中对应单臂目录的文件清单和现存草稿。第四份 Qwen 接口技术需求样本按后续要求补入。不修改、不重跑样本，不读取单臂目录外的临时辅助脚本。唯一新增文件为本报告。以下 `L` 为相应 trace.jsonl 的一基行号，`item_n` 为轨迹原有 ID。

## 总体判断

| 样本 | 可见终止状态 | 已完成的脚本 | 可见执行缺口 | 不能据此作出的判断 |
| --- | --- | --- | --- | --- |
| MiniMax `m3-responsibility_letter-baseline` | 7.25 秒，returncode=0；`turn.completed`，无 agent_message、无工具调用，最终文件为空 | 无调用记录 | **无可见交付输出**；不能从 output_tokens 推断生成了什么 | 不能判为路由循环、脚本阻塞，也不能仅凭 WebSocket 警告判为环境故障 |
| MiniMax `m3-interface_technical_requirements-candidate` | 240.17 秒，returncode=null；timeout、missing_final；无 `turn.completed` | 字数 2052，exit=0；lint 两条中风险，exit=0 | **重复读页、命令/补丁错误、检查后改写未完成**；现存草稿仍有待修标记 | 没有脚本持续未返回的证据；没有明确重启主路由循环；不知道超时瞬间模型在内部做什么 |
| Qwen `m0-synthesis_advisory-candidate` | 240.17 秒，returncode=null；timeout、missing_final；无 `turn.completed` | 11 次 lint、11 次字数命令全部 exit=0；lint 每次均报告无风险 | **多轮删建改稿和重复复测，最终检查后清理草稿，未交付** | 不能判为脚本阻塞或明确路由循环；清理动作不证明最终消息已开始生成 |
| Qwen `m0-interface_technical_requirements-candidate` | 240.17 秒，returncode=null；timeout、missing_final；无 `turn.completed` | 字数 836，exit=0；lint 返回 10 条低风险，exit=0 | **首写为空、补丁载荷错误与换方式写入后，停在已返回 lint 之后，未交付** | 没有实际加载算力附加页；不能判为脚本还在运行；最终消息是否在生成不可见 |

三份超时轨迹中，所有可见 `item.started` 均有对应 `item.completed`；没有悬挂的已记录脚本 item。此结论仅覆盖轨迹记录的调用，不排除事件流没有呈现的请求或生成阶段。超时本身只证明 240 秒预算内未取得最终交付，不自动归因于模型、宿主、服务端或网络中的某一方。

## 绑定与证据范围

两组绑定均记录 CLI `codex-cli 0.153.4`、effort `medium`、timeout `240`、`project_doc_max_bytes=0`、`temporary-no-user-documents-or-credentials`。

- MiniMax 组：`output/legacy-functions-native-r5-minimax/binding.json`，模型 `minimax-cn/MiniMax-M3`，runtime 为 `C:/Users/admin/AppData/Local/Temp/cow-native-legacy-functions-native-r5-minimax-uyc52c53`。
- Qwen 组：`output/legacy-functions-native-r5-qwen/binding.json`，模型 `alibaba-token-plan/qwen3.8-flash`，runtime 为 `C:/Users/admin/AppData/Local/Temp/cow-native-legacy-functions-native-r5-qwen-0pch8dmt`。
- 两组记录的 baseline commit 为 `1ce7112303172478faa2392667a2de1098eb912c`；candidate source 均为冻结的 `output/combined-candidate-r5/skill`；candidate fingerprint 为 `465eabfa1b0078fb9030ec00e407699411002d8c9ef7082fac621de6f2488c62`。这是绑定文件中的记录，本次未重新计算候选目录 fingerprint。
- 四份 result 的 `draft_sha256` 均为空字节 SHA-256：`e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`。它不表示 runtime 从未存在中间草稿。

## 1. MiniMax 责任书 baseline：完成事件后没有可见输出

证据前缀：`output/legacy-functions-native-r5-minimax/m3-responsibility_letter-baseline`。

### 调用与返回

完整 trace 只有三行：

1. L1：`thread.started`，thread_id=`01a0970c-4f74-74e3-9f7c-17271095c96f`。
2. L2：`turn.started`。
3. L3：`turn.completed`，usage 记录 input_tokens=18374、cached_input_tokens=9344、output_tokens=355、reasoning_output_tokens=0。

result 的 commands 为空，invalid 为 `missing_final`、`missing_skill_read_trace`；`.final.txt` 文件长度为 0。当前对应单臂目录只显示 `.agents`，未发现草稿文件。

stderr 记录 PATH alias 提示、PowerShell snapshot 不支持、WebSocket `426 Upgrade Required`，随后明确 `falling back to HTTP`；最后为 `no last agent message; wrote empty content`。

### 判断

可确认的是：运行在 7.25 秒后以 returncode=0 和完成事件结束，但没有可见正文、进度消息或工具动作。355 个输出 token 的计费记录不能还原其内容，不能据此声称模型已读 Skill、已写草稿或完成隐藏复核。

WebSocket 尝试失败后有 HTTP 回退记录，且出现 `turn.completed`；不能仅据这条警告认定整次请求由网络故障中断。当前证据也不足以区分模型空交付、输出未被事件流呈现或其他响应处理问题。本样本应维持“无可见最终交付、原因未定”，而非硬判环境故障或规则死锁。

## 2. MiniMax 接口技术需求 candidate：读页偏多，脚本已完成，修稿命令连续出错

证据前缀：`output/legacy-functions-native-r5-minimax/m3-interface_technical_requirements-candidate`。

### 可见顺序

| trace 位置 | 可见动作与返回 | 对执行阶段的含义 |
| --- | --- | --- |
| L3–23，item_0–10 | 宣布读 Skill；Skill 读取成功；多次列举目录，表格输出路径被截短；嵌套 PowerShell 的 `.FullName` 多次报错，但部分命令 exit=0；改用 `cmd /c dir` 后取得列表 | 前期有目录探查及命令构造额外开销；不能只看 exit=0 认作命令内容成功 |
| L25–73，item_11–35 | 读取技术需求主叶、索引、路由及共性页，全部命令返回 | 已选中技术需求，随后进行了较多共性加载与重读 |
| L74，item_36 | 消息明确确认接口需求说明使用技术需求主叶，并称接下来写稿和复核 | 主文种已明确；不是仍然在无法落位的路由中 |
| L76–84，item_37–41 | 检查目录、`Set-Content` 写入草稿成功；一次双重转义路径的 `dir` 失败；其后 `Get-Content` 成功读回草稿 | 首稿确已落盘，路径检查失败没有阻止后续读回 |
| L85–91，item_42–45 | 宣布检查；第一次 `cmd /c` 包装的字数命令因错误引号/路径不能打开脚本，exit=1；读取脚本使用页后，直接调用字数脚本成功：2052，exit=0 | 字数脚本后来已经完成；最初是调用路径错误，不能判脚本运行卡死 |
| L92–93，item_46 | `prose_lint.py --delivery-mode draft-body` 完成，exit=0，报告第 29、33 行两处 `unfinished-placeholder` | lint 已返回结果；这次调用没有 `--structure --format`，不能扩大宣称覆盖全部格式/结构检查 |
| L94，item_47 | 消息称两个“待确认”括号有功能意义，但仍决定为消除提示调整为章节首句与承接表达 | 可见模型选择进入局部修稿；不是脚本阻止返回 |
| L95–100，item_48–50 | 读回草稿后，整篇 `Set-Content` 因引号构造出错，exit=1；随后构造替换辅助脚本也报 `NOT-FOUND` 和 `\ -Encoding UTF8` 非法命令，exit=1 | 修稿没有取得可信的成功回执 |
| L101–102，item_51 | 执行辅助脚本命令标记 completed、exit=0，但输出为第 1 行反斜杠 `\` 不被识别的错误 | 最后一项也不是可信的改稿成功；没有其后的复扫或最终消息 |

### 重读与工具错误

轨迹共有 102 行：48 个 command_execution 启动及完成对、4 条 agent_message；48 个命令状态中，44 个 `completed/0`、4 个 `failed/1`。有些 `completed/0` 的 aggregated_output 含 PowerShell 错误，因此退出码不是唯一成功依据。

Skill/reference 的 `Get-Content` 共 27 次，21 个不同文件。以下 6 页各读两次：`task-route-cards.md`、`handling-elements.md`、`genre-checklist.md`、`formal-addressing.md`、`official-style.md`、`formulaic-language.md`。`SKILL.md`、技术需求主叶、`reference-index.md`、`genre-routing.md` 均只读一次。可确认重复加载和额外通用页读取；没有“主路由→其他主叶→回主路由→再重启”的明确循环轨迹。可见读取 `technical-terms.md`，但没有读取 `ai-compute-docs.md` 的命令，不能把本样本说成已经发生算力主附加页误路由。

stderr 另记录两次删除公共 Temp 列表文件被 policy 拒绝，以及三次 `tool apply_patch invoked with incompatible payload`（19:23:54、19:24:10、19:24:12 UTC）。这些错误没有一一对应的可见 file_change 事件，不能强行补齐其 payload 或在无时间戳的 trace 中猜定每次位置。诊断未读取公共 Temp 的列表或辅助脚本本体，只使用该样本已记录的命令及返回文本。

### 脚本完成情况与现存中间产物

字数脚本成功完成一次：`item_45`，2052 个非空白字符；lint 成功完成一次：`item_46`，两个中风险提示。后续未见第二次 lint 或字数复测。最后可见阶段仍是处理写入/替换错误，不能称为“在等待检查脚本完成”，也没有可见证据证明已经开始发送最终正文。

当前仍存在的文件：

`C:/Users/admin/AppData/Local/Temp/cow-native-legacy-functions-native-r5-minimax-uyc52c53/m3-interface_technical_requirements-candidate/需求确认稿_申报系统与进度查询页面接口需求说明.md`

- 文件长度：5914 字节。
- SHA-256：`1a09840f82cbf351ce33af0fe10c8a7fd1c800cdfb395e8a30e7d7d03bc420fc`。
- 本次只读文本计数：2052 个非空白字符，与轨迹成功字数记录相同；没有重跑 Skill 脚本。
- 当前第 29 行仍为 `## 四、接口协议与字段格式（待确认）`；第 33 行仍含 `（具体鉴权机制待确认）`。与 lint 当时提示对应，不能把后续拟议修正当成已写入。

该文件仅证明中间草稿存在，不能替代缺失的最终交付，也不能据本次执行诊断赋予成稿质量通过结论。

## 3. Qwen 情况综合与建议信 candidate：重复修稿复测后清理临时文件，最终交付缺失

证据前缀：`output/legacy-functions-native-r5-qwen/m0-synthesis_advisory-candidate`。

### 路由与文本处理顺序

L4–32 共读取 13 个不同 Skill/reference 文件，各一次：Skill、兼容路由、索引、报告主叶、意见建议主叶、信息选择、轻量任务、短稿、事实文种复核、抗 AI 味、lint 使用、交付、校对。L18 的消息明确说明两份稿件分别采用“报告—情况综合”和“合作性意见建议（建议信）”。两份主文种是用户明确要求的两个交付件，没有后续重读路由的记录，不能把双主叶判为路由循环。

L34–40 创建 `_draft_tmp` 并写入两份稿件。之后出现 11 个完成的 file_change item，含多次删除并重新添加 `doc1.txt`、`doc2.txt`。相关操作与脚本记录顺序如下：

| 阶段 | 改稿/复测证据 | 字数输出（doc1 / doc2） | lint 返回 |
| --- | --- | --- | --- |
| 首轮 | L37–48，item_18–23：两稿形成后分别 lint、计数 | 428 / 373 | 两次均无风险、exit=0 |
| 第二轮 | L49–62，item_24–30：两稿删除、重新添加、分别复测 | 393 / 373 | 两次均无风险、exit=0 |
| 第三轮 | L63 消息称收紧事实与状态；L64–75，item_32–37：再次删建、复测 | 466 / 362 | 两次均无风险、exit=0 |
| 第四轮 | L76–87，item_38–43：再次删建两稿、复测 | 479 / 425 | 两次均无风险、exit=0 |
| 建议信再改 | L88 消息指出“逐条答复”材料未给；L89–96，item_45–48：删建 doc2、复测 | — / 423 | 一次无风险、exit=0 |
| 最后重复检查 | L97–104，item_49–52：再次检查两稿，之前没有新增 file_change | 479 / 423 | 两次均无风险、exit=0 |

合计 **11 次 prose_lint、11 次 draft_length**，每次都有完成事件和 exit=0。所有 lint 均使用 `--delivery-mode draft-body --structure --format`，输出均为 `No prose risks found.`。以上事实证明脚本没有停在未返回状态，不能证明文章事实和建议已经全部正确。

可见这是文本反复修正与复测，不是持续等待一个脚本；后几轮不能全部称为无意义，因为消息中有事实修正理由，字数也发生变化。但最后一轮在无新增文件变更的情况下再次取得同样字数，属于可见的重复检查。没有证据支持进一步推断每轮内部思考内容或各步骤耗时。

### 末尾清理与剩余文件

L105–106 的 `item_53` 成功读回 doc2 全文（命令虽用了 `Select-Object -First 1`，`Get-Content -Raw` 返回的是整篇字符串）。该返回保留了当时的 423 字建议信中间文本。

L107–108 的 `item_54` 随后执行：删除 `_draft_tmp/doc1.txt` 和 `_draft_tmp/doc2.txt`，再删除 `_draft_tmp`，最后 `Test-Path`。返回 completed、exit=0、输出 `False`。本次只读检查 binding 指定的单臂目录，只剩 `.agents`，没有 `_draft_tmp` 或现存草稿。

stderr 在这之前记录过目录递归删除被 policy 拒绝（19:27:07 UTC）；最后的逐文件清理命令有独立成功记录，不能把先前拒绝推定为最后文件仍在。stderr 另有一次 invalid hunk（19:24:43 UTC）和一次同一文件多操作的 invalid patch（19:26:59 UTC）。这些均未阻断所有后续执行，之后仍有成功写入和脚本检查。

因此，只能确认两份中间草稿曾落盘并被检查，随后被原运行清理。当前没有可读取的最后草稿文件；doc2 的最后文本可见于 trace 返回，doc1 的最后可见检查值为 479。本次未按轨迹重建任何草稿，也不把 trace 残留包装成最终交付。

### 超时瞬间能确定什么

108 行轨迹有 40 个命令完成对、11 个 file_change 完成对、4 条 agent_message；没有未配对的 `item.started`。最后可见工具已经完成清理，未见随后 agent_message 或 `turn.completed`。其末尾位置与“准备交付前清理”相容，但轨迹没有记录最终正文生成已开始；不能确认是在等待模型继续、正在编写最终消息、响应传输未完成，还是其他未呈现阶段。

## 4. Qwen 接口技术需求 candidate：未加载算力页，写稿方式出错后已完成 lint

证据前缀：`output/legacy-functions-native-r5-qwen/m0-interface_technical_requirements-candidate`。沿用上列 Qwen binding，case=`interface_technical_requirements`、arm=`candidate`。result 记录 240.17 秒、returncode=null、invalid=`timeout, missing_final`、usage 为空。

### 普通技术需求是否实际误入算力

完整轨迹的读页顺序为：L6 Skill → L10 技术需求主叶 → L12 信息选择 → L14 短稿 → L16 交付 → **L18 抗 AI 味** → L20 办理要素 → L22 事实文种复核 → L24 lint 使用。9 个不同文件各读一次。

L18 确实读取了具有扩大触发文字的 `anti-ai-patterns.md`；但其后没有读取 `ai-compute-docs.md`、`technical-terms.md` 或其他算力资料的命令。两次目录列表出现算力页文件名只是文件枚举，不能算作读页。**此样本不支持“抗 AI 味已经造成实际算力页误加载”的结论**；它也不能证明触发文字在其他任务中没有风险。

没有主文种反复转换或路由重读；普通技术需求主叶已经读到，不能将该 timeout 归因于明确路由循环。

### 关键调用顺序与最后完成状态

| trace 位置 | 调用/返回 | 判断 |
| --- | --- | --- |
| L25–26，item_11 | `Set-Content ... -Value ([Console]::In.ReadToEnd())` 返回 completed、exit=0 | 仅此返回不能证明已写入稿件 |
| L27–30，item_12–13 | 文件长度为 2；字节为 `13,10` | 首写只有 CRLF，没有正文；标准输入读取已返回，不能说它一直等待输入 |
| L31–32，item_14 | file_change 报告成功添加 `out.md` | 有一个成功写入事件；stderr 中的其他失败补丁不能否定它 |
| L33–36，item_15–16 | base64 解码写入 `doc.md`，返回长度 2483，并列出文件 | 已取得实际草稿；属于改用写入方式，并非仍在读页 |
| L37–38，item_17 | `draft_length.py doc.md` 返回 `836 ... 已统计`，exit=0 | 字数脚本已完成 |
| L39，item_18 | 英文进度消息说明 out.md 已写入，正写目标文件并检查 | 这是进度说明，不是最终正文 |
| L40–41，item_19 | base64 写入中文目标文件，返回长度 2483，exit=0 | 目标文件也已落盘 |
| L42–43，item_20 | `prose_lint.py --delivery-mode draft-body --structure --format` 检查中文目标文件，completed、exit=0 | 最后可见脚本已经返回：7 条 `markdown-heading`、3 条 `western-bullet`，全部 low |

之后没有可见改稿、复扫、agent_message 或 `turn.completed`。43 行轨迹含 19 个 command_execution 完成对、1 个 file_change 完成对和1条 agent_message，所有启动 item 均有完成记录。

因此，最后可定位到 **lint 已完成、低风险待处理/待判断、最终交付未见**。不能说仍卡在读页或脚本执行；也不能在没有后续事件时断言模型已经开始修正格式，或正在撰写最终消息。

stderr 有四次 `apply_patch invoked with incompatible payload`（19:27:52、19:28:10、19:29:28、19:29:42 UTC），另有删除中文文件被 policy 拒绝（19:29:00 UTC）。本报告不把无时间戳 trace 的每个写入硬配到某次 stderr 错误，亦不把这些错误统称为正文生成失败：后续/同次运行已有文件与脚本成功记录可核对。可确认存在补丁调用不兼容和换写入方法的额外执行，不能精确估算其耗时贡献。

### 现存中间稿

binding 单臂目录为：

`C:/Users/admin/AppData/Local/Temp/cow-native-legacy-functions-native-r5-qwen-0pch8dmt/m0-interface_technical_requirements-candidate`

当前文件如下；本次完整只读比对，三者正文一致，`out.md` 多一个末尾换行：

| 文件 | 字节 | 非空白字符 | SHA-256 |
| --- | --- | --- | --- |
| `doc.md` | 2483 | 836 | `4bde9d47eaea02a493f2c70a9b8bb3384929fb74e9b2478e00580d41fc69f150` |
| `申报系统与进度查询页面接口需求说明.md` | 2483 | 836 | `4bde9d47eaea02a493f2c70a9b8bb3384929fb74e9b2478e00580d41fc69f150` |
| `out.md` | 2484 | 836 | `7707be9f564537b9a2b3f611f9be98f66bff4af21ea7051d11d6928608be152d` |

中文目标文件仍含 lint 所报告的 Markdown 标题和数字编号，没有可见后续改稿结果。836 来自原运行的字数输出，当前计数只是本次只读文本核对，没有重跑任务或 Skill 脚本。这三份文件都是中间产物，不是三份交付件，更不能冒充缺失的最终消息。

## 可复核结论与保留不确定性

- 责任书 baseline 属于**无可见输出而正常结束**；具体丢失环节未定位。
- MiniMax 接口 candidate 属于**较多加载/重读，加上工具调用与修稿错误，未完成检查后交付**。字数与 lint 已经返回，现存文件仍是带原提示标记的中间稿。
- Qwen 双稿 candidate 属于**多轮修稿和复测后，已清理中间文件但未得到最终交付**。最后重复检查已有成功记录，不能再解释成“脚本还在跑”。
- Qwen 接口 candidate 属于**首写空文本、补丁调用错误和换方法写入后，lint 已返回但未取得最终交付**；实际没有读算力附加页，也没有后续改稿事件。
- 四样本均没有足以确认的无限路由循环。MiniMax 的共性重读、Qwen 双稿的删建复测是已观察到的额外执行动作；不能仅因重复次数或 timeout 就把它们升级为规则死锁。
- 四份 stderr 共有的 WebSocket 426 都跟随 HTTP 回退；三个超时样本随后还完成了本地工具调用。因此，426 不能单独解释终止结果。没有逐调用时长和最终消息增量事件，无法把 240 秒精确分摊给读页、模型生成、重试或服务等待。
- 本报告是执行缺口诊断，不修改无效判定，不替中间稿作盲评，也不生成或补交最终正文。
