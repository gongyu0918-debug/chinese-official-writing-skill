# 最小修复门禁与工作流防漂移记录

日期：2026-07-13

## 结论

本轮按“先测试后修、本地提交”执行，只新增可追溯测试证据，不修改产品 Prompt、任务路由、reference 加载条件、输出模式、三级复核顺序、脚本或发布元数据。

36 份隔离 Codex 样稿没有 FAIL。两名独立 verifier 均确认：混合公文/论文路由、证据状态和输出结构没有形成三次以上共性失败；稀疏论文提纲存在跨章节重复铺陈的共同 WARN。由于三名 writer 的精确模型 ID 均为 `unavailable`，该共同 WARN 不具备产品修复资格。本轮不授权修改产品 Prompt，不为形成版本制造改动。

## 固定基线与边界

- 发布基线：`v1.5.7=d3755df7deb2456150c61ccb1944aa3982f7edf1`。
- 论文扩展前基线：`11a80be6c43460572cf0d0d3a19158a80f74fd41`。
- 本轮测试基线：`aaba577b9924710a92625c5044086efd7308f128`。
- 三个基线均为当前 HEAD 祖先；测试开始时工作区无跟踪改动。
- 不使用 MiniMax；不升版本、不推送、不发布，不同步 Red SkillHub 副本。
- 保持“由大至小组织、事实和引用可追溯、由小至大复核”的现有内核，不新增生成器、finalizer、检测器、硬清洗、默认联网、默认多 Agent 或强制确认。

## 模型可追溯性

三个独立 writer 均在输出文件头部报告 `MODEL_ID: unavailable`。当前 collaboration 子 Agent 接口不提供模型选择或精确 model ID；本机 `codex --version` 也因 WindowsApps 可执行文件“拒绝访问”而无法建立外部精确模型入口。

因此本轮三次运行只能作为 Codex sanity，不能标注为 `gpt-5.3-codex-spark`、`gpt-5.4` 或 `gpt-5.5`，也不能计入需要精确模型的产品修复门槛。

## 测试设计与原始证据

四组共 12 个未见真实用户式 prompt，每名 writer 独立完成全部 12 题，共 36 份输出：

1. `M1—M3`：论文主题通知、论文归档报告审稿、公文语言课程论文，检查最终交付物路由。
2. `E1—E3`：`未提供/未披露`、主观反馈和未形成结论，检查证据状态保真。
3. `S1—S3`：压缩时保留原标题/主送/落款，以及用户明确删除结构时服从用户。
4. `O1—O3`：稀疏材料三级提纲和固定四章模板，检查虚构与模板膨胀。

原始文件：

- `tests/evidence/minimal-fix-gate-20260713/prompts.md`
- `writer-a.md`、`writer-b.md`、`writer-c.md`
- `judge-1.md`、`judge-2.md`

Writer A 的 Markdown 行尾硬换行空格清理由 `e25c8d7`、`77410c7` 两个本地 evidence-only commit 留痕。Writer B 在纳入 Git 前作同类 whitespace 规范化，没有保留可独立比较的版本化前态，因此本文件只把 Writer B 视为文字、标点和顺序可复核的语义原文，不声称逐字节一致。Writer C 无需处理。

两名 verifier 只读取上述 prompt 和匿名输出，不读取 skill、仓库代码、历史 evidence、预期修复或对方结论。统一门槛为：同一语义问题至少出现在 3 份输出、2 个不同 prompt、2 名 writer 中；精确模型 ID 不可用时，固定 `eligible_for_product_fix=false`。

## 双 verifier 结果

| 分组 | Verifier 1 | Verifier 2 | 交叉结论 |
| --- | --- | --- | --- |
| 混合路由 | 8 PASS / 1 WARN | 9 PASS | 路由均正确；仅一份通知把落款“校教务处”缩为“教务处”，未形成共性。 |
| 证据状态 | 8 PASS / 1 WARN | 8 PASS / 1 WARN | 两人均只警告 Writer A 的 E3：`未披露` 被写为 `尚不明确`；仅 1 份。 |
| 输出结构 | 9 PASS | 9 PASS | S1/S2 均保留既有正式结构，S3 均按用户要求删除。 |
| 稀疏论文提纲 | 9 WARN | 2 PASS / 7 WARN | 无虚构结果；两人共同确认 O2、O3 的稀疏事实跨章重复。 |
| 合计 | 25 PASS / 11 WARN / 0 FAIL | 28 PASS / 8 WARN / 0 FAIL | 总体 WARN，非阻断。 |

双方一致确认的表面共性语义问题是稀疏提纲跨章节重复；Verifier 1 使用代码 `OUTLINE_TEMPLATE_BLOAT`，Verifier 2 使用代码 `TEMPLATE_BLOAT`。O2、O3 在三名 writer 中均把少量事实或缺口重复铺入材料、结果和结论等章节，共 6 份输出、2 个 prompt、3 名 writer。Verifier 1 另将 O1 三份也记为同类 WARN。

该问题达到输出数量门槛，但没有精确模型 ID，故：

- `threshold_met=true`（仅 sanity 计数）；
- `eligible_for_product_fix=false`；
- `product_prompt_change_authorized=false`。

## 产品文件防漂移

本轮不修改 canonical 或镜像产品文件。测试基线的关键 SHA-256 为：

| 文件 | SHA-256 |
| --- | --- |
| `chinese-official-writing/SKILL.md` | `913738916F69F6AD849D526CFD24049F4C6E80642C56D7168EA8D16AD1BD1A85` |
| `references/academic-writing.md` | `39CF183585195AD5CF4DAE1C9D1F08689064BFEB320E4D9D093179D43DF5EDCA` |
| `references/anti-ai-patterns.md` | `C5756646BA87973A6325A70C9BE331586857F5AC14062B35E4244F60344A64B9` |
| `references/review-checklist.md` | `EA334AE34AA7AA376C818B14CCE0683BB4663BBC07998206326FD04A42C21214` |
| `references/final-review-layers.md` | `62EA50A3F69289261B0EBCC8AD89872F37302FCD5E35D73BBA1609BC656A8CAA` |

当前流程仍为：论文任务先进入 `academic-writing.md` 叶子，公文任务仍按原文种与办理关系处理；没有增加“按最终交付物判路由”句，没有修改“只输出正文”的现有规则，也没有加入证据状态或论文提纲新规则。

## 工程验证

- `python -B -m unittest discover -s tests -v`：144 tests，OK。
- `python -B tools/run_real_prompt_ablation.py --baseline-root output/release-baselines/github-1.5.7-paper ...`：baseline 102/111，current 111/111。
- `python -B tools/run_real_prompt_ablation.py --baseline-root output/release-baselines/local-11a80be-paper ...`：baseline 103/111，current 111/111。
- `npm run eval:official-writing:smoke`：20/20 PASS；当前使用确定性 stub，只作工程回归，不作为真实写作质量或模型胜率证据。
- Skill `quick_validate.py`：`Skill is valid!`。
- 完整评测分组最大上下文：`MAX_CONTEXT=24910`，仍低于仓库 `<25000` 门槛。
- `git diff --check`：通过。

## 后续触发条件

只有取得可记录的精确 Codex 模型入口，并用至少两次 Codex Spark 与一次强 Codex 对同类未见 prompt 复测后，才重新判断“稀疏提纲跨章重复”是否具备修复资格。若届时仍达到门槛，下一步只评估 `academic-writing.md` 中一条“稀疏材料不为凑标准章数跨章重复”的候选句，并单独与 `aaba577` 做真实 A/B；不得同时修改混合路由、证据状态或输出结构。
