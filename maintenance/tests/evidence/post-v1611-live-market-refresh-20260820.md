# v1.6.11 后 SkillHub / ClawHub 实时竞品刷新与会议原子结果

日期：2026-08-20。范围：SkillHub.cn 与 ClawHub 当前在线发现、最新包只读检查、许可证和安全边界，以及一个会议承诺语义原子的真实写稿 A/B。未安装或运行第三方脚本，未推送、发布或上传。

## 发现范围与版本修正

此前只列少数旧样本，不能代表当前市场。本轮以14组 SkillHub 搜索词覆盖公文、公文写作、机关/正式材料、党政公文、事务文书、总结、报告、讲话、纪要、通知/请示/函、审校、事实核查和排版，去重得到73个结果；其中含通用工具和搜索噪声，不把总数写成73个高质量公文 Skill。

当前实时结果已确认的综合或近似综合包包括：

| 平台 | Skill | 当前版本 | 包体/边界 | 判断 |
| --- | --- | ---: | --- | --- |
| SkillHub | `official-document-skill` | 1.0.3 | 8文件；包内未见 LICENSE | 文种、事实和反 AI 味与 main 大体重合 |
| SkillHub | `govwriting` | 3.2.8 | 25文件；偏技法手册 | 模板与修炼体系多，未证明真实稿更稳 |
| SkillHub | `dknowc-official-doc-writer-skillhub` | 3.4.3 | 60文件；需 API Key；包内未见 LICENSE | 来源用途与地域边界值得拆原子，当前组合候选仍 HOLD |
| SkillHub | `official-document-workflow` | 1.0.0 | 14文件；多专家串行 | 单一权威格式源可借鉴，七段流水线不等于质量 |
| SkillHub | `gongwen-writing` | 1.0.6 | 13文件 | P0/P1/P2 审稿分级有价值；默认先大纲、停等确认与直接交稿边界冲突 |
| SkillHub | `official-docs-write-v2` | 1.0.0 | API 68文件；7 Phase 串行；SKILL 自报3.0.2 | 平台/包内版本冲突；低置信事实分离有价值，强制阻断和大流水线不采纳 |
| SkillHub | `gongwen-word-mini` | 1.0.3 | 58文件 | “正式发文意图”和视觉交付状态是新增原子；格式工程不冒充写稿收益 |
| SkillHub | `tizhineigongwenxiezuopaiban` | 1.0.1 | 13文件 | 问题—对策成对保持与判断强度有价值，但与 main 多有重合 |
| SkillHub | `kunlun-gongwen` | 1.1.2 | 5文件；frontmatter 标 proprietary | 能力跨度过宽，不复制；下载量不作质量证据 |
| ClawHub | `official-document-drafting` | 1.0.0 | 108文件；MIT-0 元数据；SkillSpector HIGH/DO_NOT_INSTALL | 声明式文种 spec 与 main 同构；不安装，不借占位符和固定句数 |
| ClawHub | `official-writing` | 1.0.2 | 2文件；MIT-0 元数据；扫描 clean | 模板型，未见 main 缺失的语义原子 |
| ClawHub | `official-doc-writer` | 1.1.0 | 12文件；MIT-0 元数据；SkillSpector CRITICAL/DO_NOT_INSTALL | 字体/注册表链风险高，不安装 |

SkillHub 当前还存在通知、请示、讲话、总结、报告、纪要和新闻核验等单文种或原子包；本轮实际下载并只读检查 `gongwen-tz@1.0.0`、`gongwen-qs@1.0.0`、`meeting-and-brief@2.0.0`、`meeting-decision-amplifier@1.3.2`、`newsgatekeeper@3.0.0`、`news-fact-check-plus@1.0.0`、`research-reportskill@1.0.0` 等。ClawHub 另核 `meeting-decision-receipt@1.0.1`、`meeting-copilot@1.0.3`、`meeting-minutes-craft@1.0.0` 和 `news-fact-check@1.0.1`。

许可证只按可核表面记录。SkillHub 下载包中多数没有独立 LICENSE；`meeting-decision-amplifier` 的 `SKILL.md` 标 MIT，`kunlun-gongwen` 标 proprietary。ClawHub 表中的 MIT-0 是版本元数据，多数包也没有独立 LICENSE 文件。未复制第三方文字、模板、分类标签或代码。

## 真正值得借鉴的原子

| 原子 | 来源 | 相对 main 的真实缺口 | 状态与下一最小验证 |
| --- | --- | --- | --- |
| 单稿事实台账＋句子回溯 | `gongwen-tz`、`gongwen-qs` | main 有事实边界和来源字段，但没有统一的单稿“原材料—事实项—成稿句”合同 | 值得继续；与 UL-005 合并验证语义相关性，不能只验 hash/span 存在 |
| 会议结论/承诺状态＋原话证据 sidecar | `meeting-decision-receipt` | main 正文已能保留未决、责任和期限，但没有内部 claim—evidence 侧车 | 正文候选本轮拒绝；sidecar 仍 HOLD，需解决证据相关性且不得污染正文 |
| 声明级事实核验矩阵 | `news-fact-check`、`news-fact-check-plus` | external-research 有来源和冲突要求，但没有“主张—来源—结论状态”合同 | 值得继续；仅用户明确核实时触发，先用三条冲突来源真实题 |
| 新闻发布前分级审校 | `newsgatekeeper` | main 有新闻边界和总审，但没有紧凑区分“明确错误/表述风险/优化建议”的交付 | 值得继续；先测未知日期、无来源数字、夸张判断同稿审校 |
| 正式发文意图路由 | `gongwen-word-mini` | 同名“通知/报告/函”可能只是一般材料；名称本身不应自动加红头、文号、主送和版记 | 值得继续；先测内部情况说明、正式报告、普通业务函三题，不先做 DOCX 工程 |
| 问题—措施成对保持 | `tizhineigongwenxiezuopaiban` | main 有事实和结构边界，但没有直接验证压缩/重组时问题与其对应措施不拆错、不串项 | 值得继续；先用工作总结、方案和纯问题无措施边界题，新增材料外措施即停止 |
| 文档 `delivery_ready` 与视觉复核分离 | `gongwen-word-mini` | 转换成功、机器校验和逐页视觉通过是不同事实 | 工程原子，优先级低于真实写稿；仅真实 DOCX 失败时启用 |

