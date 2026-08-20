# v1.6.11 后续原子验证与状态收口

日期：2026-08-20。范围：`UL-005`、`OT-001`、`OV-001` 的最小续验，SkillHub 竞品可借鉴原子，description 入口减载，以及发布后状态冲突。没有合并 main、推送、移动 tag、上传或发布，也没有启动大规模付费模型矩阵。

## 当前真实状态

- `main` 与 `origin/main` 均为 `b0952c0e8a7a143ac23c1bb98cbbec1a66bbf62c`；`v1.6.11^{commit}` 为 `15af538adfb5ec6a711770d67ec265498ec7127d`。
- 本地付费基线 `codex/paid-outline-review` 为 `8363fabacccac9d6f105a8f7e0fa9eeb53d3413c`，工作树清洁；本轮候选没有反向进入公开 main。
- 2026-08-20 实时查询 SkillHub.cn：latest 与 tags.latest 均为 `1.6.11`，Keen、Sanbu 均为 `benign`。旧 `queued` 记录是历史传播快照，不再表示当前状态。

## 原子结果

### UL-005：来源完整性成立，来源蕴含仍未成立

隔离分支 `codex/v1612-ul005-source-binding@95ef7498` 增加 request/D0 的 SHA-256、精确 span、quote、范围和逐增量绑定。固定边界测试能让无 span 的 R8 风险增量失败，也能让带真实 span 的 R11 增量通过。

复核发现该门只证明“引用来自权威文本”，没有证明“引用完整支持增量”：request 中任意真实但无关的 span 仍可绑定任意增量；局部相关 span 也不能排除新增目的、动作、因果、结果或状态强化。历史同模型 verifier 已在 R8 把坏增量改标后放行，因此该原型不解决 `UL-005`，不合入 main，继续 HOLD。

下一最小验证：冻结原始 R8/R11 的 request、D0、D1 和 hash；要求真正独立 verifier 对每个增量返回 `span_ids`、未被支持部分及主体/对象/状态/强度一致性；加入“绑定真实但无关 span”和“绑定局部相关 span但新增谓语”两条对抗题。R8 必须 D0、R11 必须 D1，否则停止工程化。

### OT-001：Stop 收紧候选成立一半，继续留在付费实验线

隔离付费分支 `codex/paid-outline-ot001-r3@59531540` 把 Stop 修订收紧为：初稿视为不可编辑字符串，只删除明确、可独立分离的连续纲外片段，其余字符逐字保留；无明确片段时逐字回显。

- 本地 `qwen3.8:27b` 同稿复放：删除 D0 开头23字符的纲外标题和两个换行，D1 等于 `D0[23:]`；D0 482字符、D1 459字符，其余字符逐字一致。该结果没有原始 CLI transcript，只保留正文 hash，不能冒充宿主 Hook 生命周期。
- WorkBuddy 内置 CodeBuddy CLI 2.115.0 当前在线复测：39文件 outline companion，fingerprint `9bc06052575c8b4ca0f100a826bdb74a5a2141c23a50f473ad142e34dce32a08`；`outline-planner` 调用1次并完成，Stop 主动阻断1次。初稿没有纲外片段，第二次完整答复与 D0 逐字一致，均为178字符，SHA-256 均为 `7c5fa4cb9fe11f7cd219f79ade823a982d70f82960d03e6ab215879a00d7e369`。session JSONL SHA-256 为 `63560765fbcfed1cb08609611692fc17d5494deb31ac76f250790e9fcd7bb25a`。

当前结论：无纲外片段的 exact replay 已在 CodeBuddy 闭合；明确片段删除只在本地模型复放成立，尚未在当前 CodeBuddy 形成同样的删除样本。候选不合入 `codex/paid-outline-review`，不发布；`OT-002` 和组合能力继续 HOLD。

### OV-001：CodeBuddy 生命周期已补，压缩 D1 未补

