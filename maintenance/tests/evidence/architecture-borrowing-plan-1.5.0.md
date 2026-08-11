# 1.5.0 社区 Skill 架构借鉴与最小优化方案

日期：2026-07-04
基线：`chinese-official-writing@1.4.15`，本地 HEAD `9c218ea849449a9aced6ad101e2a05fc21b233e0`
范围：只做研究、复现和方案记录；本轮不修改 `SKILL.md`、`references/`、脚本或发布元数据。

## 本轮结论

当前技能不宜直接改成“每个文种一个文件”的大拆分。更稳妥的 1.5.0 方向是保留现有“任务行为/阶段路由”主骨架，再新增一个轻量“文种/专项 playbook 层”，把会议纪要、请示/报告、函/复函、通知/通告/公告、公示通报、讲话致辞、工作总结/工作要点/周报、调研/研究/可研/建设方案、采购公告/审查材料、AI 算力专项等高频场景收束到同一套短入口里。

这样做的目的不是照搬社区模板，而是把当前分散在 common reference 中的文种和专项知识整理成“先判文种/专项，再读取对应 playbook，再进入总审”的渐进读取路径，减少 AI 算力、采购等专项内容在通用文件中的表面占比，同时保留当前技能在事实边界、用户模板、只审不改、非阻断缺项、低 AI 味软审稿上的优势。

## 现状复核

### 版本与发布面

- `git fetch` 后本地已快进到 `origin/main` / `v1.4.15`：`9c218ea849449a9aced6ad101e2a05fc21b233e0`。
- `clawhub inspect chinese-official-writing --json` 首次在代理环境下 `fetch failed`；清空 `HTTP_PROXY`、`HTTPS_PROXY`、`ALL_PROXY` 及小写变量后复现成功。
- 本轮命令记录称：CLI inspect 返回 `latestVersion.version=1.4.15`、moderation `clean`；网页展示与 inspect 结果不一致。因本报告未随附完整 inspect JSON 或网页快照，精确 stats、网页展示版本和 tag 异常只作为下轮发布前复核项，不作为本报告的独立证据结论。

### 已跑验证

- 基线消融：
  `python .\tools\run_real_prompt_ablation.py --baseline-root .\output\release-baselines\pre-1.4.15-b2fc5ba --baseline-label baseline-pre-1.4.15 --current-root . --out .\output\real-prompt-vs-pre-1.4.15-to-1.4.15`
  - baseline-pre-1.4.15：71 例，68 过，3 失败。
  - current：71 例，71 过，0 失败。
  - baseline 失败项为 P058 学校奖学金申请、P061 论文降 AI 味排除、P063 个人求职申请信排除。当前均通过。
- 全量单测：
  `python -m unittest discover -s tests -v`
  - 本轮终端执行通过；未在本报告中保存完整原始日志，最终提交报告另行记录。
- 真实样文回归：
  `python .\tools\run_real_article_eval.py --out output\real-article-1.4.15-codex-review`
  - skill 组 10/10 样本关键要素覆盖，缺失 0/61，反 AI 风险 0。
  - 同时出现 9/10 个匿名占位词风险样本。该工具会把 `主送机关`、`发文机关` 等匿名标签计入风险，因此只能作为回归信号；下一轮真实改稿或发布前必须引入独立 writer/verifier 判断。
- `git diff --check`：本轮终端执行通过；最终提交前会重新运行。
- `npm run eval:official-writing:smoke`：本轮未形成通过结论。终端记录显示问题集中在 promptfoo Python provider/本地 Python 路径环境，故只记录为评测环境阻塞，不写作 skill 逻辑通过。

## 当前 reference 架构

当前 canonical 文件：