不借鉴：固定句数和模板堆叠、默认先大纲再等待、七专家/七阶段流水线、草稿必须超过50行、自动 Word/PDF/红头/字体安装、自动发送、API Key 写入 shell 配置、下载量/星标/TRACE 宣传分数。它们没有证明当前 Skill 的真实写稿更安全、更自然或更可直接使用。

## Description 对照

综合公文竞品多数同样在 description 中枚举文种、场景和能力，部分比当前204字入口更长；这不是继续删除的质量证据。单一原子 Skill 的 description 更值得借鉴：用“任务动作＋输入/输出差异＋一两个关键边界”表达，不列全部相邻任务。

当前 `MT-005a/005b1/005b3r2/005b5` 的真实结果继续有效；制度、函件合并、讲话致辞三项扩大后仍 HOLD。市场扫描没有推翻这些真实稿结论。下一步仍按一个枚举簇或一个受众表述原子化验证，不用竞品短 description 直接替换当前入口。

## 会议承诺语义 A/B

固定基线 `main@b3491e9b`，候选 `codex/v1612-meeting-commitment-atom@9423d951`。候选只在会议纪要叶增加“已决定/暂定/提议/意向、明确承接/未确认承接、原话回指”一句规则，并同步四个普通镜像。WorkBuddy 内置 CodeBuddy CLI 2.115.0、`deepseek-v4-flash`、max、`bypassPermissions`；每臂均读取 SKILL、`information-selection.md` 和 `genre-playbook-minutes.md`。

首轮六个交互 PTY 均停在输入界面，`●=0`、无模型答复，全部记为环境无效。随后保持题面、模型、权限和插件不变，改用已验证的 `--print --output-format json` 通道，6/6 返回成功。

| 题目 | 基线 | 候选 | 判定 |
| --- | --- | --- | --- |
| “我看看”＋点名未回应＋明确周五交付 | 已分成议定事项和两个未决事项，三种状态完整 | 保留三种事实，但未明确标“未确认承接” | 基线已覆盖；候选无目标增益 |
| A方案暂定后明确改为B方案 | 旧方案只作讨论过程，当前决定为B，试运行日期和全面切换保持未决 | 同样正确，结构更长 | 两边通过；候选无独有收益 |
| 主持人明确交办、责任科室未口头回应 | 正确保留会议交办、部门、期限和交付物，不写个人主动承诺 | 额外写“未确认承接” | 候选把内部审计状态带入正式正文，直接可用性更差 |

有效稿正文 SHA-256：基线/候选依次为弱承诺 `0a006f3d…` / `c74dad4a…`，后续修正 `a191c786…` / `3775c357…`，权威交办 `0cdbaac6…` / `ba83fe50…`。六次合计输入 token 686277、输出 token 30046；token 消耗如实记录，不用成本理由降低真实写稿强度。

结论：当前正文基线3/3已实现目标；候选没有可复现改善，并在权威交办题出现直接使用回退。`9423d951` 不合入 main，产品规则停止。竞品真正剩余的价值收窄为内部 claim—evidence sidecar，必须与正文隔离，并与 UL-005 一起验证“证据与结论语义相关”，精确 span/hash 不能单独放行。

## 实际命令与原始证据

```powershell
Invoke-RestMethod 'https://api.skillhub.cn/api/v1/search?q=<query>'
Invoke-WebRequest 'https://api.skillhub.cn/api/v1/download?slug=<slug>'
Invoke-RestMethod 'https://api.skillhub.cn/api/v1/skills/<slug>'
Expand-Archive <package.zip> <directory>
rg -n -i 'license|事实|来源|决策|审校|触发|验收' <expanded-package>
clawhub -V
clawhub search <query> --limit 30
clawhub inspect <slug> --json --files
clawhub inspect <slug> --file SKILL.md
python -B maintenance/tools/assemble_hook_companion.py --host codebuddy --output <ignored-output>
python -B output/current-verification/v1.6.12-source-typing/run_codebuddy_print.py ...
```

SkillHub 搜索去重和下载包位于 `F:\Workspaces\chinese-official-writing-skill\output\current-verification\live-market-research\`。会议原始 JSONL、prompt、exit code 和无效 PTY 记录位于 `F:\Workspaces\chinese-official-writing-skill\output\current-verification\v1.6.12-meeting-commitment\`。`clawhub explore --json` 因当前 API 的 `latestVersion` 形状与 CLI 0.23.1 schema 不一致而失败；没有把该失败表面当作完整“最新列表”。