使用 WorkBuddy 5.3.13 内置 CodeBuddy CLI 2.115.0、当前 main 的54文件 `over_length` companion，fingerprint `86689e108842bd7f09f8075e074fbdd65b2faaf59557fe98e06b043370f7b96d`。

- 首次尝试中，模型自行提前压缩到上限内，没有建立 OV 事务，判为无效样本。
- 两个有效触发样本分别为506字和496字 D0、上限420字；均完成 Skill、事务、Stop、D0 选择和最终 hash 回显，但在重复观察阶段以 `invalid_preserved_segment` 安全回退，`compression_attempts=0`。两份 record SHA-256 分别为 `ec905ac210ec946a68388aa5c2071679365654cad3faa7695e33c153970534d2`、`3419ecbc5fd9441e91e53a9fd174dd8a1fa072e6c5fb54ae01603c03ad21af0a`。

该结果只证明当前 CodeBuddy 的 OV 生命周期和安全回退，不证明压缩收益。覆盖表据此改为“生命周期已补、该题 D1 未补”，停止为成功样本反复抽卡。

### MT-005：组合侦察作废为准入证据，改按原子登记

隔离侦察候选将 description 从280字压到136字，减少144字（51.4%），但同时删除负向排除清单、把长文种表改为任务簇并合并受众表述，不能把结果归因到任一改动。该组合候选不作为产品准入证据；canonical 与四套镜像没有改动。

WorkBuddy / CodeBuddy 2.115.0 小样本：

| 题目 | 280字基线 | 136字候选 | 结论 |
| --- | --- | --- | --- |
| 董事会设备更新决议 | 自主调用 Skill | 自主调用 Skill | 低频正式文种路由保持 |
| 中文论文摘要润色 | 未调用 Skill | 未调用 Skill | 删除负向清单未造成该题误触发 |

正向两稿都有共同硬失败：`dontAsk` 模式拒绝 reference 读取后，基线补出“符合公司章程”，候选补出《公司法》及章程程序判断。description 只负责入口，不能用2/2路由掩盖成稿不可用。

随后严格拆成三个顺序原子：`MT-005a` 只删除负向排除句，`MT-005b` 只把文种枚举改为任务簇，`MT-005c` 只合并受众表述。用户进一步明确，减载价值是 description 每次随宿主发现/加载进入任务上下文时的长期消耗；真实测试本身不因 token 成本而降级，但必须原子化以便归因。

`MT-005a` 使用与基线相同的 WorkBuddy / CodeBuddy 2.115.0、`deepseek-v4-flash`、max、`bypassPermissions`，保证 reference 可读。候选只删除末尾“不用于英文、文学、营销、社媒、论文或个人求职。”23字，其余 description 和产品文件逐字不变；280→257字，每次加载减少8.2%。

| 题目 | 280字基线 | 257字 `MT-005a` | 成稿/边界 |
| --- | --- | --- | --- |
| 董事会设备更新决议 | 调用 Skill | 调用 Skill | 两边均读取 reference，事实、数字、日期和办理主体保留，正文可用 |
| 中文论文摘要润色 | 未调用 | 未调用 | 无新增误触发 |
| 小红书奶茶营销文案 | 未调用 | 未调用 | 营销/社媒边界无新增误触发 |
| 个人求职自我评价 | **误调用 Skill** | 未调用 | 删除负向句没有放大风险，反而消除本样本的反向唤起 |

结论：`MT-005a` 通过本轮最小真实 A/B，可以作为单独候选进入本分支 canonical 与四套普通镜像；不据此推定 `MT-005b/005c` 也安全。八份原始 terminal 的 SHA-256 依次保存在共享 output，基线/候选分别为：决议 `109b6a53…` / `8dde0369…`，论文 `196579a9…` / `ba019583…`，营销 `4600b1f8…` / `18136e74…`，求职 `0848c8a7…` / `93287680…`。

`MT-005b1` 随后只处理新闻枚举：保留 description 开头的“新闻稿件”，删除后段“新闻稿、新闻消息、快讯、活动报道、活动新闻稿、新闻通稿、新闻评论、时评、评论员文章”42字。其余内容逐字不动；257→215字，相对原始280字累计减少65字（23.2%）。