| 文件 | 作用 |
| --- | --- |
| `SKILL.md` | 总入口、硬边界、任务模式、reference 路由 |
| `workflow.md` | 起草/改稿/复核/排版交付和多材料处理 |
| `genre-routing.md` | 文种与行文方向判断 |
| `handling-elements.md` | 主体、对象、事项、依据、期限、联系人等办理要素 |
| `argument-chains.md` | 请示、报告、通知、方案、可研、技术材料论证链 |
| `genre-checklist.md` | 文种细查清单 |
| `review-checklist.md` / `final-review-layers.md` | 审稿和定稿复核 |
| `official-style.md` / `anti-ai-patterns.md` | 正式语气、低 AI 味软审稿 |
| `format-gbt9704.md` | Word/GB/T 9704 交付前核对 |
| `ai-compute-docs.md` | AI 算力、GPU/服务器租赁、模型服务等专项 |

这个结构的优点是通用边界集中、渐进读取清楚；弱点是“文种/专项 playbook”不够显式，导致一些场景知识散落在 `SKILL.md`、`genre-routing.md`、`handling-elements.md`、`argument-chains.md`、`genre-checklist.md`、`review-checklist.md`、`anti-ai-patterns.md` 中。

本轮检索确认：AI 算力、采购、租赁、GPU、Token、SLA 等词主要集中在 `ai-compute-docs.md`，但 `SKILL.md` 和多个 common reference 也有重复出现。合理的边界是：`SKILL.md` 保留触发和路由，common reference 只保留一两句通用提醒，具体业务骨架统一落到专项 reference，避免用户明明要写普通通知/报告时被专项语境牵引。

## 社区 Skill 检索范围

本轮不是只看用户举例的三个页面，而是把 SkillHub 公文、会议纪要、报告、周报、行业研究、格式化、官方文档写作等相关包一并抽样。已下载或展开的本地包在 `output/skillhub-packages/`，只用于研究，不进入发行包。

检索和下载入口包括：

- SkillHub 公文检索：`https://api.skillhub.cn/api/skills?page=1&pageSize=30&keyword=公文`
- SkillHub 会议纪要检索：`https://api.skillhub.cn/api/skills?page=1&pageSize=30&keyword=会议纪要`
- SkillHub 报告检索：`https://api.skillhub.cn/api/skills?page=1&pageSize=30&keyword=报告`
- 用户给出的页面：`official-document-skill`、`meeting-minutes-drafter`、`govwriting`
- 下载接口：`https://api.skillhub.cn/api/v1/download?slug=<slug>`
- 当前 ClawHub 页面：`https://clawhub.ai/gongyu0918-debug/skills/chinese-official-writing`
- GitHub 仓库：`https://github.com/gongyu0918-debug/chinese-official-writing-skill`

## 候选 Skill 分组

