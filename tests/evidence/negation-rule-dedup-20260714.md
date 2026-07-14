# 否定规则去重与成品边界自证 A/B 证据

## 范围与门槛

- 固定当前基线为 `62ea0faf75455472838c011cfb6a2583023d102e`，候选只改 `SKILL.md`、`references/workflow.md`、`references/official-style.md` 中与结论强度有关的否定式反例；任务路由、reference 加载、三级复核、输出模式、事实和引用边界、默认联网、脚本行为及 Red SkillHub 归档均不变。
- 静态审查在三个运行时文件中归纳出 7 组语义重复。字段边界、文种边界、结构锁定、旧稿回流、过程泄露等重复承担不同场景职责，未删除。只有“风险、整改、检查、影响范围结论”一组与真实成稿中的边界自证问题相符，进入实测。
- 采用共性门槛：同一语义问题至少出现于 3 份输出、2 个不同 prompt、2 名独立 writer，并经两名 verifier 多数确认；任何事实状态、文种或输出模式回退均阻断候选。

## 候选改动

- 将 `材料未给……不自行写……` 加多组反例，改为“结论以材料明确内容为限；正文落到已确认问题及其对象、数量和状态；需要补充的口径按交付模式放正文外”。
- 将稀疏接口异常的否定清单改为“沿用用户对象和异常表述；正文承接已确认的时间、现象和操作记录；原因、影响、责任和处置保持材料当前状态”。
- 将 `official-style.md` 的强判断反例改为“强判断须有复查记录、运行数据、制度文件或责任闭环支撑；局部证据只支撑相应范围和强度”。
- 具体反例仍保留在按需审稿 reference、文种 playbook 和 lint 规则中，没有把事实边界整体删掉，也没有按否定词自动替换。

## 真实写稿 A/B

原 prompt 与匿名原稿见 `negation-rule-dedup-20260714-writing/`：

- S1：办公场所安全检查阶段报告，检验整改照片、待复核、风险等级和最终验收状态。
- S2：接口异常阶段报告，检验超时、恢复、28 名反馈用户、间歇性异常和待核验范围。
- S3：整改进展报告，检验 5 项现场复核、3 项在整和统一最终验收的区别。
- S4：平台试用评估报告，检验运行数据、3 周负载观察和 8 月评审议程。

匿名映射：

| 文件 | 版本 | writer session | 精确模型 |
| --- | --- | --- | --- |
| `R1.md` | baseline `62ea0fa` | `019f5fed-dde6-7ed0-82ec-25b4951a97f5` | `gpt-5.6-sol` |
| `R2.md` | baseline `62ea0fa` | `019f5ff2-94dd-7393-aaed-05a24c8067ec` | `gpt-5.6-sol` |
| `R3.md` | current candidate | `019f6002-a62d-7cc1-a8e9-25a35901a590` | `gpt-5.6-sol` |
| `R4.md` | current candidate | `019f6002-d1b1-7cf3-8461-f3340fccdd4e` | `gpt-5.6-sol` |

两名盲审 verifier 只看原 prompt 与 R1—R4，不看 Git、Skill、历史或版本映射：

| verifier | session | 精确模型 | 结论 |
| --- | --- | --- | --- |
| `verifier-1.md` | `019f600b-acee-7ee0-801d-ebb047e8dbd8` | `gpt-5.6-sol` | R3/R4 自证 0/0；R1 4、R2 29；候选必要状态完整 |
| `verifier-2.md` | `019f600b-e099-7d60-8bae-e35ca60512a7` | `gpt-5.6-sol` | R3/R4 自证 0/0；R1 5、R2 29；候选必要状态完整 |

两名 verifier 对一处句子的归类有 1 句差异，但共同确认：基线同类问题出现在 R1-S1、R1-S4 和 R2-S1 至 S4，共 6 份输出、4 个 prompt、2 名 writer；候选 8 份分稿均未出现该类保护性边界自证。四组都保留了现场复核后定结论、7 月 15 日核验、7 月 25 日统一验收和 8 月评审议程等必要业务状态，候选没有把阶段事实升级成最终结论。

候选 writer 的外层任务消息误写为使用 `## S1`—`## S4`，与 `prompts.md` 的 `=== S1 ===`—`=== S4 ===` 冲突，造成 R3/R4 一致的分隔符 WARN。该差异由测试夹具直接造成，不归因于产品 Prompt，也未据此修改产品。

## 派生统计风险复核

R3-S2 将不同异常类型合并计算总体恢复率，R3-S4 以覆盖用户数折算人均事项量；两名 verifier 均判为可能误导的 WARN。R4 未出现同类危险计算，基线 R2 也含多项正确但无必要的派生比例，因此首轮不能证明该问题由候选稳定诱发。

随后用相同 S2/S4 分别加载固定基线和当前候选，形成 `R5.md`、`R6.md`。该轮 writer 已看过首轮盲审，只记定向 sanity，不计为新盲样本。独立复核结果：

- R5/R6 均未再次计算跨异常类型的总体恢复率，也未用覆盖人数折算人均事项量，危险派生统计未稳定复现。
- R5-S4 有一次“后续观察情况将构成评审材料”的轻微程序扩写；R6-S4 有一次“跨部门协同运行记录”的轻微范围扩写。两项方向不同、各出现一次，均不构成候选独有的共性回退。
- 本轮不为单 writer 偶发 WARN 新增派生统计禁令，避免从一例一修扩展 Prompt。

本组全部 writer/verifier 的本地 `turn_context.model` 均核验为 `gpt-5.6-sol`，未使用 MiniMax。

## 工程与冷审证据

- `python -B -m unittest tests.test_skill_boundary tests.test_real_prompt_ablation -v`：53/53 通过。
- `python -B -m unittest discover -s tests -v`：152/152 通过。
- `python -B tools/run_real_prompt_ablation.py --baseline-root output\negation-ablation-20260714\baseline-62ea0fa --baseline-label baseline-62ea0fa --current-root . --out output\negation-ablation-20260714\candidate-ablation`：baseline 105/108，current 108/108；基线只在 P039、P046、P094 的新正向锚点守卫失败。
- `npm run eval:official-writing:smoke`：沙箱内首次 20 项均因 Node 无法启动本机 Python 报环境错误；放宽进程权限后重跑为 20/20 PASS，skill 10 胜，judge consistency 1.0。首次失败不计为产品失败，也未被写成通过。
- `python -B tools/run_real_article_eval.py --out output\negation-ablation-20260714\real-article-candidate`：skill 10 个样本缺失要素 0/61、关键词命中率 100%，格式风险、重复事项和反 AI 风险均为 0；占位标签仍只作人工线索。
- 完整数据集 27 批最大上下文 `24502`，低于仓库 `<25000` 门槛。
- canonical quick validate 通过，五个发行镜像与 canonical 一致，`git diff --check` 无空白错误。
- 独立 diff 冷审未发现 P0/P1/P2，确认路由、加载、三级复核、输出、事实、引用、联网和脚本行为未漂移，`publish_blocking=false`。

## 结论

候选达到共性问题修复门槛：目标问题在基线 6 份输出中复现，在两名候选 writer 的 8 份分稿中降为 0，必要业务状态全部保留。派生统计 WARN 未在候选第二 writer 或定向补测中稳定复现，不满足共性回退门槛。本轮保留该窄修复，作为 1.5.13 的新增候选；不新增自动替换、硬清洗、finalizer、默认联网、强制确认或新的写稿阶段。