| 题目 | 257字基线 | 215字 `MT-005b1` | 成稿/边界 |
| --- | --- | --- | --- |
| 100字内图书馆快讯 | 调用 Skill | 调用 Skill | 两边均保留800个、一层二层、其他区域未开放、正式日期未定 |
| 学校活动新闻稿 | 调用 Skill | 调用 Skill | 两边均保留40人、1200册、17册破损和修复时间未定，无领导讲话或意义外扩 |
| 300字内新闻短评 | 调用 Skill | 调用 Skill | 两边均保留18%、高峰无车、方案评估中和未公布完成时间；评论建议未冒充事实进展 |
| 小红书奶茶营销文案 | 既有 `MT-005a` 基线未调用 | 未调用 | 删除新闻细项未造成相邻营销误触发 |

结论：新闻总括词足以承载三个差异较大的子类型，`MT-005b1` 候选通过；不据此删除其他枚举簇。七份新增 terminal 的完整 SHA-256 为：快讯 `5ff5ab4a…` / `7c28fb24…`，活动稿 `339d1380…` / `2193fbaa…`，短评 `22a36c09…` / `f5310434…`，候选营销 `2716ae12…`。

`MT-005b2` 处理制度簇时按失败继续缩小：六项替换为“制度规范”、删除“规定/办法/管理办法”、删除“规定/办法”、只删“规定”。四档候选在管理办法或操作规程正文中分别新增材料外用途、设备就绪状态、统一预约渠道或提交动作；最小候选仍写入“通过实验室预约平台提交预约申请”。因此整簇 HOLD，保留“制度、规定、办法、管理办法、实施细则、操作规程”，不以规程和学术边界样本的局部 PASS 覆盖管理办法硬失败。

`MT-005b3` 首候选同时把“函、复函”合为“函件”并删除后段重复“征求意见函”，215→207字。征求意见函、复函均触发，私人朋友回信不触发；但候选复函独有“经研究”，材料没有该程序事实，故该合并 HOLD。候选征求意见函首跑仅启动输入框、提示未送出，作为无效样本排除；新会话重试后才形成有效稿，不把环境失败计入胜负。

随后 `MT-005b3r2` 只删除重复的“征求意见函”6字，保留“函、复函”，215→209字。征求意见函仍自主调用 Skill，保留市教育局/市卫生健康委、8月28日17时、书面反馈、无意见书面回复、李明和电话，未补文号、日期、修订背景或逾期后果；私人朋友回信仍未调用。该原子通过，累计相对280字基线减少71字（25.4%）。相关 terminal SHA-256：首候选有效征求意见函 `0844f643…`，基线/首候选复函 `08d72ad4…` / `1fd6e7ef…`，基线/首候选私人回信 `d1a6dce0…` / `4d0ec1b…`，缩小候选征求意见函 `8bc67953…`，缩小候选私人回信 `bbd7600f…`。

`MT-005b4` 先只删“致辞”3字，再缩小为仅把“讲话、致辞”并成“讲话致辞”以节省1字。两档都能触发正式签约活动致辞，私人婚礼祝酒词均不触发；但首档候选新增“合作正式启动”和组织首批学生进入基地的承诺，次档仍新增协议落地、提供保障和必然取得成果，并淡化基地建设及学生进入时间未定。两档均 HOLD，保留原词。terminal SHA-256：基线/删除候选正式致辞 `ad8626d3…` / `520cad9d…`，基线/删除候选私人祝酒 `938fa492…` / `562c2dcb…`，并词候选正式致辞 `1d1e31fd…`，并词候选私人祝酒 `19af1e76…`。