| 类型 | 候选 | 观察 | 可最小借鉴 | 不采纳 |
| --- | --- | --- | --- | --- |
| 泛公文写作 | `official-document-skill` | 单 SKILL 承载文种表、模板、反 AI 标准和评分。易用，但上下文重。 | 文种判断表、输出前补充信息提示、fact density 思路。 | 不复制模板正文、0-100 评分、过重单文件。 |
| 泛公文写作 | `govwriting` | 多章节 handbook 式，覆盖面广。 | “章节化资料库”作为反例和分层参考。 | 不导入百科式长文档，不把 reference 变成教程书。 |
| 泛公文+搜索+Word | `dknowc-official-doc-writer-skillhub` | 有任务路由、标准库、搜索策略和 Word 管线，依赖 API key。 | “任务复杂度路由 + 文种标准库 + 明确搜索边界”。 | 不默认联网/API，不默认生成 Word，不阻断无 key 普通写稿。 |
| 公文生成+Word | `official-doc-writer` | 有交互式要素收集、脚本、字体和 Word 生成。 | 写正文与 Word 交付分层、正式要素收集。 | 不引入字体安装、COM/LibreOffice、交互式长问卷。 |
| 公文脚本包装 | `official-doc` | notice/request/report/reply 等脚本入口。 | 轻量命令化分类可作测试灵感。 | 不把写作质量交给固定 shell 模板。 |
| 公文写作+政策搜索 | `official-document-writer-skill` | 强调政策检索、Word/PDF 交付。 | 来源清单和依据核验提示。 | 不默认外搜，不采纳可疑标准版本表述，不默认 PDF/Word。 |
| 公文格式 | `gongwenformat-pro` | 专注格式/版式/Word。 | 格式专项与写作专项解耦；格式只在用户要求时触发。 | 不把本技能改成排版引擎。 |
| 会议纪要专项 | `meeting-minutes-drafter` | 专项 workflow，强调输入清理、会议类型、行动项和来源。 | 会议类型判断、议题/决定/任务/责任/期限结构。 | 不默认标注发言来源，不默认读取本地会议目录。 |
| 会议纪要专项 | `meeting-minutes-organizer`、`auto-meeting-minutes` | 单文件、固定输出结构。 | 紧凑会议纪要骨架。 | 不强行输出固定模板，不覆盖用户已有纪要格式。 |
| 会议/访谈笔记 | `meeting-note` | 明确适用/不适用，按决策/讨论/访谈等分流。 | “适用/不适用 + 会议类型矩阵 + 行动项复核”。 | 不把普通公文变成知识管理笔记。 |
| 钉钉/飞书会议 | `dingtalk-minutes` | 平台化会议记录整理，带固定输入/归档倾向。 | 对接来源材料时保留时间、议题、决议、待办的顺序。 | 不引入平台 API、默认扫目录、归档副作用。 |
| 行业研究报告 | `industry-research-analyst` | 六维研究框架，reference 分层清楚。 | 长报告 playbook 的“定义、链条、竞争、驱动、风险、建议”结构。 | 不把公文报告写成投研报告。 |
| 研究报告 | `research-report-skill` | 单文件研究报告框架。 | 背景、现状、问题、原因、建议的轻量结构。 | 不加入市场预测和投资建议默认项。 |
| 周报/工作报告 | `weekly-work-report` | 周报结构短而明确。 | 工作总结/周报可复用“已完成、推进中、问题、下步”骨架。 | 不把所有总结改成周报格式。 |

补充高下载但未下载展开的相邻技能：以下名称来自检索列表或早期记录，本轮不对其内部结构作判断，只作为下轮可选复核对象。

- `doc-format-gw`、`gov-document-typesetting`、`word-cn-format`：疑似文档格式/排版相邻项；只有下载展开并确认边界后，才能作为格式专项参考。
- `tencent-meeting-skill`、`kdocs-skill`、`feishu-weekly-report`、`daily-report-skill`：可能涉及平台/API 或办公套件能力；本轮不采纳为写作规则来源。
- AI 检测/查重类技能已用于前几轮 verifier 思路，本轮只作为审稿外部参考，不把检测器内置到写作 skill。

## 可借鉴的共性结构

1. **专项 playbook 而不是模板正文**
   好的专项 skill 通常不只给一个模板，而是说明适用场景、输入要素、输出骨架、风险检查。当前技能可借鉴这种组织方式，但不能复制模板句。

2. **适用/不适用边界前置**
   `meeting-note`、会议纪要类技能的边界较清楚。当前技能可在 playbook 中写明“会议纪要不等于新闻稿、汇报材料、会议记录全文逐字稿”，也可给报告/请示/函的错位边界。

3. **文种/专项先路由，通用审稿后兜底**
   社区专项 skill 的优势在窄场景一致性。当前技能可保持 common hard boundary，再通过 playbook 给会议纪要、报告、请示、采购公告等高频场景更快进入正确骨架。

4. **格式与正文解耦**
   格式类 skill 的优势在工具链，但这不应进入默认写作流程。当前技能应继续只做 Word/GB/T 要素核对，并把真实排版交给文档工具或用户指定工具。

5. **搜索/API 显式边界**
   依赖搜索或 API 的社区 skill 往往能补政策依据，但也最容易污染事实边界。当前技能只可借鉴“来源清单”和“无法核验则列待确认”，不改默认不外搜。

