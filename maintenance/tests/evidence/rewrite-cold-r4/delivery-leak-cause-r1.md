# 最终消息过程旁白：有界归因与交付规则重排建议 R1

## 结论与证据强度

最有依据的失效环节是：扫描对象是稿件片段，最终发送时又生成了一层完成说明、路由说明或审改说明，实际最终消息没有进入同一检查范围。当前规则已有“消息从标题或正文开始”“路由记录、工具日志和自评留在内部”，所以不是完全缺少清洁要求；可能的诱因是交付对象与组装时机仍分散，尤其首页先脚本、后交付，而交付页先讲审核发现的报告方法、再讲稿件。

“写临时文件后误以为用户要文件交付”在本次读取中没有得到支持：26 份 final 没有保存/下载/稿件路径交付行为；有样本删除临时文件后才发送，最终给的是全文及过程旁白。只有 skill 路径被说成已执行步骤，不是下载路径。另一份主线主持词完全没有脚本执行和临时文件，也泄露路由，排除了“临时文件是必要原因”。不能据此排除其他未读样本存在该混淆。

另一个较具体的规则诱因是审改分支：`delivery.md:5` 无条件要求审核发现 AI 味就列原句/位置/问题/建议，与 `review-checklist.md:5,24-30` 对“纯审只提意见”“审改给改后全文”“同时要求两项才并交”的分支不够一致。活动稿轨迹表现为完整稿件之外又附已解决的问题表、改动过程和脚本标签。这是可解释的诱因，尚未由规则消融证明因果。

本报告不把两臂共有现象算作 candidate-only 回归；不评价正文写作胜负，不新增禁词或脚本检测词条。建议先试下述方案一；若全文终检对象仍漂移，再试方案二。是否采用及真实 A/B 由主代理决定。

## 实际读取与绑定

读取当前 canonical：`chinese-official-writing/references/delivery.md` 全文、`prose-lint-usage.md` 全文、`review-checklist.md` 全文，以及 `SKILL.md:77-99`。产品和测试均未修改。

读取三组 `binding.json`，读取其顶层 26 份 `*.final.txt` 并逐份核对与相应 trace 中最后一个 completed `agent_message` 的文本相等（strip 后比较，26/26 相等）。这一步排除了把中间 commentary 简单拼接进 final 的提取错误。没有借用 results 中的胜负结论。

- `speech-host-duty-main-r3`：main `1ce7112303172478faa2392667a2de1098eb912c`；candidate 来源为 `speech-host-duty-native-r1/snapshots/candidate`，binding candidate_head `ca52e80f7209fd19e177b58b4b65367078e9a66d`。模型为两路 Qwen3.8-flash 与 MiniMax-M3，effort=medium。
- `legacy-semantic-native-r1`：同一 main 与同一 candidate 来源，模型为 `command-code/deepseek-deepseek-v4.1-flash`。用户 cases 覆盖明确只要稿件、纯文本校改、短通知、算力说明和局部纪要修改。
- `lint-advice-native-r1`：baseline_ref=`ca52e80f`，baseline_commit 同 ca52e80f；candidate_source=`output/lint-advice-only-r1/skill`。此组虽然 binding 还保存 main_commit=1ce711，不能把它误当实际 baseline。模型为 Qwen 与 DeepSeek；唯一 case 要求审核并给自然简洁改好活动稿。
- 三组前缀均是“使用本目录 .agents/skills/chinese-official-writing/SKILL.md。”，`agent_documents=project_doc_max_bytes=0`，`profile=temporary-no-user-documents-or-credentials`，CLI 为 0.153.4，绑定保存各自 runtime、runner SHA 和权限配置。没有恢复 runner 内部全部宿主指令，不能排除宿主或模型默认完成简报习惯。
- 三组 candidate 的 delivery 与 prose-lint-usage 均和本次 canonical 逐字节一致；lint-advice 的 snapshots/main 两页也一致。前两组旧 main 没有同名 delivery 页，其 usage 不同。故两臂共有只能说明不是此次局部改动专有，不能证明每臂由同一句规则引起。

细读完成的五条轨迹（读取全部事件；规则读页返回按用途定位，未把进度说明当隐藏推理）：

1. `speech-host-duty-main-r3/m0-duty_oral-candidate.trace.jsonl`
2. `speech-host-duty-main-r3/m1-hosting_agenda-main.trace.jsonl`
3. `legacy-semantic-native-r1/m2-quote_proofread-candidate.trace.jsonl`
4. `lint-advice-native-r1/m2-platform_review-candidate.trace.jsonl`
5. `legacy-semantic-native-r1/m2-official_marks-candidate.trace.jsonl`

其他 21 条 trace 仅用于 final 与最后消息核对，不声称逐项分析了完整工具执行。

## 关键执行证据