`MT-005b5` 只删除后段“采购公告”5字，依赖已保留的通用“公告”，209→204字。基线与候选采购公告均自主调用 Skill，保留20台、18万元、9月5日17时、报名邮箱，以及资格、参数、评审、合同期限和交付日期均未定；候选没有新增采购方式、资格、评分、付款、交付承诺或投诉渠道。个人家用打印机选购两边均未调用 Skill。该原子通过，累计相对280字基线减少76字（27.1%）。terminal SHA-256：采购公告基线/候选 `55537633…` / `2e1a5646…`，个人购物基线/候选 `e97395cc…` / `a2e3d34f…`。

## SkillHub.cn 可借鉴原子

下载量、星标和平台排序只作发现线索，不作质量结论。以下包在下载内容中均未发现独立 LICENSE，因此只借鉴抽象方法，不复制文字、模板、标记或代码。

| 原子 | 来源与当前可见状态 | 比本 Skill 多出的价值 | 最小真实题 | 优先级 |
| --- | --- | --- | --- | --- |
| 会议争议的未决选项与来源侧车 | [`meeting-minutes-drafter`](https://api.skillhub.cn/api/v1/skills/meeting-minutes-drafter)，1.6.0，9文件 | 当前纪要叶会保留未决，但没有同时结构化呈现互斥选项及发言来源 | 甲主张立即上线、乙主张先试点、主持人未表决；不得选边或写成决定 | 1：写稿收益高、风险可界定、无 Hook 工程 |
| 研究材料用途分型与充分性停止 | [`dknowc-official-doc-writer-skillhub`](https://api.skillhub.cn/api/v1/skills/dknowc-official-doc-writer-skillhub)，3.4.2，60文件 | 把政策依据、数据支撑、参考案例、表述参考分开，并为补搜设停止条件；当前研究页有来源元数据但缺用途边界和搜索预算 | 国家/本省/外省政策、新闻稿和冲突数字混合报告；外省不得作本地依据 | 2：事实收益高，只在用户允许联网时启用 |
| 文件提取失败与降级交付 | [`meeting-minutes-drafter`](https://api.skillhub.cn/api/v1/skills/meeting-minutes-drafter)、[`gongwenformat-pro`](https://api.skillhub.cn/api/v1/skills/gongwenformat-pro)，后者1.4.0、3文件 | 明确扫描 PDF、空文件、提取失败、请求转换及 Markdown 降级；当前主要依赖外部文档工具 | 真实扫描 PDF/不支持格式失败后不编稿，给出转换或降级路径 | 3：宿主依赖高，等真实失败再做 |

不借鉴大模板库、金句库、诊断评分、格式脚本或流量排名；它们没有证明真实稿更安全、更自然或更可直接使用。

## 最小工程验证

- 首次运行7组定向测试共108项时，唯一失败是 `test_skill_boundary` 仍要求 description 包含“营销/社媒/论文”；产品真实 A/B 已改变该合同，测试同步为正向边界和负向词不存在后复跑，108/108通过。
- `MT-005b1` 接入后同组108项首次有6个失败，均为旧测试要求九个新闻别名逐字留在 frontmatter；真实 A/B 已证明总括词可触发，测试改为 frontmatter 保留“新闻稿件”、精确别名继续留在 Skill 正文路由与对应叶后，复跑108/108通过。
- `MT-005b3r2/005b5` 接入后，先将静态边界从必须逐字包含“采购公告”同步为保留通用“公告”且不再出现两个已删重复项；79项 description/边界测试和同组108项定向测试均通过。该同步只发生在真实 A/B 通过后。
- canonical、Agent Skills、Qwen Code、Hermes 四个普通入口分别运行 Skill Creator quick validate，均返回 `Skill is valid!`。
- `host-capabilities.json` JSON 解析通过；`maintenance.tests.test_repository_reachability` 包含在108项定向测试内；`git diff --check` 通过，仅有 Windows 换行提示。
- 独立轻量 review 首轮指出 CodeBuddy/Codex 生命周期范围、竞品 `/files` 与许可证命令、共享 output 路径归属不足；按范围字段、精确证据指针、命令与绝对路径修正后，最终复核无剩余 P0—P2。镜像 CRLF 可能让未标准化的 PowerShell 行长误多算1字，内容 hash 在按 description 文本取值后完全一致，不构成阻断。

## 已处理的状态冲突

- `待办.md` 和 `roadmap.md` 的当前基线从 v1.6.10 改为已发布 v1.6.11；旧版本传播记录保留为历史，不再冒充当前。
- `host-capabilities.json` 中已经发布并有真实证据的 under-length、over-length、delivery-cleanliness、repetition-cleanup 从 `candidate` 改为 `available_opt_in`，同时显式保留 `UL-005` HOLD；Codex 只绑定 CLI 0.144.6，CodeBuddy 只绑定 WorkBuddy 5.3.13 内置 CLI 2.115.0 的 `lifecycle_verified`，不外推到所有版本。对应测试同步验证范围字段。
- `requirements.md` 补登记此前 coverage 中存在但长期规格缺失的 `MT-004`，并新增 `MT-005a/005b/005c` 原子顺序；避免 coverage 有编号、requirements 无定义，也避免组合减载反复消耗真实 token。
- SkillHub v1.6.11 的 Keen/Sanbu 当前均为 benign；旧 queued 只保留在带日期的历史记录中。

## 实际命令与原始材料

```powershell
git status --short --branch
git rev-parse HEAD
git rev-parse origin/main
git rev-parse 'v1.6.11^{}'
git worktree list --porcelain
curl.exe --noproxy "*" -sS https://api.skillhub.cn/api/v1/skills/chinese-official-writing
curl.exe --noproxy "*" -sS https://api.skillhub.cn/api/v1/skills/meeting-minutes-drafter
curl.exe --noproxy "*" -sS https://api.skillhub.cn/api/v1/skills/meeting-minutes-drafter/files
curl.exe --noproxy "*" -sS https://api.skillhub.cn/api/v1/skills/dknowc-official-doc-writer-skillhub
curl.exe --noproxy "*" -sS https://api.skillhub.cn/api/v1/skills/dknowc-official-doc-writer-skillhub/files
curl.exe --noproxy "*" -sS https://api.skillhub.cn/api/v1/skills/gongwenformat-pro
curl.exe --noproxy "*" -sS https://api.skillhub.cn/api/v1/skills/gongwenformat-pro/files
Get-ChildItem <expanded-package> -Recurse -File
Test-Path <expanded-package>\LICENSE
Test-Path <expanded-package>\LICENSE.md
python -B maintenance/tools/assemble_hook_companion.py --host codebuddy --capability outline_assist --output <ignored-output>
python -B maintenance/tools/sync_adapters.py
E:\Program Files\WorkBuddy\resources\app.asar.unpacked\cli\bin\codebuddy plugin validate <companion>
python -B output/current-verification/v1.6.10-host-gaps/run_codebuddy_pty.py ...
python -B output/current-verification/v1.6.11-description-load/run_codebuddy_once.py ...
```

忽略目录中的可复核原始流均位于共享主 workspace，不在本研究 worktree 内；以下绝对路径材料不随提交传播，长期判断以本文件记录的 hash 为准：

- `F:\Workspaces\chinese-official-writing-skill\output\current-verification\v1.6.11-ov-codebuddy\run-r2\`、`run-r3\`
- `F:\Workspaces\chinese-official-writing-skill\output\current-verification\v1.6.11-ot-codebuddy\run-r2\session.jsonl`
- `F:\Workspaces\chinese-official-writing-skill\output\current-verification\v1.6.11-description-load\mt005a-{base,candidate}-{resolution,academic,marketing,job}\terminal.txt`（共享 workspace 外部忽略材料；不随研究 worktree 提交）

官方宿主契约沿用： [Codex Hooks](https://learn.chatgpt.com/docs/hooks.md)、[Claude Code Hooks](https://code.claude.com/docs/en/hooks)、[CodeBuddy Hooks](https://www.codebuddy.ai/docs/cli/hooks)。CodeBuddy Hooks 仍是 Beta；本轮实证只绑定 WorkBuddy 内置2.115.0，不外推到所有 CodeBuddy 版本。