## 不应借鉴的坏东西

- 不复制社区技能的大段 prompt、固定模板、正文句式、正则或脚本。
- 不新增硬门禁、硬清洗、固定替换表、0-100 评分或自动查重/AI 检测结论。
- 不默认联网、默认搜索单位官网、默认查政策、默认调用 API。
- 不默认生成 Word/PDF，不引入字体、COM、LibreOffice、WPS、平台会议 API 或本地目录扫描。
- 不把所有文种拆成大量独立文件作为第一步。这样会增加同步和镜像漂移风险，并可能让通用硬边界分散。
- 不把普通采购公告、费用申请、办公设备申请都吸收到 AI 算力语境里。
- 不把“会议纪要”写成会议新闻稿、个人笔记或行动项工具；用户已有会议纪要模板时仍优先保留。

## 1.5.0 推荐最小方案

### 方案 A：推荐先做

新增一个一级 reference：

`references/genre-playbooks.md`

建议结构：

```text
# 文种与专项 Playbook

## 使用方式
- 先读 SKILL.md 和 workflow/genre-routing。
- 只有命中具体文种或专项时读取本文件对应小节。
- 每个小节只给适用边界、输入要素、结构骨架、常见误区、补充读取。

## 会议纪要
## 请示/申请
## 报告/情况说明
## 函/复函/征求意见函
## 通知/通告/公告/公示/通报
## 意见/决定/决议/议案/公报/命令
## 讲话稿/致辞/述职
## 工作总结/工作要点/周报
## 调研报告/研究报告/可研报告/建设方案
## 采购公告/审查材料
## AI 算力与技术服务
```

每节控制在短清单，不写完整模板正文。`AI 算力与技术服务` 小节只放触发和跳转：详细结构仍去 `ai-compute-docs.md`。

同时更新 `SKILL.md` reference 路由表，增加一行：

- `references/genre-playbooks.md`：按文种/专项选读；当任务是会议纪要、讲话稿、工作总结/周报、调研/研究/可研、采购公告、审查材料、AI 算力专项等时读取。

### 方案 B：后续再考虑

如果 `genre-playbooks.md` 超过约 250-300 行，再拆为 `references/genres/*.md`。第一轮不建议直接拆，因为：

- 本仓库镜像较多，拆文件会增加同步和发布漂移风险。
- Skill 读取原则要求渐进 disclosure，过多文种文件会让 agent 不知道先读哪个。
- 当前多数文种共用硬边界和办理要素，过早拆分会重复规则。

### AI 算力和采购内容收束

下一轮可做的最小去偏向：

1. `SKILL.md` 保留 frontmatter 描述、范围表、reference 路由里的 AI 算力触发，不保留过多示例。
2. `handling-elements.md` 保留“仅明确涉及时核对本节”的原则，可把详细清单迁入或指向 `ai-compute-docs.md`。
3. `argument-chains.md` 保留技术材料链条的通用入口，把 Token/GPU/SLA 细节集中到 `ai-compute-docs.md`。
4. `anti-ai-patterns.md` 中 AI 算力空泛技术表述可缩成通用提醒并指向 `ai-compute-docs.md`，避免低 AI 味审稿被专项例子占太多篇幅。
5. `genre-checklist.md` 的采购公告继续保留为通用文种，不把采购公告默认解释为 AI 算力采购。

## 需要复现的问题和当前判断

