# 二次修改链路风险收敛实验

## 结论

本轮按“双层方案”完成 12 类新 holdout、Luna 低/中思考真实写稿、三种用户触发 prompt 候选、Luna/GPT-5.5 repair、确定性不变量检查和 GPT-5.5/GPT-5.6 Sol 双盲复核。

最终不修改 canonical `SKILL.md`、references、`prose_lint.py` 或正式评测入口：

- B 的三种最小 prompt 候选均在第一轮出现回退，达到停止条件。
- C1（Luna 修订）未优于当前二修链路。
- C2（GPT-5.5 修订 + fail-closed）第一轮减少 3 个 FAIL，但第二轮仅持平或轻微减少 WARN，未满足“连续三轮稳定优于 B”。因此按验收规则提前停止，不运行第三轮，也不下沉宿主实现。
- 当前最可靠的交付方式仍是现有 skill 的用户自然语言二次修改；宿主快照可保证精确回滚，但自动检测和强模型 repair 只能作为实验性可选层，不能宣称已解决旁白、事实外扩和情态漂移。

## 基线与实验隔离

- 实验起点：`afc85dcfecb80d294f12ca8e92d8fa28ce756c3e`
- 实际发行基线：tag `v1.5.6`，`7e485700a49a924abf973656d2bb0e9630054890`
- 原型、稿件、detector、contract、repair 和 verifier 输出均位于 `.gitignore` 覆盖的 `output/finalizer-experiments/attempt5/`。
- 两个 subagent 曾对 ignored 输出强制暂存，产生 `55edc71` 和 `5f2a214`；随后 `660eae4` 从当前索引移除这两项并保留本地实验文件。当前发行树不包含 attempt5 输出。
- 没有 bump 版本、tag、push 或三平台发布。

## 12 类 holdout

1. 600-800 字稀疏阶段报告。
2. 900-1100 字抽样调研报告。
3. 3000-3300 字多附件可研。
4. 拟办和未决会议纪要。
5. 固定字段与空字段申请。
6. 引语逐字保护和普通叙述正式化。
7. 只审不改。
8. 只输出正文。
9. 定点时间与截止时间区别。
10. 部分、抽样与全部检查区别。
11. 原因、责任、影响、成效和程序外扩。
12. 多轮精确回滚和回滚后单点修改。

每轮 Luna 对每类生成 3 个独立首稿，共 36 篇。writer 不读取候选规则、评分标准或 verifier 结果。

## B：用户触发 prompt 候选

### v1：完整二修边界

v1 明列锁定项、局部修订、旁白删除条件、事实外扩、情态恢复和回滚要求。结果出现规则反向泄露和过度压短：

| 组别 | 通过 | 泄露 | 不变量失败 | 禁用表达 |
| --- | ---: | ---: | ---: | ---: |
| A 当前二修 | 27/36 | 0 | 12 | 2 |
| B-v1 | 27/36 | 4 | 15 | 1 |

Sol 盲审：A `27 PASS / 9 FAIL`，v1 `22 PASS / 5 WARN / 9 FAIL`，偏好 A 15、v1 8、平局 13。GPT-5.5 判两组均为 `24 PASS / 3 WARN / 9 FAIL`，没有稳定优势。v1 拒绝。

### v2：静默局部修订

v2 缩成“内部锁定、保持有效内容和篇幅、恢复材料原词、快照回滚”四项。确定性指标恢复到 A，并把禁用表达降到 0，但两名 blind verifier 一致发现 R12 精确回滚被改坏：

- GPT-5.5：v2 `24 PASS / 12 FAIL`，A `27 PASS / 9 FAIL`。
- Sol：v2 `22 PASS / 2 WARN / 12 FAIL`，A `27 PASS / 9 FAIL`。

v2 拒绝。

### v3：只约束精确回滚

v3 只要求“以上一版本为底稿做字面替换，其他字符不变”。两名 blind verifier 仍一致判定：

- A：`27 PASS / 9 FAIL`，R12 `3/3 PASS`。
- v3：`24 PASS / 12 FAIL`，R12 `0/3 PASS`。

模型仍重新生成标题、称谓、换行或字段格式，说明精确回滚不能靠 prompt 保证。三种 prompt 方案全部失败后停止尝试，canonical 不修改。

## C：宿主检测和一次 repair

### 第一轮：Luna 低思考

首稿 36 篇：`27/36` 确定性通过，4 个泄露 finding、15 项不变量失败、6 个禁用表达。独立 GPT-5.5 detector 另标 12 条高风险语义 finding。

