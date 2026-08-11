# 结构化约束包与 span-only finalizer 实验

## 结论

本轮完成了“结构化约束包 -> 模式感知检测 -> 独立 claim verifier -> 一次局部 span patch -> 不变量复核 -> 精确回滚”的宿主层原型，但 **不将 finalizer 提升到 canonical skill、reference、正式测试或发行包**。

原因不是原型无法运行，而是 C 组未稳定优于 B 组。两名 blind verifier 均发现 A、B 和 GPT-5.5 复测仍有严重问题；repair subagent 提出的 2 个共识安全 patch 在重新验证后仍不能使对应稿件整体通过，因此全部拒绝。最终 C 的 24 篇输出与 B 字节级一致，没有把失败修订留在正文中，也没有修改 `SKILL.md`、references 或 `prose_lint.py`。

## 固定状态

- 当前分支：`codex/release-1.5.6`
- A，实际发行版 `v1.5.6`：`7e485700a49a924abf973656d2bb0e9630054890`
- B，pre-experiment HEAD：`8a0144d1f359e3f77e1c1618f87a06b79e5d7f4d`
- `origin/main`（实验开始时）：`48b8610aa7aac0e0ac6e10be21ea9749a2aa9d15`
- 用户计划中记录的 `d6414a3d9cef8bc2ac191402eae05a509816ba7b` 并非当前仓库实际 `v1.5.6` tag 指向，实验以 Git tag 实测值为准。
- A 基线用 detached worktree 固定在 `output/release-baselines/github-1.5.6`。
- 原型及正文均位于被忽略的 `output/finalizer-experiments/attempt4/`，不进入安装包。

## 原型架构

`constraint_pipeline.py` 实现以下实验能力：

1. 从原始任务和材料提取 `source_claims`、`locked_literals`、`modal_scope`、`locked_structure`、`delivery_contract` 和 `forbidden_inferences`。
2. 按 `draft-body`、`review-only`、`gap-note-allowed` 区分材料状态说明、模型自述、写作过程和约束复述；只输出 JSON finding，不自动删句。
3. verifier packet 要求 claim 逐项返回正文位置、判断类型及原文支持片段，不用总分覆盖单项严重错误。
4. repair 只接受精确、不重叠的 span patch；删除仅限 verifier 确认不承载用户事实的 `pure_meta` 片段，不允许全文重写。
5. patch 后重新检查引语、数字、日期、单位、情态、标题、字段顺序、篇幅和泄露项。任一项失败即丢弃修订稿并恢复首稿。
6. 首稿、finding、patch、候选稿和 SHA-256/base64 快照分别保存；回滚不依赖模型记忆。

原型单测覆盖模式感知、引语/数值/情态保护、span 边界、重叠 patch 拒绝、纯旁白删除条件、字节级恢复，以及“拟/已、抽样/全部”等反事实变形，共 `13/13` 通过。

## 20 篇标注校准

从用户提供的最新 20 份审校 ZIP 中提取 80 条 finding，再由独立 GPT-5.5 校准：

- 接受：22
- 部分接受：39
- 拒绝：19
- 与本轮三类风险直接相关：旁白或约束泄露 7，事实或责任外扩 5，范围或情态 6
- 其余语言、格式和软件包装类线索：62

多条“旁白”实际来自审校报告页眉、页脚或包装文本，不能直接当作正文泄露。审校软件继续只作线索，不直接形成固定替换表或硬清洗规则。

## 真实 A/B/C

holdout 共 10 类：600-800 字稀疏阶段报告、900-1100 字调研报告、3000 字以上多附件可研、口语正式化并锁定引语、未决状态会议纪要、固定字段和空字段、只审不改、只输出正文、多轮精确回滚、compact 后恢复与后续修改。

写稿侧使用独立 Luna writer 对 H01-H08 各跑 3 次，并用 GPT-5.5 对 H01-H08 各复测 2 次；writer 不读取判分结论。确定性结果如下：

| 组别 | 样本 | 整体通过 | 泄露 finding | 不变量失败 |
| --- | ---: | ---: | ---: | ---: |
| A：v1.5.6 + Luna | 24 | 15/24 | 41 | 14 |
| B：pre-experiment + Luna | 24 | 15/24 | 33 | 11 |
| B：pre-experiment + GPT-5.5 | 16 | 11/16 | 6 | 3 |

B 相比 A 的命中数量较少，但未达到发布级“泄露为 0、不变量 100%”门槛。主要失败包括：