| 线索 | 复现情况 | 当前判断 | 下一步 |
| --- | --- | --- | --- |
| ClawHub 网页与 CLI inspect 版本展示不一致 | 本轮命令记录称网页与 CLI inspect 结果不一致；未随附网页快照和 inspect JSON | 暂列展示层/缓存待复核项，不能据此认定包内版本失败 | 发布前继续以 inspect、安装包和必要网页快照交叉确认 |
| `clawhub inspect` fetch failed | 清代理后通过 | 本机代理/网络环境问题 | 后续命令先清代理变量 |
| `tags` 出现带引号 key | 本轮命令记录称 inspect JSON 中 tags 存在带引号 key；未随附原始 JSON | 暂列 tag 元数据待复核项，不能据此认定加载断裂 | 1.5.0 发布前检查 openclaw/frontmatter tag 序列化并保存 inspect 证据 |
| `npm run eval:official-writing:smoke` 失败 | 终端记录称 npm smoke 未形成通过结论，问题集中在 promptfoo Python provider/本地 Python 路径环境 | 评测环境阻塞，不是本轮方案阻断；不能宣称通过 | 下轮补充原始日志或重新运行，通过后再作为发布门禁 |
| 真实样文 eval 占位词风险 9/10 | 复现 | 工具匿名标签导致的审计限制，不能直接认定 skill 失败 | 下一轮增加真实 writer/verifier 或调整 eval 的匿名占位判断 |
| AI/算力/采购散落多个 MD | `rg` 复现 | 确有表面偏向风险，但部分是触发/边界需要 | 1.5.0 用 playbook 和专项收束，不直接删除能力 |

## 下一轮最小实施计划

1. 固定 `v1.4.15` 作为消融基线，创建 detached worktree。
2. 先补或调整 deterministic 用例，覆盖会议纪要、报告、请示/申请、函/复函、通告/公告、工作总结/周报、调研/可研、普通采购公告、AI 算力专项触发不外溢。
3. 新增 `references/genre-playbooks.md`，只写抽象 playbook，不写模板正文。
4. 更新 `SKILL.md` reference 路由表，只增加 playbook 行和少量读取说明。
5. 轻量收束 AI 算力/采购散落内容：把细节指向 `ai-compute-docs.md`，保留通用触发和硬边界。
6. 运行 `python .\tools\sync_adapters.py` 同步镜像。
7. 跑基线消融、全量单测、真实样文 eval、`git diff --check`。
8. 修复 promptfoo 环境后再跑 `npm run eval:official-writing:smoke`；若仍失败，不能发布。
9. 做真实 writer/verifier 测试：至少覆盖会议纪要、请示、报告、函/复函、普通采购公告、工作总结/周报、AI 算力专项和只审不改。verifier 只看 prompt + 输出，不看修改动机。

## 交付判据

1. 与 `v1.4.15` 消融相比，current 不新增失败。
2. 普通公文不会被 AI 算力/采购语境带偏。
3. 专项场景能更快进入正确骨架，但不改变事实边界和用户模板优先。
4. 只审不改仍不重写全文、不评分。
5. 缺金额、日期、联系人、依据时仍先成稿、正文外短列待确认，不阻断。
6. 无新增默认联网、API、Word/PDF、脚本硬门禁。

## 本轮不进入实现的原因

用户本轮要求产出借鉴方案，不直接借鉴直接改。当前已有一些显示层、评测环境和审计工具限制需要先记录清楚；如果此时直接改 reference，容易把“结构优化”和“环境异常修复”混在一起，也难以判断下一轮消融的真实来源。

## 独立复核记录

本报告提交前已交给独立只读 sample agent 复核。复核结论为 `WARN`：主结论和边界符合 `AGENTS.md` 与 `chinese-official-writing/SKILL.md`，但原稿中有三类表述需要收紧：

- ClawHub inspect 的精确 stats、网页版本和 tag 异常缺少随附原始日志，不应作为独立证据结论。
- 全量单测、`git diff --check` 和 npm smoke 的本轮结果需要区分“已在终端执行”和“有落盘日志可复核”。
- 未下载展开的候选 skill 不能写成已分析内部结构。

本版已按上述意见修订：保留可由本地 summary 和已下载包支撑的结论；把未下载候选降级为下轮可选复核对象；把 smoke 失败和网页展示不一致继续记录为待复核风险，不写成 skill 逻辑失败或通过。
