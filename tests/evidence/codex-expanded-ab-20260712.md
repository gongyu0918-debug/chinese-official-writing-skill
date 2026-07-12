# 1.5.7 Codex 扩大三条件真实写作 A/B

## 结论

本轮在当前最新提交 `3427d658b4f52ab71c10615322bde4b102ec04ce` 上扩大真实写作测试。该提交包含 1.5.7 后的本地 lint/test 和冷审证据；参与写稿的 canonical `SKILL.md`、references 与 `v1.5.7` 发布提交 `d3755df7deb2456150c61ccb1944aa3982f7edf1` 一致。

用户询问的旧任务 ID `019f08a7-0105-7ae3-b1fc-7126123987a6` 未用于本轮测试。它关联历史 1.5.2 发布/live 核验和图标目录，不是当前 commit。

扩大测试共生成 36 份 Codex 样稿：6 题 × 3 条件 × 2 次独立 writer。两名独立 verifier 在统一口径后重评，另加一名匿名仲裁。多数票结果为：

- Thin 进入胜者位 5 组；
- Short 进入胜者位 4 组；
- Full 进入胜者位 4 组；
- 其中 1 组为 Short/Thin 并列。

Thin 只呈现轻微方向性优势，不满足此前暂定的 `至少胜 7/12、负不超过 2/12` 工程门槛；Full、Short、Thin 均未出现 hard FAIL，也没有任一条件独有且达到三次的同类功能失败。因此本轮不修改 canonical、reference、核心 workflow 或默认加载路径。

## 模型和可复现边界

- 按用户要求，本轮不使用 MiniMax。
- writer 和 verifier 均使用隔离 Codex subagent。
- 当前 subagent 运行时不暴露精确 model ID 和 reasoning 档位，因此不把结果伪标为 gpt-5.3-codex-spark、gpt-5.4 或 gpt-5.5。
- 每个 writer 在一个条件上下文内连续完成 6 题；两轮由不同 writer 独立执行，并将第二轮任务顺序反转。
- 这相当于 6 次独立 writer 运行生成 36 份输出，不是 36 次完全独立采样。

## 三个条件

### Short

只使用短系统提示：文种和行文关系正确、不编造事实、正式正文不用 Markdown、直接完成用户要求；不读仓库或 skill。

writer：

- `/root/expand_short_r1`
- `/root/expand_short_r2`

### Full

固定当前 HEAD，读取 `.agents/skills/chinese-official-writing/SKILL.md`，再按当前路由实际读取：

- `references/task-route-cards.md`
- `references/genre-playbooks.md`
- `references/genre-checklist.md`
- `references/review-checklist.md`

writer：

- `/root/expand_full_r1`
- `/root/expand_full_r2`

### Thin

只使用 8 条短协议和命中微卡：事实保真、主体动作对象绑定、拟议情态、文种关系、只输出正文、缺项不编造、纯文本交付、交付前四项检查；按稀疏材料、未决纪要、缺要素请示、只审不改、动作关系通知和压缩未知数据给一条微卡。

writer：

- `/root/expand_thin_r1`
- `/root/expand_thin_r2`

## 任务覆盖

1. 稀疏接口抽查通报：不补会议内容、责任部门、处置和后续安排。
2. 缺主送、课程、政策、落款和日期的请示。
3. 建议继续试用、范围待确认、费用待复核的未决纪要。
4. 含口语、二元句、费用关注和采购未决口径的只审不改。
5. 锁定排查主体、OA 渠道、接收部门、联系人和截止时间的限字通知。
6. 保留主体、时间、数字且不得把“未提供经费数据”写成无支出的压缩报告。

完整匿名输入、36 份输出和首次 verifier rubric 见 `codex-expanded-ab-packet-20260712.md`。

## 匿名映射

- 第一轮：X = Full，Y = Short，Z = Thin。
- 第二轮：X = Thin，Y = Full，Z = Short。

两轮使用不同映射并反转任务顺序，避免 verifier 从固定标签或题序猜测条件。

## verifier 与口径纠正

verifier：

- `/root/expand_judge_1`
- `/root/expand_judge_2`
- 仲裁 `/root/expand_judge_3`

前两名 verifier 初评对“只输出正文”理解不一致：一名把标题视为正式稿必要部分，另一名把标题、主送和纪要字段视为正文外内容，导致总体胜负完全相反。统一口径后重新盲评：

1. “只输出正文”指不附写作说明、自证或待确认问卷；标题、主送和纪要基本字段属于正式稿，可以保留。
2. E6 只要求保留主体、时间和数字；“未提供经费数据”可以省略。把该句写进报告正文记为 delivery WARN，改成“无支出”才是 hard FAIL。
3. E1 把省略主语直接承接为已给的数据管理处最多记 WARN，不判 FAIL。

仲裁 verifier 使用相同口径，只看匿名包，不读取仓库和条件映射。

## 三名 verifier 的条件结果

按各自逐题 winner 映射回真实条件：

