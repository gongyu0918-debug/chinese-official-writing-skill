# 1.5.7 冷审核复核与真实写作 A/B 补充

## 结论

桌面冷审核报告抓到了两个真实问题：一是 `SKILL.md`、`workflow.md` 和 OpenClaw 入口存在高密度长行与跨文件重复；二是弱模型即使加载当前 skill，仍可能出现事实补造、日期幻觉、主体关系错位、Markdown 残留和材料旁白。

但报告的核心定量结论不能直接接受。`MiniMax-M2 3/8 -> 2/8` 来自关键词评分脚本，不是独立盲评；脚本既漏掉明显事实补造，也会把审稿时引用原文的风险词算成模型违规。现有材料只能支持“1.5.7 尚未证明对该次弱模型运行有稳定净收益”，不能支持“已经证明 skill 整体不如直接写”。

本轮不修改 canonical `SKILL.md`、reference、核心 workflow 或默认加载路径。原因有二：

1. 入口压缩、长句拆分和部分 reference 密度调整的相关候选已有真实 A/B 回退记录；桌面报告提出的全部去重方案尚未逐项验证。
2. 本轮 Codex 三条件 sanity 虽然给出“实验性短协议优于当前完整入口”的方向信号，但只有 3 题，且运行时未暴露精确模型标签和 reasoning 档位，不足以授权核心流程变更。

## 审核对象与基线

- 桌面报告：`C:\Users\admin\Desktop\chinese-official-writing-1.5.7-冷审核报告.md`
- 本地 HEAD：`1e395a11a5479cd57e9769e3b988b65b18ee6be6`
- GitHub `origin/main`：`61a5fa6c408dbcb9c343dbc2ecd557ad99a6ba33`
- 1.5.7 发布提交：`d3755df7deb2456150c61ccb1944aa3982f7edf1`

本地 HEAD 比 `origin/main` 多 4 个后续 lint/test 提交，但本轮审核涉及的 canonical `SKILL.md`、references 和 OpenClaw `SKILL.md` 在 HEAD、`origin/main`、`v1.5.7` 之间没有差异。因此，以下 Markdown 判断同时适用于当前本地最新基线和 1.5.7 发布文本。

## 桌面报告证据复核

报告所列目录真实存在：

