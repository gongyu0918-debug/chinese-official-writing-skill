# 1.5.0 Playbook 架构跟进修复与消融记录

日期：2026-07-04

本轮在 `746a267` 的 1.5.0 架构候选基础上继续处理，不发布、不打 tag、不 bump 版本。基线仍固定为 GitHub/ClawHub 1.4.15 对应的 `origin/main` commit `9c218ea849449a9aced6ad101e2a05fc21b233e0`。

## 触发原因

用户要求确认是否已和上一基线做消融，并继续用 subagent 做更大范围真实写稿/审稿测试，尤其确认 AI 相关稿件和本轮架构优化不会造成质量回退。

上一轮确定性消融已经证明 current 在新增 playbook 架构用例上补齐能力，且旧 P001-P071 未回退；但本轮 12 个真实场景 A/B 盲审发现当前候选仍有轻微回归风险，需要在发布前消除。

## A/B 复测发现

只读 writer：

- Curie 使用 1.4.15 baseline skill 生成 E01-E12。
- Einstein 使用当前候选 skill 生成同组 E01-E12。
- Avicenna 只看 prompt 和两组输出盲审。

Avicenna 结论：

- AI 算力可研和 AI 推理服务采购两项均 PASS；AI 可研短稿 current 更紧。
- current 无 outright FAIL，但存在 material regression risk。
- 共性风险为：会议纪要、讲话、工作要点中弱依据补写受众、角色或流程；字段式审查材料拆行后出现 `说明。；` 和行尾分号噪声。

## 最小修复

本轮只做 prompt/reference 层修复，不新增脚本硬门禁、不新增清洗器、不扩大默认联网或 API。

- `SKILL.md`：补一句 playbook 事实边界，会议纪要、讲话稿/致辞、工作要点等只组织已给事实，不补会议判断、受众称呼、角色分工、合同义务或服务单位责任。
- `references/genre-playbooks.md`：在会议纪要、讲话稿/致辞、工作要点、采购公告/审查材料小节补具体风险提示。
- `references/workflow.md`：把 playbook 事实边界并入事实充分性软处理；字段单元规则补“分号只是字段分隔符，拆行后不保留行尾分号或造成 `。；`”。
- `references/review-checklist.md`：增加 Playbook 事实外扩和字段拆行标点复核项。
- `tools/run_real_prompt_ablation.py`：新增 P080/P081，覆盖会议判断/受众/服务单位责任外扩和字段拆行标点噪声。
- 同步 `skills/`、`.agents/`、`.qwen/`、`hermes/`、`openclaw/` 镜像。

后续 subagent 复测又发现单点 WARN：会议纪要第三项缺完成期限时，模型写成“按维保采购预算审核执行”。该问题未形成共性，但贴近本轮事实边界，已在会议纪要 playbook 追加最小提示：责任或期限未给时留空或列为待确认，不用“按审核执行”“后续推进”等泛口径补期限。

## 修复后真实 subagent 测试

Bohr 使用修复后的 `.agents/skills/chinese-official-writing/SKILL.md` 生成 T01-T07：

- T01 AI 算力可研：PASS。未编造预算、GPU 型号、SLA、服务周期。
- T02 AI 推理服务采购：PASS。未指定品牌、模型名、供应商；保留日均 300 次、9 万元、联系人。
- T03 会议纪要：初次 WARN。未补“会议认为/会议强调”，但把未给期限写成泛口径。
- T04 揭牌讲话：PASS。未新增“同学们”等受众，未编造成效数据。
- T05 信息化工作要点：PASS。未补运维服务单位或合同责任。
- T06 字段式审查材料：PASS。字段顺序和单元边界保留，无 `。；` 和行尾分号。
- T07 只审 AI 味/格式：PASS。只审不改，未打 0-100 分。

Dalton 盲审结论：6 PASS、1 WARN，暂无 material regression risk，未发现 2 次以上共性问题。

Epicurus 在追加会议纪要期限提示后做聚焦复测：第三项完成期限留空，未再补“按审核执行”“后续推进”等泛口径，判定该边角风险解除。

## 验证命令和结果

已运行：

- `python .\tools\sync_adapters.py`：通过。说明：沙箱内 `.agents` 目录只读，实际以提权方式运行仓库既有同步脚本。
- `python -m unittest tests.test_real_prompt_ablation tests.test_skill_boundary -v`：40 tests OK。
- `python .\tools\run_real_prompt_ablation.py --baseline-root .\output\release-baselines\github-1.4.15 --baseline-label baseline-1.4.15 --current-root . --out .\output\real-prompt-vs-1.4.15-playbook-fix-final-20260704`：退出码 0。
  - baseline-1.4.15：81 用例，71 通过，10 失败。
  - current：81 用例，81 通过，0 失败。
  - baseline 失败集中在 P072-P081；P001-P071 未观察到确定性回退。
- `python -m unittest discover -s tests -v`：99 tests OK。
- `& 'C:\Users\admin\AppData\Local\Programs\Python\Python313\python.exe' evals/official-writing/run_eval.py --suite smoke --judge-batch-size 2`：通过。
  - promptfoo smoke：20/20 passed。
  - pairwise：skill 10，baseline 0，tie 0，needs_manual_review 0，judge_consistency_rate 1.0。
- `python .\tools\run_real_article_eval.py --out .\output\real-article-playbook-fix-final-20260704`：退出码 0。
  - skill：10 样本，平均差异率 0.00%，关键词命中率 100.00%，格式风险 0，重复事项 0，反 AI 风险 0。
  - 该工具仍提示匿名占位词风险样本 9，属于真实样文回归工具的复核提示，不等同质量失败。
- `git diff --check`：通过；只有 Windows LF/CRLF 提示，无 whitespace error。

说明：

- 直接 `npm run eval:official-writing:smoke` 在沙箱内失败，原因是 promptfoo 子进程无法启动当前 Python 并且旧 `.promptfoo/logs` 清理受限。最终用同一 `run_eval.py` 入口和真实 Python 3.13 在提权环境下复跑通过。
- 未运行发布、tag、push、ClawHub inspect；本轮仍是 1.5.0 本地候选修复。

## 结论

已经和 1.4.15 基线做确定性消融：旧用例 P001-P071 未回退，新增 P072-P081 current 全过。真实 subagent A/B 初测发现的 material regression risk 已通过最小 prompt/reference 修复和聚焦复测解除。AI 算力和 AI 推理服务稿件在本轮真实测试中未观察到质量下降或参数/品牌/供应商编造。

剩余风险：

- Playbook 仍是 prompt/reference 层优化，真实模型输出会有采样波动；正式 1.5.0 发布前还应再做一轮完整安装态写稿/审稿测试。
- 真实样文 eval 的匿名占位词风险需要在发布前结合人工或 LLM judge 解释。
- 当前未发布 1.5.0，也未验证 GitHub/ClawHub live 状态。
