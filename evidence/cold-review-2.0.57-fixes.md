# 冷审 2.0.57 问题复现与修复证据

日期：2026-11-12。评审来源：冷审线程 `01a1ceb3-7868-7e32-b829-b52b34692f7e`（对象为线上 2.0.57）。

- 固定基线：`b2fb1682f1f7a968f2e9c5a806acd29a475d333d`（origin/main，线上 2.0.57），只读审计工作树 `C:\Users\2\.codex\worktrees\chinese-official-writing-online-2.0.57-audit`。
- 修复分支：`codex/cold-review-2.0.57-fixes`，工作树 `C:\Users\2\.codex\worktrees\cow-fix-2.0.57`，自基线检出。
- 复现与验证脚本目录：`C:\Users\2\Documents\chinese-official-writing\output\cold-review-2.0.57-repro`（下称 scratch）。
- 环境：Windows，PowerShell 与 cmd.exe 均可用；`python`=3.14.5，`python3` 为 Microsoft Store 占位 stub；rg 可用。

修复范围：冷审确认的 P1 一项、P2 三项、P3 一项。冷审列为设计风险（工作总结约 400 字定量、通知叶子仅进展类出口、anti-AI 加载不一致）按“先核实、非确认错误”处理，本轮不改。任务路由、reference 加载条件、复核顺序、输出模式、修改次数、回退方式与发布链不变；本轮只新增不落盘分支、把一次补搜限制限定于代理自主检索、替换字数统计命令。

## 一、问题复现（均在固定基线上执行）

### P1 指定替换路径未继承“禁止落盘”例外（确认）

基线规则原文：

- `SKILL.md:14`：例外只有“用户不要工具时人工核对”。
- `references/targeted-checks.md` 第 2–4 步：强制“存原稿、写计划、生成新文件”。
- `references/writing-rules.md:19`：“含密级标识、个人敏感信息或用户要求不落盘时，不保存材料和回复临时文件，直接对照材料核对交付。”

复现：按 targeted-checks.md 文档化流程处理含身份证号的材料（scratch `p1-original.txt`、`p1-plan.json`、`p1-new.txt`），`edit_scope.py` 实际创建 3 个文件；`edit_scope.py --help` 确认脚本没有 stdin/内存模式。即敏感材料在指定替换路径下必然落盘，与 writing-rules.md:19 直接冲突。

### P2a 严格国标与模板优先冲突（确认）

- `references/format-gbt9704.md:3`（页首）：优先级为“本轮明确指令、用户模板、本页默认样式”，模板与本轮明确的严格国标要求冲突时按国标调整。
- 同页 `:38`：“页码：有用户模板时按模板”；`:87`：“单位模板另定版记样式时按模板处理”；`references/genre-playbook-institution-rules.md:35`：“按用户模板优先处理纸张、页边距……版记”。三处均无条件模板优先，与页首优先级矛盾。

### P2b 一次补搜限制阻断用户指定的多来源核验（确认）

- `references/external-research.md:14`：每项用途只允许一次补搜，“一次后无论是否补齐，都停止该项检索”，没有用户指定核验范围的例外。
- `references/genre-playbook-news-message.md:16`：支持用户明确要求的主张—来源矩阵（每个主张多个来源）。用户要求“每个声明至少两个公开来源交叉核验”时，两条规则冲突。

### P2c 字数统计命令在 Windows cmd 下失败（确认）

基线 `SKILL.md:22` 命令为 `python3 -c 'import sys; print(len("".join(sys.stdin.read().split())))'`。scratch 实测：

- `count-cmd.bat`（cmd.exe + python + 单引号一行式）：`SyntaxError: unterminated string literal`（cmd 不把单引号当字符串定界符）。
- `count-cmd3.bat`（cmd.exe + python3）：退出码 9009，触发 Microsoft Store 占位 stub。
- 同一行式在 PowerShell + python 下输出 6（"abc def"），仅在类 POSIX shell 语义下可用。

### P3 脚本注释含未定义维护术语（确认）

`scripts/draft_length.py:2` “no host lifecycle required”、`:33` “review-gate counting convention”。rg 全包检索：这两个术语在 2.0.57 公开包内仅这 2 处，无定义，属于 1.5.x 维护层残留。

