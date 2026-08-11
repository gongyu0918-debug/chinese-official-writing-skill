# LUNA / TERRA 历史 harness 与当前质量漂移预注册

## 目的

以新一代模型为主，先用原生 Skill 与无 Skill 的同题写作判断当前 1.5.14 是否在整体写稿观感、事实保真、文种功能和直接可用性上出现质量漂移；再用配套 harness 解释 1.2.x 历史组合可能获得的额外增益。字数只作为硬要求之一，不作为唯一质量指标。

harness 只用于历史诊断。它提供的分阶段调用、独立审校、返修次数和运行轨迹均属于外部 agent 能力，不能写成 Skill 本体能力，也不能作为当前 Skill 的发布通过依据。产品结论、修复触发和发布判断只采用 N、S152、S153、S514 等原生条件；这些条件必须在没有 harness 的情况下独立成立。

## 模型与任务

- writer 主模型：`gpt-5.6-luna`、`gpt-5.6-terra`，medium。
- 第一轮任务：T02 多材料情况报告、T04 未决事项会议纪要。
- 第二轮任务：第一轮保留下来的条件继续跑 T01 长篇阶段报告、T03 稀疏异常报告。
- 每个 writer 条件使用独立上下文，不读取其他条件输出、盲审标准、映射或阶段结论。

## 固定条件

| 条件 | 说明 | 目的 |
| --- | --- | --- |
| N | 无 Skill、无 harness | 固定新模型自身能力基线 |
| H | harness-only | 隔离 harness 自身贡献和过度 Prompt 风险 |
| H125 | harness + 1.2.5 compact Skill | 重建早期轻量 Skill 组合 |
| H129 | harness + 1.2.29 compact Skill | 重建 1.2.x 末期组合 |
| S152 | 原生 1.5.2 Skill | 1.5.3 前版本断点 |
| S153 | 原生 1.5.3 Skill | 1.5.2→1.5.3 漂移候选 |
| S514 | 原生 1.5.14 Skill | 当前发行基线；使用与严格 N 相同宿主外壳、仅输入原始任务并自然触发的直写稿。旧受控 writer 稿只作诊断，不进入主排名 |
| H514 | harness + 1.5.14 compact Skill | 判断 harness 的分阶段组织能否改善当前原生 Skill |

LUNA 的当前 full-route 稿只作诊断旁证，不进入上述主排名，因为 TERRA 没有同条件对应稿。

主对照为 N、S152、S153、S514。H、H125、H129、H514 单列为历史机制诊断，不与原生条件合并排名，也不用于证明 Skill 优于无 Skill。

## harness 来源与重建边界

- 来源仓库：`gongyu0918-debug/official-writing-agent-community`。
- 固定快照：`d86eec2`；其写作链与导入提交 `f43f218` 相同。
- Git 历史只有 2026-06-24 的私有基线导入和一次斜杠命令提交；内置 Skill 为 1.4.7，仓库本身不能证明 1.2.x 当时使用的精确 harness commit。
- 1.2.x 条件通过 `OFFICIAL_WRITING_SKILL_ROOT` 所代表的外部 Skill 替换方式重建，明确标为“现存 harness 快照 + 历史 Skill”，不冒充无法复核的原始运行包。

## harness 诊断执行方式

LUNA / TERRA 无法从本地 harness 的 HTTP provider 直接调用，因此按源码阶段边界在独立 App 上下文中复现：

1. outline writer：使用 `WRITER_SYSTEM`、`USER_TEMPLATE_OUTLINE` 和相应 compact Skill bundle 生成提纲。
2. outline reviewer：新的同模型独立上下文，只使用 `OUTLINE_REVIEWER_SYSTEM` 审核提纲；只处理文种、跑题、核心要求遗漏。
3. draft writer：新的同模型独立上下文，使用通过或修订后的提纲、`USER_TEMPLATE_DRAFT` 和同一 bundle 起草正文。
4. final reviewer：新的同模型独立上下文，只使用 `FINAL_REVIEWER_SYSTEM` 做阻断审校。
5. 最多一次 revision writer；仍不通过则记录 `needs_human_review`，保留原始失败，不循环修到通过。

H 条件不加载 Skill bundle；H125、H129、H514 按 `app/skill/loader.py` 的现存选择结果加载。所有阶段保留 prompt、模型、thread、原始输出和修订链。

上述步骤只复现外部 agent 的运行方式。Skill 本体不具备创建独立上下文、指定 reviewer、控制调用轮次或命令宿主 agent 的权限。若 harness 组显示增益，只把结果拆回同一上下文可执行的方法候选，例如起草前形成内部事实覆盖框架、写后核对事实状态与主体宾语、按文种检查结论强度；候选仍须在原生 Skill 条件中单独 A/B，确认无回退后才可考虑采用。

## 已知 harness 风险，评测前固定

1. `_target_words` 当前不能识别 `1300—1600 字`、`900—1100 字` 这类区间，第一轮不修正，忠实记录其对原任务的实际表现。
2. 无上传附件时，inline prompt 中出现“报告”会命中 `low_fact_report`；当前 loader 只选 `formal-addressing.md` 后返回。T04 材料中的“信息中心报告”也会触发该分支。
3. 1.2.5 没有 `formal-addressing.md`，现存 loader 实际为 252 字 Skill 摘要、0 reference；1.2.29 为 533 字摘要加该 reference。harness Prompt 的影响可能大于历史 Skill 增量，因此必须保留 H 条件。
4. harness 自身包含大量事实禁补和省略规则；若 H 与 H125/H129 结果接近，不能把差异归功于 Skill。

## 盲审维度

盲审只看原任务与匿名成稿，不看条件名。每稿给 PASS/WARN/FAIL，并给出相对无 Skill 的 `优于 / 相当 / 低于` 结论。原生组和 harness 诊断组分别汇总；只有原生组进入产品判断。

1. 显式事实、数字、日期和未决状态是否完整、准确。
2. 是否新增原因、效果、职责、会议意见、会议要求或后续动作。
3. 文种功能、标题、层级、行文视角和输出模式是否可直接使用。
4. 信息组织是否自然，开头、主体、后半篇和结尾是否均衡，有无头重脚轻或机械拼接。
5. 结论强度是否与材料一致，保护性说明是否压过正文。
6. 动作主体、宾语、对象和指代是否完整清楚。
7. “先……再……”“先行……后……”是否有真实顺序依据，是否同稿成簇重复。
8. 总体观感、人工修改成本和直接采用意愿。

机械字数和句式计数只供盲审定位，不参与自动加权，也不替代整体判断。

## 集中修复门槛

- 原生 S514 相对 N 的同一风险跨 3 个任务，或在 LUNA、TERRA 两个模型中稳定出现，才进入产品修复。harness 组的结果不能单独触发产品修改。
- 只有 H125/H129 相对 H 出现可复现增益，才把增益记为历史 Skill 与 harness 的组合线索。H514 相对 S514 的改善也只产生方法候选；候选必须改写为 Skill 同一上下文可执行的软性方法，并在原生 Skill 对 N 的 A/B 中证明有益且无事实、文种、格式或输出模式回退。
- 修复按共因处理：优先调整上下文结构、规则优先级、正向事实展开方法或审稿关注点，不追加单句禁令和固定替换表。
- 当前版若在任一硬边界上低于 N，先记录为发布风险；修复后必须重新与 N、S152、S153 和修复前 S514 盲比。
