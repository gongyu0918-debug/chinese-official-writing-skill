# 社区去 AI 味规则复核

日期：2026-09-14

范围：为中文公文 writing Skill 的 anti-AI 语言叶复核公开社区规则，重点回答“先……再……”“不是……而是……”及相关二元、三连、重复结构是否有可复用的正向判据。只记录语义编辑规则，不把规则用于作者身份判断或检测器规避。

本轮只读取少量公开 GitHub 文件，没有整批下载仓库。排除了单个词命中即禁用、故意错别字/口语化、虚构个人经历、伪造引用和“保证过检测”等不适合正式材料的做法。下文的“独立来源数”按规则家族保守计数：同一上游或明确受其启发的项目合并，不把同源实现重复算作共识。

核对的产品状态：2.0 主工作树 `F:\Workspaces\chinese-official-writing-skill` 的 `chinese-official-writing/references/anti-ai-patterns.md` 位于 `eb20eed0e0f63926c2ac49a7becfdda0baec6212`，按统一 LF 正文原文计 899 个字符；独立候选 worktree `F:\Workspaces\chinese-official-writing-skill-worktrees\anti-ai-concrete-rules-20260914` 的同名文件位于 `c884463621173ae46b6ff62c2ed8467bda949eb8`，按同一口径计 1325 个字符。候选已补 R1/R2 及机械重复、连续否定的具体判据；R3 的“三项按信息量判断”仍未写入候选。本记录不把正在进行的候选 A/B 结果当作社区规则证据。

## 1. 检索项目、许可与同源检查