## 二、修复内容（6 个文件，均在技能包内，包文件数保持 94）

1. `SKILL.md:14`：指定替换分支增加前置门——用户要求不落盘、材料含个人敏感信息或密级标识、写入受限时不创建任何文件，改用内存内或人工替换。
2. `SKILL.md:22`：字数命令改为 `python -X utf8 "<Skill目录>/scripts/draft_length.py" --delivery-mode review-only -`；脚本按已读 SKILL.md 所在目录定位，解释器按宿主可用的 Python 3 选择；段落其余内容不变。
3. `references/targeted-checks.md`：页首新增“不落盘前置门”段落；精确替换节命中前置门时跳过存原稿、写计划、生成新文件各步；第 5 步改为“读取新稿或内存内改后全文”。
4. `references/format-gbt9704.md:38/:87`：页码与版记的模板优先均加上“本轮未要求严格国标”条件；冲突时按页首优先级处理。
5. `references/genre-playbook-institution-rules.md:35`：无条件“用户模板优先”改为“按该页页首优先级处理”。
6. `references/external-research.md:14`：插入“一次补搜限制只约束代理自主检索；用户明确指定来源数量、交叉核验或核验深度时，按用户范围检索和核验，逐条记录实际打开状态”。
7. `scripts/draft_length.py`：两处注释改为自含描述（`Measure draft length before substantive review.` / `Count non-whitespace characters or CJK ideographs as a pure function.`），无行为改动。

## 三、确定性验证（实际运行）

scratch `verify_fix.py`（对修复工作树运行）：

- 计数等价：5 个样本（ascii、cjk、全角空格、tab/换行、含文后提示）旧内联公式与新命令 review-only 结果逐一相等（6/17/3/4/33），ALL_EQUAL。
- 模式必要性：含文后提示样本 review-only=33、默认 draft-body=21，证明必须显式带 `--delivery-mode review-only`。
- cjk 模式正常；4 个脚本 AST 解析通过；SKILL.md 及 references 引用的脚本/文件链接无缺失；全包无 “host lifecycle”“review-gate” 残留。

新命令跨 shell 实测（scratch `count-fixed.bat` + `count-sample.txt`，中文 UTF-8 样本）：cmd.exe=38，PowerShell=38，旧公式=38，三者一致。

`edit_scope.py` 行为回归（scratch p2-* 样本）：generate 退出码 0；`--candidate` 完全一致退出码 0；不一致退出码 1；原稿绑定哈希被篡改退出码 2。脚本行为未变。

真实写稿输出的确定性复核（scratch `check_ab.py`、`outputs.json`）：

- T1 两版交付与“原材料仅 20 日→25 日”的期望全文逐字一致（VERBATIM_OK）。
- T3 正文字数（修复版 draft_length.py，draft-body）：

| 口径 | T3-cand | T3-base |
|---|---|---|
| 仅消息段落，非空白字符（两写手各自采用） | 297（范围内） | 207（范围内） |
| 标题+段落，非空白字符 | 322（超上限 22） | 232（范围内） |
| 标题+段落，CJK 汉字 | 220（范围内） | 141（低于下限 59） |

用户要求“200—300字”未指明是否含标题、是否只数汉字；skill 默认口径为非空白字符。该歧义已连同实测数据交给盲审 verifier 按口径判定。

## 四、真实写稿 A/B（短样本 sanity，3 题 × 2 版）

设置：6 个 writer 子代理（继承同一父模型），baseline 读只读审计工作树（b2fb168），candidate 读修复工作树；writer 按各自 SKILL.md 指引读取 references，不得修改工作树；最终消息分【交付】（对用户的完整回复）与【过程记录】（评测用命令与文件清单）。盲审标签：T1 A=cand/B=base；T2 A=base/B=cand；T3 A=cand/B=base。独立 verifier 子代理只接收原始用户请求与【交付】，不知映射，另做链接抽查；【过程记录】由主审单独核对文件创建。

题目：T1 含身份证号的通知指定日期替换，要求不落盘、其余逐字保留；T2 《办公区节能管理办法》严格 GB/T 9704-2012 排版方案，单位模板三项冲突，只要方案不生成文件；T3 新能源汽车消息，两个声明各≥2 公开来源交叉核验，主张—来源矩阵+200—300字正文。

