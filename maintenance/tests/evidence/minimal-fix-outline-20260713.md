# 稀疏论文提纲跨章重复最小修复

日期：2026-07-13

## 修复授权与基线

上一轮 `minimal-fix-gate-20260713.md` 的两名独立 verifier 均确认：稀疏论文提纲会把同一少量事实或缺口重复铺入材料、结果、讨论和结论。共同交集为 6 份输出、2 个 prompt、3 名 writer；用户随后明确要求进入最小修复轮，并要求验证失败或存在回滚风险时撤销本次小修改。

- 发布基线：`v1.5.7=d3755df7deb2456150c61ccb1944aa3982f7edf1`。
- 论文功能基线：`aaba577b9924710a92625c5044086efd7308f128`；其后的提交只增加 evidence，产品文件未变。
- 候选起点：`d9a1e260ee593bb0fee9ae8a521d987fc48901e4`。

## 现有流程

论文提纲当前仍按 `研究问题或中心命题 -> 全文提纲 -> 章节任务 -> 小节要点 -> 段落论点` 由大至小分解：

1. 用户题目、材料和学校模板优先；没有模板时不强制固定章数。
2. 每章说明要回答的问题、可用材料和缺失证据，不提前写入未给结论。
3. 下一级只展开上一级任务，不另起无材料支撑的论证线。

现有流程没有明确处理“材料很少但三级提纲天然诱发多章重复”的情况。上一轮 writer 虽未编造结论，仍用近义标题把相同数字、材料缺口和边界在多章重复占位。

## 单句候选

只在 `references/academic-writing.md` 的“提纲构造”中增加一条：

> 材料稀疏时，不为凑标准章数用近义标题跨章重复同一事实或缺口；未指定模板时按证据收缩章节，指定模板时保留章节但区分各章任务。

该句只收紧论文提纲叶子质量，不改变：

- 公文或论文任务路由；
- reference 加载条件；
- 用户模板优先；
- 由大至小写、由小至大审；
- 起草、改稿、只审不改和输出模式；
- 默认不联网、事实与引用边界；
- lint、发布和回滚工作流。

## 验证与回滚门槛

1. 确定性守卫只检查该单句存在、镜像同步和上下文预算，不把静态检查包装成写作改善。
2. 真实 A/B 固定 `aaba577` 产品基线与单句候选，覆盖稀疏无模板、固定四章、用户明确六章、材料较充分和只审不改。
3. 独立 verifier 只看匿名 prompt 与输出，检查跨章重复、模板遵循、事实边界和旧能力。
4. 候选必须减少目标类重复，且不得删除用户固定章节、漏掉给定事实、补造材料、改变审稿模式或使旧硬边界回退。
5. 若目标问题没有改善、判断分歧无法收敛、任何旧硬边界回退或上下文超过 `<25000`，删除该单句并重新同步镜像；失败证据保留。

## 真实 A/B 与解盲结果

两名隔离 writer 各自对 `aaba577` 和单句候选执行 T1—T6，条件顺序反转，共保存 24 份原始输出：

- Writer 1：`X=baseline-aaba577`，`Y=current-candidate`。
- Writer 2：`X=current-candidate`，`Y=baseline-aaba577`。
- 两个 writer 均记录 `MODEL_ID: unavailable`；未使用 MiniMax，也没有猜测精确模型 ID。

两名 verifier 只读取原 prompt 和 X/Y 输出，不读取映射、diff、技能文件或提交历史。解盲结果为：

| verifier | 候选胜 | 基线胜 | 平局 | 双失败 | 候选硬回退 |
| --- | ---: | ---: | ---: | ---: | ---: |
| verifier 1 | 6 | 1 | 5 | 0 | 0 |
| verifier 2 | 8 | 1 | 3 | 0 | 0 |

两名 verifier 的共同判断：

1. T1、T2 在两次独立 writer 中均由候选胜出，跨章重复减少且没有漏掉给定事实。
2. T3 一次由候选胜出、一次由基线略胜；候选均保留固定四章和层级，没有硬回退，说明目标改善尚不稳定。
3. T4—T6 的候选没有删除固定结构、补造材料、过度收缩或改变只审不改模式。
4. 唯一硬失败发生在 Writer 2 的基线侧：遗漏“10 名师生”这一访谈对象事实，不属于候选回退。

原始 prompt、24 份输出、两份 verifier 报告和解盲映射分别保存在本报告同名目录。由于运行环境没有暴露精确模型 ID，本轮真实 A/B 只记为 Codex 原生子代理 sanity；用户已明确授权进入最小修复轮，本轮不以它替代指定精确模型矩阵或统计显著性证明。

## 工程验证

- `python -B -m unittest tests.test_skill_boundary tests.test_real_prompt_ablation -v`：52 tests，OK。
- `python -B -m unittest discover -s tests -v`：144 tests，OK。
- `python -B tools\run_real_prompt_ablation.py --baseline-root output\release-baselines\local-aaba577-outline-fix --baseline-label baseline-aaba577 --current-root . --out output\minimal-fix-outline-20260713\vs-aaba577`：基线 111/112，候选 112/112；基线只在新增 P113 失败。
- `python -B tools\run_real_prompt_ablation.py --baseline-root output\release-baselines\github-1.5.7-paper --baseline-label baseline-1.5.7 --current-root . --out output\minimal-fix-outline-20260713\vs-1.5.7`：基线 102/112，候选 112/112。
- `npm run eval:official-writing:smoke`：沙箱内首次因 Node 无法访问实际存在的 Python 可执行文件产生 20 个环境错误；按环境故障处理，不记通过。沙箱外原命令复跑为 20/20 PASS、0 failed、0 errors、judge consistency 1.0。该结果仍是 deterministic local stub 工程证据，不是写作质量证明。
- `python -B C:\Users\admin\.codex\skills\.system\skill-creator\scripts\quick_validate.py chinese-official-writing`：`Skill is valid!`。
- 完整评测数据按 10 例分 27 批计算：`MAX_CONTEXT=24910`，低于仓库 `<25000` 门槛。
- `python -B tools\sync_adapters.py`：沙箱内首次因 `.agents` 写权限失败；获批后原命令复跑成功，canonical 与 5 个发行镜像同步。
- 提交前只机械清理两份原始 writer 文件的行尾空格和 EOF 多余空行；清理前后按“去行尾空格、去 EOF 多余空行、统一 LF”计算的 SHA-256 分别保持 `7644C81D...F2B`、`2FB6A438...D7BF`，正文、标点和顺序未变。
- `git diff --check`：通过。

## 保留与剩余风险

保留这条论文提纲叶子规则。它在两个稀疏无模板 prompt、两次独立 writer 和两名 verifier 中形成一致改善；没有候选侧事实遗漏、固定模板删除、充分材料过度收缩或只审不改回退。

剩余风险：T3 固定模板下的去重复改善不稳定；精确模型 ID 未暴露；本轮没有运行 3000 字以上完整论文、长期多轮 compact 或跨供应商模型矩阵。因此该句只解决已复现的提纲重复，不扩展为完整论文无人值守能力承诺。
