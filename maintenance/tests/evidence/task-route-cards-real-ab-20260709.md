# 2026-07-09 任务路由卡最小并入与真实写稿复测

## 背景

上一轮深渐进式披露测试显示，直接让弱模型多读整份 `workflow.md` 或 `genre-playbooks.md` 并不会稳定改善，反而可能增加事实外扩和格式噪声。用户进一步明确：深渐进式披露应理解为更细颗粒的按需路由，避免加载当前写作无关内容；弱模型格式问题不死磕，只要内容符合 prompt，Markdown 残留等质量问题可容忍为 WARN。

## 本轮最小改动

- 新增 `references/task-route-cards.md`，只放材料稀疏、未决会议纪要、短通知/限字通知、二次局部修改四类轻量卡片。
- `SKILL.md` 参考资料表增加一行：材料稀疏、短稿、低上下文局部修改，或用户明确不新增事实时，先读本轻量卡片；仍复杂时再转读长 reference。
- `tools/sync_adapters.py` 的 OpenClaw 精简入口同步增加同一路由提示。
- 新增边界测试，确认轻卡存在、镜像同步、仍保持短文件和软性口径。

本轮不新增 lint 规则、不新增硬门禁、不新增默认联网、不扩大 `SKILL.md` 硬边界。

## 真实写稿复测

writer 均为隔离上下文，只给 skill 路径和自然语言任务，不给本轮诊断结论，不修改仓库。

- Writer A：`gpt-5.3-codex-spark`，low reasoning。
- Writer B：`gpt-5.5`，low reasoning。
- Verifier：独立 `gpt-5.5`，只看原 prompt 和两份成稿。

### Prompt 覆盖

1. `版慎通数据治理专项推进情况说明`：材料只给 3 个业务系统、重复字段 120 项、初步梳理、未形成整改结论；明确没有责任部门、时间表、验收标准；禁止补工作组、问题清单、统一共识、治理流程、验收节点、责任单位或完成时限。
2. `版慎通模型成本治理会议纪要`：保留 2026 年 7 月 9 日上午、第一会议室、技术应用部/财务部、一个月成本约 6 万元、贵价模型占比较高、拟评估低思考档位和分级模型机制、下次会议听取测试结果；禁止写“会议强调”“会议认为”，禁止补责任分工、完成期限、采购方案或考核要求。
3. 220 字以内账号安全清查通知：保留 OA、联系人李明、电话 12345678、技术应用部、2026 年 7 月 9 日；禁止补“认真落实、严肃处理、记录留痕、无论有无异常”等执行链条。

### Verifier 结果

| Writer | 任务1 | 任务2 | 任务3 | 结论 |
| --- | --- | --- | --- | --- |
| A weak | WARN | WARN | WARN | 核心事实和禁止项基本守住；仍有轻微补落款单位/记录单位、轻微处置链条倾向和格式包装。按用户放宽口径不判 FAIL。 |
| B strong | PASS | PASS | PASS | 三项均遵循 prompt，未补禁止事实或执行链条。 |

## 判断

本轮轻卡并入后，弱模型首稿从前一轮材料稀疏场景连续 FAIL 改为无硬 FAIL；强模型未出现回退。弱模型仍不能按强模型标准要求一次成稿，后续交付口径保持“首稿基本可用，二次/三次自然语言局部修改后可交付”。Markdown 残留、标题包装等格式噪声只作为 WARN 记录，除非影响正式内容理解。

## 已运行验证

- `python -m unittest tests.test_skill_boundary`：34 tests OK。
- `python -m unittest tests.test_real_prompt_ablation`：8 tests OK。
- `python .\tools\run_real_prompt_ablation.py --baseline-root output\release-baselines\pre-task-route-cards-f0ae58f --baseline-label baseline-f0ae58f --current-root . --out output\real-prompt-vs-f0ae58f-task-route-cards`：baseline 85/85，current 85/85。
- `python .\tools\run_real_prompt_ablation.py --baseline-root output\release-baselines\github-1.5.2 --baseline-label baseline-1.5.2 --current-root . --out output\real-prompt-vs-1.5.2-task-route-cards`：baseline 85/85，current 85/85。
- `python -m unittest discover -s tests`：106 tests OK。
- `git diff --check`：通过，无空白错误。
- `python evals\official-writing\run_eval.py --suite smoke --judge-batch-size 2`：20/20 passed，judge consistency 1.0。首次未提权运行因 npm registry 网络权限失败；提权后通过。
- `python C:\Users\2\.codex\skills\.system\skill-creator\scripts\quick_validate.py chinese-official-writing`：Skill is valid。

后续发布前仍需按上一发行基线跑完整 deterministic ablation、全量 unittest、promptfoo smoke 和真实 writer/verifier 发布级复核。