| 样本与真实用户要求 | 轨迹位置与实际动作 | 最终消息表现 | 可支持的判断 |
| --- | --- | --- | --- |
| Qwen candidate 现场述职，简短自然、直接读 | trace:20 已读取 delivery，26 读 usage；28 将只有称呼和述职正文写入 `_duty_draft.txt`，长度127；30 用 draft-body/structure/format 扫描，无风险；32 删除临时稿 | trace:33 / final:1 另加“按现场述职发言（主叶路径）成稿，实测127字，语言与结构脚本检查未提示风险” | 有明确输入文本，可确认检查后新增包装。已读 delivery 也未守住最终消息边界；临时文件没有变成文件交付 |
| Qwen main 主持词，按议程串完整直接使用 | trace:4-20 读入口及写作页；没有 prose_lint、临时文件或其他命令执行写稿 | trace:21 / final:1 先报告技能路由、稀疏短稿、已读页面，再给主持词和“两点说明” | 无脚本仍泄露过程；临时文件不是该现象必要原因 |
| DeepSeek candidate 纯文本讲话校改、给全文不用Markdown | trace:3 的英文读技能说明是中间消息；19 读 delivery，33 读 usage；36-37 创建 `_lint_draft.txt`，39 draft-body 复核无风险，40-41 删除；42 为最后消息 | 最后消息新增 skill 路径、校对步骤、脚本无风险等说明，然后全文，再附未核出处和已改标题说明等 | final 与最后消息一致。文件内容未包含在 file_change 事件中，不能声称逐字还原被扫描文本；但看不到最终完整消息复扫，且文件已删后又写成品说明 |
| DeepSeek candidate 活动新闻“审核并改好” | trace:27 读 delivery；31 原稿进 draft.txt，33 扫到两处 vague-claim；38 revised.txt 只含52字新闻正文，40 以 gap-note-allowed 扫这个正文，无风险；42 测52；43 最终消息 | 技能完成说明+问题解释+改后稿+改动说明，并直接出现工具标签 vague-claim，末尾才文后提示 | 参数选 gap-note-allowed 不能代表实际输入已包含提示；已解决意见和扫描标签是在正文终检之后另加的 |
| DeepSeek candidate 明确“我只要改后稿件”的工作提示（干净反例） | trace:17 读 delivery，18 读 usage；24 标准输入扫描拟交付稿；26 又扫原稿；27 最终交付 | 最终只含用户要求保留的资料/版本标识和改后正文，无技能或脚本旁白 | 同规则、同路由模型可干净交付；明确输出约束与干净结果相容，但一次反例不能证明唯一原因。其原稿扫描竟报无风险，不能将该样本当脚本防泄露能力证明 |

26 份最终消息与末条 agent_message 相等；以上只对人工细读的案例作语义判断，没有根据关键词给全部 26 份自动打泄露率。

## 规则诱因分层

### 1. 发送对象后组装，检查对象先固定（中高置信度诱因）

`SKILL.md:93-99` 的外层动作是“脚本复核→交付”。`prose-lint-usage.md:3,15-19` 同时允许扫描原稿、正文、正文加提示和审稿意见，尚未要求在最后一次复核之前把用户实际接收的完整消息组装好。第27行“最终发送采用已检查文本，临时增加的开场或说明也纳入检查”已有防线，却把“临时增加开场/说明”当成后续可能动作，而没有正向指定最后发送的对象。

述职和新闻两份输入可还原样本都表现为扫描正文后另写包装。因果还不能钉死：也可能是模型没有遵守明确存在的第27行；因此宜用规则重排验证，而不是宣称路由已经逻辑上允许旁白。

### 2. 纯审与审改在交付页开头再次混合（中置信度诱因）

review-checklist 已分开纯审与审改，但 delivery:5 先无条件说“审核发现 AI 味问题时，列出原句或具体位置、问题表现及建议改法”。后续审改任务很容易把“列已处理问题”和“交改后稿”都视为必须。lint-advice 两臂的最终消息均可看到审稿/改动说明，candidate DeepSeek 还带出 vague-claim 标签。这与该句的处理结构吻合，但工具标签泄露仍是未遵守 delivery:22，并非该句直接授权。

把这句纳入“用户要求审稿意见”分支即可消除歧义；无需取消默认文后提示，也无需把“审核并改好”变成只审不改。

### 3. 临时文件→用户文件交付（本次证据不支持）

delivery:9 “文件交付时”没明确写用户触发条件，理论上可写得更准确；但本次没有临时稿路径被当下载链接、没有改成仅给文件，也有不落盘就泄露的样本。应把“临时文件不改变交付方式”作为低成本边界澄清，不能作为已证主因。

### 4. 默认文后提示可能承接了完成简报（中低置信度诱因）

delivery:15-20 原本承接缺项、风险、建议和旧问题；样本却塞入“已保留事实”“已修改标题”“复核无风险”等已完成动作。一方面规则允许“无实质事项时可简短说明”，另一方面也明确“自评留内部”。这是分类没有落实，而不是文后提示本身有错。应正向写清文后提示服务当前稿件使用，保留实质事项；不采用删掉所有提示的规避方式。

## 两种最小重排方案（互为备选）

### 方案一：只重排 delivery 的分支与交付对象，usage 做一句对齐（优先做局部实验）

修改限于两个页面，不增加强制读页。把 delivery 顶部改为先确定“用户最终接收什么”，再写提示规则；第5行审核定位要求移到纯审/明确要意见的分支。建议结构如下，可沿用现有原句中的实质条款：