| 编号 | 公开项目及主要规则原文 | 许可 | 同源/复制检查 |
|---|---|---|---|
| A | [syw2039/humanizer-zh：中文规则](https://github.com/syw2039/humanizer-zh/blob/main/references/chinese-ai-patterns.md)；[SKILL.md](https://github.com/syw2039/humanizer-zh/blob/main/SKILL.md) | MIT（[LICENSE](https://github.com/syw2039/humanizer-zh/blob/main/LICENSE)） | `SKILL.md` 明确以 [blader/humanizer v2.9.1](https://github.com/blader/humanizer/blob/main/SKILL.md) 为基础，归入 humanizer 家族。 |
| B | [fy-agent/humanize-chinese-writing：中文去 AI 味 Skill](https://github.com/fy-agent/humanize-chinese-writing/blob/main/SKILL.md) | PolyForm Noncommercial License 1.0.0（[LICENSE](https://github.com/fy-agent/humanize-chinese-writing/blob/main/LICENSE)） | GitHub 元数据为 `fork=false`、无 `parent`；检阅的 README/SKILL 未声明上游。许可限制下只作规则观察，不直接搬入商业产品。 |
| C | [foreverseapp/zh-ai-flavor-rules：规则数据](https://github.com/foreverseapp/zh-ai-flavor-rules/blob/main/rules/rules.json)；[README](https://github.com/foreverseapp/zh-ai-flavor-rules/blob/main/README.md) | MIT（[LICENSE](https://github.com/foreverseapp/zh-ai-flavor-rules/blob/main/LICENSE)） | GitHub 元数据为 `fork=false`、无 `parent`；README 称规则来自 Foreverse 生产审查流水线，未声明 humanizer 上游。 |
| D | [evelynyaxueke/anti-ai-writing-kit-zh：中文规则](https://github.com/evelynyaxueke/anti-ai-writing-kit-zh/blob/main/SKILL.md)；[README](https://github.com/evelynyaxueke/anti-ai-writing-kit-zh/blob/main/README.md) | MIT（[LICENSE](https://github.com/evelynyaxueke/anti-ai-writing-kit-zh/blob/main/LICENSE)） | GitHub 元数据为 `fork=false`、无 `parent`；README 将 Humanizer-zh、renwei-writing 列作对比条件，没有声明自身由其派生，按独立实现计，但不把对比实验当第三方质量证明。 |
| E | [LifelongLazyLearner/qu-ai-wei：模式目录](https://github.com/LifelongLazyLearner/qu-ai-wei/blob/main/references/pattern-catalog.md)；[README](https://github.com/LifelongLazyLearner/qu-ai-wei/blob/main/README.md) | MIT（[LICENSE](https://github.com/LifelongLazyLearner/qu-ai-wei/blob/main/LICENSE)） | GitHub 元数据为 `fork=false`、无 `parent`；README 明确称方法受 humanizer 启发、翻译腔参考 yage.ai。为避免重复计数，与 A 合并为 humanizer 相关家族。 |
| F | [KamiOrz/stop-slop-zh：结构规则](https://github.com/KamiOrz/stop-slop-zh/blob/main/references/structures.md)；[README](https://github.com/KamiOrz/stop-slop-zh/blob/main/README.md) | MIT（[LICENSE](https://github.com/KamiOrz/stop-slop-zh/blob/main/LICENSE)） | GitHub 元数据为 `fork=false`、无 `parent`；README 明确基于 [hardikpandya/stop-slop](https://github.com/hardikpandya/stop-slop) 中文化，属于与 humanizer 不同的上游家族。 |

元数据核对入口：上述六个仓库各自的 [GitHub REST 仓库信息](https://api.github.com/repos/syw2039/humanizer-zh)、[humanize-chinese-writing](https://api.github.com/repos/fy-agent/humanize-chinese-writing)、[zh-ai-flavor-rules](https://api.github.com/repos/foreverseapp/zh-ai-flavor-rules)、[anti-ai-writing-kit-zh](https://api.github.com/repos/evelynyaxueke/anti-ai-writing-kit-zh)、[qu-ai-wei](https://api.github.com/repos/LifelongLazyLearner/qu-ai-wei)、[stop-slop-zh](https://api.github.com/repos/KamiOrz/stop-slop-zh)（本轮读取时间）。这是 fork/显式上游检查，不是逐字相似度或抄袭鉴定；规则计数已对 A/E 的 humanizer 关系作保守合并，也没有把两个英文上游再计为额外项目。

## 2. 多项目重复的规则类别

“项目数”是检阅到该语义的仓库数；“独立来源数”是合并 A/E humanizer 家族后的保守数。每类只给最小概括和正式材料边界，未复制社区长段原文。

### R1. 虚假二元对比、伪递进

项目数 6（A、B、C、D、E、F）；独立来源数 5。

最小规则：当“不是 A，而是 B”“不在于 A，而在于 B”“不仅 A，更 B”等前半项只是陪衬、两端同义，或材料只支持 B 而没有真实排除/替代关系时，直接写事实、主张或建议。真实事实纠正、范围排除、方案比较、职责边界和引文保留。

正式材料理由：可减少无依据的“揭示感”和强行抬高结论，同时不损失真实的范围、比较和政策性质。误判边界是不能因为出现一次就删：例如“不是所有模块迁云，而是仅迁移审校模块”有明确范围排除，应保留。

来源：[A 句式目录](https://github.com/syw2039/humanizer-zh/blob/main/references/chinese-ai-patterns.md)、[B 核心信号](https://github.com/fy-agent/humanize-chinese-writing/blob/main/SKILL.md)、[C 正则规则](https://github.com/foreverseapp/zh-ai-flavor-rules/blob/main/rules/rules.json)、[D 硬性规则](https://github.com/evelynyaxueke/anti-ai-writing-kit-zh/blob/main/SKILL.md)、[E 对称骨架](https://github.com/LifelongLazyLearner/qu-ai-wei/blob/main/references/pattern-catalog.md)、[F 二元对立](https://github.com/KamiOrz/stop-slop-zh/blob/main/references/structures.md)。

2.0 状态：主文件已有语义提醒；c8844636 候选已补具体判据和“公众反映最强烈”虚构强度的例子，属于已覆盖项。

### R2. 机械先后与连接词流水线

项目数 5（A、B、D、E、F）；独立来源数 4。

最小规则：没有实际时间、步骤、办理顺序或责任次序时，不用“首先、其次、最后”“先……再……”和连续“此外、同时、进一步、综上”制造逻辑；有真实流程、参观路线、审批顺序、条款顺序或材料指定顺序时照实保留。删除路标时保留其引出的事实。

正式材料理由：公文经常需要明确步骤和责任，规则只能压缩人为制造的阶段感，不能抹掉程序顺序。误判边界是不能把所有“首先”或“先……再……”视作 AI 味。

来源：[A 连接词流水线](https://github.com/syw2039/humanizer-zh/blob/main/references/chinese-ai-patterns.md)、[B 路标信号](https://github.com/fy-agent/humanize-chinese-writing/blob/main/SKILL.md)、[D 过渡词](https://github.com/evelynyaxueke/anti-ai-writing-kit-zh/blob/main/SKILL.md)、[E 开头/篇章组织](https://github.com/LifelongLazyLearner/qu-ai-wei/blob/main/references/pattern-catalog.md)、[F 公式化叙事与段首连接](https://github.com/KamiOrz/stop-slop-zh/blob/main/references/structures.md)。

2.0 状态：主文件已有“首先、其次、综上”按语境判断；c8844636 候选已具体区分真实办理/参观顺序与人为分阶段，已覆盖。连接词流水线仍属于候选规则的软性复核，不宜改成词表硬门禁。

### R3. 强凑三项、三段式强迫症

项目数 5（A、B、D、E、F）；独立来源数 4。

最小规则：按真实信息量决定分项数量；两项就写两项，四项就写四项。只有在为追求完整感硬凑三个形容词、三个动作、三段或“观点—解释—总结”且各项没有独立事实落点时，才合并、删去空项或改成自然段。真实步骤、责任分工、法定要件、完整清单和用户指定结构保留。

正式材料理由：公文中的三项结构有时是法定要件、工作任务或并列责任，保留比打散更清楚。误判边界是不能因“恰好三项”判错，必须确认第三项无独立信息或只是换词升华。

来源：[A 三段式/三点目录](https://github.com/syw2039/humanizer-zh/blob/main/references/chinese-ai-patterns.md)、[B 三段式信号](https://github.com/fy-agent/humanize-chinese-writing/blob/main/SKILL.md)、[D 列表规则](https://github.com/evelynyaxueke/anti-ai-writing-kit-zh/blob/main/SKILL.md)、[E 任意分层与三连](https://github.com/LifelongLazyLearner/qu-ai-wei/blob/main/references/pattern-catalog.md)、[F 机械三连](https://github.com/KamiOrz/stop-slop-zh/blob/main/references/structures.md)。

2.0 状态：主文件仅在“连续排比”层面泛化提醒；c8844636 候选的新增四类判据中仍没有“按真实信息量决定两项/四项”的明确规则。这是本轮唯一有充分历史和多项目支持的真缺口，推荐只补这一条，不再扩张到数字黑名单或标点禁用。

### R4. 同义词轮换与主体/对象漂移

项目数 4（A、B、D、E）；独立来源数 3。

最小规则：同一主体、对象或概念在同一稿中不要为了避免重复轮换成“项目/平台/系统/服务”等称呼；统一稳定名称。若词语确实承担不同范围、职责或术语含义，应保留区别。

正式材料理由：稳定称呼能保护责任归属、对象边界和术语一致性。误判边界是不能为了“自然”删掉必要复称，也不能把不同系统、不同责任主体合并成一个名称。

来源：[A 同义词轮换](https://github.com/syw2039/humanizer-zh/blob/main/references/chinese-ai-patterns.md)、[B 三段式与同义词轮换](https://github.com/fy-agent/humanize-chinese-writing/blob/main/SKILL.md)、[D 语义检查护栏](https://github.com/evelynyaxueke/anti-ai-writing-kit-zh/blob/main/SKILL.md)、[E 词汇与语义复现](https://github.com/LifelongLazyLearner/qu-ai-wei/blob/main/references/pattern-catalog.md)。

2.0 状态：主文件已有“换词重复、反复换名称造成指代不清”的原则；c8844636 候选又允许关键主体沿用原名，已覆盖，不建议单独增加规则。

### R5. 事实后的重复解释、包装式总结与口号收尾

项目数 4（A、B、D、E）；独立来源数 3。

最小规则：同一事实已经说清后，若下一句只是换词解释，第三句再宣布其意义，且没有新事实、限制、决定或行动，只保留信息最足的一层。结尾停在最后一个事实、状态、决定或有依据的动作。

正式材料理由：能压缩报告中的“事实—同义解释—再总结”而不削弱证据。误判边界是摘要、定义、法律限定、风险解释和用户要求的结论段有独立功能时保留；不能因有数据就删除其必要作用说明。

来源：[A 重复解释与结尾](https://github.com/syw2039/humanizer-zh/blob/main/references/chinese-ai-patterns.md)、[B 段落信息密度](https://github.com/fy-agent/humanize-chinese-writing/blob/main/SKILL.md)、[D 一个命题一个落点](https://github.com/evelynyaxueke/anti-ai-writing-kit-zh/blob/main/SKILL.md)、[E 低信息密度与收尾](https://github.com/LifelongLazyLearner/qu-ai-wei/blob/main/references/pattern-catalog.md)。

2.0 状态：主文件的“无新信息合并”和“无实际作用的口号”已覆盖；历史上有实际重复展开案例，但目前没有比 c8844636 更强的独立规则缺口，宜在真实 A/B 中观察，不追加长规则。

### R6. 库存开头、元话语与流程旁白

项目数 5（A、B、D、E、F）；独立来源数 4。

最小规则：删掉只宣布“本文将……、下面说明……、为了便于理解……”或模型正在如何组织文字的句子，直接进入事实、事项或有据分析；真实的文件用途、办理背景、文内导语和用户要求的声明保留。

正式材料理由：去掉正文外的写作旁白后，读者能直接找到事项和办理内容。误判边界是“现将……报告如下”、真实导读、适用范围、保密声明和引用的原有业务功能不能当作模型旁白删除。

来源：[A 元话语与章节模板](https://github.com/syw2039/humanizer-zh/blob/main/references/chinese-ai-patterns.md)、[B 路标/协作口吻](https://github.com/fy-agent/humanize-chinese-writing/blob/main/SKILL.md)、[D 元话语](https://github.com/evelynyaxueke/anti-ai-writing-kit-zh/blob/main/SKILL.md)、[E 开头声明计划](https://github.com/LifelongLazyLearner/qu-ai-wei/blob/main/references/pattern-catalog.md)、[F 公式化叙事](https://github.com/KamiOrz/stop-slop-zh/blob/main/references/structures.md)。

2.0 状态：主文件已有专门的“旁白与业务文字”段落和示例，已覆盖。

### R7. 抽象空动词、黑话堆叠与无据强评价

项目数 5（A、B、D、E、F）；独立来源数 4。C 的规则数据有套话/句式检测信号，但没有把它计入这一语义编辑规则的项目数。

最小规则：当“赋能、闭环、打造、推动、进行、形成”等词没有明确主体、对象、动作、结果或制度载体时，改写为材料已有的具体事实；“显著提升、深刻变革、全面覆盖”等评价超过证据时，收窄或删除无据部分。确有行业术语、制度术语、指标或结果依据时保留。

正式材料理由：把工作主体、动作、数据和责任重新放到句子主干，减少宣传腔与空泛结论。误判边界是不能把正式术语、真实成效、引用、计划状态和材料已有的抽象判断一律清零。

来源：[A 空泛意义与空动词](https://github.com/syw2039/humanizer-zh/blob/main/references/chinese-ai-patterns.md)、[B 抽象意义与黑话](https://github.com/fy-agent/humanize-chinese-writing/blob/main/SKILL.md)、[D 正向细节规则](https://github.com/evelynyaxueke/anti-ai-writing-kit-zh/blob/main/SKILL.md)、[E 抽象名词化与弱动词](https://github.com/LifelongLazyLearner/qu-ai-wei/blob/main/references/pattern-catalog.md)、[F README 结构概括](https://github.com/KamiOrz/stop-slop-zh/blob/main/README.md)。C 仅作检测型旁证，见[规则数据](https://github.com/foreverseapp/zh-ai-flavor-rules/blob/main/rules/rules.json)。

2.0 状态：主文件已有强评价、模糊归因和抽象词的语境判断，已覆盖。本轮不将社区词表直接移植为正式公文禁词表。

### R8. 等长句群、整齐段落与连续口号短句

项目数 5（A、B、D、E、F）；独立来源数 4。

最小规则：只有在跨句/跨段出现相同骨架、等长节拍、每段“观点—解释—总结”且没有不同信息职责时，合并、拆分或改变信息重心；短句必须承担事实、限制、决定或动作，不能连续用口号制造节奏。

正式材料理由：帮助压缩模型常见的“每段一样长、每段都升华”，但公文条款、步骤、责任清单和表格说明本来需要平行结构。误判边界是不能为制造“不整齐”而打乱文种骨架、删除并列要件或添加口语。

来源：[A 机械对称与连续短句](https://github.com/syw2039/humanizer-zh/blob/main/references/chinese-ai-patterns.md)、[B 均匀节奏](https://github.com/fy-agent/humanize-chinese-writing/blob/main/SKILL.md)、[D 等长节奏/连续口号列项](https://github.com/evelynyaxueke/anti-ai-writing-kit-zh/blob/main/SKILL.md)、[E 段落过齐](https://github.com/LifelongLazyLearner/qu-ai-wei/blob/main/references/pattern-catalog.md)、[F 节奏与标点](https://github.com/KamiOrz/stop-slop-zh/blob/main/references/structures.md)。

2.0 状态：现有机械重复、连续排比和口号结尾规则可覆盖其中一部分，但主文件未单列句长或段落等长，不能称为完全等效。因正式材料误判边界较宽，不建议本轮再加定量阈值。

## 3. 与历史真实测试的对照

### 3.1 三连是题面中的真实坏例，不应误报成模型失败

`1.5.36-tier1-lint-anti-ai-prompts-20260804.md:9-15` 的 AA02 题面明确给出“首先要高度重视，其次要扎实推进，最后要形成闭环”，并同时给出 12 项巡检、8 项修复、按月检查和月底汇总等事实。AA03 题面还给出“高度重视、扎实推进、确保工作落地见效、形成闭环”（同文件 `:17-25`）。这是测试输入用来探测模板化表达的坏例，不是模型自行生成的失败样本。

对应结果 `1.5.36-tier1-lint-anti-ai-result-20260804.md:55-56`：AA02 两稿被判难分，保留 12 项、8 项、按月检查和月底汇总；AA03 候选把“落地见效”和“形成闭环”分开定位，但结果页明确提示差异可能是自然分组波动。该结果证明事实没有回退，不能证明三连规则已经稳定清理。因此，R3 是合理的规则补回方向，但不应把旧结果包装成已验证的模型增益。

### 3.2 真实对比必须保留

`real-writing-1.5.11-anti-ai.md:30-50,80-122` 的 S2 明确要求保留同一 12 个月口径下 180 万元与 120 万元预算比较，以及“不是所有模块迁云，而是仅迁移审校模块、检索模块仍在本地运行”的真实范围关系。两次复测均要求保留该句；独立 verifier 最终 A/B 均 PASS。该例支持 R1 的保护条件：去掉虚假铺垫，不删除真实比较和必要否定。

### 3.3 重复展开曾在真实输出中出现

`wr001-date-r1/r2-result.md:9-16` 记录了一次实际写稿输出：模型先总述导读、讨论和练习三个环节，再逐项重复展开，最终被记为“重复偏长”。同一记录还另有模型把题面只给的环节补成未提供的具体过程，这是事实边界问题，不能归入单纯去 AI 味。当前 anti-AI 的“同一意思合并”可覆盖重复展开，仍须保留真实三个环节，不应因三项结构本身而删项。

## 4. 结论与补齐建议

1. 社区重复最强的结构规则是二元对比、机械三连、连接词/先后流水线、同义词轮换、事实重复解释、库存开头/旁白、抽象空动词和整齐节奏。当前 2.0 主文件对后七类已有原则性覆盖；c8844636 候选已把 R1、R2 及机械重复、连续否定改为较具体的语义判据。
2. 唯一清晰缺口是 R3：明确告诉模型“内容决定分项数量，两项写两项，四项写四项；只处理无独立信息的强凑三项”，并同时列出真实步骤、职责、法定要件和用户结构的保留条件。建议最多补这一条，保持质量建议层，不做词表硬禁。
3. R5 的“事实—重复解释—再总结”和 R8 的等长节奏可在后续真实 A/B 继续观察，当前证据不足以要求再加规则；R7 不应移植社区黑话词表，避免误伤公文术语和正式成效。
4. 本记录只提供社区规则证据和边界判断，没有改产品文件、没有调用写作模型测试，也没有提交本记录。