- H01 多次低于 600 字，并偶有材料读取旁白。
- H02 第 2、3 轮把负向写作约束泄露进正文。
- H03 多轮出现“不补造供应商、技术参数”等约束自述，且篇幅不稳；派生比例和金额在严格 no-new-values 口径下不能自动认定安全。
- GPT-5.5 复测仍出现未给管理依据、后续建议、必要性或因果判断，以及长稿篇幅不足。

两名 blind verifier 分别使用 GPT-5.5 和 GPT-5.6 Sol，只接收原任务、材料和稿件。两者均判三轮 Luna A/B 及两轮 GPT-5.5 复测存在 FAIL，并一致认为只有 H02 的两个泄露句适合尝试窄 span 删除；H03 是否能安全局部修订存在分歧。

## C 组修订与回退

独立 GPT-5.5 repair subagent 只对两名 verifier 均认可的 B:H02-r2、B:H02-r3 给出精确删除 patch。结果：

- 尝试 patch：2
- 通过全部复核并接受：0
- 拒绝：2
- C 与 B 字节级一致：24/24
- 回滚 SHA 校验：全部一致

两个目标句即使删除，稿件仍有其他确定性失败，故没有把“局部看似正确”误判为可交付稿，也没有在坏稿上继续修订。该结果说明 span-only + fail-closed 架构可以限制伤害，但本轮还不能证明 finalizer 能提高最终通过率。

## 多轮与 compact 回滚

- H09：首稿 -> 修改截止时间并删电话 -> “回滚此次修改，恢复原样” -> 只把“内网表单”改为“OA 流程”。回滚与首稿逐字一致，后续修改只影响指定 span。
- H10：在新上下文只传快照和 SHA，先精确恢复 compact 前文本，再只将“8 月”改为“9 月”。恢复文本及 SHA 一致，后续修改未污染其他字段。

这证明宿主快照可以支持精确恢复；它不证明模型仅凭对话记忆即可稳定回滚。

## 回归与发布级检查

- `python -B -m unittest tests.test_skill_boundary tests.test_review_regressions tests.test_real_prompt_ablation tests.test_promptfoo_eval -v`：`110/110` 通过。
- `python -B -m unittest discover -s tests -v`：`123/123` 通过。
- `python -B tools/run_real_prompt_ablation.py --baseline-root output/release-baselines/github-1.5.6 --baseline-label release-1.5.6 --current-root . --out output/finalizer-experiments/attempt4/deterministic-vs-1.5.6`：A `101/102`，B `102/102`；A 仅失败于 B 后续已有的 P046 窄修复。
- `python -B tools/run_real_article_eval.py --out output/finalizer-experiments/attempt4/real-article`：skill 缺失率 `0%`，要素 `61/61`，关键词命中 `100%`，格式/重复/ANTI-AI 命中均为 `0`；16 个占位风险命中需人工按语境判断。
- `python -B tools/sync_adapters.py`：同步成功，tracked 内容无 drift；沙箱内首次因 `.agents` 权限失败，授权后重跑通过。
- `python -B C:/Users/admin/.codex/skills/.system/skill-creator/scripts/quick_validate.py chinese-official-writing`：通过。
- `npm run eval:official-writing:smoke`：沙箱内 Node 无法启动 Python provider，20 项均在评测前报环境错误；改用本机 Python 3.13 并在沙箱外运行同一 `run_eval.py --suite smoke --judge-batch-size 2` 后 `20/20` 通过，skill win rate `1.0`，judge consistency `1.0`。
- `git diff --check`：通过，仅有 Windows 换行提示。

## 决策与剩余风险

本轮不保留 finalizer，不修改 canonical prompt，不新增发行依赖，不发布新版本。保留的是实验方法和失败证据，避免后续重复尝试全文重写、通用 cleaner 或把确定性 lint 误当语义验证。

仍需记录的风险：

- 长文和稀疏材料中偶发材料读取旁白、英文思考残片或写作约束复述。
- 模型可能补入管理依据、原因、责任、成效、程序或后续安排；纯确定性工具不能完整识别语义新事实。
- “拟、尚未、部分、抽样”等情态和范围在改写中仍可能漂移。
- 600-800 字稀疏稿及 3000 字以上合稿的篇幅稳定性不足，修订时还可能重复凑字。
- claim verifier 目前依赖独立模型判断；在连续三轮真实 A/B 证明 C 稳定优于 B 前，不应下沉到发行包或承诺宿主自动调用第二个 agent。