> 起草、改写、压缩和审查后改稿，最终消息以完整稿件开始，随后是独立的文后提示。用户明确只要稿件或省略说明时，最终消息就是稿件。用户只要审稿意见时，直接给出位置、问题和建议；同时要求意见与改后稿时，交付两项。
>
> 审查后改稿先把有依据且在本轮范围内的问题修正到全文。文后提示收纳当前仍影响使用的缺项、矛盾、风险、必要建议以及上一轮未解决的问题；已解决的项目移除。没有实质事项时仍可按当前规则作一句简短说明。
>
> 用户要求文件交付时，成稿写入文件，文后提示放交付消息。用于脚本的临时文本是内部检查载体，交付方式仍按用户要求。

保留文后提示独立标题、编号/落款/附件在提示之前结束、实质检查数据如何转成具体问题等现有规范。将 usage:27 收为“最终发送本轮已检查的交付文本”，取消对后加开场的开放式描述，不再增长禁词。

预期：减少审改分支自动附“审核完成/改动说明”，强化完整消息是交付对象。限制：没有改动外层检查→交付的时间结构，仍可能出现正文扫描后才组织文后提示，应由真实测试确认。

### 方案二：在方案一交付契约基础上，把组装完整发送对象放到最后一次脚本之前

保持脚本参数和功能不变，范围为 delivery、usage 及首页相邻第四/第五步。三处职责各一句即可，不新增循环：

- 首页第四步：按 delivery 已定形态组成拟发送文本，再按 usage 做最后复核；第五步发送这份已复核的交付文本。此前原稿审查扫描仍按需保留。
- usage：原稿用于找问题；最后一次检查面向本轮实际发送的完整消息。默认稿件与独立文后提示一起按 gap-note-allowed 扫；明确只要稿件按 draft-body；纯审意见按 review-only。读过的交付规则直接应用，不要求再次整页加载。
- delivery：保留方案一全部分支与提示职责，负责规定交付件；最终发送使用已组装核对的内容，避免再次生成完成简报。

文件交付仍区分实际成稿文件与交付消息：各自按其用途检查，不把链接当正文，也不要求生成另一个交付日志。环境无法跑脚本时仍按现有人工检查与实质提示规则处理，用户明确只要正文的偏好保持。

预期：直接针对已观察到的“52/127字片段通过后另包最终消息”现象。风险：完整消息复核可能新增一次扫描或改变提示组织，需要检查总执行次数；不要把它实现为先终检正文、再终检正文+提示、再生成新提示的循环。若首次扫描本来已覆盖完整消息且未变化，直接发送。

## 留给主代理的有界验证建议

先固定同一组自然用户请求和各臂有效材料，比较当前规则与一种候选，别把增加用户禁令当作产品修复。最少覆盖默认短稿、审改、纯审、明确只要稿件四类；其中默认短稿应同时有无实质缺项的输入，审改应含可直接修的问题和真正未决问题。

评价对象是完整最后一条消息，不能截取正文再宣布干净。同步保留轨迹里的实际扫描输入、模式和最终消息，以确认：完整稿件仍在；纯审给位置问题建议；审改已经修正可改问题；默认独立文后提示保留实质缺项/风险/建议/旧问题；明确只要稿件时省提示；脚本仍真实执行。过程说明出现在中间进度消息与进入最终消息应分开记录。

本次没有进行新模型实写或 A/B，没有改产品、测试或 runner。只有只读文件/轨迹对照与本报告生成；所有因果强度按上述证据边界保留。

## 文件指纹

- `chinese-official-writing/references/delivery.md`: `6f64b596fafaf838d8aafb016c45c309c41967f8e5f0d9a8e3f9f5d901855711`
- `chinese-official-writing/references/prose-lint-usage.md`: `efbb99dbb72599e5b9614b18ad901abc5284812aacd0bc9e92177f2139d70525`
- `chinese-official-writing/references/review-checklist.md`: `c854b5b1a35785ef08f389ae7d558785dcb3ac704857ddaa12d0669db0cfe9f8`
- `output/speech-host-duty-main-r3/m0-duty_oral-candidate.trace.jsonl`: `7d0acf491a7b4193759fd8502b60431caebdbc36f59ff68672f3cccd51f21522`
- `output/speech-host-duty-main-r3/m1-hosting_agenda-main.trace.jsonl`: `bbfb08b25fc4c877848d4a667143dc1e4448994b1cde825ffa9b1f9e9819b256`
- `output/legacy-semantic-native-r1/m2-quote_proofread-candidate.trace.jsonl`: `fdae26970c58d145399b9a7f23001f9ac673eae9b2bf0bb3928f1994f8cc8f56`
- `output/lint-advice-native-r1/m2-platform_review-candidate.trace.jsonl`: `79b665eebc1e3453391a32cce20672e8726ada8905645fff76f92cf20709401c`
- `output/legacy-semantic-native-r1/m2-official_marks-candidate.trace.jsonl`: `62241d00b0e75c421c69f51ff3ab3efc99b724c062cc73b9f6d37939858f8b53`