过程核对：6 份【过程记录】均声明无文件创建或修改；两工作树 git status 确认——修复树仅 6 个预期改动文件，审计树无改动（另有脚本运行产生的未跟踪 `__pycache__`，提交前清理）。

### 盲审结论（独立 verifier，只读原始请求+【交付】，不知映射）

- T1：A(cand)=PASS，B(base)=PASS，难分。两版交付逐字相同，仅目标日期变化，身份证号、落款、成文日期逐字保留，无添加。【交付】栏目标记为评测包装要求，不属于对用户交付本身。
- T2：A(base)=PASS（轻微 WARN），B(cand)=WARN，A 窄胜（条件性）。两版都正确执行“本轮严格国标优先于模板”，都列出冲突调整项——P2a 修复的目标行为在两版均成立。候选版 WARN：写“普通页边距、不勾选对称页边距”，在双面印刷左侧装订下偶数页订口会为 26 mm（国标订口 28±1 mm），且未明确双面印刷；基线版用对称页边距（内 28/外 26）更稳。基线版 WARN：“版心下边缘下方 7 mm”表述精度不足（应为“上距 7 mm”）、把 ±1 mm 公差写成四个方向均由标准直接规定（标准直接规定天头 37±1、订口 28±1）、对模板图层作推测、调整项清单过度包含。候选版胜在“上距 7 mm”精确表述与只列 3 项实际冲突调整的清单。
- T3：A(cand)=PASS（篇幅 WARN），B(base)=PASS（篇幅 WARN），难分。两版均每个声明≥2 公开来源、矩阵字段齐全、消息文种正确、无编造数字或来源。篇幅按主口径（消息段落非空白字符）均合格；另两种口径各有越界项（见上表），均记 WARN 不单判 FAIL。
- 链接抽查：verifier 实际打开两侧全部 5 个唯一链接（人民日报、新华网、中国能源报、工信部、国家统计局 PDF 附件），均 HTTP 200 且内容支持对应主张；统计局 PDF 为 15 页、第 10 页载 1288.8/1286.6 万辆与 40.9% 及纯电/插混分项，内存解析成功，不判为编造。
- 总体：未发现某一侧独有的事实或指令硬回退。

### 主审交叉验证

1. T1 逐字一致已用脚本独立复验（check_ab.py，两版 VERBATIM_OK），不依赖 verifier 目测。
2. T3 字数已用修复版 draft_length.py 独立复测（上表），verifier 收到的是同一组实测数据。
3. T2 候选版“对称页边距”问题：rg 确认两版 format-gbt9704.md 均无“双面/对称页边距”表述（仅附件条目含“装订”），本轮改动的优先级条件句不涉及页边距设置指引；该差异是写手层面的单样本实现选择，不能归因于本轮规则改动，按普通场景单次观察登记，不作为本轮修复阻断。技能页对双面印刷与对称页边距的沉默是潜在文档缺口，如需补充须另立候选并单独 A/B，不混入本轮。
4. 过程核对：6 份过程记录均无文件创建；两工作树 git status 与之一致。

结论：P1/P2a/P2b 的目标行为在候选版运行中均成立（不落盘、严格国标优先、用户指定多来源核验），P2c/P3 由确定性验证覆盖；无候选版独有的事实、指令或输出模式硬回退；T2 存在一项与改动文本无关的条件性版式观察，已登记。

## 五、边界与未完成

- 2.0.57 公开树没有单元测试套件；本轮验证为自定义确定性脚本+短样本 A/B，属 sanity 级，不是发布级矩阵，未跑长文、多附件、跨模型矩阵。
- T2 按用户要求只交方案，未生成 DOCX，未做渲染核对。
- T3 来源核验以写手实际打开+verifier 抽查为限，未逐条穷尽复核。
- 设计风险三项未改（见开头）。
- 本地仓库 main（2d0edb9，1.5.20 线）与 origin/main 分叉（ahead 300 / behind 729），本轮未动本地 main；修复分支基于 origin/main 基线。
- 本地已安装插件 `C:\Users\2\plugins\chinese-official-writing`（84a5cec，94 文件 SHA-256 清单）未同步，等待批准。
- 未 push、未发布、未向任何商店提交。
