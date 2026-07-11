# 旁白交付检测与 Prompt 可执行性复核

## 结论

本轮不修改 `SKILL.md`、写稿 reference、事实硬边界或默认 workflow。已回滚稀疏扩写实验，保留一个默认关闭的 mode-aware `prose_lint.py` 检查入口，用于发现正式正文中的材料读取旁白、约束自证、交付说明、AI 身份和英文思考残片；它只输出 finding，不删除或改写正文。

当前 Markdown 对显式 AI 身份和改稿过程较清楚，但没有让低思考模型稳定区分“用户材料中的业务事实”和“模型对输入材料充分性的自我说明”。三名独立复核 agent 在未给补充说明时，均把以下两类句子误判为正文可保留：

- `由于现有材料仅反映阶段情况，暂无法形成完整判断。`
- `本报告仅反映已给事实，不对未提供事项作延伸判断。`

只读注入下面一条候选说明后，三名 agent 均改判为正文外内容，同时继续保留 `现将有关情况报告如下`，也没有误伤用户原文明确给出的材料缺失事实：

> 交付正文直接写业务事实。“材料不足、未提供、仅反映”如果只是模型对输入是否充分的判断，应移到正文外提示；只有用户原文明确要求写入材料状态，或材料状态本身就是事项进展、审查结论、风险依据等业务事实时，才可在正文保留。

该句本轮只记录为下一轮 prompt 候选，未进入 canonical。理解分类 `3/3` 通过不等于真实写稿 A/B 通过，不能据此宣称旁白已经解决。

## 检测器边界

- `generic`：保持历史默认行为，不加载新增 delivery 规则。
- `draft-body`：正式正文中新增旁白或泄露出现一次即 high；正文外待确认区也视为不符合只交付正文。
- `review-only`：允许审稿意见说明材料不足，并豁免同一行或有限跨行的原句引语；未加引号的模型自述和英文思考仍扫描全文。
- `gap-note-allowed`：材料不足说明可放在正文外指定区域；AI 身份、思考残片、约束自证和交付说明仍扫描全文。
- 代码围栏不能隐藏 `draft-body` delivery high；未闭合引号不启用跨行豁免；引号和 inline code 中的审稿示例不作为 agent 自身泄露。
- 不自动删句、不使用固定替换表、不判断事实真伪、不改变默认写稿链路。

## 短样本验证

写稿使用 Luna low 和 GPT-5.5 low，各覆盖稀疏阶段报告、正常通知、字段材料加待确认项、只审不改四个短场景。后续按测试分级规则不再追加长稿矩阵。

- Luna 稀疏稿中的 `现有材料未提供其他账号状态……` 命中 `material-reading-narration`。
- GPT-5.5 稀疏稿中的 `不扩大为……结论`、`本报告仅反映……不作延伸判断` 命中 `constraint-self-certification`。
- 正常通知、字段材料和 review-only 审稿意见无 high 命中。
- 本轮检测器只发现风险，没有启动 cleaner、repair 或全文重写。

writer：`019f5230-288d-7203-bf18-98d58e8a6830`、`019f5230-3cd3-75c0-b5ab-3af65c9c7d6c`。Prompt 理解复核：`019f5236-4229-7fa2-9084-006912078bfe`、`019f5236-5667-7122-a27b-1904335a12e4`、`019f5236-6b1c-7180-baa9-5f14ca513c04`。

## Cold Review

独立 cold reviewer `019f5233-81d9-73f2-9039-43a8dee658bb` 先后复现并推动修复：

1. `review-only` 未加引号泄露和待确认标题后内容漏扫。
2. 多行引语误报。
3. 不加 `--format` 时代码围栏隐藏 delivery high。
4. `gap-note-allowed` 引号或 inline code 中引用原句误报。
5. 未闭合引号导致后续内容全部被当作引语豁免。
6. canonical 与发行镜像不同步。

最终复核剩余 P1/P2 为 0，`publish_blocking=false`。canonical 与五个发行镜像 SHA-256 均为 `6EDBEFB03D9FA539C7137C6EF96B3FFEAA36ABF97ABD51BD75358BC41421FA48`，长度 37,021 字节，逐字节一致。

## 验证

- `python -B -m unittest discover -s tests`：`137/137` 通过。
- `python -B tools/run_real_prompt_ablation.py --baseline-root output/release-baselines/github-1.5.7 --baseline-label release-1.5.7 --current-root . --out output/narration-delivery-mode-vs-1.5.7-final2`：发行基线 `102/103`，当前 `103/103`；原有 102 项无下降。
- Promptfoo smoke：沙箱内 Node 无法调用 Python provider；改在沙箱外显式使用 Python 3.13 后 `20/20` 通过，skill win rate `1.0`，judge consistency `1.0`。
- `python -B tools/run_real_article_eval.py --out output/real-article-narration-delivery-mode-final`：skill 关键要素 `61/61`，格式、重复和反 AI 风险为 0；占位词风险仍按人工口径解释。
- `python -B tools/sync_adapters.py`：同步成功。
- `quick_validate.py chinese-official-writing`：通过。
- `git diff --check`：通过，仅有 Windows 换行提示。

## 剩余风险

- 默认写稿 prompt 尚未采用上面的候选澄清句，弱模型仍可能误把输入充分性说明当作正式正文。
- 新检测器是 opt-in；宿主不显式传入 delivery mode 时，默认写稿运行行为不变，也不会自动获得该检查收益。
- 正则只能发现高置信字面泄露，不能判断任意语义改写、事实外扩或情态漂移。
- 未实现自动 repair；历史 cleaner/finalizer 会造成事实和情态回退，不得原样重试。
- 本轮没有重新运行 3000 字以上、多附件或完整文种长稿矩阵，符合新增测试分级规则。
