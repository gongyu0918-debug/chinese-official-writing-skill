# 1.4.4 SkillHub 公文相关技能检索记录

日期：2026-06-22

本轮使用 SkillHub 公开 API 现场核验，目标是寻找能按最小原则吸收的机制。社区技能只作为思路来源和 prompt/markdown 组织方式参考，不作为可直接复制的实现来源。

## 借鉴门禁原则

任何社区借鉴点进入 1.4.4 候选前，必须同时满足以下门禁：

1. **符合本技能定位**：只增强中文公文起草、改写、复核和正文交付衔接，不把本技能改造成 docx 排版引擎、政策检索系统、法律合规系统或多 agent 平台。
2. **只借鉴思路，不誊抄实现**：禁止直接复制社区技能代码、脚本、正则、模板库、大段 prompt 或固定话术。可借鉴的是流程形态、检查维度、markdown 清单结构和抽象后的 prompt 组织方式。
3. **先归纳共性，再最小吸收**：只有真实写作测试中三次以上出现的共性问题，或多个社区技能共同证明的通用短板，才进入候选；不做一例一修。
4. **不扩大默认触发**：不得把联网搜索、强制确认、Word 生成、格式清洗、模板套用变成默认步骤；用户未要求时仍按现有轻量 workflow 处理。
5. **用户模板优先**：任何借鉴点不得破坏字段式申请、内部模板、附件关系、用户锁定标题/主送/落款/结尾语。
6. **消融后再采纳**：每个候选吸收点落地后，必须和 1.4.3 基线做消融；指标至少覆盖公文格式遵循、文种判断、AI 味残留、prompt 遵循、事实边界、关键要点置入。

## 检索入口

- 公文搜索列表：<https://api.skillhub.cn/api/skills?keyword=%E5%85%AC%E6%96%87&sortBy=score&page=1&pageSize=24>
- `official-doc-writer`：<https://api.skillhub.cn/api/v1/skills/official-doc-writer>
- `official-document-skill`：<https://api.skillhub.cn/api/v1/skills/official-document-skill>
- `gongwenformat-pro`：<https://api.skillhub.cn/api/v1/skills/gongwenformat-pro>
- `doc-format`：<https://api.skillhub.cn/api/v1/skills/doc-format>
- `govwriter-skill`：<https://api.skillhub.cn/api/v1/skills/govwriter-skill>
- `govwriter-pro`：<https://api.skillhub.cn/api/v1/skills/govwriter-pro>
- `official-writing`：<https://api.skillhub.cn/api/v1/skills/official-writing>
- `gov-doc-writing`：<https://api.skillhub.cn/api/v1/skills/gov-doc-writing>

## 81 个搜索结果类型分布

按主功能单归类：

| 类型 | 约数量 | 高分代表 |
| --- | ---: | --- |
| 排版 / docx / 文档转换 | 43 | `gongwenformat-pro`, `doc-format`, `gov-doc-format`, `official-doc-writer`, `official-writing`, `doc-format-gw` |
| 写作 / 改写 / 重构 | 18 | `official-document-skill`, `govwriting`, `govwriter-pro`, `official-document-writer-skill`, `chinese-official-writing` |
| 审校 / 质检 / 校对 | 7 | `docformat`, `plan-proofread`, `ifly-text-proofread`, `iflytek-text-proofread`, `quality-pipeline` |
| 检索 / 政策依据 / 知识库 | 5 | `govwriter-skill`, `nathan-legal-os-pro`, `dknowc-search`, `zhiqi-docx`, `xingqingbaoanalysis` |
| 多 agent / 流程编排 | 2 | `quality-pipeline`, `mdt-consultation` |
| 泛办公 / 其他弱相关 | 6 | 秘书、办公自动化、翻译、PDF 转换、通用写作方法等 |

补充观察：按功能标签可重叠统计，排版/docx 约 66 条，写作/重构约 54 条，审校/质检约 18 条，检索约 15 条。SkillHub 高分公文生态的主流优势集中在 Word/docx 交付与格式工具，不是单纯“更会写正文”。

## 最值得最小借鉴的 5 个机制

1. **显式区分“写正文”和“交付 Word/docx”**  
   来源：`gongwenformat-pro`、`doc-format`、`official-doc-writer`。  
   最小吸收：只补排版交付前核对，不引入脚本：内容是否定稿、是否另存、不覆盖原文件、缺文号/签发人/印章不代填、Markdown 痕迹清除。

2. **抽象词必须落到具体事实或动作**  
   来源：`official-document-skill` 的 fact density、abstract-word control、paragraph function。  
   最小吸收：并入质量建议层；凡出现“提升、强化、推进、赋能、闭环、机制”等抽象词，后面应接对象、动作、责任、时限、数据或制度载体。

3. **评价强度与证据强度匹配**  
   来源：`official-document-skill` 对“初步见效、明显成效、形成机制”等表达的证据约束。  
   最小吸收：没有数据、制度、流程或稳定运行证据时，少用“显著、全面、根本、长效机制”等高强度判断；作为质量建议，不做硬清洗。

4. **联网检索后的依据清单**  
   来源：`govwriter-skill` 的政策检索阶段。  
   最小吸收：不扩大默认联网；仅在用户明确要求搜索或涉及时效政策时，正文外增加“依据来源清单：名称、发布机关/文号、发布日期、用于哪一段、是否已核验”。

5. **创作模式与修改模式的素材处理差异**  
   来源：`govwriter-pro` 区分修改模式和创作模式。  
   最小吸收：当前技能已有模式路由，可补一句：修改模式不得把旧版本或外部参考材料带回最新版；创作模式才可把提纲、过往材料、公开依据转成初稿素材，并标明待确认事实。

## 不应吸收的 5 点

1. 不吸收重脚本、字体安装、COM、LibreOffice 依赖。当前技能定位是写作与复核，不变成 docx 生成器。
2. 不把联网搜政策、新闻、案例作为默认流程。默认联网会污染用户材料边界。
3. 不在每次模式判断后强制暂停确认。普通顺稿、压缩、小改应保持轻量。
4. 不引入一键格式清洗、标点硬清洗、统一模板化。它可能破坏真实模板、字段式申请、附件关系。
5. 不引入大模板库、法律/合同/RAG 知识库或多 agent 流水线作为默认能力。超出“公文写作辅助”边界。

## 1.4.4 最小候选改动

- 在 `workflow.md` 强化缺项和正文边界：没有给出的截止时间、联系人、反馈渠道、政策依据不得写成正文事实或泛占位。
- 在 `workflow.md` 强化字段/单元边界：新增字段只写字段名或用户给定值，不自填字段内容；字段顺序默认按用户原顺序，新增字段放在相邻语义位置或用户指定位置。
- 在 `workflow.md` 强化限字压缩：先列不可丢要素，再压缩重复和低信息过渡；限制字数必须真实执行。
- 在 `anti-ai-patterns.md` 或 `official-style.md` 增加抽象词落地和评价强度匹配证据。
- 在 `format-gbt9704.md` 增加 docx 交付前核对，不引入排版脚本。