- C1 Luna 修订：`27/36`，2 个泄露、14 项不变量失败、0 个禁用表达。相对 A 新增泄露和不变量失败，拒绝。
- C2 GPT-5.5 raw：`27/36`，4 个泄露、9 项不变量失败、0 个禁用表达。不能整组保留。
- C2 fail-closed：只接受确定性通过且两名 verifier 均 PASS 的 27 篇，拒绝并字节级回退 9 篇。最终确定性指标与 A 相同。

全新 cold verifier 结论：

| Verifier | A | C2 fail-closed |
| --- | --- | --- |
| GPT-5.5 | 24 PASS / 12 FAIL | 27 PASS / 9 FAIL |
| GPT-5.6 Sol | 21 PASS / 3 WARN / 12 FAIL | 26 PASS / 1 WARN / 9 FAIL |

第一轮 C2 减少 3 个严重失败，无 C 独有严重回退，允许进入第二轮。

### 第二轮：Luna 中等思考

首稿 36 篇：`28/36` 确定性通过，但有 21 个泄露 finding。独立 detector 另标 25 条高风险语义 finding。

- A 当前二修：`27/36`，11 个泄露、9 项不变量失败。
- C2 raw：`28/36`，0 个泄露、8 项不变量失败。
- 语义筛选发生分歧：GPT-5.5 判 raw C2 少 1 个 FAIL，Sol 判 raw C2 多 1 个 FAIL。
- fail-closed 只接受双方均 PASS 的 23 篇，拒绝并字节级回退 13 篇；最终确定性指标与 A 相同。

全新 cold verifier 结论：

| Verifier | A | C2 fail-closed |
| --- | --- | --- |
| GPT-5.5 | 26 PASS / 1 WARN / 9 FAIL | 27 PASS / 9 FAIL |
| GPT-5.6 Sol | 27 PASS / 9 FAIL | 27 PASS / 9 FAIL |

第二轮没有减少 FAIL，Sol 判完全持平。C2 未满足“稳定优于 B”，按计划停止，不运行第三轮 GPT-5.5 矩阵。

## 工程验证

- attempt5 原型单测：`7/7` 通过，覆盖 12 类 case、contract 字段、host brief、情态/范围不变量、只审不改、字节级回退和快照恢复。
- 两轮共生成 72 篇 Luna 首稿；A、C1/C2 修订均使用独立 subagent，上下文隔离。
- 所有 fail-closed 拒绝稿均恢复 base 文本，第一轮 9/9、第二轮 13/13 字节一致。
- attempt5 输出不在 `git ls-files` 中，不进入 canonical 包。
- `python -B -m unittest tests.test_revision_instruction_eval tests.test_skill_boundary tests.test_review_regressions tests.test_real_prompt_ablation tests.test_promptfoo_eval -v`：`123/123` 通过。
- `python -B -m unittest discover -s tests -v`：`123/123` 通过。
- v1.5.6 确定性消融：release `101/102`，current `102/102`；release 只失败于后续已有的 P046 窄修复。
- `python -B tools/run_revision_instruction_eval.py`：生成 12 case、36 turn task packet；默认模式未调用 agent，不能替代上方真实 subagent 二修矩阵。
- `python -B tools/run_real_article_eval.py`：skill 关键要素 `61/61`、关键词命中 `100%`、格式/重复/ANTI-AI 风险为 0；9 个样本共 16 个占位词命中继续按人工风险解释。
- Promptfoo smoke：`20/20`，skill win rate `1.0`，judge consistency `1.0`。
- `tools/sync_adapters.py` 同步成功且无镜像 drift；`quick_validate.py chinese-official-writing` 通过；`git diff --check` 通过。

## 保留能力与剩余风险

保留：

- 当前 `SKILL.md` 已有的事实映射式二次修改和 `task-route-cards.md` 二次局部修改入口。
- 用户指出问题后的自然语言二修，可继续用于删除补造内容、恢复材料口径和清理格式。
- 宿主以 SHA/base64 快照执行精确恢复；回滚后再做单点修改时由宿主直接处理文本版本，不要求模型回忆原稿。

不保留：

- 三种 candidate prompt。
- Luna repair C1。
- GPT-5.5 repair C2 的产品化路由、自动承诺或发行依赖。
- 第三方框架、embedding API、默认联网、语义清洗脚本或自动全文重写。

剩余风险：稀疏材料和长文的篇幅稳定性、正文旁白和约束泄露、原因/责任/程序外扩、范围与情态漂移、verifier 判分漂移。宿主 C2 在单轮可降低风险，但跨轮次未稳定优于当前链路，只能作为后续研究方向，不能宣称已解决。
