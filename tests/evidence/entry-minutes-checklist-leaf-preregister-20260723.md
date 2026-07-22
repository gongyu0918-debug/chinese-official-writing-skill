# 会议纪要检查项原子叶子拆分验证（2026-07-23）

## 固定边界

- Candidate 起点：`f22a472`；Baseline 固定为该提交的只读副本。
- 单一变量：把 `genre-checklist.md` 中现有“会议纪要”小节逐字迁入独立的 `genre-checklist-minutes.md`，并把 `SKILL.md` 与 `genre-playbooks.md` 的纪要指针改到新叶子。
- 不增删或改写会议纪要规则，不调整事实边界、文种骨架、任务路由、输出模式、复核顺序、修改次数、脚本门禁和发布链。
- 该原子用于验证按文种缩小实际加载内容能否保持或增强指令遵循；不把字符减少本身当作写作质量提升。

## 加载对照

| 场景 | Baseline | Candidate |
| --- | --- | --- |
| 完整会议纪要 | `SKILL.md` + `genre-playbooks.md` + `genre-checklist.md` 纪要小节所在整文件 | `SKILL.md` + `genre-playbooks.md` + `genre-checklist-minutes.md` |
| 其他文种细查 | `genre-checklist.md`（含纪要小节） | `genre-checklist.md`（不含纪要小节） |
| 材料稀疏且完整命中轻卡 | `task-route-cards.md` | 不变 |

## 精确 diff 计划

1. 新建 `references/genre-checklist-minutes.md`，只承载原纪要检查项。
2. 从 `references/genre-checklist.md` 删除相同小节，不改相邻文种内容。
3. 更新 `SKILL.md` reference 表和 `genre-playbooks.md` 的补充读取指针。
4. 更新评测 provider，使完整会议纪要测试显式加载新叶子；稀疏未决纪要仍走原轻卡。
5. 增加镜像、路由和逐字迁移边界测试，同步发行镜像。

## 不修改的文件和能力

- `information-selection.md`、`workflow.md`、`task-route-cards.md`、`review-checklist.md`、`final-review-layers.md`、`proofreading-checklist.md`、`anti-ai-patterns.md`。
- 事实、数字、主体、责任和状态强度；用户模板与输出范围；长文提纲和篇幅预算；Word 交付；审稿模式；有限修改和回退机制。

## 测试预注册

1. 工程门：定向单测、全量 unittest、固定基线确定性消融、Promptfoo smoke、quick validate、镜像一致性和 `git diff --check`。
2. T01 完整会议纪要：材料包含会议时间、地点、主持人、参会主体、两项明确议定事项、责任单位和期限；检查是否保持议定事项、责任和期限绑定，不写成会议新闻。
3. T02 非纪要对照：普通通知或报告任务；检查拆分后是否误读纪要叶子，正文质量不得回退。
4. Candidate 与 Baseline 使用逐字一致自然语言输入、同模型和同 thinking，各取首个技术有效输出；写稿与匿名盲审使用独立上下文。

## 验收

- 两题均无 Candidate 独有的事实、数字、日期、主体、状态、文种、格式、篇幅或输出模式回退。
- T01 的纪要功能和直接修改成本不低于 Baseline；T02 至少持平。
- PASS 时保留；任一 Candidate 独有硬回退时完整撤回产品改动，仅留失败证据。

## 工程结果

- 机械拆分后，通用 `genre-checklist.md` 的规范化字符数由 3,388 降至 3,277，减少 111；新纪要叶为 112 字符。为保持从入口直接可达，`SKILL.md` reference 表增加 44 个规范化字符。
- 首次全量 unittest 出现 31 个失败，全部来自旧 provider 测试仍断言完整纪要只加载 playbook；更新该路由契约后仍有 2 个旧断言遗漏，修正后全量 357 项通过。两次失败均为测试预期未同步，不是写作或产品错误。
- 固定基线确定性消融：Baseline 108/108，Candidate 108/108。
- Promptfoo smoke：20/20 通过，0 failed，0 errors，Skill 10 胜，一致性 1.0。
- quick validate 和 `git diff --check`：通过。

## 真实 A/B

模型与推理档位均为 `gpt-5.6-sol` / `ultra`，同题逐字一致，各取首个技术有效输出。

| 任务 | Candidate SHA-256 | Baseline SHA-256 | 匿名结果 | 硬回退 |
| --- | --- | --- | --- | --- |
| T01 完整会议纪要 | `5B1FBA9055A60CCD0DFF7C26EE6E196EDF82061594CA77F583210902E1FEBF44` | `511B7BA339695FF2511BA8A81A2DAD879CD40485FF83CD7D69D9A959D38BBA60` | 难分 | 无 |
| T02 普通通知 | `867C128915E4FF5B769ABA09EEB1830481C26AEB79DFBB3950B13C1EECCAB18E` | `C892FCA9A1F5E0ED6CA88994190B9235096D3A1D80D142E793F3A72EF72B2642` | Baseline 胜 | 无 |

T01 两条件除纪要检查项来源不同外，实际读取路径一致；纪要功能未见回退。T02 两条件实际读取路径完全一致，盲审差异很可能包含模型采样噪音，但预注册要求非目标文种至少持平，不以事后解释放宽。

## 结论

结果为 **FAIL**。会议纪要专用叶和 provider 路由全部撤回，产品回到 `f22a472`；只保留本证据。该实验不支持当前以“新增入口指针换取小型 reference 拆分”的方案，后续优先选择不增加入口说明的去重或既有叶子内拆分。