`C:\Users\admin\AppData\Local\Temp\opencode\cold-audit-1.5.7-writing\`

其中可核对：

- 8 个原始 prompt；
- MiniMax-M2、abab6.5s-chat 两个模型的 baseline/skill 共 32 份样稿；
- baseline system prompt；
- `v1.5.7 SKILL.md + task-route-cards.md` 的 skill system prompt；
- token 汇总、关键词评分脚本和评分 JSON。

不能完整复现的部分：目录未保留 API runner、原始请求与响应和完整请求参数。`temperature=0.3` 只见于桌面报告文字，无法由原始请求独立核验。因此可以复核样稿和输入文本，不能把生成过程描述为已独立复现。

### 原评分器的关键误差

1. MiniMax baseline T08 补写“作业质量达标、路面整洁度良好、分类收运体系运转正常、市容秩序良好”，评分器未覆盖这些表达，仍判 PASS。
2. T04 是只审不改任务，输出必须引用原文；评分器扫描整篇文本，会把被引用的“全面赋能”等原文词误算成生成违规。
3. MiniMax skill T07 主要问题是 Markdown，事实明显优于补写“运行基本稳定、达到预期效果”的 baseline，但两者都被等权计为 FAIL。
4. abab skill T01 补写“寻求解决方案、后续情况将及时通报”，评分器仍判 PASS。
5. T03 多份函件补写活动目的、场地评价或绑定错联系人，评分器覆盖不足。

因此，报告中的绝对 PASS 数和 `3/8 -> 2/8`、`3/8 -> 4/8` 不作为本轮裁决依据。

## P0—P3 裁决

| finding | 裁决 | 复核结论 |
| --- | --- | --- |
| P0-1 弱模型加载 skill 后通过率下降 | 暂缓，降为样本级警报 | 旧评分器不可靠；只能确认本次运行未证明稳定净收益。 |
| P0-2 入口过密、注意力税 | 接受为架构风险 | 长行、重复和 token 增量均可复核；“因此导致退化”的因果仍需重复 A/B。 |
| P0-3 评测数字误导 | 拒绝 P0 定性 | README 和 OpenClaw 已明确合成/stub 不代表真实业务胜率；可继续降低视觉权重，但不是当前发布可信度缺陷。 |
| P1-1 缺事实请示补政策、培训天数和课程 | 接受 | MiniMax skill T02 可直接复现；现有规则已禁止，属于执行失败。 |
| P1-2 待确认区出现半占位 | 接受 | `上级单位名称`、`XX市教育局` 与“只输出正文”同时冲突。 |
| P1-3 日期幻觉 | 接受为单样本 finding | T01 擅自补 2024 年；需重复运行确认频率，不能直接归因于长 prompt。 |
| P1-4 材料元叙述反转事实 | 接受 | “未提供经费数据”被写成“本月未涉及经费支出事项”。 |
| P1-5 口语审稿升级强判断 | 暂缓 | 部分建议确有过度具体化，但现有样本不足以定为稳定 P1。 |
| P2-1 本次 MiniMax skill 条件 4/8 出现 Markdown 残留 | 接受 | T01、T02、T03、T07 均有 `**`，T02 还有 `---`；不从一次运行外推总体频率。 |
| P2-2 OpenClaw 第 5 条不可扫描 | 接受 | 单行约 442 字，混合路由、缺项、输出模式和二次修改规则。 |
| P2-3 跨文件重复 | 接受窄义 finding | 事实边界、待确认、Markdown、行文关系和只输出正文在多文件重复承载；不接受据此立即新建单一事实边界源。 |
| P3-1 lint 能力边界不清 | 拒绝 | canonical、README 和总审资料已明确 lint 不覆盖事实与文种语义。 |
| P3-2 镜像易漂移 | 暂缓 | 风险存在，但当前镜像有同步工具和契约测试，本轮未复现漂移。 |
| P3-3 算力专项污染通用任务 | 暂缓 | 已有专项加载门禁，本轮没有针对性 A/B。 |

## 静态信息密度复核

下表按 LF 归一后的文本统计字符和行长，避免 CRLF 计数差异。

| 文件 | 字符 | 行数 | bullet | 不少于 160 字的行 | 最长行 |
| --- | ---: | ---: | ---: | ---: | ---: |
| canonical `SKILL.md` | 11,563 | 173 | 70 | 17 | 422 |
| `workflow.md` | 8,080 | 178 | 70 | 8 | 462 |
| `review-checklist.md` | 6,068 | 120 | 98 | 2 | 192 |
| `final-review-layers.md` | 2,535 | 73 | 45 | 0 | 152 |
| `genre-playbooks.md` | 4,663 | 108 | 66 | 4 | 417 |
| `task-route-cards.md` | 1,034 | 36 | 16 | 1 | 171 |
| OpenClaw `SKILL.md` | 5,104 | 149 | 38 | 5 | 442 |

有意义的近重复包括：

- 用户点名缺口只列点名项：canonical 与 `workflow.md` 双写；
- 字段式材料限制：canonical 与 `workflow.md` 双写；
- 待补事项不得升级成执行命令：canonical 与 `workflow.md` 双写；
- 稀疏通报骨架：canonical、`workflow.md`、`genre-playbooks.md` 三写。

静态证据支持“canonical 入口与 `workflow.md` 同时承载较多相同细则”，但不能证明重复必然使模型退化。重复也可能强化边界，必须通过删改后的真实 A/B 裁决。`final-review-layers.md`、`review-checklist.md` 和 `genre-playbooks.md` 已在文件头说明各自职责，本轮不把它们笼统判为职责不清。

## 对具体优化建议的判断

### 接受为候选方向

- OpenClaw 第 5 条只拆条、不改语义；同步修改生成模板和契约测试。
- 将“只输出正文 / 允许文后提示 / 点名缺项”整理为低分支决策表，但先做临时候选，不直接替换 canonical。
- 删除 `task-route-cards.md` 中“弱模型测试优先看……”这类评测旁白，改成直接交付规则。
- 将二次局部修改卡的联网表述明确为“默认不联网；用户要求核验或命中时效事实时再核验”。
- 真实评测采用事实硬门和 delivery 分栏，优先 pairwise 盲评，不再用关键词 PASS 总数代替人工判断。

上述候选均先在临时 prompt 包中做 A/B；即使字面语义不变，也不能因“只是拆条或改写”而免测。

### 拒绝直接实施

- 强制把 canonical 压到 6 KB 或 120 行；
- 把硬规则压成固定 8 条后将其余全部下沉；
- 新建单一 `fact-boundary.md` 并让其他文件只保留链接；
- 将办理要素改成“成稿 / 待确认 / 必须追问”三态；
- 给反 AI 模式预设统一硬风险等级；
- 删除段落—小节—全文三级复核；
- 把合成/stub 数字全部移出 README；
- 因静态重复直接大范围改 13 个 Markdown 文件。

### 暂缓

- 缩短 frontmatter description 的文种枚举；
- 把报告/情况说明拆成更多路由卡；
- 正式产品化 S/M/L 三档加载；
- 把 review checklist 大幅缩成链接目录；
- 调整 AI 算力专项在 description 和入口中的权重。

## 旧样稿双 verifier 独立盲评

本轮将桌面报告的 32 份旧样稿随机匿名化，两名独立 verifier 只看原 prompt 与匿名成稿，不读桌面报告、评分脚本和 baseline/skill 映射。匿名包保存在 `output/cold-audit-1.5.7-recheck-20260712/anonymous/`，该目录被 Git 忽略；verifier 任务名为 `/root/blind_judge_1`、`/root/blind_judge_2`。裁决时：

- 事实、数字、日期、主体动作对象绑定、拟议情态、文种和禁止项作为硬问题；
- Markdown、标题包装和普通形式问题单列 delivery，不与政策幻觉、日期错误等权；
- 同时报绝对 PASS/WARN/FAIL 和同题组内排序。

### MiniMax-M2 旧样稿的 pairwise 结果

| 结果 | 任务数 |
| --- | ---: |
| skill 更好 | 3 |
| 短 baseline 更好 | 2 |
| 两位 verifier 分歧或实质持平 | 3 |

skill 的明确优势出现在 T06 限字通知、T07 未决纪要和 T08 压缩报告；baseline 的明确优势出现在 T01 稀疏通报和 T02 缺要素请示；T03、T04、T05 未形成稳定胜负。T08 两边都 FAIL，但 skill 的单一事实反转仍轻于 baseline 的四处成效编造。

该结果推翻原评分器的“2/8 对 3/8”绝对胜负，但不证明 skill 已经稳定有效：两组仍有大量硬失败，且只有一次生成。

### abab6.5s-chat 旧样稿的 pairwise 结果

| 结果 | 任务数 |
| --- | ---: |
| skill 更好 | 5 |
| 短 baseline 更好 | 1 |
| 实质持平 | 2 |

该结果同样说明原关键词 PASS 数不能代表真实 pairwise 质量。本轮只把这些旧样稿用于复核桌面报告，不把它们写成新的模型测试。

### 匿名映射与逐题排序

完整匿名映射可由本地匿名包文件名与桌面原样稿核对。按原模型与同题条件汇总，两名 verifier 的共同或分歧结果如下：

| 模型/任务 | baseline 样稿 | skill 样稿 | pairwise 结论 |
| --- | --- | --- | --- |
| MiniMax T01 | sample_17 | sample_19 | baseline 更好 |
| MiniMax T02 | sample_14 | sample_09 | baseline 更好 |
| MiniMax T03 | sample_01 | sample_18 | verifier 分歧 |
| MiniMax T04 | sample_05 | sample_32 | verifier 分歧 |
| MiniMax T05 | sample_15 | sample_13 | 持平 |
| MiniMax T06 | sample_20 | sample_27 | skill 更好 |
| MiniMax T07 | sample_12 | sample_21 | skill 更好 |
| MiniMax T08 | sample_31 | sample_07 | skill 更好，双方均 FAIL |
| abab T01 | sample_04 | sample_25 | skill 更好 |
| abab T02 | sample_02 | sample_06 | skill 更好 |
| abab T03 | sample_11 | sample_24 | baseline 更好 |
| abab T04 | sample_08 | sample_03 | skill 更好 |
| abab T05 | sample_30 | sample_26 | 持平 |
| abab T06 | sample_10 | sample_22 | 持平 |
| abab T07 | sample_23 | sample_29 | skill 更好，双方均 FAIL |
| abab T08 | sample_28 | sample_16 | skill 更好，双方均有问题 |

## 本轮 Codex 三条件真实写作 sanity

用户明确要求不再使用 MiniMax。本轮没有生成新的 MiniMax 写稿样本。

本轮改用隔离 Codex subagent，三个 writer 上下文互相隔离：

- Short：不读仓库，只使用一段短系统提示；
- Full：读取当前 1.5.7 canonical，并实际读取 `task-route-cards.md`、`review-checklist.md`；
- Thin：不读仓库，只使用 8 条实验性短协议。

覆盖 3 个新 prompt：

1. 排查主体、OA 报送对象、联系人电话和截止时间绑定的 220 字通知；
2. 缺主送、落款、日期、政策、培训天数和课程的请示；
3. 含口语、二元句、建议试用和未形成采购决定的只审不改。

三组共 9 份样稿随机标为 X/Y/Z，由两名独立 Codex verifier 只看 prompt 和输出盲评。writer 任务名为 `/root/codex_writer_short`、`/root/codex_writer_full`、`/root/codex_writer_thin`；verifier 任务名为 `/root/codex_ab_judge_1`、`/root/codex_ab_judge_2`。subagent 运行时未暴露精确模型标签和 reasoning 档位，因此本报告不把结果伪标为 gpt-5.3-codex-spark、gpt-5.4 或 gpt-5.5。完整 prompt、协议、9 份输出、匿名映射和逐题结论见 `cold-audit-1.5.7-codex-ab-packet-20260712.md`。

### 双 verifier 独立盲评结果

首次 verifier 紧凑输入误漏 P3 原文标题，导致 Full 建议补明“模型服务”主语被误判为事实外扩。补回标题并在不揭示匿名映射的情况下重评后，两名 verifier 都判 P3 三组 PASS；修正后的有效总体结论是 Thin 一致居首，Short 与 Full 次序不稳定。

| 任务 | Thin | Short | Full |
| --- | --- | --- | --- |
| P1 动作关系通知 | PASS/WARN；仅“须”弱化为“请” | PASS/WARN；同左 | PASS/WARN；同左 |
| P2 缺要素请示 | PASS | WARN：补“提升应用能力”，且正文漏写市文化馆主体 | WARN：写成“培训对象为80人”，对象属性不完整 |
| P3 只审不改 | PASS | PASS，覆盖最完整 | PASS；“模型服务”由原文标题支持 |

结果支持继续测试“短协议 + 命中微卡”的方向，但不能直接改产品：只有 3 题、每条件 1 次，且没有精确模型标签。三名 writer 分别在一个共享条件上下文中连续完成 3 题，因此是 3 次 writer 运行产生 9 份输出，不是 9 次独立采样，可能存在顺序和共享上下文影响。

## 当前修改方向

### 现在

1. 不修改 canonical、reference、核心 workflow 和默认加载路径。
2. 不发布新版本，不把本轮 sanity 包装成发布通过。
3. 先把评测口径改为“事实硬门 + delivery 分栏 + pairwise 匿名盲评”。
4. 固定 `v1.5.7` 输入，不把当前 HEAD 的 opt-in lint 后续提交混进写稿条件。

### 下一轮

1. 使用能够记录精确 model ID 和 reasoning 档位的 Codex 环境；目标模型实际可选时，再分别承担弱模型主测和强模型回退哨兵，否则记录并使用环境实际提供的对应模型。
2. 测试 A/B/C 三臂：短 baseline、完整 1.5.7、8—12 条短协议加单个命中微卡。
3. 至少覆盖 6 题，每题每臂重复 2 次；重点覆盖稀疏通报、缺要素请示、未决纪要、只审不改、动作关系通知和“未提供数据”压缩。
4. 两名独立 verifier 盲评；事实、日期、主体关系或拟议情态出现一次新硬 FAIL 即停止候选。
5. 下一轮暂定工程门槛：短协议相对完整 1.5.7 至少胜 7/12、负不超过 2/12，且强模型哨兵无硬回退，才进入产品修改讨论；该门槛不是既有质量标准。
6. 候选还要与上一发行版和相关早期稳定基线分别做确定性消融和真实 A/B。通过后，先向用户说明现有流程、拟改流程、改变原因、基线差异和回退方式；用户明确同意前不得修改核心 workflow。

## 剩余风险

- 桌面报告的旧 MiniMax 调用缺少完整 runner 和原始请求，不能一键复现。
- 本轮 Codex subagent 不暴露精确模型标签和 reasoning 档位，只能作为方向 sanity。
- 本轮 Codex 三条件测试是每个 writer 在同一条件上下文中连续完成 3 题，不是 9 次独立采样。
- 旧样稿的双 verifier 匿名盲评仍是对单次生成的事后裁决，不能代替重复采样。
- 静态长行和重复统计不能单独证明因果。
- 当前 HEAD 的 opt-in delivery lint 只检测不改写，与本轮 Markdown 信息架构判断分开处理。

## 本轮处理

- 未修改产品 `SKILL.md`、references、lint、测试逻辑、版本号或发布元数据。
- 仅新增本复核报告和 Codex A/B 原始包两份证据文件。
- 未发布 GitHub、ClawHub 或 SkillHub。

## 工程验证

- `python -B -m unittest discover -s tests -v`：142/142 通过。
- `python -B C:\Users\admin\.codex\skills\.system\skill-creator\scripts\quick_validate.py chinese-official-writing`：通过。
- Promptfoo smoke 在沙箱内三次均因 Node 无法访问实际存在的 Python 而产生 20 个启动错误，不计为内容失败；改用 Codex bundled Python 并在沙箱外重跑后 20/20 通过，0 error，judge consistency 1.0。
- `git diff --check`：通过。