| verifier | Full 进入胜者位 | Short 进入胜者位 | Thin 进入胜者位 | 总体倾向 |
| --- | ---: | ---: | ---: | --- |
| judge 1 | 3 | 4 | 7 | Thin |
| judge 2 | 8 | 6 | 5 | Full |
| judge 3 | 5 | 2 | 6 | Thin |

这组分歧说明总体胜负受采样和审稿偏好影响较大，不能只引用某一名 verifier 的总票数。

### 12 组多数票

计票规则：每名 verifier 每组的独占 winner 记 1 票；并列第一时，并列条件各记 1 票，不拆分为小数。三名 verifier 的票按真实条件汇总，最高票条件为该组多数 winner；同票最高则保留并列。匿名映射为第一轮 `X=Full、Y=Short、Z=Thin`，第二轮 `X=Thin、Y=Full、Z=Short`。

| 轮次/任务 | judge 1 匿名 winner | judge 2 匿名 winner | judge 3 匿名 winner | 映射后票数（Full / Short / Thin） | 多数 winner |
| --- | --- | --- | --- | --- | --- |
| R1-E1 | Z | Y = Z | X | 1 / 1 / 2 | Thin |
| R1-E2 | Y = Z | Y = Z | Y = Z | 0 / 3 / 3 | Short = Thin |
| R1-E3 | Z | X = Y = Z | Z | 1 / 1 / 3 | Thin |
| R1-E4 | Y | Y | Z | 0 / 2 / 1 | Short |
| R1-E5 | X = Z | X = Z | Z | 2 / 0 / 3 | Thin |
| R1-E6 | Z | Z | Z | 0 / 0 / 3 | Thin |
| R2-E1 | Z | Y = Z | X | 1 / 2 / 1 | Short |
| R2-E2 | X | Y | Y | 2 / 0 / 1 | Full |
| R2-E3 | X | Y | Y | 2 / 0 / 1 | Full |
| R2-E4 | Y | Y | Y | 3 / 0 / 0 | Full |
| R2-E5 | Z | Y = Z | Z | 1 / 3 / 0 | Short |
| R2-E6 | Y | Y | Y | 3 / 0 / 0 | Full |

逐行多数 winner 汇总如下：

| 任务 | 第一轮多数 winner | 第二轮多数 winner |
| --- | --- | --- |
| E1 稀疏通报 | Thin | Short |
| E2 缺要素请示 | Short = Thin | Full |
| E3 未决纪要 | Thin | Full |
| E4 只审不改 | Short | Full |
| E5 动作关系通知 | Thin | Short |
| E6 压缩报告 | Thin | Full |

多数票呈明显轮次反转：第一轮 Thin 较优，第二轮 Full 较优；Short 在通知和第一轮审稿中有优势。不能把这一结果解释成稳定的“上下文越短越好”或“完整 skill 更好”。

## 共性问题

### 达到三次

4 份 E6 稿把“经费数据未提供”写进工作报告正文：

- Short 第一轮、第二轮；
- Full 第一轮；
- Thin 第二轮。

该句没有把未知事实改成无支出，不是 hard FAIL；但它属于材料说明进入正文的 delivery/材料旁白倾向。Thin 第一轮和 Full 第二轮能直接省略，说明问题没有稳定绑定某一条件。

### 未达到三次或不稳定

- “须”弱化为“请”出现 2 次，分别来自 Short 第一轮和 Thin 第二轮。
- E1 明确补出内部协调会组织主体出现 2 次，分别来自 Full 第一轮和 Thin 第二轮。
- Full 第一轮请示遗漏“市图书馆”申请主体 1 次。
- 请示请求事项写得偏隐含在多个条件出现，但未造成主体、金额、经费渠道或请批语错误；是否需要明确写“申请批准”与事实边界存在取舍，不作单例补丁。

## 修改判断

1. 不接受“Thin 已证明优于 Full”。多数票只领先 1 组，且两轮方向反转。
2. 不接受依据本轮直接压缩 `SKILL.md`、删除入口硬边界或改默认 reference 路由。
3. 接受 E6 材料说明倾向作为后续观察项，但它未达到条件内三次共性，暂不改 prompt。
4. 保留 Thin 作为临时实验包，不进入发行内容。
5. 下一轮若能选择并记录精确模型，优先用较弱 Codex 模型低思考重复本组任务，并用强模型作回退哨兵；否则继续按实际可见模型如实记录。

## 本轮处理

- 未修改产品 `SKILL.md`、references、lint、测试逻辑、版本号或发布元数据。
- 仅新增扩大测试报告和匿名原始包。
- 未发布 GitHub、ClawHub 或 SkillHub。

## 工程验证

- `python -B -m unittest discover -s tests`：142 tests，OK。
- `python -B C:\Users\admin\.codex\skills\.system\skill-creator\scripts\quick_validate.py chinese-official-writing`：`Skill is valid!`。
- `C:\Users\admin\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe evals\official-writing\run_eval.py --suite smoke --judge-batch-size 2`：20/20 PASS，0 failed，0 errors，judge consistency 1.0。
- `git diff --check`：通过。
- 独立只读终审复算三名 verifier 的逐组矩阵、条件总票、12 组多数 winner 和共性问题计数，未发现阻断错误。
